"""Unit tests for pedantic rules (BP001-BP005)."""

from __future__ import annotations

from pathlib import Path

from behave_lint.models.config import Config
from behave_lint.models.enums import Category, Severity
from behave_lint.rules.builtin.pedantic import (
    MissingBackgroundRule,
    MissingExamplesNameRule,
    MissingScenarioTagsRule,
    ShortFeatureNameRule,
    ShortScenarioNameRule,
)
from behave_lint.rules.registry import RuleRegistry


def _load_feature(tmp_path: Path, content: str) -> object:
    from behave_lint.infrastructure.project_loader import load_single

    f = tmp_path / "test.feature"
    f.write_text(content, encoding="utf-8")
    feature = load_single(str(f))
    assert feature is not None, f"Failed to parse feature:\n{content}"
    return feature


class TestMissingScenarioTagsRule:
    """Tests for BP001 - Missing Scenario Tags."""

    def test_with_tags(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  @smoke\n"
            "  Scenario: A scenario\n"
            "    Given a step\n",
        )
        rule = MissingScenarioTagsRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_without_tags(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: A scenario\n"
            "    Given a step\n",
        )
        rule = MissingScenarioTagsRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BP001"
        assert diags[0].severity == Severity.INFO

    def test_category_is_pedantic(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: A scenario\n"
            "    Given a step\n",
        )
        rule = MissingScenarioTagsRule()
        diags = rule.check(feature, Config())
        assert diags[0].category == Category.PEDANTIC


class TestMissingBackgroundRule:
    """Tests for BP002 - Missing Background."""

    def test_with_background(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Background: Setup\n"
            "    Given a step\n\n"
            "  Scenario: A scenario\n"
            "    When I do something\n",
        )
        rule = MissingBackgroundRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_without_background(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: A scenario\n"
            "    Given a step\n",
        )
        rule = MissingBackgroundRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BP002"


class TestShortScenarioNameRule:
    """Tests for BP003 - Short Scenario Name."""

    def test_descriptive_name_ok(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: User can log in\n"
            "    Given a step\n",
        )
        rule = ShortScenarioNameRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_short_name_flagged(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n  Scenario: S1\n    Given a step\n",
        )
        rule = ShortScenarioNameRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BP003"

    def test_empty_name_flagged(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n  Scenario:\n    Given a step\n",
        )
        rule = ShortScenarioNameRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1


class TestShortFeatureNameRule:
    """Tests for BP004 - Short Feature Name."""

    def test_descriptive_name_ok(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: User Authentication\n  Description.\n\n"
            "  Scenario: A scenario\n"
            "    Given a step\n",
        )
        rule = ShortFeatureNameRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_short_name_flagged(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: App\n  Description.\n\n"
            "  Scenario: A scenario\n"
            "    Given a step\n",
        )
        rule = ShortFeatureNameRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BP004"


class TestMissingExamplesNameRule:
    """Tests for BP005 - Missing Examples Name."""

    def test_named_examples_ok(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario Outline: Test <v>\n"
            "    Given a <v>\n\n"
            "    Examples: Valid values\n"
            "      | v |\n"
            "      | a |\n",
        )
        rule = MissingExamplesNameRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_unnamed_examples_flagged(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario Outline: Test <v>\n"
            "    Given a <v>\n\n"
            "    Examples:\n"
            "      | v |\n"
            "      | a |\n",
        )
        rule = MissingExamplesNameRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BP005"

    def test_no_examples_no_diag(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n  Scenario: Test\n    Given a step\n",
        )
        rule = MissingExamplesNameRule()
        diags = rule.check(feature, Config())
        assert diags == []


class TestRegisterBuiltinsWithPedantic:
    """Test that register_builtins includes pedantic rules."""

    def test_all_rules_registered(self) -> None:
        from behave_lint.rules.builtin import register_builtins

        registry = RuleRegistry()
        register_builtins(registry)
        assert len(registry) == 31
        assert "BP001" in registry
        assert "BP002" in registry
        assert "BP003" in registry
        assert "BP004" in registry
        assert "BP005" in registry
