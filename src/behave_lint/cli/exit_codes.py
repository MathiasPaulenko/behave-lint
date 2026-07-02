"""Exit code manager — determines exit codes per SPECIFICATION.md Section 10.

Exit codes:
    0 — No diagnostics at or above the failure severity.
    1 — Diagnostics at or above the failure severity (default: warning).
    2 — Internal error (configuration error, parse error, unexpected exception).
    3 — Internal error (unexpected failure, indicates a bug).

See SPECIFICATION.md Section 10 and constants.py.
"""

from __future__ import annotations

from behave_lint.constants import (
    EXIT_CODE_CONFIG_ERROR,
    EXIT_CODE_INTERNAL_ERROR,
    EXIT_CODE_SUCCESS,
    EXIT_CODE_USER_ERROR,
)
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Severity


def determine_exit_code(
    diagnostics: list[Diagnostic],
    fail_on: Severity = Severity.WARNING,
) -> int:
    """Determine the exit code based on diagnostics and failure threshold.

    Args:
        diagnostics: List of diagnostics from the lint run.
        fail_on: Minimum severity that causes non-zero exit.
            Severity.OFF means never fail (always return 0).

    Returns:
        0 if no diagnostics at or above fail_on, 1 otherwise.
    """
    if fail_on == Severity.OFF:
        return EXIT_CODE_SUCCESS

    severity_order = {
        Severity.OFF: 0,
        Severity.INFO: 1,
        Severity.WARNING: 2,
        Severity.ERROR: 3,
    }

    threshold = severity_order.get(fail_on, 2)

    for diag in diagnostics:
        if severity_order.get(diag.severity, 0) >= threshold:
            return EXIT_CODE_USER_ERROR

    return EXIT_CODE_SUCCESS


def config_error_exit_code() -> int:
    """Exit code for configuration errors.

    Returns:
        2 (EXIT_CODE_CONFIG_ERROR).
    """
    return EXIT_CODE_CONFIG_ERROR


def internal_error_exit_code() -> int:
    """Exit code for internal errors.

    Returns:
        3 (EXIT_CODE_INTERNAL_ERROR).
    """
    return EXIT_CODE_INTERNAL_ERROR


__all__ = [
    "config_error_exit_code",
    "determine_exit_code",
    "internal_error_exit_code",
]
