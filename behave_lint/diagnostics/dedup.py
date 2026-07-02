"""Diagnostic deduplication — remove duplicate diagnostics.

Deduplication removes diagnostics that are exact duplicates:
same rule_id, same file_path, same line, same column, same message.

See DIAGNOSTIC_ENGINE.md Section 8 (deduplication is optional but
designed for v1).
"""

from __future__ import annotations

from behave_lint.models.diagnostic import Diagnostic


def deduplicate_diagnostics(
    diagnostics: list[Diagnostic],
) -> list[Diagnostic]:
    """Remove duplicate diagnostics.

    A diagnostic is a duplicate if another diagnostic with the same
    (rule_id, file_path, line, column, message) already exists.
    The first occurrence is kept; subsequent duplicates are dropped.

    Args:
        diagnostics: List of diagnostics (may contain duplicates).

    Returns:
        List with duplicates removed, preserving order of first
        occurrence.
    """
    seen: set[tuple[str, str, int, int | None, str]] = set()
    result: list[Diagnostic] = []
    for diag in diagnostics:
        key = (
            diag.rule_id,
            diag.file_path,
            diag.line,
            diag.column,
            diag.message,
        )
        if key not in seen:
            seen.add(key)
            result.append(diag)
    return result


__all__ = ["deduplicate_diagnostics"]
