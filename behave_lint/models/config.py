"""Configuration data model — resolved configuration for a lint run.

Config is an immutable frozen dataclass created by the configuration
loader. It is passed to the Linter at construction time and never
mutated during a run.

See API.md Section 4 and CONFIGURATION_SYSTEM.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from behave_lint.models.enums import Severity


@dataclass(frozen=True, slots=True)
class Config:
    """Resolved configuration for a lint run.

    Attributes:
        select: Rule IDs to enable (empty = all defaults).
        ignore: Rule IDs to disable.
        severity_overrides: Per-rule severity overrides.
        output: Output format(s), comma-separated.
        output_file: Output file path (None = stdout).
        paths: Default paths to lint.
        exclude: Paths to exclude from linting.
        step_definitions: Step definitions directory, or None.
        cache: Whether to enable caching.
        cache_dir: Cache directory path.
        plugins: Plugin enable/disable map.
        rule_params: Per-rule parameters.
        fail_on: Minimum severity that causes non-zero exit.
        max_warnings: Max warnings before exit code is non-zero (-1 = no limit).
    """

    select: list[str] = field(default_factory=list)
    ignore: list[str] = field(default_factory=list)
    severity_overrides: dict[str, Severity] = field(default_factory=dict)
    output: str = "console"
    output_file: str | None = None
    paths: list[str] = field(default_factory=lambda: ["features/"])
    exclude: list[str] = field(default_factory=list)
    step_definitions: str | None = None
    cache: bool = True
    cache_dir: str = ".behave-lint-cache"
    plugins: dict[str, bool] = field(default_factory=dict)
    rule_params: dict[str, dict[str, object]] = field(default_factory=dict)
    fail_on: Severity = Severity.WARNING
    max_warnings: int = -1

    def is_rule_enabled(self, rule_id: str) -> bool:
        """Check if a rule is enabled given select/ignore lists.

        Args:
            rule_id: The rule ID to check.

        Returns:
            True if the rule is enabled, False if explicitly ignored.
            If select is non-empty, only selected rules are enabled.
        """
        if rule_id in self.ignore:
            return False
        if self.select:
            return rule_id in self.select
        return True

    def get_severity(self, rule_id: str, default: Severity) -> Severity:
        """Get the effective severity for a rule.

        Args:
            rule_id: The rule ID.
            default: Default severity if no override exists.

        Returns:
            The severity from overrides, or the default.
        """
        return self.severity_overrides.get(rule_id, default)


__all__ = ["Config"]
