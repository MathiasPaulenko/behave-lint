"""Unit tests for configuration defaults and constants.

See CONFIGURATION_SYSTEM.md Sections 2, 5, and 10.
"""

from __future__ import annotations

from behave_lint.configuration.defaults import (
    DEFAULT_CACHE,
    DEFAULT_CACHE_DIR,
    DEFAULT_IGNORE,
    DEFAULT_OUTPUT,
    DEFAULT_PATHS,
    DEFAULT_SELECT,
    ENV_BOOL_VARS,
    ENV_INTERNAL_VARS,
    ENV_INVERTED_BOOLS,
    ENV_VAR_MAP,
    KEY_ALIASES,
    KNOWN_CONFIG_KEYS,
    _default_config_dict,
    _parse_bool_env,
)


class TestKnownConfigKeys:
    """Tests for KNOWN_CONFIG_KEYS."""

    def test_contains_select(self) -> None:
        assert "select" in KNOWN_CONFIG_KEYS

    def test_contains_ignore(self) -> None:
        assert "ignore" in KNOWN_CONFIG_KEYS

    def test_contains_severity(self) -> None:
        assert "severity" in KNOWN_CONFIG_KEYS

    def test_contains_output(self) -> None:
        assert "output" in KNOWN_CONFIG_KEYS

    def test_contains_cache(self) -> None:
        assert "cache" in KNOWN_CONFIG_KEYS

    def test_contains_kebab_case_aliases(self) -> None:
        assert "output-file" in KNOWN_CONFIG_KEYS
        assert "cache-dir" in KNOWN_CONFIG_KEYS
        assert "fail-on" in KNOWN_CONFIG_KEYS
        assert "step-definitions" in KNOWN_CONFIG_KEYS


class TestKeyAliases:
    """Tests for KEY_ALIASES."""

    def test_output_file(self) -> None:
        assert KEY_ALIASES["output-file"] == "output_file"

    def test_cache_dir(self) -> None:
        assert KEY_ALIASES["cache-dir"] == "cache_dir"

    def test_fail_on(self) -> None:
        assert KEY_ALIASES["fail-on"] == "fail_on"

    def test_step_definitions(self) -> None:
        assert KEY_ALIASES["step-definitions"] == "step_definitions"


class TestDefaults:
    """Tests for default values."""

    def test_default_select(self) -> None:
        assert DEFAULT_SELECT == []

    def test_default_ignore(self) -> None:
        assert DEFAULT_IGNORE == []

    def test_default_output(self) -> None:
        assert DEFAULT_OUTPUT == "console"

    def test_default_paths(self) -> None:
        assert DEFAULT_PATHS == ["features/"]

    def test_default_cache(self) -> None:
        assert DEFAULT_CACHE is True

    def test_default_cache_dir(self) -> None:
        assert DEFAULT_CACHE_DIR == ".behave-lint-cache"


class TestDefaultConfigDict:
    """Tests for _default_config_dict()."""

    def test_returns_all_keys(self) -> None:
        d = _default_config_dict()
        assert "select" in d
        assert "ignore" in d
        assert "severity_overrides" in d
        assert "output" in d
        assert "output_file" in d
        assert "paths" in d
        assert "step_definitions" in d
        assert "cache" in d
        assert "cache_dir" in d
        assert "plugins" in d
        assert "rule_params" in d
        assert "fail_on" in d
        assert "max_warnings" in d

    def test_fail_on_is_warning(self) -> None:
        d = _default_config_dict()
        assert d["fail_on"] == "warning"

    def test_returns_independent_lists(self) -> None:
        d1 = _default_config_dict()
        d2 = _default_config_dict()
        assert d1["select"] is not d2["select"]
        assert d1["paths"] is not d2["paths"]


class TestEnvVarMap:
    """Tests for environment variable mappings."""

    def test_output_mapping(self) -> None:
        assert ENV_VAR_MAP["OUTPUT"] == "output"

    def test_output_file_mapping(self) -> None:
        assert ENV_VAR_MAP["OUTPUT_FILE"] == "output_file"

    def test_no_cache_mapping(self) -> None:
        assert ENV_VAR_MAP["NO_CACHE"] == "cache"

    def test_cache_dir_mapping(self) -> None:
        assert ENV_VAR_MAP["CACHE_DIR"] == "cache_dir"

    def test_fail_on_mapping(self) -> None:
        assert ENV_VAR_MAP["FAIL_ON"] == "fail_on"

    def test_no_cache_is_bool(self) -> None:
        assert "NO_CACHE" in ENV_BOOL_VARS

    def test_no_cache_is_inverted(self) -> None:
        assert "NO_CACHE" in ENV_INVERTED_BOOLS

    def test_trace_is_internal(self) -> None:
        assert "TRACE" in ENV_INTERNAL_VARS

    def test_config_is_internal(self) -> None:
        assert "CONFIG" in ENV_INTERNAL_VARS


class TestParseBoolEnv:
    """Tests for _parse_bool_env()."""

    def test_true_values(self) -> None:
        assert _parse_bool_env("1") is True
        assert _parse_bool_env("true") is True
        assert _parse_bool_env("TRUE") is True
        assert _parse_bool_env("yes") is True
        assert _parse_bool_env("Yes") is True

    def test_false_values(self) -> None:
        assert _parse_bool_env("0") is False
        assert _parse_bool_env("false") is False
        assert _parse_bool_env("no") is False
        assert _parse_bool_env("") is False
        assert _parse_bool_env("anything") is False
