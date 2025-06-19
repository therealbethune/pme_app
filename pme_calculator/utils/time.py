"""Central timezone utilities for PME Calculator.

This module provides timezone-aware datetime utilities to replace
the deprecated datetime.utcnow() calls throughout the codebase.
"""

from datetime import UTC, datetime
from typing import Final

# Explicitly define UTC for clarity and type safety
UTC_TZ: Final = UTC


def utc_now() -> datetime:
    """Return a timezone-aware datetime in UTC.

    This function replaces datetime.utcnow() which returns a naive datetime.
    All datetime objects returned by this function are timezone-aware and
    set to UTC.

    Returns:
        datetime: A timezone-aware datetime object in UTC.

    Example:
        >>> now = utc_now()
        >>> now.tzinfo is not None
        True
        >>> now.tzinfo == UTC
        True
    """
    return datetime.now(UTC_TZ)
