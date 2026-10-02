"""Example reporter plugin: CSV output for behave-lint."""

from __future__ import annotations

import csv
import io
import sys
from typing import ClassVar

from behave_lint.models.lint_result import LintResult
from behave_lint.reporters.base import Reporter


class CSVReporter(Reporter):
    """Writes diagnostics as CSV rows: file,line,rule,severity,message."""

    name: ClassVar[str] = "csv"
    supports_file_output: ClassVar[bool] = True
    supports_stdout: ClassVar[bool] = True

    def render(self, result: LintResult, output_file: str | None = None) -> None:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["file", "line", "rule", "severity", "message"])
        for d in result.diagnostics:
            writer.writerow(
                [d.file_path, d.line, d.rule_id, d.severity.value, d.message]
            )
        content = buf.getvalue()
        if output_file:
            from pathlib import Path

            Path(output_file).write_text(content, encoding="utf-8")
        else:
            sys.stdout.write(content)


__all__ = ["CSVReporter"]
