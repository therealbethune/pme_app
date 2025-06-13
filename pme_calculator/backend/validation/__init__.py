"""
PME Calculator validation package.
Provides Pydantic models and file validation for financial data.
"""

from .schemas import (
    CashflowRow,
    NavRow,
    UploadMeta,
    AnalysisRequest,
    ValidationResult,
    FundDataSchema,
    IndexDataSchema,
)

from .file_check import (
    validate_fund_file,
    validate_index_file,
    validate_csv_structure,
    detect_column_mappings,
)

__all__ = [
    "CashflowRow",
    "NavRow",
    "UploadMeta",
    "AnalysisRequest",
    "ValidationResult",
    "FundDataSchema",
    "IndexDataSchema",
    "validate_fund_file",
    "validate_index_file",
    "validate_csv_structure",
    "detect_column_mappings",
]
