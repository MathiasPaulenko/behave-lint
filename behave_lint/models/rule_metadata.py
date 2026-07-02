"""Rule metadata models — RuleMetadata and RuleExample.

RuleMetadata is the identity card of a rule. It drives configuration
validation, documentation generation, CLI features, and plugin
compatibility checking.

See API.md Section 4, RULE_ENGINE.md Section 4, and RULE_TAXONOMY.md
Section 5.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from behave_lint.models.enums import (
    AutoFixCapability,
    Category,
    EducationalValue,
    FixCost,
    PerformanceImpact,
    Severity,
)


@dataclass(frozen=True, slots=True)
class RuleExample:
    """A before/after example for a rule.

    Attributes:
        before: Gherkin code that triggers the rule.
        after: Gherkin code after the fix, or "No fix available".
        description: Explanation of the example.
    """

    before: str
    after: str
    description: str


@dataclass(frozen=True, slots=True)
class RuleMetadata:
    """Identity and documentation for a rule.

    Attributes:
        rule_id: Stable, unique identifier (e.g., "BC001").
        name: Short, human-readable, kebab-case name.
        title: One-line summary for CLI and documentation.
        description: One-paragraph description of what the rule checks.
        category: Rule category.
        default_severity: Default severity when the rule is enabled.
        motivation: Why the rule exists — the problem it solves.
        since: Version when the rule was introduced.
        examples: Before/after examples for documentation.
        auto_fix: Auto-fix capability. Defaults to NONE.
        tags: Free-form tags for filtering and grouping.
        references: External references (URLs, book sections, standards).
        configurable: Whether the rule accepts parameters.
        experimental: Whether the rule is experimental.
        deprecated: Whether the rule is deprecated.
        deprecated_version: Version in which the rule was deprecated.
        replaced_by: Rule ID that replaces this one, or None.
        aliases: Alternative names for backward compatibility.
        dependencies: Rule IDs that must execute before this rule.
        conflicts: Rule IDs that conflict with this rule.
        doc_url: URL to rule documentation, or None.
        author: Author or maintainer of the rule, or None.
        min_version: Minimum behave-lint version required, or None.
        estimated_fix_cost: Estimated effort to fix.
        performance_impact: Execution cost.
        educational_value: Pedagogical value.
    """

    rule_id: str
    name: str
    title: str
    description: str
    category: Category
    default_severity: Severity
    motivation: str
    since: str
    examples: list[RuleExample] = field(default_factory=list)
    auto_fix: AutoFixCapability = AutoFixCapability.NONE
    tags: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    configurable: bool = False
    experimental: bool = False
    deprecated: bool = False
    deprecated_version: str | None = None
    replaced_by: str | None = None
    aliases: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    doc_url: str | None = None
    author: str | None = None
    min_version: str | None = None
    estimated_fix_cost: FixCost = FixCost.LOW
    performance_impact: PerformanceImpact = PerformanceImpact.NEGLIGIBLE
    educational_value: EducationalValue = EducationalValue.NONE

    def __post_init__(self) -> None:
        """Validate field constraints after initialization."""
        if not self.rule_id:
            raise ValueError("rule_id must be a non-empty string")
        if not self.name:
            raise ValueError("name must be a non-empty string")
        if not self.description:
            raise ValueError("description must be a non-empty string")
        if not self.motivation:
            raise ValueError("motivation must be a non-empty string")
        if not self.since:
            raise ValueError("since must be a non-empty string")
        if self.deprecated and not self.replaced_by and not self.deprecated_version:
            import warnings

            warnings.warn(
                f"Rule {self.rule_id} is deprecated but has no "
                "replaced_by or deprecated_version.",
                stacklevel=2,
            )


__all__ = ["RuleExample", "RuleMetadata"]
