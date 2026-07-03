"""Built-in groups — category and tag-based rule collections.

Groups provide a convenient way to select rules by category or tag
without listing each rule ID individually. Unlike profiles (which set
both ``select`` and ``ignore``), groups only add to the ``select``
list and are additive — multiple groups can be combined.

Resolution order (same as profiles):
1. Built-in defaults
2. Profile (if specified)
3. Groups (if specified)
4. pyproject.toml [tool.behave-lint]
5. Environment variables (BEHAVE_LINT_*)
6. CLI overrides (highest)

A group expands to a list of rule IDs. When a group is specified,
those rule IDs are added to the ``select`` list. If ``select`` is
empty and a group is specified, only the group's rules are enabled.

Built-in groups (category-based):
- ``correctness`` — all BC rules (definitively wrong structures).
- ``style`` — all BS rules (stylistic conventions).
- ``pedantic`` — all BP rules (strict best practices, opt-in).
- ``step-definitions`` — all BD rules (cross-reference with step defs).
- ``consistency`` — all BK rules (cross-file consistency).

Built-in groups (tag-based):
- ``naming`` — rules related to naming conventions.
- ``tags`` — rules related to tag usage.
- ``steps`` — rules related to step content and phrasing.
- ``background`` — rules related to Background sections.
- ``description`` — rules related to feature/scenario descriptions.
- ``documentation`` — rules related to documentation completeness.
- ``formatting`` — rules related to whitespace and formatting.
- ``examples`` — rules related to Examples tables.
- ``scenarios`` — rules related to scenario structure.
- ``readability`` — rules related to readability improvements.
"""

from __future__ import annotations

from behave_lint.exceptions import InvalidConfigValueError

# Category-based group names (map to Category enum values)
GROUP_CORRECTNESS = "correctness"
GROUP_STYLE = "style"
GROUP_PEDANTIC = "pedantic"
GROUP_STEP_DEFINITIONS = "step-definitions"
GROUP_CONSISTENCY = "consistency"

# Tag-based group names
GROUP_NAMING = "naming"
GROUP_TAGS = "tags"
GROUP_STEPS = "steps"
GROUP_BACKGROUND = "background"
GROUP_DESCRIPTION = "description"
GROUP_DOCUMENTATION = "documentation"
GROUP_FORMATTING = "formatting"
GROUP_EXAMPLES = "examples"
GROUP_SCENARIOS = "scenarios"
GROUP_READABILITY = "readability"

# Category prefix mapping (group name -> rule ID prefix)
_CATEGORY_PREFIXES: dict[str, str] = {
    GROUP_CORRECTNESS: "BC",
    GROUP_STYLE: "BS",
    GROUP_PEDANTIC: "BP",
    GROUP_STEP_DEFINITIONS: "BD",
    GROUP_CONSISTENCY: "BK",
}

# Tag-based group definitions (group name -> set of tags that match)
_TAG_GROUPS: dict[str, set[str]] = {
    GROUP_NAMING: {"naming"},
    GROUP_TAGS: {"tags"},
    GROUP_STEPS: {"steps"},
    GROUP_BACKGROUND: {"background"},
    GROUP_DESCRIPTION: {"description"},
    GROUP_DOCUMENTATION: {"documentation"},
    GROUP_FORMATTING: {"formatting", "whitespace", "indentation", "tabs"},
    GROUP_EXAMPLES: {"examples"},
    GROUP_SCENARIOS: {"scenarios"},
    GROUP_READABILITY: {"readability"},
}

# All valid group names
_ALL_GROUPS: set[str] = set(_CATEGORY_PREFIXES.keys()) | set(_TAG_GROUPS.keys())


def get_group_names() -> list[str]:
    """Return the names of all built-in groups.

    Returns:
        Sorted list of group names.
    """
    return sorted(_ALL_GROUPS)


def is_valid_group(name: str) -> bool:
    """Check if a group name is valid.

    Args:
        name: Group name to check.

    Returns:
        True if the group exists.
    """
    return name in _ALL_GROUPS


def is_category_group(name: str) -> bool:
    """Check if a group is category-based.

    Args:
        name: Group name to check.

    Returns:
        True if the group maps to a rule ID prefix (category-based).
    """
    return name in _CATEGORY_PREFIXES


def get_category_prefix(name: str) -> str | None:
    """Get the rule ID prefix for a category-based group.

    Args:
        name: Group name.

    Returns:
        Rule ID prefix (e.g. "BC") or None if not a category group.
    """
    return _CATEGORY_PREFIXES.get(name)


def get_group_tags(name: str) -> set[str] | None:
    """Get the tags for a tag-based group.

    Args:
        name: Group name.

    Returns:
        Set of tags that match this group, or None if not a tag group.
    """
    return _TAG_GROUPS.get(name)


def parse_groups(value: str | list[str]) -> list[str]:
    """Parse a group specification into a list of group names.

    Accepts comma-separated strings or lists of strings.

    Args:
        value: Comma-separated string or list of group names.

    Returns:
        List of validated group names.

    Raises:
        InvalidConfigValueError: If any group name is invalid.
    """
    if isinstance(value, str):
        names = [g.strip() for g in value.split(",") if g.strip()]
    else:
        names = [g.strip() for g in value if g.strip()]

    for name in names:
        if not is_valid_group(name):
            valid = ", ".join(get_group_names())
            raise InvalidConfigValueError(
                key="group",
                value=name,
                expected=f"one of: {valid}",
            )

    return names


__all__ = [
    "GROUP_BACKGROUND",
    "GROUP_CONSISTENCY",
    "GROUP_CORRECTNESS",
    "GROUP_DESCRIPTION",
    "GROUP_DOCUMENTATION",
    "GROUP_EXAMPLES",
    "GROUP_FORMATTING",
    "GROUP_NAMING",
    "GROUP_PEDANTIC",
    "GROUP_READABILITY",
    "GROUP_SCENARIOS",
    "GROUP_STEPS",
    "GROUP_STEP_DEFINITIONS",
    "GROUP_STYLE",
    "GROUP_TAGS",
    "get_category_prefix",
    "get_group_names",
    "get_group_tags",
    "is_category_group",
    "is_valid_group",
    "parse_groups",
]
