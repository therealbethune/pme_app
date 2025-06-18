"""
PME Calculator validation package.
Provides Pydantic models and file validation for financial data.
"""

from .file_check import (
    detect_column_mappings,
    validate_csv_structure,
    validate_fund_file,
    validate_index_file,
)
from .schemas import (
    AnalysisRequest,
    CashflowRow,
    FundDataSchema,
    IndexDataSchema,
    NavRow,
    UploadMeta,
    ValidationResult,
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
