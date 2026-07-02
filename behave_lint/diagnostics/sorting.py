"""Diagnostic sorting — deterministic sort by file, line, column, rule ID.

The sort order is stable and documented:
1. File path (lexicographic, ascending).
2. Line number (ascending).
3. Column number (ascending, None sorts before any value).
4. Rule ID (lexicographic, ascending).

See DIAGNOSTIC_ENGINE.md Section 9.
"""

from __future__ import annotations

from behave_lint.models.diagnostic import Diagnostic


def _sort_key(diag: Diagnostic) -> tuple[str, int, int, str]:
    """Compute the sort key for a diagnostic.

    Args:
        diag: The diagnostic.

    Returns:
        A tuple of (file_path, line, column, rule_id) for sorting.
        None column is converted to -1 so it sorts before any
        positive column.
    """
    col = diag.column if diag.column is not None else -1
    return (diag.file_path, diag.line, col, diag.rule_id)


def sort_diagnostics(
    diagnostics: list[Diagnostic],
) -> list[Diagnostic]:
    """Sort diagnostics deterministically.

    Sort order: file path, line, column (None first), rule ID.

    Args:
        diagnostics: List of diagnostics.

    Returns:
        A new list sorted deterministically.
    """
    return sorted(diagnostics, key=_sort_key)


__all__ = ["sort_diagnostics"]
