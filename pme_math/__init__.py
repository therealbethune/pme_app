"""
PME Math Module - Phase 1 Implementation

High-performance data processing and error handling for PME calculations.
"""

from .alignment_engine import AlignmentStrategy, DataAlignmentEngine
from .error_envelope import (
    ErrorCategory,
    ErrorCollector,
    ErrorDetail,
    ErrorEnvelope,
    ErrorSeverity,
    create_alignment_error,
    create_missing_data_warning,
    envelope_fail,
    envelope_ok,
    envelope_partial,
    wrap_with_envelope,
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
