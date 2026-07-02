"""Unit tests for the FixCoordinator."""

from __future__ import annotations

from pathlib import Path

from behave_lint.autofix.coordinator import FixCoordinator
from behave_lint.autofix.models import FixEdit
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


class TestFixCoordinatorFiltering:
    """Tests for safety filtering."""

    def test_safe_only_by_default(self) -> None:
        coord = FixCoordinator()
        edits = [
            _make_edit(safety=AutoFixCapability.SAFE, rule_id="S1"),
            _make_edit(safety=AutoFixCapability.UNSAFE, rule_id="U1"),
        ]
        filtered = coord.filter_edits(edits)
        assert len(filtered) == 1
        assert filtered[0].rule_id == "S1"

    def test_unsafe_allowed(self) -> None:
        coord = FixCoordinator(allow_unsafe=True)
        edits = [
            _make_edit(safety=AutoFixCapability.SAFE, rule_id="S1"),
            _make_edit(safety=AutoFixCapability.UNSAFE, rule_id="U1"),
        ]
        filtered = coord.filter_edits(edits)
        assert len(filtered) == 2

    def test_none_filtered_always(self) -> None:
        coord = FixCoordinator(allow_unsafe=True)
        edits = [
            _make_edit(safety=AutoFixCapability.SAFE),
        ]
        filtered = coord.filter_edits(edits)
        assert len(filtered) == 1


class TestFixCoordinatorConflicts:
    """Tests for conflict resolution."""

    def test_no_conflicts(self) -> None:
        coord = FixCoordinator()
        edits = [
            _make_edit(start_line=1, end_line=1, rule_id="R1"),
            _make_edit(start_line=5, end_line=5, rule_id="R2"),
        ]
        accepted, skipped = coord.resolve_conflicts(edits)
        assert len(accepted) == 2
        assert len(skipped) == 0

    def test_overlapping_conflict(self) -> None:
        coord = FixCoordinator()
        edits = [
            _make_edit(start_line=3, end_line=7, rule_id="R1"),
            _make_edit(start_line=5, end_line=10, rule_id="R2"),
        ]
        accepted, skipped = coord.resolve_conflicts(edits)
        assert len(accepted) == 1
        assert len(skipped) == 1
        assert skipped[0].status == "skipped"
        assert "Conflicts" in skipped[0].reason

    def test_adjacent_no_conflict(self) -> None:
        coord = FixCoordinator()
        edits = [
            _make_edit(start_line=1, end_line=3, rule_id="R1"),
            _make_edit(start_line=4, end_line=6, rule_id="R2"),
        ]
        accepted, skipped = coord.resolve_conflicts(edits)
        assert len(accepted) == 2
        assert len(skipped) == 0

    def test_different_files_no_conflict(self) -> None:
        coord = FixCoordinator()
        edits = [
            _make_edit(file_path="a.feature", start_line=3, end_line=3),
            _make_edit(file_path="b.feature", start_line=3, end_line=3),
        ]
        accepted, skipped = coord.resolve_conflicts(edits)
        assert len(accepted) == 2
        assert len(skipped) == 0

    def test_first_fix_wins(self) -> None:
        coord = FixCoordinator()
        edits = [
            _make_edit(start_line=5, end_line=5, rule_id="AAA"),
            _make_edit(start_line=5, end_line=5, rule_id="BBB"),
        ]
        accepted, skipped = coord.resolve_conflicts(edits)
        assert len(accepted) == 1
        assert accepted[0].rule_id == "AAA"
        assert len(skipped) == 1
        assert skipped[0].edit.rule_id == "BBB"

    def test_three_overlapping(self) -> None:
        coord = FixCoordinator()
        edits = [
            _make_edit(start_line=3, end_line=8, rule_id="R1"),
            _make_edit(start_line=5, end_line=6, rule_id="R2"),
            _make_edit(start_line=7, end_line=10, rule_id="R3"),
        ]
        accepted, skipped = coord.resolve_conflicts(edits)
        # Bottom-to-top: R3 (7-10) accepted, R2 (5-6) no conflict, R1 (3-8) conflicts
        assert len(accepted) == 2
        assert len(skipped) == 1
        assert skipped[0].edit.rule_id == "R1"


class TestFixCoordinatorApply:
    """Tests for applying edits to files."""

    def test_apply_single_edit(self, tmp_path: Path) -> None:
        feature = tmp_path / "test.feature"
        feature.write_text("Feature: Test\n\nGiven a step\n", encoding="utf-8")

        coord = FixCoordinator()
        edit = FixEdit(
            file_path=str(feature),
            start_line=3,
            end_line=3,
            old_text="Given a step\n",
            new_text="Given a fixed step\n",
            safety=AutoFixCapability.SAFE,
            rule_id="BS001",
            diagnostic_line=3,
        )
        result = coord.apply_edits([edit])
        assert result.applied_count == 1
        assert result.failed_count == 0
        assert str(feature) in result.files_modified
        content = feature.read_text(encoding="utf-8")
        assert "Given a fixed step" in content

    def test_apply_multiple_non_conflicting(self, tmp_path: Path) -> None:
        feature = tmp_path / "test.feature"
        feature.write_text(
            "Feature: Test\n\nLine A\nLine B\nLine C\n", encoding="utf-8"
        )

        coord = FixCoordinator()
        edits = [
            FixEdit(
                file_path=str(feature),
                start_line=3,
                end_line=3,
                old_text="Line A\n",
                new_text="Fixed A\n",
                safety=AutoFixCapability.SAFE,
                rule_id="R1",
                diagnostic_line=3,
            ),
            FixEdit(
                file_path=str(feature),
                start_line=5,
                end_line=5,
                old_text="Line C\n",
                new_text="Fixed C\n",
                safety=AutoFixCapability.SAFE,
                rule_id="R2",
                diagnostic_line=5,
            ),
        ]
        result = coord.apply_edits(edits)
        assert result.applied_count == 2
        content = feature.read_text(encoding="utf-8")
        assert "Fixed A" in content
        assert "Fixed C" in content

    def test_dry_run_does_not_write(self, tmp_path: Path) -> None:
        feature = tmp_path / "test.feature"
        original = "Feature: Test\n\nGiven a step\n"
        feature.write_text(original, encoding="utf-8")

        coord = FixCoordinator(dry_run=True)
        edit = _make_edit(
            file_path=str(feature),
            old_text="Given a step\n",
            new_text="Given a fixed step\n",
        )
        result = coord.apply_edits([edit])
        assert result.applied_count == 1
        content = feature.read_text(encoding="utf-8")
        assert content == original

    def test_old_text_mismatch(self, tmp_path: Path) -> None:
        feature = tmp_path / "test.feature"
        feature.write_text("Feature: Test\n\nDifferent text\n", encoding="utf-8")

        coord = FixCoordinator()
        edit = _make_edit(
            file_path=str(feature),
            old_text="Given a step\n",
            new_text="Given a fixed step\n",
        )
        result = coord.apply_edits([edit])
        assert result.applied_count == 0
        assert result.failed_count == 1
        assert result.records[0].status == "failed"
        assert "mismatch" in result.records[0].reason

    def test_unsafe_filtered_out(self, tmp_path: Path) -> None:
        feature = tmp_path / "test.feature"
        feature.write_text("Feature: Test\n\nGiven a step\n", encoding="utf-8")

        coord = FixCoordinator(allow_unsafe=False)
        edit = _make_edit(
            file_path=str(feature),
            safety=AutoFixCapability.UNSAFE,
        )
        result = coord.apply_edits([edit])
        assert result.applied_count == 0
        assert result.total == 0

    def test_unsafe_allowed(self, tmp_path: Path) -> None:
        feature = tmp_path / "test.feature"
        feature.write_text("Feature: Test\n\nGiven a step\n", encoding="utf-8")

        coord = FixCoordinator(allow_unsafe=True)
        edit = _make_edit(
            file_path=str(feature),
            safety=AutoFixCapability.UNSAFE,
        )
        result = coord.apply_edits([edit])
        assert result.applied_count == 1

    def test_conflict_skipped(self, tmp_path: Path) -> None:
        feature = tmp_path / "test.feature"
        feature.write_text("Feature: Test\n\nLine A\n", encoding="utf-8")

        coord = FixCoordinator()
        edits = [
            FixEdit(
                file_path=str(feature),
                start_line=3,
                end_line=3,
                old_text="Line A\n",
                new_text="Fixed A\n",
                safety=AutoFixCapability.SAFE,
                rule_id="R1",
                diagnostic_line=3,
            ),
            FixEdit(
                file_path=str(feature),
                start_line=3,
                end_line=3,
                old_text="Line A\n",
                new_text="Also Fixed A\n",
                safety=AutoFixCapability.SAFE,
                rule_id="R2",
                diagnostic_line=3,
            ),
        ]
        result = coord.apply_edits(edits)
        assert result.applied_count == 1
        assert result.skipped_count == 1

    def test_nonexistent_file(self) -> None:
        coord = FixCoordinator()
        edit = _make_edit(file_path="nonexistent_file_xyz.feature")
        result = coord.apply_edits([edit])
        assert result.failed_count == 1
        assert result.applied_count == 0

    def test_multi_line_edit(self, tmp_path: Path) -> None:
        feature = tmp_path / "test.feature"
        feature.write_text(
            "Feature: Test\n\nScenario: Old\nGiven step\n", encoding="utf-8"
        )

        coord = FixCoordinator()
        edit = FixEdit(
            file_path=str(feature),
            start_line=3,
            end_line=4,
            old_text="Scenario: Old\nGiven step\n",
            new_text="Scenario: New\nGiven fixed step\n",
            safety=AutoFixCapability.SAFE,
            rule_id="R1",
            diagnostic_line=3,
        )
        result = coord.apply_edits([edit])
        assert result.applied_count == 1
        content = feature.read_text(encoding="utf-8")
        assert "Scenario: New" in content
        assert "Given fixed step" in content

    def test_properties(self) -> None:
        coord = FixCoordinator(allow_unsafe=True, dry_run=True)
        assert coord.allow_unsafe is True
        assert coord.dry_run is True

    def test_empty_edits(self) -> None:
        coord = FixCoordinator()
        result = coord.apply_edits([])
        assert result.applied_count == 0
        assert result.skipped_count == 0
        assert result.failed_count == 0
        assert result.has_fixes is False

    def test_multiple_files(self, tmp_path: Path) -> None:
        file_a = tmp_path / "a.feature"
        file_b = tmp_path / "b.feature"
        file_a.write_text("Feature: A\n\nLine A\n", encoding="utf-8")
        file_b.write_text("Feature: B\n\nLine B\n", encoding="utf-8")

        coord = FixCoordinator()
        edits = [
            FixEdit(
                file_path=str(file_a),
                start_line=3,
                end_line=3,
                old_text="Line A\n",
                new_text="Fixed A\n",
                safety=AutoFixCapability.SAFE,
                rule_id="R1",
                diagnostic_line=3,
            ),
            FixEdit(
                file_path=str(file_b),
                start_line=3,
                end_line=3,
                old_text="Line B\n",
                new_text="Fixed B\n",
                safety=AutoFixCapability.SAFE,
                rule_id="R2",
                diagnostic_line=3,
            ),
        ]
        result = coord.apply_edits(edits)
        assert result.applied_count == 2
        assert len(result.files_modified) == 2
