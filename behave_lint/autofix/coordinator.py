"""Fix coordinator — collects, orders, conflict-checks, and applies fixes.

Collects fixable diagnostics from rules, orders them by file (bottom-to-top)
and rule execution order, detects conflicts (overlapping line ranges), and
applies non-conflicting fixes atomically per file. Supports --fix (safe only)
and --unsafe-fixes (safe + unsafe). Dry-run mode previews without writing.

See RULE_ENGINE.md Section 9 and COMPONENT_DESIGN.md C18.
"""

from __future__ import annotations

import logging
from pathlib import Path

from behave_lint.autofix.models import FixEdit, FixRecord, FixResult
from behave_lint.models.enums import AutoFixCapability

logger = logging.getLogger(__name__)


def _edits_conflict(a: FixEdit, b: FixEdit) -> bool:
    """Check if two edits to the same file have overlapping line ranges.

    Args:
        a: First edit.
        b: Second edit.

    Returns:
        True if the line ranges overlap, False otherwise.
    """
    return not (a.end_line < b.start_line or b.end_line < a.start_line)


class FixCoordinator:
    """Coordinates fix collection, conflict detection, and application.

    Attributes:
        _allow_unsafe: Whether unsafe fixes are allowed.
        _dry_run: Whether to preview without writing files.
    """

    def __init__(
        self,
        allow_unsafe: bool = False,
        dry_run: bool = False,
    ) -> None:
        """Initialize the fix coordinator.

        Args:
            allow_unsafe: If True, apply both safe and unsafe fixes.
                If False, apply only safe fixes.
            dry_run: If True, compute fixes but do not write files.
        """
        self._allow_unsafe = allow_unsafe
        self._dry_run = dry_run

    def filter_edits(self, edits: list[FixEdit]) -> list[FixEdit]:
        """Filter edits by safety level.

        Args:
            edits: All collected edits.

        Returns:
            Edits that pass the safety filter.
        """
        if self._allow_unsafe:
            return [
                e
                for e in edits
                if e.safety in (AutoFixCapability.SAFE, AutoFixCapability.UNSAFE)
            ]
        return [e for e in edits if e.safety is AutoFixCapability.SAFE]

    def resolve_conflicts(
        self, edits: list[FixEdit]
    ) -> tuple[list[FixEdit], list[FixRecord]]:
        """Detect and resolve conflicts among edits.

        Edits are ordered by file, then bottom-to-top (highest line first),
        then by rule_id. The first edit for a location wins; subsequent
        overlapping edits are skipped.

        Args:
            edits: Filtered edits to resolve.

        Returns:
            A tuple of (non_conflicting_edits, skipped_records).
        """
        ordered = sorted(
            edits,
            key=lambda e: (e.file_path, -e.start_line, e.rule_id),
        )

        accepted: list[FixEdit] = []
        skipped: list[FixRecord] = []
        occupied: list[FixEdit] = []

        for edit in ordered:
            conflict = None
            for existing in occupied:
                if existing.file_path != edit.file_path:
                    continue
                if _edits_conflict(existing, edit):
                    conflict = existing
                    break

            if conflict is not None:
                skipped.append(
                    FixRecord(
                        edit=edit,
                        status="skipped",
                        reason=(
                            f"Conflicts with fix from '{conflict.rule_id}' "
                            f"at lines {conflict.start_line}-{conflict.end_line}"
                        ),
                    )
                )
            else:
                accepted.append(edit)
                occupied.append(edit)

        return accepted, skipped

    def apply_edits(self, edits: list[FixEdit]) -> FixResult:
        """Apply a list of edits to files.

        Edits are filtered by safety, conflicts are resolved, and
        non-conflicting edits are applied atomically per file.

        Args:
            edits: All collected edits.

        Returns:
            A FixResult with applied, skipped, and failed records.
        """
        filtered = self.filter_edits(edits)
        accepted, skipped = self.resolve_conflicts(filtered)

        records: list[FixRecord] = list(skipped)
        modified_files: set[str] = set()
        applied_count = 0
        failed_count = 0

        # Group accepted edits by file
        by_file: dict[str, list[FixEdit]] = {}
        for edit in accepted:
            by_file.setdefault(edit.file_path, []).append(edit)

        for file_path, file_edits in sorted(by_file.items()):
            file_records, file_modified = self._apply_to_file(file_path, file_edits)
            records.extend(file_records)
            if file_modified:
                modified_files.add(file_path)

        for record in records:
            if record.status == "applied":
                applied_count += 1
            elif record.status == "failed":
                failed_count += 1

        return FixResult(
            records=records,
            files_modified=frozenset(modified_files),
            applied_count=applied_count,
            skipped_count=len(skipped),
            failed_count=failed_count,
        )

    def _apply_to_file(
        self, file_path: str, edits: list[FixEdit]
    ) -> tuple[list[FixRecord], bool]:
        """Apply edits to a single file atomically.

        Args:
            file_path: Path to the file.
            edits: Edits for this file (already conflict-free, bottom-to-top).

        Returns:
            A tuple of (records, file_was_modified).
        """
        path = Path(file_path)

        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("Failed to read '%s': %s", file_path, exc)
            return [
                FixRecord(edit=e, status="failed", reason=str(exc)) for e in edits
            ], False

        lines = content.splitlines(keepends=True)
        records: list[FixRecord] = []
        modified = False

        # Edits are already sorted bottom-to-top, so applying in order
        # doesn't shift line numbers for subsequent edits.
        for edit in sorted(edits, key=lambda e: -e.start_line):
            start_idx = edit.start_line - 1
            end_idx = edit.end_line  # end_line is inclusive, slice is exclusive

            if start_idx < 0 or end_idx > len(lines):
                records.append(
                    FixRecord(
                        edit=edit,
                        status="failed",
                        reason=(
                            f"Line range {edit.start_line}-{edit.end_line} "
                            f"out of bounds (file has {len(lines)} lines)"
                        ),
                    )
                )
                continue

            old_slice = "".join(lines[start_idx:end_idx])
            if old_slice != edit.old_text:
                records.append(
                    FixRecord(
                        edit=edit,
                        status="failed",
                        reason=(
                            f"old_text mismatch at lines {edit.start_line}-"
                            f"{edit.end_line}. Expected:\n{edit.old_text!r}\n"
                            f"Found:\n{old_slice!r}"
                        ),
                    )
                )
                continue

            lines[start_idx:end_idx] = (
                edit.new_text.splitlines(keepends=True) if edit.new_text else []
            )
            modified = True
            records.append(FixRecord(edit=edit, status="applied"))

        if modified and not self._dry_run:
            try:
                path.write_text("".join(lines), encoding="utf-8")
            except OSError as exc:
                logger.warning("Failed to write '%s': %s", file_path, exc)
                return [
                    FixRecord(edit=e, status="failed", reason=str(exc)) for e in edits
                ], False

        return records, modified

    @property
    def allow_unsafe(self) -> bool:
        """Whether unsafe fixes are allowed."""
        return self._allow_unsafe

    @property
    def dry_run(self) -> bool:
        """Whether dry-run mode is active."""
        return self._dry_run


__all__ = ["FixCoordinator"]
