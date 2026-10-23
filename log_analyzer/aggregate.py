"""Streaming aggregation. No collection of all input records is retained."""
from collections import Counter
from dataclasses import dataclass, field
from .parser import Event


@dataclass
class Summary:
    valid_lines: int = 0
    invalid_lines: int = 0
    filtered_events: int = 0
    levels: Counter = field(default_factory=Counter)
    sources: Counter = field(default_factory=Counter)
    error_codes: Counter = field(default_factory=Counter)
    invalid_details: list[str] = field(default_factory=list)

    def add_invalid(self, line_number: int, reason: str) -> None:
        self.invalid_lines += 1
        self.invalid_details.append(f"Line {line_number}: {reason}")

    def add_valid_event(self) -> None:
        """Count a syntactically valid record before applying filters."""
        self.valid_lines += 1

    def add_event(self, event: Event) -> None:
        """Aggregate an event that passed all filters."""
        self.filtered_events += 1
        self.levels[event.level] += 1
        self.sources[event.source] += 1
        if event.level == "ERROR":
            self.error_codes[event.event_code] += 1

    def as_dict(self, top_n: int = 10) -> dict:
        return {
            "valid_lines": self.valid_lines,
            "invalid_lines": self.invalid_lines,
            "events_after_filter": self.filtered_events,
            "by_level": dict(sorted(self.levels.items())),
            "by_source": dict(sorted(self.sources.items())),
            "top_error_codes": [
                {"event_code": code, "count": count}
                for code, count in sorted(self.error_codes.items(), key=lambda item: (-item[1], item[0]))[:top_n]
            ],
            "invalid_details": list(self.invalid_details),
        }
