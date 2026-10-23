"""Parsing and validation for pipe-separated event log records."""
from dataclasses import dataclass
from datetime import datetime, timezone

VALID_LEVELS = {"TRACE", "DEBUG", "INFO", "WARN", "ERROR"}


@dataclass(frozen=True)
class Event:
    timestamp: datetime
    level: str
    source: str
    event_code: str
    message: str


def parse_event(line: str) -> Event:
    """Parse one record; raise ValueError with a useful reason if invalid."""
    fields = [part.strip() for part in line.rstrip("\r\n").split("|")]
    if len(fields) != 5:
        raise ValueError("expected exactly 5 fields separated by '|'" )
    timestamp_text, level, source, event_code, message = fields
    if not all(fields):
        raise ValueError("fields must not be empty")
    if level not in VALID_LEVELS:
        raise ValueError(f"unsupported level: {level}")
    try:
        # The input contract requires ISO 8601 UTC, represented by a trailing Z.
        if not timestamp_text.endswith("Z"):
            raise ValueError
        timestamp = datetime.fromisoformat(timestamp_text[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError("timestamp must be ISO 8601 UTC ending in Z") from exc
    if timestamp.tzinfo is None or timestamp.utcoffset() != timezone.utc.utcoffset(timestamp):
        raise ValueError("timestamp must be UTC")
    return Event(timestamp, level, source, event_code, message)
