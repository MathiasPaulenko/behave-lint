"""Shared domain models — Severity, Category, Diagnostic, Config, LintResult.

Domain layer (innermost). No dependencies on any other subpackage.

See API.md Section 4 and COMPONENT_DESIGN.md Section 6.
"""

from __future__ import annotations

from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import (
    AutoFixCapability,
    Category,
    EducationalValue,
    FixCost,
    PerformanceImpact,
    Severity,
)
from behave_lint.models.lint_result import LintResult, LintSummary
from behave_lint.models.rule_metadata import RuleExample, RuleMetadata

__all__ = [
    "AutoFixCapability",
    "Category",
    "Config",
    "Diagnostic",
    "EducationalValue",
    "FixCost",
    "LintResult",
    "LintSummary",
    "PerformanceImpact",
    "RuleExample",
    "RuleMetadata",
    "Severity",
]
