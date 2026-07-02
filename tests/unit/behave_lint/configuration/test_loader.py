"""Unit tests for configuration loader — merge, env, and load_config().

See CONFIGURATION_SYSTEM.md Sections 2, 4, 10, 11.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from behave_lint.configuration.loader import (
    build_config,
    load_config,
    load_from_env,
    merge_configs,
)
from behave_lint.exceptions import InvalidConfigValueError
from behave_lint.models.config import Config
from behave_lint.models.enums import Severity


class TestMergeConfigs:
    """Tests for merge_configs()."""

    def test_scalar_replace(self) -> None:
        base = {"output": "console", "cache": True}
        override = {"output": "json"}
        result = merge_configs(base, override)
        assert result["output"] == "json"
        assert result["cache"] is True

    def test_list_replace(self) -> None:
        base = {"select": ["BC001", "BS001"]}
        override = {"select": ["BX001"]}
        result = merge_configs(base, override)
        assert result["select"] == ["BX001"]

    def test_dict_merge(self) -> None:
        base = {"severity": {"BC001": "error"}}
        override = {"severity": {"BS001": "info"}}
        result = merge_configs(base, override)
        assert result["severity"]["BC001"] == "error"
        assert result["severity"]["BS001"] == "info"

    def test_dict_override_key(self) -> None:
        base = {"severity": {"BC001": "error"}}
        override = {"severity": {"BC001": "warning"}}
        result = merge_configs(base, override)
        assert result["severity"]["BC001"] == "warning"

    def test_new_key_added(self) -> None:
        base = {"output": "console"}
        override = {"cache": False}
        result = merge_configs(base, override)
        assert result["output"] == "console"
        assert result["cache"] is False


class TestLoadFromEnv:
    """Tests for load_from_env()."""

    def test_output(self) -> None:
        result = load_from_env({"BEHAVE_LINT_OUTPUT": "json"})
        assert result["output"] == "json"

    def test_output_file(self) -> None:
        result = load_from_env({"BEHAVE_LINT_OUTPUT_FILE": "results.json"})
        assert result["output_file"] == "results.json"

    def test_no_cache_inverted(self) -> None:
        result = load_from_env({"BEHAVE_LINT_NO_CACHE": "1"})
        assert result["cache"] is False

    def test_no_cache_false(self) -> None:
        result = load_from_env({"BEHAVE_LINT_NO_CACHE": "0"})
        assert result["cache"] is True

    def test_cache_dir(self) -> None:
        result = load_from_env({"BEHAVE_LINT_CACHE_DIR": "/tmp/cache"})
        assert result["cache_dir"] == "/tmp/cache"

    def test_fail_on(self) -> None:
        result = load_from_env({"BEHAVE_LINT_FAIL_ON": "error"})
        assert result["fail_on"] == "error"

    def test_no_env_vars(self) -> None:
        result = load_from_env({})
        assert result == {}

    def test_ignores_unknown_prefix(self) -> None:
        result = load_from_env({"OTHER_VAR": "value"})
        assert result == {}


class TestBuildConfig:
    """Tests for build_config()."""

    def test_defaults(self) -> None:
        config = build_config({})
        assert isinstance(config, Config)
        assert config.select == []
        assert config.output == "console"
        assert config.paths == ["features/"]
        assert config.cache is True

    def test_with_values(self) -> None:
        config = build_config(
            {
                "select": ["BC001"],
                "ignore": ["BS001"],
                "output": "json",
                "cache": False,
            }
        )
        assert config.select == ["BC001"]
        assert config.ignore == ["BS001"]
        assert config.output == "json"
        assert config.cache is False

    def test_severity_overrides(self) -> None:
        config = build_config({"severity": {"BC001": "info"}})
        assert config.severity_overrides["BC001"] is Severity.INFO

    def test_invalid_severity_raises(self) -> None:
        with pytest.raises(InvalidConfigValueError):
            build_config({"severity": {"BC001": "critical"}})

    def test_fail_on(self) -> None:
        config = build_config({"fail_on": "error"})
        assert config.fail_on is Severity.ERROR

    def test_empty_output_file_becomes_none(self) -> None:
        config = build_config({"output_file": ""})
        assert config.output_file is None

    def test_empty_step_definitions_becomes_none(self) -> None:
        config = build_config({"step_definitions": ""})
        assert config.step_definitions is None


class TestLoadConfig:
    """Tests for the public load_config() function."""

    def test_no_config_file_returns_defaults(self, tmp_path: Path) -> None:
        config = load_config(start_dir=tmp_path, env={})
        assert config.select == []
        assert config.output == "console"
        assert config.paths == ["features/"]

    def test_with_pyproject_toml(self, tmp_path: Path) -> None:
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text(
            textwrap.dedent("""\
            [tool.behave-lint]
            select = ["BC001", "BS001"]
            output = "json"
            output-file = "results.json"
            cache = false
        """)
        )
        config = load_config(start_dir=tmp_path, env={})
        assert config.select == ["BC001", "BS001"]
        assert config.output == "json"
        assert config.output_file == "results.json"
        assert config.cache is False

    def test_env_overrides_pyproject(self, tmp_path: Path) -> None:
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text('[tool.behave-lint]\noutput = "console"\n')
        config = load_config(
            start_dir=tmp_path,
            env={"BEHAVE_LINT_OUTPUT": "json"},
        )
        assert config.output == "json"

    def test_explicit_overrides_env(self, tmp_path: Path) -> None:
        config = load_config(
            start_dir=tmp_path,
            env={"BEHAVE_LINT_OUTPUT": "json"},
            overrides={"output": "sarif"},
        )
        assert config.output == "sarif"

    def test_overrides_pyproject(self, tmp_path: Path) -> None:
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text('[tool.behave-lint]\nselect = ["BC001"]\n')
        config = load_config(
            start_dir=tmp_path,
            env={},
            overrides={"select": ["BS001"]},
        )
        assert config.select == ["BS001"]

    def test_severity_from_toml(self, tmp_path: Path) -> None:
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text(
            textwrap.dedent("""\
            [tool.behave-lint]
            severity = { BC001 = "info", BS001 = "error" }
        """)
        )
        config = load_config(start_dir=tmp_path, env={})
        assert config.severity_overrides["BC001"] is Severity.INFO
        assert config.severity_overrides["BS001"] is Severity.ERROR

    def test_no_cache_env(self, tmp_path: Path) -> None:
        config = load_config(
            start_dir=tmp_path,
            env={"BEHAVE_LINT_NO_CACHE": "1"},
        )
        assert config.cache is False

    def test_fail_on_from_toml(self, tmp_path: Path) -> None:
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text('[tool.behave-lint]\nfail-on = "error"\n')
        config = load_config(start_dir=tmp_path, env={})
        assert config.fail_on is Severity.ERROR

    def test_explicit_config_path(self, tmp_path: Path) -> None:
        config_file = tmp_path / "custom.toml"
        config_file.write_text('[tool.behave-lint]\noutput = "json"\n')
        config = load_config(
            config_path=str(config_file),
            env={},
            start_dir=tmp_path,
        )
        assert config.output == "json"

    def test_dict_merge_for_severity(self, tmp_path: Path) -> None:
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text(
            textwrap.dedent("""\
            [tool.behave-lint]
            severity = { BC001 = "error" }
        """)
        )
        config = load_config(
            start_dir=tmp_path,
            env={},
            overrides={"severity": {"BS001": "info"}},
        )
        assert config.severity_overrides["BC001"] is Severity.ERROR
        assert config.severity_overrides["BS001"] is Severity.INFO

    def test_importable_from_top_level(self) -> None:
        from behave_lint import load_config as lc

        assert callable(lc)

    def test_importable_from_config_module(self) -> None:
        from behave_lint.config import load_config as lc

        assert callable(lc)
