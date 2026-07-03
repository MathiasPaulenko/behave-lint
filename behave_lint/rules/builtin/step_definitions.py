"""Step definition rules - BD001-BD499.

Rules that detect potential step definition issues by analyzing
step text patterns. Default severity: WARNING.

See RULE_TAXONOMY.md Section 3 and IMPLEMENTATION_ROADMAP.md E7.6.
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

_PLACEHOLDER_PATTERN = re.compile(r"<[^>]+>")
_PARAMETER_PATTERN = re.compile(r"\{[^}]+\}")


class UndefinedStepPatternRule(Rule):
    """BD001: Detect steps that may not have matching definitions.

    Steps with placeholders like '<value>' in non-outline scenarios
    are likely undefined — placeholders are only valid in Scenario
    Outline steps.
    """

    metadata = RuleMetadata(
        rule_id="BD001",
        name="undefined-step-pattern",
        title="Step may not have a matching definition",
        description=(
            "Detects steps that use placeholder syntax (<value>) "
            "outside of Scenario Outline contexts, which likely "
            "indicates a missing or incorrect step definition."
        ),
        category=Category.STEP_DEFINITIONS,
        default_severity=Severity.WARNING,
        motivation=(
            "Placeholders in non-outline scenarios won't be "
            "substituted and will cause step matching failures "
            "at runtime."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=("  Scenario: Test\n    Given a <value>\n"),
                after=(
                    "  Scenario Outline: Test <value>\n"
                    "    Given a <value>\n\n"
                    "    Examples:\n"
                    "      | value |\n"
                    "      | foo   |\n"
                ),
                description="Use a Scenario Outline with Examples.",
            ),
        ],
        tags=["steps", "definitions", "placeholders"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            is_outline = getattr(scenario, "examples", None) is not None
            if is_outline:
                continue

            steps = getattr(scenario, "steps", [])
            for step in steps:
                text = getattr(step, "name", "")
                if _PLACEHOLDER_PATTERN.search(text):
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Step '{step.name}' uses placeholder "
                                "syntax but is not in a Scenario Outline"
                            ),
                            node=step,
                            suggestion=(
                                "Move this step to a Scenario Outline "
                                "with Examples, or replace the "
                                "placeholder with a concrete value."
                            ),
                        )
                    )

        return diagnostics


class AmbiguousStepPatternRule(Rule):
    """BD002: Detect steps that could match multiple definitions.

    Steps with very generic text (e.g., 'Given a thing') may match
    multiple step definitions, causing ambiguous matches at runtime.
    """

    metadata = RuleMetadata(
        rule_id="BD002",
        name="ambiguous-step-pattern",
        title="Step text may match multiple definitions",
        description=(
            "Detects steps with very generic text that could match "
            "multiple step definitions, leading to ambiguous matches "
            "at runtime."
        ),
        category=Category.STEP_DEFINITIONS,
        default_severity=Severity.WARNING,
        motivation=(
            "Ambiguous step matches cause runtime errors in behave. "
            "Using more specific step text avoids this problem."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=("  Scenario: Test\n    Given a thing\n"),
                after=("  Scenario: Test\n    Given a user named 'Alice'\n"),
                description="Use more specific step text.",
            ),
        ],
        tags=["steps", "definitions", "ambiguous"],
    )

    _GENERIC_WORDS = frozenset(
        {"thing", "stuff", "item", "data", "value", "object", "element"}
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            for step in steps:
                text = getattr(step, "name", "").strip().lower()
                words = set(text.split())
                if words & self._GENERIC_WORDS:
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Step '{step.name}' uses generic "
                                "text that may match multiple "
                                "definitions"
                            ),
                            node=step,
                            suggestion=(
                                "Use more specific text to avoid "
                                "ambiguous step matches."
                            ),
                        )
                    )

        return diagnostics


class UnusedStepDefinitionRule(Rule):
    """BD003: Detect step text patterns that are never reused.

    Steps that appear only once across all scenarios may indicate
    an unused step definition or a lack of step reuse.
    """

    metadata = RuleMetadata(
        rule_id="BD003",
        name="unused-step-definition",
        title="Step text is used only once",
        description=(
            "Detects step text that appears only once in the entire "
            "feature. While not necessarily wrong, low reuse may "
            "indicate missing step definition reuse."
        ),
        category=Category.STEP_DEFINITIONS,
        default_severity=Severity.INFO,
        motivation=(
            "Step definitions are most valuable when reused across "
            "scenarios. Steps used only once may not warrant a "
            "dedicated definition."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "  Scenario: A\n"
                    "    Given a unique step\n\n"
                    "  Scenario: B\n"
                    "    Given a different step\n"
                ),
                after=(
                    "  Scenario: A\n"
                    "    Given a common step\n\n"
                    "  Scenario: B\n"
                    "    Given a common step\n"
                ),
                description="Reuse step definitions where possible.",
            ),
        ],
        tags=["steps", "definitions", "reuse"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        step_counts: dict[str, int] = {}
        step_instances: list[tuple[Any, str]] = []

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            for step in steps:
                text = getattr(step, "name", "").strip().lower()
                if not text:
                    continue
                step_counts[text] = step_counts.get(text, 0) + 1
                step_instances.append((step, text))

        for step, text in step_instances:
            if step_counts[text] == 1:
                diagnostics.append(
                    self.diagnostic(
                        message=(
                            f"Step '{step.name}' is used only once in this feature"
                        ),
                        node=step,
                        suggestion=(
                            "Consider reusing this step in other "
                            "scenarios or inlining it."
                        ),
                        severity=Severity.INFO,
                    )
                )

        return diagnostics


class StepParameterConventionRule(Rule):
    """BD004: Detect inconsistent step parameter conventions.

    Steps should use consistent parameter syntax. Mixing {param}
    style with <param> style in the same scenario is inconsistent.
    """

    metadata = RuleMetadata(
        rule_id="BD004",
        name="step-parameter-convention",
        title="Step parameter convention is inconsistent",
        description=(
            "Detects steps that mix different parameter conventions "
            "({param} vs <param>) within the same scenario. "
            "Consistent parameter syntax improves readability."
        ),
        category=Category.STEP_DEFINITIONS,
        default_severity=Severity.WARNING,
        motivation=(
            "Mixing parameter conventions is confusing. Use <param> "
            "for Scenario Outline placeholders and {param} for "
            "step definition parameters."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "  Scenario Outline: Test\n    Given a <value> with {count} items\n"
                ),
                after=(
                    "  Scenario Outline: Test\n    Given a <value> with <count> items\n"
                ),
                description="Use consistent parameter syntax.",
            ),
        ],
        tags=["steps", "parameters", "conventions"],
        auto_fix=AutoFixCapability.SAFE,
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            has_brace_param = False
            has_angle_param = False

            for step in steps:
                text = getattr(step, "name", "")
                if _PARAMETER_PATTERN.search(text):
                    has_brace_param = True
                if _PLACEHOLDER_PATTERN.search(text):
                    has_angle_param = True

            if has_brace_param and has_angle_param:
                for step in steps:
                    text = getattr(step, "name", "")
                    if _PARAMETER_PATTERN.search(text):
                        diagnostics.append(
                            self.diagnostic(
                                message=(
                                    f"Step '{step.name}' uses {{param}} "
                                    "syntax while other steps use "
                                    "<param> syntax"
                                ),
                                node=step,
                                suggestion=(
                                    "Use consistent parameter syntax "
                                    "within the same scenario."
                                ),
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

        diag_lines = {d.line for d in diagnostics if d.rule_id == "BD004"}

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            has_brace_param = False
            has_angle_param = False

            for step in steps:
                text = getattr(step, "name", "")
                if _PARAMETER_PATTERN.search(text):
                    has_brace_param = True
                if _PLACEHOLDER_PATTERN.search(text):
                    has_angle_param = True

            if not (has_brace_param and has_angle_param):
                continue

            for step in steps:
                text = getattr(step, "name", "")
                if not _PARAMETER_PATTERN.search(text):
                    continue

                step_line = getattr(step, "line", None)
                if step_line is None:
                    loc = getattr(step, "location", None)
                    if loc is not None:
                        step_line = getattr(loc, "line", None)
                if step_line is None or step_line not in diag_lines:
                    continue

                idx = step_line - 1
                if idx < 0 or idx >= len(lines):
                    continue

                old_line = lines[idx]
                new_line = _PARAMETER_PATTERN.sub(
                    lambda m: f"<{m.group()[1:-1]}>", old_line
                )

                if new_line != old_line:
                    fixes.append(
                        FixEdit(
                            file_path=file_path,
                            start_line=step_line,
                            end_line=step_line,
                            old_text=old_line,
                            new_text=new_line,
                            safety=AutoFixCapability.SAFE,
                            rule_id="BD004",
                            diagnostic_line=step_line,
                        )
                    )

        return fixes


class StepTrailingPunctuationRule(Rule):
    """BD005: Detect steps ending with punctuation.

    Step text should not end with a period, comma, or other
    punctuation. This is a step definition convention issue
    that can cause matching failures.
    """

    metadata = RuleMetadata(
        rule_id="BD005",
        name="step-trailing-punctuation",
        title="Step text ends with punctuation",
        description=(
            "Detects steps that end with punctuation marks like "
            "periods or commas. Trailing punctuation can cause "
            "step matching failures."
        ),
        category=Category.STEP_DEFINITIONS,
        default_severity=Severity.WARNING,
        motivation=(
            "Step definitions typically don't include trailing "
            "punctuation. A step ending with '.' won't match a "
            "definition that doesn't expect it."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "  Scenario: Test\n    Given a user.\n    When I click submit.\n"
                ),
                after=("  Scenario: Test\n    Given a user\n    When I click submit\n"),
                description="Remove trailing punctuation from steps.",
            ),
        ],
        tags=["steps", "punctuation", "definitions"],
        auto_fix=AutoFixCapability.SAFE,
    )

    _TRAILING_PUNCTUATION = frozenset({".", ",", ";", "!", ":"})

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            for step in steps:
                text = getattr(step, "name", "").strip()
                if text and text[-1] in self._TRAILING_PUNCTUATION:
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Step '{step.name}' ends with punctuation '{text[-1]}'"
                            ),
                            node=step,
                            suggestion=(
                                "Remove trailing punctuation from the step text."
                            ),
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

        diag_lines = {d.line for d in diagnostics if d.rule_id == "BD005"}

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            for step in steps:
                text = getattr(step, "name", "").strip()
                if not text or text[-1] not in self._TRAILING_PUNCTUATION:
                    continue

                step_line = getattr(step, "line", None)
                if step_line is None:
                    loc = getattr(step, "location", None)
                    if loc is not None:
                        step_line = getattr(loc, "line", None)
                if step_line is None or step_line not in diag_lines:
                    continue

                idx = step_line - 1
                if idx < 0 or idx >= len(lines):
                    continue

                old_line = lines[idx]
                stripped = old_line.rstrip("\r\n")
                trailing = old_line[len(stripped) :]

                if stripped[-1] in self._TRAILING_PUNCTUATION:
                    new_line = stripped[:-1] + trailing
                    fixes.append(
                        FixEdit(
                            file_path=file_path,
                            start_line=step_line,
                            end_line=step_line,
                            old_text=old_line,
                            new_text=new_line,
                            safety=AutoFixCapability.SAFE,
                            rule_id="BD005",
                            diagnostic_line=step_line,
                        )
                    )

        return fixes


__all__ = [
    "AmbiguousStepPatternRule",
    "StepParameterConventionRule",
    "StepTrailingPunctuationRule",
    "UndefinedStepPatternRule",
    "UnusedStepDefinitionRule",
]
