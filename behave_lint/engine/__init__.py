"""Lint Engine, Rule Registry, Rule Executor, Validation, Error Handler.

Application layer — components C03, C04, C05, C17, C20.

See COMPONENT_DESIGN.md Section 5 and RULE_ENGINE.md.
"""

from __future__ import annotations

from behave_lint.engine.lint_engine import LintEngine

__all__ = ["LintEngine"]
