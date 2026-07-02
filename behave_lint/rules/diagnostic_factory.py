"""Diagnostic factory — creates diagnostics with rule metadata pre-filled.

The factory ensures that diagnostics are always correctly attributed to
the producing rule and have consistent metadata (rule_id, category,
severity).

See RULE_ENGINE.md Section 8 and API.md Section 7.
"""

from __future__ import annotations

from typing import Protocol

from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity


class HasLocation(Protocol):
    """Protocol for objects that provide file location info.

    A behave-model node (Feature, Scenario, Step, etc.) is expected to
    have ``file_path`` and ``line`` attributes. This protocol allows
    the factory to accept any such object without depending on
    behave-model at type-check time.
    """

    file_path: str
    line: int

    @property
    def column(self) -> int | None: ...


class DiagnosticFactory:
    """Factory for creating diagnostics with rule metadata pre-filled.

    Attributes:
        rule_id: The rule ID to stamp on each diagnostic.
        category: The category to stamp on each diagnostic.
        severity: The effective severity (after overrides).
        file_path: Default file path (for single-file rules).
    """

    __slots__ = ("category", "file_path", "rule_id", "severity")

    def __init__(
        self,
        rule_id: str,
        category: Category,
        severity: Severity,
        file_path: str | None = None,
    ) -> None:
        """Initialize the factory.

        Args:
            rule_id: The rule ID to stamp on diagnostics.
            category: The category to stamp on diagnostics.
            severity: The effective severity for diagnostics.
            file_path: Default file path (used if node has no file_path).
        """
        self.rule_id = rule_id
        self.category = category
        self.severity = severity
        self.file_path = file_path

    def create(
        self,
        message: str,
        node: HasLocation | None = None,
        *,
        line: int | None = None,
        column: int | None = None,
        file_path: str | None = None,
        end_line: int | None = None,
        end_column: int | None = None,
        suggestion: str | None = None,
        doc_url: str | None = None,
    ) -> Diagnostic:
        """Create a diagnostic with rule metadata pre-filled.

        Location is determined from (in order of precedence):
        1. Explicit ``line``/``column``/``file_path`` arguments.
        2. The ``node`` parameter (if provided).
        3. The factory's default ``file_path``.

        Args:
            message: What is wrong (factual statement).
            node: A behave-model element with file_path and line.
            line: Explicit line number (overrides node).
            column: Explicit column number (overrides node).
            file_path: Explicit file path (overrides node and factory).
            end_line: End line of the diagnostic range.
            end_column: End column of the diagnostic range.
            suggestion: How to fix it (actionable guidance).
            doc_url: URL to rule documentation.

        Returns:
            A Diagnostic with rule_id, category, and severity pre-filled.
        """
        # Resolve line
        resolved_line = line
        if resolved_line is None and node is not None:
            resolved_line = getattr(node, "line", None)
            if resolved_line is None:
                loc = getattr(node, "location", None)
                if loc is not None:
                    resolved_line = getattr(loc, "line", None)
        if not resolved_line:
            resolved_line = 1

        # Resolve column
        resolved_column = column
        if resolved_column is None and node is not None:
            resolved_column = getattr(node, "column", None)

        # Resolve file_path
        resolved_path = file_path
        if not resolved_path and node is not None:
            resolved_path = getattr(node, "file_path", None)
        if not resolved_path and node is not None:
            loc = getattr(node, "location", None)
            if loc is not None:
                resolved_path = getattr(loc, "filename", None)
        if not resolved_path:
            resolved_path = self.file_path
        if not resolved_path:
            resolved_path = ""

        return Diagnostic(
            rule_id=self.rule_id,
            severity=self.severity,
            message=message,
            file_path=resolved_path,
            line=resolved_line,
            category=self.category,
            column=resolved_column,
            end_line=end_line,
            end_column=end_column,
            suggestion=suggestion,
            doc_url=doc_url,
        )


__all__ = ["DiagnosticFactory", "HasLocation"]
