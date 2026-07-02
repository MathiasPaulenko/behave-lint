"""Unit tests for the GitHubActionsReporter."""

from __future__ import annotations

from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.lint_result import LintResult, LintSummary
from behave_lint.reporters.github import GitHubActionsReporter


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


class TestGitHubActionsReporter:
    """Tests for GitHubActionsReporter."""

    def test_name(self) -> None:
        assert GitHubActionsReporter.name == "github"

    def test_supports_file_output_false(self) -> None:
        assert GitHubActionsReporter.supports_file_output is False

    def test_error_annotation(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = GitHubActionsReporter()
        result = _make_result([_make_diag(Severity.ERROR)])
        reporter.render(result)
        captured = capsys.readouterr()
        assert (
            "::error file=features/login.feature,line=12,col=1"
            "::BC001: Duplicate scenario name" in captured.out
        )

    def test_warning_annotation(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = GitHubActionsReporter()
        result = _make_result([_make_diag(Severity.WARNING)])
        reporter.render(result)
        captured = capsys.readouterr()
        assert "::warning " in captured.out

    def test_info_annotation(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = GitHubActionsReporter()
        result = _make_result([_make_diag(Severity.INFO)])
        reporter.render(result)
        captured = capsys.readouterr()
        assert "::notice " in captured.out

    def test_no_column(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = GitHubActionsReporter()
        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="Test",
            file_path="test.feature",
            line=5,
            category=Category.CORRECTNESS,
        )
        result = _make_result([diag])
        reporter.render(result)
        captured = capsys.readouterr()
        assert "::error file=test.feature,line=5::BC001: Test" in captured.out
        assert "col=" not in captured.out

    def test_notice_summary(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = GitHubActionsReporter()
        result = _make_result([_make_diag()])
        reporter.render(result)
        captured = capsys.readouterr()
        assert "::notice::" in captured.out
        assert "1 diagnostics" in captured.out

    def test_no_diagnostics(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = GitHubActionsReporter()
        result = _make_result([])
        reporter.render(result)
        captured = capsys.readouterr()
        assert "::notice::" in captured.out
        assert "0 diagnostics" in captured.out

    def test_multiple_diagnostics(self, capsys) -> None:  # type: ignore[no-untyped-def]
        reporter = GitHubActionsReporter()
        diags = [
            _make_diag(Severity.ERROR, line=12),
            _make_diag(Severity.WARNING, rule_id="BS001", line=25),
        ]
        result = _make_result(diags)
        reporter.render(result)
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        error_lines = [ln for ln in lines if ln.startswith("::error")]
        warning_lines = [ln for ln in lines if ln.startswith("::warning")]
        assert len(error_lines) == 1
        assert len(warning_lines) == 1
