"""JSON reporter — machine-readable output with stable schema.

Produces a JSON object with schemaVersion, diagnostics array, and
summary object. The schema is versioned independently of the tool.

See SPECIFICATION.md Section 12 and API.md Section 8.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import ClassVar

from behave_lint import __version__
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.lint_result import LintResult
from behave_lint.reporters.base import Reporter

SCHEMA_VERSION = "1.0.0"


class JSONReporter(Reporter):
    """Machine-readable JSON output with a stable, versioned schema."""

    name: ClassVar[str] = "json"
    supports_file_output: ClassVar[bool] = True
    supports_stdout: ClassVar[bool] = True

    @staticmethod
    def _diagnostic_to_dict(diag: Diagnostic) -> dict[str, object]:
        """Convert a diagnostic to a JSON-serializable dictionary.

        Args:
            diag: The diagnostic to convert.

        Returns:
            A dictionary representation of the diagnostic.
        """
        result: dict[str, object] = {
            "rule_id": diag.rule_id,
            "severity": diag.severity.value,
            "message": diag.message,
            "file_path": diag.file_path,
            "line": diag.line,
            "category": diag.category.value,
        }
        if diag.column is not None:
            result["column"] = diag.column
        if diag.end_line is not None:
            result["end_line"] = diag.end_line
        if diag.end_column is not None:
            result["end_column"] = diag.end_column
        if diag.suggestion is not None:
            result["suggestion"] = diag.suggestion
        if diag.doc_url is not None:
            result["doc_url"] = diag.doc_url
        return result

    @staticmethod
    def _summary_to_dict(result: LintResult) -> dict[str, object]:
        """Convert the lint summary to a JSON-serializable dictionary.

        Args:
            result: The lint result.

        Returns:
            A dictionary representation of the summary.
        """
        s = result.summary
        return {
            "total_files": s.total_files,
            "files_with_issues": s.files_with_issues,
            "total_diagnostics": s.total_diagnostics,
            "error_count": s.error_count,
            "warning_count": s.warning_count,
            "info_count": s.info_count,
            "rules_executed": s.rules_executed,
            "duration_ms": s.duration_ms,
            "cache_hits": s.cache_hits,
            "cache_misses": s.cache_misses,
        }

    def render(self, result: LintResult, output_file: str | None = None) -> None:
        """Render diagnostics to JSON output.

        Args:
            result: The lint result containing diagnostics and summary.
            output_file: Path to write JSON to. If None, writes to stdout.
        """
        output = {
            "schemaVersion": SCHEMA_VERSION,
            "tool": {
                "name": "behave-lint",
                "version": __version__,
            },
            "timestamp": datetime.now(UTC).isoformat(),
            "diagnostics": [self._diagnostic_to_dict(d) for d in result.diagnostics],
            "summary": self._summary_to_dict(result),
            "exit_code": result.exit_code,
        }

        content = json.dumps(output, indent=2, ensure_ascii=False)
        self._write_output(content, output_file)


__all__ = ["SCHEMA_VERSION", "JSONReporter"]
