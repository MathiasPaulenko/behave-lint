"""Rule validation — metadata checks at registration time.

Validates that every registered rule meets the minimum requirements
for correct execution. Invalid rules are rejected with a warning.

See RULE_ENGINE.md Section 12.
"""

from __future__ import annotations

import re
import warnings

from behave_lint.models.enums import Category, Severity
from behave_lint.models.rule_metadata import RuleMetadata

_RULE_ID_PATTERN = re.compile(r"^[A-Z]{2,5}\d{3}$")
_KEBAB_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+")


def validate_metadata(metadata: RuleMetadata) -> bool:
    """Validate rule metadata at registration time.

    Checks:
    - rule_id: Non-empty, matches naming convention (e.g., BC001).
    - name: Non-empty, kebab-case.
    - description: Non-empty.
    - category: Valid Category enum member.
    - default_severity: Valid Severity enum member.
    - since: Valid semver string.

    Args:
        metadata: The rule metadata to validate.

    Returns:
        True if valid, False otherwise. Invalid metadata emits
        a warning describing the issue.
    """
    errors: list[str] = []

    # rule_id
    if not metadata.rule_id:
        errors.append("rule_id must be a non-empty string")
    elif not _RULE_ID_PATTERN.match(metadata.rule_id):
        errors.append(
            f"rule_id '{metadata.rule_id}' does not match "
            "the naming convention (e.g., BC001)"
        )

    # name
    if not metadata.name:
        errors.append("name must be a non-empty string")
    elif not _KEBAB_CASE_PATTERN.match(metadata.name):
        errors.append(
            f"name '{metadata.name}' must be kebab-case "
            "(e.g., 'duplicate-scenario-name')"
        )

    # description
    if not metadata.description:
        errors.append("description must be a non-empty string")

    # motivation
    if not metadata.motivation:
        errors.append("motivation must be a non-empty string")

    # category
    if not isinstance(metadata.category, Category):
        errors.append(
            f"category must be a Category enum, got {type(metadata.category).__name__}"
        )

    # default_severity
    if not isinstance(metadata.default_severity, Severity):
        errors.append(
            f"default_severity must be a Severity enum, "
            f"got {type(metadata.default_severity).__name__}"
        )

    # since
    if not metadata.since:
        errors.append("since must be a non-empty string")
    elif not _SEMVER_PATTERN.match(metadata.since):
        errors.append(f"since '{metadata.since}' is not a valid semver string")

    if errors:
        rule_id = metadata.rule_id or "<unknown>"
        warnings.warn(
            f"Rule '{rule_id}' has invalid metadata: "
            + "; ".join(errors)
            + ". Rule rejected.",
            stacklevel=2,
        )
        return False

    return True


__all__ = ["validate_metadata"]
