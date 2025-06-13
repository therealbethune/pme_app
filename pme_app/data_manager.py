"""
Data Management System for PME Calculator
Handles project management, session persistence, data validation, and user preferences
"""

import hashlib
import json
import logging
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


class DataManager:
    """Comprehensive data management system for PME calculator."""

    def __init__(self, data_dir: str = "pme_data"):
        self.data_dir = Path(data_dir)
        self.projects_dir = self.data_dir / "projects"
        self.settings_dir = self.data_dir / "settings"
        self.cache_dir = self.data_dir / "cache"
        self.exports_dir = self.data_dir / "exports"

        # Create directories
        for dir_path in [
            self.data_dir,
            self.projects_dir,
            self.settings_dir,
            self.cache_dir,
            self.exports_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self.db_path = self.data_dir / "pme_database.db"
        self._init_database()

        # Load user preferences
        self.preferences = self._load_preferences()

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging for data management operations."""
        log_file = self.data_dir / "data_manager.log"
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger(__name__)

    def _init_database(self):
        """Initialize SQLite database for project metadata."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Projects table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    fund_name TEXT,
                    benchmark_name TEXT,
                    created_date TEXT,
                    modified_date TEXT,
                    file_path TEXT,
                    tags TEXT,
                    fund_type TEXT,
                    analysis_method TEXT,
                    status TEXT DEFAULT 'active'
                )
            """
            )

            # Analysis sessions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS analysis_sessions (
                    id TEXT PRIMARY KEY,
                    project_id TEXT,
                    session_name TEXT,
                    created_date TEXT,
                    metrics TEXT,
                    settings TEXT,
                    file_path TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            """
            )

            # Data validation log
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS validation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT,
                    data_type TEXT,
                    validation_date TEXT,
                    issues_found INTEGER,
                    issues_detail TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            """
            )

            # User preferences
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_date TEXT
                )
            """
            )

            conn.commit()

    def create_project(
        self,
        name: str,
        description: str = "",
        fund_name: str = "",
        fund_type: str = "private_equity",
        tags: list[str] = None,
    ) -> str:
        """Create a new project."""
        project_id = self._generate_project_id(name)

        # Create project directory
        project_dir = self.projects_dir / project_id
        project_dir.mkdir(exist_ok=True)

        # Project metadata
        project_data = {
            "id": project_id,
            "name": name,
            "description": description,
            "fund_name": fund_name,
            "fund_type": fund_type,
            "created_date": datetime.now().isoformat(),
            "modified_date": datetime.now().isoformat(),
            "tags": tags or [],
            "status": "active",
        }

        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO projects
                (id, name, description, fund_name, created_date, modified_date,
                 file_path, tags, fund_type, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    project_id,
                    name,
                    description,
                    fund_name,
                    project_data["created_date"],
                    project_data["modified_date"],
                    str(project_dir),
                    json.dumps(tags or []),
                    fund_type,
                    "active",
                ),
            )
            conn.commit()

        # Save project metadata file
        metadata_file = project_dir / "metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(project_data, f, indent=2)

        self.logger.info(f"Created project: {name} (ID: {project_id})")
        return project_id

    def save_project_session(
        self,
        project_id: str,
        session_name: str,
        fund_data: pd.DataFrame,
        index_data: pd.DataFrame,
        metrics: dict,
        settings: dict,
    ) -> str:
        """Save a complete analysis session."""
        session_id = f"{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        project_dir = self.projects_dir / project_id
        session_dir = project_dir / "sessions" / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Save data files
            fund_data.to_csv(session_dir / "fund_data.csv")
            index_data.to_csv(session_dir / "index_data.csv")

            # Save metrics and settings
            with open(session_dir / "metrics.json", "w") as f:
                json.dump(self._serialize_metrics(metrics), f, indent=2)

            with open(session_dir / "settings.json", "w") as f:
                json.dump(settings, f, indent=2)

            # Save session metadata
            session_metadata = {
                "id": session_id,
                "project_id": project_id,
                "session_name": session_name,
                "created_date": datetime.now().isoformat(),
                "fund_records": len(fund_data),
                "index_records": len(index_data),
                "metrics_count": len(metrics),
                "data_hash": self._calculate_data_hash(fund_data, index_data),
            }

            with open(session_dir / "session_metadata.json", "w") as f:
                json.dump(session_metadata, f, indent=2)

            # Update database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO analysis_sessions
                    (id, project_id, session_name, created_date, metrics, settings, file_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        session_id,
                        project_id,
                        session_name,
                        session_metadata["created_date"],
                        json.dumps(self._serialize_metrics(metrics)),
                        json.dumps(settings),
                        str(session_dir),
                    ),
                )

                # Update project modified date
                cursor.execute(
                    """
                    UPDATE projects SET modified_date = ? WHERE id = ?
                """,
                    (datetime.now().isoformat(), project_id),
                )

                conn.commit()

            self.logger.info(f"Saved session: {session_name} for project {project_id}")
            return session_id

        except Exception as e:
            self.logger.error(f"Failed to save session: {str(e)}")
            # Cleanup on failure
            if session_dir.exists():
                shutil.rmtree(session_dir)
            raise

    def load_project_session(
        self, session_id: str
    ) -> tuple[pd.DataFrame, pd.DataFrame, dict, dict]:
        """Load a complete analysis session."""
        # Find session directory
        session_dir = None
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                potential_session_dir = project_dir / "sessions" / session_id
                if potential_session_dir.exists():
                    session_dir = potential_session_dir
                    break

        if not session_dir:
            raise FileNotFoundError(f"Session {session_id} not found")

        try:
            # Load data files
            fund_data = pd.read_csv(
                session_dir / "fund_data.csv", index_col=0, parse_dates=True
            )
            index_data = pd.read_csv(
                session_dir / "index_data.csv", index_col=0, parse_dates=True
            )

            # Load metrics and settings
            with open(session_dir / "metrics.json") as f:
                metrics = json.load(f)

            with open(session_dir / "settings.json") as f:
                settings = json.load(f)

            self.logger.info(f"Loaded session: {session_id}")
            return fund_data, index_data, metrics, settings

        except Exception as e:
            self.logger.error(f"Failed to load session {session_id}: {str(e)}")
            raise

    def get_projects(self, status: str = "active") -> list[dict]:
        """Get list of all projects."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name, description, fund_name, created_date, modified_date,
                       tags, fund_type, benchmark_name
                FROM projects
                WHERE status = ?
                ORDER BY modified_date DESC
            """,
                (status,),
            )

            projects = []
            for row in cursor.fetchall():
                project = {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "fund_name": row[3],
                    "created_date": row[4],
                    "modified_date": row[5],
                    "tags": json.loads(row[6]) if row[6] else [],
                    "fund_type": row[7],
                    "benchmark_name": row[8] or "Not set",
                }
                projects.append(project)

            return projects

    def get_project_sessions(self, project_id: str) -> list[dict]:
        """Get all analysis sessions for a project."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, session_name, created_date, file_path
                FROM analysis_sessions
                WHERE project_id = ?
                ORDER BY created_date DESC
            """,
                (project_id,),
            )

            sessions = []
            for row in cursor.fetchall():
                session = {
                    "id": row[0],
                    "session_name": row[1],
                    "created_date": row[2],
                    "file_path": row[3],
                }
                sessions.append(session)

            return sessions

    def validate_data(
        self, project_id: str, fund_data: pd.DataFrame, index_data: pd.DataFrame
    ) -> dict:
        """Comprehensive data validation."""
        issues = []
        warnings = []

        # Validate fund data
        fund_issues = self._validate_fund_data(fund_data)
        issues.extend(fund_issues)

        # Validate index data
        index_issues = self._validate_index_data(index_data)
        issues.extend(index_issues)

        # Cross-validation
        cross_issues = self._validate_data_alignment(fund_data, index_data)
        issues.extend(cross_issues)

        # Generate validation report
        validation_report = {
            "validation_date": datetime.now().isoformat(),
            "fund_data_records": len(fund_data),
            "index_data_records": len(index_data),
            "issues_count": len(issues),
            "warnings_count": len(warnings),
            "issues": issues,
            "warnings": warnings,
            "overall_status": "PASS" if len(issues) == 0 else "FAIL",
            "data_quality_score": self._calculate_quality_score(
                fund_data, index_data, issues
            ),
        }

        # Log to database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO validation_log
                (project_id, data_type, validation_date, issues_found, issues_detail)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    project_id,
                    "fund_and_index",
                    validation_report["validation_date"],
                    len(issues),
                    json.dumps(issues),
                ),
            )
            conn.commit()

        return validation_report

    def _validate_fund_data(self, df: pd.DataFrame) -> list[str]:
        """Validate fund cash flow data."""
        issues = []

        if df.empty:
            issues.append("Fund data is empty")
            return issues

        # Check required columns
        required_columns = ["cash_flow", "nav"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            issues.append(f"Missing required columns: {missing_columns}")

        # Check for null values
        if df.isnull().any().any():
            null_columns = df.columns[df.isnull().any()].tolist()
            issues.append(f"Null values found in columns: {null_columns}")

        # Check date index
        if not isinstance(df.index, pd.DatetimeIndex):
            issues.append("Index is not a DatetimeIndex")

        # Check for duplicate dates
        if df.index.duplicated().any():
            issues.append("Duplicate dates found in fund data")

        # Validate cash flows
        if "cash_flow" in df.columns:
            if (df["cash_flow"] == 0).all():
                issues.append("All cash flows are zero")

            # Check for extreme values
            cf_std = df["cash_flow"].std()
            cf_mean = df["cash_flow"].mean()
            extreme_threshold = abs(cf_mean) + 5 * cf_std

            if (abs(df["cash_flow"]) > extreme_threshold).any():
                issues.append("Extreme cash flow values detected")

        return issues

    def _validate_index_data(self, df: pd.DataFrame) -> list[str]:
        """Validate index/benchmark data."""
        issues = []

        if df.empty:
            issues.append("Index data is empty")
            return issues

        # Check for price column
        if "price" not in df.columns and len(df.columns) < 1:
            issues.append("No price data found in index")

        # Check date index
        if not isinstance(df.index, pd.DatetimeIndex):
            issues.append("Index data does not have DatetimeIndex")

        # Check for negative prices
        price_column = "price" if "price" in df.columns else df.columns[0]
        if (df[price_column] <= 0).any():
            issues.append("Negative or zero prices found in index data")

        # Check for reasonable price movements
        if len(df) > 1:
            returns = df[price_column].pct_change().dropna()
            if (abs(returns) > 0.5).any():  # >50% single period return
                issues.append("Extreme price movements detected in index data")

        return issues

    def _validate_data_alignment(
        self, fund_df: pd.DataFrame, index_df: pd.DataFrame
    ) -> list[str]:
        """Validate alignment between fund and index data."""
        issues = []

        if fund_df.empty or index_df.empty:
            return issues

        # Check date range overlap
        fund_start, fund_end = fund_df.index.min(), fund_df.index.max()
        index_start, index_end = index_df.index.min(), index_df.index.max()

        if fund_start < index_start:
            issues.append(
                f"Fund data starts before index data ({fund_start} vs {index_start})"
            )

        if fund_end > index_end:
            issues.append(
                f"Fund data ends after index data ({fund_end} vs {index_end})"
            )

        # Check for sufficient overlap
        overlap_start = max(fund_start, index_start)
        overlap_end = min(fund_end, index_end)
        overlap_days = (overlap_end - overlap_start).days

        if overlap_days < 365:  # Less than 1 year overlap
            issues.append(f"Insufficient data overlap: only {overlap_days} days")

        return issues

    def _calculate_quality_score(
        self, fund_df: pd.DataFrame, index_df: pd.DataFrame, issues: list[str]
    ) -> float:
        """Calculate data quality score (0-100)."""
        base_score = 100.0

        # Deduct points for issues
        issue_penalty = len(issues) * 10
        base_score -= issue_penalty

        # Bonus for data completeness
        if not fund_df.empty and not index_df.empty:
            completeness_bonus = min(
                10, len(fund_df) / 12
            )  # Bonus for more data points
            base_score += completeness_bonus

        # Bonus for data range
        if len(fund_df) > 0 and len(index_df) > 0:
            fund_range = (fund_df.index.max() - fund_df.index.min()).days / 365.25
            range_bonus = min(10, fund_range / 5)  # Bonus for longer time series
            base_score += range_bonus

        return max(0, min(100, base_score))

    def export_project_data(self, project_id: str, export_format: str = "excel") -> str:
        """Export complete project data."""
        project_dir = self.projects_dir / project_id
        if not project_dir.exists():
            raise FileNotFoundError(f"Project {project_id} not found")

        # Create export directory
        export_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = self.exports_dir / f"{project_id}_{export_timestamp}"
        export_dir.mkdir(exist_ok=True)

        try:
            # Load project metadata
            with open(project_dir / "metadata.json") as f:
                metadata = json.load(f)

            if export_format.lower() == "excel":
                return self._export_to_excel(project_id, export_dir, metadata)
            elif export_format.lower() == "zip":
                return self._export_to_zip(project_id, export_dir, metadata)
            else:
                raise ValueError(f"Unsupported export format: {export_format}")

        except Exception as e:
            self.logger.error(f"Failed to export project {project_id}: {str(e)}")
            raise

    def _export_to_excel(
        self, project_id: str, export_dir: Path, metadata: dict
    ) -> str:
        """Export project to Excel format."""

        export_file = export_dir / f"{metadata['name']}_export.xlsx"

        with pd.ExcelWriter(export_file, engine="openpyxl") as writer:
            # Project summary
            summary_df = pd.DataFrame(
                [
                    ["Project Name", metadata["name"]],
                    ["Description", metadata.get("description", "")],
                    ["Fund Name", metadata.get("fund_name", "")],
                    ["Fund Type", metadata.get("fund_type", "")],
                    ["Created Date", metadata["created_date"]],
                    ["Modified Date", metadata["modified_date"]],
                ],
                columns=["Property", "Value"],
            )

            summary_df.to_excel(writer, sheet_name="Project Summary", index=False)

            # Get all sessions and export their data
            sessions = self.get_project_sessions(project_id)
            for i, session in enumerate(sessions[:5]):  # Limit to 5 most recent
                try:
                    fund_data, index_data, metrics, settings = (
                        self.load_project_session(session["id"])
                    )

                    sheet_name = f"Session_{i+1}"
                    fund_data.to_excel(writer, sheet_name=f"{sheet_name}_Fund")
                    index_data.to_excel(writer, sheet_name=f"{sheet_name}_Index")

                    # Metrics sheet
                    metrics_df = pd.DataFrame(
                        list(metrics.items()), columns=["Metric", "Value"]
                    )
                    metrics_df.to_excel(
                        writer, sheet_name=f"{sheet_name}_Metrics", index=False
                    )

                except Exception as e:
                    self.logger.warning(
                        f"Could not export session {session['id']}: {str(e)}"
                    )

        self.logger.info(f"Exported project {project_id} to Excel: {export_file}")
        return str(export_file)

    def _generate_project_id(self, name: str) -> str:
        """Generate unique project ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_hash = hashlib.md5(name.encode()).hexdigest()[:8]
        return f"proj_{timestamp}_{name_hash}"

    def _calculate_data_hash(
        self, fund_data: pd.DataFrame, index_data: pd.DataFrame
    ) -> str:
        """Calculate hash for data integrity checking."""
        combined_str = f"{fund_data.to_string()}{index_data.to_string()}"
        return hashlib.md5(combined_str.encode()).hexdigest()

    def _serialize_metrics(self, metrics: dict) -> dict:
        """Serialize metrics for JSON storage."""
        from pme_app.utils import to_jsonable

        return to_jsonable(metrics)

    def _load_preferences(self) -> dict:
        """Load user preferences."""
        preferences_file = self.settings_dir / "preferences.json"
        default_preferences = {
            "default_pme_method": "kaplan_schoar",
            "default_benchmark": "sp500",
            "auto_save_sessions": True,
            "max_recent_projects": 10,
            "export_format": "excel",
            "data_validation_level": "strict",
            "theme": "light",
        }

        if preferences_file.exists():
            try:
                with open(preferences_file) as f:
                    loaded_prefs = json.load(f)
                default_preferences.update(loaded_prefs)
            except Exception as e:
                self.logger.warning(f"Could not load preferences: {str(e)}")

        return default_preferences

    def save_preferences(self, preferences: dict):
        """Save user preferences."""
        self.preferences.update(preferences)
        preferences_file = self.settings_dir / "preferences.json"

        try:
            with open(preferences_file, "w") as f:
                json.dump(self.preferences, f, indent=2)

            # Also save to database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for key, value in preferences.items():
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO user_preferences (key, value, updated_date)
                        VALUES (?, ?, ?)
                    """,
                        (key, json.dumps(value), datetime.now().isoformat()),
                    )
                conn.commit()

            self.logger.info("Saved user preferences")

        except Exception as e:
            self.logger.error(f"Failed to save preferences: {str(e)}")
            raise

    def get_recent_projects(self, limit: int = None) -> list[dict]:
        """Get recently modified projects."""
        if limit is None:
            limit = self.preferences.get("max_recent_projects", 10)

        projects = self.get_projects()
        return projects[:limit]

    def delete_project(self, project_id: str):
        """Soft delete a project."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE projects SET status = 'deleted', modified_date = ?
                WHERE id = ?
            """,
                (datetime.now().isoformat(), project_id),
            )
            conn.commit()

        self.logger.info(f"Deleted project: {project_id}")

    def cleanup_old_data(self, days_old: int = 30):
        """Cleanup old temporary files and cache."""
        cutoff_date = datetime.now() - timedelta(days=days_old)

        # Cleanup cache
        for cache_file in self.cache_dir.iterdir():
            if (
                cache_file.is_file()
                and cache_file.stat().st_mtime < cutoff_date.timestamp()
            ):
                cache_file.unlink()

        # Cleanup old exports
        for export_file in self.exports_dir.iterdir():
            if (
                export_file.is_file()
                and export_file.stat().st_mtime < cutoff_date.timestamp()
            ):
                export_file.unlink()

        self.logger.info(f"Cleaned up data older than {days_old} days")


# Singleton instance
data_manager = DataManager()
