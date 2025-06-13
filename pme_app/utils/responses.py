"""
FastAPI response utilities with automatic serialization.

This module provides custom response classes that automatically handle
pandas, numpy, and datetime serialization for FastAPI applications.
"""

import json
from typing import Any, Dict, Optional

from fastapi import Response
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTask

from .serialization import safe_json_dumps, to_jsonable


class SerializingJSONResponse(JSONResponse):
    """
    Custom JSONResponse that automatically serializes pandas, numpy, and datetime objects.

    This response class uses our to_jsonable utility to convert non-JSON-serializable
    objects before sending the response.
    """

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        # Convert content using our serialization utility
        if content is not None:
            content = to_jsonable(content)

        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )


class ORJSONSerializingResponse(Response):
    """
    High-performance JSON response using orjson with automatic serialization.

    Falls back to standard JSON if orjson is not available.
    """

    media_type = "application/json"

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        # Convert content using our serialization utility
        if content is not None:
            content = to_jsonable(content)

        super().__init__(
            content=self._serialize_content(content),
            status_code=status_code,
            headers=headers,
            media_type=media_type or self.media_type,
            background=background,
        )

    def _serialize_content(self, content: Any) -> bytes:
        """Serialize content using orjson if available, otherwise standard json."""
        try:
            import orjson

            return orjson.dumps(content)
        except ImportError:
            # Fall back to standard json
            return json.dumps(
                content, ensure_ascii=False, separators=(",", ":")
            ).encode("utf-8")


class UJSONSerializingResponse(Response):
    """
    High-performance JSON response using ujson with automatic serialization.

    Falls back to standard JSON if ujson is not available.
    """

    media_type = "application/json"

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        # Convert content using our serialization utility
        if content is not None:
            content = to_jsonable(content)

        super().__init__(
            content=self._serialize_content(content),
            status_code=status_code,
            headers=headers,
            media_type=media_type or self.media_type,
            background=background,
        )

    def _serialize_content(self, content: Any) -> bytes:
        """Serialize content using ujson if available, otherwise standard json."""
        try:
            import ujson

            return ujson.dumps(content, ensure_ascii=False).encode("utf-8")
        except ImportError:
            # Fall back to standard json
            return json.dumps(
                content, ensure_ascii=False, separators=(",", ":")
            ).encode("utf-8")


def create_success_response(
    data: Any = None, message: str = "Success", status_code: int = 200, **kwargs
) -> SerializingJSONResponse:
    """
    Create a standardized success response.

    Args:
        data: Response data (will be automatically serialized)
        message: Success message
        status_code: HTTP status code
        **kwargs: Additional response fields

    Returns:
        SerializingJSONResponse with standardized format
    """
    response_data = {"success": True, "message": message, "data": data, **kwargs}

    return SerializingJSONResponse(content=response_data, status_code=status_code)


def create_error_response(
    error: str, details: Any = None, status_code: int = 400, **kwargs
) -> SerializingJSONResponse:
    """
    Create a standardized error response.

    Args:
        error: Error message
        details: Additional error details
        status_code: HTTP status code
        **kwargs: Additional response fields

    Returns:
        SerializingJSONResponse with standardized error format
    """
    response_data = {"success": False, "error": error, "details": details, **kwargs}

    return SerializingJSONResponse(content=response_data, status_code=status_code)


def create_data_response(
    data: Any, status_code: int = 200, use_orjson: bool = True
) -> Response:
    """
    Create a response with automatic serialization and optimal JSON encoder.

    Args:
        data: Data to serialize and return
        status_code: HTTP status code
        use_orjson: Whether to prefer orjson over ujson/standard json

    Returns:
        Response with optimally serialized data
    """
    if use_orjson:
        return ORJSONSerializingResponse(content=data, status_code=status_code)
    else:
        return UJSONSerializingResponse(content=data, status_code=status_code)


# Default response class for the application
DefaultJSONResponse = SerializingJSONResponse
