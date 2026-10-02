"""Shared domain models — Severity, Category, Diagnostic, Config, LintResult.

Domain layer (innermost). No dependencies on any other subpackage.
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
from behave_lint.models.project import Project
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
    "Project",
    "RuleExample",
    "RuleMetadata",
    "Severity",
]
