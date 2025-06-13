"""
Simplified Pydantic schemas for PME Calculator - optimized for production use.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FileTypeEnum(str, Enum):
    CSV = "csv"
    XLSX = "xlsx"
    XLS = "xls"


class AnalysisMethodEnum(str, Enum):
    KAPLAN_SCHOAR = "Kaplan Schoar"
    MODIFIED_PME = "Modified PME"
    DIRECT_ALPHA = "Direct Alpha"


class UploadMeta(BaseModel):
    """Metadata for uploaded files."""

    filename: str = Field(..., max_length=255)
    file_size: int = Field(..., gt=0)
    file_type: FileTypeEnum
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    row_count: int | None = Field(None, ge=0)
    column_count: int | None = Field(None, ge=0)
    date_range: dict[str, str] | None = None
    detected_columns: dict[str, str] | None = None


class ValidationResult(BaseModel):
    """Result of file validation."""

    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: UploadMeta | None = None
    detected_mappings: dict[str, str] | None = None


class AnalysisRequest(BaseModel):
    """Request for PME analysis."""

    fund_file_id: str
    index_file_id: str | None = None
    method: AnalysisMethodEnum = AnalysisMethodEnum.KAPLAN_SCHOAR
    risk_free_rate: float = Field(0.025, ge=0, le=1)
    confidence_level: float = Field(0.95, gt=0, lt=1)
    start_date: str | None = None
    end_date: str | None = None


class AnalysisResponse(BaseModel):
    """Response from PME analysis."""

    request_id: str
    success: bool
    metrics: dict[str, Any] | None = None
    charts: dict[str, Any] | None = None
    summary: dict[str, Any] | None = None
    errors: list[str] = Field(default_factory=list)
    processing_time_ms: float | None = None


class UploadResponse(BaseModel):
    """Response model for file uploads."""

    success: bool
    file_id: str
    filename: str
    validation: ValidationResult
    message: str
