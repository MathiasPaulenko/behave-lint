"""Unit tests for style rules (BS001-BS005)."""

from __future__ import annotations

from pathlib import Path

from behave_lint.models.config import Config
from behave_lint.models.enums import Category, Severity
from behave_lint.rules.builtin.style import (
    BackgroundNameRule,
    FeatureDescriptionFormattingRule,
    KeywordOrderingRule,
    StepKeywordCasingRule,
    StepPhrasingRule,
    TabIndentationRule,
    TagCasingRule,
    TrailingWhitespaceRule,
)
from behave_lint.rules.registry import RuleRegistry


def _load_feature(tmp_path: Path, content: str) -> object:
    from behave_lint.infrastructure.project_loader import load_single

    f = tmp_path / "test.feature"
    f.write_text(content, encoding="utf-8")
    feature = load_single(str(f))
    assert feature is not None, f"Failed to parse feature:\n{content}"
    return feature


class TestTagCasingRule:
    """Tests for BS001 - Tag Casing."""

    def test_valid_lowercase_tags(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "@smoke_test\nFeature: Test\n\n  Scenario: A scenario\n    Given a step\n",
        )
        rule = TagCasingRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_mixed_case_tag(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "@SmokeTest\nFeature: Test\n\n  Scenario: A scenario\n    Given a step\n",
        )
        rule = TagCasingRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BS001"

    def test_kebab_case_tag(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "@smoke-test\nFeature: Test\n\n  Scenario: A scenario\n    Given a step\n",
        )
        rule = TagCasingRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1

    def test_no_tags(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n  Scenario: A scenario\n    Given a step\n",
        )
        rule = TagCasingRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_severity_is_warning(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "@SmokeTest\nFeature: Test\n\n  Scenario: A scenario\n    Given a step\n",
        )
        rule = TagCasingRule()
        diags = rule.check(feature, Config())
        assert diags[0].severity == Severity.WARNING

    def test_category_is_style(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "@SmokeTest\nFeature: Test\n\n  Scenario: A scenario\n    Given a step\n",
        )
        rule = TagCasingRule()
        diags = rule.check(feature, Config())
        assert diags[0].category == Category.STYLE


class TestKeywordOrderingRule:
    """Tests for BS002 - Keyword Ordering."""

    def test_correct_order(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Test\n"
            "    Given a precondition\n"
            "    When I do something\n"
            "    Then I see a result\n",
        )
        rule = KeywordOrderingRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_then_before_when(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Test\n"
            "    Then I see a result\n"
            "    When I do something\n",
        )
        rule = KeywordOrderingRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BS002"

    def test_given_after_when(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Test\n"
            "    When I do something\n"
            "    Given a precondition\n",
        )
        rule = KeywordOrderingRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1

    def test_and_preserves_context(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Test\n"
            "    Given a precondition\n"
            "    And another precondition\n"
            "    When I do something\n"
            "    Then I see a result\n",
        )
        rule = KeywordOrderingRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_no_steps(self, tmp_path: Path) -> None:
        feature = _load_feature(tmp_path, "Feature: Test\n")
        rule = KeywordOrderingRule()
        diags = rule.check(feature, Config())
        assert diags == []


class TestStepPhrasingRule:
    """Tests for BS003 - Step Phrasing."""

    def test_third_person_ok(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Test\n"
            "    Given the user is logged in\n"
            "    When the user clicks submit\n",
        )
        rule = StepPhrasingRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_first_person_flagged(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Test\n"
            "    Given I am logged in\n"
            "    When I click submit\n",
        )
        rule = StepPhrasingRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 2
        assert diags[0].rule_id == "BS003"

    def test_no_first_person(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Test\n"
            "    Given a system state\n"
            "    Then a result appears\n",
        )
        rule = StepPhrasingRule()
        diags = rule.check(feature, Config())
        assert diags == []


class TestBackgroundNameRule:
    """Tests for BS004 - Background Name."""

    def test_named_background(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Background: Common setup\n"
            "    Given a step\n\n"
            "  Scenario: A scenario\n"
            "    When I do something\n",
        )
        rule = BackgroundNameRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_unnamed_background(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Background:\n"
            "    Given a step\n\n"
            "  Scenario: A scenario\n"
            "    When I do something\n",
        )
        rule = BackgroundNameRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BS004"

    def test_no_background(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n  Scenario: A scenario\n    Given a step\n",
        )
        rule = BackgroundNameRule()
        diags = rule.check(feature, Config())
        assert diags == []


class TestFeatureDescriptionFormattingRule:
    """Tests for BS005 - Feature Description Formatting."""

    def test_with_description(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Login\n"
            "  As a user\n"
            "  I want to log in\n"
            "  So that I can access the app\n\n"
            "  Scenario: Successful login\n"
            "    Given valid credentials\n",
        )
        rule = FeatureDescriptionFormattingRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_without_description(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Login\n\n"
            "  Scenario: Successful login\n"
            "    Given valid credentials\n",
        )
        rule = FeatureDescriptionFormattingRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BS005"

    def test_empty_description(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Login\n"
            "  \n"
            "  Scenario: Successful login\n"
            "    Given valid credentials\n",
        )
        rule = FeatureDescriptionFormattingRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1


class TestRegisterBuiltinsWithStyle:
    """Test that register_builtins includes style rules."""

    def test_all_rules_registered(self) -> None:
        from behave_lint.rules.builtin import register_builtins

        registry = RuleRegistry()
        register_builtins(registry)
        assert len(registry) == 41
        assert "BS001" in registry
        assert "BS002" in registry
        assert "BS003" in registry
        assert "BS004" in registry
        assert "BS005" in registry
        assert "BS006" in registry
        assert "BS007" in registry
        assert "BS008" in registry


class TestStepKeywordCasingRule:
    """Tests for BS006 - Step Keyword Casing."""

    def test_no_diagnostic_when_keywords_capitalized(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Test\n"
            "    Given a step\n"
            "    When I do something\n"
            "    Then I see a result\n",
        )
        rule = StepKeywordCasingRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_diagnostic_when_keywords_lowercase(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Test\n"
            "    given a step\n"
            "    when I do something\n"
            "    then I see a result\n",
        )
        rule = StepKeywordCasingRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 3
        assert all(d.rule_id == "BS006" for d in diags)


class TestTrailingWhitespaceRule:
    """Tests for BS007 - Trailing Whitespace."""

    def test_no_diagnostic_when_no_trailing_whitespace(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n  Scenario: Test\n    Given a step\n",
        )
        rule = TrailingWhitespaceRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_diagnostic_when_trailing_whitespace(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test   \n  Scenario: A  \n    Given a step\n",
        )
        rule = TrailingWhitespaceRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 2
        assert all(d.rule_id == "BS007" for d in diags)


class TestTabIndentationRule:
    """Tests for BS008 - Tab Indentation."""

    def test_no_diagnostic_when_spaces_used(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n  Scenario: Test\n    Given a step\n",
        )
        rule = TabIndentationRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_diagnostic_when_tabs_used(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\tScenario: A\n\t\tGiven a step\n",
        )
        rule = TabIndentationRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 2
        assert all(d.rule_id == "BS008" for d in diags)
