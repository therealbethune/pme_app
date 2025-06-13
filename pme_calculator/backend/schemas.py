"""
Phase 1A: Data Contracts & Validation Schemas
Comprehensive data validation for PME Calculator using Pydantic.
"""

from __future__ import annotations
from pydantic import BaseModel, field_validator, Field
from typing import List, Optional, Union, Tuple
from datetime import datetime, date
from enum import Enum
import pandas as pd


# Data Quality Enums
class DataQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    INVALID = "invalid"


class CashFlowType(str, Enum):
    CONTRIBUTION = "contribution"
    DISTRIBUTION = "distribution"
    NAV_UPDATE = "nav_update"
    UNKNOWN = "unknown"


class ValidationSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# Core Data Models
class FundCashFlowRecord(BaseModel):
    """Individual fund cash flow record with validation."""

    date: Union[datetime, date, str]
    cashflow: float
    nav: float
    description: Optional[str] = None
    type: Optional[CashFlowType] = CashFlowType.UNKNOWN

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            try:
                return pd.to_datetime(v).date()
            except:
                raise ValueError(f"Invalid date format: {v}")
        elif isinstance(v, datetime):
            return v.date()
        return v

    @field_validator("cashflow")
    @classmethod
    def validate_cashflow(cls, v):
        if pd.isna(v) or not isinstance(v, (int, float)):
            raise ValueError("Cash flow must be a valid number")
        return float(v)

    @field_validator("nav")
    @classmethod
    def validate_nav(cls, v):
        if pd.isna(v) or not isinstance(v, (int, float)):
            raise ValueError("NAV must be a valid number")
        if v < 0:
            raise ValueError("NAV cannot be negative")
        return float(v)


class IndexRecord(BaseModel):
    """Individual index/benchmark record with validation."""

    date: Union[datetime, date, str]
    price: float
    total_return_index: Optional[float] = None
    dividend_yield: Optional[float] = None

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            try:
                return pd.to_datetime(v).date()
            except:
                raise ValueError(f"Invalid date format: {v}")
        elif isinstance(v, datetime):
            return v.date()
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if pd.isna(v) or not isinstance(v, (int, float)):
            raise ValueError("Price must be a valid number")
        if v <= 0:
            raise ValueError("Price must be positive")
        return float(v)


# Validation Result Models
class ValidationError(BaseModel):
    """Data validation error with context."""

    row_index: int
    column: str
    error_type: str
    message: str
    severity: ValidationSeverity
    suggested_fix: Optional[str] = None


class DataQualityReport(BaseModel):
    """Comprehensive data quality assessment."""

    overall_score: float = Field(..., ge=0, le=1)
    quality_level: DataQuality
    total_records: int
    valid_records: int
    error_count: int
    warning_count: int
    errors: List[ValidationError] = Field(default_factory=list)
    completeness_score: float
    consistency_score: float
    timeliness_score: float
    suggestions: List[str] = Field(default_factory=list)


class ColumnMapping(BaseModel):
    """Column mapping with confidence score."""

    original_name: str
    standardized_name: str
    data_type: str
    confidence: float = Field(..., ge=0, le=1)
    transformations: List[str] = Field(default_factory=list)


class DatasetMetadata(BaseModel):
    """Dataset metadata and quality information."""

    name: str
    rows: int
    columns: int
    date_range: Tuple[datetime, datetime]
    data_quality_score: float
    missing_data_percentage: float
    column_mappings: List[ColumnMapping] = Field(default_factory=list)


# Analysis Request Models
class AnalysisRequest(BaseModel):
    """PME analysis request with parameters."""

    fund_file_id: str
    index_file_id: Optional[str] = None
    calculation_methods: List[str] = Field(
        default=["kaplan_schoar", "pme_plus", "direct_alpha"]
    )
    benchmark_index: Optional[str] = "SP500"
    risk_free_rate: float = 0.025
    confidence_level: float = 0.95
    include_monte_carlo: bool = False
    include_stress_tests: bool = False


class CalculationParameters(BaseModel):
    """Calculation parameters for PME metrics."""

    irr_method: str = "newton_raphson"
    twr_frequency: str = "monthly"
    benchmark_adjustment: str = "none"
    currency: str = "USD"
    decimals: int = 4


# Comprehensive Validation Engine
class DataValidator:
    """Advanced data validation engine for PME calculations."""

    @staticmethod
    def validate_fund_data(df: pd.DataFrame) -> DataQualityReport:
        """Validate fund cash flow data comprehensively."""
        errors = []
        warnings = []

        # Check required columns
        required_columns = ["date", "cashflow", "nav"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            for col in missing_columns:
                errors.append(
                    ValidationError(
                        row_index=-1,
                        column=col,
                        error_type="missing_column",
                        message=f"Required column '{col}' is missing",
                        severity=ValidationSeverity.ERROR,
                        suggested_fix=f"Add '{col}' column to your data",
                    )
                )

        # Validate each record
        valid_records = 0
        for idx, row in df.iterrows():
            try:
                FundCashFlowRecord(**row.to_dict())
                valid_records += 1
            except Exception as e:
                errors.append(
                    ValidationError(
                        row_index=idx,
                        column="multiple",
                        error_type="validation_error",
                        message=str(e),
                        severity=ValidationSeverity.ERROR,
                    )
                )

        # Calculate quality scores
        completeness_score = 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
        consistency_score = min(1.0, valid_records / len(df)) if len(df) > 0 else 0
        timeliness_score = DataValidator._calculate_timeliness_score(df)
        overall_score = (completeness_score + consistency_score + timeliness_score) / 3

        # Determine quality level
        if overall_score >= 0.9:
            quality_level = DataQuality.EXCELLENT
        elif overall_score >= 0.8:
            quality_level = DataQuality.GOOD
        elif overall_score >= 0.7:
            quality_level = DataQuality.ACCEPTABLE
        elif overall_score >= 0.5:
            quality_level = DataQuality.POOR
        else:
            quality_level = DataQuality.INVALID

        # Generate suggestions
        suggestions = []
        if completeness_score < 0.9:
            suggestions.append("Fill in missing data values where possible")
        if consistency_score < 0.9:
            suggestions.append("Review data types and formats for consistency")
        if len(errors) > 0:
            suggestions.append(f"Address {len(errors)} validation errors")

        return DataQualityReport(
            overall_score=overall_score,
            quality_level=quality_level,
            total_records=len(df),
            valid_records=valid_records,
            error_count=len(errors),
            warning_count=len(warnings),
            errors=errors,
            completeness_score=completeness_score,
            consistency_score=consistency_score,
            timeliness_score=timeliness_score,
            suggestions=suggestions,
        )

    @staticmethod
    def validate_index_data(df: pd.DataFrame) -> DataQualityReport:
        """Validate index/benchmark data comprehensively."""
        errors = []
        warnings = []

        # Check required columns
        required_columns = ["date", "price"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            for col in missing_columns:
                errors.append(
                    ValidationError(
                        row_index=-1,
                        column=col,
                        error_type="missing_column",
                        message=f"Required column '{col}' is missing",
                        severity=ValidationSeverity.ERROR,
                        suggested_fix=f"Add '{col}' column to your data",
                    )
                )

        # Validate each record
        valid_records = 0
        for idx, row in df.iterrows():
            try:
                IndexRecord(**row.to_dict())
                valid_records += 1
            except Exception as e:
                errors.append(
                    ValidationError(
                        row_index=idx,
                        column="multiple",
                        error_type="validation_error",
                        message=str(e),
                        severity=ValidationSeverity.ERROR,
                    )
                )

        # Calculate quality scores
        completeness_score = 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
        consistency_score = min(1.0, valid_records / len(df)) if len(df) > 0 else 0
        timeliness_score = DataValidator._calculate_timeliness_score(df)
        overall_score = (completeness_score + consistency_score + timeliness_score) / 3

        # Determine quality level
        if overall_score >= 0.9:
            quality_level = DataQuality.EXCELLENT
        elif overall_score >= 0.8:
            quality_level = DataQuality.GOOD
        elif overall_score >= 0.7:
            quality_level = DataQuality.ACCEPTABLE
        elif overall_score >= 0.5:
            quality_level = DataQuality.POOR
        else:
            quality_level = DataQuality.INVALID

        suggestions = []
        if completeness_score < 0.9:
            suggestions.append("Fill in missing price data")
        if consistency_score < 0.9:
            suggestions.append("Check for data type inconsistencies")

        return DataQualityReport(
            overall_score=overall_score,
            quality_level=quality_level,
            total_records=len(df),
            valid_records=valid_records,
            error_count=len(errors),
            warning_count=len(warnings),
            errors=errors,
            completeness_score=completeness_score,
            consistency_score=consistency_score,
            timeliness_score=timeliness_score,
            suggestions=suggestions,
        )

    @staticmethod
    def _calculate_timeliness_score(df: pd.DataFrame) -> float:
        """Calculate data timeliness score based on date consistency."""
        if "date" not in df.columns or len(df) < 2:
            return 0.5

        try:
            dates = pd.to_datetime(df["date"])
            date_diffs = dates.diff().dropna()

            # Check for regular intervals
            mode_diff = (
                date_diffs.mode().iloc[0] if len(date_diffs.mode()) > 0 else None
            )
            if mode_diff:
                regular_intervals = (date_diffs == mode_diff).sum()
                timeliness_score = regular_intervals / len(date_diffs)
            else:
                timeliness_score = 0.5

            return min(1.0, timeliness_score)
        except:
            return 0.3

    @staticmethod
    def intelligent_column_mapping(
        columns: List[str], data_type: str = "fund"
    ) -> List[ColumnMapping]:
        """Intelligent column mapping with confidence scoring."""
        mappings = []

        if data_type == "fund":
            # Date mapping
            date_keywords = [
                "date",
                "period",
                "time",
                "month",
                "quarter",
                "year",
                "timestamp",
            ]
            cashflow_keywords = [
                "cashflow",
                "cash_flow",
                "cash flow",
                "cf",
                "net_cash",
                "amount",
                "contribution",
                "distribution",
            ]
            nav_keywords = ["nav", "net_asset_value", "value", "balance", "book_value"]

            for col in columns:
                col_lower = col.lower().strip()

                # Date column mapping
                date_confidence = max(
                    [0.9 if keyword in col_lower else 0 for keyword in date_keywords]
                )
                if date_confidence > 0.5:
                    mappings.append(
                        ColumnMapping(
                            original_name=col,
                            standardized_name="date",
                            data_type="datetime",
                            confidence=date_confidence,
                        )
                    )
                    continue

                # Cashflow mapping
                cf_confidence = max(
                    [
                        0.9 if keyword in col_lower else 0
                        for keyword in cashflow_keywords
                    ]
                )
                if cf_confidence > 0.5:
                    mappings.append(
                        ColumnMapping(
                            original_name=col,
                            standardized_name="cashflow",
                            data_type="float",
                            confidence=cf_confidence,
                        )
                    )
                    continue

                # NAV mapping
                nav_confidence = max(
                    [0.9 if keyword in col_lower else 0 for keyword in nav_keywords]
                )
                if nav_confidence > 0.5:
                    mappings.append(
                        ColumnMapping(
                            original_name=col,
                            standardized_name="nav",
                            data_type="float",
                            confidence=nav_confidence,
                        )
                    )
                    continue

                # Unmapped column
                mappings.append(
                    ColumnMapping(
                        original_name=col,
                        standardized_name="unknown",
                        data_type="unknown",
                        confidence=0.0,
                    )
                )

        elif data_type == "index":
            date_keywords = ["date", "period", "time", "month", "quarter", "year"]
            price_keywords = [
                "price",
                "level",
                "index",
                "value",
                "close",
                "closing",
                "adjusted",
            ]

            for col in columns:
                col_lower = col.lower().strip()

                # Date mapping
                date_confidence = max(
                    [0.9 if keyword in col_lower else 0 for keyword in date_keywords]
                )
                if date_confidence > 0.5:
                    mappings.append(
                        ColumnMapping(
                            original_name=col,
                            standardized_name="date",
                            data_type="datetime",
                            confidence=date_confidence,
                        )
                    )
                    continue

                # Price mapping
                price_confidence = max(
                    [0.9 if keyword in col_lower else 0 for keyword in price_keywords]
                )
                if price_confidence > 0.5:
                    mappings.append(
                        ColumnMapping(
                            original_name=col,
                            standardized_name="price",
                            data_type="float",
                            confidence=price_confidence,
                        )
                    )
                    continue

                # Unmapped column
                mappings.append(
                    ColumnMapping(
                        original_name=col,
                        standardized_name="unknown",
                        data_type="unknown",
                        confidence=0.0,
                    )
                )

        return mappings
