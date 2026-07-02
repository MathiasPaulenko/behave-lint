"""Unit tests for the JSONReporter."""

from __future__ import annotations

import json

from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.lint_result import LintResult, LintSummary
from behave_lint.reporters.json_reporter import SCHEMA_VERSION, JSONReporter


def _make_diag(
    severity: Severity = Severity.ERROR,
    rule_id: str = "BC001",
    file_path: str = "features/login.feature",
    line: int = 12,
    column: int | None = 1,
    message: str = "Duplicate scenario name",
) -> Diagnostic:
    return Diagnostic(
        rule_id=rule_id,
        severity=severity,
        message=message,
        file_path=file_path,
        line=line,
        column=column,
        category=Category.CORRECTNESS,
        suggestion="Rename the scenario",
        doc_url="https://example.com/BC001",
    )


def _make_result(diagnostics: list[Diagnostic] | None = None) -> LintResult:
    diags = diagnostics or []
    return LintResult(
        diagnostics=diags,
        summary=LintSummary.from_diagnostics(
            diags,
            total_files=2,
            files_with_issues=1,
            rules_executed=5,
            duration_ms=120.0,
        ),
        exit_code=1,
    )


class TestJSONReporter:
    """Tests for JSONReporter."""

    def test_name(self) -> None:
        assert JSONReporter.name == "json"

    def test_supports_file_output(self) -> None:
        assert JSONReporter.supports_file_output is True

    def test_no_diagnostics(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = JSONReporter()
        result = _make_result([])
        reporter.render(result)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["schemaVersion"] == SCHEMA_VERSION
        assert data["diagnostics"] == []
        assert data["summary"]["total_diagnostics"] == 0

    def test_with_diagnostics(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = JSONReporter()
        result = _make_result([_make_diag()])
        reporter.render(result)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["schemaVersion"] == SCHEMA_VERSION
        assert len(data["diagnostics"]) == 1
        diag = data["diagnostics"][0]
        assert diag["rule_id"] == "BC001"
        assert diag["severity"] == "error"
        assert diag["file_path"] == "features/login.feature"
        assert diag["line"] == 12
        assert diag["column"] == 1
        assert diag["category"] == "correctness"
        assert diag["suggestion"] == "Rename the scenario"
        assert diag["doc_url"] == "https://example.com/BC001"

    def test_summary_fields(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = JSONReporter()
        result = _make_result([_make_diag()])
        reporter.render(result)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        summary = data["summary"]
        assert summary["total_files"] == 2
        assert summary["files_with_issues"] == 1
        assert summary["total_diagnostics"] == 1
        assert summary["error_count"] == 1
        assert summary["rules_executed"] == 5

    def test_tool_metadata(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = JSONReporter()
        result = _make_result([])
        reporter.render(result)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["tool"]["name"] == "behave-lint"
        assert "version" in data["tool"]

    def test_timestamp_present(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = JSONReporter()
        result = _make_result([])
        reporter.render(result)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "timestamp" in data

    def test_exit_code_in_output(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = JSONReporter()
        result = _make_result([_make_diag()])
        reporter.render(result)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["exit_code"] == 1

    def test_optional_fields_omitted(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = JSONReporter()
        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="Test",
            file_path="test.feature",
            line=1,
            category=Category.CORRECTNESS,
        )
        result = _make_result([diag])
        reporter.render(result)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        diag = data["diagnostics"][0]
        assert "column" not in diag
        assert "suggestion" not in diag
        assert "doc_url" not in diag
        assert "end_line" not in diag

    def test_output_to_file(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        reporter = JSONReporter()
        result = _make_result([_make_diag()])
        path = str(tmp_path / "output.json")
        reporter.render(result, path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["schemaVersion"] == SCHEMA_VERSION
        assert len(data["diagnostics"]) == 1
