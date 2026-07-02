"""Configuration Manager — loading, merging, validation, defaults.

Application layer — component C02.

See COMPONENT_DESIGN.md Section 5 and CONFIGURATION_SYSTEM.md.
"""

from __future__ import annotations

from behave_lint.configuration.discovery import (
    find_config_file,
    load_toml_config,
)
from behave_lint.configuration.loader import (
    build_config,
    load_config,
    load_from_env,
    merge_configs,
)
from behave_lint.configuration.schema import (
    check_unknown_keys,
    normalize_keys,
    validate_fail_on,
    validate_severity_overrides,
    validate_types,
)

__all__ = [
    "build_config",
    "check_unknown_keys",
    "find_config_file",
    "load_config",
    "load_from_env",
    "load_toml_config",
    "merge_configs",
    "normalize_keys",
    "validate_fail_on",
    "validate_severity_overrides",
    "validate_types",
]
