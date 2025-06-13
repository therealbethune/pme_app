"""
PME Engine - Redirects to Analysis Engine Implementation
The PME calculations have been integrated into analysis_engine.py for better maintainability.
This file provides compatibility layer for any code that still imports PMEEngine.
"""

import os
import tempfile
from enum import Enum
from typing import Optional

import pandas as pd
from analysis_engine import PMEAnalysisEngine


class BenchmarkType(Enum):
    """Benchmark type enumeration for compatibility."""

    PRICE_ONLY = "price_only"
    TOTAL_RETURN = "total_return"


class PMEResult:
    """PME calculation result wrapper."""

    def __init__(self, value: float, alpha: float | None = None):
        self.value = value
        self.alpha = alpha


class PMEEngine:
    """
    Compatibility wrapper for the old PME Engine interface.
    Delegates to PMEAnalysisEngine for actual calculations.
    """

    def __init__(
        self,
        fund_data: pd.DataFrame,
        benchmark_data: pd.DataFrame,
        benchmark_type: BenchmarkType = BenchmarkType.PRICE_ONLY,
    ):
        """Initialize PME Engine with fund and benchmark data."""
        self.fund_data = fund_data.copy()
        self.benchmark_data = benchmark_data.copy()
        self.benchmark_type = benchmark_type
        self.analysis_engine = PMEAnalysisEngine()

        # Save data to temporary files to work with analysis engine
        try:
            # Save fund data
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as f:
                self.fund_data.to_csv(f.name, index=False)
                self.fund_temp_path = f.name

            # Save benchmark data
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as f:
                self.benchmark_data.to_csv(f.name, index=False)
                self.benchmark_temp_path = f.name

            # Load data into analysis engine
            self.analysis_engine.load_fund_data(self.fund_temp_path)
            self.analysis_engine.load_index_data(self.benchmark_temp_path)

        except Exception as e:
            raise ValueError(f"Failed to initialize PME Engine: {str(e)}")

    def calculate_kaplan_schoar_pme(self) -> PMEResult:
        """Calculate Kaplan-Schoar PME ratio."""
        try:
            results = self.analysis_engine.calculate_pme_metrics()
            pme_metrics = results.get("metrics", {}).get("pme_metrics", {})

            ks_pme = pme_metrics.get("kaplan_schoar_pme", 1.0)
            alpha = pme_metrics.get("direct_alpha", 0.0)

            return PMEResult(value=ks_pme, alpha=alpha)

        except Exception:
            return PMEResult(value=1.0, alpha=0.0)  # Default values on error

    def calculate_pme_plus(self) -> PMEResult:
        """Calculate PME+ metric."""
        try:
            results = self.analysis_engine.calculate_pme_metrics()
            pme_metrics = results.get("metrics", {}).get("pme_metrics", {})

            pme_plus = pme_metrics.get("pme_plus_lambda", 1.0)

            return PMEResult(value=pme_plus)

        except Exception:
            return PMEResult(value=1.0)  # Default value on error

    def calculate_direct_alpha(self) -> PMEResult:
        """Calculate Direct Alpha."""
        try:
            results = self.analysis_engine.calculate_pme_metrics()
            pme_metrics = results.get("metrics", {}).get("pme_metrics", {})

            alpha = pme_metrics.get("direct_alpha", 0.0)

            return PMEResult(value=alpha)

        except Exception:
            return PMEResult(value=0.0)  # Default value on error

    def calculate_long_nickels_pme(self) -> PMEResult:
        """Calculate Long-Nickels PME."""
        try:
            results = self.analysis_engine.calculate_pme_metrics()
            pme_metrics = results.get("metrics", {}).get("pme_metrics", {})

            ln_pme = pme_metrics.get("long_nickels_pme_irr", 0.0)

            return PMEResult(value=ln_pme)

        except Exception:
            return PMEResult(value=0.0)  # Default value on error

    def __del__(self):
        """Cleanup temporary files."""
        try:
            if hasattr(self, "fund_temp_path") and os.path.exists(self.fund_temp_path):
                os.unlink(self.fund_temp_path)
            if hasattr(self, "benchmark_temp_path") and os.path.exists(
                self.benchmark_temp_path
            ):
                os.unlink(self.benchmark_temp_path)
        except Exception:
            pass  # Ignore cleanup errors
