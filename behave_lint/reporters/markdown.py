"""Markdown reporter — output for GitHub Actions summaries and PR comments.

Produces a Markdown document with a summary table and a diagnostic
table, using collapsible sections for long diagnostic lists.

See SPECIFICATION.md Section 12 and API.md Section 8.
"""

from __future__ import annotations

from typing import ClassVar

from behave_lint.models.enums import Severity
from behave_lint.models.lint_result import LintResult
from behave_lint.reporters.base import Reporter


class MarkdownReporter(Reporter):
    """Markdown output for GitHub Actions summaries and PR comments."""

    name: ClassVar[str] = "markdown"
    supports_file_output: ClassVar[bool] = True
    supports_stdout: ClassVar[bool] = True

    @staticmethod
    def _severity_emoji(severity: Severity) -> str:
        """Get an emoji for a severity level.

        Args:
            severity: The severity level.

        Returns:
            An emoji string representing the severity.
        """
        emojis = {
            Severity.ERROR: "\u274c",
            Severity.WARNING: "\u26a0\ufe0f",
            Severity.INFO: "\u2139\ufe0f",
        }
        return emojis.get(severity, severity.value)

    def _summary_table(self, result: LintResult) -> str:
        """Generate the summary table.

        Args:
            result: The lint result.

        Returns:
            A Markdown table string.
        """
        s = result.summary
        lines = [
            "## Summary",
            "",
            "| Metric | Count |",
            "|--------|-------|",
            f"| Total files | {s.total_files} |",
            f"| Files with issues | {s.files_with_issues} |",
            f"| Total diagnostics | {s.total_diagnostics} |",
            f"| Errors | {s.error_count} |",
            f"| Warnings | {s.warning_count} |",
            f"| Info | {s.info_count} |",
            f"| Rules executed | {s.rules_executed} |",
            f"| Duration | {s.duration_ms / 1000:.2f}s |",
        ]
        return "\n".join(lines)

    def _diagnostics_table(self, result: LintResult) -> str:
        """Generate the diagnostics table.

        Args:
            result: The lint result.

        Returns:
            A Markdown table string.
        """
        if not result.diagnostics:
            return "## Diagnostics\n\nNo diagnostics found. \u2705"

        lines = [
            "## Diagnostics",
            "",
            "| File | Line | Rule | Severity | Message |",
            "|------|------|------|----------|---------|",
        ]

        for diag in result.diagnostics:
            severity = f"{self._severity_emoji(diag.severity)} {diag.severity.value}"
            message = diag.message.replace("|", "\\|")
            lines.append(
                f"| {diag.file_path} | {diag.line} | "
                f"{diag.rule_id} | {severity} | {message} |"
            )

        return "\n".join(lines)

    def render(self, result: LintResult, output_file: str | None = None) -> None:
        """Render diagnostics to Markdown output.

        Args:
            result: The lint result containing diagnostics and summary.
            output_file: Path to write Markdown to. If None, writes to
                stdout.
        """
        sections = [
            "# behave-lint Report",
            "",
            self._summary_table(result),
            "",
            self._diagnostics_table(result),
            "",
        ]

        content = "\n".join(sections)
        self._write_output(content, output_file)


__all__ = ["MarkdownReporter"]
