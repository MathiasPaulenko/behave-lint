"""Rule registry — catalog of discovered and registered rules.

Maintains the registry of rule classes and their metadata. Provides
lookup by ID, category, and tag. Filters rules based on configuration
(select, ignore) and provides the ordered list of enabled rules.

See COMPONENT_DESIGN.md C04 and RULE_ENGINE.md Section 3.
"""

from __future__ import annotations

import warnings

from behave_lint.models.config import Config
from behave_lint.models.enums import Category
from behave_lint.models.rule_metadata import RuleMetadata
from behave_lint.rules.base import Rule
from behave_lint.rules.validation import validate_metadata

# Category execution order (RULE_ENGINE.md Section 5)
_CATEGORY_ORDER: dict[Category, int] = {
    Category.CORRECTNESS: 0,
    Category.STYLE: 1,
    Category.COMPLEXITY: 2,
    Category.CONSISTENCY: 3,
    Category.STEP_DEFINITIONS: 4,
    Category.PEDANTIC: 5,
    Category.SECURITY: 6,
    Category.I18N: 7,
    Category.ACCESSIBILITY: 8,
}


class RuleRegistry:
    """Registry of rule classes and their metadata.

    Thread-safe after population (read-only during execution).

    Attributes:
        _rules: Dict mapping rule_id to (rule_class, metadata, source).
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._rules: dict[str, tuple[type[Rule], RuleMetadata, str]] = {}
        self._names: dict[str, str] = {}  # name -> rule_id

    def register(
        self,
        rule_class: type[Rule],
        source: str = "built-in",
    ) -> bool:
        """Register a rule class with the registry.

        Registration is idempotent — registering the same rule twice
        is a no-op. The first registration wins for duplicate IDs.

        Args:
            rule_class: The rule class to register.
            source: Source of the rule ("built-in" or plugin name).

        Returns:
            True if registered, False if rejected (invalid metadata
            or duplicate ID).
        """
        metadata = getattr(rule_class, "metadata", None)
        if metadata is None:
            warnings.warn(
                f"Rule class {rule_class.__name__} has no metadata. Rule rejected.",
                stacklevel=2,
            )
            return False

        if not isinstance(metadata, RuleMetadata):
            warnings.warn(
                f"Rule class {rule_class.__name__} metadata is not "
                f"a RuleMetadata object. Rule rejected.",
                stacklevel=2,
            )
            return False

        if not validate_metadata(metadata):
            return False

        rule_id = metadata.rule_id

        # Check for duplicate ID
        if rule_id in self._rules:
            existing_source = self._rules[rule_id][2]
            warnings.warn(
                f"Duplicate rule ID '{rule_id}' from '{source}'. "
                f"Already registered from '{existing_source}'. "
                "First registration wins.",
                stacklevel=2,
            )
            return False

        # Check for duplicate name
        if metadata.name in self._names:
            existing_id = self._names[metadata.name]
            warnings.warn(
                f"Duplicate rule name '{metadata.name}' from '{source}'. "
                f"Already used by rule '{existing_id}'. "
                "Name conflict (rule registered by ID).",
                stacklevel=2,
            )
        else:
            self._names[metadata.name] = rule_id

        self._rules[rule_id] = (rule_class, metadata, source)
        return True

    def get(self, rule_id: str) -> tuple[type[Rule], RuleMetadata, str] | None:
        """Look up a rule by ID.

        Args:
            rule_id: The rule ID to look up.

        Returns:
            Tuple of (rule_class, metadata, source) or None if not found.
        """
        return self._rules.get(rule_id)

    def get_by_name(self, name: str) -> tuple[type[Rule], RuleMetadata, str] | None:
        """Look up a rule by name.

        Args:
            name: The rule name to look up.

        Returns:
            Tuple of (rule_class, metadata, source) or None if not found.
        """
        rule_id = self._names.get(name)
        if rule_id is None:
            return None
        return self._rules.get(rule_id)

    def get_all(self) -> list[tuple[type[Rule], RuleMetadata, str]]:
        """Get all registered rules.

        Returns:
            List of (rule_class, metadata, source) tuples.
        """
        return list(self._rules.values())

    def get_by_category(
        self, category: Category
    ) -> list[tuple[type[Rule], RuleMetadata, str]]:
        """Get all rules in a category.

        Args:
            category: The category to filter by.

        Returns:
            List of (rule_class, metadata, source) tuples.
        """
        return [
            (cls, meta, src)
            for cls, meta, src in self._rules.values()
            if meta.category == category
        ]

    def get_enabled(self, config: Config) -> list[tuple[type[Rule], RuleMetadata]]:
        """Get the ordered list of enabled rules based on configuration.

        Rules are filtered by select/ignore and ordered by:
        1. Category order (Correctness → Style → ... → Pedantic).
        2. Rule ID (ascending, lexicographic).

        Args:
            config: The resolved configuration object.

        Returns:
            Ordered list of (rule_class, metadata) tuples.
        """
        enabled: list[tuple[type[Rule], RuleMetadata]] = []

        for rule_class, metadata, _source in self._rules.values():
            rule_id = metadata.rule_id

            # Check if enabled by config
            if not config.is_rule_enabled(rule_id):
                continue

            # Skip experimental rules unless explicitly selected
            if metadata.experimental and rule_id not in config.select:
                continue

            # Skip deprecated rules unless explicitly selected
            if metadata.deprecated and rule_id not in config.select:
                continue

            enabled.append((rule_class, metadata))

        # Sort by category order, then rule ID
        enabled.sort(
            key=lambda item: (
                _CATEGORY_ORDER.get(item[1].category, 99),
                item[1].rule_id,
            )
        )

        return enabled

    def __len__(self) -> int:
        """Number of registered rules."""
        return len(self._rules)

    def __contains__(self, rule_id: str) -> bool:
        """Check if a rule ID is registered."""
        return rule_id in self._rules


__all__ = ["RuleRegistry"]
