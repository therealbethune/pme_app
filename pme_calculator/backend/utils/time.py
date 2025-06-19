"""Time utilities for backend services."""

from datetime import UTC, datetime, timezone
from typing import Final

UTC: Final = UTC


def now_utc() -> datetime:
    """Return an aware datetime in UTC (tzinfo = UTC)."""
    return datetime.now(UTC)


__all__ = ["UTC", "now_utc"]
