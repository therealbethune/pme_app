"""
Advanced Data Processor for PME Calculator

This module provides intelligent data processing capabilities that can:
1. Auto-detect column types and formats
2. Handle multiple naming conventions
3. Construct optimal data structures for calculations
4. Validate and clean data
5. Support multiple portfolio/fund datasets
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

logger = logging.getLogger(__name__)


class DataType(Enum):
    DATE = "date"
    CASH_FLOW = "cash_flow"
    CONTRIBUTION = "contribution"
    DISTRIBUTION = "distribution"
    NAV = "nav"
    INDEX_VALUE = "index_value"
    PRICE = "price"
    RETURN = "return"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    COUNT = "count"
    TEXT = "text"
    UNKNOWN = "unknown"
    OTHER_CASH_FLOW = "other"  # Requires user classification


@dataclass
class DataIssue:
    """Represents a data issue that can be automatically fixed"""

    issue_id: str
    title: str
    description: str
    severity: str  # 'error', 'warning', 'info'
    affected_columns: list[str]
    affected_rows: list[int]
    fix_description: str
    fix_parameters: dict[str, Any]
    auto_fixable: bool = True


@dataclass
class ColumnMapping:
    """Represents a detected column mapping"""

    original_name: str
    standardized_name: str
    data_type: DataType
    confidence: float
    transformations: list[str] = field(default_factory=list)


@dataclass
class DatasetMetadata:
    """Metadata about a processed dataset"""

    name: str
    rows: int
    columns: int
    date_range: tuple[datetime, datetime]
    column_mappings: list[ColumnMapping]
    data_quality_score: float
    missing_data_percentage: float


@dataclass
class UnclassifiedColumn:
    """Represents a column that needs user classification"""

    column_name: str
    sample_values: list[str | float | int]
    detected_patterns: list[str]
    suggested_type: str | None
    confidence: float
    file_name: str


@dataclass
class OptimalDataStructure:
    """The optimal data structure for PME calculations"""

    fund_data: pd.DataFrame
    index_data: pd.DataFrame | None
    metadata: dict[str, DatasetMetadata]
    calculation_ready: bool
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    unclassified_columns: list[UnclassifiedColumn] = field(default_factory=list)
    data_issues: list[DataIssue] = field(default_factory=list)


class IntelligentDataProcessor:
    """
    Advanced data processor that can automatically detect and optimize data structures
    """

    def __init__(self):
        self.column_patterns = self._initialize_column_patterns()
        self.date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%m-%d-%Y",
            "%d-%m-%Y",
            "%Y%m%d",
            "%m/%d/%y",
            "%d/%m/%y",
            "%y/%m/%d",
            "%m-%d-%y",
            "%d-%m-%y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
        ]

    def _initialize_column_patterns(self) -> dict[DataType, list[str]]:
        """Initialize regex patterns for column detection"""
        return {
            DataType.DATE: [
                r".*date.*",
                r".*time.*",
                r".*period.*",
                r".*month.*",
                r".*year.*",
                r".*day.*",
                r".*dt.*",
                r".*timestamp.*",
                r".*when.*",
            ],
            DataType.CASH_FLOW: [
                r".*cash.*flow.*",
                r".*cashflow.*",
                r".*cf.*",
                r".*flow.*",
                r".*net.*cash.*",
                r".*cash.*",
            ],
            DataType.CONTRIBUTION: [
                r".*contribution.*",
                r".*contrib.*",
                r".*capital.*call.*",
                r".*call.*",
                r".*paid.*in.*",
                r".*investment.*",
                r".*funding.*",
                r".*drawdown.*",
                r".*commitment.*",
                r".*inflow.*",
            ],
            DataType.DISTRIBUTION: [
                r".*distribution.*",
                r".*distrib.*",
                r".*payout.*",
                r".*dividend.*",
                r".*return.*capital.*",
                r".*proceeds.*",
                r".*realization.*",
                r".*outflow.*",
                r".*cash.*out.*",
            ],
            DataType.NAV: [
                r".*nav.*",
                r".*net.*asset.*value.*",
                r".*valuation.*",
                r".*value.*",
                r".*market.*value.*",
                r".*fair.*value.*",
                r".*book.*value.*",
                r".*ending.*value.*",
                r".*balance.*",
            ],
            DataType.INDEX_VALUE: [
                r".*index.*",
                r".*benchmark.*",
                r".*market.*",
                r".*s&p.*",
                r".*sp.*",
                r".*russell.*",
                r".*msci.*",
                r".*level.*",
                r".*price.*index.*",
            ],
            DataType.PRICE: [r".*price.*", r".*level.*", r".*quote.*", r".*rate.*"],
            DataType.RETURN: [
                r".*return.*",
                r".*yield.*",
                r".*performance.*",
                r".*gain.*",
                r".*growth.*",
                r".*change.*",
            ],
        }

    def detect_column_type(
        self, column_name: str, sample_values: list[Any]
    ) -> ColumnMapping:
        """
        Detect the type and purpose of a column based on name and sample values
        """
        column_name_lower = column_name.lower().strip()

        # Try to match column name patterns
        best_match = DataType.UNKNOWN
        best_confidence = 0.0

        for data_type, patterns in self.column_patterns.items():
            for pattern in patterns:
                if re.match(pattern, column_name_lower):
                    confidence = len(re.findall(pattern, column_name_lower)) / len(
                        patterns
                    )
                    if confidence > best_confidence:
                        best_match = data_type
                        best_confidence = confidence

        # Analyze sample values to improve detection
        if best_match == DataType.UNKNOWN or best_confidence < 0.5:
            value_based_type, value_confidence = self._analyze_sample_values(
                sample_values
            )
            if value_confidence > best_confidence:
                best_match = value_based_type
                best_confidence = value_confidence

        # Generate standardized name
        standardized_name = self._generate_standard_name(best_match, column_name)

        return ColumnMapping(
            original_name=column_name,
            standardized_name=standardized_name,
            data_type=best_match,
            confidence=best_confidence,
        )

    def _analyze_sample_values(
        self, sample_values: list[Any]
    ) -> tuple[DataType, float]:
        """Analyze sample values to determine data type"""
        if not sample_values:
            return DataType.UNKNOWN, 0.0

        # Remove None/NaN values
        clean_values = [v for v in sample_values if pd.notna(v)]
        if not clean_values:
            return DataType.UNKNOWN, 0.0

        # Check for dates
        date_count = sum(1 for v in clean_values if self._is_date_like(v))
        if date_count / len(clean_values) > 0.7:
            return DataType.DATE, 0.9

        # Check for numeric patterns
        numeric_values = []
        for v in clean_values:
            try:
                if isinstance(v, int | float):
                    numeric_values.append(float(v))
                elif isinstance(v, str):
                    # Try to parse as number
                    clean_v = re.sub(r"[,$%]", "", v.strip())
                    numeric_values.append(float(clean_v))
            except (ValueError, TypeError):
                continue

        if len(numeric_values) / len(clean_values) > 0.8:
            # Analyze numeric patterns for cash flow detection
            cash_flow_patterns = self._detect_cash_flow_patterns(numeric_values)

            # If it looks like cash flow but we can't classify it specifically
            if (
                cash_flow_patterns["is_likely_cash_flow"]
                and not cash_flow_patterns["specific_type"]
            ):
                return DataType.OTHER_CASH_FLOW, 0.6

            # Analyze numeric patterns
            if all(v >= 0 for v in numeric_values):
                if all(v < 10 and v > -10 for v in numeric_values):
                    return DataType.RETURN, 0.7  # Likely returns/percentages
                elif max(numeric_values) > 1000:
                    return DataType.CURRENCY, 0.8  # Likely currency amounts

            return DataType.COUNT, 0.6  # Generic numeric

        return DataType.TEXT, 0.5

    def _detect_cash_flow_patterns(self, numeric_values: list[float]) -> dict[str, Any]:
        """Detect patterns that indicate cash flow types"""
        if not numeric_values:
            return {"is_likely_cash_flow": False, "specific_type": None, "patterns": []}

        patterns = []
        has_negative = any(v < 0 for v in numeric_values)
        has_positive = any(v > 0 for v in numeric_values)
        has_large_amounts = any(abs(v) > 10000 for v in numeric_values)
        has_small_amounts = any(0 < abs(v) < 100 for v in numeric_values)

        # Detect specific patterns
        if has_negative and not has_positive:
            patterns.append("negative_values")
        elif has_positive and not has_negative:
            patterns.append("positive_values")
        elif has_negative and has_positive:
            patterns.append("mixed_values")

        if has_large_amounts:
            patterns.append("large_amounts")
        if has_small_amounts:
            patterns.append("small_amounts")

        # Check for percentage-like values
        if all(-5 <= v <= 5 for v in numeric_values if v != 0):
            patterns.append("percentage_like")

        # Check for quarterly patterns (every 3 months)
        if len(numeric_values) >= 4 and len(numeric_values) % 4 == 0:
            patterns.append("quarterly_pattern")

        # Determine if this looks like cash flow
        is_likely_cash_flow = (
            has_large_amounts
            and (has_negative or has_positive)
            and "percentage_like" not in patterns
        )

        # Try to determine specific type
        specific_type = None
        if "negative_values" in patterns and "large_amounts" in patterns:
            specific_type = "contribution"
        elif "positive_values" in patterns and "large_amounts" in patterns:
            specific_type = "distribution"

        return {
            "is_likely_cash_flow": is_likely_cash_flow,
            "specific_type": specific_type,
            "patterns": patterns,
        }

    def _is_date_like(self, value: Any) -> bool:
        """Check if a value looks like a date"""
        if isinstance(value, datetime | date):
            return True

        if isinstance(value, str):
            for fmt in self.date_formats:
                try:
                    datetime.strptime(value.strip(), fmt)
                    return True
                except ValueError:
                    continue

        return False

    def _generate_standard_name(self, data_type: DataType, original_name: str) -> str:
        """Generate a standardized column name"""
        mapping = {
            DataType.DATE: "date",
            DataType.CASH_FLOW: "cashflow",
            DataType.CONTRIBUTION: "contribution",
            DataType.DISTRIBUTION: "distribution",
            DataType.NAV: "nav",
            DataType.INDEX_VALUE: "index_value",
            DataType.PRICE: "price",
            DataType.RETURN: "return",
        }

        return mapping.get(data_type, original_name.lower().replace(" ", "_"))

    def process_dataset(
        self,
        data: pd.DataFrame | dict[str, list] | list[dict],
        dataset_name: str = "dataset",
    ) -> tuple[pd.DataFrame, DatasetMetadata]:
        """
        Process a single dataset and return optimized structure
        """
        # Convert to DataFrame if needed
        df = pd.DataFrame(data) if isinstance(data, dict | list) else data.copy()

        list(df.columns)

        # Detect and map columns
        column_mappings = []
        for col in df.columns:
            sample_values = df[col].dropna().head(10).tolist()
            mapping = self.detect_column_type(col, sample_values)
            column_mappings.append(mapping)

        # Apply transformations
        transformed_df = self._apply_transformations(df, column_mappings)

        # Calculate metadata
        metadata = self._calculate_metadata(
            dataset_name, transformed_df, column_mappings
        )

        return transformed_df, metadata

    def _apply_transformations(
        self, df: pd.DataFrame, mappings: list[ColumnMapping]
    ) -> pd.DataFrame:
        """Apply necessary transformations to optimize the data structure"""
        result_df = df.copy()

        for mapping in mappings:
            col = mapping.original_name

            if mapping.data_type == DataType.DATE:
                result_df[mapping.standardized_name] = self._standardize_dates(df[col])
                mapping.transformations.append("date_standardization")

            elif mapping.data_type in [
                DataType.CASH_FLOW,
                DataType.CONTRIBUTION,
                DataType.DISTRIBUTION,
                DataType.NAV,
                DataType.CURRENCY,
            ]:
                result_df[mapping.standardized_name] = self._standardize_currency(
                    df[col]
                )
                mapping.transformations.append("currency_standardization")

            elif mapping.data_type == DataType.RETURN:
                result_df[mapping.standardized_name] = self._standardize_percentages(
                    df[col]
                )
                mapping.transformations.append("percentage_standardization")

            else:
                result_df[mapping.standardized_name] = df[col]

            # Remove original column if name changed
            if mapping.original_name != mapping.standardized_name:
                result_df = result_df.drop(columns=[mapping.original_name])

        return result_df

    def _standardize_dates(self, series: pd.Series) -> pd.Series:
        """Standardize date formats"""

        def parse_date(value):
            if pd.isna(value):
                return None

            if isinstance(value, datetime | date):
                return value

            if isinstance(value, str):
                for fmt in self.date_formats:
                    try:
                        return datetime.strptime(value.strip(), fmt)
                    except ValueError:
                        continue

            return None

        return series.apply(parse_date)

    def _standardize_currency(self, series: pd.Series) -> pd.Series:
        """Standardize currency values"""

        def parse_currency(value):
            if pd.isna(value):
                return 0.0

            if isinstance(value, int | float):
                return float(value)

            if isinstance(value, str):
                # Remove currency symbols and commas
                clean_value = re.sub(r"[$,€£¥₹]", "", value.strip())

                # Handle parentheses as negative
                if clean_value.startswith("(") and clean_value.endswith(")"):
                    clean_value = "-" + clean_value[1:-1]

                try:
                    return float(clean_value)
                except ValueError:
                    return 0.0

            return 0.0

        return series.apply(parse_currency)

    def _standardize_percentages(self, series: pd.Series) -> pd.Series:
        """Standardize percentage values"""

        def parse_percentage(value):
            if pd.isna(value):
                return 0.0

            if isinstance(value, int | float):
                # If value is > 1, assume it's already in percentage form
                return float(value) / 100 if abs(value) > 1 else float(value)

            if isinstance(value, str):
                clean_value = value.strip().replace("%", "")
                try:
                    num_value = float(clean_value)
                    return num_value / 100 if abs(num_value) > 1 else num_value
                except ValueError:
                    return 0.0

            return 0.0

        return series.apply(parse_percentage)

    def _calculate_metadata(
        self, name: str, df: pd.DataFrame, mappings: list[ColumnMapping]
    ) -> DatasetMetadata:
        """Calculate metadata for the processed dataset"""
        date_columns = [
            m.standardized_name for m in mappings if m.data_type == DataType.DATE
        ]

        if date_columns:
            date_series = df[date_columns[0]].dropna()
            if len(date_series) > 0:
                date_range = (date_series.min(), date_series.max())
            else:
                date_range = (datetime.now(), datetime.now())
        else:
            date_range = (datetime.now(), datetime.now())

        missing_percentage = (
            df.isnull().sum().sum() / (len(df) * len(df.columns))
        ) * 100

        # Calculate data quality score
        quality_score = self._calculate_quality_score(df, mappings)

        return DatasetMetadata(
            name=name,
            rows=len(df),
            columns=len(df.columns),
            date_range=date_range,
            column_mappings=mappings,
            data_quality_score=quality_score,
            missing_data_percentage=missing_percentage,
        )

    def _calculate_quality_score(
        self, df: pd.DataFrame, mappings: list[ColumnMapping]
    ) -> float:
        """Calculate overall data quality score"""
        if df.empty:
            return 0.0

        # Factors: missing data, column confidence, data consistency
        missing_penalty = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100

        confidence_scores = [mapping.confidence for mapping in mappings]
        avg_confidence = (
            sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        )

        # Quality score (0-100)
        quality_score = max(0, (avg_confidence * 100) - missing_penalty)
        return min(100, quality_score)

    def detect_data_issues(
        self,
        df: pd.DataFrame,
        mappings: list[ColumnMapping],
        dataset_name: str = "dataset",
    ) -> list[DataIssue]:
        """Detect common data issues that can be automatically fixed"""
        issues = []

        # 1. Date Format Issues
        date_issues = self._detect_date_issues(df, mappings)
        issues.extend(date_issues)

        # 2. Missing Critical Values
        missing_issues = self._detect_missing_value_issues(df, mappings)
        issues.extend(missing_issues)

        # 3. Cash Flow Sign Issues
        cash_flow_issues = self._detect_cash_flow_sign_issues(df, mappings)
        issues.extend(cash_flow_issues)

        # 4. Duplicate Data Issues
        duplicate_issues = self._detect_duplicate_issues(df)
        issues.extend(duplicate_issues)

        # 5. Inconsistent Naming
        naming_issues = self._detect_naming_issues(df)
        issues.extend(naming_issues)

        # 6. Invalid Numeric Values
        numeric_issues = self._detect_numeric_issues(df, mappings)
        issues.extend(numeric_issues)

        return issues

    def _detect_date_issues(
        self, df: pd.DataFrame, mappings: list[ColumnMapping]
    ) -> list[DataIssue]:
        """Detect date formatting and parsing issues"""
        issues = []

        for mapping in mappings:
            if mapping.data_type == DataType.DATE:
                col_name = mapping.original_name
                if col_name in df.columns:
                    series = df[col_name]

                    # Find rows with unparseable dates
                    invalid_dates = []
                    for idx, value in series.items():
                        if pd.notna(value) and not self._is_date_like(value):
                            invalid_dates.append(idx)

                    if invalid_dates:
                        issues.append(
                            DataIssue(
                                issue_id=f"date_format_{col_name}",
                                title=f"Invalid Date Format in '{col_name}'",
                                description=f"Found {len(invalid_dates)} rows with invalid date formats",
                                severity="warning",
                                affected_columns=[col_name],
                                affected_rows=invalid_dates[:10],  # Limit to first 10
                                fix_description="Convert dates to standard YYYY-MM-DD format",
                                fix_parameters={
                                    "column": col_name,
                                    "format": "standard_date",
                                },
                            )
                        )

        return issues

    def _detect_missing_value_issues(
        self, df: pd.DataFrame, mappings: list[ColumnMapping]
    ) -> list[DataIssue]:
        """Detect critical missing values"""
        issues = []

        critical_types = [
            DataType.DATE,
            DataType.CASH_FLOW,
            DataType.CONTRIBUTION,
            DataType.DISTRIBUTION,
        ]

        for mapping in mappings:
            if mapping.data_type in critical_types:
                col_name = mapping.original_name
                if col_name in df.columns:
                    missing_count = df[col_name].isnull().sum()
                    missing_pct = (missing_count / len(df)) * 100

                    if missing_pct > 10:  # More than 10% missing
                        severity = "error" if missing_pct > 30 else "warning"
                        issues.append(
                            DataIssue(
                                issue_id=f"missing_values_{col_name}",
                                title=f"High Missing Data in '{col_name}'",
                                description=f"{missing_pct:.1f}% of values are missing ({missing_count} out of {len(df)})",
                                severity=severity,
                                affected_columns=[col_name],
                                affected_rows=df[df[col_name].isnull()].index.tolist()[
                                    :10
                                ],
                                fix_description="Fill missing values with appropriate defaults or interpolation",
                                fix_parameters={
                                    "column": col_name,
                                    "method": "interpolate",
                                    "type": mapping.data_type.value,
                                },
                            )
                        )

        return issues

    def _detect_cash_flow_sign_issues(
        self, df: pd.DataFrame, mappings: list[ColumnMapping]
    ) -> list[DataIssue]:
        """Detect cash flow sign inconsistencies"""
        issues = []

        cash_flow_types = [
            DataType.CONTRIBUTION,
            DataType.DISTRIBUTION,
            DataType.CASH_FLOW,
        ]

        for mapping in mappings:
            if mapping.data_type in cash_flow_types:
                col_name = mapping.original_name
                if col_name in df.columns:
                    series = df[col_name].dropna()
                    if len(series) > 0:

                        # Check for sign consistency
                        if mapping.data_type == DataType.CONTRIBUTION:
                            # Contributions should typically be negative (outflows from investor perspective)
                            positive_count = (series > 0).sum()
                            if (
                                positive_count > len(series) * 0.8
                            ):  # More than 80% positive
                                issues.append(
                                    DataIssue(
                                        issue_id=f"contribution_sign_{col_name}",
                                        title=f"Contribution Sign Issue in '{col_name}'",
                                        description=f"Contributions are typically negative (investor outflows), but {positive_count} out of {len(series)} are positive",
                                        severity="warning",
                                        affected_columns=[col_name],
                                        affected_rows=df[
                                            df[col_name] > 0
                                        ].index.tolist()[:10],
                                        fix_description="Convert positive contributions to negative values",
                                        fix_parameters={
                                            "column": col_name,
                                            "operation": "negate_positive",
                                        },
                                    )
                                )

                        elif mapping.data_type == DataType.DISTRIBUTION:
                            # Distributions should typically be positive (inflows to investor)
                            negative_count = (series < 0).sum()
                            if (
                                negative_count > len(series) * 0.8
                            ):  # More than 80% negative
                                issues.append(
                                    DataIssue(
                                        issue_id=f"distribution_sign_{col_name}",
                                        title=f"Distribution Sign Issue in '{col_name}'",
                                        description=f"Distributions are typically positive (investor inflows), but {negative_count} out of {len(series)} are negative",
                                        severity="warning",
                                        affected_columns=[col_name],
                                        affected_rows=df[
                                            df[col_name] < 0
                                        ].index.tolist()[:10],
                                        fix_description="Convert negative distributions to positive values",
                                        fix_parameters={
                                            "column": col_name,
                                            "operation": "negate_negative",
                                        },
                                    )
                                )

        return issues

    def _detect_duplicate_issues(self, df: pd.DataFrame) -> list[DataIssue]:
        """Detect duplicate rows"""
        issues = []

        duplicates = df.duplicated()
        duplicate_count = duplicates.sum()

        if duplicate_count > 0:
            issues.append(
                DataIssue(
                    issue_id="duplicate_rows",
                    title="Duplicate Rows Detected",
                    description=f"Found {duplicate_count} duplicate rows that should be removed",
                    severity="warning",
                    affected_columns=list(df.columns),
                    affected_rows=df[duplicates].index.tolist()[:10],
                    fix_description="Remove duplicate rows, keeping the first occurrence",
                    fix_parameters={"operation": "drop_duplicates"},
                )
            )

        return issues

    def _detect_naming_issues(self, df: pd.DataFrame) -> list[DataIssue]:
        """Detect column naming inconsistencies"""
        issues = []

        # Check for columns with extra spaces or inconsistent casing
        problematic_columns = []
        for col in df.columns:
            if col != col.strip() or col != col.lower():
                problematic_columns.append(col)

        if problematic_columns:
            issues.append(
                DataIssue(
                    issue_id="column_naming",
                    title="Inconsistent Column Naming",
                    description=f"Found {len(problematic_columns)} columns with spacing or casing issues",
                    severity="info",
                    affected_columns=problematic_columns,
                    affected_rows=[],
                    fix_description="Standardize column names (trim spaces, lowercase)",
                    fix_parameters={
                        "columns": problematic_columns,
                        "operation": "standardize_names",
                    },
                )
            )

        return issues

    def _detect_numeric_issues(
        self, df: pd.DataFrame, mappings: list[ColumnMapping]
    ) -> list[DataIssue]:
        """Detect invalid numeric values"""
        issues = []

        numeric_types = [
            DataType.CASH_FLOW,
            DataType.CONTRIBUTION,
            DataType.DISTRIBUTION,
            DataType.NAV,
            DataType.PRICE,
            DataType.RETURN,
        ]

        for mapping in mappings:
            if mapping.data_type in numeric_types:
                col_name = mapping.original_name
                if col_name in df.columns:
                    series = df[col_name]

                    # Check for string values that should be numeric
                    string_numeric_rows = []
                    for idx, value in series.items():
                        if isinstance(value, str) and value.strip():
                            # Try to parse as number
                            try:
                                clean_value = re.sub(r"[,$%]", "", value.strip())
                                float(clean_value)
                                string_numeric_rows.append(idx)
                            except ValueError:
                                continue

                    if string_numeric_rows:
                        issues.append(
                            DataIssue(
                                issue_id=f"string_numeric_{col_name}",
                                title=f"String Numbers in '{col_name}'",
                                description=f"Found {len(string_numeric_rows)} numeric values stored as text",
                                severity="warning",
                                affected_columns=[col_name],
                                affected_rows=string_numeric_rows[:10],
                                fix_description="Convert string numbers to numeric format",
                                fix_parameters={
                                    "column": col_name,
                                    "operation": "string_to_numeric",
                                },
                            )
                        )

        return issues

    def apply_data_fix(self, df: pd.DataFrame, issue: DataIssue) -> pd.DataFrame:
        """Apply a specific data fix to the dataframe"""
        df_fixed = df.copy()

        try:
            if issue.fix_parameters.get("operation") == "negate_positive":
                col = issue.fix_parameters["column"]
                df_fixed.loc[df_fixed[col] > 0, col] = -df_fixed.loc[
                    df_fixed[col] > 0, col
                ]

            elif issue.fix_parameters.get("operation") == "negate_negative":
                col = issue.fix_parameters["column"]
                df_fixed.loc[df_fixed[col] < 0, col] = -df_fixed.loc[
                    df_fixed[col] < 0, col
                ]

            elif issue.fix_parameters.get("operation") == "drop_duplicates":
                df_fixed = df_fixed.drop_duplicates()

            elif issue.fix_parameters.get("operation") == "standardize_names":
                columns = issue.fix_parameters["columns"]
                rename_map = {col: col.strip().lower() for col in columns}
                df_fixed = df_fixed.rename(columns=rename_map)

            elif issue.fix_parameters.get("operation") == "string_to_numeric":
                col = issue.fix_parameters["column"]

                def clean_numeric(value):
                    if isinstance(value, str):
                        try:
                            return float(re.sub(r"[,$%]", "", value.strip()))
                        except ValueError:
                            return value
                    return value

                df_fixed[col] = df_fixed[col].apply(clean_numeric)

            elif issue.fix_parameters.get("operation") == "interpolate":
                col = issue.fix_parameters["column"]
                if issue.fix_parameters.get("type") in [
                    "cash_flow",
                    "contribution",
                    "distribution",
                ]:
                    df_fixed[col] = df_fixed[col].fillna(0)  # Fill cash flows with 0
                else:
                    df_fixed[col] = df_fixed[col].interpolate()

            elif issue.fix_parameters.get("format") == "standard_date":
                col = issue.fix_parameters["column"]
                df_fixed[col] = self._standardize_dates(df_fixed[col])

            logger.info(f"Applied fix for issue: {issue.title}")

        except Exception as e:
            logger.error(f"Failed to apply fix for issue {issue.issue_id}: {str(e)}")

        return df_fixed

    def create_optimal_structure(
        self,
        datasets: dict[str, pd.DataFrame | dict | list],
        primary_dataset: str = None,
        column_classifications: dict[str, str] | None = None,
    ) -> OptimalDataStructure:
        """
        Create the optimal data structure for PME calculations from multiple datasets
        """
        processed_datasets = {}
        metadata = {}
        warnings = []
        suggestions = []
        unclassified_columns = []

        # Process each dataset
        for name, data in datasets.items():
            try:
                processed_df, dataset_metadata = self.process_dataset(data, name)
                processed_datasets[name] = processed_df
                metadata[name] = dataset_metadata

                # Check for unclassified columns that need user input
                for mapping in dataset_metadata.column_mappings:
                    if mapping.data_type == DataType.OTHER_CASH_FLOW:
                        # Get sample values from the original data
                        if isinstance(data, pd.DataFrame):
                            sample_values = (
                                data[mapping.original_name].dropna().head(5).tolist()
                            )
                        else:
                            sample_values = []

                        # Get detected patterns
                        numeric_sample = []
                        for v in sample_values:
                            try:
                                if isinstance(v, int | float):
                                    numeric_sample.append(float(v))
                                elif isinstance(v, str):
                                    clean_v = re.sub(r"[,$%]", "", v.strip())
                                    numeric_sample.append(float(clean_v))
                            except (ValueError, TypeError):
                                continue

                        patterns = self._detect_cash_flow_patterns(numeric_sample)

                        unclassified_columns.append(
                            UnclassifiedColumn(
                                column_name=mapping.original_name,
                                sample_values=sample_values,
                                detected_patterns=patterns["patterns"],
                                suggested_type=patterns["specific_type"],
                                confidence=mapping.confidence,
                                file_name=name,
                            )
                        )

                logger.info(
                    f"Processed dataset '{name}': {dataset_metadata.rows} rows, "
                    f"quality score: {dataset_metadata.data_quality_score:.1f}"
                )

            except Exception as e:
                warnings.append(f"Failed to process dataset '{name}': {str(e)}")
                logger.error(f"Error processing dataset '{name}': {str(e)}")

        if not processed_datasets:
            raise ValueError("No datasets could be processed successfully")

        # Identify fund and index data
        fund_data = None
        index_data = None

        # Auto-detect fund vs index data
        for name, df in processed_datasets.items():
            dataset_meta = metadata[name]
            column_types = {m.data_type for m in dataset_meta.column_mappings}

            # Fund data typically has contributions, distributions, NAV
            fund_indicators = {
                DataType.CONTRIBUTION,
                DataType.DISTRIBUTION,
                DataType.NAV,
                DataType.CASH_FLOW,
            }

            # Index data typically has index values or prices
            index_indicators = {DataType.INDEX_VALUE, DataType.PRICE}

            if fund_indicators.intersection(column_types):
                if (
                    fund_data is None
                    or dataset_meta.data_quality_score
                    > metadata[list(processed_datasets.keys())[0]].data_quality_score
                ):
                    fund_data = df
                    primary_dataset = name
            elif index_indicators.intersection(column_types):
                if index_data is None:
                    index_data = df

        # If no clear fund data, use the primary dataset or first one
        if fund_data is None:
            if primary_dataset and primary_dataset in processed_datasets:
                fund_data = processed_datasets[primary_dataset]
            else:
                fund_data = list(processed_datasets.values())[0]

        # Detect data issues for automatic fixing
        all_data_issues = []
        for dataset_name, df in processed_datasets.items():
            dataset_meta = metadata[dataset_name]
            data_issues = self.detect_data_issues(
                df, dataset_meta.column_mappings, dataset_name
            )
            all_data_issues.extend(data_issues)

        # If there are unclassified columns, we're not ready for calculation yet
        if unclassified_columns:
            calculation_ready = False
            warnings.append(
                f"Found {len(unclassified_columns)} cash flow columns that need classification"
            )
            suggestions.append(
                "Please classify the ambiguous cash flow columns to proceed with analysis"
            )
        else:
            # Validate calculation readiness
            calculation_ready = self._validate_calculation_readiness(
                fund_data, index_data, warnings, suggestions
            )

        return OptimalDataStructure(
            fund_data=fund_data,
            index_data=index_data,
            metadata=metadata,
            calculation_ready=calculation_ready,
            warnings=warnings,
            suggestions=suggestions,
            unclassified_columns=unclassified_columns,
            data_issues=all_data_issues,
        )

    def _validate_calculation_readiness(
        self,
        fund_data: pd.DataFrame,
        index_data: pd.DataFrame | None,
        warnings: list[str],
        suggestions: list[str],
    ) -> bool:
        """Validate if the data structure is ready for PME calculations"""
        ready = True

        # Check for required columns in fund data
        has_cashflow = "cashflow" in fund_data.columns
        has_contribution_distribution = (
            "contribution" in fund_data.columns and "distribution" in fund_data.columns
        )

        if not (has_cashflow or has_contribution_distribution):
            warnings.append("Fund data missing cash flow information")
            suggestions.append(
                "Ensure you have either 'cashflow' column or both 'contribution' and 'distribution' columns"
            )
            ready = False

        if "nav" not in fund_data.columns:
            warnings.append("Fund data missing NAV (Net Asset Value) information")
            suggestions.append("Add a column containing NAV or valuation data")
            ready = False

        # Check date column
        if "date" not in fund_data.columns:
            warnings.append("Fund data missing date information")
            suggestions.append("Ensure you have a date column")
            ready = False

        # Check for sufficient data points
        if len(fund_data) < 2:
            warnings.append("Insufficient data points for meaningful calculations")
            suggestions.append("Provide at least 2 data points with different dates")
            ready = False

        # Check index data if provided
        if index_data is not None:
            if "date" not in index_data.columns:
                warnings.append("Index data missing date information")
                ready = False

            index_value_cols = [
                col
                for col in index_data.columns
                if col in ["index_value", "price", "level"]
            ]
            if not index_value_cols:
                warnings.append("Index data missing value information")
                ready = False

        if ready:
            suggestions.append(
                "Data structure is optimized and ready for PME calculations"
            )

        return ready


# Convenience function for quick processing
def process_multiple_datasets(
    datasets: dict[str, Any], primary_dataset: str = None
) -> OptimalDataStructure:
    """
    Convenience function to quickly process multiple datasets

    Args:
        datasets: Dictionary of dataset_name -> data mappings
        primary_dataset: Name of the primary dataset (usually fund data)

    Returns:
        OptimalDataStructure ready for PME calculations
    """
    processor = IntelligentDataProcessor()
    return processor.create_optimal_structure(datasets, primary_dataset)
