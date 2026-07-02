"""Rule executor — schedules and executes rules, collects diagnostics.

Schedules single-file rules for parallel execution and cross-file rules
sequentially. Each rule receives its own context. Rule failures are
isolated — a failure in one rule does not crash others.

See COMPONENT_DESIGN.md C05 and RULE_ENGINE.md Section 6.
"""

from __future__ import annotations

import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from behave_lint.autofix.models import FixEdit
from behave_lint.diagnostics.validation import validate_diagnostics
from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.rule_metadata import RuleMetadata
from behave_lint.rules.base import Rule
from behave_lint.rules.diagnostic_factory import DiagnosticFactory
from behave_lint.rules.registry import RuleRegistry
from behave_lint.rules.scope import RuleScope


class RuleExecutor:
    """Executes rules and collects raw diagnostics.

    Created per lint run. Executes rules in deterministic order.
    Results are passed to the diagnostic collector for filtering.

    Attributes:
        registry: The rule registry with registered rules.
        config: The resolved configuration object.
    """

    def __init__(
        self,
        registry: RuleRegistry,
        config: Config,
    ) -> None:
        """Initialize the executor.

        Args:
            registry: The rule registry with registered rules.
            config: The resolved configuration object.
        """
        self._registry = registry
        self._config = config

    def execute(
        self,
        features: list[Any],
        project: Any | None = None,
        *,
        max_workers: int | None = None,
        collect_fixes: bool = False,
    ) -> tuple[list[Diagnostic], list[FixEdit]]:
        """Execute all enabled rules and collect diagnostics.

        Single-file rules are executed for each (rule, feature) pair.
        Cross-file rules are executed once with the full project.

        Args:
            features: List of parsed feature models.
            project: The full project model (for cross-file rules).
            max_workers: Thread pool size (default: CPU count).
            collect_fixes: Whether to also collect auto-fix edits.

        Returns:
            A tuple of (raw diagnostics, fix edits) from all rules.
        """
        enabled = self._registry.get_enabled(self._config)
        all_diagnostics: list[Diagnostic] = []
        all_fixes: list[FixEdit] = []

        # Partition into single-file and cross-file
        single_file_rules: list[tuple[type[Rule], RuleMetadata]] = []
        cross_file_rules: list[tuple[type[Rule], RuleMetadata]] = []

        for rule_class, metadata in enabled:
            scope = getattr(rule_class, "scope", RuleScope.SINGLE_FILE)
            if scope == RuleScope.CROSS_FILE:
                cross_file_rules.append((rule_class, metadata))
            else:
                single_file_rules.append((rule_class, metadata))

        # Execute single-file rules (parallel)
        if single_file_rules and features:
            diags, fixes = self._execute_single_file(
                single_file_rules, features, max_workers, collect_fixes
            )
            all_diagnostics.extend(diags)
            all_fixes.extend(fixes)

        # Execute cross-file rules (sequential)
        for rule_class, metadata in cross_file_rules:
            diags, fixes = self._execute_rule(
                rule_class,
                metadata,
                project,
                is_cross_file=True,
                collect_fixes=collect_fixes,
            )
            all_diagnostics.extend(diags)
            all_fixes.extend(fixes)

        return all_diagnostics, all_fixes

    def _execute_single_file(
        self,
        rules: list[tuple[type[Rule], RuleMetadata]],
        features: list[Any],
        max_workers: int | None,
        collect_fixes: bool = False,
    ) -> tuple[list[Diagnostic], list[FixEdit]]:
        """Execute single-file rules in parallel.

        Args:
            rules: List of (rule_class, metadata) tuples.
            features: List of parsed feature models.
            max_workers: Thread pool size.
            collect_fixes: Whether to also collect auto-fix edits.

        Returns:
            A tuple of (diagnostics, fix edits) from all single-file
            rule executions.
        """
        # Build work units: (rule_class, metadata, feature)
        work_units: list[tuple[type[Rule], RuleMetadata, Any]] = []
        for rule_class, metadata in rules:
            for feature in features:
                work_units.append((rule_class, metadata, feature))

        if not work_units:
            return [], []

        results: list[Diagnostic] = []
        all_fixes: list[FixEdit] = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self._execute_rule,
                    rule_class,
                    metadata,
                    feature,
                    collect_fixes=collect_fixes,
                ): (
                    metadata.rule_id,
                    getattr(feature, "file_path", ""),
                )
                for rule_class, metadata, feature in work_units
            }

            for future in as_completed(futures):
                rule_id, file_path = futures[future]
                try:
                    diags, fixes = future.result()
                    results.extend(diags)
                    all_fixes.extend(fixes)
                except Exception as exc:
                    warnings.warn(
                        f"Rule '{rule_id}' failed on '{file_path}': {exc}. "
                        "Rule skipped for this file.",
                        stacklevel=2,
                    )

        return results, all_fixes

    def _execute_rule(
        self,
        rule_class: type[Rule],
        metadata: RuleMetadata,
        model: Any,
        *,
        is_cross_file: bool = False,
        collect_fixes: bool = False,
    ) -> tuple[list[Diagnostic], list[FixEdit]]:
        """Execute a single rule and return its diagnostics.

        Args:
            rule_class: The rule class to instantiate.
            metadata: The rule's metadata.
            model: The feature (single-file) or project (cross-file).
            is_cross_file: Whether this is a cross-file rule.
            collect_fixes: Whether to also collect auto-fix edits.

        Returns:
            A tuple of (validated diagnostics, fix edits) from the rule.
        """
        # Instantiate
        try:
            rule = rule_class()
        except Exception as exc:
            warnings.warn(
                f"Rule '{metadata.rule_id}' failed to instantiate: {exc}. "
                "Rule skipped.",
                stacklevel=2,
            )
            return [], []

        # Determine effective severity
        severity = self._config.get_severity(
            metadata.rule_id, metadata.default_severity
        )

        # Determine file path
        file_path: str | None = None
        if not is_cross_file:
            file_path = getattr(model, "file_path", None)
            if not file_path:
                location = getattr(model, "location", None)
                if location is not None:
                    file_path = getattr(location, "filename", None)

        # Create diagnostic factory
        factory = DiagnosticFactory(
            rule_id=metadata.rule_id,
            category=metadata.category,
            severity=severity,
            file_path=file_path,
        )

        # Inject factory into rule
        rule._set_diagnostic_factory(factory)

        # Emit deprecation warning if needed
        if metadata.deprecated:
            deprecation_msg = f"Rule '{metadata.rule_id}' is deprecated."
            if metadata.replaced_by:
                deprecation_msg += f" Use '{metadata.replaced_by}' instead."
            warnings.warn(
                deprecation_msg,
                DeprecationWarning,
                stacklevel=2,
            )

        # Execute
        try:
            raw_diagnostics = rule.check(model, self._config)
        except Exception as exc:
            warnings.warn(
                f"Rule '{metadata.rule_id}' raised an exception: {exc}. Rule skipped.",
                stacklevel=2,
            )
            return [], []

        if raw_diagnostics is None:
            return [], []

        # Stamp diagnostics: ensure rule_id and category match metadata
        stamped: list[Diagnostic] = []
        for diag in raw_diagnostics:
            stamped_diag = Diagnostic(
                rule_id=metadata.rule_id,
                severity=severity,
                message=diag.message,
                file_path=diag.file_path,
                line=diag.line,
                category=metadata.category,
                column=diag.column,
                end_line=diag.end_line,
                end_column=diag.end_column,
                suggestion=diag.suggestion,
                doc_url=diag.doc_url or metadata.doc_url,
            )
            stamped.append(stamped_diag)

        # Validate diagnostics
        validated = validate_diagnostics(stamped)

        # Collect fixes if requested
        fixes: list[FixEdit] = []
        if collect_fixes and validated:
            try:
                fixes = rule.get_fixes(model, self._config, validated)
            except Exception as exc:
                warnings.warn(
                    f"Rule '{metadata.rule_id}' get_fixes() raised: {exc}. "
                    "Fixes skipped for this rule.",
                    stacklevel=2,
                )
                fixes = []

        return validated, fixes


__all__ = ["RuleExecutor"]
