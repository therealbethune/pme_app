"""
Simplified file validation service for PME Calculator.
"""

import logging
from pathlib import Path

import pandas as pd

from .schemas_simple import FileTypeEnum, UploadMeta, ValidationResult

logger = logging.getLogger(__name__)


def detect_column_mappings(df: pd.DataFrame, file_type: str = "fund") -> dict[str, str]:
    """
    Detect column mappings by analyzing column names.
    Returns mapping of standard names to actual column names.
    """
    mappings = {}
    columns = [col.lower().strip() for col in df.columns]

    # Date column detection
    date_keywords = ["date", "dt", "time", "timestamp", "period"]
    for i, col in enumerate(columns):
        if any(keyword in col for keyword in date_keywords):
            mappings["date"] = df.columns[i]
            break

    if file_type == "fund":
        # Cashflow column detection
        cashflow_keywords = ["cashflow", "cash_flow", "cf", "flow", "net"]
        for i, col in enumerate(columns):
            if any(keyword in col for keyword in cashflow_keywords):
                mappings["cashflow"] = df.columns[i]
                break

        # NAV column detection
        nav_keywords = ["nav", "value", "net_asset", "valuation", "val"]
        for i, col in enumerate(columns):
            if any(keyword in col for keyword in nav_keywords):
                mappings["nav"] = df.columns[i]
                break

        # Optional: Contributions/Distributions
        contrib_keywords = ["contribution", "contrib", "investment", "commit"]
        for i, col in enumerate(columns):
            if any(keyword in col for keyword in contrib_keywords):
                mappings["contributions"] = df.columns[i]
                break

        distrib_keywords = ["distribution", "distrib", "payout", "dividend"]
        for i, col in enumerate(columns):
            if any(keyword in col for keyword in distrib_keywords):
                mappings["distributions"] = df.columns[i]
                break

    elif file_type == "index":
        # Price column detection
        price_keywords = ["price", "level", "index", "value", "close", "closing"]
        for i, col in enumerate(columns):
            if any(keyword in col for keyword in price_keywords):
                mappings["price"] = df.columns[i]
                break

    return mappings


def validate_csv_structure(
    file_path: str | Path,
) -> tuple[pd.DataFrame, list[str]]:
    """
    Validate basic CSV structure and return DataFrame with errors.
    """
    # Convert string to Path object if needed
    if isinstance(file_path, str):
        file_path = Path(file_path)

    errors = []

    if not file_path.exists():
        errors.append(f"File not found: {file_path}")
        return None, errors

    if file_path.stat().st_size == 0:
        errors.append("File is empty")
        return None, errors

    if file_path.stat().st_size > 50 * 1024 * 1024:  # 50MB limit
        errors.append("File too large (>50MB)")
        return None, errors

    try:
        # Try to read the file
        if file_path.suffix.lower() == ".csv":
            # Try different separators
            for sep in [",", ";", "\t", "|"]:
                try:
                    df = pd.read_csv(file_path, sep=sep, nrows=5)
                    if len(df.columns) > 1:  # Found the right separator
                        df = pd.read_csv(file_path, sep=sep)
                        break
                except (pd.errors.ParserError, UnicodeDecodeError, PermissionError):
                    continue
            else:
                errors.append("Could not parse CSV file")
                return None, errors

        elif file_path.suffix.lower() in [".xlsx", ".xls"]:
            try:
                df = pd.read_excel(file_path)
            except Exception as e:
                errors.append(f"Could not read Excel file: {str(e)}")
                return None, errors
        else:
            errors.append(f"Unsupported file type: {file_path.suffix}")
            return None, errors

    except Exception as e:
        errors.append(f"Failed to read file: {str(e)}")
        return None, errors

    # Basic structure validation
    if df.empty:
        errors.append("File contains no data")
        return df, errors

    if len(df.columns) < 2:
        errors.append("File must have at least 2 columns")

    if len(df) < 3:
        errors.append("File must have at least 3 data rows")

    return df, errors


def validate_fund_file(file_path: str | Path) -> list[str]:
    """
    Validate fund cashflow file and return list of error strings.
    """
    # Convert string to Path object if needed
    if isinstance(file_path, str):
        file_path = Path(file_path)

    errors = []

    # Basic structure validation
    df, structure_errors = validate_csv_structure(file_path)
    errors.extend(structure_errors)

    if df is None or structure_errors:
        return errors

    # Detect column mappings
    mappings = detect_column_mappings(df, "fund")

    # Check required columns
    required_columns = ["date", "cashflow", "nav"]
    missing_required = []

    for req_col in required_columns:
        if req_col not in mappings:
            missing_required.append(req_col)

    if missing_required:
        errors.append(
            f"Could not identify required columns: {', '.join(missing_required)}"
        )
        errors.append(f"Available columns: {', '.join(df.columns.tolist())}")

    return errors


def validate_index_file(file_path: str | Path) -> list[str]:
    """
    Validate index price file and return list of error strings.
    """
    # Convert string to Path object if needed
    if isinstance(file_path, str):
        file_path = Path(file_path)

    errors = []

    # Basic structure validation
    df, structure_errors = validate_csv_structure(file_path)
    errors.extend(structure_errors)

    if df is None or structure_errors:
        return errors

    # Detect column mappings
    mappings = detect_column_mappings(df, "index")

    # Check required columns
    required_columns = ["date", "price"]
    missing_required = []

    for req_col in required_columns:
        if req_col not in mappings:
            missing_required.append(req_col)

    if missing_required:
        errors.append(
            f"Could not identify required columns: {', '.join(missing_required)}"
        )
        errors.append(f"Available columns: {', '.join(df.columns.tolist())}")

    return errors


def create_upload_metadata(file_path: Path, df: pd.DataFrame = None) -> UploadMeta:
    """Create metadata object for uploaded file."""
    # Determine file type
    file_ext = file_path.suffix.lower()
    if file_ext == ".csv":
        file_type = FileTypeEnum.CSV
    elif file_ext == ".xlsx":
        file_type = FileTypeEnum.XLSX
    elif file_ext == ".xls":
        file_type = FileTypeEnum.XLS
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")

    metadata = UploadMeta(
        filename=file_path.name, file_size=file_path.stat().st_size, file_type=file_type
    )

    if df is not None:
        metadata.row_count = len(df)
        metadata.column_count = len(df.columns)

        # Try to detect date range
        mappings = detect_column_mappings(df, "fund")  # Default to fund type
        if "date" in mappings:
            try:
                date_col = mappings["date"]
                dates = pd.to_datetime(df[date_col], errors="coerce")
                valid_dates = dates.dropna()
                if not valid_dates.empty:
                    metadata.date_range = {
                        "start": valid_dates.min().strftime("%Y-%m-%d"),
                        "end": valid_dates.max().strftime("%Y-%m-%d"),
                    }
            except (ValueError, TypeError, AttributeError):
                pass

        metadata.detected_columns = mappings

    return metadata


def validate_file_comprehensive(
    file_path: str | Path, file_type: str = "fund"
) -> ValidationResult:
    """
    Comprehensive file validation returning detailed ValidationResult.
    """
    # Convert string to Path object if needed
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # Basic structure check
    df, structure_errors = validate_csv_structure(file_path)

    if structure_errors:
        return ValidationResult(is_valid=False, errors=structure_errors)

    # Type-specific validation
    if file_type == "fund":
        validation_errors = validate_fund_file(file_path)
    elif file_type == "index":
        validation_errors = validate_index_file(file_path)
    else:
        return ValidationResult(
            is_valid=False, errors=[f"Unknown file type: {file_type}"]
        )

    # Create metadata
    try:
        metadata = create_upload_metadata(file_path, df)
        detected_mappings = detect_column_mappings(df, file_type)
    except Exception as e:
        validation_errors.append(f"Failed to create metadata: {str(e)}")
        metadata = None
        detected_mappings = None

    return ValidationResult(
        is_valid=len(validation_errors) == 0,
        errors=validation_errors,
        metadata=metadata,
        detected_mappings=detected_mappings,
    )
