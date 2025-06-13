"""
Tests for PME App serialization utilities.

This module tests the comprehensive serialization functionality for
pandas, numpy, datetime, and other non-JSON-serializable objects.
"""

import json
import pytest
from datetime import datetime, date, time
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd

from pme_app.utils.serialization import (
    to_jsonable,
    safe_json_dumps,
    dataframe_to_records,
    series_to_dict,
    make_json_serializable,
)


class TestToJsonable:
    """Test the main to_jsonable function."""

    def test_none_values(self):
        """Test handling of None values."""
        assert to_jsonable(None) is None

    def test_basic_types(self):
        """Test handling of basic JSON-serializable types."""
        assert to_jsonable("string") == "string"
        assert to_jsonable(42) == 42
        assert to_jsonable(True) is True
        assert to_jsonable(False) is False

    def test_numpy_scalars(self):
        """Test handling of numpy scalar types."""
        assert to_jsonable(np.int32(42)) == 42
        assert to_jsonable(np.int64(42)) == 42
        assert to_jsonable(np.float32(3.14)) == pytest.approx(3.14)
        assert to_jsonable(np.float64(3.14)) == pytest.approx(3.14)
        assert to_jsonable(np.bool_(True)) is True

    def test_numpy_special_values(self):
        """Test handling of NaN and infinity."""
        assert to_jsonable(np.nan) is None
        assert to_jsonable(np.inf) == "Infinity"
        assert to_jsonable(-np.inf) == "-Infinity"
        assert to_jsonable(float('nan')) is None
        assert to_jsonable(float('inf')) == "Infinity"

    def test_numpy_arrays(self):
        """Test handling of numpy arrays."""
        arr = np.array([1, 2, 3])
        assert to_jsonable(arr) == [1, 2, 3]
        
        # 2D array
        arr_2d = np.array([[1, 2], [3, 4]])
        assert to_jsonable(arr_2d) == [[1, 2], [3, 4]]
        
        # Empty array
        empty_arr = np.array([])
        assert to_jsonable(empty_arr) == []
        
        # Scalar array
        scalar_arr = np.array(42)
        assert to_jsonable(scalar_arr) == 42

    def test_pandas_dataframe(self):
        """Test handling of pandas DataFrames."""
        df = pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4.0, 5.0, np.nan],
            'c': ['x', 'y', 'z']
        })
        
        result = to_jsonable(df)
        expected = {
            'a': [1, 2, 3],
            'b': [4.0, 5.0, None],
            'c': ['x', 'y', 'z']
        }
        assert result == expected

    def test_pandas_series(self):
        """Test handling of pandas Series."""
        series = pd.Series([1, 2, np.nan, 4])
        result = to_jsonable(series)
        assert result == [1, 2, None, 4]

    def test_pandas_timestamp(self):
        """Test handling of pandas Timestamp."""
        ts = pd.Timestamp('2023-01-01 12:30:45')
        result = to_jsonable(ts)
        assert result == '2023-01-01T12:30:45'
        
        # NaT (Not a Time)
        nat = pd.NaT
        assert to_jsonable(nat) is None

    def test_datetime_objects(self):
        """Test handling of datetime objects."""
        dt = datetime(2023, 1, 1, 12, 30, 45)
        assert to_jsonable(dt) == '2023-01-01T12:30:45'
        
        d = date(2023, 1, 1)
        assert to_jsonable(d) == '2023-01-01'
        
        t = time(12, 30, 45)
        assert to_jsonable(t) == '12:30:45'

    def test_decimal_and_complex(self):
        """Test handling of Decimal and complex numbers."""
        dec = Decimal('3.14159')
        assert to_jsonable(dec) == 3.14159
        
        comp = complex(3, 4)
        assert to_jsonable(comp) == {"real": 3.0, "imag": 4.0}

    def test_path_objects(self):
        """Test handling of Path objects."""
        path = Path('/tmp/test.txt')
        assert to_jsonable(path) == '/tmp/test.txt'

    def test_nested_structures(self):
        """Test handling of nested dictionaries and lists."""
        data = {
            'numbers': [1, np.int32(2), np.float64(3.14)],
            'dataframe': pd.DataFrame({'x': [1, 2]}),
            'timestamp': pd.Timestamp('2023-01-01'),
            'nested': {
                'array': np.array([1, 2, 3]),
                'nan_value': np.nan
            }
        }
        
        result = to_jsonable(data)
        expected = {
            'numbers': [1, 2, 3.14],
            'dataframe': {'x': [1, 2]},
            'timestamp': '2023-01-01T00:00:00',
            'nested': {
                'array': [1, 2, 3],
                'nan_value': None
            }
        }
        assert result == expected


class TestSafeJsonDumps:
    """Test the safe_json_dumps function."""

    def test_basic_serialization(self):
        """Test basic JSON serialization."""
        data = {'a': 1, 'b': 'test'}
        result = safe_json_dumps(data)
        assert json.loads(result) == data

    def test_numpy_serialization(self):
        """Test serialization of numpy objects."""
        data = {
            'array': np.array([1, 2, 3]),
            'scalar': np.int32(42),
            'nan': np.nan
        }
        
        result = safe_json_dumps(data)
        parsed = json.loads(result)
        
        assert parsed['array'] == [1, 2, 3]
        assert parsed['scalar'] == 42
        assert parsed['nan'] is None

    def test_dataframe_serialization(self):
        """Test serialization of pandas DataFrame."""
        df = pd.DataFrame({'a': [1, 2], 'b': [3.0, np.nan]})
        result = safe_json_dumps(df)
        parsed = json.loads(result)
        
        assert parsed == {'a': [1, 2], 'b': [3.0, None]}


class TestDataFrameToRecords:
    """Test the dataframe_to_records function."""

    def test_basic_conversion(self):
        """Test basic DataFrame to records conversion."""
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=2),
            'value': [1.0, np.nan]
        })
        
        result = dataframe_to_records(df)
        assert len(result) == 2
        assert result[0]['date'] == '2023-01-01T00:00:00'
        assert result[0]['value'] == 1.0
        assert result[1]['value'] is None

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        df = pd.DataFrame()
        result = dataframe_to_records(df)
        assert result == []

    def test_different_orientations(self):
        """Test different orientation options."""
        df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        
        # Records orientation
        records = dataframe_to_records(df, orient='records')
        assert records == [{'a': 1, 'b': 3}, {'a': 2, 'b': 4}]
        
        # Index orientation
        index_result = dataframe_to_records(df, orient='index')
        assert isinstance(index_result, dict)
        
        # Values orientation
        values_result = dataframe_to_records(df, orient='values')
        assert values_result == [[1, 3], [2, 4]]


class TestSeriesToDict:
    """Test the series_to_dict function."""

    def test_basic_conversion(self):
        """Test basic Series to dict conversion."""
        series = pd.Series([1, 2, 3], index=['a', 'b', 'c'])
        result = series_to_dict(series)
        assert result == {'a': 1, 'b': 2, 'c': 3}

    def test_empty_series(self):
        """Test handling of empty Series."""
        series = pd.Series([], dtype=float)
        result = series_to_dict(series)
        assert result == {}

    def test_series_with_nan(self):
        """Test Series with NaN values."""
        series = pd.Series([1, np.nan, 3])
        result = series_to_dict(series)
        assert result[1] is None


class TestBackwardCompatibility:
    """Test backward compatibility aliases."""

    def test_make_json_serializable_alias(self):
        """Test that make_json_serializable works as alias."""
        data = np.array([1, 2, 3])
        result1 = to_jsonable(data)
        result2 = make_json_serializable(data)
        assert result1 == result2


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_custom_objects(self):
        """Test handling of custom objects."""
        class CustomObject:
            def __init__(self):
                self.value = 42
        
        obj = CustomObject()
        result = to_jsonable(obj)
        assert result == {'value': 42}

    def test_objects_with_to_dict(self):
        """Test objects with to_dict method."""
        class ObjectWithToDict:
            def to_dict(self):
                return {'custom': 'data'}
        
        obj = ObjectWithToDict()
        result = to_jsonable(obj)
        assert result == {'custom': 'data'}

    def test_circular_references(self):
        """Test handling of circular references (should not hang)."""
        # Create a simple circular reference
        data = {'a': 1}
        data['self'] = data
        
        # This should not hang or crash
        try:
            result = to_jsonable(data)
            # The exact result depends on implementation,
            # but it should not crash
            assert isinstance(result, dict)
        except RecursionError:
            # This is acceptable behavior for circular references
            pass


if __name__ == "__main__":
    pytest.main([__file__]) 