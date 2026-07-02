"""Lint engine — pipeline orchestrator (C03).

Coordinates the entire linting process:
1. Discover .feature files in the specified paths.
2. Load feature files via behave-model.
3. Execute enabled rules via RuleExecutor.
4. Collect and process diagnostics via DiagnosticCollector.
5. Build and return a LintResult.

See COMPONENT_DESIGN.md C03 and ARCHITECTURE.md Section 6.
"""

from __future__ import annotations

import time

from behave_lint.diagnostics.collector import DiagnosticCollector
from behave_lint.infrastructure.file_discovery import discover_files
from behave_lint.infrastructure.project_loader import load_features
from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.lint_result import LintResult, LintSummary
from behave_lint.rules.executor import RuleExecutor
from behave_lint.rules.registry import RuleRegistry


def _make_parse_error_diagnostic(
    file_path: str,
    message: str,
) -> Diagnostic:
    """Create a diagnostic for a parse error.

    Args:
        file_path: Path to the file that failed to parse.
        message: Error message from the parser.

    Returns:
        An ERROR-level diagnostic for the parse failure.
    """
    return Diagnostic(
        rule_id="B000",
        severity=Severity.ERROR,
        message=f"Parse error: {message}",
        file_path=file_path,
        line=1,
        category=Category.CORRECTNESS,
        suggestion="Fix the Gherkin syntax error in this file.",
    )


class LintEngine:
    """Pipeline orchestrator for the linting process.

    Created per lint run with a resolved configuration and rule registry.
    Orchestrates file discovery, feature loading, rule execution, and
    diagnostic collection.

    Attributes:
        config: The resolved configuration object.
        registry: The rule registry with registered rules.
    """

    def __init__(
        self,
        config: Config,
        registry: RuleRegistry,
    ) -> None:
        """Initialize the lint engine.

        Args:
            config: Resolved configuration object.
            registry: Rule registry with registered rules.
        """
        self._config = config
        self._registry = registry

    def lint(
        self,
        paths: list[str] | None = None,
        *,
        exclude: list[str] | None = None,
        max_workers: int | None = None,
        collect_fixes: bool = False,
    ) -> LintResult:
        """Run the full lint pipeline.

        Args:
            paths: Paths to lint. If None, uses config.paths.
            exclude: Glob patterns to exclude.
            max_workers: Thread pool size for rule execution.
            collect_fixes: Whether to also collect auto-fix edits.

        Returns:
            A LintResult with diagnostics, summary, and exit code.
        """
        start_time = time.perf_counter()

        lint_paths = paths if paths is not None else list(self._config.paths)
        exclude_patterns = exclude or []

        # 1. Discover files
        file_paths = discover_files(lint_paths, exclude=exclude_patterns)

        if not file_paths:
            return LintResult(
                diagnostics=[],
                summary=LintSummary(
                    total_files=0,
                    files_with_issues=0,
                    rules_executed=0,
                    duration_ms=0.0,
                ),
                exit_code=0,
            )

        # 2. Load features
        load_result = load_features(file_paths)

        # 3. Build parse error diagnostics
        parse_errors: list[Diagnostic] = []
        for file_path, error_msg in load_result.errors:
            parse_errors.append(_make_parse_error_diagnostic(file_path, error_msg))

        # 4. Execute rules
        executor = RuleExecutor(self._registry, self._config)
        raw_diagnostics, fixes = executor.execute(
            load_result.features,
            project=None,
            max_workers=max_workers,
            collect_fixes=collect_fixes,
        )

        # 5. Collect and process diagnostics
        collector = DiagnosticCollector(self._config)
        all_diagnostics = parse_errors + raw_diagnostics
        processed = collector.collect_from(all_diagnostics)

        # 6. Build summary
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        files_with_issues = len({d.file_path for d in processed if d.file_path})
        enabled_count = len(self._registry.get_enabled(self._config))

        summary = LintSummary.from_diagnostics(
            processed,
            total_files=len(file_paths),
            files_with_issues=files_with_issues,
            rules_executed=enabled_count,
            duration_ms=elapsed_ms,
        )

        result = LintResult(
            diagnostics=processed,
            summary=summary,
            exit_code=0,
            fixes=fixes,
        )

        return result


__all__ = ["LintEngine"]
