"""Unit tests for project loader (C11)."""

from __future__ import annotations

from pathlib import Path

from behave_lint.infrastructure.project_loader import (
    LoadResult,
    get_file_path_from_feature,
    get_line_from_feature,
    load_features,
    load_single,
)


class TestLoadSingle:
    """Tests for load_single."""

    def test_load_valid_feature(self, tmp_path: Path) -> None:
        feature_file = tmp_path / "test.feature"
        feature_file.write_text(
            "Feature: Test Feature\n\n  Scenario: A scenario\n    Given a step\n",
            encoding="utf-8",
        )
        feature = load_single(str(feature_file))
        assert feature is not None
        assert feature.name == "Test Feature"

    def test_load_nonexistent_file(self) -> None:
        result = load_single("nonexistent_xyz.feature")
        assert result is None

    def test_load_invalid_feature(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "bad.feature"
        bad_file.write_text("This is not valid Gherkin\n", encoding="utf-8")
        result = load_single(str(bad_file))
        assert result is None


class TestLoadFeatures:
    """Tests for load_features."""

    def test_load_multiple_valid(self, tmp_path: Path) -> None:
        f1 = tmp_path / "f1.feature"
        f1.write_text(
            "Feature: F1\n\n  Scenario: S1\n    Given step\n", encoding="utf-8"
        )
        f2 = tmp_path / "f2.feature"
        f2.write_text(
            "Feature: F2\n\n  Scenario: S2\n    Given step\n", encoding="utf-8"
        )
        result = load_features([str(f1), str(f2)])
        assert len(result.features) == 2
        assert not result.has_errors

    def test_load_with_errors(self, tmp_path: Path) -> None:
        good = tmp_path / "good.feature"
        good.write_text(
            "Feature: Good\n\n  Scenario: S\n    Given step\n", encoding="utf-8"
        )
        bad = tmp_path / "bad.feature"
        bad.write_text("Not valid Gherkin\n", encoding="utf-8")
        result = load_features([str(good), str(bad)])
        assert len(result.features) == 1
        assert result.has_errors
        assert len(result.errors) == 1
        assert result.errors[0][0] == str(bad)

    def test_load_empty_list(self) -> None:
        result = load_features([])
        assert len(result.features) == 0
        assert not result.has_errors

    def test_load_nonexistent_files(self) -> None:
        result = load_features(["nonexistent1.feature", "nonexistent2.feature"])
        assert len(result.features) == 0
        assert result.has_errors
        assert len(result.errors) == 2


class TestLoadResult:
    """Tests for LoadResult."""

    def test_empty_result(self) -> None:
        result = LoadResult()
        assert result.features == []
        assert result.errors == []
        assert not result.has_errors

    def test_with_errors(self) -> None:
        result = LoadResult(errors=[("file.feature", "Parse error")])
        assert result.has_errors


class TestFeatureHelpers:
    """Tests for feature helper functions."""

    def test_get_file_path_from_feature(self, tmp_path: Path) -> None:
        feature_file = tmp_path / "test.feature"
        feature_file.write_text(
            "Feature: Test\n\n  Scenario: S\n    Given step\n",
            encoding="utf-8",
        )
        feature = load_single(str(feature_file))
        assert feature is not None
        path = get_file_path_from_feature(feature)
        assert "test.feature" in path

    def test_get_line_from_feature(self, tmp_path: Path) -> None:
        feature_file = tmp_path / "test.feature"
        feature_file.write_text(
            "Feature: Test\n\n  Scenario: S\n    Given step\n",
            encoding="utf-8",
        )
        feature = load_single(str(feature_file))
        assert feature is not None
        line = get_line_from_feature(feature)
        assert line >= 1

    def test_get_file_path_no_location(self) -> None:
        class FakeFeature:
            location = None

        assert get_file_path_from_feature(FakeFeature()) == ""

    def test_get_line_no_location(self) -> None:
        class FakeFeature:
            location = None

        assert get_line_from_feature(FakeFeature()) == 1
