"""Fix data models — FixEdit and FixResult for the auto-fix system.

FixEdit represents a single text replacement to apply to a .feature file.
FixResult records the outcome of a fix application run.

See RULE_ENGINE.md Section 9 and COMPONENT_DESIGN.md C18.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from behave_lint.models.enums import AutoFixCapability


@dataclass(frozen=True, slots=True)
class FixEdit:
    """A single text edit to apply to a file.

    Attributes:
        file_path: Path to the file to modify.
        start_line: 1-based start line of the region to replace.
        end_line: 1-based end line (inclusive) of the region to replace.
        old_text: The original text being replaced (for validation).
        new_text: The replacement text.
        safety: Whether this is a SAFE or UNSAFE fix.
        rule_id: The rule that produced this fix.
        diagnostic_line: The diagnostic line number that triggered this fix.
    """

    file_path: str
    start_line: int
    end_line: int
    old_text: str
    new_text: str
    safety: AutoFixCapability
    rule_id: str
    diagnostic_line: int

    def __post_init__(self) -> None:
        """Validate field constraints."""
        if self.start_line < 1:
            raise ValueError(f"start_line must be >= 1, got {self.start_line}")
        if self.end_line < self.start_line:
            raise ValueError(
                f"end_line ({self.end_line}) must be >= start_line ({self.start_line})"
            )
        if self.safety is AutoFixCapability.NONE:
            raise ValueError("FixEdit safety must be SAFE or UNSAFE, not NONE")

    @property
    def is_safe(self) -> bool:
        """Whether this fix is safe (does not change semantics).

        Returns:
            True if safety is SAFE, False if UNSAFE.
        """
        return self.safety is AutoFixCapability.SAFE

    @property
    def line_span(self) -> int:
        """Number of lines spanned by this edit (inclusive).

        Returns:
            The number of lines from start_line to end_line.
        """
        return self.end_line - self.start_line + 1


@dataclass(frozen=True, slots=True)
class FixRecord:
    """Record of a single fix application attempt.

    Attributes:
        edit: The fix edit that was processed.
        status: "applied", "skipped", or "failed".
        reason: Why the fix was skipped or failed, or None if applied.
    """

    edit: FixEdit
    status: str
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class FixResult:
    """Outcome of a fix application run.

    Attributes:
        records: List of fix records (applied, skipped, failed).
        files_modified: Set of file paths that were modified.
        applied_count: Number of fixes applied.
        skipped_count: Number of fixes skipped (conflicts).
        failed_count: Number of fixes that failed (errors).
    """

    records: list[FixRecord] = field(default_factory=list)
    files_modified: frozenset[str] = frozenset()
    applied_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0

    @property
    def total(self) -> int:
        """Total number of fix attempts.

        Returns:
            The sum of applied, skipped, and failed counts.
        """
        return self.applied_count + self.skipped_count + self.failed_count

    @property
    def has_fixes(self) -> bool:
        """Whether any fixes were applied.

        Returns:
            True if at least one fix was applied.
        """
        return self.applied_count > 0


__all__ = ["FixEdit", "FixRecord", "FixResult"]
