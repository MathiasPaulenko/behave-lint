"""Unit tests for the ReporterManager."""

from __future__ import annotations

from typing import ClassVar

import pytest

from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.lint_result import LintResult, LintSummary
from behave_lint.reporters.base import Reporter
from behave_lint.reporters.manager import ReporterManager


class FakeReporter(Reporter):
    """Fake reporter for testing registration."""

    name: ClassVar[str] = "fake"

    def __init__(self) -> None:
        self.rendered = False

    def render(self, result: LintResult, output_file: str | None = None) -> None:
        self.rendered = True


def _make_result() -> LintResult:
    diag = Diagnostic(
        rule_id="BC001",
        severity=Severity.ERROR,
        message="Test",
        file_path="test.feature",
        line=1,
        category=Category.CORRECTNESS,
    )
    return LintResult(
        diagnostics=[diag],
        summary=LintSummary.from_diagnostics([diag], total_files=1),
    )


class TestReporterManager:
    """Tests for ReporterManager."""

    def test_available_formats(self) -> None:
        manager = ReporterManager()
        formats = manager.available_formats()
        assert "console" in formats
        assert "json" in formats
        assert "markdown" in formats
        assert "sarif" in formats
        assert "github" in formats

    def test_get_reporter_builtin(self) -> None:
        manager = ReporterManager()
        reporter = manager.get_reporter("json")
        assert reporter.name == "json"

    def test_get_reporter_unknown(self) -> None:
        manager = ReporterManager()
        with pytest.raises(ValueError, match="Unknown output format"):
            manager.get_reporter("nonexistent")

    def test_get_reporter_cached(self) -> None:
        manager = ReporterManager()
        r1 = manager.get_reporter("json")
        r2 = manager.get_reporter("json")
        assert r1 is r2

    def test_register_custom_reporter(self) -> None:
        manager = ReporterManager()
        manager.register(FakeReporter)
        assert "fake" in manager.available_formats()
        reporter = manager.get_reporter("fake")
        assert reporter.name == "fake"

    def test_register_empty_name_raises(self) -> None:
        manager = ReporterManager()

        class NoNameReporter(Reporter):
            name: ClassVar[str] = ""

            def render(
                self, result: LintResult, output_file: str | None = None
            ) -> None:
                pass

        with pytest.raises(ValueError, match="non-empty"):
            manager.register(NoNameReporter)

    def test_render_single_format(self) -> None:
        manager = ReporterManager()
        result = _make_result()
        manager.render(result, ["json"])
        # No exception means success

    def test_render_multiple_formats(self) -> None:
        manager = ReporterManager()
        result = _make_result()
        manager.render(result, ["json", "markdown"])
        # No exception means success

    def test_render_unknown_format_raises(self) -> None:
        manager = ReporterManager()
        result = _make_result()
        with pytest.raises(ValueError, match="Unknown output format"):
            manager.render(result, ["nonexistent"])
