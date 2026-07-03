"""Built-in rules — registered via entry points in M7.

This subpackage contains all built-in rule implementations organized by
category (per RULE_TAXONOMY.md). Each category gets its own module.
"""

from __future__ import annotations

from behave_lint.rules.builtin.accessibility import (
    AbleistLanguageRule,
    ColorOnlyContrastRule,
    MissingAccessibilityScenarioRule,
)
from behave_lint.rules.builtin.complexity import (
    FeatureFileTooLongRule,
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
    DuplicateExamplesNameRule,
    DuplicateFeatureNamesRule,
    DuplicateScenarioNamesRule,
    EmptyFeatureRule,
    EmptyScenarioRule,
    InvalidExampleTableStructureRule,
    InvalidTagSyntaxRule,
    ScenarioOutlineWithoutExamplesRule,
    UndefinedOutlinePlaceholderRule,
    UnusedOutlinePlaceholderRule,
)
from behave_lint.rules.builtin.i18n import (
    HardcodedCurrencyRule,
    HardcodedDateFormatRule,
    NonAsciiStepTextRule,
)
from behave_lint.rules.builtin.pedantic import (
    MissingBackgroundRule,
    MissingExamplesNameRule,
    MissingFeatureDescriptionRule,
    MissingScenarioTagsRule,
    ScenarioWithoutAssertionRule,
    ShortFeatureNameRule,
    ShortScenarioNameRule,
)
from behave_lint.rules.builtin.security import (
    HardcodedSecretsRule,
    SensitiveTagRule,
    UrlWithCredentialsRule,
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
    StepKeywordCasingRule,
    StepPhrasingRule,
    TabIndentationRule,
    TagCasingRule,
    TrailingWhitespaceRule,
)
from behave_lint.rules.registry import RuleRegistry

_BUILTIN_RULES: list[type] = [
    DuplicateScenarioNamesRule,
    EmptyFeatureRule,
    EmptyScenarioRule,
    ScenarioOutlineWithoutExamplesRule,
    InvalidTagSyntaxRule,
    DuplicateFeatureNamesRule,
    InvalidExampleTableStructureRule,
    UnusedOutlinePlaceholderRule,
    UndefinedOutlinePlaceholderRule,
    DuplicateExamplesNameRule,
    TagCasingRule,
    KeywordOrderingRule,
    StepPhrasingRule,
    BackgroundNameRule,
    FeatureDescriptionFormattingRule,
    StepKeywordCasingRule,
    TrailingWhitespaceRule,
    TabIndentationRule,
    TooManyStepsRule,
    TooManyScenariosRule,
    TooManyExampleRowsRule,
    LongStepTextRule,
    TooManyTagsRule,
    FeatureFileTooLongRule,
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
    MissingFeatureDescriptionRule,
    ScenarioWithoutAssertionRule,
    UndefinedStepPatternRule,
    AmbiguousStepPatternRule,
    UnusedStepDefinitionRule,
    StepParameterConventionRule,
    StepTrailingPunctuationRule,
    HardcodedSecretsRule,
    UrlWithCredentialsRule,
    SensitiveTagRule,
    HardcodedDateFormatRule,
    HardcodedCurrencyRule,
    NonAsciiStepTextRule,
    AbleistLanguageRule,
    MissingAccessibilityScenarioRule,
    ColorOnlyContrastRule,
]


def register_builtins(registry: RuleRegistry) -> None:
    """Register all built-in rules with the given registry.

    Args:
        registry: The rule registry to populate.
    """
    for rule_class in _BUILTIN_RULES:
        registry.register(rule_class, source="built-in")


__all__ = [
    "AbleistLanguageRule",
    "AmbiguousStepPatternRule",
    "BackgroundNameRule",
    "ColorOnlyContrastRule",
    "DuplicateExamplesNameRule",
    "DuplicateFeatureNamesRule",
    "DuplicateScenarioNamesRule",
    "DuplicateStepTextRule",
    "EmptyFeatureRule",
    "EmptyScenarioRule",
    "FeatureDescriptionFormattingRule",
    "FeatureFileTooLongRule",
    "HardcodedCurrencyRule",
    "HardcodedDateFormatRule",
    "HardcodedSecretsRule",
    "InconsistentNamingConventionRule",
    "InconsistentScenarioLengthRule",
    "InconsistentStepTextRule",
    "InconsistentTagUsageRule",
    "InvalidExampleTableStructureRule",
    "InvalidTagSyntaxRule",
    "KeywordOrderingRule",
    "LongStepTextRule",
    "MissingAccessibilityScenarioRule",
    "MissingBackgroundRule",
    "MissingExamplesNameRule",
    "MissingFeatureDescriptionRule",
    "MissingScenarioTagsRule",
    "NonAsciiStepTextRule",
    "ScenarioOutlineWithoutExamplesRule",
    "ScenarioWithoutAssertionRule",
    "SensitiveTagRule",
    "ShortFeatureNameRule",
    "ShortScenarioNameRule",
    "StepKeywordCasingRule",
    "StepParameterConventionRule",
    "StepPhrasingRule",
    "StepTrailingPunctuationRule",
    "TabIndentationRule",
    "TagCasingRule",
    "TooManyExampleRowsRule",
    "TooManyScenariosRule",
    "TooManyStepsRule",
    "TooManyTagsRule",
    "TrailingWhitespaceRule",
    "UndefinedOutlinePlaceholderRule",
    "UndefinedStepPatternRule",
    "UnusedOutlinePlaceholderRule",
    "UnusedStepDefinitionRule",
    "UrlWithCredentialsRule",
    "register_builtins",
]
