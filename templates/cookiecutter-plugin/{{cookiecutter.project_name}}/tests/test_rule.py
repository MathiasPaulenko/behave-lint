"""Tests for {{ cookiecutter.rule_id }} ({{ cookiecutter.rule_name }})."""

from __future__ import annotations

from pathlib import Path

import pytest

from behave_lint.configuration.loader import load_config
from behave_lint.engine.lint_engine import LintEngine
from behave_lint.rules.builtin import register_builtins
from behave_lint.rules.registry import RuleRegistry

from {{ cookiecutter.plugin_name }}.rules import register_rules


@pytest.fixture
def registry() -> RuleRegistry:
    reg = RuleRegistry()
    register_builtins(reg)
    for rule_class in register_rules():
        reg.register(rule_class, source="{{ cookiecutter.project_name }}")
    return reg


@pytest.fixture
def feature_file(tmp_path: Path) -> Path:
    f = tmp_path / "test.feature"
    f.write_text(
        "Feature: Test\n\n"
        "  Scenario: A scenario\n"
        "    Given a step\n"
        "    When I do something\n"
        "    Then I see a result\n",
        encoding="utf-8",
    )
    return f


class Test{{ cookiecutter.class_name }}Rule:
    """Tests for {{ cookiecutter.rule_id }}."""

    def test_rule_is_registered(self, registry: RuleRegistry) -> None:
        assert "{{ cookiecutter.rule_id }}" in registry

    def test_rule_has_correct_metadata(self, registry: RuleRegistry) -> None:
        entry = registry.get("{{ cookiecutter.rule_id }}")
        assert entry is not None
        metadata = entry[1]
        assert metadata.name == "{{ cookiecutter.rule_name }}"
        assert metadata.title == "{{ cookiecutter.rule_title }}"

    def test_check_returns_diagnostics(
        self, registry: RuleRegistry, feature_file: Path
    ) -> None:
        config = load_config(overrides={"select": ["{{ cookiecutter.rule_id }}"]})
        engine = LintEngine(config, registry)
        result = engine.lint([str(feature_file)])

        # TODO: Adjust this assertion based on your rule's behavior.
        # The rule may or may not produce diagnostics for this fixture.
        assert isinstance(result.diagnostics, list)

    def test_no_diagnostics_on_clean_file(
        self, registry: RuleRegistry, tmp_path: Path
    ) -> None:
        f = tmp_path / "clean.feature"
        f.write_text(
            "Feature: Clean\n\n"
            "  Scenario: A scenario\n"
            "    Given a step\n"
            "    When I do something\n"
            "    Then I see a result\n",
            encoding="utf-8",
        )
        config = load_config(overrides={"select": ["{{ cookiecutter.rule_id }}"]})
        engine = LintEngine(config, registry)
        result = engine.lint([str(f)])

        # TODO: Adjust — if your rule finds issues in this file, change this.
        # For now, just verify the run doesn't crash.
        assert result.exit_code == 0
