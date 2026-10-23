from datetime import timezone
import pytest
from log_analyzer.parser import parse_event


def test_parse_valid_event():
    event = parse_event("2026-09-01T00:08:59Z | WARN | auth-api | AUTH_LOGIN_OK | session created")
    assert event.level == "WARN"
    assert event.source == "auth-api"
    assert event.timestamp.tzinfo == timezone.utc


@pytest.mark.parametrize("line", [
    "not-a-timestamp | ERROR | api | CODE | message",
    "2026-09-01T00:00:00Z | NOTICE | api | CODE | message",
    "2026-09-01T00:00:00Z | ERROR | api | | message",
    "2026-09-01T00:00:00Z | ERROR | api | CODE",
    "2026-09-01T00:00:00+01:00 | ERROR | api | CODE | message",
])
def test_reject_bad_records(line):
    with pytest.raises(ValueError):
        parse_event(line)


def test_reject_empty_field():
    with pytest.raises(ValueError, match="must not be empty"):
        parse_event("2026-09-01T00:00:00Z | ERROR | api | CODE |   ")
