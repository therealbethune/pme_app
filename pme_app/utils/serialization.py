"""
Comprehensive serialization utilities for PME Calculator.

This module provides utilities to convert pandas DataFrames, numpy arrays,
datetime objects, and other non-JSON-serializable types to JSON-compatible formats.
"""

import json
import warnings
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def to_jsonable(obj: Any) -> Any:
    """
    Convert any object to a JSON-serializable format.

    Handles:
    - pandas DataFrames and Series
    - numpy arrays and scalars
    - datetime objects (datetime, date, time, pd.Timestamp)
    - Decimal objects
    - Path objects
    - Complex nested structures (dicts, lists)
    - NaN and infinity values

    Args:
        obj: Object to convert

    Returns:
        JSON-serializable version of the object

    Examples:
        >>> import pandas as pd
        >>> import numpy as np
        >>> from datetime import datetime

        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3.0, np.nan]})
        >>> to_jsonable(df)
        {'a': [1, 2], 'b': [3.0, None]}

        >>> to_jsonable(np.array([1, 2, 3]))
        [1, 2, 3]

        >>> to_jsonable(datetime.now())
        '2023-12-01T10:30:00.123456'
    """
    # Handle None
    if obj is None:
        return None

    # Handle pandas objects
    if isinstance(obj, pd.DataFrame):
        return _dataframe_to_jsonable(obj)
    elif isinstance(obj, pd.Series):
        return _series_to_jsonable(obj)
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, pd.Timedelta | pd.Interval):
        return str(obj)
    elif hasattr(obj, "__class__") and "pandas" in str(obj.__class__):
        # Handle pandas NaT and other pandas NA values
        try:
            if pd.isna(obj):
                return None
        except (ValueError, TypeError):
            # pd.isna() failed, not a scalar pandas object
            pass

    # Handle numpy objects
    elif isinstance(obj, np.ndarray):
        return _array_to_jsonable(obj)
    elif isinstance(obj, np.integer | np.floating):
        return _numpy_scalar_to_jsonable(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.complexfloating):
        return {"real": float(obj.real), "imag": float(obj.imag)}

    # Handle datetime objects
    elif isinstance(obj, datetime | date | time):
        return obj.isoformat()

    # Handle other numeric types
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, complex):
        return {"real": obj.real, "imag": obj.imag}

    # Handle special float values
    elif isinstance(obj, float):
        if np.isnan(obj):
            return None
        elif np.isinf(obj):
            return "Infinity" if obj > 0 else "-Infinity"
        return obj

    # Handle Path objects
    elif isinstance(obj, Path):
        return str(obj)

    # Handle collections
    elif isinstance(obj, dict):
        return {key: to_jsonable(value) for key, value in obj.items()}
    elif isinstance(obj, list | tuple | set):
        return [to_jsonable(item) for item in obj]

    # Handle basic types (str, int, bool)
    elif isinstance(obj, str | int | bool):
        return obj

    # Handle objects with custom serialization
    elif hasattr(obj, "to_dict"):
        return to_jsonable(obj.to_dict())
    elif hasattr(obj, "__dict__"):
        return to_jsonable(obj.__dict__)

    # Fallback: convert to string
    else:
        warnings.warn(
            f"Converting {type(obj)} to string for JSON serialization",
            UserWarning,
            stacklevel=2,
        )
        return str(obj)


def _dataframe_to_jsonable(df: pd.DataFrame) -> dict[str, list[Any]]:
    """Convert pandas DataFrame to JSON-serializable dict."""
    if df.empty:
        return {}

    result = {}

    # Handle index
    if df.index.name or not isinstance(df.index, pd.RangeIndex):
        index_name = df.index.name or "index"
        result[index_name] = to_jsonable(df.index.tolist())

    # Handle columns
    for col in df.columns:
        result[str(col)] = to_jsonable(df[col].tolist())

    return result


def _series_to_jsonable(series: pd.Series) -> list[Any]:
    """Convert pandas Series to JSON-serializable list."""
    if series.empty:
        return []

    return to_jsonable(series.tolist())


def _array_to_jsonable(arr: np.ndarray) -> list[Any] | Any:
    """Convert numpy array to JSON-serializable format."""
    if arr.size == 0:
        return []

    # Handle scalar arrays
    if arr.ndim == 0:
        return to_jsonable(arr.item())

    # Convert to list and recursively process
    return to_jsonable(arr.tolist())


def _numpy_scalar_to_jsonable(scalar: np.integer | np.floating) -> int | float | None:
    """Convert numpy scalar to JSON-serializable format."""
    if np.isnan(scalar) or np.isinf(scalar):
        if np.isnan(scalar):
            return None
        else:
            return "Infinity" if scalar > 0 else "-Infinity"

    if isinstance(scalar, np.integer):
        return int(scalar)
    else:
        return float(scalar)


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Safely serialize object to JSON string using to_jsonable conversion.

    Args:
        obj: Object to serialize
        **kwargs: Additional arguments passed to json.dumps

    Returns:
        JSON string representation

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3.0, float('nan')]})
        >>> safe_json_dumps(df)
        '{"a": [1, 2], "b": [3.0, null]}'
    """
    # Set default arguments
    kwargs.setdefault("ensure_ascii", False)
    kwargs.setdefault("separators", (",", ":"))

    try:
        # First try direct serialization
        return json.dumps(obj, **kwargs)
    except (TypeError, ValueError):
        # Fall back to our conversion
        converted = to_jsonable(obj)
        return json.dumps(converted, **kwargs)


def dataframe_to_records(
    df: pd.DataFrame, orient: str = "records"
) -> list[dict[str, Any]]:
    """
    Convert DataFrame to list of records with proper serialization.

    Args:
        df: DataFrame to convert
        orient: Orientation for conversion ('records', 'index', 'values')

    Returns:
        List of JSON-serializable records

    Examples:
        >>> df = pd.DataFrame({'date': pd.date_range('2023-01-01', periods=2), 'value': [1.0, np.nan]})
        >>> dataframe_to_records(df)
        [{'date': '2023-01-01T00:00:00', 'value': 1.0}, {'date': '2023-01-02T00:00:00', 'value': None}]
    """
    if df.empty:
        return []

    if orient == "records":
        records = df.to_dict("records")
        return [to_jsonable(record) for record in records]
    elif orient == "index":
        return to_jsonable(df.to_dict("index"))
    elif orient == "values":
        return to_jsonable(df.values.tolist())
    else:
        raise ValueError(f"Unsupported orient: {orient}")


def series_to_dict(series: pd.Series) -> dict[str, Any]:
    """
    Convert Series to dictionary with proper serialization.

    Args:
        series: Series to convert

    Returns:
        JSON-serializable dictionary
    """
    if series.empty:
        return {}

    return to_jsonable(series.to_dict())


# Backward compatibility aliases
make_json_serializable = to_jsonable  # For existing code
serialize_for_json = to_jsonable  # Alternative name
