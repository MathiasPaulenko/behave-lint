"""Unit tests for accessibility rules (BACC001-BACC003)."""

from __future__ import annotations

from pathlib import Path

from behave_lint.models.config import Config
from behave_lint.models.enums import Category, Severity
from behave_lint.rules.builtin.accessibility import (
    AbleistLanguageRule,
    ColorOnlyContrastRule,
    MissingAccessibilityScenarioRule,
)
from behave_lint.rules.registry import RuleRegistry


def _load_feature(tmp_path: Path, content: str) -> object:
    """Helper: write a .feature file and load it via behave-model."""
    from behave_lint.infrastructure.project_loader import load_single

    f = tmp_path / "test.feature"
    f.write_text(content, encoding="utf-8")
    feature = load_single(str(f))
    assert feature is not None, f"Failed to parse feature:\n{content}"
    return feature


class TestAbleistLanguageRule:
    """Tests for BACC001 - Ableist language."""

    def test_detects_ableist_in_scenario_name(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n  Scenario: Register disabled user\n    Given a step\n",
        )
        rule = AbleistLanguageRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BACC001"
        assert "disabled" in diags[0].message.lower()

    def test_detects_ableist_in_step(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n  Scenario: Normal scenario\n    Given a disabled user\n",
        )
        rule = AbleistLanguageRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BACC001"

    def test_detects_wheelchair_bound(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n  Scenario: Access\n    Given a wheelchair-bound user\n",
        )
        rule = AbleistLanguageRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert "wheelchair" in diags[0].message.lower()

    def test_no_false_positive_inclusive_language(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Register user with a disability\n"
            "    Given a user with a disability\n",
        )
        rule = AbleistLanguageRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_category_and_severity(self) -> None:
        rule = AbleistLanguageRule()
        assert rule.metadata.category is Category.ACCESSIBILITY
        assert rule.metadata.default_severity is Severity.WARNING


class TestMissingAccessibilityScenarioRule:
    """Tests for BACC002 - Missing accessibility scenario."""

    def test_detects_ui_feature_without_a11y(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "@ui\n"
            "Feature: Login form\n\n"
            "  Scenario: Successful login\n"
            "    Given the user is on the login page\n",
        )
        rule = MissingAccessibilityScenarioRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BACC002"
        assert "accessibility" in diags[0].message.lower()

    def test_no_diag_when_a11y_tag_present(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "@ui\n"
            "Feature: Login form\n\n"
            "  @accessibility\n"
            "  Scenario: Keyboard nav\n"
            "    Given the user is on the login page\n",
        )
        rule = MissingAccessibilityScenarioRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_no_diag_when_no_ui_tag(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: API test\n\n  Scenario: Call endpoint\n    Given the API is up\n",
        )
        rule = MissingAccessibilityScenarioRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_category_and_severity(self) -> None:
        rule = MissingAccessibilityScenarioRule()
        assert rule.metadata.category is Category.ACCESSIBILITY
        assert rule.metadata.default_severity is Severity.WARNING


class TestColorOnlyContrastRule:
    """Tests for BACC003 - Color-only contrast."""

    def test_detects_color_only(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n  Scenario: Status\n    Then the button is red\n",
        )
        rule = ColorOnlyContrastRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BACC003"
        assert "color" in diags[0].message.lower()

    def test_no_false_positive_with_text_indicator(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Status\n"
            '    Then the button is red and shows "Error"\n',
        )
        rule = ColorOnlyContrastRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_no_false_positive_no_color(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            'Feature: Test\n\n  Scenario: Status\n    Then the button shows "Error"\n',
        )
        rule = ColorOnlyContrastRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_category_and_severity(self) -> None:
        rule = ColorOnlyContrastRule()
        assert rule.metadata.category is Category.ACCESSIBILITY
        assert rule.metadata.default_severity is Severity.WARNING


class TestRegisterAccessibilityRules:
    """Test that accessibility rules are registered."""

    def test_all_accessibility_rules_registered(self) -> None:
        from behave_lint.rules.builtin import register_builtins

        registry = RuleRegistry()
        register_builtins(registry)
        assert len(registry) == 50
        assert "BACC001" in registry
        assert "BACC002" in registry
        assert "BACC003" in registry
