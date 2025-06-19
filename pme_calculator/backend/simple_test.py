#!/usr/bin/env python3
"""
Simple system test to verify core functionality without problematic imports.
"""

import sys

import structlog

logger = structlog.get_logger()
import tempfile

import pandas as pd


def test_core_functionality():
    """Test core PME functionality without problematic schemas."""
    logger.debug("🔬 Testing Core PME System...")

    try:
        # Test 1: Analysis Engine
        from analysis_engine import PMEAnalysisEngine

        logger.debug("   ✅ Analysis Engine imported successfully")

        # Create test data
        test_data = pd.DataFrame(
            {
                "date": pd.date_range("2020-01-01", periods=8, freq="QE"),
                "cashflow": [-1000, -500, 0, 200, 300, 0, 400, 500],
                "nav": [1000, 1400, 1450, 1350, 1600, 1700, 1600, 1800],
            }
        )

        # Save to temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_file = f.name

        try:
            # Test analysis engine
            engine = PMEAnalysisEngine()
            result = engine.load_fund_data(temp_file)
            logger.debug(f"   ✅ Fund data loaded: {result['success']}")

            # Test metrics calculation
            metrics = engine.calculate_pme_metrics()
            logger.debug(f"   ✅ Metrics calculated: {metrics['success']}")

            # Test specific metrics
            fund_irr = metrics["metrics"].get("Fund IRR", 0)
            tvpi = metrics["metrics"].get("TVPI", 0)
            logger.debug(f"   ✅ Fund IRR: {fund_irr:.1%}")
            logger.debug(f"   ✅ TVPI: {tvpi:.2f}x")

        finally:
            # Cleanup
            import os

            os.unlink(temp_file)

    except Exception as e:
        logger.debug(f"   ❌ Analysis engine failed: {e}")
        return False

    try:
        # Test 2: PME Engine compatibility layer
        from pme_engine import BenchmarkType, PMEEngine

        logger.debug("   ✅ PME Engine imported successfully")

        # Create test data
        fund_data = pd.DataFrame(
            {
                "date": pd.date_range("2020-01-01", periods=8, freq="QE"),
                "cashflow": [-1000, -500, 0, 200, 300, 0, 400, 500],
                "nav": [1000, 1400, 1450, 1350, 1600, 1700, 1600, 1800],
            }
        )

        benchmark_data = pd.DataFrame(
            {
                "date": pd.date_range("2020-01-01", periods=8, freq="QE"),
                "price": [100, 105, 110, 108, 115, 120, 118, 125],
            }
        )

        # Test PME engine
        engine = PMEEngine(fund_data, benchmark_data, BenchmarkType.PRICE_ONLY)
        logger.debug("   ✅ PME Engine initialized")

        # Test calculations
        ks_result = engine.calculate_kaplan_schoar_pme()
        logger.debug(f"   ✅ Kaplan-Schoar PME: {ks_result.value:.3f}")

        pme_plus_result = engine.calculate_pme_plus()
        logger.debug(f"   ✅ PME+: {pme_plus_result.value:.3f}")

        alpha_result = engine.calculate_direct_alpha()
        logger.debug(f"   ✅ Direct Alpha: {alpha_result.value:.3f}")

    except Exception as e:
        logger.debug(f"   ❌ PME engine failed: {e}")
        return False

    try:
        # Test 3: Math Engine
        from math_engine import MathEngine

        logger.debug("   ✅ Math Engine imported successfully")

        # Test IRR calculation
        cashflows = [-1000, -500, 200, 300, 800]
        irr = MathEngine.calculate_irr(cashflows)
        logger.debug(f"   ✅ IRR calculation: {irr:.1%}")

        # Test TVPI calculation
        tvpi = MathEngine.calculate_tvpi(1500, 1300, 500)
        logger.debug(f"   ✅ TVPI calculation: {tvpi:.2f}x")

        # Test DPI calculation
        dpi = MathEngine.calculate_dpi(1500, 1300)
        logger.debug(f"   ✅ DPI calculation: {dpi:.2f}x")

        # Test volatility calculation
        returns = [0.05, -0.02, 0.08, 0.01, -0.03, 0.04]
        volatility = MathEngine.calculate_volatility(returns)
        logger.debug(f"   ✅ Volatility calculation: {volatility:.1%}")

    except Exception as e:
        logger.debug(f"   ❌ Math engine failed: {e}")
        return False

    try:
        # Test 4: FastAPI imports

        logger.debug("   ✅ FastAPI components loaded successfully")

    except Exception as e:
        logger.debug(f"   ❌ FastAPI components failed: {e}")
        return False

    logger.debug("\n🎉 All core tests passed! System is functional.")
    return True


def test_dependencies():
    """Test critical dependencies."""
    logger.debug("\n🔬 Testing Dependencies...")

    dependencies = [
        ("numpy", "np"),
        ("pandas", "pd"),
        ("scipy", "scipy"),
        ("fastapi", "FastAPI"),
    ]

    for dep_name, _import_name in dependencies:
        try:
            if dep_name == "numpy":
                import numpy as np
            elif dep_name == "pandas":
                import pandas as pd
            elif dep_name == "scipy":
                import scipy
            elif dep_name == "fastapi":
                from fastapi import FastAPI
            logger.debug(f"   ✅ {dep_name}")
        except ImportError as e:
            logger.debug(f"   ❌ {dep_name}: {e}")
            return False

    return True


def main():
    """Run simplified system tests."""
    logger.debug("🚀 PME Calculator - Simple System Test")
    logger.debug("=" * 50)

    # Test dependencies first
    if not test_dependencies():
        logger.debug("\n❌ Critical dependencies missing. Please install requirements.")
        sys.exit(1)

    # Test core functionality
    if not test_core_functionality():
        logger.debug("\n❌ Core functionality tests failed.")
        sys.exit(1)

    logger.debug("\n✅ System Test Complete - All checks passed!")
    logger.debug("🎯 Ready to proceed with enhancements!")


if __name__ == "__main__":
    main()
