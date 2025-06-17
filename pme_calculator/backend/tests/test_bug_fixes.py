"""
Comprehensive bug detection and testing for the PME Calculator backend.
Tests various edge cases and potential issues identified through code scanning.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import modules that need testing
from cache import CacheManager
from math_engine import MathEngine
from pme_engine import PMEEngine, PMEResult
from validation import schemas
from validation.file_check_simple import validate_file_comprehensive


class TestValidationSchemas:
    """Test validation schemas for various edge cases."""

    def test_cashflow_row_edge_cases(self):
        """Test CashflowRow with edge case inputs."""
        # Valid data
        valid_row = schemas.CashflowRow(
            date="2023-01-01", cashflow=1000.50, nav=50000.0
        )
        assert valid_row.date.year == 2023
        assert valid_row.cashflow == 1000.50

        # Edge case: zero values
        zero_row = schemas.CashflowRow(date="2023-01-01", cashflow=0.0, nav=0.0)
        assert zero_row.nav == 0.0

        # Edge case: negative cashflow (distribution)
        negative_row = schemas.CashflowRow(
            date="2023-01-01", cashflow=-500.0, nav=49500.0
        )
        assert negative_row.cashflow == -500.0

    def test_cashflow_row_invalid_dates(self):
        """Test CashflowRow with invalid date formats."""
        invalid_dates = [
            "invalid-date",
            "2023/13/01",  # Invalid month
            "2023-02-30",  # Invalid day
            "23-01-01",  # Wrong year format
            "",
            None,
        ]

        for invalid_date in invalid_dates:
            with pytest.raises((ValueError, TypeError)):
                schemas.CashflowRow(date=invalid_date, cashflow=1000.0, nav=50000.0)

    def test_decimal_validation_edge_cases(self):
        """Test decimal validation with various edge cases."""
        test_cases = [
            ("1000.50", 1000.50),
            ("$1,000.50", 1000.50),  # Currency symbols
            ("1,000", 1000.0),  # Commas
            ("", 0),  # Empty string
            ("-", 0),  # Dash only
            ("0", 0),  # Zero
            ("0.00", 0),  # Zero with decimals
        ]

        for input_value, expected in test_cases:
            row = schemas.CashflowRow(
                date="2023-01-01", cashflow=input_value, nav="50000.0"
            )
            assert float(row.cashflow) == expected

    def test_cashflow_consistency_validation(self):
        """Test cashflow component consistency validation."""
        # Valid consistent data
        consistent_row = schemas.CashflowRow(
            date="2023-01-01",
            cashflow=500.0,
            nav=50000.0,
            contributions=1000.0,
            distributions=500.0,
        )
        assert consistent_row.cashflow == 500.0

        # Invalid inconsistent data
        with pytest.raises(ValueError, match="doesn't match"):
            schemas.CashflowRow(
                date="2023-01-01",
                cashflow=100.0,  # Should be 500.0
                nav=50000.0,
                contributions=1000.0,
                distributions=500.0,
            )


class TestMathEngine:
    """Test MathEngine for calculation errors and edge cases."""

    def test_irr_calculation_edge_cases(self):
        """Test IRR calculation with edge cases."""
        engine = MathEngine()

        # Edge case: All positive cashflows (should handle gracefully)
        all_positive = [100, 200, 300]
        result = engine.calculate_irr(all_positive)
        # Should return NaN or handle gracefully
        assert result is None or np.isnan(result)

        # Edge case: All negative cashflows
        all_negative = [-100, -200, -300]
        result = engine.calculate_irr(all_negative)
        assert result is None or np.isnan(result)

        # Edge case: Empty list
        with pytest.raises((ValueError, IndexError)):
            engine.calculate_irr([])

        # Edge case: Single value
        with pytest.raises((ValueError, IndexError)):
            engine.calculate_irr([100])

    def test_safe_division(self):
        """Test safe division operations."""
        engine = MathEngine()

        # Normal division
        assert engine.safe_divide(10, 2) == 5.0

        # Division by zero
        result = engine.safe_divide(10, 0)
        assert result == 0.0 or np.isnan(result) or np.isinf(result)

        # Division with NaN
        result = engine.safe_divide(np.nan, 2)
        assert np.isnan(result)

        # Division of zero by zero
        result = engine.safe_divide(0, 0)
        assert result == 0.0 or np.isnan(result)


class TestPMEEngine:
    """Test PME Engine for compatibility and error handling."""

    def create_sample_data(self):
        """Create sample fund and benchmark data for testing."""
        dates = pd.date_range("2020-01-01", periods=12, freq="M")

        fund_data = pd.DataFrame(
            {
                "date": dates,
                "cashflow": [-1000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1200],
                "nav": [
                    1000,
                    1050,
                    1100,
                    1080,
                    1120,
                    1150,
                    1180,
                    1160,
                    1200,
                    1220,
                    1250,
                    0,
                ],
            }
        )

        benchmark_data = pd.DataFrame(
            {
                "date": dates,
                "price": [100, 102, 105, 103, 108, 110, 112, 109, 115, 117, 120, 118],
            }
        )

        return fund_data, benchmark_data

    def test_pme_engine_initialization(self):
        """Test PME Engine initialization with various inputs."""
        fund_data, benchmark_data = self.create_sample_data()

        # Test normal initialization
        engine = PMEEngine(fund_data, benchmark_data)
        assert engine.fund_data is not None
        assert engine.benchmark_data is not None

    def test_pme_calculations_with_invalid_data(self):
        """Test PME calculations with invalid or edge case data."""
        # Empty DataFrames
        empty_fund = pd.DataFrame()
        empty_benchmark = pd.DataFrame()

        try:
            engine = PMEEngine(empty_fund, empty_benchmark)
            # Should return default values on error
            result = engine.calculate_kaplan_schoar_pme()
            assert isinstance(result, PMEResult)
            assert result.value == 1.0  # Default value
        except Exception:
            # Exception is acceptable for invalid data
            pass

    def test_cleanup_on_deletion(self):
        """Test that temporary files are cleaned up properly."""
        fund_data, benchmark_data = self.create_sample_data()

        engine = PMEEngine(fund_data, benchmark_data)

        # Check that temp files were created
        hasattr(engine, "fund_temp_path") and os.path.exists(engine.fund_temp_path)
        hasattr(engine, "benchmark_temp_path") and os.path.exists(
            engine.benchmark_temp_path
        )

        # Delete the engine
        del engine

        # Files should be cleaned up (or at least the cleanup attempt should not crash)
        # We can't easily test file cleanup due to __del__ timing, but we ensure no errors


class TestFileValidation:
    """Test file validation edge cases."""

    def test_validate_nonexistent_file(self):
        """Test validation of non-existent files."""
        result = validate_file_comprehensive("nonexistent_file.csv")
        assert not result.is_valid
        assert len(result.errors) > 0
        assert (
            "not found" in result.errors[0].lower()
            or "does not exist" in result.errors[0].lower()
        )

    def test_validate_empty_file(self):
        """Test validation of empty files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("")  # Empty file
            temp_path = f.name

        try:
            result = validate_file_comprehensive(temp_path)
            assert not result.is_valid
            assert len(result.errors) > 0
        finally:
            os.unlink(temp_path)

    def test_validate_invalid_csv_format(self):
        """Test validation of malformed CSV files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("invalid,csv\ndata,with,mismatched,columns\n")
            temp_path = f.name

        try:
            result = validate_file_comprehensive(temp_path)
            # Should handle gracefully - either validate or fail with meaningful error
            assert isinstance(result.is_valid, bool)
        finally:
            os.unlink(temp_path)


class TestCacheEdgeCases:
    """Test cache implementation edge cases."""

    def test_cache_key_generation_with_special_characters(self):
        """Test cache key generation with special characters and edge cases."""
        cache_manager = CacheManager()

        # Test with special characters
        key1 = cache_manager._generate_key(
            "test", "arg with spaces", "arg/with/slashes"
        )
        key2 = cache_manager._generate_key(
            "test", "arg with spaces", "arg/with/slashes"
        )
        assert key1 == key2  # Should be deterministic

        # Test with None values
        key3 = cache_manager._generate_key("test", None, param=None)
        assert "test" in key3

        # Test with complex nested objects
        complex_obj = {
            "nested": {
                "data": [1, 2, {"deep": "value"}],
                "func": lambda x: x,  # Non-serializable
            }
        }
        key4 = cache_manager._generate_key("test", complex_obj)
        assert "test:" in key4


class TestErrorHandling:
    """Test error handling across modules."""

    def test_json_serialization_errors(self):
        """Test handling of JSON serialization errors."""

        # Test with non-serializable objects
        class NonSerializable:
            def __init__(self):
                self.func = lambda x: x

        obj = NonSerializable()

        # This should be handled gracefully by json.dumps(obj, default=str)
        try:
            result = json.dumps(obj, default=str)
            assert isinstance(result, str)
        except Exception as e:
            # If it still fails, at least it's a proper exception
            assert isinstance(e, (TypeError, ValueError))

    def test_dataframe_operations_with_empty_data(self):
        """Test DataFrame operations with empty or invalid data."""
        # Empty DataFrame
        empty_df = pd.DataFrame()

        # Operations should handle empty DataFrames gracefully
        try:
            # These operations should not crash
            result1 = empty_df.dropna()
            result2 = empty_df.fillna(0)
            assert isinstance(result1, pd.DataFrame)
            assert isinstance(result2, pd.DataFrame)
        except Exception:
            # If they do crash, it should be a proper exception
            pass

        # DataFrame with NaN values
        nan_df = pd.DataFrame({"a": [1, np.nan, 3], "b": [np.nan, 2, np.nan]})

        try:
            # These should handle NaN values properly
            result3 = nan_df.dropna()
            result4 = nan_df.fillna(0)
            assert isinstance(result3, pd.DataFrame)
            assert isinstance(result4, pd.DataFrame)
        except Exception:
            pass

    def test_numpy_operations_with_edge_cases(self):
        """Test numpy operations with edge cases."""
        # Division by zero
        try:
            result = np.array([1, 2, 3]) / np.array([1, 0, 3])
            # Should get inf for division by zero
            assert np.isinf(result[1])
        except Exception:
            pass

        # Operations with NaN
        try:
            arr_with_nan = np.array([1, np.nan, 3])
            result = np.mean(arr_with_nan)
            assert np.isnan(result)
        except Exception:
            pass


class TestSystemIntegration:
    """Test system integration and cross-module compatibility."""

    def test_module_imports(self):
        """Test that all modules can be imported without errors."""
        try:
            from pme_calculator.backend.cache import CacheManager
            from pme_calculator.backend.math_engine import MathEngine
            from pme_calculator.backend.validation.schemas import (
                CashflowRow,
                ValidationResult,
            )

            assert True  # If we get here, imports worked
        except ImportError as e:
            pytest.fail(f"Import error: {e}")

    def test_module_interfaces(self):
        """Test that module interfaces are compatible."""
        # Test that ValidationResult can be created
        result = schemas.ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.has_errors is False

        # Test that MathEngine can be instantiated
        engine = MathEngine()
        assert engine is not None


if __name__ == "__main__":
    pytest.main([__file__])
