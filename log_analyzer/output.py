"""Terminal, JSON and CSV report rendering."""
import csv
import json
from pathlib import Path
from .aggregate import Summary


def render_terminal(summary: Summary, top_n: int = 10) -> str:
    data = summary.as_dict(top_n)
    lines = [
        "Log analysis summary",
        f"Valid matching events: {data['events_after_filter']}",
        f"Invalid lines: {data['invalid_lines']}",
        "By level:",
    ]
    lines.extend(f"  {key}: {value}" for key, value in data["by_level"].items())
    lines.append("By source:")
    lines.extend(f"  {key}: {value}" for key, value in data["by_source"].items())
    lines.append("Top error codes:")
    lines.extend(f"  {item['event_code']}: {item['count']}" for item in data["top_error_codes"])
    if data["invalid_details"]:
        lines.append("Invalid records:")
        lines.extend(f"  {detail}" for detail in data["invalid_details"])
    return "\n".join(lines)


def write_report(summary: Summary, output_path: str | Path, fmt: str, top_n: int = 10) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = summary.as_dict(top_n)
    if fmt == "json":
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return
    if fmt == "csv":
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["section", "key", "value"])
            writer.writerow(["summary", "valid_lines", data["valid_lines"]])
            writer.writerow(["summary", "invalid_lines", data["invalid_lines"]])
            writer.writerow(["summary", "events_after_filter", data["events_after_filter"]])
            for key, value in data["by_level"].items():
                writer.writerow(["by_level", key, value])
            for key, value in data["by_source"].items():
                writer.writerow(["by_source", key, value])
            for item in data["top_error_codes"]:
                writer.writerow(["top_error_codes", item["event_code"], item["count"]])
            for detail in data["invalid_details"]:
                writer.writerow(["invalid_details", "line", detail])
        return
    raise ValueError("format must be json or csv")
