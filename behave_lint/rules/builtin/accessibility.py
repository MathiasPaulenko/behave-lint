"""Accessibility rules - BACC001-BACC499.

Rules that detect accessibility and inclusive design concerns in
Gherkin feature files, such as ableist language or missing
accessibility-related test coverage.

Default severity: WARNING.
"""

from __future__ import annotations

import re
from typing import Any, ClassVar

from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import AutoFixCapability, Category, Severity
from behave_lint.models.rule_metadata import RuleExample, RuleMetadata
from behave_lint.rules.base import Rule

_ABLEIST_TERMS = re.compile(
    r"\b(disabled|handicapped|crippled|mute|deaf-mute|"
    r"wheelchair-bound|confined to a wheelchair|"
    r"suffering from|afflicted with|victim of|"
    r"normal person|able-bodied)\b",
    re.IGNORECASE,
)

_INCLUSIVE_ALTERNATIVES = {
    "disabled": "person with a disability",
    "handicapped": "person with a disability",
    "crippled": "person with a mobility impairment",
    "mute": "person with a speech impairment",
    "deaf-mute": "person who is deaf and non-speaking",
    "wheelchair-bound": "wheelchair user",
    "confined to a wheelchair": "wheelchair user",
    "suffering from": "living with",
    "afflicted with": "living with",
    "victim of": "person affected by",
    "normal person": "person without disabilities",
    "able-bodied": "person without disabilities",
}


class AbleistLanguageRule(Rule):
    """BACC001: Detect ableist language in step text and scenario names.

    Steps or scenario names that contain ableist terms (e.g.,
    "disabled person", "wheelchair-bound") should be replaced with
    inclusive language (e.g., "person with a disability",
    "wheelchair user").
    """

    metadata = RuleMetadata(
        rule_id="BACC001",
        name="ableist-language",
        title="Ableist language in steps and scenarios",
        description=(
            "Detects ableist terms in step text and scenario names. "
            "Ableist language reinforces stereotypes and should be "
            "replaced with person-first or identity-first language."
        ),
        category=Category.ACCESSIBILITY,
        default_severity=Severity.WARNING,
        motivation=(
            "Inclusive language in tests promotes accessibility "
            "awareness and avoids reinforcing harmful stereotypes "
            "about people with disabilities."
        ),
        since="2.4.0",
        examples=[
            RuleExample(
                before=(
                    "Feature: User management\n\n"
                    "  Scenario: Register disabled user\n"
                    "    Given a disabled user\n"
                    "    When they register\n"
                ),
                after=(
                    "Feature: User management\n\n"
                    "  Scenario: Register user with a disability\n"
                    "    Given a user with a disability\n"
                    "    When they register\n"
                ),
                description="Replace 'disabled' with 'person with a disability'.",
            ),
        ],
        tags=["accessibility", "inclusive-language", "ableism"],
        auto_fix=AutoFixCapability.NONE,
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            scenario_name = getattr(scenario, "name", "") or ""
            match = _ABLEIST_TERMS.search(scenario_name)
            if match:
                term = match.group(0).lower()
                alternative = _INCLUSIVE_ALTERNATIVES.get(term, "inclusive language")
                diagnostics.append(
                    self.diagnostic(
                        message=(
                            f"Scenario name contains ableist term "
                            f"'{term}': '{scenario_name}'"
                        ),
                        node=scenario,
                        suggestion=f"Use '{alternative}' instead.",
                    )
                )

            steps = getattr(scenario, "steps", [])
            for step in steps:
                text = getattr(step, "name", "")
                match = _ABLEIST_TERMS.search(text)
                if match:
                    term = match.group(0).lower()
                    alternative = _INCLUSIVE_ALTERNATIVES.get(
                        term, "inclusive language"
                    )
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Step contains ableist term '{term}': "
                                f"'{text.strip()}'"
                            ),
                            node=step,
                            suggestion=f"Use '{alternative}' instead.",
                        )
                    )

        return diagnostics


class MissingAccessibilityScenarioRule(Rule):
    """BACC002: Detect features with UI scenarios but no accessibility tests.

    Features that contain UI-related tags (e.g., @ui, @frontend, @web)
    should include at least one scenario with an @accessibility tag
    to ensure accessibility testing coverage.
    """

    metadata = RuleMetadata(
        rule_id="BACC002",
        name="missing-accessibility-scenario",
        title="UI features should include accessibility test scenarios",
        description=(
            "Detects features with UI-related tags (@ui, @frontend, "
            "@web) that lack accessibility test scenarios (tagged "
            "@accessibility or @a11y). Accessibility testing should "
            "be part of UI feature coverage."
        ),
        category=Category.ACCESSIBILITY,
        default_severity=Severity.WARNING,
        motivation=(
            "Accessibility testing is essential for inclusive "
            "software. Features that test UI behavior should also "
            "verify accessibility compliance."
        ),
        since="2.4.0",
        examples=[
            RuleExample(
                before=(
                    "@ui\n"
                    "Feature: Login form\n\n"
                    "  Scenario: Successful login\n"
                    "    Given the user is on the login page\n"
                ),
                after=(
                    "@ui\n"
                    "Feature: Login form\n\n"
                    "  Scenario: Successful login\n"
                    "    Given the user is on the login page\n\n"
                    "  @accessibility\n"
                    "  Scenario: Login form is keyboard accessible\n"
                    "    Given the user is on the login page\n"
                    "    Then the form can be completed with the keyboard\n"
                ),
                description="Add an accessibility scenario to the feature.",
            ),
        ],
        tags=["accessibility", "coverage", "ui"],
        auto_fix=AutoFixCapability.NONE,
    )

    _UI_TAGS: ClassVar[frozenset[str]] = frozenset(
        {"ui", "frontend", "web", "e2e"}
    )
    _A11Y_TAGS: ClassVar[frozenset[str]] = frozenset(
        {"accessibility", "a11y"}
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        feature_tags = {
            getattr(t, "name", str(t)).lstrip("@").lower()
            for t in getattr(feature, "tags", [])
        }
        all_tags = set(feature_tags)

        scenarios = list(feature.all_scenarios())
        for scenario in scenarios:
            scenario_tags = {
                getattr(t, "name", str(t)).lstrip("@").lower()
                for t in getattr(scenario, "tags", [])
            }
            all_tags |= scenario_tags

        has_ui_tag = bool(all_tags & self._UI_TAGS)
        has_a11y_tag = bool(all_tags & self._A11Y_TAGS)

        if has_ui_tag and not has_a11y_tag:
            diagnostics.append(
                self.diagnostic(
                    message=(
                        f"Feature '{feature.name}' has UI tags but no "
                        f"accessibility test scenarios"
                    ),
                    node=feature,
                    suggestion=(
                        "Add a scenario tagged @accessibility to "
                        "verify keyboard navigation, screen reader "
                        "compatibility, or other accessibility aspects."
                    ),
                )
            )

        return diagnostics


class ColorOnlyContrastRule(Rule):
    """BACC003: Detect steps that rely solely on color for information.

    Steps that reference color alone to convey information (e.g.,
    "the button is red") are inaccessible to users with color
    blindness. Tests should verify that information is also conveyed
    through text, icons, or other non-color cues.
    """

    metadata = RuleMetadata(
        rule_id="BACC003",
        name="color-only-contrast",
        title="Steps should not rely solely on color for information",
        description=(
            "Detects steps that reference color alone to convey "
            "information (e.g., 'the button is red'). Relying solely "
            "on color is inaccessible to users with color blindness."
        ),
        category=Category.ACCESSIBILITY,
        default_severity=Severity.WARNING,
        motivation=(
            "Approximately 8% of men and 0.5% of women have some "
            "form of color vision deficiency. Tests should verify "
            "that information is conveyed through multiple channels, "
            "not color alone."
        ),
        since="2.4.0",
        examples=[
            RuleExample(
                before=(
                    "Feature: Status display\n\n"
                    '  Scenario: Error state\n'
                    '    Then the button is red\n'
                ),
                after=(
                    "Feature: Status display\n\n"
                    '  Scenario: Error state\n'
                    '    Then the button is red and shows "Error"\n'
                ),
                description="Add a text indicator in addition to color.",
            ),
        ],
        tags=["accessibility", "color", "contrast"],
        auto_fix=AutoFixCapability.NONE,
    )

    _COLOR_PATTERN = re.compile(
        r"\b(?:red|green|blue|yellow|orange|purple|pink|"
        r"black|white|gray|grey|brown)\b",
        re.IGNORECASE,
    )
    _NON_COLOR_INDICATORS = re.compile(
        r"(?:text|label|icon|symbol|message|error|warning|"
        r"success|border|underline|pattern|shape)",
        re.IGNORECASE,
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            for step in steps:
                text = getattr(step, "name", "")
                has_color = bool(self._COLOR_PATTERN.search(text))
                has_non_color = bool(self._NON_COLOR_INDICATORS.search(text))
                if has_color and not has_non_color:
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Step relies solely on color to convey "
                                f"information: '{text.strip()}'"
                            ),
                            node=step,
                            suggestion=(
                                "Add a text, icon, or pattern indicator "
                                "in addition to color."
                            ),
                        )
                    )

        return diagnostics


__all__ = [
    "AbleistLanguageRule",
    "ColorOnlyContrastRule",
    "MissingAccessibilityScenarioRule",
]
