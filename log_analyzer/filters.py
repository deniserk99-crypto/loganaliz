"""Filtering helpers for parsed events."""
from datetime import datetime
from .parser import Event


def matches_filters(event: Event, start: datetime | None = None, end: datetime | None = None,
                    levels: set[str] | None = None, sources: set[str] | None = None) -> bool:
    """Return whether an event matches all provided filters; start inclusive, end exclusive."""
    if start is not None and event.timestamp < start:
        return False
    if end is not None and event.timestamp >= end:
        return False
    if levels and event.level not in levels:
        return False
    if sources and event.source not in sources:
        return False
    return True
