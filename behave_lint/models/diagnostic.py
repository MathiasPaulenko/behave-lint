"""Diagnostic data model — represents a single issue found by a rule.

A Diagnostic is an immutable frozen dataclass created by rules during
execution. It is consumed by reporters for output and never modified
by the engine.

See API.md Section 4 and DIAGNOSTIC_ENGINE.md Section 3.
"""

from __future__ import annotations

from dataclasses import dataclass

from behave_lint.models.enums import Category, Severity


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """A single issue found by a rule.

    Attributes:
        rule_id: Stable rule identifier (e.g., "BC001").
        severity: Severity level (effective, after user overrides).
        message: Human-readable description of the issue.
        file_path: Path to the .feature file.
        line: 1-based line number where the issue starts.
        column: 1-based column number, or None.
        end_line: End line for multi-line issues, or None.
        end_column: End column for multi-line issues, or None.
        suggestion: Human-readable fix suggestion, or None.
        doc_url: URL to rule documentation, or None.
        category: Rule category.
    """

    rule_id: str
    severity: Severity
    message: str
    file_path: str
    line: int
    category: Category
    column: int | None = None
    end_line: int | None = None
    end_column: int | None = None
    suggestion: str | None = None
    doc_url: str | None = None

    def __post_init__(self) -> None:
        """Validate field constraints after initialization."""
        if self.line < 1:
            raise ValueError(f"line must be >= 1, got {self.line}")
        if self.column is not None and self.column < 1:
            raise ValueError(f"column must be >= 1, got {self.column}")
        if self.end_line is not None and self.end_line < self.line:
            raise ValueError(
                f"end_line ({self.end_line}) must be >= line ({self.line})"
            )
        if self.end_column is not None and self.column is None:
            raise ValueError("end_column requires column to be set")

    @property
    def location(self) -> str:
        """Formatted location string for display.

        Returns:
            A string like "features/login.feature:15:3" or
            "features/login.feature:15".
        """
        if self.column is not None:
            return f"{self.file_path}:{self.line}:{self.column}"
        return f"{self.file_path}:{self.line}"

    @property
    def is_error(self) -> bool:
        """Whether this diagnostic has ERROR severity.

        Returns:
            True if severity is ERROR, False otherwise.
        """
        return self.severity is Severity.ERROR

    @property
    def is_warning(self) -> bool:
        """Whether this diagnostic has WARNING severity.

        Returns:
            True if severity is WARNING, False otherwise.
        """
        return self.severity is Severity.WARNING

    @property
    def is_info(self) -> bool:
        """Whether this diagnostic has INFO severity.

        Returns:
            True if severity is INFO, False otherwise.
        """
        return self.severity is Severity.INFO


__all__ = ["Diagnostic"]
