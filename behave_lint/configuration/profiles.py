"""Built-in profiles — predefined rule sets for common use cases.

Profiles provide a convenient way to select groups of rules without
listing each rule ID individually. They are resolved early in the
configuration pipeline, before pyproject.toml and CLI overrides.

Resolution order:
1. Built-in defaults
2. Profile (if specified)
3. pyproject.toml [tool.behave-lint]
4. Environment variables (BEHAVE_LINT_*)
5. CLI overrides (highest)

A profile sets the ``select`` and ``ignore`` lists. Any explicit
``select`` or ``ignore`` from a higher-precedence source overrides
the profile's values.

Built-in profiles:
- ``recommended`` — all rules except pedantic (BP) and experimental.
- ``strict`` — all rules including pedantic.
- ``minimal`` — only correctness (BC) and step-definition (BD) rules.
"""

from __future__ import annotations

from behave_lint.exceptions import InvalidConfigValueError

# Profile name constants
PROFILE_RECOMMENDED = "recommended"
PROFILE_STRICT = "strict"
PROFILE_MINIMAL = "minimal"
PROFILE_NONE = "none"

# Built-in profile definitions.
# Each profile maps to a dict with "select" and "ignore" lists.
# An empty "select" means "all rules"; the "ignore" list excludes
# specific categories or rules.
_PROFILES: dict[str, dict[str, list[str]]] = {
    PROFILE_RECOMMENDED: {
        "select": [],
        "ignore": ["BP001", "BP002", "BP003", "BP004", "BP005", "BP006", "BP007"],
    },
    PROFILE_STRICT: {
        "select": [],
        "ignore": [],
    },
    PROFILE_MINIMAL: {
        "select": [
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
            "BD001",
            "BD002",
            "BD003",
            "BD004",
            "BD005",
        ],
        "ignore": [],
    },
}


def get_profile_names() -> list[str]:
    """Return the names of all built-in profiles.

    Returns:
        Sorted list of profile names.
    """
    return sorted(_PROFILES.keys())


def is_valid_profile(name: str) -> bool:
    """Check if a profile name is valid.

    Args:
        name: Profile name to check.

    Returns:
        True if the profile exists or is "none".
    """
    return name in _PROFILES or name == PROFILE_NONE


def get_profile_config(name: str) -> dict[str, object]:
    """Get the configuration dict for a profile.

    Args:
        name: Profile name.

    Returns:
        Dict with "select" and "ignore" keys.

    Raises:
        InvalidConfigValueError: If the profile name is not recognized.
    """
    if name == PROFILE_NONE:
        return {"select": [], "ignore": []}
    if name not in _PROFILES:
        valid = ", ".join(get_profile_names())
        raise InvalidConfigValueError(
            key="profile",
            value=name,
            expected=f"one of: {valid}, none",
        )
    profile = _PROFILES[name]
    return {
        "select": list(profile["select"]),
        "ignore": list(profile["ignore"]),
    }


__all__ = [
    "PROFILE_MINIMAL",
    "PROFILE_NONE",
    "PROFILE_RECOMMENDED",
    "PROFILE_STRICT",
    "get_profile_config",
    "get_profile_names",
    "is_valid_profile",
]
