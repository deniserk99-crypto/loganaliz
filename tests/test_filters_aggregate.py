from datetime import datetime, timezone
from log_analyzer.aggregate import Summary
from log_analyzer.filters import matches_filters
from log_analyzer.parser import parse_event


def dt(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def test_filter_boundaries_and_combined_filters():
    event = parse_event("2026-09-01T00:00:00Z | ERROR | payment-worker | PAYMENT_TIMEOUT | timeout")
    assert matches_filters(event, dt("2026-09-01T00:00:00Z"), dt("2026-09-02T00:00:00Z"), {"ERROR"}, {"payment-worker"})
    assert not matches_filters(event, end=dt("2026-09-01T00:00:00Z"))
    assert not matches_filters(event, levels={"INFO"})
    assert not matches_filters(event, sources={"auth-api"})


def test_summary_and_deterministic_top_n():
    summary = Summary()
    summary.add_valid_event()
    summary.add_event(parse_event("2026-09-01T00:00:00Z | ERROR | gateway | HTTP_502 | bad gateway"))
    summary.add_valid_event()
    summary.add_event(parse_event("2026-09-01T00:01:00Z | ERROR | gateway | HTTP_502 | bad gateway"))
    summary.add_valid_event()
    summary.add_event(parse_event("2026-09-01T00:02:00Z | INFO | auth-api | AUTH_LOGIN_OK | ok"))
    summary.add_invalid(4, "invalid timestamp")
    data = summary.as_dict(1)
    assert data["valid_lines"] == 3
    assert data["invalid_lines"] == 1
    assert data["events_after_filter"] == 3
    assert data["top_error_codes"] == [{"event_code": "HTTP_502", "count": 2}]
    assert data["invalid_details"] == ["Line 4: invalid timestamp"]
