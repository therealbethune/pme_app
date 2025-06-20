"""
PME Math - Pure mathematical functions for PME calculations.

This package contains standalone mathematical functions for Private Market Equivalent
calculations without any I/O or logging dependencies.
"""

from .metrics import direct_alpha, ks_pme, ln_pme, pme_plus, xirr_wrapper

__all__ = ["xirr_wrapper", "ks_pme", "ln_pme", "direct_alpha", "pme_plus"]

__version__ = "1.0.0"
