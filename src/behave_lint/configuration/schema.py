"""Configuration validation — schema, type checking, unknown key detection.

Validates raw configuration dicts from any source (TOML, env, CLI)
before they are merged into a Config object.

See CONFIGURATION_SYSTEM.md Section 12.
"""

from __future__ import annotations

import warnings

from behave_lint.configuration.defaults import KEY_ALIASES, KNOWN_CONFIG_KEYS
from behave_lint.exceptions import InvalidConfigValueError
from behave_lint.models.enums import Severity

# Expected types for each config key (after alias normalization).
# None means the value can be None (nullable fields).
_EXPECTED_TYPES: dict[str, type | tuple[type, ...] | None] = {
    "select": list,
    "ignore": list,
    "severity": dict,
    "output": str,
    "output_file": (str, type(None)),
    "paths": list,
    "step_definitions": (str, type(None)),
    "exclude": list,
    "cache": bool,
    "cache_dir": str,
    "extends": str,
    "fail_on": str,
    "plugins": dict,
    "rules": dict,
    "max_warnings": int,
}


def normalize_keys(raw: dict[str, object]) -> dict[str, object]:
    """Normalize kebab-case keys to snake_case.

    Args:
        raw: Raw configuration dict with potential kebab-case keys.

    Returns:
        Dict with all keys normalized to snake_case.
    """
    normalized: dict[str, object] = {}
    for key, value in raw.items():
        normalized_key = KEY_ALIASES.get(key, key)
        normalized[normalized_key] = value
    return normalized


def check_unknown_keys(raw: dict[str, object]) -> list[str]:
    """Detect unknown configuration keys and emit warnings.

    Args:
        raw: Raw configuration dict (before normalization).

    Returns:
        List of unknown key names.
    """
    unknown: list[str] = []
    for key in raw:
        if key not in KNOWN_CONFIG_KEYS:
            unknown.append(key)
            warnings.warn(
                f"Unknown configuration key '{key}'.",
                stacklevel=2,
            )
    return unknown


def validate_types(
    normalized: dict[str, object],
) -> None:
    """Validate that each config value has the expected type.

    Args:
        normalized: Normalized configuration dict.

    Raises:
        InvalidConfigValueError: If a value has an unexpected type.
    """
    for key, value in normalized.items():
        expected_type = _EXPECTED_TYPES.get(key)
        if expected_type is None:
            continue
        if not isinstance(value, expected_type):
            type_name = (
                expected_type.__name__
                if isinstance(expected_type, type)
                else " or ".join(
                    t.__name__ if t is not type(None) else "None" for t in expected_type
                )
            )
            actual_type = type(value).__name__
            raise InvalidConfigValueError(
                key=key,
                value=str(value),
                expected=f"{type_name} (got {actual_type})",
            )


def validate_severity_overrides(
    severity: dict[str, str],
) -> dict[str, Severity]:
    """Validate and convert severity override strings to Severity enums.

    Args:
        severity: Dict mapping rule IDs to severity strings.

    Returns:
        Dict mapping rule IDs to Severity enum members.

    Raises:
        InvalidConfigValueError: If a severity string is invalid.
    """
    result: dict[str, Severity] = {}
    for rule_id, sev_str in severity.items():
        try:
            result[rule_id] = Severity.from_string(sev_str)
        except ValueError:
            valid = ", ".join(s.value for s in Severity)
            raise InvalidConfigValueError(
                key=f"severity.{rule_id}",
                value=sev_str,
                expected=valid,
            ) from None
    return result


def validate_fail_on(value: str) -> Severity:
    """Validate and convert a fail_on string to a Severity enum.

    Args:
        value: Severity string from configuration.

    Returns:
        The corresponding Severity member.

    Raises:
        InvalidConfigValueError: If the value is not a valid severity.
    """
    try:
        return Severity.from_string(value)
    except ValueError:
        valid = ", ".join(s.value for s in Severity)
        raise InvalidConfigValueError(
            key="fail_on",
            value=value,
            expected=valid,
        ) from None


__all__ = [
    "check_unknown_keys",
    "normalize_keys",
    "validate_fail_on",
    "validate_severity_overrides",
    "validate_types",
]
