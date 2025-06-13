"""
Pydantic schemas for PME Calculator data validation.
Enhanced version with proper validation functionality.
"""

from datetime import datetime
import datetime as dt
from decimal import Decimal
from typing import List, Optional, Dict, Any
from enum import Enum
import re

from pydantic import BaseModel, Field, field_validator, model_validator


class FileTypeEnum(str, Enum):
    CSV = "csv"
    XLSX = "xlsx" 
    XLS = "xls"


class AnalysisMethodEnum(str, Enum):
    KAPLAN_SCHOAR = "Kaplan Schoar"
    MODIFIED_PME = "Modified PME"
    DIRECT_ALPHA = "Direct Alpha"


def parse_date_value(value):
    """Parse date from string or datetime object."""
    if isinstance(value, (dt.date, datetime)):
        return value.date() if isinstance(value, datetime) else value
    
    if isinstance(value, str):
        # Try multiple date formats
        formats = [
            ('%Y-%m-%d', r'^\d{4}-\d{2}-\d{2}$'),  # YYYY-MM-DD
            ('%m/%d/%Y', r'^\d{2}/\d{2}/\d{4}$'),  # MM/DD/YYYY
            ('%m-%d-%Y', r'^\d{2}-\d{2}-\d{4}$'),  # MM-DD-YYYY
        ]
        
        for date_format, pattern in formats:
            if re.match(pattern, value):
                try:
                    return datetime.strptime(value, date_format).date()
                except ValueError:
                    continue
    
    raise ValueError(f"Invalid date format: {value}. Expected YYYY-MM-DD, MM/DD/YYYY, or MM-DD-YYYY")


def parse_decimal_value(value):
    """Parse decimal from string or numeric value."""
    if value is None:
        return value
    if isinstance(value, str):
        # Remove currency symbols and commas
        cleaned = re.sub(r'[$,\s]', '', value)
        if cleaned in ['', '-']:
            return 0.0
        value = cleaned
    try:
        return float(value)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid numeric value: {value}")


class CashflowRow(BaseModel):
    """Single row of fund cashflow data."""
    date: dt.date = Field(..., description="Date in YYYY-MM-DD format")
    cashflow: float = Field(..., description="Net cashflow (positive = contribution, negative = distribution)")
    nav: float = Field(..., ge=0, description="Net Asset Value, must be non-negative")
    contributions: Optional[float] = Field(None, ge=0, description="Explicit contributions if separate from cashflow")
    distributions: Optional[float] = Field(None, ge=0, description="Explicit distributions if separate from cashflow")
    
    @field_validator('date', mode='before')
    @classmethod
    def validate_date(cls, v):
        """Validate and normalize date formats."""
        return parse_date_value(v)
    
    @field_validator('cashflow', 'nav', 'contributions', 'distributions', mode='before')
    @classmethod
    def validate_decimal(cls, v):
        """Convert numeric values to float for processing."""
        return parse_decimal_value(v)
    
    @model_validator(mode='after')
    def validate_cashflow_components(self):
        """Ensure cashflow components are consistent."""
        if self.contributions is not None and self.distributions is not None:
            expected_cashflow = self.contributions - self.distributions
            if abs(self.cashflow - expected_cashflow) > 0.01:
                raise ValueError(
                    f"Cashflow {self.cashflow} doesn't match contributions {self.contributions} - distributions {self.distributions}"
                )
        return self


class NavRow(BaseModel):
    """Single row of NAV/index data."""
    date: dt.date = Field(..., description="Date in YYYY-MM-DD format") 
    price: float = Field(..., gt=0, description="Index price/level, must be positive")
    returns: Optional[float] = Field(None, description="Period returns if available")
    
    @field_validator('date', mode='before')
    @classmethod
    def validate_date(cls, v):
        """Validate and normalize date formats."""
        return parse_date_value(v)
    
    @field_validator('price', 'returns', mode='before')
    @classmethod
    def validate_decimal(cls, v):
        """Convert numeric values to float for processing."""
        return parse_decimal_value(v)


class FundDataSchema(BaseModel):
    """Complete fund dataset validation."""
    rows: List[CashflowRow] = Field(..., min_length=3, description="Minimum 3 data points required")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('rows')
    @classmethod
    def validate_date_sequence(cls, v):
        """Ensure dates are in chronological order."""
        if len(v) < 2:
            return v
            
        dates = [row.date for row in v]
        sorted_dates = sorted(dates)
        
        if dates != sorted_dates:
            raise ValueError("Dates must be in chronological order")
        
        # Check for duplicate dates
        if len(set(dates)) != len(dates):
            raise ValueError("Duplicate dates found in dataset")
        
        return v


class IndexDataSchema(BaseModel):
    """Complete index dataset validation."""
    rows: List[NavRow] = Field(..., min_length=3, description="Minimum 3 data points required")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('rows')
    @classmethod
    def validate_date_sequence(cls, v):
        """Ensure dates are in chronological order."""
        if len(v) < 2:
            return v
            
        dates = [row.date for row in v]
        sorted_dates = sorted(dates)
        
        if dates != sorted_dates:
            raise ValueError("Dates must be in chronological order")
        
        if len(set(dates)) != len(dates):
            raise ValueError("Duplicate dates found in dataset")
        
        return v


class UploadMeta(BaseModel):
    """Metadata for uploaded files."""
    filename: str = Field(..., max_length=255)
    file_size: int = Field(..., gt=0, description="File size in bytes")
    file_type: FileTypeEnum
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    row_count: Optional[int] = Field(None, ge=0)
    column_count: Optional[int] = Field(None, ge=0)
    date_range: Optional[Dict[str, str]] = None
    detected_columns: Optional[Dict[str, str]] = None
    
    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        """Validate filename."""
        if not v or v.isspace():
            raise ValueError("Filename cannot be empty")
        
        # Check for potentially dangerous characters
        forbidden_chars = ['<', '>', ':', '"', '|', '?', '*']
        if any(char in v for char in forbidden_chars):
            raise ValueError(f"Filename contains forbidden characters: {forbidden_chars}")
        
        return v.strip()


class ValidationResult(BaseModel):
    """Result of file validation."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Optional[UploadMeta] = None
    detected_mappings: Optional[Dict[str, str]] = None
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


class AnalysisRequest(BaseModel):
    """Request for PME analysis."""
    fund_file_id: str
    index_file_id: Optional[str] = None
    method: AnalysisMethodEnum = AnalysisMethodEnum.KAPLAN_SCHOAR
    risk_free_rate: float = Field(0.025, ge=0, le=1, description="Risk-free rate (default 2.5%)")
    confidence_level: float = Field(0.95, gt=0, lt=1, description="Confidence level (default 95%)")
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response from PME analysis."""
    request_id: str
    success: bool
    metrics: Optional[Dict[str, Any]] = None
    charts: Optional[Dict[str, List[Dict]]] = None
    summary: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)
    processing_time_ms: Optional[float] = None 