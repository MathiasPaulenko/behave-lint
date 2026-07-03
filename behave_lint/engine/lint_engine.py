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
from pathlib import Path

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
        use_cache: bool = False,
        clear_cache: bool = False,
    ) -> LintResult:
        """Run the full lint pipeline.

        Args:
            paths: Paths to lint. If None, uses config.paths.
            exclude: Glob patterns to exclude.
            max_workers: Thread pool size for rule execution.
            collect_fixes: Whether to also collect auto-fix edits.
            use_cache: Whether to use incremental cache.
            clear_cache: Whether to clear the cache before running.

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

        # 1b. Initialize cache if requested (skip cache when collecting fixes)
        cache_mgr: CacheManager | None = None
        if use_cache and self._config.cache and not collect_fixes:
            from behave_lint.cache.manager import CacheManager

            cache_mgr = CacheManager(self._config.cache_dir, self._config)
            if clear_cache:
                cache_mgr.clear()
                cache_mgr = CacheManager(self._config.cache_dir, self._config)

        # 2. Split files into cached and uncached
        cached_diagnostics: list[Diagnostic] = []
        uncached_paths: list[str] = []
        uncached_contents: dict[str, str] = {}

        for fp in file_paths:
            content = None
            if cache_mgr is not None:
                try:
                    content = Path(fp).read_text(encoding="utf-8")
                except OSError:
                    content = None
                if content is not None:
                    cached = cache_mgr.get(fp, content)
                    if cached is not None:
                        cached_diagnostics.extend(cached)
                        continue
            uncached_paths.append(fp)
            if content is not None:
                uncached_contents[fp] = content

        # 3. Load features for uncached files only
        load_result = load_features(uncached_paths)

        # 4. Build parse error diagnostics
        parse_errors: list[Diagnostic] = []
        for file_path, error_msg in load_result.errors:
            parse_errors.append(_make_parse_error_diagnostic(file_path, error_msg))

        # 5. Execute rules on uncached features
        executor = RuleExecutor(self._registry, self._config)
        raw_diagnostics, fixes = executor.execute(
            load_result.features,
            project=None,
            max_workers=max_workers,
            collect_fixes=collect_fixes,
        )

        # 6. Store uncached results in cache
        if cache_mgr is not None:
            from behave_lint.infrastructure.project_loader import (
                get_file_path_from_feature,
            )

            for feature in load_result.features:
                fp = get_file_path_from_feature(feature)
                if fp and fp in uncached_contents:
                    file_diags = [d for d in raw_diagnostics if d.file_path == fp]
                    cache_mgr.put(fp, uncached_contents[fp], file_diags)
            # Also cache parse errors
            for fp, _ in load_result.errors:
                if fp in uncached_contents:
                    file_diags = [d for d in parse_errors if d.file_path == fp]
                    cache_mgr.put(fp, uncached_contents[fp], file_diags)
            cache_mgr.save()

        # 7. Collect and process diagnostics
        collector = DiagnosticCollector(self._config)
        all_diagnostics = parse_errors + raw_diagnostics + cached_diagnostics
        processed = collector.collect_from(all_diagnostics)

        # 8. Build summary
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        files_with_issues = len({d.file_path for d in processed if d.file_path})
        enabled_count = len(self._registry.get_enabled(self._config))

        cache_hits = cache_mgr.stats.hits if cache_mgr else 0
        cache_misses = cache_mgr.stats.misses if cache_mgr else 0

        summary = LintSummary.from_diagnostics(
            processed,
            total_files=len(file_paths),
            files_with_issues=files_with_issues,
            rules_executed=enabled_count,
            duration_ms=elapsed_ms,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
        )

        result = LintResult(
            diagnostics=processed,
            summary=summary,
            exit_code=0,
            fixes=fixes,
        )

        return result


__all__ = ["LintEngine"]
