"""Unit tests for configuration file discovery.

See CONFIGURATION_SYSTEM.md Section 3.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from behave_lint.configuration.discovery import (
    find_config_file,
    load_toml_config,
)
from behave_lint.exceptions import ConfigError


class TestFindConfigFile:
    """Tests for find_config_file()."""

    def test_explicit_path(self, tmp_path: Path) -> None:
        config = tmp_path / "pyproject.toml"
        config.write_text('[tool.behave-lint]\nselect = ["BC001"]\n')
        result = find_config_file(explicit_path=str(config))
        assert result == config

    def test_explicit_path_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(ConfigError, match="not found"):
            find_config_file(explicit_path=str(tmp_path / "nonexistent.toml"))

    def test_search_finds_in_current_dir(self, tmp_path: Path) -> None:
        config = tmp_path / "pyproject.toml"
        config.write_text('[tool.behave-lint]\noutput = "json"\n')
        result = find_config_file(start_dir=tmp_path)
        assert result == config

    def test_search_finds_in_parent(self, tmp_path: Path) -> None:
        parent_config = tmp_path / "pyproject.toml"
        parent_config.write_text('[tool.behave-lint]\nselect = ["BC001"]\n')
        subdir = tmp_path / "features" / "subdir"
        subdir.mkdir(parents=True)
        result = find_config_file(start_dir=subdir)
        assert result == parent_config

    def test_search_no_config_file(self, tmp_path: Path) -> None:
        result = find_config_file(start_dir=tmp_path)
        assert result is None

    def test_skips_pyproject_without_section(self, tmp_path: Path) -> None:
        config = tmp_path / "pyproject.toml"
        config.write_text('[tool.other]\nkey = "value"\n')
        result = find_config_file(start_dir=tmp_path)
        assert result is None


class TestLoadTomlConfig:
    """Tests for load_toml_config()."""

    def test_loads_config_section(self, tmp_path: Path) -> None:
        config = tmp_path / "pyproject.toml"
        config.write_text(
            textwrap.dedent("""\
            [tool.behave-lint]
            select = ["BC001", "BS001"]
            output = "json"

            [tool.other]
            key = "value"
        """)
        )
        result = load_toml_config(config)
        assert result["select"] == ["BC001", "BS001"]
        assert result["output"] == "json"

    def test_no_section_returns_empty(self, tmp_path: Path) -> None:
        config = tmp_path / "pyproject.toml"
        config.write_text('[tool.other]\nkey = "value"\n')
        result = load_toml_config(config)
        assert result == {}

    def test_invalid_toml_raises(self, tmp_path: Path) -> None:
        config = tmp_path / "pyproject.toml"
        config.write_text("invalid toml [[[[")
        with pytest.raises(ConfigError, match="Invalid TOML"):
            load_toml_config(config)

    @pytest.mark.skipif(
        __import__("sys").platform == "win32",
        reason="chmod does not prevent reads on Windows",
    )
    def test_unreadable_file_raises(self, tmp_path: Path) -> None:
        config = tmp_path / "pyproject.toml"
        config.write_text("[tool.behave-lint]\nselect = []\n")
        config.chmod(0o000)
        try:
            with pytest.raises(ConfigError, match="Cannot read"):
                load_toml_config(config)
        finally:
            config.chmod(0o644)
