"""Unit tests for LintResult and LintSummary.

See API.md Section 4.
"""

from __future__ import annotations

import pytest

from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.lint_result import LintResult, LintSummary


def _make_diag(severity: Severity) -> Diagnostic:
    return Diagnostic(
        rule_id="BC001",
        severity=severity,
        message="test",
        file_path="f.feature",
        line=1,
        category=Category.CORRECTNESS,
    )


class TestLintSummary:
    """Tests for LintSummary."""

    def test_defaults(self) -> None:
        summary = LintSummary()
        assert summary.total_files == 0
        assert summary.files_with_issues == 0
        assert summary.total_diagnostics == 0
        assert summary.error_count == 0
        assert summary.warning_count == 0
        assert summary.info_count == 0
        assert summary.rules_executed == 0
        assert summary.duration_ms == 0.0
        assert summary.cache_hits == 0
        assert summary.cache_misses == 0

    def test_from_diagnostics_empty(self) -> None:
        summary = LintSummary.from_diagnostics([])
        assert summary.total_diagnostics == 0
        assert summary.error_count == 0

    def test_from_diagnostics_mixed(self) -> None:
        diags = [
            _make_diag(Severity.ERROR),
            _make_diag(Severity.ERROR),
            _make_diag(Severity.WARNING),
            _make_diag(Severity.INFO),
        ]
        summary = LintSummary.from_diagnostics(
            diags,
            total_files=10,
            files_with_issues=3,
            rules_executed=5,
            duration_ms=42.5,
            cache_hits=7,
            cache_misses=3,
        )
        assert summary.total_diagnostics == 4
        assert summary.error_count == 2
        assert summary.warning_count == 1
        assert summary.info_count == 1
        assert summary.total_files == 10
        assert summary.files_with_issues == 3
        assert summary.rules_executed == 5
        assert summary.duration_ms == 42.5
        assert summary.cache_hits == 7
        assert summary.cache_misses == 3


class TestLintResult:
    """Tests for LintResult."""

    def test_defaults(self) -> None:
        result = LintResult()
        assert result.diagnostics == []
        assert result.exit_code == 0
        assert result.has_errors is False
        assert result.has_diagnostics is False
        assert result.passed is True

    def test_with_errors(self) -> None:
        result = LintResult(
            diagnostics=[_make_diag(Severity.ERROR)],
            summary=LintSummary.from_diagnostics([_make_diag(Severity.ERROR)]),
            exit_code=1,
        )
        assert result.has_errors is True
        assert result.has_diagnostics is True
        assert result.passed is False

    def test_with_warnings_only(self) -> None:
        result = LintResult(
            diagnostics=[_make_diag(Severity.WARNING)],
            summary=LintSummary.from_diagnostics([_make_diag(Severity.WARNING)]),
            exit_code=0,
        )
        assert result.has_errors is False
        assert result.has_diagnostics is True
        assert result.passed is True

    def test_frozen(self) -> None:
        result = LintResult()
        with pytest.raises(AttributeError):
            result.exit_code = 1  # type: ignore[misc]
