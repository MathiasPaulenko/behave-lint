"""Diagnostic collector — aggregate, validate, filter, deduplicate, sort.

The collector is the pipeline orchestrator for diagnostic processing.
It takes raw diagnostics from rule execution and produces a clean,
sorted, deduplicated list ready for reporting.

Pipeline: validate → filter (severity, disabled rules, excluded files,
inline disables) → deduplicate → sort.

See DIAGNOSTIC_ENGINE.md Section 2 and COMPONENT_DESIGN.md C07.
"""

from __future__ import annotations

from behave_lint.diagnostics.dedup import deduplicate_diagnostics
from behave_lint.diagnostics.filters import (
    filter_by_severity,
    filter_disabled_rules,
    filter_excluded_files,
    filter_inline_disables,
)
from behave_lint.diagnostics.sorting import sort_diagnostics
from behave_lint.diagnostics.validation import validate_diagnostics
from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Severity


class DiagnosticCollector:
    """Collects, filters, sorts, and deduplicates diagnostics.

    The collector processes raw diagnostics through a pipeline:
    1. Validate — drop invalid diagnostics.
    2. Filter by severity — remove OFF and below-threshold.
    3. Filter disabled rules — safety net for disabled rules.
    4. Filter excluded files — remove diagnostics from excluded paths.
    5. Filter inline disables — remove suppressed diagnostics.
    6. Deduplicate — remove exact duplicates.
    7. Sort — deterministic order (file, line, column, rule ID).

    Attributes:
        config: The configuration object for filtering decisions.
    """

    def __init__(self, config: Config) -> None:
        """Initialize the collector.

        Args:
            config: Configuration object with rule selection, severity
                overrides, and exclude patterns.
        """
        self._config = config
        self._raw: list[Diagnostic] = []
        self._file_contents: dict[str, list[str]] = {}

    def add_diagnostics(self, diagnostics: list[Diagnostic]) -> None:
        """Add raw diagnostics to the collector.

        Args:
            diagnostics: Raw diagnostics from rule execution.
        """
        self._raw.extend(diagnostics)

    def add_file_contents(self, file_path: str, lines: list[str]) -> None:
        """Add file contents for inline disable comment parsing.

        Args:
            file_path: Path to the feature file.
            lines: Lines of the feature file.
        """
        self._file_contents[file_path] = lines

    def collect(self) -> list[Diagnostic]:
        """Process all collected diagnostics through the pipeline.

        Returns:
            Sorted, filtered, deduplicated list of diagnostics.
        """
        # 1. Validate
        result = validate_diagnostics(self._raw)

        # 2. Filter by severity (remove OFF, keep INFO and above)
        result = filter_by_severity(result, min_severity=Severity.INFO)

        # 3. Filter disabled rules (safety net)
        result = filter_disabled_rules(result, self._config)

        # 4. Filter excluded files
        result = filter_excluded_files(result, [])

        # 5. Filter inline disables
        if self._file_contents:
            result = filter_inline_disables(result, self._file_contents)

        # 6. Deduplicate
        result = deduplicate_diagnostics(result)

        # 7. Sort
        result = sort_diagnostics(result)

        return result

    def collect_from(
        self,
        diagnostics: list[Diagnostic],
        *,
        file_contents: dict[str, list[str]] | None = None,
    ) -> list[Diagnostic]:
        """Convenience method: add and collect in one call.

        Args:
            diagnostics: Raw diagnostics from rule execution.
            file_contents: Optional file contents for inline disable
                parsing.

        Returns:
            Sorted, filtered, deduplicated list of diagnostics.
        """
        self.add_diagnostics(diagnostics)
        if file_contents:
            for path, lines in file_contents.items():
                self.add_file_contents(path, lines)
        return self.collect()


__all__ = ["DiagnosticCollector"]
