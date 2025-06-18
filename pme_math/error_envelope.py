"""
Phase 1: Error Envelope System - Structured error handling for PME calculations

Provides graceful error handling and recovery mechanisms for PME analysis,
replacing silent failures with actionable error information.

Key Features:
- Structured error responses with context
- Partial results when possible
- Error classification and recovery suggestions
- Performance and diagnostic information
"""

import logging
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ErrorSeverity(Enum):
    """Error severity levels for PME calculations."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categories of errors in PME calculations."""

    DATA_ALIGNMENT = "data_alignment"
    DATA_VALIDATION = "data_validation"
    CALCULATION = "calculation"
    PERFORMANCE = "performance"
    CONFIGURATION = "configuration"
    SYSTEM = "system"


@dataclass
class ErrorDetail:
    """Detailed error information with context."""

    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    code: str
    context: dict[str, Any] = field(default_factory=dict)
    suggestion: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations."""

    execution_time_ms: float
    memory_usage_mb: float | None = None
    rows_processed: int | None = None
    cache_hit_rate: float | None = None


@dataclass
class ErrorEnvelope(Generic[T]):
    """
    Envelope containing operation results, errors, and metadata.

    This replaces boolean success/failure with rich error context
    and allows partial results when operations can be recovered.
    """

    success: bool
    data: T | None = None
    errors: list[ErrorDetail] = field(default_factory=list)
    warnings: list[ErrorDetail] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    performance: PerformanceMetrics | None = None

    @property
    def has_errors(self) -> bool:
        """Check if envelope contains any errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if envelope contains any warnings."""
        return len(self.warnings) > 0

    @property
    def has_critical_errors(self) -> bool:
        """Check if envelope contains critical errors."""
        return any(error.severity == ErrorSeverity.CRITICAL for error in self.errors)

    @property
    def error_summary(self) -> str:
        """Get a summary of all errors."""
        if not self.has_errors:
            return "No errors"

        error_counts = {}
        for error in self.errors:
            severity = error.severity.value
            error_counts[severity] = error_counts.get(severity, 0) + 1

        return ", ".join(
            [f"{count} {severity}" for severity, count in error_counts.items()]
        )


def envelope_ok(
    data: T,
    metadata: dict[str, Any] | None = None,
    performance: PerformanceMetrics | None = None,
) -> ErrorEnvelope[T]:
    """Create a successful envelope with data."""
    return ErrorEnvelope(
        success=True, data=data, metadata=metadata or {}, performance=performance
    )


def envelope_partial(
    data: T | None,
    warnings: list[ErrorDetail],
    metadata: dict[str, Any] | None = None,
    performance: PerformanceMetrics | None = None,
) -> ErrorEnvelope[T]:
    """Create a partial success envelope with warnings."""
    return ErrorEnvelope(
        success=True,
        data=data,
        warnings=warnings,
        metadata=metadata or {},
        performance=performance,
    )


def envelope_fail(
    errors: list[ErrorDetail],
    data: T | None = None,
    metadata: dict[str, Any] | None = None,
    performance: PerformanceMetrics | None = None,
) -> ErrorEnvelope[T]:
    """Create a failed envelope with errors."""
    return ErrorEnvelope(
        success=False,
        data=data,
        errors=errors,
        metadata=metadata or {},
        performance=performance,
    )


def wrap_with_envelope(func):
    """
    Decorator to wrap functions with error envelope handling.

    Automatically catches exceptions and converts them to structured errors.
    """

    def wrapper(*args, **kwargs):
        start_time = datetime.now()

        try:
            result = func(*args, **kwargs)

            # Calculate performance metrics
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            performance = PerformanceMetrics(execution_time_ms=execution_time)

            # If function already returns an envelope, return it
            if isinstance(result, ErrorEnvelope):
                if result.performance is None:
                    result.performance = performance
                return result

            # Otherwise wrap the result in a success envelope
            return envelope_ok(result, performance=performance)

        except Exception as e:
            # Convert exception to structured error
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            performance = PerformanceMetrics(execution_time_ms=execution_time)

            error = ErrorDetail(
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.ERROR,
                message=str(e),
                code=type(e).__name__,
                context={
                    "function": func.__name__,
                    "args": str(args)[:200],
                    "traceback": traceback.format_exc(),
                },
                suggestion="Check input data and parameters",
            )

            logger.error(f"Function {func.__name__} failed: {e}")
            return envelope_fail([error], performance=performance)

    return wrapper


class ErrorCollector:
    """Helper class to collect and manage errors during complex operations."""

    def __init__(self):
        self.errors: list[ErrorDetail] = []
        self.warnings: list[ErrorDetail] = []

    def add_error(
        self,
        category: ErrorCategory,
        severity: ErrorSeverity,
        message: str,
        code: str,
        context: dict[str, Any] | None = None,
        suggestion: str | None = None,
    ):
        """Add an error to the collector."""
        error = ErrorDetail(
            category=category,
            severity=severity,
            message=message,
            code=code,
            context=context or {},
            suggestion=suggestion,
        )

        if severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
            self.errors.append(error)
            logger.error(f"[{category.value}] {message}")
        else:
            self.warnings.append(error)
            logger.warning(f"[{category.value}] {message}")

    def add_data_alignment_error(self, message: str, context: dict[str, Any]):
        """Add a data alignment error with standard context."""
        self.add_error(
            category=ErrorCategory.DATA_ALIGNMENT,
            severity=ErrorSeverity.ERROR,
            message=message,
            code="ALIGNMENT_MISMATCH",
            context=context,
            suggestion="Use DataAlignmentEngine to align datasets before calculation",
        )

    def add_validation_warning(self, message: str, context: dict[str, Any]):
        """Add a validation warning."""
        self.add_error(
            category=ErrorCategory.DATA_VALIDATION,
            severity=ErrorSeverity.WARNING,
            message=message,
            code="VALIDATION_WARNING",
            context=context,
            suggestion="Review input data quality",
        )

    def has_errors(self) -> bool:
        """Check if collector has any errors."""
        return len(self.errors) > 0

    def has_critical_errors(self) -> bool:
        """Check if collector has critical errors."""
        return any(error.severity == ErrorSeverity.CRITICAL for error in self.errors)

    def to_envelope(
        self,
        data: T | None = None,
        metadata: dict[str, Any] | None = None,
        performance: PerformanceMetrics | None = None,
    ) -> ErrorEnvelope[T]:
        """Convert collector state to an error envelope."""
        if self.has_errors():
            return ErrorEnvelope(
                success=False,
                data=data,
                errors=self.errors,
                warnings=self.warnings,  # Include warnings even when there are errors
                metadata=metadata or {},
                performance=performance,
            )
        elif self.warnings:
            return envelope_partial(
                data=data,
                warnings=self.warnings,
                metadata=metadata,
                performance=performance,
            )
        else:
            return envelope_ok(data=data, metadata=metadata, performance=performance)


# Pre-defined common errors for PME calculations
def create_alignment_error(fund_shape: tuple, index_shape: tuple) -> ErrorDetail:
    """Create a standard data alignment error."""
    return ErrorDetail(
        category=ErrorCategory.DATA_ALIGNMENT,
        severity=ErrorSeverity.ERROR,
        message=f"Data alignment mismatch: fund data has {fund_shape[0]} rows, index data has {index_shape[0]} rows",
        code="SHAPE_MISMATCH",
        context={"fund_shape": fund_shape, "index_shape": index_shape},
        suggestion="Use DataAlignmentEngine.align_fund_and_index() to fix alignment issues",
    )


def create_missing_data_warning(
    missing_count: int, total_count: int, data_type: str
) -> ErrorDetail:
    """Create a standard missing data warning."""
    percentage = (missing_count / total_count) * 100 if total_count > 0 else 0

    return ErrorDetail(
        category=ErrorCategory.DATA_VALIDATION,
        severity=ErrorSeverity.WARNING if percentage < 10 else ErrorSeverity.ERROR,
        message=f"Missing data in {data_type}: {missing_count}/{total_count} ({percentage:.1f}%)",
        code="MISSING_DATA",
        context={
            "missing_count": missing_count,
            "total_count": total_count,
            "percentage": percentage,
            "data_type": data_type,
        },
        suggestion="Consider using forward_fill or interpolation strategies",
    )
