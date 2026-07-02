"""Custom rule: detect Given steps appearing after Then steps."""

from __future__ import annotations

from typing import Any

from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.rule_metadata import RuleMetadata, RuleExample
from behave_lint.rules.base import Rule


class NoGivenAfterThenRule(Rule):
    """EX001: Given steps should not appear after Then steps."""

    metadata = RuleMetadata(
        rule_id="EX001",
        name="no-given-after-then",
        title="Given steps should not appear after Then steps",
        description=(
            "Detects Given steps that appear after a Then step, "
            "which breaks the Given-When-Then convention."
        ),
        category=Category.STYLE,
        default_severity=Severity.WARNING,
        motivation=(
            "Given steps after Then steps are confusing and break "
            "the Arrange-Act-Assert pattern."
        ),
        since="1.0.0",
        examples=[
            RuleExample(
                before=(
                    "  Scenario: Test\n"
                    "    Given a user\n"
                    "    Then I see results\n"
                    "    Given another user\n"
                ),
                after=(
                    "  Scenario: Test\n"
                    "    Given a user\n"
                    "    And another user\n"
                    "    Then I see results\n"
                ),
                description="Move Given steps before Then.",
            ),
        ],
        tags=["steps", "ordering", "custom"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for scenario in feature.all_scenarios():
            seen_then = False
            for step in getattr(scenario, "steps", []):
                keyword = getattr(step, "keyword", "").strip().lower()
                if keyword == "then":
                    seen_then = True
                if seen_then and keyword == "given":
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Given step '{step.name}' appears "
                                "after a Then step"
                            ),
                            node=step,
                            suggestion="Move Given steps before Then.",
                        )
                    )
        return diagnostics
