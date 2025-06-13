"""
File validation service for PME Calculator.
Validates fund and index data files for structure and content integrity.
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Union
import re
import chardet

from .schemas import (
    ValidationResult,
    UploadMeta,
    FileTypeEnum,
    FundDataSchema,
    IndexDataSchema,
    CashflowRow,
    NavRow,
)


class FileValidationError(Exception):
    """Custom exception for file validation errors."""

    pass


def detect_file_encoding(file_path: Union[str, Path]) -> str:
    """Detect file encoding using chardet."""
    try:
        with open(file_path, "rb") as f:
            raw_data = f.read(10000)  # Read first 10KB for detection
            result = chardet.detect(raw_data)
            return result.get("encoding", "utf-8") or "utf-8"
    except Exception:
        return "utf-8"


def detect_column_mappings(df: pd.DataFrame, file_type: str = "fund") -> Dict[str, str]:
    """
    Intelligently detect column mappings based on common patterns.
    Returns dict mapping detected column -> standard column name.
    """
    mappings = {}
    columns = [col.lower().strip() for col in df.columns]

    if file_type == "fund":
        # Fund file column patterns
        date_patterns = [
            "date",
            "period",
            "as_of",
            "valuation_date",
            "quarter",
            "month",
        ]
        cashflow_patterns = [
            "cashflow",
            "cash_flow",
            "net_cashflow",
            "cf",
            "cash_flows",
            "contributions_distributions",
            "net_cf",
            "cash_flow_amount",
        ]
        nav_patterns = [
            "nav",
            "net_asset_value",
            "value",
            "valuation",
            "fund_value",
            "portfolio_value",
        ]
        contrib_patterns = [
            "contributions",
            "contribution",
            "calls",
            "capital_calls",
            "drawdowns",
        ]
        distrib_patterns = ["distributions", "distribution", "proceeds", "realizations"]

        # Find best matches
        for col in columns:
            col_clean = re.sub(r"[^a-z0-9_]", "", col)

            # Date column
            if not mappings.get("date") and any(
                pattern in col_clean for pattern in date_patterns
            ):
                mappings["date"] = df.columns[columns.index(col)]

            # Cashflow column
            elif not mappings.get("cashflow") and any(
                pattern in col_clean for pattern in cashflow_patterns
            ):
                mappings["cashflow"] = df.columns[columns.index(col)]

            # NAV column
            elif not mappings.get("nav") and any(
                pattern in col_clean for pattern in nav_patterns
            ):
                mappings["nav"] = df.columns[columns.index(col)]

            # Contributions
            elif not mappings.get("contributions") and any(
                pattern in col_clean for pattern in contrib_patterns
            ):
                mappings["contributions"] = df.columns[columns.index(col)]

            # Distributions
            elif not mappings.get("distributions") and any(
                pattern in col_clean for pattern in distrib_patterns
            ):
                mappings["distributions"] = df.columns[columns.index(col)]

    elif file_type == "index":
        # Index file column patterns
        date_patterns = ["date", "period", "as_of", "month", "quarter"]
        price_patterns = [
            "price",
            "level",
            "index_level",
            "value",
            "close",
            "closing_price",
            "index",
        ]
        return_patterns = ["return", "returns", "pct_change", "change", "performance"]

        for col in columns:
            col_clean = re.sub(r"[^a-z0-9_]", "", col)

            # Date column
            if not mappings.get("date") and any(
                pattern in col_clean for pattern in date_patterns
            ):
                mappings["date"] = df.columns[columns.index(col)]

            # Price column
            elif not mappings.get("price") and any(
                pattern in col_clean for pattern in price_patterns
            ):
                mappings["price"] = df.columns[columns.index(col)]

            # Returns column
            elif not mappings.get("returns") and any(
                pattern in col_clean for pattern in return_patterns
            ):
                mappings["returns"] = df.columns[columns.index(col)]

    return mappings


def validate_csv_structure(
    file_path: Union[str, Path],
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Validate basic CSV structure and return DataFrame with errors.
    """
    errors = []
    file_path = Path(file_path)

    if not file_path.exists():
        errors.append(f"File not found: {file_path}")
        return None, errors

    if file_path.stat().st_size == 0:
        errors.append("File is empty")
        return None, errors

    if file_path.stat().st_size > 50 * 1024 * 1024:  # 50MB limit
        errors.append("File too large (>50MB)")
        return None, errors

    # Detect encoding
    encoding = detect_file_encoding(file_path)

    try:
        # Try to read the file
        if file_path.suffix.lower() == ".csv":
            # Try different separators
            for sep in [",", ";", "\t", "|"]:
                try:
                    df = pd.read_csv(file_path, encoding=encoding, sep=sep, nrows=5)
                    if len(df.columns) > 1:  # Found the right separator
                        df = pd.read_csv(file_path, encoding=encoding, sep=sep)
                        break
                except:
                    continue
            else:
                errors.append("Could not parse CSV file with any common separator")
                return None, errors

        elif file_path.suffix.lower() in [".xlsx", ".xls"]:
            try:
                df = pd.read_excel(
                    file_path,
                    engine="openpyxl" if file_path.suffix == ".xlsx" else "xlrd",
                )
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

    # Check for completely empty columns
    empty_cols = df.columns[df.isnull().all()].tolist()
    if empty_cols:
        errors.append(f"Empty columns found: {', '.join(empty_cols)}")

    return df, errors


def validate_fund_file(file_path: Union[str, Path]) -> List[str]:
    """
    Validate fund cashflow file and return list of error strings.
    Empty list means validation passed.
    """
    errors = []
    file_path = Path(file_path)

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

    try:
        # Validate data content using Pydantic models
        rows_data = []
        date_col = mappings["date"]
        cashflow_col = mappings["cashflow"]
        nav_col = mappings["nav"]
        contrib_col = mappings.get("contributions")
        distrib_col = mappings.get("distributions")

        for idx, row in df.iterrows():
            try:
                row_dict = {
                    "date": row[date_col],
                    "cashflow": row[cashflow_col],
                    "nav": row[nav_col],
                }

                if contrib_col and pd.notna(row.get(contrib_col)):
                    row_dict["contributions"] = row[contrib_col]

                if distrib_col and pd.notna(row.get(distrib_col)):
                    row_dict["distributions"] = row[distrib_col]

                # Validate single row
                cashflow_row = CashflowRow(**row_dict)
                rows_data.append(cashflow_row)

            except Exception as e:
                errors.append(
                    f"Row {idx + 2}: {str(e)}"
                )  # +2 for header and 0-indexing

        if not errors and rows_data:
            # Validate complete dataset
            try:
                fund_data = FundDataSchema(rows=rows_data)
            except Exception as e:
                errors.append(f"Dataset validation failed: {str(e)}")

    except Exception as e:
        errors.append(f"Data validation failed: {str(e)}")

    return errors


def validate_index_file(file_path: Union[str, Path]) -> List[str]:
    """
    Validate index price file and return list of error strings.
    Empty list means validation passed.
    """
    errors = []
    file_path = Path(file_path)

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

    try:
        # Validate data content using Pydantic models
        rows_data = []
        date_col = mappings["date"]
        price_col = mappings["price"]
        returns_col = mappings.get("returns")

        for idx, row in df.iterrows():
            try:
                row_dict = {"date": row[date_col], "price": row[price_col]}

                if returns_col and pd.notna(row.get(returns_col)):
                    row_dict["returns"] = row[returns_col]

                # Validate single row
                nav_row = NavRow(**row_dict)
                rows_data.append(nav_row)

            except Exception as e:
                errors.append(
                    f"Row {idx + 2}: {str(e)}"
                )  # +2 for header and 0-indexing

        if not errors and rows_data:
            # Validate complete dataset
            try:
                index_data = IndexDataSchema(rows=rows_data)
            except Exception as e:
                errors.append(f"Dataset validation failed: {str(e)}")

    except Exception as e:
        errors.append(f"Data validation failed: {str(e)}")

    return errors


def create_upload_metadata(
    file_path: Union[str, Path], df: pd.DataFrame = None
) -> UploadMeta:
    """Create metadata object for uploaded file."""
    file_path = Path(file_path)

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
        mappings = detect_column_mappings(df)
        if "date" in mappings:
            try:
                date_col = mappings["date"]
                dates = pd.to_datetime(df[date_col], errors="coerce")
                valid_dates = dates.dropna()
                if not valid_dates.empty:
                    metadata.date_range = {
                        "start": valid_dates.min().date(),
                        "end": valid_dates.max().date(),
                    }
            except:
                pass

        metadata.detected_columns = mappings

    return metadata


def validate_file_comprehensive(
    file_path: Union[str, Path], file_type: str = "fund"
) -> ValidationResult:
    """
    Comprehensive file validation returning detailed ValidationResult.
    """
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
