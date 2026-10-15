"""GitHub Actions reporter — inline PR annotations using workflow commands.

Outputs ``::error`` and ``::warning`` workflow commands that GitHub
Actions renders as inline annotations in PR review.
"""

from __future__ import annotations

from typing import ClassVar

from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Severity
from behave_lint.models.lint_result import LintResult
from behave_lint.reporters.base import Reporter

_SEVERITY_TO_COMMAND: dict[Severity, str] = {
    Severity.ERROR: "error",
    Severity.WARNING: "warning",
    Severity.INFO: "notice",
}


def _escape_data(value: str) -> str:
    """Escape command data per the workflow-command spec."""
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _escape_property(value: str) -> str:
    """Escape a command property value (``file=``, ``col=``, …)."""
    return _escape_data(value).replace(":", "%3A").replace(",", "%2C")


class GitHubActionsReporter(Reporter):
    """GitHub Actions workflow command output for inline PR annotations."""

    name: ClassVar[str] = "github"
    supports_file_output: ClassVar[bool] = False
    supports_stdout: ClassVar[bool] = True

    @staticmethod
    def _format_annotation(diag: Diagnostic) -> str:
        """Format a diagnostic as a GitHub Actions workflow command.

        Args:
            diag: The diagnostic to format.

        Returns:
            A workflow command string like
            ``::error file=...,line=...::rule_id: message``.
        """
        command = _SEVERITY_TO_COMMAND.get(diag.severity, "warning")
        parts: list[str] = [
            f"file={_escape_property(diag.file_path)}",
            f"line={diag.line}",
        ]
        if diag.column is not None:
            parts.append(f"col={diag.column}")
        params = ",".join(parts)
        message = _escape_data(f"{diag.rule_id}: {diag.message}")
        return f"::{command} {params}::{message}"

    def render(self, result: LintResult, output_file: str | None = None) -> None:
        """Render diagnostics to GitHub Actions workflow commands.

        Args:
            result: The lint result containing diagnostics and summary.
            output_file: Ignored — GitHub Actions commands go to stdout.
        """
        lines: list[str] = []

        for diag in result.diagnostics:
            lines.append(self._format_annotation(diag))

        if lines:
            lines.append("")

        s = result.summary
        lines.append(
            f"::notice::behave-lint found {s.total_diagnostics} diagnostics "
            f"({s.error_count} error, {s.warning_count} warning, "
            f"{s.info_count} info) in {s.files_with_issues} files"
        )

        output = "\n".join(lines)
        self._write_output(output, None)


__all__ = ["GitHubActionsReporter"]
