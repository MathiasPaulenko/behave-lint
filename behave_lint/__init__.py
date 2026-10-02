"""behave-lint — A fast, opinionated, extensible linter for Gherkin .feature files.

This package provides static analysis for Behave BDD projects, consuming
behave-model as its single source of truth.

Only names explicitly exported here are considered stable and publicly
supported.
"""

from __future__ import annotations

from behave_lint.configuration.loader import load_config
from behave_lint.models import (
    AutoFixCapability,
    Category,
    Config,
    Diagnostic,
    FixCost,
    LintResult,
    LintSummary,
    PerformanceImpact,
    RuleExample,
    RuleMetadata,
    Severity,
)
from behave_lint.version import __version__

__all__ = [
    "AutoFixCapability",
    "Category",
    "Config",
    "Diagnostic",
    "FixCost",
    "LintResult",
    "LintSummary",
    "PerformanceImpact",
    "RuleExample",
    "RuleMetadata",
    "Severity",
    "__version__",
    "load_config",
]
