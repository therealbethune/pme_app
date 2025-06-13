"""
PME App utilities package.

This package provides common utilities for serialization, responses, and data handling.
"""

from .serialization import (
    to_jsonable,
    safe_json_dumps,
    dataframe_to_records,
    series_to_dict,
    make_json_serializable,  # Backward compatibility
    serialize_for_json,      # Alternative name
)

from .responses import (
    SerializingJSONResponse,
    ORJSONSerializingResponse,
    UJSONSerializingResponse,
    create_success_response,
    create_error_response,
    create_data_response,
    DefaultJSONResponse,
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