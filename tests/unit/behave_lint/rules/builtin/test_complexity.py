"""Unit tests for complexity rules (BX001-BX005)."""

from __future__ import annotations

from pathlib import Path

from behave_lint.models.config import Config
from behave_lint.models.enums import Category, Severity
from behave_lint.rules.builtin.complexity import (
    FeatureFileTooLongRule,
    LongStepTextRule,
    TooManyExampleRowsRule,
    TooManyScenariosRule,
    TooManyStepsRule,
    TooManyTagsRule,
)
from behave_lint.rules.registry import RuleRegistry


def _load_feature(tmp_path: Path, content: str) -> object:
    from behave_lint.infrastructure.project_loader import load_single

    f = tmp_path / "test.feature"
    f.write_text(content, encoding="utf-8")
    feature = load_single(str(f))
    assert feature is not None, f"Failed to parse feature:\n{content}"
    return feature


def _make_steps(count: int) -> str:
    lines = []
    for i in range(count):
        if i == 0:
            lines.append(f"    Given step {i}")
        elif i == 1:
            lines.append(f"    When step {i}")
        else:
            lines.append(f"    Then step {i}")
    return "\n".join(lines)


def _make_scenarios(count: int) -> str:
    lines = []
    for i in range(count):
        lines.append(f"  Scenario: Scenario {i}")
        lines.append("    Given a step")
        lines.append("")
    return "\n".join(lines)


class TestTooManyStepsRule:
    """Tests for BX001 - Too Many Steps."""

    def test_within_limit(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: Test\n"
            "    Given a step\n"
            "    When a step\n"
            "    Then a step\n",
        )
        rule = TooManyStepsRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_exceeds_limit(self, tmp_path: Path) -> None:
        steps = "\n".join(
            f"    {'Given' if i == 0 else 'And'} step {i}" for i in range(12)
        )
        feature = _load_feature(
            tmp_path,
            f"Feature: Test\n  Description.\n\n  Scenario: Test\n{steps}\n",
        )
        rule = TooManyStepsRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BX001"
        assert "12" in diags[0].message

    def test_category_is_complexity(self, tmp_path: Path) -> None:
        steps = "\n".join(
            f"    {'Given' if i == 0 else 'And'} step {i}" for i in range(12)
        )
        feature = _load_feature(
            tmp_path,
            f"Feature: Test\n  Description.\n\n  Scenario: Test\n{steps}\n",
        )
        rule = TooManyStepsRule()
        diags = rule.check(feature, Config())
        assert diags[0].category == Category.COMPLEXITY

    def test_severity_is_warning(self, tmp_path: Path) -> None:
        steps = "\n".join(
            f"    {'Given' if i == 0 else 'And'} step {i}" for i in range(12)
        )
        feature = _load_feature(
            tmp_path,
            f"Feature: Test\n  Description.\n\n  Scenario: Test\n{steps}\n",
        )
        rule = TooManyStepsRule()
        diags = rule.check(feature, Config())
        assert diags[0].severity == Severity.WARNING


class TestTooManyScenariosRule:
    """Tests for BX002 - Too Many Scenarios."""

    def test_within_limit(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: S1\n    Given a step\n\n"
            "  Scenario: S2\n    Given a step\n",
        )
        rule = TooManyScenariosRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_exceeds_limit(self, tmp_path: Path) -> None:
        scenarios = "\n".join(
            f"  Scenario: S{i}\n    Given a step\n" for i in range(12)
        )
        feature = _load_feature(
            tmp_path,
            f"Feature: Test\n  Description.\n\n{scenarios}",
        )
        rule = TooManyScenariosRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BX002"
        assert "12" in diags[0].message


class TestTooManyExampleRowsRule:
    """Tests for BX003 - Too Many Example Rows."""

    def test_within_limit(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario Outline: Test <v>\n"
            "    Given a <v>\n\n"
            "    Examples:\n"
            "      | v |\n"
            "      | a |\n"
            "      | b |\n",
        )
        rule = TooManyExampleRowsRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_exceeds_limit(self, tmp_path: Path) -> None:
        rows = "\n".join(f"      | r{i} |" for i in range(25))
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario Outline: Test <v>\n"
            "    Given a <v>\n\n"
            f"    Examples:\n      | v |\n{rows}\n",
        )
        rule = TooManyExampleRowsRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BX003"
        assert "25" in diags[0].message

    def test_no_examples(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n  Scenario: Test\n    Given a step\n",
        )
        rule = TooManyExampleRowsRule()
        diags = rule.check(feature, Config())
        assert diags == []


class TestLongStepTextRule:
    """Tests for BX004 - Long Step Text."""

    def test_short_step_ok(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: Test\n"
            "    Given a short step\n",
        )
        rule = LongStepTextRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_long_step_flagged(self, tmp_path: Path) -> None:
        long_text = "x" * 150
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            f"  Scenario: Test\n"
            f"    Given {long_text}\n",
        )
        rule = LongStepTextRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BX004"

    def test_exact_boundary_ok(self, tmp_path: Path) -> None:
        text = "x" * 120
        feature = _load_feature(
            tmp_path,
            f"Feature: Test\n  Description.\n\n  Scenario: Test\n    Given {text}\n",
        )
        rule = LongStepTextRule()
        diags = rule.check(feature, Config())
        assert diags == []


class TestTooManyTagsRule:
    """Tests for BX005 - Too Many Tags."""

    def test_within_limit(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "@smoke @regression\n"
            "Feature: Test\n  Description.\n\n"
            "  Scenario: A scenario\n"
            "    Given a step\n",
        )
        rule = TooManyTagsRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_too_many_feature_tags(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "@a @b @c @d @e @f\n"
            "Feature: Test\n  Description.\n\n"
            "  Scenario: A scenario\n"
            "    Given a step\n",
        )
        rule = TooManyTagsRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BX005"

    def test_too_many_scenario_tags(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  @a @b @c @d @e @f\n"
            "  Scenario: A scenario\n"
            "    Given a step\n",
        )
        rule = TooManyTagsRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1

    def test_no_tags(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n  Description.\n\n"
            "  Scenario: A scenario\n"
            "    Given a step\n",
        )
        rule = TooManyTagsRule()
        diags = rule.check(feature, Config())
        assert diags == []


class TestRegisterBuiltinsWithComplexity:
    """Test that register_builtins includes complexity rules."""

    def test_all_rules_registered(self) -> None:
        from behave_lint.rules.builtin import register_builtins

        registry = RuleRegistry()
        register_builtins(registry)
        assert len(registry) == 41
        assert "BX001" in registry
        assert "BX002" in registry
        assert "BX003" in registry
        assert "BX004" in registry
        assert "BX005" in registry
        assert "BX006" in registry


class TestFeatureFileTooLongRule:
    """Tests for BX006 - Feature File Too Long."""

    def test_no_diagnostic_when_file_short(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n  Scenario: Test\n    Given a step\n",
        )
        rule = FeatureFileTooLongRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_diagnostic_when_file_too_long(self, tmp_path: Path) -> None:
        lines = ["Feature: Big Feature\n\n"]
        for i in range(80):
            lines.append(f"  Scenario: Scenario {i}\n")
            lines.append("    Given a step\n")
            lines.append("    Then a result\n\n")
        content = "".join(lines)
        assert len(content.splitlines()) > 300

        feature = _load_feature(tmp_path, content)
        rule = FeatureFileTooLongRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BX006"
