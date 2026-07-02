"""Complexity rules - BX001-BX499.

Rules that detect overly complex features and scenarios.
Default severity: WARNING.

See RULE_TAXONOMY.md Section 3 and IMPLEMENTATION_ROADMAP.md E7.3.
"""

from __future__ import annotations

from typing import Any, ClassVar

from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.rule_metadata import RuleExample, RuleMetadata
from behave_lint.rules.base import Rule

_DEFAULT_MAX_STEPS = 10
_DEFAULT_MAX_SCENARIOS = 10
_DEFAULT_MAX_EXAMPLE_ROWS = 20
_DEFAULT_MAX_STEP_LENGTH = 120


class TooManyStepsRule(Rule):
    """BX001: Detect scenarios with too many steps.

    Scenarios with many steps are hard to understand and maintain.
    The default threshold is 10 steps.
    """

    metadata = RuleMetadata(
        rule_id="BX001",
        name="too-many-steps",
        title="Scenario has too many steps",
        description=(
            "Detects scenarios that exceed the maximum number of "
            "steps. Complex scenarios are hard to understand and "
            "maintain."
        ),
        category=Category.COMPLEXITY,
        default_severity=Severity.WARNING,
        motivation=(
            "Scenarios with many steps try to test too much at once. "
            "Splitting them into smaller scenarios improves "
            "readability and maintainability."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "  Scenario: Complex test\n"
                    "    Given step 1\n"
                    "    And step 2\n"
                    "    ... (12 steps)\n"
                    "    Then result\n"
                ),
                after=(
                    "  Scenario: Setup\n"
                    "    Given step 1\n"
                    "    And step 2\n\n"
                    "  Scenario: Action and result\n"
                    "    When step 3\n"
                    "    Then result\n"
                ),
                description="Split the scenario into smaller ones.",
            ),
        ],
        tags=["scenario", "steps", "complexity"],
        configurable=True,
    )

    default_params: ClassVar[dict[str, Any]] = {"max_steps": _DEFAULT_MAX_STEPS}

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        max_steps = _DEFAULT_MAX_STEPS

        rule_config = getattr(config, "rules", {}).get("BX001", {})
        if isinstance(rule_config, dict):
            max_steps = rule_config.get("max_steps", max_steps)

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            if len(steps) > max_steps:
                diagnostics.append(
                    self.diagnostic(
                        message=(
                            f"Scenario '{scenario.name}' has {len(steps)} "
                            f"steps (max: {max_steps})"
                        ),
                        node=scenario,
                        suggestion=(
                            "Split this scenario into smaller, focused scenarios."
                        ),
                    )
                )

        return diagnostics


class TooManyScenariosRule(Rule):
    """BX002: Detect features with too many scenarios.

    Features with many scenarios are hard to navigate and maintain.
    The default threshold is 10 scenarios.
    """

    metadata = RuleMetadata(
        rule_id="BX002",
        name="too-many-scenarios",
        title="Feature has too many scenarios",
        description=(
            "Detects features that exceed the maximum number of "
            "scenarios. Large features should be split into "
            "smaller, focused features."
        ),
        category=Category.COMPLEXITY,
        default_severity=Severity.WARNING,
        motivation=(
            "A feature with many scenarios tries to cover too much. "
            "Splitting it into smaller features improves organization "
            "and navigability."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "Feature: Big Feature\n\n"
                    "  Scenario: Test 1\n"
                    "    ...\n\n"
                    "  Scenario: Test 2\n"
                    "    ...\n\n"
                    "  ... (15 scenarios)\n"
                ),
                after=(
                    "# feature1.feature\n"
                    "Feature: Feature Part 1\n\n"
                    "  Scenario: Test 1\n"
                    "    ...\n\n"
                    "# feature2.feature\n"
                    "Feature: Feature Part 2\n\n"
                    "  Scenario: Test 2\n"
                    "    ...\n"
                ),
                description="Split the feature into multiple files.",
            ),
        ],
        tags=["feature", "scenarios", "complexity"],
        configurable=True,
    )

    default_params: ClassVar[dict[str, Any]] = {"max_scenarios": _DEFAULT_MAX_SCENARIOS}

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        scenarios = list(feature.all_scenarios())
        max_scenarios = _DEFAULT_MAX_SCENARIOS

        rule_config = getattr(config, "rules", {}).get("BX002", {})
        if isinstance(rule_config, dict):
            max_scenarios = rule_config.get("max_scenarios", max_scenarios)

        if len(scenarios) > max_scenarios:
            location = getattr(feature, "location", None)
            file_path = getattr(location, "filename", "") if location else ""
            return [
                self.diagnostic(
                    message=(
                        f"Feature '{feature.name}' has {len(scenarios)} "
                        f"scenarios (max: {max_scenarios})"
                    ),
                    node=feature,
                    file_path=file_path or None,
                    suggestion=("Split this feature into smaller, focused features."),
                )
            ]
        return []


class TooManyExampleRowsRule(Rule):
    """BX003: Detect example tables with too many rows.

    Example tables with many rows create long test runs and are
    hard to maintain. The default threshold is 20 rows.
    """

    metadata = RuleMetadata(
        rule_id="BX003",
        name="too-many-example-rows",
        title="Example table has too many rows",
        description=(
            "Detects example tables that exceed the maximum number "
            "of data rows. Large example tables are hard to maintain "
            "and slow down test execution."
        ),
        category=Category.COMPLEXITY,
        default_severity=Severity.WARNING,
        motivation=(
            "Example tables with many rows are hard to review and "
            "maintain. Consider grouping related rows into separate "
            "Examples sections or scenarios."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "  Scenario Outline: Test <value>\n"
                    "    Given a <value>\n\n"
                    "    Examples:\n"
                    "      | value |\n"
                    "      | a     |\n"
                    "      | b     |\n"
                    "      ... (25 rows)\n"
                ),
                after=(
                    "  Scenario Outline: Valid <value>\n"
                    "    Given a <value>\n\n"
                    "    Examples: Valid values\n"
                    "      | value |\n"
                    "      | a     |\n"
                    "      | b     |\n\n"
                    "    Examples: Edge cases\n"
                    "      | value |\n"
                    "      | z     |\n"
                ),
                description="Split examples into named groups.",
            ),
        ],
        tags=["examples", "table", "complexity"],
        configurable=True,
    )

    default_params: ClassVar[dict[str, Any]] = {
        "max_example_rows": _DEFAULT_MAX_EXAMPLE_ROWS
    }

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        max_rows = _DEFAULT_MAX_EXAMPLE_ROWS

        rule_config = getattr(config, "rules", {}).get("BX003", {})
        if isinstance(rule_config, dict):
            max_rows = rule_config.get("max_example_rows", max_rows)

        for scenario in feature.all_scenarios():
            examples = getattr(scenario, "examples", None)
            if not examples:
                continue

            for example in examples:
                table = getattr(example, "table", None)
                if table is None:
                    continue

                rows = getattr(table, "rows", [])
                if len(rows) > max_rows:
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Example table in scenario "
                                f"'{scenario.name}' has {len(rows)} "
                                f"data rows (max: {max_rows})"
                            ),
                            node=example,
                            suggestion=(
                                "Split the examples into named "
                                "groups or separate scenarios."
                            ),
                        )
                    )

        return diagnostics


class LongStepTextRule(Rule):
    """BX004: Detect steps with overly long text.

    Steps with very long text are hard to read. The default
    threshold is 120 characters.
    """

    metadata = RuleMetadata(
        rule_id="BX004",
        name="long-step-text",
        title="Step text is too long",
        description=(
            "Detects steps with text exceeding the maximum length. "
            "Long step text reduces readability."
        ),
        category=Category.COMPLEXITY,
        default_severity=Severity.WARNING,
        motivation=(
            "Very long step text is hard to scan and understand. "
            "Consider using a data table or breaking the step into "
            "smaller, more descriptive steps."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "  Scenario: Test\n"
                    "    Given a very long step that goes on "
                    "and on with lots of detail about what it does\n"
                ),
                after=(
                    "  Scenario: Test\n"
                    "    Given a precondition\n"
                    "      | detail |\n"
                    "      | value  |\n"
                ),
                description="Use a data table for detailed information.",
            ),
        ],
        tags=["steps", "readability", "complexity"],
        configurable=True,
    )

    default_params: ClassVar[dict[str, Any]] = {
        "max_step_length": _DEFAULT_MAX_STEP_LENGTH
    }

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        max_length = _DEFAULT_MAX_STEP_LENGTH

        rule_config = getattr(config, "rules", {}).get("BX004", {})
        if isinstance(rule_config, dict):
            max_length = rule_config.get("max_step_length", max_length)

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            for step in steps:
                text = getattr(step, "name", "")
                if len(text) > max_length:
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Step text is {len(text)} characters "
                                f"(max: {max_length})"
                            ),
                            node=step,
                            suggestion=(
                                "Shorten the step text or use a "
                                "data table for detailed information."
                            ),
                        )
                    )

        return diagnostics


class TooManyTagsRule(Rule):
    """BX005: Detect scenarios or features with too many tags.

    Having too many tags on a single element makes it hard to
    understand which tags are meaningful. The default threshold
    is 5 tags.
    """

    metadata = RuleMetadata(
        rule_id="BX005",
        name="too-many-tags",
        title="Element has too many tags",
        description=(
            "Detects features or scenarios that exceed the maximum "
            "number of tags. Too many tags reduce clarity."
        ),
        category=Category.COMPLEXITY,
        default_severity=Severity.WARNING,
        motivation=(
            "When an element has many tags, it becomes hard to "
            "understand which tags are meaningful for filtering. "
            "Keep tags focused and minimal."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "@smoke @regression @fast @wip @nightly @integration\n"
                    "  Scenario: Test\n"
                    "    Given a step\n"
                ),
                after=("@smoke @regression\n  Scenario: Test\n    Given a step\n"),
                description="Keep only the most relevant tags.",
            ),
        ],
        tags=["tags", "complexity"],
        configurable=True,
    )

    default_params: ClassVar[dict[str, Any]] = {"max_tags": 5}

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        max_tags = 5

        rule_config = getattr(config, "rules", {}).get("BX005", {})
        if isinstance(rule_config, dict):
            max_tags = rule_config.get("max_tags", max_tags)

        feature_tags = getattr(feature, "tags", [])
        if len(feature_tags) > max_tags:
            location = getattr(feature, "location", None)
            file_path = getattr(location, "filename", "") if location else ""
            diagnostics.append(
                self.diagnostic(
                    message=(
                        f"Feature '{feature.name}' has "
                        f"{len(feature_tags)} tags (max: {max_tags})"
                    ),
                    node=feature,
                    file_path=file_path or None,
                    suggestion="Reduce the number of tags on this feature.",
                )
            )

        for scenario in feature.all_scenarios():
            scenario_tags = getattr(scenario, "tags", [])
            if len(scenario_tags) > max_tags:
                diagnostics.append(
                    self.diagnostic(
                        message=(
                            f"Scenario '{scenario.name}' has "
                            f"{len(scenario_tags)} tags (max: {max_tags})"
                        ),
                        node=scenario,
                        suggestion=("Reduce the number of tags on this scenario."),
                    )
                )

        return diagnostics


__all__ = [
    "LongStepTextRule",
    "TooManyExampleRowsRule",
    "TooManyScenariosRule",
    "TooManyStepsRule",
    "TooManyTagsRule",
]
