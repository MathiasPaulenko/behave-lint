"""Style rules - BS001-BS499.

Rules that enforce stylistic conventions for readability and consistency.
Default severity: WARNING.

See RULE_TAXONOMY.md Section 3 and IMPLEMENTATION_ROADMAP.md E7.2.
"""

from __future__ import annotations

import re
from typing import Any

from behave_lint.autofix.models import FixEdit
from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import AutoFixCapability, Category, Severity
from behave_lint.models.rule_metadata import RuleExample, RuleMetadata
from behave_lint.rules.base import Rule

_GHERKIN_KEYWORDS = {"given", "when", "then", "and", "but", "*"}
_STEP_KEYWORDS_ORDER = ["given", "when", "then"]

_CAMEL_CASE_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


class TagCasingRule(Rule):
    """BS001: Enforce consistent tag casing (lowercase with underscores).

    Tags should use lowercase letters with underscores (snake_case)
    for consistency. Mixed-case tags like @SmokeTest or @smoke-test
    are flagged.
    """

    metadata = RuleMetadata(
        rule_id="BS001",
        name="tag-casing",
        title="Tags should use lowercase with underscores",
        description=(
            "Detects tags that do not follow the lowercase snake_case "
            "convention (e.g., @smoke_test). Mixed-case or kebab-case "
            "tags are flagged."
        ),
        category=Category.STYLE,
        default_severity=Severity.WARNING,
        motivation=(
            "Consistent tag casing improves readability and prevents "
            "silent mismatches when filtering tests by tag name."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "@SmokeTest\n"
                    "Feature: Test\n\n"
                    "  Scenario: A scenario\n"
                    "    Given a step\n"
                ),
                after=(
                    "@smoke_test\n"
                    "Feature: Test\n\n"
                    "  Scenario: A scenario\n"
                    "    Given a step\n"
                ),
                description="Convert tag to lowercase snake_case.",
            ),
        ],
        tags=["tags", "naming", "convention"],
    )

    def _normalize_tag(self, tag_name: str) -> str:
        """Convert a tag name to lowercase snake_case.

        Args:
            tag_name: Tag name without the leading '@'.

        Returns:
            Normalized tag name.
        """
        return _CAMEL_CASE_PATTERN.sub("_", tag_name).lower().replace("-", "_")

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        all_tags: list[Any] = []

        feature_tags = getattr(feature, "tags", [])
        if feature_tags:
            all_tags.extend(feature_tags)

        for scenario in feature.all_scenarios():
            scenario_tags = getattr(scenario, "tags", [])
            if scenario_tags:
                all_tags.extend(scenario_tags)

        for tag in all_tags:
            tag_name = getattr(tag, "name", str(tag))
            without_at = tag_name[1:] if tag_name.startswith("@") else tag_name
            expected = self._normalize_tag(without_at)
            if without_at != expected:
                diagnostics.append(
                    self.diagnostic(
                        message=(
                            f"Tag '{tag_name}' does not follow "
                            "lowercase snake_case convention"
                        ),
                        node=tag,
                        suggestion=(f"Use '@{expected}' instead."),
                    )
                )

        return diagnostics

    def get_fixes(
        self, feature: Any, config: Config, diagnostics: list[Diagnostic]
    ) -> list[FixEdit]:
        from pathlib import Path

        fixes: list[FixEdit] = []
        file_path = getattr(feature, "file_path", None)
        if not file_path:
            location = getattr(feature, "location", None)
            if location is not None:
                file_path = getattr(location, "filename", None)
        if not file_path:
            return fixes

        try:
            content = Path(file_path).read_text(encoding="utf-8")
            lines = content.splitlines(keepends=True)
        except OSError:
            return fixes

        diag_lines = {d.line for d in diagnostics if d.rule_id == "BS001"}

        all_tags: list[Any] = []
        feature_tags = getattr(feature, "tags", [])
        if feature_tags:
            all_tags.extend(feature_tags)
        for scenario in feature.all_scenarios():
            scenario_tags = getattr(scenario, "tags", [])
            if scenario_tags:
                all_tags.extend(scenario_tags)

        for tag in all_tags:
            tag_name = getattr(tag, "name", str(tag))
            without_at = tag_name[1:] if tag_name.startswith("@") else tag_name
            expected = self._normalize_tag(without_at)
            if without_at == expected:
                continue

            tag_line = getattr(tag, "line", None)
            if tag_line is None:
                loc = getattr(tag, "location", None)
                if loc is not None:
                    tag_line = getattr(loc, "line", None)
            if tag_line is None or tag_line not in diag_lines:
                continue

            idx = tag_line - 1
            if idx < 0 or idx >= len(lines):
                continue

            old_line = lines[idx]
            old_tag = f"@{without_at}"
            new_tag = f"@{expected}"

            if old_tag in old_line:
                new_line = old_line.replace(old_tag, new_tag)
                fixes.append(
                    FixEdit(
                        file_path=file_path,
                        start_line=tag_line,
                        end_line=tag_line,
                        old_text=old_line,
                        new_text=new_line,
                        safety=AutoFixCapability.SAFE,
                        rule_id="BS001",
                        diagnostic_line=tag_line,
                    )
                )

        return fixes


class KeywordOrderingRule(Rule):
    """BS002: Enforce Given-When-Then keyword ordering in scenarios.

    Steps within a scenario should follow the Given-When-Then order.
    A Given after a When, or a Then before a When, indicates a
    disorganized test arrangement.
    """

    metadata = RuleMetadata(
        rule_id="BS002",
        name="keyword-ordering",
        title="Steps should follow Given-When-Then order",
        description=(
            "Detects scenarios where steps do not follow the "
            "Given-When-Then ordering convention. Steps using 'And' "
            "or 'But' inherit the preceding keyword's position."
        ),
        category=Category.STYLE,
        default_severity=Severity.WARNING,
        motivation=(
            "Given-When-Then ordering makes test intent clear: "
            "setup (Given), action (When), assertion (Then). "
            "Out-of-order steps obscure the test structure."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "  Scenario: Test\n"
                    "    Then I should see result\n"
                    "    When I do something\n"
                    "    Given a precondition\n"
                ),
                after=(
                    "  Scenario: Test\n"
                    "    Given a precondition\n"
                    "    When I do something\n"
                    "    Then I should see result\n"
                ),
                description="Reorder steps to Given-When-Then.",
            ),
        ],
        tags=["steps", "keywords", "ordering"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            if not steps:
                continue

            last_major_keyword: str | None = None
            for step in steps:
                keyword = getattr(step, "keyword", "").strip().lower()
                if keyword in ("and", "but", "*"):
                    continue
                if keyword in _STEP_KEYWORDS_ORDER:
                    if last_major_keyword is not None:
                        current_idx = _STEP_KEYWORDS_ORDER.index(keyword)
                        last_idx = _STEP_KEYWORDS_ORDER.index(last_major_keyword)
                        if current_idx < last_idx:
                            diagnostics.append(
                                self.diagnostic(
                                    message=(
                                        f"Step keyword '{keyword.title()}' "
                                        f"appears after "
                                        f"'{last_major_keyword.title()}' "
                                        "in scenario "
                                        f"'{scenario.name}'"
                                    ),
                                    node=step,
                                    suggestion=(
                                        "Reorder steps to follow "
                                        "Given-When-Then convention."
                                    ),
                                )
                            )
                    last_major_keyword = keyword

        return diagnostics


class StepPhrasingRule(Rule):
    """BS003: Detect steps that start with 'I' instead of third-person.

    Steps should use third-person phrasing (e.g., 'the user clicks')
    rather than first-person ('I click'). Third-person phrasing is
    more readable and reusable across scenarios.
    """

    metadata = RuleMetadata(
        rule_id="BS003",
        name="step-phrasing",
        title="Steps should use third-person phrasing",
        description=(
            "Detects steps that start with 'I ' (first-person phrasing). "
            "Third-person phrasing (e.g., 'the user clicks') is "
            "preferred for readability and reusability."
        ),
        category=Category.STYLE,
        default_severity=Severity.WARNING,
        motivation=(
            "First-person steps ('I click') are less descriptive than "
            "third-person ('the user clicks'). Third-person phrasing "
            "makes the actor explicit and improves readability."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "  Scenario: Test\n"
                    "    Given I am on the homepage\n"
                    "    When I click the button\n"
                ),
                after=(
                    "  Scenario: Test\n"
                    "    Given the user is on the homepage\n"
                    "    When the user clicks the button\n"
                ),
                description="Replace 'I' with a descriptive third-person actor.",
            ),
        ],
        tags=["steps", "phrasing", "readability"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            for step in steps:
                text = getattr(step, "name", "").strip()
                if text.startswith("I ") or text.startswith("I've "):
                    diagnostics.append(
                        self.diagnostic(
                            message=(f"Step '{text}' uses first-person phrasing ('I')"),
                            node=step,
                            suggestion=(
                                "Use third-person phrasing (e.g., "
                                "'the user ...') for clarity."
                            ),
                        )
                    )

        return diagnostics


class BackgroundNameRule(Rule):
    """BS004: Detect backgrounds without a descriptive name.

    A Background should have a descriptive name that explains what
    the common setup is about. Unnamed backgrounds reduce readability.
    """

    metadata = RuleMetadata(
        rule_id="BS004",
        name="background-name",
        title="Background should have a descriptive name",
        description=(
            "Detects Background sections that lack a descriptive name. "
            "A named background improves readability and helps team "
            "members understand the common setup."
        ),
        category=Category.STYLE,
        default_severity=Severity.WARNING,
        motivation=(
            "An unnamed Background is just a list of steps. A "
            "descriptive name (e.g., 'Background: Given a logged-in "
            "user') communicates the shared context at a glance."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "Feature: Test\n\n"
                    "  Background:\n"
                    "    Given a logged-in user\n\n"
                    "  Scenario: A scenario\n"
                    "    When I do something\n"
                ),
                after=(
                    "Feature: Test\n\n"
                    "  Background: Authenticated user\n"
                    "    Given a logged-in user\n\n"
                    "  Scenario: A scenario\n"
                    "    When I do something\n"
                ),
                description="Add a descriptive name to the Background.",
            ),
        ],
        tags=["background", "naming", "readability"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        background = getattr(feature, "background", None)
        if background is None:
            return []

        name = getattr(background, "name", "").strip()
        if not name:
            return [
                self.diagnostic(
                    message="Background has no descriptive name",
                    node=background,
                    suggestion=(
                        "Add a descriptive name after 'Background:' "
                        "to explain the common setup."
                    ),
                )
            ]
        return []


class FeatureDescriptionFormattingRule(Rule):
    """BS005: Detect features missing a description.

    A feature should have a description (text between the Feature
    line and the first scenario/background) explaining the feature's
    purpose. Features without descriptions are harder to understand.
    """

    metadata = RuleMetadata(
        rule_id="BS005",
        name="feature-description-formatting",
        title="Feature should have a description",
        description=(
            "Detects features that lack a description. A description "
            "explains the feature's purpose and provides context for "
            "the scenarios below."
        ),
        category=Category.STYLE,
        default_severity=Severity.WARNING,
        motivation=(
            "A feature without a description is just a title. The "
            "description provides context, explains the business "
            "value, and helps team members understand the feature."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "Feature: User Registration\n\n"
                    "  Scenario: Register\n"
                    "    Given a new user\n"
                ),
                after=(
                    "Feature: User Registration\n"
                    "  As a new visitor\n"
                    "  I want to register an account\n"
                    "  So that I can access the application\n\n"
                    "  Scenario: Register\n"
                    "    Given a new user\n"
                ),
                description="Add a description after the Feature line.",
            ),
        ],
        tags=["feature", "description", "documentation"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        description = getattr(feature, "description", "").strip()
        if not description:
            location = getattr(feature, "location", None)
            file_path = getattr(location, "filename", "") if location else ""
            return [
                self.diagnostic(
                    message=(f"Feature '{feature.name}' has no description"),
                    node=feature,
                    file_path=file_path or None,
                    suggestion=(
                        "Add a description (e.g., 'As a ... I want to "
                        "... So that ...') after the Feature line."
                    ),
                )
            ]
        return []


__all__ = [
    "BackgroundNameRule",
    "FeatureDescriptionFormattingRule",
    "KeywordOrderingRule",
    "StepPhrasingRule",
    "TagCasingRule",
]
