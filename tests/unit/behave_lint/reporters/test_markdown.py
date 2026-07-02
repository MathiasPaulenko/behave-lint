"""Unit tests for the MarkdownReporter."""

from __future__ import annotations

from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.lint_result import LintResult, LintSummary
from behave_lint.reporters.markdown import MarkdownReporter


def _make_diag(
    severity: Severity = Severity.ERROR,
    rule_id: str = "BC001",
    file_path: str = "features/login.feature",
    line: int = 12,
    message: str = "Duplicate scenario name",
) -> Diagnostic:
    return Diagnostic(
        rule_id=rule_id,
        severity=severity,
        message=message,
        file_path=file_path,
        line=line,
        category=Category.CORRECTNESS,
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
    )


class TestMarkdownReporter:
    """Tests for MarkdownReporter."""

    def test_name(self) -> None:
        assert MarkdownReporter.name == "markdown"

    def test_supports_file_output(self) -> None:
        assert MarkdownReporter.supports_file_output is True

    def test_header_present(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = MarkdownReporter()
        result = _make_result([])
        reporter.render(result)
        captured = capsys.readouterr()
        assert "# behave-lint Report" in captured.out

    def test_summary_table(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = MarkdownReporter()
        result = _make_result([_make_diag()])
        reporter.render(result)
        captured = capsys.readouterr()
        assert "## Summary" in captured.out
        assert "| Total files | 2 |" in captured.out
        assert "| Errors | 1 |" in captured.out

    def test_no_diagnostics(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = MarkdownReporter()
        result = _make_result([])
        reporter.render(result)
        captured = capsys.readouterr()
        assert "No diagnostics found" in captured.out

    def test_diagnostics_table(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = MarkdownReporter()
        result = _make_result([_make_diag()])
        reporter.render(result)
        captured = capsys.readouterr()
        assert "## Diagnostics" in captured.out
        assert "| File | Line | Rule | Severity | Message |" in captured.out
        assert "features/login.feature" in captured.out
        assert "BC001" in captured.out
        assert "Duplicate scenario name" in captured.out

    def test_pipe_escaped_in_message(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = MarkdownReporter()
        diag = _make_diag(message="Error | pipe character")
        result = _make_result([diag])
        reporter.render(result)
        captured = capsys.readouterr()
        assert "\\|" in captured.out

    def test_output_to_file(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        reporter = MarkdownReporter()
        result = _make_result([_make_diag()])
        path = str(tmp_path / "output.md")
        reporter.render(result, path)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        assert "# behave-lint Report" in content

    def test_severity_emoji(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = MarkdownReporter()
        result = _make_result([_make_diag(Severity.WARNING)])
        reporter.render(result)
        captured = capsys.readouterr()
        assert "\u26a0" in captured.out
