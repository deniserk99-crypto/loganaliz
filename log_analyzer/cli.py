"""Command-line interface for the log analyzer."""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from .aggregate import Summary
from .filters import matches_filters
from .output import render_terminal, write_report
from .parser import VALID_LEVELS, parse_event


def parse_cli_datetime(value: str) -> datetime:
    """Parse a CLI time as ISO 8601 UTC ending in Z."""
    try:
        if not value.endswith("Z"):
            raise ValueError
        result = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be ISO 8601 UTC, for example 2026-09-01T00:00:00Z") from exc
    if result.utcoffset() != timezone.utc.utcoffset(result):
        raise argparse.ArgumentTypeError("timestamp must be UTC")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Stream and summarize a pipe-separated event log.")
    parser.add_argument("--input", required=True, help="path to input log")
    parser.add_argument("--from", dest="start", type=parse_cli_datetime, help="inclusive UTC start timestamp")
    parser.add_argument("--to", dest="end", type=parse_cli_datetime, help="exclusive UTC end timestamp")
    parser.add_argument("--level", action="append", choices=sorted(VALID_LEVELS), help="level filter; repeat to select multiple")
    parser.add_argument("--source", action="append", help="source filter; repeat to select multiple")
    parser.add_argument("--top", type=int, default=10, help="number of top ERROR event codes (default: 10)")
    parser.add_argument("--format", choices=("json", "csv"), default="json", help="report format")
    parser.add_argument("--output", help="optional report output path")
    return parser


def analyze_file(input_path: str | Path, start=None, end=None, levels=None, sources=None) -> Summary:
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"input file not found: {path}")
    if not path.is_file():
        raise ValueError(f"input path is not a file: {path}")
    summary = Summary()
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                summary.add_invalid(line_number, "empty line")
                print(f"Line {line_number}: empty line", file=sys.stderr)
                continue
            try:
                event = parse_event(line)
            except ValueError as exc:
                summary.add_invalid(line_number, str(exc))
                print(f"Line {line_number}: {exc}", file=sys.stderr)
                continue
            summary.add_valid_event()
            if matches_filters(event, start, end, set(levels or []), set(sources or [])):
                summary.add_event(event)
    return summary


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.top < 0:
        parser.error("--top must be zero or greater")
    if args.start and args.end and args.start >= args.end:
        parser.error("--from must be earlier than --to")
    try:
        summary = analyze_file(args.input, args.start, args.end, args.level, args.source)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(render_terminal(summary, args.top))
    if args.output:
        write_report(summary, args.output, args.format, args.top)
        print(f"Report saved to: {args.output}")
    return 0
