"""
PME App utilities package.

This package provides common utilities for serialization, responses, and data handling.
"""

from .responses import (
    DefaultJSONResponse,
    ORJSONSerializingResponse,
    SerializingJSONResponse,
    UJSONSerializingResponse,
    create_data_response,
    create_error_response,
    create_success_response,
)
from .serialization import (
    dataframe_to_records,
    make_json_serializable,  # Backward compatibility
    safe_json_dumps,
    serialize_for_json,  # Alternative name
    series_to_dict,
    to_jsonable,
)

__all__ = [
    # Serialization utilities
    "to_jsonable",
    "safe_json_dumps",
    "dataframe_to_records",
    "series_to_dict",
    "make_json_serializable",
    "serialize_for_json",
    # Response utilities
    "SerializingJSONResponse",
    "ORJSONSerializingResponse",
    "UJSONSerializingResponse",
    "create_success_response",
    "create_error_response",
    "create_data_response",
    "DefaultJSONResponse",
]
