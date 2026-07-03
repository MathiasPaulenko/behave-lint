"""Rules for the {{ cookiecutter.project_name }} plugin."""

from __future__ import annotations

from typing import Any

{% if cookiecutter.include_auto_fix == "yes" %}from behave_lint.autofix.models import FixEdit
{% endif %}from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
{% if cookiecutter.include_auto_fix == "yes" %}from behave_lint.models.enums import AutoFixCapability
{% endif %}from behave_lint.models.rule_metadata import RuleExample, RuleMetadata
from behave_lint.rules.base import Rule


class {{ cookiecutter.class_name }}Rule(Rule):
    """{{ cookiecutter.rule_id }}: {{ cookiecutter.rule_title }}

    {{ cookiecutter.rule_description }}
    """

    metadata = RuleMetadata(
        rule_id="{{ cookiecutter.rule_id }}",
        name="{{ cookiecutter.rule_name }}",
        title="{{ cookiecutter.rule_title }}",
        description="{{ cookiecutter.rule_description }}",
        category=Category.{{ cookiecutter.category | upper }},
        default_severity=Severity.{{ cookiecutter.severity | upper }},
        motivation=(
            "TODO: Explain why this rule exists — what problem does it solve?"
        ),
        since="{{ cookiecutter.version }}",
        examples=[
            RuleExample(
                before=(
                    "Feature: Example\n\n"
                    "  Scenario: A scenario\n"
                    "    Given a step\n"
                ),
                after=(
                    "Feature: Example\n\n"
                    "  Scenario: A scenario\n"
                    "    Given a fixed step\n"
                ),
                description="TODO: Describe the fix.",
            ),
        ],
        tags=["custom"],
{% if cookiecutter.include_auto_fix == "yes" %}
        auto_fix=AutoFixCapability.SAFE,
{% endif %}
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        """Analyze the feature and return diagnostics.

        Args:
            feature: The parsed feature model.
            config: The resolved configuration object.

        Returns:
            A list of diagnostics.
        """
        diagnostics: list[Diagnostic] = []

        # TODO: Implement your rule logic here.
        # Use self.diagnostic() to create diagnostics with metadata pre-filled.
        #
        # Example:
        #   for scenario in getattr(feature, "scenarios", []):
        #       name = getattr(scenario, "name", "")
        #       if not name:
        #           diagnostics.append(
        #               self.diagnostic(
        #                   message="Scenario has no name",
        #                   node=scenario,
        #                   suggestion="Add a descriptive name.",
        #               )
        #           )

        return diagnostics
{% if cookiecutter.include_auto_fix == "yes" %}

    def get_fixes(
        self, feature: Any, config: Config, diagnostics: list[Diagnostic]
    ) -> list[FixEdit]:
        """Return fix edits for the given diagnostics.

        Override this method to provide auto-fix support.

        Args:
            feature: The parsed feature model.
            config: The resolved configuration object.
            diagnostics: Diagnostics produced by this rule's check().

        Returns:
            A list of FixEdit objects to apply.
        """
        fixes: list[FixEdit] = []

        # TODO: Implement your fix logic here.
        # See existing rules (e.g., BS001, BS007) for patterns.

        return fixes
{% endif %}


def register_rules() -> list[type[Rule]]:
    """Entry point function — returns rule classes to register.

    This function is called by behave-lint's plugin manager when
    the plugin is discovered via the ``behave_lint.rules`` entry point.

    Returns:
        A list of Rule subclasses to register.
    """
    return [{{ cookiecutter.class_name }}Rule]
