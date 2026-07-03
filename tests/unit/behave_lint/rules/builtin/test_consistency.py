"""Unit tests for consistency rules (BK001-BK005)."""

from __future__ import annotations

from pathlib import Path

from behave_lint.models.config import Config
from behave_lint.models.enums import Category, Severity
from behave_lint.rules.builtin.consistency import (
    DuplicateStepTextRule,
    InconsistentNamingConventionRule,
    InconsistentScenarioLengthRule,
    InconsistentStepTextRule,
    InconsistentTagUsageRule,
)
from behave_lint.rules.registry import RuleRegistry


def _load_feature(tmp_path: Path, content: str) -> object:
    from behave_lint.infrastructure.project_loader import load_single

    f = tmp_path / "test.feature"
    f.write_text(content, encoding="utf-8")
    feature = load_single(str(f))
    assert feature is not None, f"Failed to parse feature:\n{content}"
    return feature


class TestInconsistentStepTextRule:
    """Tests for BK001 - Inconsistent Step Text."""

    def test_consistent_steps(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: A\n"
            "    Given the user is logged in\n\n"
            "  Scenario: B\n"
            "    Given the user is logged in\n",
        )
        rule = InconsistentStepTextRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_inconsistent_whitespace(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: A\n"
            "    Given a  step\n\n"
            "  Scenario: B\n"
            "    Given a step\n",
        )
        rule = InconsistentStepTextRule()
        diags = rule.check(feature, Config())
        assert len(diags) >= 1
        assert diags[0].rule_id == "BK001"

    def test_category_is_consistency(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: A\n"
            "    Given a  step\n\n"
            "  Scenario: B\n"
            "    Given a step\n",
        )
        rule = InconsistentStepTextRule()
        diags = rule.check(feature, Config())
        assert diags[0].category == Category.CONSISTENCY


class TestInconsistentTagUsageRule:
    """Tests for BK002 - Inconsistent Tag Usage."""

    def test_all_tagged(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  @smoke\n"
            "  Scenario: A\n"
            "    Given a step\n\n"
            "  @smoke\n"
            "  Scenario: B\n"
            "    Given a step\n",
        )
        rule = InconsistentTagUsageRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_some_untagged(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  @smoke\n"
            "  Scenario: A\n"
            "    Given a step\n\n"
            "  Scenario: B\n"
            "    Given a step\n",
        )
        rule = InconsistentTagUsageRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BK002"
        assert diags[0].severity == Severity.INFO

    def test_no_tags_at_all(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: A\n"
            "    Given a step\n\n"
            "  Scenario: B\n"
            "    Given a step\n",
        )
        rule = InconsistentTagUsageRule()
        diags = rule.check(feature, Config())
        assert diags == []


class TestInconsistentNamingConventionRule:
    """Tests for BK003 - Inconsistent Naming Convention."""

    def test_consistent_naming(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: User logs in\n"
            "    Given a step\n\n"
            "  Scenario: User logs out\n"
            "    Given a step\n",
        )
        rule = InconsistentNamingConventionRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_mixed_conventions(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: Given a user logs in\n"
            "    Given a step\n\n"
            "  Scenario: Given a user logs out\n"
            "    Given a step\n\n"
            "  Scenario: User registers\n"
            "    Given a step\n",
        )
        rule = InconsistentNamingConventionRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BK003"

    def test_single_scenario_not_flagged(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n  Scenario: Only one\n    Given a step\n",
        )
        rule = InconsistentNamingConventionRule()
        diags = rule.check(feature, Config())
        assert diags == []


class TestInconsistentScenarioLengthRule:
    """Tests for BK004 - Inconsistent Scenario Length."""

    def test_similar_lengths_ok(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: A\n"
            "    Given a step\n"
            "    When a step\n"
            "    Then a step\n\n"
            "  Scenario: B\n"
            "    Given a step\n"
            "    When a step\n"
            "    Then a step\n",
        )
        rule = InconsistentScenarioLengthRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_large_disparity_flagged(self, tmp_path: Path) -> None:
        short_steps = "    Given a step\n    Then a result\n"
        long_steps = "\n".join(
            f"    {'Given' if i == 0 else 'And'} step {i}" for i in range(10)
        )
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            f"  Scenario: Short\n{short_steps}\n\n"
            f"  Scenario: Long\n{long_steps}\n",
        )
        rule = InconsistentScenarioLengthRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BK004"
        assert diags[0].severity == Severity.INFO

    def test_single_scenario_not_flagged(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n  Scenario: Only one\n    Given a step\n",
        )
        rule = InconsistentScenarioLengthRule()
        diags = rule.check(feature, Config())
        assert diags == []


class TestDuplicateStepTextRule:
    """Tests for BK005 - Duplicate Step Text."""

    def test_no_duplicates(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: Test\n"
            "    Given a step\n"
            "    When another step\n",
        )
        rule = DuplicateStepTextRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_duplicate_steps(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: Test\n"
            "    Given a user\n"
            "    Given a user\n"
            "    When I do something\n",
        )
        rule = DuplicateStepTextRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BK005"

    def test_same_text_different_case_flagged(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: Test\n"
            "    Given A User\n"
            "    Given a user\n",
        )
        rule = DuplicateStepTextRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1


class TestRegisterBuiltinsWithConsistency:
    """Test that register_builtins includes consistency rules."""

    def test_all_rules_registered(self) -> None:
        from behave_lint.rules.builtin import register_builtins

        registry = RuleRegistry()
        register_builtins(registry)
        assert len(registry) == 50
        assert "BK001" in registry
        assert "BK002" in registry
        assert "BK003" in registry
        assert "BK004" in registry
        assert "BK005" in registry
