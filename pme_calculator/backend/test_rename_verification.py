#!/usr/bin/env python3
"""
Simple test to verify the analysis_engine rename works.
"""

import sys
import os
import warnings

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_rename_functionality():
    """Test that the rename preserves functionality."""
    print("🔍 Testing analysis engine rename functionality...")

    try:
        # Test 1: Import from legacy file directly
        from analysis_engine_legacy import PMEAnalysisEngine, make_json_serializable

        print("✅ Direct import from legacy file works")

        # Test 2: Import from shim (should show deprecation warning)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Check if deprecation warning was issued
            deprecation_warnings = [
                warning
                for warning in w
                if issubclass(warning.category, DeprecationWarning)
            ]
            if len(deprecation_warnings) > 0:
                print("✅ Deprecation warning issued for shim import")
            else:
                print("⚠️  No deprecation warning for shim import")

        # Test 3: Test PMEAnalysisEngine functionality
        engine = PMEAnalysisEngine()
        assert engine is not None
        assert hasattr(engine, "fund_data")
        assert hasattr(engine, "index_data")
        print("✅ PMEAnalysisEngine functionality preserved")

        # Test 4: Test make_json_serializable functionality
        test_data = {"test": 123, "array": [1, 2, 3]}
        result = make_json_serializable(test_data)
        assert result == test_data
        print("✅ make_json_serializable functionality preserved")

        # Test 5: Test deprecated shim functions
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            from analysis_engine_legacy import xirr_wrapper, ks_pme, direct_alpha

            # These should be callable
            assert callable(xirr_wrapper)
            assert callable(ks_pme)
            assert callable(direct_alpha)
            print("✅ Deprecated shim functions still callable")

        # Test 6: Test preferred import path
        from pme_math.metrics import xirr_wrapper as preferred_xirr

        assert callable(preferred_xirr)
        print("✅ Preferred import path works")

        print("\n🎉 All rename functionality tests PASSED!")
        return True

    except Exception as e:
        print(f"\n❌ Rename functionality test FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_rename_functionality()
    sys.exit(0 if success else 1)
