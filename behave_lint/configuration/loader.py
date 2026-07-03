"""Configuration loader — merge all sources and produce a Config object.

Sources merged by precedence (lowest to highest):
1. Built-in defaults
2. pyproject.toml [tool.behave-lint]
3. Environment variables (BEHAVE_LINT_*)
4. CLI overrides (passed as dict to load_config)

Merge rules:
- Scalars: highest precedence wins (replaces).
- Lists: highest precedence wins (replaces, no concatenation).
- Dicts: merged (highest precedence keys override matching lower keys).

See CONFIGURATION_SYSTEM.md Sections 2, 4, 10, 11.
"""

from __future__ import annotations

import os
from pathlib import Path

from behave_lint.configuration.defaults import (
    ENV_BOOL_VARS,
    ENV_INVERTED_BOOLS,
    ENV_PREFIX,
    ENV_VAR_MAP,
    _default_config_dict,
    _parse_bool_env,
)
from behave_lint.configuration.discovery import (
    find_config_file,
    load_toml_config,
)
from behave_lint.configuration.schema import (
    check_unknown_keys,
    normalize_keys,
    validate_fail_on,
    validate_severity_overrides,
    validate_types,
)
from behave_lint.exceptions import InvalidConfigValueError
from behave_lint.models.config import Config

# Config fields that are dicts (merged rather than replaced)
_DICT_FIELDS: frozenset[str] = frozenset(
    {"severity", "severity_overrides", "plugins", "rule_params", "rules"}
)

# Config fields that are lists (replaced, not concatenated)
_LIST_FIELDS: frozenset[str] = frozenset(
    {"select", "ignore", "paths", "exclude", "group"}
)


def load_from_env(env: dict[str, str] | None = None) -> dict[str, object]:
    """Extract configuration overrides from environment variables.

    Args:
        env: Environment dict. If None, uses os.environ.

    Returns:
        Dict of config overrides from environment variables.
    """
    if env is None:
        env = dict(os.environ)

    result: dict[str, object] = {}
    for env_key, config_key in ENV_VAR_MAP.items():
        full_key = f"{ENV_PREFIX}{env_key}"
        raw_value = env.get(full_key)
        if raw_value is None:
            continue

        if env_key in ENV_BOOL_VARS:
            bool_val = _parse_bool_env(raw_value)
            if env_key in ENV_INVERTED_BOOLS:
                result[config_key] = not bool_val
            else:
                result[config_key] = bool_val
        else:
            result[config_key] = raw_value

    return result


def merge_configs(
    base: dict[str, object],
    override: dict[str, object],
) -> dict[str, object]:
    """Merge two configuration dicts following precedence rules.

    Args:
        base: Lower-precedence config dict.
        override: Higher-precedence config dict.

    Returns:
        Merged dict.
    """
    result = dict(base)
    for key, value in override.items():
        if (
            key in _DICT_FIELDS
            and isinstance(value, dict)
            and isinstance(result.get(key), dict)
        ):
            merged = dict(result[key])  # type: ignore[call-overload]
            merged.update(value)
            result[key] = merged
        else:
            result[key] = value
    return result


def build_config(merged: dict[str, object]) -> Config:
    """Build a Config object from a merged configuration dict.

    Performs final validation and type conversion.

    Args:
        merged: Fully merged configuration dict.

    Returns:
        A frozen Config object.

    Raises:
        InvalidConfigValueError: If any value is invalid.
    """
    validate_types(merged)

    severity_raw = merged.get("severity", {})
    if not isinstance(severity_raw, dict):
        severity_raw = {}
    severity_overrides = validate_severity_overrides(
        {k: str(v) for k, v in severity_raw.items()}
    )

    fail_on_raw = merged.get("fail_on", "warning")
    if not isinstance(fail_on_raw, str):
        fail_on_raw = "warning"
    fail_on = validate_fail_on(fail_on_raw)

    output_file = merged.get("output_file")
    if output_file == "" or output_file is None:
        output_file = None

    step_definitions = merged.get("step_definitions")
    if step_definitions == "" or step_definitions is None:
        step_definitions = None

    select = merged.get("select", [])
    if not isinstance(select, list):
        select = []
    ignore = merged.get("ignore", [])
    if not isinstance(ignore, list):
        ignore = []

    profile = merged.get("profile", "none")
    if not isinstance(profile, str):
        profile = "none"

    group_raw = merged.get("group", [])
    if isinstance(group_raw, str):
        from behave_lint.configuration.groups import parse_groups

        group = parse_groups(group_raw)
    elif isinstance(group_raw, list):
        group = list(group_raw)
    else:
        group = []

    paths = merged.get("paths", ["features/"])
    if not isinstance(paths, list):
        paths = ["features/"]

    exclude = merged.get("exclude", [])
    if not isinstance(exclude, list):
        exclude = []

    plugins = merged.get("plugins", {})
    if not isinstance(plugins, dict):
        plugins = {}

    rule_params = merged.get("rules", {})
    if not isinstance(rule_params, dict):
        rule_params = {}

    cache = merged.get("cache", True)
    if not isinstance(cache, bool):
        cache = True

    cache_dir = merged.get("cache_dir", ".behave-lint-cache")
    if not isinstance(cache_dir, str):
        cache_dir = ".behave-lint-cache"

    output = merged.get("output", "console")
    if not isinstance(output, str):
        output = "console"

    max_warnings = merged.get("max_warnings", -1)
    if not isinstance(max_warnings, int):
        max_warnings = -1

    return Config(
        select=list(select),
        ignore=list(ignore),
        profile=profile,
        group=list(group),
        severity_overrides=severity_overrides,
        output=output,
        output_file=output_file if isinstance(output_file, str) else None,
        paths=list(paths),
        exclude=list(exclude),
        step_definitions=(
            step_definitions if isinstance(step_definitions, str) else None
        ),
        cache=cache,
        cache_dir=cache_dir,
        plugins=plugins,
        rule_params=rule_params,
        fail_on=fail_on,
        max_warnings=max_warnings,
    )


def _build_rule_mappings() -> tuple[set[str], dict[str, set[str]]]:
    """Build rule ID and tag mappings from built-in rules.

    Used by group expansion to map group names to rule IDs.

    Returns:
        Tuple of (all rule IDs, rule ID -> tags mapping).
    """
    from behave_lint.rules.builtin import _BUILTIN_RULES

    all_ids: set[str] = set()
    rule_tags: dict[str, set[str]] = {}
    for rule_class in _BUILTIN_RULES:
        metadata = getattr(rule_class, "metadata", None)
        if metadata is None:
            continue
        rule_id = metadata.rule_id
        all_ids.add(rule_id)
        rule_tags[rule_id] = set(metadata.tags)
    return all_ids, rule_tags


def load_config(
    *,
    config_path: str | None = None,
    overrides: dict[str, object] | None = None,
    env: dict[str, str] | None = None,
    start_dir: Path | None = None,
) -> Config:
    """Load and resolve configuration from all sources.

    Merges configuration from four sources by precedence:
    1. Built-in defaults (lowest)
    2. pyproject.toml [tool.behave-lint]
    3. Environment variables (BEHAVE_LINT_*)
    4. Explicit overrides (highest)

    Args:
        config_path: Explicit path to a pyproject.toml. If None,
            searches the current directory and ancestors.
        overrides: Dictionary of configuration overrides (same keys as
            Config fields). These have the highest precedence.
        env: Environment dict. If None, uses os.environ.
        start_dir: Directory to start searching from. Defaults to cwd.

    Returns:
        A resolved Config object.

    Raises:
        ConfigError: If configuration is invalid (unknown key, invalid
            value, invalid severity).
    """
    # 1. Built-in defaults
    merged = _default_config_dict()

    # 2. Load pyproject.toml (if any)
    config_file = find_config_file(start_dir=start_dir, explicit_path=config_path)
    toml_config: dict[str, object] = {}
    if config_file is not None:
        raw_toml = load_toml_config(config_file)
        check_unknown_keys(raw_toml)
        toml_config = normalize_keys(raw_toml)

    # 3. Determine profile from highest-precedence source:
    #    CLI overrides > env > pyproject.toml > defaults
    profile_name = "none"
    if overrides is not None:
        profile_name = str(overrides.get("profile", "none"))
    if profile_name == "none":
        env_profile = env.get(f"{ENV_PREFIX}PROFILE") if env else None
        if env_profile is None:
            import os

            env_profile = os.environ.get(f"{ENV_PREFIX}PROFILE")
        if env_profile:
            profile_name = env_profile
    if profile_name == "none":
        toml_profile = toml_config.get("profile", "none")
        if isinstance(toml_profile, str):
            profile_name = toml_profile

    # 4. Apply profile (after defaults, before pyproject.toml values)
    if profile_name != "none":
        from behave_lint.configuration.profiles import get_profile_config

        profile_config = get_profile_config(profile_name)
        merged = merge_configs(merged, profile_config)
        merged["profile"] = profile_name

    # 4b. Determine groups from highest-precedence source:
    #     CLI overrides > env > pyproject.toml > defaults
    group_names: list[str] = []
    if overrides is not None:
        group_raw = overrides.get("group", [])
        if isinstance(group_raw, str):
            from behave_lint.configuration.groups import parse_groups

            group_names = parse_groups(group_raw)
        elif isinstance(group_raw, list):
            group_names = list(group_raw)
    if not group_names:
        env_group = env.get(f"{ENV_PREFIX}GROUP") if env else None
        if env_group is None:
            import os

            env_group = os.environ.get(f"{ENV_PREFIX}GROUP")
        if env_group:
            from behave_lint.configuration.groups import parse_groups

            group_names = parse_groups(env_group)
    if not group_names:
        toml_group = toml_config.get("group", [])
        if isinstance(toml_group, str):
            from behave_lint.configuration.groups import parse_groups

            group_names = parse_groups(toml_group)
        elif isinstance(toml_group, list):
            group_names = list(toml_group)

    # 4c. Record group names for later expansion
    if group_names:
        merged["group"] = group_names

    # 5. pyproject.toml values (override profile)
    if toml_config:
        merged = merge_configs(merged, toml_config)

    # 6. Environment variables
    env_overrides = load_from_env(env)
    merged = merge_configs(merged, env_overrides)

    # 7. Explicit overrides (highest precedence)
    if overrides is not None:
        normalized_overrides = normalize_keys(overrides)
        merged = merge_configs(merged, normalized_overrides)

    # 8. Expand groups to rule IDs (after all merges, additive to select)
    final_groups = merged.get("group", [])
    if isinstance(final_groups, str):
        from behave_lint.configuration.groups import parse_groups

        final_groups = parse_groups(final_groups)
        merged["group"] = final_groups
    if isinstance(final_groups, list) and final_groups:
        from behave_lint.configuration.groups import (
            get_category_prefix,
            get_group_tags,
            is_category_group,
            is_valid_group,
        )

        for gname in final_groups:
            if not is_valid_group(gname):
                from behave_lint.configuration.groups import get_group_names

                valid = ", ".join(get_group_names())
                raise InvalidConfigValueError(
                    key="group",
                    value=gname,
                    expected=f"one of: {valid}",
                )

        all_rule_ids, rule_tags_map = _build_rule_mappings()

        group_rule_ids: set[str] = set()
        for gname in final_groups:
            if is_category_group(gname):
                prefix = get_category_prefix(gname)
                if prefix:
                    for rule_id in all_rule_ids:
                        if rule_id.startswith(prefix):
                            group_rule_ids.add(rule_id)
            else:
                tags = get_group_tags(gname)
                if tags:
                    for rule_id, rule_tags in rule_tags_map.items():
                        if tags & rule_tags:
                            group_rule_ids.add(rule_id)

        if group_rule_ids:
            existing_select = merged.get("select", [])
            if not isinstance(existing_select, list):
                existing_select = []
            merged["select"] = list(
                set(existing_select) | group_rule_ids,
            )

    return build_config(merged)


__all__ = [
    "build_config",
    "load_config",
    "load_from_env",
    "merge_configs",
]
