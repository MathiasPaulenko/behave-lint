"""Auto-Fix Coordinator — fix collection, conflict detection, application.

Application layer — component C18.
"""

from __future__ import annotations

from behave_lint.autofix.coordinator import FixCoordinator
from behave_lint.autofix.models import FixEdit, FixRecord, FixResult

__all__ = [
    "FixCoordinator",
    "FixEdit",
    "FixRecord",
    "FixResult",
]
