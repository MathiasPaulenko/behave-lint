"""Unit tests for file discovery (C10)."""

from __future__ import annotations

from pathlib import Path

from behave_lint.infrastructure.file_discovery import discover_files


class TestDiscoverFiles:
    """Tests for discover_files."""

    def test_empty_paths(self, tmp_path: Path) -> None:
        result = discover_files([])
        assert result == []

    def test_nonexistent_path(self) -> None:
        result = discover_files(["nonexistent_xyz"])
        assert result == []

    def test_single_feature_file(self, tmp_path: Path) -> None:
        feature = tmp_path / "test.feature"
        feature.write_text("Feature: Test\n", encoding="utf-8")
        result = discover_files([str(feature)])
        assert len(result) == 1
        assert result[0] == str(feature)

    def test_directory_with_features(self, tmp_path: Path) -> None:
        (tmp_path / "a.feature").write_text("Feature: A\n", encoding="utf-8")
        (tmp_path / "b.feature").write_text("Feature: B\n", encoding="utf-8")
        result = discover_files([str(tmp_path)])
        assert len(result) == 2

    def test_ignores_non_feature_files(self, tmp_path: Path) -> None:
        (tmp_path / "test.feature").write_text("Feature: Test\n", encoding="utf-8")
        (tmp_path / "readme.md").write_text("# Readme\n", encoding="utf-8")
        (tmp_path / "script.py").write_text("print('hi')\n", encoding="utf-8")
        result = discover_files([str(tmp_path)])
        assert len(result) == 1
        assert result[0].endswith("test.feature")

    def test_nested_directories(self, tmp_path: Path) -> None:
        sub = tmp_path / "sub" / "deep"
        sub.mkdir(parents=True)
        (sub / "nested.feature").write_text("Feature: Nested\n", encoding="utf-8")
        (tmp_path / "top.feature").write_text("Feature: Top\n", encoding="utf-8")
        result = discover_files([str(tmp_path)])
        assert len(result) == 2

    def test_exclude_pattern(self, tmp_path: Path) -> None:
        vendor = tmp_path / "vendor"
        vendor.mkdir()
        (vendor / "vendor.feature").write_text("Feature: Vendor\n", encoding="utf-8")
        (tmp_path / "main.feature").write_text("Feature: Main\n", encoding="utf-8")
        result = discover_files(
            [str(tmp_path)],
            exclude=["**/vendor/**"],
        )
        assert len(result) == 1
        assert result[0].endswith("main.feature")

    def test_exclude_filename_pattern(self, tmp_path: Path) -> None:
        (tmp_path / "test.feature").write_text("Feature: Test\n", encoding="utf-8")
        (tmp_path / "ignored.feature").write_text(
            "Feature: Ignored\n", encoding="utf-8"
        )
        result = discover_files(
            [str(tmp_path)],
            exclude=["ignored.feature"],
        )
        assert len(result) == 1
        assert result[0].endswith("test.feature")

    def test_sorted_output(self, tmp_path: Path) -> None:
        (tmp_path / "c.feature").write_text("Feature: C\n", encoding="utf-8")
        (tmp_path / "a.feature").write_text("Feature: A\n", encoding="utf-8")
        (tmp_path / "b.feature").write_text("Feature: B\n", encoding="utf-8")
        result = discover_files([str(tmp_path)])
        assert len(result) == 3
        assert result[0].endswith("a.feature")
        assert result[1].endswith("b.feature")
        assert result[2].endswith("c.feature")

    def test_mixed_files_and_dirs(self, tmp_path: Path) -> None:
        subdir = tmp_path / "sub"
        subdir.mkdir()
        (subdir / "in_dir.feature").write_text("Feature: InDir\n", encoding="utf-8")
        standalone = tmp_path / "standalone.feature"
        standalone.write_text("Feature: Standalone\n", encoding="utf-8")
        result = discover_files([str(standalone), str(subdir)])
        assert len(result) == 2

    def test_deduplicates(self, tmp_path: Path) -> None:
        feature = tmp_path / "test.feature"
        feature.write_text("Feature: Test\n", encoding="utf-8")
        result = discover_files([str(feature), str(tmp_path)])
        assert len(result) == 1
