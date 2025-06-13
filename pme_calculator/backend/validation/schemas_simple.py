"""
Simplified Pydantic schemas for PME Calculator - optimized for production use.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from enum import Enum
import re

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
    row_count: Optional[int] = Field(None, ge=0)
    column_count: Optional[int] = Field(None, ge=0)
    date_range: Optional[Dict[str, str]] = None
    detected_columns: Optional[Dict[str, str]] = None


class ValidationResult(BaseModel):
    """Result of file validation."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Optional[UploadMeta] = None
    detected_mappings: Optional[Dict[str, str]] = None


class AnalysisRequest(BaseModel):
    """Request for PME analysis."""
    fund_file_id: str
    index_file_id: Optional[str] = None
    method: AnalysisMethodEnum = AnalysisMethodEnum.KAPLAN_SCHOAR
    risk_free_rate: float = Field(0.025, ge=0, le=1)
    confidence_level: float = Field(0.95, gt=0, lt=1)
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response from PME analysis."""
    request_id: str
    success: bool
    metrics: Optional[Dict[str, Any]] = None
    charts: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)
    processing_time_ms: Optional[float] = None


class UploadResponse(BaseModel):
    """Response model for file uploads."""
    success: bool
    file_id: str
    filename: str
    validation: ValidationResult
    message: str 