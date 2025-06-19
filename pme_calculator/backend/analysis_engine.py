"""
Backward compatibility shim for analysis_engine.py

# deprecated – use pme_math.metrics
This module is deprecated. Import from analysis_engine_legacy or use pme_math.metrics directly.
"""

import warnings

# Re-export specific classes and functions from legacy for backward compatibility
from analysis_engine_legacy import (
    PMEAnalysisEngine,
    direct_alpha,
    ks_pme,
    make_json_serializable,
    safe_float,
    xirr_wrapper,
)

warnings.warn(
    "analysis_engine module is deprecated. Use analysis_engine_legacy for PMEAnalysisEngine "
    "or pme_math.metrics for mathematical functions.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export for backward compatibility
__all__ = [
    "PMEAnalysisEngine",
    "direct_alpha", 
    "ks_pme",
    "make_json_serializable",
    "safe_float",
    "xirr_wrapper",
]
