"""Configuration defaults, known keys, and environment variable mappings.

These constants define the built-in defaults, the set of recognized
configuration keys, and the mapping between environment variables and
config fields.

See CONFIGURATION_SYSTEM.md Sections 2, 5, and 10.
"""

from __future__ import annotations

from behave_lint.constants import ENV_PREFIX

# --- Known top-level configuration keys ---

KNOWN_CONFIG_KEYS: frozenset[str] = frozenset(
    {
        "select",
        "ignore",
        "severity",
        "output",
        "output_file",
        "output-file",
        "paths",
        "step_definitions",
        "step-definitions",
        "exclude",
        "cache",
        "cache_dir",
        "cache-dir",
        "extends",
        "fail_on",
        "fail-on",
        "plugins",
        "rules",
        "max_warnings",
        "max-warnings",
    }
)

# Keys that use kebab-case in TOML but map to snake_case in Config
KEY_ALIASES: dict[str, str] = {
    "output-file": "output_file",
    "step-definitions": "step_definitions",
    "cache-dir": "cache_dir",
    "fail-on": "fail_on",
    "max-warnings": "max_warnings",
}

# --- Built-in defaults ---

DEFAULT_SELECT: list[str] = []
DEFAULT_IGNORE: list[str] = []
DEFAULT_OUTPUT: str = "console"
DEFAULT_OUTPUT_FILE: str | None = None
DEFAULT_PATHS: list[str] = ["features/"]
DEFAULT_STEP_DEFINITIONS: str | None = None
DEFAULT_EXCLUDE: list[str] = []
DEFAULT_CACHE: bool = True
DEFAULT_CACHE_DIR: str = ".behave-lint-cache"
DEFAULT_FAIL_ON: str = "warning"
DEFAULT_MAX_WARNINGS: int = -1

# --- Environment variable mappings ---

# Maps env var name (without prefix) to config field name
ENV_VAR_MAP: dict[str, str] = {
    "OUTPUT": "output",
    "OUTPUT_FILE": "output_file",
    "NO_CACHE": "cache",
    "CACHE_DIR": "cache_dir",
    "FAIL_ON": "fail_on",
}

# Env vars that are boolean flags (value "1"/"true"/"yes" = True)
ENV_BOOL_VARS: frozenset[str] = frozenset({"NO_CACHE"})

# Env vars that are inverted booleans (NO_CACHE=1 means cache=False)
ENV_INVERTED_BOOLS: frozenset[str] = frozenset({"NO_CACHE"})

# Env vars that don't map to Config fields (internal use)
ENV_INTERNAL_VARS: frozenset[str] = frozenset({"TRACE", "CONFIG"})


def _default_config_dict() -> dict[str, object]:
    """Return a dict of built-in default configuration values.

    Returns:
        A dictionary with all default config values.
    """
    return {
        "select": list(DEFAULT_SELECT),
        "ignore": list(DEFAULT_IGNORE),
        "severity_overrides": {},
        "output": DEFAULT_OUTPUT,
        "output_file": DEFAULT_OUTPUT_FILE,
        "paths": list(DEFAULT_PATHS),
        "exclude": list(DEFAULT_EXCLUDE),
        "step_definitions": DEFAULT_STEP_DEFINITIONS,
        "cache": DEFAULT_CACHE,
        "cache_dir": DEFAULT_CACHE_DIR,
        "plugins": {},
        "rule_params": {},
        "fail_on": DEFAULT_FAIL_ON,
        "max_warnings": DEFAULT_MAX_WARNINGS,
    }


def _parse_bool_env(value: str) -> bool:
    """Parse a boolean environment variable value.

    Args:
        value: The raw environment variable value.

    Returns:
        True for "1", "true", "yes" (case-insensitive), False otherwise.
    """
    return value.strip().lower() in ("1", "true", "yes")


__all__ = [
    "DEFAULT_CACHE",
    "DEFAULT_CACHE_DIR",
    "DEFAULT_EXCLUDE",
    "DEFAULT_FAIL_ON",
    "DEFAULT_IGNORE",
    "DEFAULT_MAX_WARNINGS",
    "DEFAULT_OUTPUT",
    "DEFAULT_OUTPUT_FILE",
    "DEFAULT_PATHS",
    "DEFAULT_SELECT",
    "DEFAULT_STEP_DEFINITIONS",
    "ENV_BOOL_VARS",
    "ENV_INTERNAL_VARS",
    "ENV_INVERTED_BOOLS",
    "ENV_PREFIX",
    "ENV_VAR_MAP",
    "KEY_ALIASES",
    "KNOWN_CONFIG_KEYS",
]
