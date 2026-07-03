"""Tests for auto-fix on BS002, BS003, BS005 style rules."""

from __future__ import annotations

from pathlib import Path

import pytest

from behave_lint.cli.coordinator import main
from behave_lint.models.enums import AutoFixCapability

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def phrasing_file(tmp_path: Path) -> Path:
    """Feature file with first-person step phrasing."""
    f = tmp_path / "phrasing.feature"
    f.write_text(
        "Feature: Test\n\n"
        "  Scenario: Login\n"
        "    Given I am on the homepage\n"
        "    When I click the button\n"
        "    Then I see the result\n",
        encoding="utf-8",
    )
    return f


@pytest.fixture
def phrasing_ive_file(tmp_path: Path) -> Path:
    """Feature file with 'I've' phrasing."""
    f = tmp_path / "ive.feature"
    f.write_text(
        "Feature: Test\n\n"
        "  Scenario: Check\n"
        "    Given I've logged in\n"
        "    Then the dashboard loads\n",
        encoding="utf-8",
    )
    return f


@pytest.fixture
def keyword_order_file(tmp_path: Path) -> Path:
    """Feature file with out-of-order step keywords."""
    f = tmp_path / "order.feature"
    f.write_text(
        "Feature: Test\n\n"
        "  Scenario: Reorder me\n"
        "    Then the result is visible\n"
        "    When the action happens\n"
        "    Given a precondition\n",
        encoding="utf-8",
    )
    return f


@pytest.fixture
def keyword_order_with_and_file(tmp_path: Path) -> Path:
    """Feature file with And/But steps between major keywords."""
    f = tmp_path / "order_and.feature"
    f.write_text(
        "Feature: Test\n\n"
        "  Scenario: Reorder with And\n"
        "    Then the result is visible\n"
        "    And the result is saved\n"
        "    When the action happens\n"
        "    Given a precondition\n"
        "    And another precondition\n",
        encoding="utf-8",
    )
    return f


@pytest.fixture
def no_description_file(tmp_path: Path) -> Path:
    """Feature file without a description."""
    f = tmp_path / "no_desc.feature"
    f.write_text(
        "Feature: User Registration\n\n  Scenario: Register\n    Given a new user\n",
        encoding="utf-8",
    )
    return f


# ---------------------------------------------------------------------------
# BS003 — Step phrasing auto-fix (SAFE)
# ---------------------------------------------------------------------------


class TestBS003PhrasingFix:
    """Tests for BS003 step phrasing auto-fix."""

    def test_fix_replaces_first_person(self, phrasing_file: Path) -> None:
        main(["--fix", str(phrasing_file)])
        content = phrasing_file.read_text(encoding="utf-8")
        assert "I am on the homepage" not in content
        assert "the user is on the homepage" in content
        assert "I click the button" not in content
        assert "the user click the button" in content

    def test_fix_replaces_ive(self, phrasing_ive_file: Path) -> None:
        main(["--fix", str(phrasing_ive_file)])
        content = phrasing_ive_file.read_text(encoding="utf-8")
        assert "I've logged in" not in content
        assert "the user has logged in" in content

    def test_no_fix_without_flag(self, phrasing_file: Path) -> None:
        original = phrasing_file.read_text(encoding="utf-8")
        main([str(phrasing_file)])
        assert phrasing_file.read_text(encoding="utf-8") == original

    def test_fix_is_safe(self, phrasing_file: Path) -> None:
        """BS003 fix should be applied with --fix (safe only)."""
        main(["--fix", str(phrasing_file)])
        content = phrasing_file.read_text(encoding="utf-8")
        assert "the user" in content


# ---------------------------------------------------------------------------
# BS002 — Keyword ordering auto-fix (UNSAFE)
# ---------------------------------------------------------------------------


class TestBS002KeywordOrderFix:
    """Tests for BS002 keyword ordering auto-fix."""

    def test_fix_reorders_steps_with_unsafe(self, keyword_order_file: Path) -> None:
        main(["--fix", "--unsafe-fixes", str(keyword_order_file)])
        content = keyword_order_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        step_lines = [
            line for line in lines if line.strip().startswith(("Given", "When", "Then"))
        ]
        assert step_lines[0].strip().startswith("Given")
        assert step_lines[1].strip().startswith("When")
        assert step_lines[2].strip().startswith("Then")

    def test_fix_not_applied_without_unsafe_flag(
        self, keyword_order_file: Path
    ) -> None:
        original = keyword_order_file.read_text(encoding="utf-8")
        main(["--fix", str(keyword_order_file)])
        assert keyword_order_file.read_text(encoding="utf-8") == original

    def test_fix_preserves_and_steps(self, keyword_order_with_and_file: Path) -> None:
        main(["--fix", "--unsafe-fixes", str(keyword_order_with_and_file)])
        content = keyword_order_with_and_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        step_lines = [
            line
            for line in lines
            if line.strip()
            and not line.startswith("Feature")
            and not line.startswith("  Scenario")
        ]
        given_idx = next(
            i for i, line in enumerate(step_lines) if line.strip().startswith("Given")
        )
        and_idx = next(
            i for i, line in enumerate(step_lines) if line.strip().startswith("And")
        )
        assert given_idx < and_idx


# ---------------------------------------------------------------------------
# BS005 — Feature description auto-fix (UNSAFE)
# ---------------------------------------------------------------------------


class TestBS005DescriptionFix:
    """Tests for BS005 feature description auto-fix."""

    def test_fix_inserts_description_with_unsafe(
        self, no_description_file: Path
    ) -> None:
        main(["--fix", "--unsafe-fixes", str(no_description_file)])
        content = no_description_file.read_text(encoding="utf-8")
        assert "As a [role]" in content
        assert "I want to [action]" in content
        assert "So that [benefit]" in content

    def test_fix_not_applied_without_unsafe_flag(
        self, no_description_file: Path
    ) -> None:
        original = no_description_file.read_text(encoding="utf-8")
        main(["--fix", str(no_description_file)])
        assert no_description_file.read_text(encoding="utf-8") == original

    def test_description_inserted_after_feature_line(
        self, no_description_file: Path
    ) -> None:
        main(["--fix", "--unsafe-fixes", str(no_description_file)])
        content = no_description_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        feature_idx = next(
            i for i, line in enumerate(lines) if line.startswith("Feature:")
        )
        assert "As a" in lines[feature_idx + 1]


# ---------------------------------------------------------------------------
# Metadata tests
# ---------------------------------------------------------------------------


class TestAutoFixMetadata:
    """Verify auto_fix metadata is correctly set."""

    def test_bs002_is_unsafe(self) -> None:
        from behave_lint.rules.builtin.style import KeywordOrderingRule

        assert KeywordOrderingRule.metadata.auto_fix is AutoFixCapability.UNSAFE

    def test_bs003_is_safe(self) -> None:
        from behave_lint.rules.builtin.style import StepPhrasingRule

        assert StepPhrasingRule.metadata.auto_fix is AutoFixCapability.SAFE

    def test_bs005_is_unsafe(self) -> None:
        from behave_lint.rules.builtin.style import (
            FeatureDescriptionFormattingRule,
        )

        assert (
            FeatureDescriptionFormattingRule.metadata.auto_fix
            is AutoFixCapability.UNSAFE
        )
