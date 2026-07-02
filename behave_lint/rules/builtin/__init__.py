"""Built-in rules — registered via entry points in M7.

This subpackage contains all built-in rule implementations organized by
category (per RULE_TAXONOMY.md). Each category gets its own module.
"""

from __future__ import annotations

from behave_lint.rules.builtin.complexity import (
    LongStepTextRule,
    TooManyExampleRowsRule,
    TooManyScenariosRule,
    TooManyStepsRule,
    TooManyTagsRule,
)
from behave_lint.rules.builtin.consistency import (
    DuplicateStepTextRule,
    InconsistentNamingConventionRule,
    InconsistentScenarioLengthRule,
    InconsistentStepTextRule,
    InconsistentTagUsageRule,
)
from behave_lint.rules.builtin.correctness import (
    DuplicateFeatureNamesRule,
    DuplicateScenarioNamesRule,
    EmptyFeatureRule,
    InvalidExampleTableStructureRule,
    InvalidTagSyntaxRule,
    ScenarioOutlineWithoutExamplesRule,
)
from behave_lint.rules.builtin.pedantic import (
    MissingBackgroundRule,
    MissingExamplesNameRule,
    MissingScenarioTagsRule,
    ShortFeatureNameRule,
    ShortScenarioNameRule,
)
from behave_lint.rules.builtin.step_definitions import (
    AmbiguousStepPatternRule,
    StepParameterConventionRule,
    StepTrailingPunctuationRule,
    UndefinedStepPatternRule,
    UnusedStepDefinitionRule,
)
from behave_lint.rules.builtin.style import (
    BackgroundNameRule,
    FeatureDescriptionFormattingRule,
    KeywordOrderingRule,
    StepPhrasingRule,
    TagCasingRule,
)
from behave_lint.rules.registry import RuleRegistry

_BUILTIN_RULES: list[type] = [
    DuplicateScenarioNamesRule,
    EmptyFeatureRule,
    ScenarioOutlineWithoutExamplesRule,
    InvalidTagSyntaxRule,
    DuplicateFeatureNamesRule,
    InvalidExampleTableStructureRule,
    TagCasingRule,
    KeywordOrderingRule,
    StepPhrasingRule,
    BackgroundNameRule,
    FeatureDescriptionFormattingRule,
    TooManyStepsRule,
    TooManyScenariosRule,
    TooManyExampleRowsRule,
    LongStepTextRule,
    TooManyTagsRule,
    InconsistentStepTextRule,
    InconsistentTagUsageRule,
    InconsistentNamingConventionRule,
    InconsistentScenarioLengthRule,
    DuplicateStepTextRule,
    MissingScenarioTagsRule,
    MissingBackgroundRule,
    ShortScenarioNameRule,
    ShortFeatureNameRule,
    MissingExamplesNameRule,
    UndefinedStepPatternRule,
    AmbiguousStepPatternRule,
    UnusedStepDefinitionRule,
    StepParameterConventionRule,
    StepTrailingPunctuationRule,
]


def register_builtins(registry: RuleRegistry) -> None:
    """Register all built-in rules with the given registry.

    Args:
        registry: The rule registry to populate.
    """
    for rule_class in _BUILTIN_RULES:
        registry.register(rule_class, source="built-in")


__all__ = [
    "AmbiguousStepPatternRule",
    "BackgroundNameRule",
    "DuplicateFeatureNamesRule",
    "DuplicateScenarioNamesRule",
    "DuplicateStepTextRule",
    "EmptyFeatureRule",
    "FeatureDescriptionFormattingRule",
    "InconsistentNamingConventionRule",
    "InconsistentScenarioLengthRule",
    "InconsistentStepTextRule",
    "InconsistentTagUsageRule",
    "InvalidExampleTableStructureRule",
    "InvalidTagSyntaxRule",
    "KeywordOrderingRule",
    "LongStepTextRule",
    "MissingBackgroundRule",
    "MissingExamplesNameRule",
    "MissingScenarioTagsRule",
    "ScenarioOutlineWithoutExamplesRule",
    "ShortFeatureNameRule",
    "ShortScenarioNameRule",
    "StepParameterConventionRule",
    "StepPhrasingRule",
    "StepTrailingPunctuationRule",
    "TagCasingRule",
    "TooManyExampleRowsRule",
    "TooManyScenariosRule",
    "TooManyStepsRule",
    "TooManyTagsRule",
    "UndefinedStepPatternRule",
    "UnusedStepDefinitionRule",
    "register_builtins",
]
