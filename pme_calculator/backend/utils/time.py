"""Tiny time helpers shared across the backend."""

from datetime import datetime, timezone
from typing import Final

UTC: Final = timezone.utc


def now_utc() -> datetime:
    """Return an aware datetime in UTC (tzinfo = UTC)."""
    return datetime.now(UTC)
