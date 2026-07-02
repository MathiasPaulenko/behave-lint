"""Console reporter — human-readable output for terminal use.

Formats diagnostics with optional ANSI color support, file grouping,
and a summary line with counts and timing.

See SPECIFICATION.md Section 12 and API.md Section 8.
"""

from __future__ import annotations

import sys
from typing import ClassVar

from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Severity
from behave_lint.models.lint_result import LintResult
from behave_lint.reporters.base import Reporter


class _AnsiColors:
    """ANSI escape codes for colored output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"


class ConsoleReporter(Reporter):
    """Human-readable console output with optional color support.

    Attributes:
        use_color: Whether to use ANSI color codes.
    """

    name: ClassVar[str] = "console"
    supports_file_output: ClassVar[bool] = False
    supports_stdout: ClassVar[bool] = True

    def __init__(self, *, use_color: bool | None = None) -> None:
        """Initialize the console reporter.

        Args:
            use_color: Force enable/disable color. If None, auto-detect
                based on whether stdout is a terminal.
        """
        if use_color is None:
            self._use_color = sys.stdout.isatty()
        else:
            self._use_color = use_color

    @property
    def use_color(self) -> bool:
        """Whether color output is enabled.

        Returns:
            True if ANSI color codes are used.
        """
        return self._use_color

    def _colorize(self, text: str, color: str) -> str:
        """Wrap text in ANSI color codes if color is enabled.

        Args:
            text: The text to colorize.
            color: The ANSI color code.

        Returns:
            Colorized text, or plain text if color is disabled.
        """
        if not self._use_color:
            return text
        return f"{color}{text}{_AnsiColors.RESET}"

    def _severity_label(self, severity: Severity) -> str:
        """Get the colored severity label.

        Args:
            severity: The severity to format.

        Returns:
            A colored severity string.
        """
        labels = {
            Severity.ERROR: (self._colorize("error", _AnsiColors.RED)),
            Severity.WARNING: (self._colorize("warning", _AnsiColors.YELLOW)),
            Severity.INFO: (self._colorize("info", _AnsiColors.BLUE)),
        }
        return labels.get(severity, severity.value)

    def _format_diagnostic(self, diag: Diagnostic) -> str:
        """Format a single diagnostic for console output.

        Args:
            diag: The diagnostic to format.

        Returns:
            A formatted line string.
        """
        location = diag.location
        rule_id = self._colorize(diag.rule_id, _AnsiColors.CYAN)
        severity = self._severity_label(diag.severity)
        return f"{location:<40}  {rule_id:<8}  {severity:<10}  {diag.message}"

    def _format_summary(self, result: LintResult) -> str:
        """Format the summary line.

        Args:
            result: The lint result.

        Returns:
            A formatted summary string.
        """
        s = result.summary
        parts: list[str] = []

        if s.total_diagnostics == 0:
            return "No diagnostics found."

        parts.append(f"Found {s.total_diagnostics} diagnostics")
        detail_parts: list[str] = []
        if s.error_count > 0:
            detail_parts.append(f"{s.error_count} error")
        if s.warning_count > 0:
            detail_parts.append(f"{s.warning_count} warning")
        if s.info_count > 0:
            detail_parts.append(f"{s.info_count} info")
        if detail_parts:
            parts.append(f"({', '.join(detail_parts)})")
        parts.append(f"in {s.files_with_issues} files")
        if s.duration_ms > 0:
            parts.append(f"in {s.duration_ms / 1000:.2f}s")
        return " ".join(parts) + "."

    def render(self, result: LintResult, output_file: str | None = None) -> None:
        """Render diagnostics to console output.

        Args:
            result: The lint result containing diagnostics and summary.
            output_file: Ignored — console output always goes to stdout.
        """
        lines: list[str] = []

        for diag in result.diagnostics:
            lines.append(self._format_diagnostic(diag))

        if lines:
            lines.append("")

        lines.append(self._format_summary(result))

        output = "\n".join(lines)
        self._write_output(output, None)


__all__ = ["ConsoleReporter"]
