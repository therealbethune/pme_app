"""Tiny time helpers shared across the backend."""

from datetime import UTC, datetime
from typing import Final

UTC: Final = UTC


def now_utc() -> datetime:
    """Return an aware datetime in UTC (tzinfo = UTC)."""
    return datetime.now(UTC)


def utc_now() -> datetime:
    """Return a timezone-aware datetime in UTC.

    This replaces datetime.utcnow() with a timezone-aware equivalent.
    """
    return datetime.now(UTC)
