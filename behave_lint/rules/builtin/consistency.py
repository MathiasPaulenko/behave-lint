"""Consistency rules - BK001-BK499.

Rules that detect inconsistencies across features and scenarios.
Default severity: WARNING. Some rules are cross-file scope.

See RULE_TAXONOMY.md Section 3 and IMPLEMENTATION_ROADMAP.md E7.4.
"""

from __future__ import annotations

from typing import Any

from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.rule_metadata import RuleExample, RuleMetadata
from behave_lint.rules.base import Rule


class InconsistentStepTextRule(Rule):
    """BK001: Detect inconsistent step text for the same concept.

    Steps that perform the same action should use the same text.
    For example, 'Given a logged in user' and 'Given the user is
    logged in' are inconsistent phrasings of the same concept.
    """

    metadata = RuleMetadata(
        rule_id="BK001",
        name="inconsistent-step-text",
        title="Step text is inconsistent across scenarios",
        description=(
            "Detects steps that use different text for the same "
            "action. Consistent step text improves readability and "
            "enables better step definition reuse."
        ),
        category=Category.CONSISTENCY,
        default_severity=Severity.WARNING,
        motivation=(
            "When the same action is described with different words, "
            "it becomes hard to reuse step definitions and maintain "
            "consistency across the test suite."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "  # Scenario 1\n"
                    "    Given a logged in user\n\n"
                    "  # Scenario 2\n"
                    "    Given the user is logged in\n"
                ),
                after=(
                    "  # Scenario 1\n"
                    "    Given the user is logged in\n\n"
                    "  # Scenario 2\n"
                    "    Given the user is logged in\n"
                ),
                description="Use the same text for the same action.",
            ),
        ],
        tags=["steps", "consistency", "naming"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        step_texts: dict[str, list[Any]] = {}
        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            for step in steps:
                text = getattr(step, "name", "").strip().lower()
                if not text:
                    continue
                if text not in step_texts:
                    step_texts[text] = []
                step_texts[text].append(step)

        seen_variations: dict[str, set[str]] = {}
        normalized_map: dict[str, str] = {}
        for text in step_texts:
            normalized = " ".join(text.split())
            if normalized not in normalized_map:
                normalized_map[normalized] = text
                seen_variations[normalized] = set()
            seen_variations[normalized].add(text)

        for normalized, variations in seen_variations.items():
            if len(variations) > 1:
                canonical = normalized_map[normalized]
                for variation in variations:
                    if variation == canonical:
                        continue
                    for step in step_texts[variation]:
                        diagnostics.append(
                            self.diagnostic(
                                message=(
                                    f"Step text '{step.name}' is "
                                    f"inconsistent with "
                                    f"'{step_texts[canonical][0].name}'"
                                ),
                                node=step,
                                suggestion=(
                                    f"Use '{step_texts[canonical][0].name}' "
                                    "for consistency."
                                ),
                            )
                        )

        return diagnostics


class InconsistentTagUsageRule(Rule):
    """BK002: Detect inconsistent tag usage across scenarios.

    Tags should be applied consistently. If a tag like @smoke is
    used on some scenarios but not on similar ones, it may indicate
    missing or incorrect tagging.
    """

    metadata = RuleMetadata(
        rule_id="BK002",
        name="inconsistent-tag-usage",
        title="Tag usage is inconsistent across scenarios",
        description=(
            "Detects scenarios that may be missing tags that similar "
            "scenarios have. This is a heuristic rule based on "
            "scenario name similarity."
        ),
        category=Category.CONSISTENCY,
        default_severity=Severity.INFO,
        motivation=(
            "Inconsistent tagging can lead to incomplete test "
            "selection when filtering by tags. Similar scenarios "
            "should share relevant tags."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "  @smoke\n"
                    "  Scenario: User can log in\n"
                    "    Given a user\n\n"
                    "  Scenario: User can log out\n"
                    "    Given a user\n"
                ),
                after=(
                    "  @smoke\n"
                    "  Scenario: User can log in\n"
                    "    Given a user\n\n"
                    "  @smoke\n"
                    "  Scenario: User can log out\n"
                    "    Given a user\n"
                ),
                description="Apply the @smoke tag consistently.",
            ),
        ],
        tags=["tags", "consistency"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        all_tags: set[str] = set()
        for scenario in feature.all_scenarios():
            tags = getattr(scenario, "tags", [])
            for tag in tags:
                all_tags.add(getattr(tag, "name", str(tag)))

        if not all_tags:
            return []

        for scenario in feature.all_scenarios():
            scenario_tags = getattr(scenario, "tags", [])
            tag_names = {getattr(t, "name", str(t)) for t in scenario_tags}
            if not tag_names:
                diagnostics.append(
                    self.diagnostic(
                        message=(
                            f"Scenario '{scenario.name}' has no tags "
                            "while other scenarios in this feature do"
                        ),
                        node=scenario,
                        suggestion=(
                            "Consider adding relevant tags to this "
                            "scenario for consistency."
                        ),
                        severity=Severity.INFO,
                    )
                )

        return diagnostics


class InconsistentNamingConventionRule(Rule):
    """BK003: Detect inconsistent scenario naming conventions.

    Scenario names should follow a consistent convention. Mixing
    'Given a user logs in' with 'User logs in' is inconsistent.
    """

    metadata = RuleMetadata(
        rule_id="BK003",
        name="inconsistent-naming-convention",
        title="Scenario naming convention is inconsistent",
        description=(
            "Detects features where scenario names follow different "
            "conventions (e.g., some start with 'Given' and others "
            "don't). Consistent naming improves readability."
        ),
        category=Category.CONSISTENCY,
        default_severity=Severity.WARNING,
        motivation=(
            "When scenario names follow different patterns, it "
            "becomes harder to scan and understand the test suite. "
            "Pick one convention and stick to it."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "  Scenario: Given a user is logged in\n"
                    "    ...\n\n"
                    "  Scenario: User logs out\n"
                    "    ...\n"
                ),
                after=(
                    "  Scenario: User is logged in\n"
                    "    ...\n\n"
                    "  Scenario: User logs out\n"
                    "    ...\n"
                ),
                description="Use consistent naming without 'Given'.",
            ),
        ],
        tags=["naming", "consistency", "scenarios"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        scenarios = list(feature.all_scenarios())
        if len(scenarios) < 2:
            return []

        starts_with_given = [
            s for s in scenarios if (s.name or "").strip().lower().startswith("given ")
        ]
        does_not = [
            s
            for s in scenarios
            if not (s.name or "").strip().lower().startswith("given ")
        ]

        if starts_with_given and does_not:
            (starts_with_given if len(starts_with_given) > len(does_not) else does_not)
            minority = (
                does_not
                if len(starts_with_given) > len(does_not)
                else starts_with_given
            )

            for scenario in minority:
                diagnostics.append(
                    self.diagnostic(
                        message=(
                            f"Scenario '{scenario.name}' follows a "
                            "different naming convention than the "
                            "majority of scenarios in this feature"
                        ),
                        node=scenario,
                        suggestion=(
                            "Use a consistent naming convention across all scenarios."
                        ),
                    )
                )

        return diagnostics


class InconsistentScenarioLengthRule(Rule):
    """BK004: Detect scenarios with very different step counts.

    Scenarios within the same feature should have roughly similar
    complexity. A scenario with 2 steps alongside one with 15 steps
    indicates inconsistent test granularity.
    """

    metadata = RuleMetadata(
        rule_id="BK004",
        name="inconsistent-scenario-length",
        title="Scenarios have very different step counts",
        description=(
            "Detects features where scenarios have very different "
            "numbers of steps. Large disparities indicate inconsistent "
            "test granularity."
        ),
        category=Category.CONSISTENCY,
        default_severity=Severity.INFO,
        motivation=(
            "When scenarios in the same feature vary wildly in "
            "complexity, it's hard to understand the feature's "
            "scope. Aim for consistent test granularity."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "  Scenario: Quick check\n"
                    "    Given a step\n"
                    "    Then a result\n\n"
                    "  Scenario: Full test\n"
                    "    Given step 1\n"
                    "    And step 2\n"
                    "    ... (10 more steps)\n"
                ),
                after=(
                    "  # Split into a separate feature or\n"
                    "  # balance the step counts\n"
                ),
                description="Balance scenario complexity within a feature.",
            ),
        ],
        tags=["scenarios", "consistency", "complexity"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        scenarios = list(feature.all_scenarios())
        if len(scenarios) < 2:
            return []

        step_counts = [len(getattr(s, "steps", [])) for s in scenarios]
        max_count = max(step_counts)
        min_count = min(step_counts)

        if max_count - min_count >= 8:
            for scenario, count in zip(scenarios, step_counts, strict=False):
                if count == max_count:
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Scenario '{scenario.name}' has {count} "
                                f"steps while the shortest scenario in "
                                f"this feature has {min_count} steps"
                            ),
                            node=scenario,
                            suggestion=(
                                "Balance scenario complexity by "
                                "splitting or merging scenarios."
                            ),
                            severity=Severity.INFO,
                        )
                    )

        return diagnostics


class DuplicateStepTextRule(Rule):
    """BK005: Detect duplicate steps within a scenario.

    Having the same step text repeated within a scenario is usually
    a mistake or indicates a missing 'And' continuation.
    """

    metadata = RuleMetadata(
        rule_id="BK005",
        name="duplicate-step-text",
        title="Duplicate step text within a scenario",
        description=(
            "Detects scenarios that contain the same step text "
            "multiple times. This is usually a mistake or indicates "
            "a missing 'And' continuation."
        ),
        category=Category.CONSISTENCY,
        default_severity=Severity.WARNING,
        motivation=(
            "Duplicate steps within a scenario are confusing and "
            "may indicate a copy-paste error or a missing 'And' "
            "continuation."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "  Scenario: Test\n"
                    "    Given a user\n"
                    "    Given a user\n"
                    "    When I do something\n"
                ),
                after=("  Scenario: Test\n    Given a user\n    When I do something\n"),
                description="Remove the duplicate step.",
            ),
        ],
        tags=["steps", "duplicates", "consistency"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            seen: set[str] = set()
            for step in steps:
                text = getattr(step, "name", "").strip().lower()
                if not text:
                    continue
                if text in seen:
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Duplicate step '{step.name}' in "
                                f"scenario '{scenario.name}'"
                            ),
                            node=step,
                            suggestion=(
                                "Remove the duplicate step or use "
                                "'And' for continuation."
                            ),
                        )
                    )
                else:
                    seen.add(text)

        return diagnostics


__all__ = [
    "DuplicateStepTextRule",
    "InconsistentNamingConventionRule",
    "InconsistentScenarioLengthRule",
    "InconsistentStepTextRule",
    "InconsistentTagUsageRule",
]
