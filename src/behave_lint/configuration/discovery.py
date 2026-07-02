"""Configuration file discovery — locate pyproject.toml with parent search.

Discovery order:
1. Explicit path (if provided).
2. Current directory → parent directories (walk up to filesystem root).
3. Defaults (if no file found).

See CONFIGURATION_SYSTEM.md Section 3.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from behave_lint.exceptions import ConfigError

CONFIG_SECTION = "tool"
CONFIG_SUBSECTION = "behave-lint"


def find_config_file(
    start_dir: Path | None = None,
    *,
    explicit_path: str | None = None,
) -> Path | None:
    """Find the pyproject.toml containing a [tool.behave-lint] section.

    Args:
        start_dir: Directory to start searching from. Defaults to cwd.
        explicit_path: Explicit path to a config file. If provided,
            no search is performed.

    Returns:
        Path to the configuration file, or None if not found.

    Raises:
        ConfigError: If an explicit path is provided but does not exist
            or is not a valid TOML file.
    """
    if explicit_path is not None:
        path = Path(explicit_path)
        if not path.exists():
            raise ConfigError(f"Configuration file not found: {explicit_path}")
        return path

    search_dir = start_dir if start_dir is not None else Path.cwd()
    return _search_upwards(search_dir)


def _search_upwards(start: Path) -> Path | None:
    """Search for pyproject.toml from start directory upwards.

    Stops at the first pyproject.toml that contains a
    [tool.behave-lint] section.

    Args:
        start: Directory to start searching from.

    Returns:
        Path to the configuration file, or None if not found.
    """
    current = start.resolve()
    while True:
        candidate = current / "pyproject.toml"
        if candidate.is_file() and _has_config_section(candidate):
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _has_config_section(path: Path) -> bool:
    """Check if a pyproject.toml contains a [tool.behave-lint] section.

    Args:
        path: Path to the pyproject.toml file.

    Returns:
        True if the file contains the section, False otherwise.
    """
    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError):
        return False
    tool = data.get(CONFIG_SECTION, {})
    return CONFIG_SUBSECTION in tool


def load_toml_config(path: Path) -> dict[str, object]:
    """Load and parse a pyproject.toml file, returning the config section.

    Args:
        path: Path to the pyproject.toml file.

    Returns:
        The contents of the [tool.behave-lint] section as a dict,
        or an empty dict if the section is not present.

    Raises:
        ConfigError: If the file contains invalid TOML.
    """
    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(
            f"Invalid TOML in configuration file '{path}': {exc}"
        ) from exc
    except OSError as exc:
        raise ConfigError(f"Cannot read configuration file '{path}': {exc}") from exc

    tool = data.get(CONFIG_SECTION, {})
    if not isinstance(tool, dict):
        return {}
    section = tool.get(CONFIG_SUBSECTION, {})
    if not isinstance(section, dict):
        return {}
    return dict(section)


__all__ = [
    "CONFIG_SECTION",
    "CONFIG_SUBSECTION",
    "find_config_file",
    "load_toml_config",
]
