"""Rule base class, visitor engine, documentation provider, built-in rules.

Domain layer — components C04, C05, C06, C19.

See COMPONENT_DESIGN.md Section 6 and RULE_ENGINE.md.
"""

from __future__ import annotations

from behave_lint.rules.base import Rule
from behave_lint.rules.context import FeatureLike, ProjectLike, RuleContext
from behave_lint.rules.diagnostic_factory import DiagnosticFactory, HasLocation
from behave_lint.rules.executor import RuleExecutor
from behave_lint.rules.registry import RuleRegistry
from behave_lint.rules.scope import RuleScope
from behave_lint.rules.validation import validate_metadata

__all__ = [
    "DiagnosticFactory",
    "FeatureLike",
    "HasLocation",
    "ProjectLike",
    "Rule",
    "RuleContext",
    "RuleExecutor",
    "RuleRegistry",
    "RuleScope",
    "validate_metadata",
]
