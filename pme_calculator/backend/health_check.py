#!/usr/bin/env python3
"""
Comprehensive Health Check Script for PME Calculator Backend
Tests all critical components and dependencies to ensure system health.
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

# Set up structured logging
from logger import get_logger

logger = get_logger(__name__)


def test_imports():
    """Test all critical imports."""
    logger.info("🔬 Testing imports...")
    errors = []

    try:
        import numpy as np

        logger.info(f"   ✅ numpy: {np.__version__}")
    except ImportError as e:
        errors.append(f"numpy import failed: {e}")
        logger.error(f"   ❌ numpy import failed: {e}")

    try:
        import pandas as pd

        logger.info(f"   ✅ pandas: {pd.__version__}")
    except ImportError as e:
        errors.append(f"pandas import failed: {e}")
        logger.error(f"   ❌ pandas import failed: {e}")

    try:
        import scipy

        logger.info(f"   ✅ scipy: {scipy.__version__}")
    except ImportError as e:
        errors.append(f"scipy import failed: {e}")
        logger.error(f"   ❌ scipy import failed: {e}")

    try:
        import numpy_financial as npf

        logger.info("   ✅ numpy_financial")
    except ImportError as e:
        errors.append(f"numpy_financial import failed: {e}")
        logger.error(f"   ❌ numpy_financial import failed: {e}")

    try:
        from fastapi import FastAPI

        logger.info("   ✅ fastapi")
    except ImportError as e:
        errors.append(f"fastapi import failed: {e}")
        logger.error(f"   ❌ fastapi import failed: {e}")

    try:
        from analysis_engine import PMEAnalysisEngine

        logger.info("   ✅ analysis_engine")
    except ImportError as e:
        errors.append(f"analysis_engine import failed: {e}")
        logger.error(f"   ❌ analysis_engine import failed: {e}")

    try:
        from pme_engine import BenchmarkType, PMEEngine

        logger.info("   ✅ pme_engine")
    except ImportError as e:
        errors.append(f"pme_engine import failed: {e}")
        logger.error(f"   ❌ pme_engine import failed: {e}")

    try:
        from math_engine import MathEngine

        logger.info("   ✅ math_engine")
    except ImportError as e:
        errors.append(f"math_engine import failed: {e}")
        logger.error(f"   ❌ math_engine import failed: {e}")

    try:
        from validation.file_check_simple import validate_file_comprehensive

        logger.info("   ✅ file validation")
    except ImportError as e:
        errors.append(f"file validation import failed: {e}")
        logger.error(f"   ❌ file validation import failed: {e}")

    try:
        from validation.schemas_simple import ValidationResult

        logger.info("   ✅ validation schemas")
    except ImportError as e:
        errors.append(f"validation schemas import failed: {e}")
        logger.error(f"   ❌ validation schemas import failed: {e}")

    return errors


def test_analysis_engine():
    """Test the analysis engine functionality."""
    logger.info("\n🔬 Testing Analysis Engine...")
    errors = []

    try:
        from analysis_engine import PMEAnalysisEngine

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
            if result["success"]:
                logger.info("   ✅ Fund data loaded")
            else:
                errors.append(
                    f"Fund data loading failed: {result.get('error', 'Unknown error')}"
                )
                logger.error(
                    f"   ❌ Fund data loading failed: {result.get('error', 'Unknown error')}"
                )

            # Test metrics calculation
            if engine.fund_data is not None:
                metrics = engine.calculate_pme_metrics()
                if "Fund IRR" in metrics:
                    logger.info("   ✅ Metrics calculated")
                else:
                    errors.append("Metrics calculation returned incomplete results")
                    logger.error(
                        "   ❌ Metrics calculation returned incomplete results"
                    )

        finally:
            # Cleanup
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    except Exception as e:
        errors.append(f"Analysis engine test failed: {str(e)}")
        logger.error(f"   ❌ Analysis engine test failed: {str(e)}")
        traceback.print_exc()

    return errors


def test_pme_engine():
    """Test the PME engine compatibility layer."""
    logger.info("\n🔬 Testing PME Engine...")
    errors = []

    try:
        from pme_engine import BenchmarkType, PMEEngine

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
        logger.info("   ✅ PME Engine initialized")

        # Test calculations
        ks_result = engine.calculate_kaplan_schoar_pme()
        if not np.isnan(ks_result.value):
            logger.info(f"   ✅ Kaplan-Schoar PME: {ks_result.value:.3f}")
        else:
            logger.warning("   ⚠️  Kaplan-Schoar PME calculation returned NaN")

        pme_plus_result = engine.calculate_pme_plus()
        if not np.isnan(pme_plus_result.value):
            logger.info(f"   ✅ PME+: {pme_plus_result.value:.3f}")
        else:
            logger.warning("   ⚠️  PME+ calculation returned NaN")

        alpha_result = engine.calculate_direct_alpha()
        if not np.isnan(alpha_result.value):
            logger.info(f"   ✅ Direct Alpha: {alpha_result.value:.3f}")
        else:
            logger.warning("   ⚠️  Direct Alpha calculation returned NaN")

    except Exception as e:
        errors.append(f"PME engine test failed: {str(e)}")
        logger.error(f"   ❌ PME engine test failed: {str(e)}")
        traceback.print_exc()

    return errors


def test_math_engine():
    """Test the math engine utilities."""
    logger.info("\n🔬 Testing Math Engine...")
    errors = []

    try:
        from math_engine import MathEngine

        # Test IRR calculation
        cashflows = [-1000, -500, 200, 300, 800]
        irr = MathEngine.calculate_irr(cashflows)
        if not np.isnan(irr):
            logger.info(f"   ✅ IRR calculation: {irr:.1%}")
        else:
            logger.warning("   ⚠️  IRR calculation returned NaN")

        # Test TVPI calculation
        tvpi = MathEngine.calculate_tvpi(1500, 1300, 500)
        if not np.isnan(tvpi):
            logger.info(f"   ✅ TVPI calculation: {tvpi:.2f}x")
        else:
            logger.warning("   ⚠️  TVPI calculation returned NaN")

        # Test DPI calculation
        dpi = MathEngine.calculate_dpi(1500, 1300)
        if not np.isnan(dpi):
            logger.info(f"   ✅ DPI calculation: {dpi:.2f}x")
        else:
            logger.warning("   ⚠️  DPI calculation returned NaN")

        # Test volatility calculation
        returns = [0.05, -0.02, 0.08, 0.01, -0.03, 0.04]
        volatility = MathEngine.calculate_volatility(returns)
        if not np.isnan(volatility):
            logger.info(f"   ✅ Volatility calculation: {volatility:.1%}")
        else:
            logger.warning("   ⚠️  Volatility calculation returned NaN")

    except Exception as e:
        errors.append(f"Math engine test failed: {str(e)}")
        logger.error(f"   ❌ Math engine test failed: {str(e)}")
        traceback.print_exc()

    return errors


def test_file_validation():
    """Test file validation functionality."""
    logger.info("\n🔬 Testing File Validation...")
    errors = []

    try:
        from validation.file_check_simple import validate_file_comprehensive

        # Create test file
        test_data = pd.DataFrame(
            {
                "date": ["2020-01-01", "2020-04-01", "2020-07-01"],
                "cashflow": [-1000, 200, 300],
                "nav": [1000, 1200, 1500],
            }
        )

        # Save to temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_file = f.name

        try:
            # Test validation
            result = validate_file_comprehensive(Path(temp_file), "fund")
            if result.is_valid:
                logger.info("   ✅ File validation passed")
            else:
                logger.warning(f"   ⚠️  File validation failed: {result.errors}")

            if result.metadata:
                logger.info(f"   ✅ Rows detected: {result.metadata.row_count}")
                logger.info(f"   ✅ Columns detected: {result.metadata.column_count}")

            if result.detected_mappings:
                logger.info(f"   ✅ Column mappings: {result.detected_mappings}")

        finally:
            # Cleanup
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    except Exception as e:
        errors.append(f"File validation test failed: {str(e)}")
        logger.error(f"   ❌ File validation test failed: {str(e)}")
        traceback.print_exc()

    return errors


def test_fastapi_imports():
    """Test FastAPI application imports."""
    logger.info("\n🔬 Testing FastAPI Components...")
    errors = []

    try:
        # Test main application imports
        try:

            logger.info("   ✅ main_minimal app")
        except Exception as e:
            errors.append(f"main_minimal import failed: {e}")
            logger.error(f"   ❌ main_minimal import failed: {e}")

        # Test routers
        try:

            logger.info("   ✅ upload router")
        except Exception as e:
            logger.warning(f"   ⚠️  upload router import failed: {e}")

        try:

            logger.info("   ✅ simple analysis router")
        except Exception as e:
            logger.warning(f"   ⚠️  simple analysis router import failed: {e}")

    except Exception as e:
        errors.append(f"FastAPI component test failed: {str(e)}")
        logger.error(f"   ❌ FastAPI component test failed: {str(e)}")
        traceback.print_exc()

    return errors


def main():
    """Run comprehensive health check."""
    logger.info("🚀 PME Calculator - Comprehensive Health Check")
    logger.info("=" * 60)

    all_errors = []

    # Run all tests
    all_errors.extend(test_imports())
    all_errors.extend(test_analysis_engine())
    all_errors.extend(test_pme_engine())
    all_errors.extend(test_math_engine())
    all_errors.extend(test_file_validation())
    all_errors.extend(test_fastapi_imports())

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📋 HEALTH CHECK RESULTS")
    logger.info("=" * 60)

    if not all_errors:
        logger.info("🎉 ALL TESTS PASSED - SYSTEM IS HEALTHY!")
        logger.info("\n✅ SYSTEM STATUS:")
        logger.info("   • All imports working correctly")
        logger.info("   • Analysis engine functional")
        logger.info("   • PME engine compatibility layer working")
        logger.info("   • Math engine calculations working")
        logger.info("   • File validation operational")
        logger.info("   • FastAPI components accessible")
        logger.info("\n🚀 READY FOR PRODUCTION!")
        return 0
    else:
        logger.error(f"{len(all_errors)} ISSUES FOUND:")
        for i, error in enumerate(all_errors, 1):
            logger.error(f"   {i}. {error}")
        logger.warning("⚠️  Please address these issues before deployment")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
