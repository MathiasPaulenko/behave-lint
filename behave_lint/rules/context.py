"""Rule context — execution environment provided to each rule.

The context is read-only. Rules must not modify it. It contains all
the data and services a rule needs to perform its analysis.

See RULE_ENGINE.md Section 8.
"""

from __future__ import annotations

from typing import Any, Protocol

from behave_lint.models.config import Config
from behave_lint.models.enums import Category, Severity
from behave_lint.rules.diagnostic_factory import DiagnosticFactory


class FeatureLike(Protocol):
    """Protocol for a parsed feature (from behave-model)."""

    file_path: str
    line: int

    @property
    def name(self) -> str: ...

    @property
    def scenarios(self) -> list[Any]: ...


class ProjectLike(Protocol):
    """Protocol for a parsed project (from behave-model)."""

    @property
    def features(self) -> list[Any]: ...


class RuleContext:
    """Execution environment for a rule.

    Attributes:
        feature: The feature being analyzed (single-file rules).
        project: The full project model (cross-file rules).
        config: The resolved configuration object (immutable).
        rule_params: This rule's parameters (merged defaults + user config).
        severity: The effective severity (after overrides).
        file_path: Path to the current file (single-file rules).
        step_definitions: Parsed step definitions (if configured).
        diagnostic_factory: Helper for creating diagnostics.
    """

    __slots__ = (
        "config",
        "diagnostic_factory",
        "feature",
        "file_path",
        "project",
        "rule_params",
        "severity",
        "step_definitions",
    )

    def __init__(
        self,
        *,
        config: Config,
        severity: Severity,
        rule_params: dict[str, Any] | None = None,
        feature: FeatureLike | None = None,
        project: ProjectLike | None = None,
        file_path: str | None = None,
        step_definitions: list[Any] | None = None,
        diagnostic_factory: DiagnosticFactory | None = None,
    ) -> None:
        """Initialize the rule context.

        Args:
            config: The resolved configuration object.
            severity: The effective severity (after overrides).
            rule_params: This rule's parameters.
            feature: The feature being analyzed (single-file rules).
            project: The full project model (cross-file rules).
            file_path: Path to the current file.
            step_definitions: Parsed step definitions (if configured).
            diagnostic_factory: Helper for creating diagnostics.
        """
        self.config = config
        self.severity = severity
        self.rule_params = rule_params or {}
        self.feature = feature
        self.project = project
        self.file_path = file_path
        self.step_definitions = step_definitions
        self.diagnostic_factory = diagnostic_factory or DiagnosticFactory(
            rule_id="",
            category=Category.CORRECTNESS,
            severity=severity,
            file_path=file_path,
        )


__all__ = ["FeatureLike", "ProjectLike", "RuleContext"]
