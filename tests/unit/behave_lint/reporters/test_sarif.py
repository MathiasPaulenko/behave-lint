"""Unit tests for the SARIFReporter."""

from __future__ import annotations

import json

from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.lint_result import LintResult, LintSummary
from behave_lint.reporters.sarif import SARIF_SCHEMA, SARIF_VERSION, SARIFReporter


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
        ),
    )


class TestSARIFReporter:
    """Tests for SARIFReporter."""

    def test_name(self) -> None:
        assert SARIFReporter.name == "sarif"

    def test_supports_file_output(self) -> None:
        assert SARIFReporter.supports_file_output is True

    def test_sarif_version(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = SARIFReporter()
        result = _make_result([])
        reporter.render(result)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["version"] == SARIF_VERSION
        assert data["$schema"] == SARIF_SCHEMA

    def test_no_results(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = SARIFReporter()
        result = _make_result([])
        reporter.render(result)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["runs"][0]["results"] == []
        assert data["runs"][0]["tool"]["driver"]["rules"] == []

    def test_with_diagnostics(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = SARIFReporter()
        result = _make_result([_make_diag()])
        reporter.render(result)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        run = data["runs"][0]
        assert len(run["results"]) == 1
        res = run["results"][0]
        assert res["ruleId"] == "BC001"
        assert res["level"] == "error"
        assert res["message"]["text"] == "Duplicate scenario name"
        loc = res["locations"][0]
        assert (
            loc["physicalLocation"]["artifactLocation"]["uri"]
            == "features/login.feature"
        )
        assert loc["physicalLocation"]["region"]["startLine"] == 12
        assert loc["physicalLocation"]["region"]["startColumn"] == 1

    def test_rules_deduplicated(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = SARIFReporter()
        diags = [
            _make_diag(line=12),
            _make_diag(line=25),
            _make_diag(line=30),
        ]
        result = _make_result(diags)
        reporter.render(result)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        rules = data["runs"][0]["tool"]["driver"]["rules"]
        assert len(rules) == 1
        assert rules[0]["id"] == "BC001"

    def test_tool_metadata(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = SARIFReporter()
        result = _make_result([])
        reporter.render(result)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        driver = data["runs"][0]["tool"]["driver"]
        assert driver["name"] == "behave-lint"
        assert "version" in driver
        assert "informationUri" in driver

    def test_severity_mapping(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = SARIFReporter()
        result = _make_result(
            [
                _make_diag(Severity.WARNING),
                _make_diag(Severity.INFO),
            ]
        )
        reporter.render(result)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        results = data["runs"][0]["results"]
        assert results[0]["level"] == "warning"
        assert results[1]["level"] == "note"

    def test_output_to_file(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        reporter = SARIFReporter()
        result = _make_result([_make_diag()])
        path = str(tmp_path / "output.sarif")
        reporter.render(result, path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["version"] == SARIF_VERSION

    def test_help_uri(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = SARIFReporter()
        result = _make_result([_make_diag()])
        reporter.render(result)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        rules = data["runs"][0]["tool"]["driver"]["rules"]
        assert rules[0]["helpUri"] == "https://example.com/BC001"

    def test_end_line_column(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = SARIFReporter()
        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="Test",
            file_path="test.feature",
            line=5,
            column=1,
            end_line=10,
            end_column=20,
            category=Category.CORRECTNESS,
        )
        result = _make_result([diag])
        reporter.render(result)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        region = data["runs"][0]["results"][0]["locations"][0]["physicalLocation"][
            "region"
        ]
        assert region["endLine"] == 10
        assert region["endColumn"] == 20
