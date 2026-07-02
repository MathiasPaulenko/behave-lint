"""Unit tests for the Reporter base class."""

from __future__ import annotations

from typing import ClassVar

import pytest

from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.lint_result import LintResult, LintSummary
from behave_lint.reporters.base import Reporter


class StubReporter(Reporter):
    """Minimal reporter for testing the base class."""

    name: ClassVar[str] = "stub"

    def __init__(self) -> None:
        self.rendered = False
        self.last_result: LintResult | None = None
        self.last_output_file: str | None = None

    def render(self, result: LintResult, output_file: str | None = None) -> None:
        self.rendered = True
        self.last_result = result
        self.last_output_file = output_file


def _make_result(diagnostics: list[Diagnostic] | None = None) -> LintResult:
    return LintResult(
        diagnostics=diagnostics or [],
        summary=LintSummary.from_diagnostics(diagnostics or [], total_files=1),
    )


class TestReporterBase:
    """Tests for the Reporter base class."""

    def test_cannot_instantiate_abstract(self) -> None:
        with pytest.raises(TypeError):
            Reporter()  # type: ignore[abstract]

    def test_stub_reporter_name(self) -> None:
        assert StubReporter.name == "stub"

    def test_default_capabilities(self) -> None:
        assert StubReporter.supports_file_output is True
        assert StubReporter.supports_stdout is True
        assert StubReporter.supports_streaming is False

    def test_render_called(self) -> None:
        reporter = StubReporter()
        result = _make_result()
        reporter.render(result)
        assert reporter.rendered is True
        assert reporter.last_result is result

    def test_render_with_output_file(self) -> None:
        reporter = StubReporter()
        result = _make_result()
        reporter.render(result, "output.txt")
        assert reporter.last_output_file == "output.txt"

    def test_write_output_to_file(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        path = str(tmp_path / "out.txt")
        Reporter._write_output("hello", path)
        with open(path, encoding="utf-8") as f:
            assert f.read() == "hello"

    def test_write_output_to_stdout(self, capsys) -> None:  # type: ignore[no-untyped-def]
        Reporter._write_output("hello", None)
        captured = capsys.readouterr()
        assert captured.out == "hello\n"
