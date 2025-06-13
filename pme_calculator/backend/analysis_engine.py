"""
Backward compatibility shim for analysis_engine.py

# deprecated – use pme_math.metrics
This module is deprecated. Import from analysis_engine_legacy or use pme_math.metrics directly.
"""

import warnings

# Re-export everything from legacy for backward compatibility
from analysis_engine_legacy import *

warnings.warn(
    "analysis_engine module is deprecated. Use analysis_engine_legacy for PMEAnalysisEngine "
    "or pme_math.metrics for mathematical functions.",
    DeprecationWarning,
    stacklevel=2
) 