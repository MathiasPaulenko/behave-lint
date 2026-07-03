"""Pedantic rules - BP001-BP499.

Opt-in rules for very strict conventions.
Default severity: INFO.

See RULE_TAXONOMY.md Section 3 and IMPLEMENTATION_ROADMAP.md E7.5.
"""

from __future__ import annotations

from typing import Any, ClassVar

from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.rule_metadata import RuleExample, RuleMetadata
from behave_lint.rules.base import Rule

_DEFAULT_MIN_NAME_LENGTH = 5
_DEFAULT_MIN_FEATURE_NAME_LENGTH = 5


class MissingScenarioTagsRule(Rule):
    """BP001: Detect scenarios without any tags.

    Every scenario should have at least one tag for filtering and
    categorization. This is a pedantic rule, opt-in only.
    """

    metadata = RuleMetadata(
        rule_id="BP001",
        name="missing-scenario-tags",
        title="Scenario should have at least one tag",
        description=(
            "Detects scenarios that do not have any tags. Tags "
            "help filter and categorize scenarios for targeted "
            "test execution."
        ),
        category=Category.PEDANTIC,
        default_severity=Severity.INFO,
        motivation=(
            "Tags enable selective test execution (e.g., running "
            "only @smoke tests). Scenarios without tags cannot be "
            "filtered, reducing test suite flexibility."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=("  Scenario: Test\n    Given a step\n"),
                after=("  @smoke\n  Scenario: Test\n    Given a step\n"),
                description="Add at least one tag to the scenario.",
            ),
        ],
        tags=["tags", "scenarios", "pedantic"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            tags = getattr(scenario, "tags", [])
            if not tags:
                diagnostics.append(
                    self.diagnostic(
                        message=(f"Scenario '{scenario.name}' has no tags"),
                        node=scenario,
                        suggestion=(
                            "Add at least one tag (e.g., @smoke, "
                            "@regression) for filtering."
                        ),
                        severity=Severity.INFO,
                    )
                )

        return diagnostics


class MissingBackgroundRule(Rule):
    """BP002: Detect features without a Background section.

    Features without a Background may have duplicated setup steps
    across scenarios. This is a pedantic rule.
    """

    metadata = RuleMetadata(
        rule_id="BP002",
        name="missing-background",
        title="Feature should have a Background section",
        description=(
            "Detects features that lack a Background section. "
            "Common setup steps should be extracted into a "
            "Background to avoid duplication."
        ),
        category=Category.PEDANTIC,
        default_severity=Severity.INFO,
        motivation=(
            "When multiple scenarios share the same Given steps, "
            "a Background reduces duplication and improves "
            "maintainability."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "  Scenario: A\n"
                    "    Given a user\n"
                    "    When I do X\n\n"
                    "  Scenario: B\n"
                    "    Given a user\n"
                    "    When I do Y\n"
                ),
                after=(
                    "  Background: Common setup\n"
                    "    Given a user\n\n"
                    "  Scenario: A\n"
                    "    When I do X\n\n"
                    "  Scenario: B\n"
                    "    When I do Y\n"
                ),
                description="Extract common steps into a Background.",
            ),
        ],
        tags=["background", "pedantic"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        background = getattr(feature, "background", None)
        if background is None:
            location = getattr(feature, "location", None)
            file_path = getattr(location, "filename", "") if location else ""
            return [
                self.diagnostic(
                    message=(f"Feature '{feature.name}' has no Background section"),
                    node=feature,
                    file_path=file_path or None,
                    suggestion=(
                        "Extract common setup steps into a Background section."
                    ),
                    severity=Severity.INFO,
                )
            ]
        return []


class ShortScenarioNameRule(Rule):
    """BP003: Detect scenarios with very short names.

    Scenario names should be descriptive. Names shorter than 5
    characters are likely too vague. This is a pedantic rule.
    """

    metadata = RuleMetadata(
        rule_id="BP003",
        name="short-scenario-name",
        title="Scenario name is too short",
        description=(
            "Detects scenarios with names shorter than the "
            "minimum length. Short names are often vague and "
            "uninformative."
        ),
        category=Category.PEDANTIC,
        default_severity=Severity.INFO,
        motivation=(
            "A scenario name like 'Test' or 'S1' doesn't convey "
            "what the scenario tests. Descriptive names improve "
            "readability and test report clarity."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=("  Scenario: S1\n    Given a step\n"),
                after=(
                    "  Scenario: User can log in with valid credentials\n"
                    "    Given a step\n"
                ),
                description="Use a descriptive scenario name.",
            ),
        ],
        tags=["naming", "scenarios", "pedantic"],
        configurable=True,
    )

    default_params: ClassVar[dict[str, Any]] = {
        "min_name_length": _DEFAULT_MIN_NAME_LENGTH
    }

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        min_length = _DEFAULT_MIN_NAME_LENGTH

        rule_config = getattr(config, "rules", {}).get("BP003", {})
        if isinstance(rule_config, dict):
            min_length = rule_config.get("min_name_length", min_length)

        for scenario in feature.all_scenarios():
            name = (getattr(scenario, "name", "") or "").strip()
            if len(name) < min_length:
                diagnostics.append(
                    self.diagnostic(
                        message=(
                            f"Scenario name '{name}' is too short "
                            f"(min: {min_length} characters)"
                        ),
                        node=scenario,
                        suggestion=(
                            "Use a more descriptive name that "
                            "explains what the scenario tests."
                        ),
                        severity=Severity.INFO,
                    )
                )

        return diagnostics


class ShortFeatureNameRule(Rule):
    """BP004: Detect features with very short names.

    Feature names should be descriptive. Names shorter than 5
    characters are likely too vague. This is a pedantic rule.
    """

    metadata = RuleMetadata(
        rule_id="BP004",
        name="short-feature-name",
        title="Feature name is too short",
        description=(
            "Detects features with names shorter than the "
            "minimum length. Short names are often vague and "
            "uninformative."
        ),
        category=Category.PEDANTIC,
        default_severity=Severity.INFO,
        motivation=(
            "A feature name like 'App' doesn't convey what the "
            "feature covers. Descriptive names improve navigation "
            "and understanding."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=("Feature: App\n  Scenario: Test\n    Given a step\n"),
                after=(
                    "Feature: User Authentication\n  Scenario: Test\n    Given a step\n"
                ),
                description="Use a descriptive feature name.",
            ),
        ],
        tags=["naming", "feature", "pedantic"],
        configurable=True,
    )

    default_params: ClassVar[dict[str, Any]] = {
        "min_feature_name_length": _DEFAULT_MIN_FEATURE_NAME_LENGTH
    }

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        min_length = _DEFAULT_MIN_FEATURE_NAME_LENGTH

        rule_config = getattr(config, "rules", {}).get("BP004", {})
        if isinstance(rule_config, dict):
            min_length = rule_config.get("min_feature_name_length", min_length)

        name = (getattr(feature, "name", "") or "").strip()
        if len(name) < min_length:
            location = getattr(feature, "location", None)
            file_path = getattr(location, "filename", "") if location else ""
            return [
                self.diagnostic(
                    message=(
                        f"Feature name '{name}' is too short "
                        f"(min: {min_length} characters)"
                    ),
                    node=feature,
                    file_path=file_path or None,
                    suggestion=(
                        "Use a more descriptive name that "
                        "explains what the feature covers."
                    ),
                    severity=Severity.INFO,
                )
            ]
        return []


class MissingExamplesNameRule(Rule):
    """BP005: Detect Examples sections without a name.

    Named Examples sections improve readability by grouping
    related data. Unnamed Examples are harder to understand.
    """

    metadata = RuleMetadata(
        rule_id="BP005",
        name="missing-examples-name",
        title="Examples section should have a name",
        description=(
            "Detects Examples sections that lack a descriptive "
            "name. Named examples improve readability by "
            "grouping related data."
        ),
        category=Category.PEDANTIC,
        default_severity=Severity.INFO,
        motivation=(
            "An unnamed Examples block is just a table. A name "
            "like 'Examples: Valid inputs' communicates the "
            "purpose of the data."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "  Scenario Outline: Test <v>\n"
                    "    Given a <v>\n\n"
                    "    Examples:\n"
                    "      | v |\n"
                    "      | a |\n"
                ),
                after=(
                    "  Scenario Outline: Test <v>\n"
                    "    Given a <v>\n\n"
                    "    Examples: Valid values\n"
                    "      | v |\n"
                    "      | a |\n"
                ),
                description="Add a descriptive name to the Examples.",
            ),
        ],
        tags=["examples", "naming", "pedantic"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            examples = getattr(scenario, "examples", None)
            if not examples:
                continue

            for example in examples:
                name = (getattr(example, "name", "") or "").strip()
                if not name:
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Examples in scenario '{scenario.name}' has no name"
                            ),
                            node=example,
                            suggestion=(
                                "Add a descriptive name after "
                                "'Examples:' (e.g., 'Valid inputs')."
                            ),
                            severity=Severity.INFO,
                        )
                    )

        return diagnostics


class MissingFeatureDescriptionRule(Rule):
    """BP006: Detect features without a description.

    A feature should have a description block (text between the
    Feature line and the first Scenario/Background) explaining
    the feature's purpose.
    """

    metadata = RuleMetadata(
        rule_id="BP006",
        name="missing-feature-description",
        title="Feature should have a description",
        description=(
            "Detects features that lack a description block. A "
            "description explains the feature's purpose and improves "
            "readability for non-technical stakeholders."
        ),
        category=Category.PEDANTIC,
        default_severity=Severity.INFO,
        motivation=(
            "A feature without a description is just a collection of "
            "scenarios. A description provides context and helps "
            "stakeholders understand the feature's intent."
        ),
        since="1.2.0",
        examples=[
            RuleExample(
                before=(
                    "Feature: User Authentication\n"
                    "  Scenario: Login\n"
                    "    Given a user\n"
                ),
                after=(
                    "Feature: User Authentication\n"
                    "  As a registered user\n"
                    "  I want to log in\n"
                    "  So that I can access my account\n\n"
                    "  Scenario: Login\n"
                    "    Given a user\n"
                ),
                description="Add a description after the Feature line.",
            ),
        ],
        tags=["feature", "description", "pedantic"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        description = getattr(feature, "description", None)
        if not description or not str(description).strip():
            location = getattr(feature, "location", None)
            file_path = getattr(location, "filename", "") if location else ""
            return [
                self.diagnostic(
                    message=(
                        f"Feature '{feature.name}' has no description"
                    ),
                    node=feature,
                    file_path=file_path or None,
                    suggestion=(
                        "Add a description (e.g., 'As a ... I want to "
                        "... So that ...') after the Feature line."
                    ),
                    severity=Severity.INFO,
                )
            ]
        return []


class ScenarioWithoutAssertionRule(Rule):
    """BP007: Detect scenarios without a 'Then' step.

    Every scenario should include at least one assertion (Then step)
    to verify the expected outcome. Scenarios without assertions
    don't actually test anything.
    """

    metadata = RuleMetadata(
        rule_id="BP007",
        name="scenario-without-assertion",
        title="Scenario has no 'Then' step",
        description=(
            "Detects scenarios that do not contain at least one 'Then' "
            "step. Without an assertion, the scenario does not verify "
            "any expected outcome."
        ),
        category=Category.PEDANTIC,
        default_severity=Severity.INFO,
        motivation=(
            "A scenario without a 'Then' step executes actions but "
            "never verifies the result. This gives false confidence "
            "that the test is passing."
        ),
        since="1.2.0",
        examples=[
            RuleExample(
                before=(
                    "  Scenario: Setup only\n"
                    "    Given a user\n"
                    "    When I log in\n"
                ),
                after=(
                    "  Scenario: Login succeeds\n"
                    "    Given a user\n"
                    "    When I log in\n"
                    "    Then I should be on the dashboard\n"
                ),
                description="Add a 'Then' step to verify the outcome.",
            ),
        ],
        tags=["scenarios", "assertion", "pedantic"],
    )

    _ASSERTION_KEYWORDS: ClassVar[frozenset[str]] = frozenset({"then"})

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            has_assertion = False
            for step in steps:
                keyword = getattr(step, "keyword", "").strip().lower()
                if keyword in self._ASSERTION_KEYWORDS:
                    has_assertion = True
                    break

            if not has_assertion and steps:
                diagnostics.append(
                    self.diagnostic(
                        message=(
                            f"Scenario '{scenario.name}' has no 'Then' step"
                        ),
                        node=scenario,
                        suggestion=(
                            "Add a 'Then' step to verify the expected "
                            "outcome of this scenario."
                        ),
                        severity=Severity.INFO,
                    )
                )

        return diagnostics


__all__ = [
    "MissingBackgroundRule",
    "MissingExamplesNameRule",
    "MissingFeatureDescriptionRule",
    "MissingScenarioTagsRule",
    "ScenarioWithoutAssertionRule",
    "ShortFeatureNameRule",
    "ShortScenarioNameRule",
]
