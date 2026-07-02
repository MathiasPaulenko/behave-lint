"""Unit tests for FixEdit, FixRecord, and FixResult data models."""

from __future__ import annotations

import pytest

from behave_lint.autofix.models import FixEdit, FixRecord, FixResult
from behave_lint.models.enums import AutoFixCapability


def _make_edit(
    file_path: str = "features/test.feature",
    start_line: int = 3,
    end_line: int = 3,
    old_text: str = "Given a step\n",
    new_text: str = "Given a fixed step\n",
    safety: AutoFixCapability = AutoFixCapability.SAFE,
    rule_id: str = "BS001",
    diagnostic_line: int = 3,
) -> FixEdit:
    return FixEdit(
        file_path=file_path,
        start_line=start_line,
        end_line=end_line,
        old_text=old_text,
        new_text=new_text,
        safety=safety,
        rule_id=rule_id,
        diagnostic_line=diagnostic_line,
    )


class TestFixEdit:
    """Tests for FixEdit dataclass."""

    def test_basic_creation(self) -> None:
        edit = _make_edit()
        assert edit.file_path == "features/test.feature"
        assert edit.start_line == 3
        assert edit.end_line == 3
        assert edit.old_text == "Given a step\n"
        assert edit.new_text == "Given a fixed step\n"
        assert edit.safety is AutoFixCapability.SAFE
        assert edit.rule_id == "BS001"

    def test_is_safe_true(self) -> None:
        edit = _make_edit(safety=AutoFixCapability.SAFE)
        assert edit.is_safe is True

    def test_is_safe_false(self) -> None:
        edit = _make_edit(safety=AutoFixCapability.UNSAFE)
        assert edit.is_safe is False

    def test_line_span_single(self) -> None:
        edit = _make_edit(start_line=5, end_line=5)
        assert edit.line_span == 1

    def test_line_span_multi(self) -> None:
        edit = _make_edit(start_line=3, end_line=7)
        assert edit.line_span == 5

    def test_frozen(self) -> None:
        edit = _make_edit()
        try:
            edit.file_path = "other"  # type: ignore[misc]
            raise AssertionError("Should have raised")
        except AttributeError:
            pass

    def test_invalid_start_line(self) -> None:
        with pytest.raises(ValueError, match="start_line must be >= 1"):
            _make_edit(start_line=0)

    def test_end_before_start(self) -> None:
        with pytest.raises(ValueError, match="end_line"):
            _make_edit(start_line=5, end_line=3)

    def test_safety_none_raises(self) -> None:
        with pytest.raises(ValueError, match="SAFE or UNSAFE"):
            _make_edit(safety=AutoFixCapability.NONE)


class TestFixRecord:
    """Tests for FixRecord dataclass."""

    def test_applied_record(self) -> None:
        edit = _make_edit()
        record = FixRecord(edit=edit, status="applied")
        assert record.status == "applied"
        assert record.reason is None

    def test_skipped_record(self) -> None:
        edit = _make_edit()
        record = FixRecord(edit=edit, status="skipped", reason="Conflict")
        assert record.status == "skipped"
        assert record.reason == "Conflict"

    def test_failed_record(self) -> None:
        edit = _make_edit()
        record = FixRecord(edit=edit, status="failed", reason="IOError")
        assert record.status == "failed"
        assert record.reason == "IOError"


class TestFixResult:
    """Tests for FixResult dataclass."""

    def test_empty_result(self) -> None:
        result = FixResult()
        assert result.applied_count == 0
        assert result.skipped_count == 0
        assert result.failed_count == 0
        assert result.total == 0
        assert result.has_fixes is False
        assert result.records == []
        assert result.files_modified == frozenset()

    def test_with_applied(self) -> None:
        result = FixResult(
            applied_count=3,
            skipped_count=1,
            failed_count=0,
            files_modified=frozenset({"a.feature", "b.feature"}),
        )
        assert result.total == 4
        assert result.has_fixes is True
        assert len(result.files_modified) == 2

    def test_total_property(self) -> None:
        result = FixResult(applied_count=2, skipped_count=3, failed_count=1)
        assert result.total == 6

    def test_has_fixes_false_when_only_skipped(self) -> None:
        result = FixResult(applied_count=0, skipped_count=2, failed_count=0)
        assert result.has_fixes is False
