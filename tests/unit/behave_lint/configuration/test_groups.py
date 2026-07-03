"""Tests for rule groups — category and tag-based rule selection."""

from __future__ import annotations

import pytest

from behave_lint.configuration.groups import (
    get_category_prefix,
    get_group_names,
    get_group_tags,
    is_category_group,
    is_valid_group,
    parse_groups,
)
from behave_lint.configuration.loader import load_config
from behave_lint.exceptions import InvalidConfigValueError

# ---------------------------------------------------------------------------
# Unit tests — groups module
# ---------------------------------------------------------------------------


class TestGroupsModule:
    """Tests for the groups module API."""

    def test_get_group_names_returns_sorted_list(self) -> None:
        names = get_group_names()
        assert isinstance(names, list)
        assert names == sorted(names)
        assert "correctness" in names
        assert "style" in names
        assert "naming" in names

    def test_is_valid_group_true_for_known(self) -> None:
        assert is_valid_group("correctness")
        assert is_valid_group("style")
        assert is_valid_group("naming")
        assert is_valid_group("step-definitions")

    def test_is_valid_group_false_for_unknown(self) -> None:
        assert not is_valid_group("nonexistent")
        assert not is_valid_group("")

    def test_is_category_group_true_for_categories(self) -> None:
        assert is_category_group("correctness")
        assert is_category_group("style")
        assert is_category_group("pedantic")
        assert is_category_group("step-definitions")
        assert is_category_group("consistency")

    def test_is_category_group_false_for_tags(self) -> None:
        assert not is_category_group("naming")
        assert not is_category_group("tags")
        assert not is_category_group("steps")

    def test_get_category_prefix(self) -> None:
        assert get_category_prefix("correctness") == "BC"
        assert get_category_prefix("style") == "BS"
        assert get_category_prefix("pedantic") == "BP"
        assert get_category_prefix("step-definitions") == "BD"
        assert get_category_prefix("consistency") == "BK"
        assert get_category_prefix("naming") is None

    def test_get_group_tags_returns_set(self) -> None:
        tags = get_group_tags("naming")
        assert tags is not None
        assert "naming" in tags

    def test_get_group_tags_returns_none_for_category(self) -> None:
        assert get_group_tags("correctness") is None

    def test_get_group_tags_formatting_includes_related(self) -> None:
        tags = get_group_tags("formatting")
        assert tags is not None
        assert "formatting" in tags
        assert "whitespace" in tags
        assert "indentation" in tags


# ---------------------------------------------------------------------------
# parse_groups
# ---------------------------------------------------------------------------


class TestParseGroups:
    """Tests for parse_groups function."""

    def test_parse_string_single(self) -> None:
        result = parse_groups("correctness")
        assert result == ["correctness"]

    def test_parse_string_multiple(self) -> None:
        result = parse_groups("correctness,style")
        assert result == ["correctness", "style"]

    def test_parse_string_with_spaces(self) -> None:
        result = parse_groups(" correctness , style ")
        assert result == ["correctness", "style"]

    def test_parse_list(self) -> None:
        result = parse_groups(["correctness", "style"])
        assert result == ["correctness", "style"]

    def test_parse_empty_string(self) -> None:
        result = parse_groups("")
        assert result == []

    def test_parse_empty_list(self) -> None:
        result = parse_groups([])
        assert result == []

    def test_parse_invalid_raises(self) -> None:
        with pytest.raises(InvalidConfigValueError):
            parse_groups("nonexistent")

    def test_parse_mixed_valid_invalid_raises(self) -> None:
        with pytest.raises(InvalidConfigValueError):
            parse_groups("correctness,nonexistent")


# ---------------------------------------------------------------------------
# Integration — load_config with groups
# ---------------------------------------------------------------------------


class TestGroupConfigIntegration:
    """Tests for group expansion in load_config."""

    def test_category_group_correctness(self) -> None:
        config = load_config(overrides={"group": ["correctness"]})
        assert config.group == ["correctness"]
        assert len(config.select) > 0
        for rule_id in config.select:
            assert rule_id.startswith("BC")

    def test_category_group_style(self) -> None:
        config = load_config(overrides={"group": ["style"]})
        assert config.group == ["style"]
        for rule_id in config.select:
            assert rule_id.startswith("BS")

    def test_category_group_pedantic(self) -> None:
        config = load_config(overrides={"group": ["pedantic"]})
        assert config.group == ["pedantic"]
        for rule_id in config.select:
            assert rule_id.startswith("BP")

    def test_category_group_step_definitions(self) -> None:
        config = load_config(overrides={"group": ["step-definitions"]})
        assert config.group == ["step-definitions"]
        for rule_id in config.select:
            assert rule_id.startswith("BD")

    def test_tag_group_naming(self) -> None:
        config = load_config(overrides={"group": ["naming"]})
        assert config.group == ["naming"]
        assert len(config.select) > 0

    def test_tag_group_steps(self) -> None:
        config = load_config(overrides={"group": ["steps"]})
        assert config.group == ["steps"]
        assert len(config.select) > 0

    def test_multiple_groups_combined(self) -> None:
        config = load_config(overrides={"group": ["correctness", "style"]})
        assert config.group == ["correctness", "style"]
        bc_count = sum(1 for r in config.select if r.startswith("BC"))
        bs_count = sum(1 for r in config.select if r.startswith("BS"))
        assert bc_count > 0
        assert bs_count > 0

    def test_group_with_string_value(self) -> None:
        config = load_config(overrides={"group": "correctness,style"})
        assert config.group == ["correctness", "style"]
        assert len(config.select) > 0

    def test_no_group_empty_select(self) -> None:
        config = load_config()
        assert config.group == []
        assert config.select == []

    def test_group_adds_to_existing_select(self) -> None:
        config = load_config(overrides={"group": ["correctness"], "select": ["BS001"]})
        assert "BS001" in config.select
        assert any(r.startswith("BC") for r in config.select)

    def test_group_with_profile(self) -> None:
        config = load_config(
            overrides={"profile": "recommended", "group": ["pedantic"]}
        )
        assert config.profile == "recommended"
        assert config.group == ["pedantic"]
        # Pedantic rules should be in select despite profile ignoring them
        assert any(r.startswith("BP") for r in config.select)

    def test_invalid_group_raises(self) -> None:
        with pytest.raises(InvalidConfigValueError):
            load_config(overrides={"group": ["nonexistent"]})


# ---------------------------------------------------------------------------
# Integration — env var
# ---------------------------------------------------------------------------


class TestGroupEnvVar:
    """Tests for BEHAVE_LINT_GROUP env var."""

    def test_env_var_group(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BEHAVE_LINT_GROUP", "correctness")
        config = load_config()
        assert config.group == ["correctness"]
        assert len(config.select) > 0
        assert all(r.startswith("BC") for r in config.select)


# ---------------------------------------------------------------------------
# Integration — CLI
# ---------------------------------------------------------------------------


class TestGroupCLI:
    """Tests for --group CLI flag."""

    def test_group_option_exists_in_command_params(self) -> None:
        import typer

        from behave_lint.cli.parser import app

        cmd = typer.main.get_command(app)
        opts = [p.name for p in cmd.params]
        assert "group" in opts

    def test_group_flag_selects_correctness(
        self, tmp_path: pytest.TempPathFactory, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from behave_lint.cli.coordinator import main

        f = tmp_path / "test_group.feature"
        f.write_text(
            "Feature: Test Feature\n\n  Scenario: Test Scenario\n    Given a step\n",
            encoding="utf-8",
        )
        exit_code = main(["--group", "correctness", str(f)])
        assert exit_code != 2  # Not a crash
