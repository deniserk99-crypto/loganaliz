import csv
import json
from pathlib import Path
from log_analyzer.aggregate import Summary
from log_analyzer.cli import analyze_file, main
from log_analyzer.output import render_terminal, write_report


def test_json_and_csv_reports(tmp_path):
    summary = Summary()
    summary.add_event(__import__("log_analyzer.parser", fromlist=["parse_event"]).parse_event(
        "2026-09-01T00:00:00Z | ERROR | gateway | HTTP_502 | bad gateway"))
    json_path = tmp_path / "out.json"
    csv_path = tmp_path / "nested" / "out.csv"
    write_report(summary, json_path, "json")
    write_report(summary, csv_path, "csv")
    assert json.loads(json_path.read_text())["events_after_filter"] == 1
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == ["section", "key", "value"]
    assert any(row[1] == "events_after_filter" and row[2] == "1" for row in rows)


def test_empty_file_and_missing_file(tmp_path):
    empty = tmp_path / "empty.log"
    empty.write_text("")
    assert analyze_file(empty).filtered_events == 0
    assert main(["--input", str(tmp_path / "missing.log")]) == 2


def test_analyze_bad_lines_reports_line_number(tmp_path, capsys):
    source = tmp_path / "sample.log"
    source.write_text("bad line\n2026-09-01T00:00:00Z | INFO | api | OK | good\n", encoding="utf-8")
    summary = analyze_file(source)
    assert summary.invalid_lines == 1
    assert summary.filtered_events == 1
    assert "Line 1" in capsys.readouterr().err


def test_cli_filters_and_output(tmp_path, capsys):
    source = tmp_path / "sample.log"
    source.write_text(
        "2026-09-01T00:00:00Z | ERROR | gateway | HTTP_502 | bad\n"
        "2026-09-01T01:00:00Z | INFO | auth-api | LOGIN | ok\n", encoding="utf-8")
    output = tmp_path / "report.json"
    code = main(["--input", str(source), "--from", "2026-09-01T00:00:00Z",
                 "--to", "2026-09-01T01:00:00Z", "--level", "ERROR", "--source", "gateway",
                 "--top", "1", "--format", "json", "--output", str(output)])
    assert code == 0
    assert json.loads(output.read_text())["events_after_filter"] == 1
    assert "Valid matching events: 1" in capsys.readouterr().out


def test_invalid_time_range_is_rejected(tmp_path):
    source = tmp_path / "empty.log"
    source.write_text("")
    import pytest
    with pytest.raises(SystemExit) as exc:
        main(["--input", str(source), "--from", "2026-09-02T00:00:00Z",
              "--to", "2026-09-01T00:00:00Z"])
    assert exc.value.code == 2
