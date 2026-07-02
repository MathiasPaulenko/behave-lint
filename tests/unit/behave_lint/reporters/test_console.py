"""Unit tests for the ConsoleReporter."""

from __future__ import annotations

from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.lint_result import LintResult, LintSummary
from behave_lint.reporters.console import ConsoleReporter


def _make_diag(
    severity: Severity = Severity.ERROR,
    rule_id: str = "BC001",
    file_path: str = "features/login.feature",
    line: int = 12,
    column: int | None = 1,
    message: str = "Duplicate scenario name 'Login'",
) -> Diagnostic:
    return Diagnostic(
        rule_id=rule_id,
        severity=severity,
        message=message,
        file_path=file_path,
        line=line,
        column=column,
        category=Category.CORRECTNESS,
    )


def _make_result(diagnostics: list[Diagnostic] | None = None) -> LintResult:
    diags = diagnostics or []
    return LintResult(
        diagnostics=diags,
        summary=LintSummary.from_diagnostics(
            diags,
            total_files=2,
            files_with_issues=len({d.file_path for d in diags}),
            duration_ms=120.0,
        ),
    )


class TestConsoleReporter:
    """Tests for ConsoleReporter."""

    def test_name(self) -> None:
        assert ConsoleReporter.name == "console"

    def test_no_diagnostics(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = ConsoleReporter(use_color=False)
        result = _make_result([])
        reporter.render(result)
        captured = capsys.readouterr()
        assert "No diagnostics found" in captured.out

    def test_single_diagnostic(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = ConsoleReporter(use_color=False)
        result = _make_result([_make_diag()])
        reporter.render(result)
        captured = capsys.readouterr()
        assert "features/login.feature:12:1" in captured.out
        assert "BC001" in captured.out
        assert "error" in captured.out
        assert "Duplicate scenario name" in captured.out

    def test_summary_line(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = ConsoleReporter(use_color=False)
        diags = [
            _make_diag(Severity.ERROR),
            _make_diag(Severity.WARNING, rule_id="BS001", line=25),
            _make_diag(Severity.INFO, rule_id="BK001", line=3),
        ]
        result = _make_result(diags)
        reporter.render(result)
        captured = capsys.readouterr()
        assert "Found 3 diagnostics" in captured.out
        assert "1 error" in captured.out
        assert "1 warning" in captured.out
        assert "1 info" in captured.out

    def test_color_disabled(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = ConsoleReporter(use_color=False)
        result = _make_result([_make_diag()])
        reporter.render(result)
        captured = capsys.readouterr()
        assert "\033[" not in captured.out

    def test_color_enabled(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = ConsoleReporter(use_color=True)
        result = _make_result([_make_diag()])
        reporter.render(result)
        captured = capsys.readouterr()
        assert "\033[31m" in captured.out

    def test_supports_file_output_false(self) -> None:
        assert ConsoleReporter.supports_file_output is False

    def test_supports_stdout_true(self) -> None:
        assert ConsoleReporter.supports_stdout is True

    def test_multiple_files(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = ConsoleReporter(use_color=False)
        diags = [
            _make_diag(file_path="features/a.feature", line=1),
            _make_diag(file_path="features/b.feature", line=5),
        ]
        result = _make_result(diags)
        reporter.render(result)
        captured = capsys.readouterr()
        assert "features/a.feature:1" in captured.out
        assert "features/b.feature:5" in captured.out

    def test_duration_in_summary(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = ConsoleReporter(use_color=False)
        result = _make_result([_make_diag()])
        reporter.render(result)
        captured = capsys.readouterr()
        assert "0.12s" in captured.out
