"""Unit tests for step definition rules (BD001-BD005)."""

from __future__ import annotations

from pathlib import Path

from behave_lint.models.config import Config
from behave_lint.models.enums import Category, Severity
from behave_lint.rules.builtin.step_definitions import (
    AmbiguousStepPatternRule,
    StepParameterConventionRule,
    StepTrailingPunctuationRule,
    UndefinedStepPatternRule,
    UnusedStepDefinitionRule,
)
from behave_lint.rules.registry import RuleRegistry


def _load_feature(tmp_path: Path, content: str) -> object:
    from behave_lint.infrastructure.project_loader import load_single

    f = tmp_path / "test.feature"
    f.write_text(content, encoding="utf-8")
    feature = load_single(str(f))
    assert feature is not None, f"Failed to parse feature:\n{content}"
    return feature


class TestUndefinedStepPatternRule:
    """Tests for BD001 - Undefined Step Pattern."""

    def test_no_placeholders(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: Test\n"
            "    Given a concrete step\n",
        )
        rule = UndefinedStepPatternRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_placeholder_in_outline_ok(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario Outline: Test <v>\n"
            "    Given a <v>\n\n"
            "    Examples:\n"
            "      | v |\n"
            "      | a |\n",
        )
        rule = UndefinedStepPatternRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_placeholder_in_regular_scenario(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n  Scenario: Test\n    Given a <value>\n",
        )
        rule = UndefinedStepPatternRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BD001"

    def test_category_is_step_definitions(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n  Scenario: Test\n    Given a <value>\n",
        )
        rule = UndefinedStepPatternRule()
        diags = rule.check(feature, Config())
        assert diags[0].category == Category.STEP_DEFINITIONS


class TestAmbiguousStepPatternRule:
    """Tests for BD002 - Ambiguous Step Pattern."""

    def test_specific_step_ok(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: Test\n"
            "    Given a user named Alice\n",
        )
        rule = AmbiguousStepPatternRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_generic_step_flagged(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n  Scenario: Test\n    Given a thing\n",
        )
        rule = AmbiguousStepPatternRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BD002"

    def test_severity_is_warning(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n  Scenario: Test\n    Given some stuff\n",
        )
        rule = AmbiguousStepPatternRule()
        diags = rule.check(feature, Config())
        assert diags[0].severity == Severity.WARNING


class TestUnusedStepDefinitionRule:
    """Tests for BD003 - Unused Step Definition."""

    def test_reused_steps_ok(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: A\n"
            "    Given a user\n\n"
            "  Scenario: B\n"
            "    Given a user\n",
        )
        rule = UnusedStepDefinitionRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_unique_steps_flagged(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: A\n"
            "    Given a unique step\n\n"
            "  Scenario: B\n"
            "    Given a different step\n",
        )
        rule = UnusedStepDefinitionRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 2
        assert diags[0].rule_id == "BD003"
        assert diags[0].severity == Severity.INFO


class TestStepParameterConventionRule:
    """Tests for BD004 - Step Parameter Convention."""

    def test_consistent_angle_ok(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario Outline: Test\n"
            "    Given a <value> with <count> items\n\n"
            "    Examples:\n"
            "      | value | count |\n"
            "      | a     | 1     |\n",
        )
        rule = StepParameterConventionRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_mixed_conventions_flagged(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario Outline: Test\n"
            "    Given a <value> with {count} items\n\n"
            "    Examples:\n"
            "      | value |\n"
            "      | a     |\n",
        )
        rule = StepParameterConventionRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BD004"

    def test_no_params_ok(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n  Scenario: Test\n    Given a step\n",
        )
        rule = StepParameterConventionRule()
        diags = rule.check(feature, Config())
        assert diags == []


class TestStepTrailingPunctuationRule:
    """Tests for BD005 - Step Trailing Punctuation."""

    def test_no_punctuation_ok(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: Test\n"
            "    Given a step\n"
            "    And another step\n",
        )
        rule = StepTrailingPunctuationRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_trailing_period_flagged(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: Test\n"
            "    Given a user.\n"
            "    Then a result\n",
        )
        rule = StepTrailingPunctuationRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BD005"

    def test_trailing_comma_flagged(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: Test\n"
            "    Given a user,\n"
            "    Then a result\n",
        )
        rule = StepTrailingPunctuationRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1


class TestRegisterBuiltinsWithStepDefinitions:
    """Test that register_builtins includes step definition rules."""

    def test_all_rules_registered(self) -> None:
        from behave_lint.rules.builtin import register_builtins

        registry = RuleRegistry()
        register_builtins(registry)
        assert len(registry) == 31
        assert "BD001" in registry
        assert "BD002" in registry
        assert "BD003" in registry
        assert "BD004" in registry
        assert "BD005" in registry
