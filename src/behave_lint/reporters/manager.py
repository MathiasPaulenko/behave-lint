"""Reporter manager — selects and coordinates output reporters.

Selects reporters based on the configured output format, instantiates
them, and coordinates rendering. Supports multiple simultaneous
output formats.

See COMPONENT_DESIGN.md C08 and API.md Section 8.
"""

from __future__ import annotations

from behave_lint.models.lint_result import LintResult
from behave_lint.reporters.base import Reporter
from behave_lint.reporters.console import ConsoleReporter
from behave_lint.reporters.github import GitHubActionsReporter
from behave_lint.reporters.json_reporter import JSONReporter
from behave_lint.reporters.markdown import MarkdownReporter
from behave_lint.reporters.sarif import SARIFReporter

_BUILTIN_REPORTERS: dict[str, type[Reporter]] = {
    "console": ConsoleReporter,
    "json": JSONReporter,
    "markdown": MarkdownReporter,
    "sarif": SARIFReporter,
    "github": GitHubActionsReporter,
}


class ReporterManager:
    """Selects, instantiates, and coordinates output reporters.

    Attributes:
        _reporters: Mapping of format name to reporter class.
        _instances: Mapping of format name to reporter instance.
    """

    def __init__(self) -> None:
        """Initialize the reporter manager with built-in reporters."""
        self._reporters: dict[str, type[Reporter]] = dict(_BUILTIN_REPORTERS)
        self._instances: dict[str, Reporter] = {}

    def register(self, reporter_cls: type[Reporter]) -> None:
        """Register a custom reporter class.

        Args:
            reporter_cls: The reporter class to register. Must have a
                non-empty ``name`` class attribute.
        """
        name = reporter_cls.name
        if not name:
            raise ValueError("Reporter must have a non-empty 'name' attribute.")
        self._reporters[name] = reporter_cls

    def get_reporter(self, format_name: str) -> Reporter:
        """Get or create a reporter instance for the given format.

        Args:
            format_name: The output format name (e.g., "json").

        Returns:
            A reporter instance.

        Raises:
            ValueError: If the format is not registered.
        """
        if format_name in self._instances:
            return self._instances[format_name]

        cls = self._reporters.get(format_name)
        if cls is None:
            raise ValueError(
                f"Unknown output format: '{format_name}'. "
                f"Available: {', '.join(sorted(self._reporters))}"
            )

        instance = cls()
        self._instances[format_name] = instance
        return instance

    def available_formats(self) -> list[str]:
        """List all registered output format names.

        Returns:
            A sorted list of format names.
        """
        return sorted(self._reporters)

    def render(
        self,
        result: LintResult,
        formats: list[str],
        output_file: str | None = None,
    ) -> None:
        """Render diagnostics using one or more output formats.

        Args:
            result: The lint result to render.
            formats: List of output format names.
            output_file: Path to write output to. If None, writes to
                stdout. Only used for formats that support file output.
        """
        for fmt in formats:
            reporter = self.get_reporter(fmt)
            if output_file and not reporter.supports_file_output:
                reporter.render(result, None)
            else:
                reporter.render(result, output_file)


__all__ = ["ReporterManager"]
