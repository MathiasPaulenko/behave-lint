"""Tests for auto-fix on BP001, BP005, BP006 pedantic rules."""

from __future__ import annotations

from pathlib import Path

import pytest

from behave_lint.cli.coordinator import main

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def no_tags_file(tmp_path: Path) -> Path:
    """Feature file with scenarios without tags."""
    f = tmp_path / "no_tags.feature"
    f.write_text(
        "Feature: Test\n\n"
        "  Scenario: Login\n"
        "    Given a user\n"
        "    When the user logs in\n"
        "    Then the dashboard is visible\n",
        encoding="utf-8",
    )
    return f


@pytest.fixture
def no_examples_name_file(tmp_path: Path) -> Path:
    """Feature file with unnamed Examples section."""
    f = tmp_path / "no_examples_name.feature"
    f.write_text(
        "Feature: Test\n\n"
        "  Scenario Outline: Login <role>\n"
        "    Given a <role> user\n"
        "    When the user logs in\n"
        "    Then the dashboard is visible\n\n"
        "    Examples:\n"
        "      | role |\n"
        "      | admin |\n"
        "      | guest |\n",
        encoding="utf-8",
    )
    return f


@pytest.fixture
def no_feature_description_file(tmp_path: Path) -> Path:
    """Feature file without a description."""
    f = tmp_path / "no_desc.feature"
    f.write_text(
        "Feature: User Authentication\n\n"
        "  Scenario: Login\n"
        "    Given a user\n"
        "    When the user logs in\n"
        "    Then the dashboard is visible\n",
        encoding="utf-8",
    )
    return f


# ---------------------------------------------------------------------------
# BP001 — Missing scenario tags auto-fix (UNSAFE)
# ---------------------------------------------------------------------------


class TestBP001MissingTagsFix:
    """Tests for BP001 missing scenario tags auto-fix."""

    def test_fix_adds_smoke_tag_with_unsafe(self, no_tags_file: Path) -> None:
        main(
            [
                "--fix",
                "--unsafe-fixes",
                "--select",
                "BP001",
                str(no_tags_file),
            ]
        )
        content = no_tags_file.read_text(encoding="utf-8")
        assert "@smoke" in content
        lines = content.splitlines()
        tag_lines = [line for line in lines if line.strip() == "@smoke"]
        assert len(tag_lines) == 1

    def test_fix_not_applied_without_unsafe_flag(self, no_tags_file: Path) -> None:
        original = no_tags_file.read_text(encoding="utf-8")
        main(["--fix", "--select", "BP001", str(no_tags_file)])
        assert no_tags_file.read_text(encoding="utf-8") == original

    def test_no_fix_without_flag(self, no_tags_file: Path) -> None:
        original = no_tags_file.read_text(encoding="utf-8")
        main(["--select", "BP001", str(no_tags_file)])
        assert no_tags_file.read_text(encoding="utf-8") == original

    def test_fix_preserves_indentation(self, no_tags_file: Path) -> None:
        main(
            [
                "--fix",
                "--unsafe-fixes",
                "--select",
                "BP001",
                str(no_tags_file),
            ]
        )
        content = no_tags_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        for line in lines:
            if line.strip() == "@smoke":
                assert line.startswith("  ")


# ---------------------------------------------------------------------------
# BP005 — Missing examples name auto-fix (UNSAFE)
# ---------------------------------------------------------------------------


class TestBP005MissingExamplesNameFix:
    """Tests for BP005 missing examples name auto-fix."""

    def test_fix_adds_name_with_unsafe(self, no_examples_name_file: Path) -> None:
        main(
            [
                "--fix",
                "--unsafe-fixes",
                "--select",
                "BP005",
                str(no_examples_name_file),
            ]
        )
        content = no_examples_name_file.read_text(encoding="utf-8")
        assert "Examples: Valid values" in content
        assert "Examples:\n" not in content

    def test_fix_not_applied_without_unsafe_flag(
        self, no_examples_name_file: Path
    ) -> None:
        original = no_examples_name_file.read_text(encoding="utf-8")
        main(["--fix", "--select", "BP005", str(no_examples_name_file)])
        assert no_examples_name_file.read_text(encoding="utf-8") == original

    def test_no_fix_without_flag(self, no_examples_name_file: Path) -> None:
        original = no_examples_name_file.read_text(encoding="utf-8")
        main(["--select", "BP005", str(no_examples_name_file)])
        assert no_examples_name_file.read_text(encoding="utf-8") == original


# ---------------------------------------------------------------------------
# BP006 — Missing feature description auto-fix (UNSAFE)
# ---------------------------------------------------------------------------


class TestBP006MissingFeatureDescriptionFix:
    """Tests for BP006 missing feature description auto-fix."""

    def test_fix_adds_description_with_unsafe(
        self, no_feature_description_file: Path
    ) -> None:
        main(
            [
                "--fix",
                "--unsafe-fixes",
                "--select",
                "BP006",
                str(no_feature_description_file),
            ]
        )
        content = no_feature_description_file.read_text(encoding="utf-8")
        assert "As a [role]" in content
        assert "I want to [action]" in content
        assert "So that [benefit]" in content

    def test_fix_not_applied_without_unsafe_flag(
        self, no_feature_description_file: Path
    ) -> None:
        original = no_feature_description_file.read_text(encoding="utf-8")
        main(["--fix", "--select", "BP006", str(no_feature_description_file)])
        assert no_feature_description_file.read_text(encoding="utf-8") == original

    def test_no_fix_without_flag(self, no_feature_description_file: Path) -> None:
        original = no_feature_description_file.read_text(encoding="utf-8")
        main(["--select", "BP006", str(no_feature_description_file)])
        assert no_feature_description_file.read_text(encoding="utf-8") == original

    def test_fix_inserts_after_feature_line(
        self, no_feature_description_file: Path
    ) -> None:
        main(
            [
                "--fix",
                "--unsafe-fixes",
                "--select",
                "BP006",
                str(no_feature_description_file),
            ]
        )
        content = no_feature_description_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        feature_idx = next(
            i for i, line in enumerate(lines) if line.startswith("Feature:")
        )
        assert "As a [role]" in lines[feature_idx + 1]
