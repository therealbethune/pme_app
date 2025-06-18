"""
Health check router for PME Calculator backend.
Provides simple health status and version information.
"""

from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

# Import version from the backend package
try:
    import os
    import sys

    # Add the backend directory to the path for imports
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    from __init__ import __version__
except ImportError:
    __version__ = "1.0.0"  # Fallback version

from logger import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter(tags=["health"])


@router.get("/healthz")
async def health_check() -> dict[str, Any]:
    """
    Simple health check endpoint.

    Returns:
        JSON response with status and version information
    """
    try:
        response = {"status": "ok", "version": __version__}

        logger.debug(
            "Health check requested",
            extra={"endpoint": "/healthz", "status": "ok", "version": __version__},
        )

        return response

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "version": __version__, "error": str(e)},
        )
