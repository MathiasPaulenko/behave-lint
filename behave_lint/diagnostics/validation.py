"""Diagnostic validation — field checks before aggregation.

Validates that each diagnostic has required fields with correct types
and values. Invalid diagnostics are dropped with a warning.

See DIAGNOSTIC_ENGINE.md Section 2 (Validation stage).
"""

from __future__ import annotations

import warnings

from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity


def validate_diagnostic(diag: Diagnostic) -> bool:
    """Validate a diagnostic's fields.

    Checks:
    - rule_id is non-empty.
    - severity is a valid Severity enum member.
    - message is non-empty.
    - file_path is non-empty.
    - line is a positive integer.
    - category is a valid Category enum member.

    Args:
        diag: The diagnostic to validate.

    Returns:
        True if valid, False otherwise. Invalid diagnostics emit
        a warning describing the issue.
    """
    if not diag.rule_id or not isinstance(diag.rule_id, str):
        warnings.warn(
            f"Invalid diagnostic: rule_id must be a non-empty string, "
            f"got {diag.rule_id!r}. Dropping.",
            stacklevel=2,
        )
        return False

    if not isinstance(diag.severity, Severity):
        warnings.warn(
            f"Invalid diagnostic from rule {diag.rule_id}: "
            f"severity must be a Severity enum, got {type(diag.severity).__name__}. "
            f"Dropping.",
            stacklevel=2,
        )
        return False

    if not diag.message or not isinstance(diag.message, str):
        warnings.warn(
            f"Invalid diagnostic from rule {diag.rule_id}: "
            f"message must be a non-empty string. Dropping.",
            stacklevel=2,
        )
        return False

    if not diag.file_path or not isinstance(diag.file_path, str):
        warnings.warn(
            f"Invalid diagnostic from rule {diag.rule_id}: "
            f"file_path must be a non-empty string. Dropping.",
            stacklevel=2,
        )
        return False

    if not isinstance(diag.line, int) or diag.line < 1:
        warnings.warn(
            f"Invalid diagnostic from rule {diag.rule_id}: "
            f"line must be a positive integer, got {diag.line}. Dropping.",
            stacklevel=2,
        )
        return False

    if not isinstance(diag.category, Category):
        warnings.warn(
            f"Invalid diagnostic from rule {diag.rule_id}: "
            f"category must be a Category enum, got {type(diag.category).__name__}. "
            f"Dropping.",
            stacklevel=2,
        )
        return False

    return True


def validate_diagnostics(
    diagnostics: list[Diagnostic],
) -> list[Diagnostic]:
    """Filter a list of diagnostics, keeping only valid ones.

    Args:
        diagnostics: Raw diagnostics from rule execution.

    Returns:
        List of valid diagnostics. Invalid ones are dropped with
        a warning.
    """
    return [d for d in diagnostics if validate_diagnostic(d)]


__all__ = [
    "validate_diagnostic",
    "validate_diagnostics",
]
