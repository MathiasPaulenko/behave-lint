"""Unit tests for correctness rules (BC001-BC006)."""

from __future__ import annotations

from pathlib import Path

from behave_lint.models.config import Config
from behave_lint.models.enums import Category, Severity
from behave_lint.rules.builtin.correctness import (
    DuplicateFeatureNamesRule,
    DuplicateScenarioNamesRule,
    EmptyFeatureRule,
    InvalidExampleTableStructureRule,
    InvalidTagSyntaxRule,
    ScenarioOutlineWithoutExamplesRule,
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


def _load_project(tmp_path: Path, files: dict[str, str]) -> object:
    """Helper: write multiple .feature files and load as a project."""
    from behave_model import load_project

    for name, content in files.items():
        f = tmp_path / name
        f.write_text(content, encoding="utf-8")
    return load_project(str(tmp_path))


class TestDuplicateScenarioNamesRule:
    """Tests for BC001 - Duplicate Scenario Names."""

    def test_no_duplicates(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: First scenario\n"
            "    Given a step\n\n"
            "  Scenario: Second scenario\n"
            "    Given a step\n",
        )
        rule = DuplicateScenarioNamesRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_duplicate_names(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Same name\n"
            "    Given a step\n\n"
            "  Scenario: Same name\n"
            "    Given a step\n",
        )
        rule = DuplicateScenarioNamesRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BC001"
        assert "Same name" in diags[0].message

    def test_three_duplicates(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Dup\n"
            "    Given a step\n\n"
            "  Scenario: Dup\n"
            "    Given a step\n\n"
            "  Scenario: Dup\n"
            "    Given a step\n",
        )
        rule = DuplicateScenarioNamesRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 2

    def test_empty_names_skipped(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario:\n"
            "    Given a step\n\n"
            "  Scenario:\n"
            "    Given a step\n",
        )
        rule = DuplicateScenarioNamesRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_severity_is_error(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Dup\n"
            "    Given a step\n\n"
            "  Scenario: Dup\n"
            "    Given a step\n",
        )
        rule = DuplicateScenarioNamesRule()
        diags = rule.check(feature, Config())
        assert diags[0].severity == Severity.ERROR

    def test_category_is_correctness(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Dup\n"
            "    Given a step\n\n"
            "  Scenario: Dup\n"
            "    Given a step\n",
        )
        rule = DuplicateScenarioNamesRule()
        diags = rule.check(feature, Config())
        assert diags[0].category == Category.CORRECTNESS


class TestEmptyFeatureRule:
    """Tests for BC002 - Empty Feature."""

    def test_feature_with_scenarios(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n  Scenario: A scenario\n    Given a step\n",
        )
        rule = EmptyFeatureRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_empty_feature(self, tmp_path: Path) -> None:
        feature = _load_feature(tmp_path, "Feature: Empty\n")
        rule = EmptyFeatureRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BC002"
        assert "no scenarios" in diags[0].message.lower()

    def test_feature_with_background_only(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n  Background:\n    Given a step\n",
        )
        rule = EmptyFeatureRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1


class TestScenarioOutlineWithoutExamplesRule:
    """Tests for BC003 - Scenario Outline Without Examples."""

    def test_outline_with_examples(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario Outline: Processing <item>\n"
            "    Given a <item>\n\n"
            "    Examples:\n"
            "      | item |\n"
            "      | box  |\n",
        )
        rule = ScenarioOutlineWithoutExamplesRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_outline_without_examples(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario Outline: Processing <item>\n"
            "    Given a <item>\n",
        )
        rule = ScenarioOutlineWithoutExamplesRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BC003"
        assert "no Examples" in diags[0].message

    def test_regular_scenario_not_flagged(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n  Scenario: Regular\n    Given a step\n",
        )
        rule = ScenarioOutlineWithoutExamplesRule()
        diags = rule.check(feature, Config())
        assert diags == []


class TestInvalidTagSyntaxRule:
    """Tests for BC004 - Invalid Tag Syntax."""

    def test_valid_tags(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "@valid_tag\n"
            "Feature: Test\n\n"
            "  @smoke\n"
            "  Scenario: A scenario\n"
            "    Given a step\n",
        )
        rule = InvalidTagSyntaxRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_tag_with_space(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "@tag-with-dashes\n"
            "Feature: Test\n\n"
            "  Scenario: A scenario\n"
            "    Given a step\n",
        )
        rule = InvalidTagSyntaxRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BC004"

    def test_tag_with_special_chars(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "@tag.with.dots\n"
            "Feature: Test\n\n"
            "  Scenario: A scenario\n"
            "    Given a step\n",
        )
        rule = InvalidTagSyntaxRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1

    def test_no_tags(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n  Scenario: A scenario\n    Given a step\n",
        )
        rule = InvalidTagSyntaxRule()
        diags = rule.check(feature, Config())
        assert diags == []


class TestDuplicateFeatureNamesRule:
    """Tests for BC005 - Duplicate Feature Names (cross-file)."""

    def test_no_duplicates(self, tmp_path: Path) -> None:
        project = _load_project(
            tmp_path,
            {
                "a.feature": "Feature: Alpha\n\n  Scenario: S\n    Given step\n",
                "b.feature": "Feature: Beta\n\n  Scenario: S\n    Given step\n",
            },
        )
        rule = DuplicateFeatureNamesRule()
        diags = rule.check(project, Config())
        assert diags == []

    def test_duplicate_feature_names(self, tmp_path: Path) -> None:
        project = _load_project(
            tmp_path,
            {
                "a.feature": "Feature: Login\n\n  Scenario: S\n    Given step\n",
                "b.feature": "Feature: Login\n\n  Scenario: S\n    Given step\n",
            },
        )
        rule = DuplicateFeatureNamesRule()
        diags = rule.check(project, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BC005"
        assert "Login" in diags[0].message

    def test_single_feature_no_diagnostic(self, tmp_path: Path) -> None:
        project = _load_project(
            tmp_path,
            {"a.feature": "Feature: Solo\n\n  Scenario: S\n    Given step\n"},
        )
        rule = DuplicateFeatureNamesRule()
        diags = rule.check(project, Config())
        assert diags == []


class TestInvalidExampleTableStructureRule:
    """Tests for BC006 - Invalid Example Table Structure."""

    def test_valid_table(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario Outline: Test <value>\n"
            "    Given a <value>\n\n"
            "    Examples:\n"
            "      | value |\n"
            "      | a     |\n"
            "      | b     |\n",
        )
        rule = InvalidExampleTableStructureRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_no_data_rows(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario Outline: Test <value>\n"
            "    Given a <value>\n\n"
            "    Examples:\n"
            "      | value |\n",
        )
        rule = InvalidExampleTableStructureRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BC006"
        assert "no data rows" in diags[0].message.lower()

    def test_column_count_mismatch(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario Outline: Test <value>\n"
            "    Given a <value>\n\n"
            "    Examples:\n"
            "      | |\n"
            "      | a |\n",
        )
        rule = InvalidExampleTableStructureRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert "empty" in diags[0].message.lower()

    def test_regular_scenario_not_flagged(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n  Scenario: Regular\n    Given a step\n",
        )
        rule = InvalidExampleTableStructureRule()
        diags = rule.check(feature, Config())
        assert diags == []


class TestRegisterBuiltins:
    """Test that register_builtins populates the registry."""

    def test_all_rules_registered(self) -> None:
        from behave_lint.rules.builtin import register_builtins

        registry = RuleRegistry()
        register_builtins(registry)
        assert len(registry) == 31
        assert "BC001" in registry
        assert "BC002" in registry
        assert "BC003" in registry
        assert "BC004" in registry
        assert "BC005" in registry
        assert "BC006" in registry

    def test_idempotent(self) -> None:
        import warnings

        from behave_lint.rules.builtin import register_builtins

        registry = RuleRegistry()
        register_builtins(registry)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            register_builtins(registry)
        assert len(registry) == 31
