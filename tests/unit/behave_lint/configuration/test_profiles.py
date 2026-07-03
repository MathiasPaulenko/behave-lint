"""Exhaustive unit tests for built-in profiles.

Tests cover:
- Profile name constants and values.
- get_profile_names() return value and sorting.
- is_valid_profile() for all valid, invalid, and edge-case names.
- get_profile_config() for each profile — exact contents, immutability,
  error handling.
- Config.is_rule_enabled() behavior under each profile.
- load_config() integration: overrides, env vars, pyproject.toml,
  precedence, invalid profile handling.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from behave_lint.configuration.profiles import (
    PROFILE_MINIMAL,
    PROFILE_NONE,
    PROFILE_RECOMMENDED,
    PROFILE_STRICT,
    get_profile_config,
    get_profile_names,
    is_valid_profile,
)
from behave_lint.exceptions import InvalidConfigValueError

# ---------------------------------------------------------------------------
# Profile name constants
# ---------------------------------------------------------------------------


class TestProfileConstants:
    """Verify profile name constant values."""

    def test_recommended_value(self) -> None:
        assert PROFILE_RECOMMENDED == "recommended"

    def test_strict_value(self) -> None:
        assert PROFILE_STRICT == "strict"

    def test_minimal_value(self) -> None:
        assert PROFILE_MINIMAL == "minimal"

    def test_none_value(self) -> None:
        assert PROFILE_NONE == "none"


# ---------------------------------------------------------------------------
# get_profile_names()
# ---------------------------------------------------------------------------


class TestGetProfileNames:
    """Tests for get_profile_names()."""

    def test_returns_all_builtin_profiles(self) -> None:
        names = get_profile_names()
        assert PROFILE_RECOMMENDED in names
        assert PROFILE_STRICT in names
        assert PROFILE_MINIMAL in names

    def test_returns_sorted(self) -> None:
        names = get_profile_names()
        assert names == sorted(names)

    def test_returns_exactly_three(self) -> None:
        names = get_profile_names()
        assert len(names) == 3

    def test_does_not_include_none(self) -> None:
        names = get_profile_names()
        assert PROFILE_NONE not in names


# ---------------------------------------------------------------------------
# is_valid_profile()
# ---------------------------------------------------------------------------


class TestIsValidProfile:
    """Tests for is_valid_profile()."""

    @pytest.mark.parametrize(
        "name",
        [PROFILE_RECOMMENDED, PROFILE_STRICT, PROFILE_MINIMAL, PROFILE_NONE],
    )
    def test_valid_names(self, name: str) -> None:
        assert is_valid_profile(name) is True

    def test_invalid_name(self) -> None:
        assert is_valid_profile("nonexistent") is False

    def test_empty_string(self) -> None:
        assert is_valid_profile("") is False

    def test_case_sensitive(self) -> None:
        assert is_valid_profile("Recommended") is False
        assert is_valid_profile("STRICT") is False
        assert is_valid_profile("MINIMAL") is False

    def test_none_value_is_not_valid_as_profile(self) -> None:
        assert is_valid_profile("None") is False

    def test_whitespace_only(self) -> None:
        assert is_valid_profile("  ") is False

    def test_partial_match(self) -> None:
        assert is_valid_profile("recommend") is False
        assert is_valid_profile("strict ") is False
        assert is_valid_profile(" minimal") is False


# ---------------------------------------------------------------------------
# get_profile_config() — recommended
# ---------------------------------------------------------------------------


class TestGetProfileConfigRecommended:
    """Detailed tests for the recommended profile."""

    def test_select_is_empty(self) -> None:
        config = get_profile_config(PROFILE_RECOMMENDED)
        assert config["select"] == []

    def test_ignore_contains_all_pedantic(self) -> None:
        config = get_profile_config(PROFILE_RECOMMENDED)
        ignore = config["ignore"]
        for bp_rule in [
            "BP001",
            "BP002",
            "BP003",
            "BP004",
            "BP005",
            "BP006",
            "BP007",
        ]:
            assert bp_rule in ignore

    def test_ignore_count_is_seven(self) -> None:
        config = get_profile_config(PROFILE_RECOMMENDED)
        assert len(config["ignore"]) == 7

    def test_ignore_only_contains_bp_rules(self) -> None:
        config = get_profile_config(PROFILE_RECOMMENDED)
        assert all(r.startswith("BP") for r in config["ignore"])


# ---------------------------------------------------------------------------
# get_profile_config() — strict
# ---------------------------------------------------------------------------


class TestGetProfileConfigStrict:
    """Detailed tests for the strict profile."""

    def test_select_is_empty(self) -> None:
        config = get_profile_config(PROFILE_STRICT)
        assert config["select"] == []

    def test_ignore_is_empty(self) -> None:
        config = get_profile_config(PROFILE_STRICT)
        assert config["ignore"] == []


# ---------------------------------------------------------------------------
# get_profile_config() — minimal
# ---------------------------------------------------------------------------


class TestGetProfileConfigMinimal:
    """Detailed tests for the minimal profile."""

    def test_select_is_not_empty(self) -> None:
        config = get_profile_config(PROFILE_MINIMAL)
        assert config["select"] != []

    def test_select_contains_all_bc_rules(self) -> None:
        config = get_profile_config(PROFILE_MINIMAL)
        select = config["select"]
        for bc_rule in [
            "BC001",
            "BC002",
            "BC003",
            "BC004",
            "BC005",
            "BC006",
            "BC007",
            "BC008",
            "BC009",
            "BC010",
        ]:
            assert bc_rule in select

    def test_select_contains_all_bd_rules(self) -> None:
        config = get_profile_config(PROFILE_MINIMAL)
        select = config["select"]
        for bd_rule in ["BD001", "BD002", "BD003", "BD004", "BD005"]:
            assert bd_rule in select

    def test_select_count_is_fifteen(self) -> None:
        config = get_profile_config(PROFILE_MINIMAL)
        assert len(config["select"]) == 15

    def test_select_only_contains_bc_and_bd(self) -> None:
        config = get_profile_config(PROFILE_MINIMAL)
        assert all(r.startswith("BC") or r.startswith("BD") for r in config["select"])

    def test_select_does_not_contain_bs_rules(self) -> None:
        config = get_profile_config(PROFILE_MINIMAL)
        assert not any(r.startswith("BS") for r in config["select"])

    def test_select_does_not_contain_bk_rules(self) -> None:
        config = get_profile_config(PROFILE_MINIMAL)
        assert not any(r.startswith("BK") for r in config["select"])

    def test_select_does_not_contain_bx_rules(self) -> None:
        config = get_profile_config(PROFILE_MINIMAL)
        assert not any(r.startswith("BX") for r in config["select"])

    def test_select_does_not_contain_bp_rules(self) -> None:
        config = get_profile_config(PROFILE_MINIMAL)
        assert not any(r.startswith("BP") for r in config["select"])

    def test_ignore_is_empty(self) -> None:
        config = get_profile_config(PROFILE_MINIMAL)
        assert config["ignore"] == []


# ---------------------------------------------------------------------------
# get_profile_config() — none
# ---------------------------------------------------------------------------


class TestGetProfileConfigNone:
    """Tests for the 'none' profile."""

    def test_returns_empty_select(self) -> None:
        config = get_profile_config(PROFILE_NONE)
        assert config["select"] == []

    def test_returns_empty_ignore(self) -> None:
        config = get_profile_config(PROFILE_NONE)
        assert config["ignore"] == []


# ---------------------------------------------------------------------------
# get_profile_config() — error handling
# ---------------------------------------------------------------------------


class TestGetProfileConfigErrorHandling:
    """Tests for error handling in get_profile_config()."""

    def test_invalid_name_raises(self) -> None:
        with pytest.raises(InvalidConfigValueError):
            get_profile_config("nonexistent")

    def test_empty_string_raises(self) -> None:
        with pytest.raises(InvalidConfigValueError):
            get_profile_config("")

    def test_error_message_contains_profile_name(self) -> None:
        with pytest.raises(InvalidConfigValueError) as exc_info:
            get_profile_config("bogus")
        assert "bogus" in str(exc_info.value)

    def test_error_message_contains_valid_options(self) -> None:
        with pytest.raises(InvalidConfigValueError) as exc_info:
            get_profile_config("bogus")
        msg = str(exc_info.value)
        assert "recommended" in msg
        assert "strict" in msg
        assert "minimal" in msg
        assert "none" in msg


# ---------------------------------------------------------------------------
# get_profile_config() — immutability
# ---------------------------------------------------------------------------


class TestGetProfileConfigImmutability:
    """Verify that get_profile_config returns fresh copies."""

    def test_returns_copies_not_references(self) -> None:
        c1 = get_profile_config(PROFILE_RECOMMENDED)
        c2 = get_profile_config(PROFILE_RECOMMENDED)
        assert c1["ignore"] == c2["ignore"]
        assert c1["ignore"] is not c2["ignore"]

    def test_returns_copies_for_select(self) -> None:
        c1 = get_profile_config(PROFILE_MINIMAL)
        c2 = get_profile_config(PROFILE_MINIMAL)
        assert c1["select"] == c2["select"]
        assert c1["select"] is not c2["select"]

    def test_modifying_returned_dict_does_not_affect_subsequent_calls(
        self,
    ) -> None:
        c1 = get_profile_config(PROFILE_RECOMMENDED)
        c1["ignore"].append("BC999")
        c2 = get_profile_config(PROFILE_RECOMMENDED)
        assert "BC999" not in c2["ignore"]


# ---------------------------------------------------------------------------
# Config.is_rule_enabled() with profiles
# ---------------------------------------------------------------------------


class TestConfigIsRuleEnabledWithProfiles:
    """Test Config.is_rule_enabled() under each profile."""

    def test_recommended_enables_bc_rules(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config(overrides={"profile": PROFILE_RECOMMENDED})
        assert config.is_rule_enabled("BC001")
        assert config.is_rule_enabled("BC010")

    def test_recommended_disables_bp_rules(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config(overrides={"profile": PROFILE_RECOMMENDED})
        assert not config.is_rule_enabled("BP001")
        assert not config.is_rule_enabled("BP007")

    def test_recommended_enables_bs_rules(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config(overrides={"profile": PROFILE_RECOMMENDED})
        assert config.is_rule_enabled("BS001")
        assert config.is_rule_enabled("BS008")

    def test_strict_enables_all_rules(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config(overrides={"profile": PROFILE_STRICT})
        assert config.is_rule_enabled("BC001")
        assert config.is_rule_enabled("BS001")
        assert config.is_rule_enabled("BP001")
        assert config.is_rule_enabled("BX001")

    def test_minimal_enables_only_bc_and_bd(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config(overrides={"profile": PROFILE_MINIMAL})
        assert config.is_rule_enabled("BC001")
        assert config.is_rule_enabled("BD005")
        assert not config.is_rule_enabled("BS001")
        assert not config.is_rule_enabled("BK001")
        assert not config.is_rule_enabled("BX001")
        assert not config.is_rule_enabled("BP001")

    def test_none_profile_enables_all(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config()
        assert config.is_rule_enabled("BC001")
        assert config.is_rule_enabled("BP001")
        assert config.is_rule_enabled("BS001")


# ---------------------------------------------------------------------------
# load_config() integration tests
# ---------------------------------------------------------------------------


class TestLoadConfigWithProfile:
    """Integration tests for load_config() with profiles."""

    def test_recommended_profile(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config(overrides={"profile": PROFILE_RECOMMENDED})
        assert config.profile == PROFILE_RECOMMENDED
        assert "BP001" in config.ignore
        assert config.select == []

    def test_strict_profile(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config(overrides={"profile": PROFILE_STRICT})
        assert config.profile == PROFILE_STRICT
        assert config.ignore == []
        assert config.select == []

    def test_minimal_profile(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config(overrides={"profile": PROFILE_MINIMAL})
        assert config.profile == PROFILE_MINIMAL
        assert config.select != []
        assert all(r.startswith("BC") or r.startswith("BD") for r in config.select)

    def test_no_profile_defaults_to_none(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config()
        assert config.profile == "none"

    def test_explicit_none_profile(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config(overrides={"profile": "none"})
        assert config.profile == "none"
        assert config.select == []
        assert config.ignore == []


class TestLoadConfigProfileOverrides:
    """Test that higher-precedence sources override profile settings."""

    def test_cli_select_overrides_profile_select(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config(
            overrides={"profile": PROFILE_MINIMAL, "select": ["BX001"]}
        )
        assert config.profile == PROFILE_MINIMAL
        assert config.select == ["BX001"]

    def test_cli_ignore_overrides_profile_ignore(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config(
            overrides={"profile": PROFILE_RECOMMENDED, "ignore": ["BC001"]}
        )
        assert config.profile == PROFILE_RECOMMENDED
        assert config.ignore == ["BC001"]

    def test_cli_select_and_ignore_override_profile(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config(
            overrides={
                "profile": PROFILE_STRICT,
                "select": ["BC001", "BC002"],
                "ignore": ["BS001"],
            }
        )
        assert config.profile == PROFILE_STRICT
        assert config.select == ["BC001", "BC002"]
        assert config.ignore == ["BS001"]

    def test_empty_select_overrides_profile_select(self) -> None:
        """Empty select in overrides replaces profile's select (list replacement)."""
        from behave_lint.configuration.loader import load_config

        config = load_config(overrides={"profile": PROFILE_MINIMAL, "select": []})
        assert config.profile == PROFILE_MINIMAL
        assert config.select == []


class TestLoadConfigProfileEnv:
    """Test profile resolution via environment variables."""

    def test_profile_via_env(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config(env={"BEHAVE_LINT_PROFILE": PROFILE_STRICT})
        assert config.profile == PROFILE_STRICT

    def test_profile_via_env_recommended(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config(env={"BEHAVE_LINT_PROFILE": PROFILE_RECOMMENDED})
        assert config.profile == PROFILE_RECOMMENDED
        assert "BP001" in config.ignore

    def test_profile_via_env_minimal(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config(env={"BEHAVE_LINT_PROFILE": PROFILE_MINIMAL})
        assert config.profile == PROFILE_MINIMAL
        assert config.select != []

    def test_cli_profile_overrides_env_profile(self) -> None:
        from behave_lint.configuration.loader import load_config

        config = load_config(
            overrides={"profile": PROFILE_STRICT},
            env={"BEHAVE_LINT_PROFILE": PROFILE_MINIMAL},
        )
        assert config.profile == PROFILE_STRICT
        assert config.select == []


class TestLoadConfigProfilePyproject:
    """Test profile resolution via pyproject.toml."""

    def test_profile_from_pyproject_toml(self, tmp_path: Path) -> None:
        from behave_lint.configuration.loader import load_config

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[tool.behave-lint]\nprofile = "recommended"\n',
            encoding="utf-8",
        )
        config = load_config(start_dir=tmp_path)
        assert config.profile == PROFILE_RECOMMENDED
        assert "BP001" in config.ignore

    def test_profile_from_pyproject_strict(self, tmp_path: Path) -> None:
        from behave_lint.configuration.loader import load_config

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[tool.behave-lint]\nprofile = "strict"\n',
            encoding="utf-8",
        )
        config = load_config(start_dir=tmp_path)
        assert config.profile == PROFILE_STRICT
        assert config.ignore == []

    def test_cli_profile_overrides_pyproject_profile(self, tmp_path: Path) -> None:
        from behave_lint.configuration.loader import load_config

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[tool.behave-lint]\nprofile = "minimal"\n',
            encoding="utf-8",
        )
        config = load_config(
            start_dir=tmp_path,
            overrides={"profile": PROFILE_STRICT},
        )
        assert config.profile == PROFILE_STRICT
        assert config.select == []

    def test_pyproject_select_overrides_profile_select(self, tmp_path: Path) -> None:
        from behave_lint.configuration.loader import load_config

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[tool.behave-lint]\nprofile = "minimal"\nselect = ["BX001", "BX002"]\n',
            encoding="utf-8",
        )
        config = load_config(start_dir=tmp_path)
        assert config.profile == PROFILE_MINIMAL
        assert config.select == ["BX001", "BX002"]


class TestLoadConfigProfilePrecedence:
    """Test full precedence chain: defaults < profile < pyproject < env < CLI."""

    def test_env_overrides_pyproject_profile(self, tmp_path: Path) -> None:
        from behave_lint.configuration.loader import load_config

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[tool.behave-lint]\nprofile = "minimal"\n',
            encoding="utf-8",
        )
        config = load_config(
            start_dir=tmp_path,
            env={"BEHAVE_LINT_PROFILE": PROFILE_STRICT},
        )
        assert config.profile == PROFILE_STRICT

    def test_cli_overrides_all(self, tmp_path: Path) -> None:
        from behave_lint.configuration.loader import load_config

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[tool.behave-lint]\nprofile = "recommended"\n',
            encoding="utf-8",
        )
        config = load_config(
            start_dir=tmp_path,
            env={"BEHAVE_LINT_PROFILE": PROFILE_STRICT},
            overrides={"profile": PROFILE_MINIMAL},
        )
        assert config.profile == PROFILE_MINIMAL


class TestLoadConfigProfileErrors:
    """Test error handling for invalid profiles."""

    def test_invalid_profile_raises(self) -> None:
        from behave_lint.configuration.loader import load_config

        with pytest.raises(InvalidConfigValueError):
            load_config(overrides={"profile": "nonexistent"})

    def test_invalid_profile_via_env_raises(self) -> None:
        from behave_lint.configuration.loader import load_config

        with pytest.raises(InvalidConfigValueError):
            load_config(env={"BEHAVE_LINT_PROFILE": "bogus"})

    def test_invalid_profile_in_pyproject_raises(self, tmp_path: Path) -> None:
        from behave_lint.configuration.loader import load_config

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[tool.behave-lint]\nprofile = "nonexistent"\n',
            encoding="utf-8",
        )
        with pytest.raises(InvalidConfigValueError):
            load_config(start_dir=tmp_path)


# ---------------------------------------------------------------------------
# Config.profile field
# ---------------------------------------------------------------------------


class TestConfigProfileField:
    """Test that Config.profile is correctly populated."""

    def test_default_profile_is_none(self) -> None:
        from behave_lint.models.config import Config

        config = Config()
        assert config.profile == "none"

    def test_profile_field_is_set(self) -> None:
        from behave_lint.configuration.loader import load_config

        for profile_name in [
            PROFILE_RECOMMENDED,
            PROFILE_STRICT,
            PROFILE_MINIMAL,
            PROFILE_NONE,
        ]:
            config = load_config(overrides={"profile": profile_name})
            assert config.profile == profile_name

    def test_profile_field_is_frozen(self) -> None:
        from behave_lint.models.config import Config

        config = Config(profile="strict")
        with pytest.raises(AttributeError):
            config.profile = "minimal"  # type: ignore[misc]
