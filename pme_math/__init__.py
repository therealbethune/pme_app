"""
PME Math Module - Phase 1 Implementation

High-performance data processing and error handling for PME calculations.
"""

from .alignment_engine import DataAlignmentEngine, AlignmentStrategy
from .error_envelope import (
    ErrorEnvelope,
    ErrorDetail,
    ErrorSeverity,
    ErrorCategory,
    envelope_ok,
    envelope_fail,
    envelope_partial,
    ErrorCollector,
    wrap_with_envelope,
    create_alignment_error,
    create_missing_data_warning,
)

__version__ = "1.0.0"
__all__ = [
    "DataAlignmentEngine",
    "AlignmentStrategy",
    "ErrorEnvelope",
    "ErrorDetail",
    "ErrorSeverity",
    "ErrorCategory",
    "envelope_ok",
    "envelope_fail",
    "envelope_partial",
    "ErrorCollector",
    "wrap_with_envelope",
    "create_alignment_error",
    "create_missing_data_warning",
]
