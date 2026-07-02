"""Lint result models — LintResult and LintSummary.

LintResult is the top-level return value of a lint run. It contains
all diagnostics, an execution summary, and the exit code.

See API.md Section 4.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from behave_lint.autofix.models import FixEdit
from behave_lint.models.diagnostic import Diagnostic


@dataclass(frozen=True, slots=True)
class LintSummary:
    """Execution summary for a lint run.

    Attributes:
        total_files: Number of files analyzed.
        files_with_issues: Number of files with at least one diagnostic.
        total_diagnostics: Total diagnostics produced.
        error_count: Diagnostics with severity ERROR.
        warning_count: Diagnostics with severity WARNING.
        info_count: Diagnostics with severity INFO.
        rules_executed: Number of rules that ran.
        duration_ms: Execution time in milliseconds.
        cache_hits: Number of cache hits.
        cache_misses: Number of cache misses.
    """

    total_files: int = 0
    files_with_issues: int = 0
    total_diagnostics: int = 0
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    rules_executed: int = 0
    duration_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0

    @classmethod
    def from_diagnostics(
        cls,
        diagnostics: list[Diagnostic],
        *,
        total_files: int = 0,
        files_with_issues: int = 0,
        rules_executed: int = 0,
        duration_ms: float = 0.0,
        cache_hits: int = 0,
        cache_misses: int = 0,
    ) -> LintSummary:
        """Build a summary from a list of diagnostics.

        Args:
            diagnostics: The diagnostics produced by the run.
            total_files: Number of files analyzed.
            files_with_issues: Number of files with issues.
            rules_executed: Number of rules that ran.
            duration_ms: Execution time in milliseconds.
            cache_hits: Number of cache hits.
            cache_misses: Number of cache misses.

        Returns:
            A LintSummary with counts derived from the diagnostics.
        """
        error_count = sum(1 for d in diagnostics if d.is_error)
        warning_count = sum(1 for d in diagnostics if d.is_warning)
        info_count = sum(1 for d in diagnostics if d.is_info)
        return cls(
            total_files=total_files,
            files_with_issues=files_with_issues,
            total_diagnostics=len(diagnostics),
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
            rules_executed=rules_executed,
            duration_ms=duration_ms,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
        )


@dataclass(frozen=True, slots=True)
class LintResult:
    """Result of a lint run.

    Attributes:
        diagnostics: All diagnostics, sorted by file/line/rule.
        summary: Execution summary.
        exit_code: Exit code (0, 1, or 2).
        fixes: Auto-fix edits collected during the run (if any).
    """

    diagnostics: list[Diagnostic] = field(default_factory=list)
    summary: LintSummary = field(default_factory=LintSummary)
    exit_code: int = 0
    fixes: list[FixEdit] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Whether any diagnostic has ERROR severity.

        Returns:
            True if at least one error diagnostic exists.
        """
        return self.summary.error_count > 0

    @property
    def has_diagnostics(self) -> bool:
        """Whether any diagnostics were produced.

        Returns:
            True if the diagnostics list is non-empty.
        """
        return self.summary.total_diagnostics > 0

    @property
    def passed(self) -> bool:
        """Whether the lint run passed (exit code 0).

        Returns:
            True if exit_code is 0.
        """
        return self.exit_code == 0


__all__ = ["LintResult", "LintSummary"]
