"""Plugin manager — discovers, loads, and registers plugins via entry points.

Discovers plugins from Python entry points, loads them lazily, and
registers their rules/reporters with the appropriate registries. Plugin
failures are isolated — a broken plugin does not crash the engine.

See COMPONENT_DESIGN.md C09, API.md Section 9, and RULE_ENGINE.md Section 3.
"""

from __future__ import annotations

import importlib
import logging
import warnings
from typing import Protocol

from behave_lint.exceptions import PluginLoadError, PluginRegistrationError
from behave_lint.plugins.plugin_info import PluginInfo, PluginType
from behave_lint.rules.base import Rule
from behave_lint.rules.registry import RuleRegistry

logger = logging.getLogger(__name__)

_ENTRY_POINT_GROUPS: dict[PluginType, str] = {
    PluginType.RULES: "behave_lint.rules",
    PluginType.REPORTERS: "behave_lint.reporters",
    PluginType.CONFIG: "behave_lint.config",
}


class SupportsEntryPoint(Protocol):
    """Protocol for an entry point object (importlib.metadata.EntryPoint)."""

    @property
    def name(self) -> str: ...

    @property
    def value(self) -> str: ...

    @property
    def group(self) -> str: ...


class SupportsEntryPointDiscovery(Protocol):
    """Protocol for discovering entry points."""

    def discover(self, group: str) -> list[SupportsEntryPoint]: ...


class _ImportLibDiscovery:
    """Discovery implementation using importlib.metadata."""

    def discover(self, group: str) -> list[SupportsEntryPoint]:
        """Discover entry points for a group.

        Args:
            group: The entry point group name.

        Returns:
            A list of entry point objects.
        """
        try:
            from importlib.metadata import entry_points

            eps = entry_points(group=group)
            return list(eps)
        except Exception:
            return []


class PluginManager:
    """Discovers, loads, and registers plugins.

    Attributes:
        _registry: Rule registry for registering plugin rules.
        _discovery: Entry point discovery mechanism.
        _plugins: Discovered plugin metadata, keyed by (group, name).
        _loaded: Set of plugin keys that have been loaded.
        _errors: List of errors encountered during loading/registration.
    """

    def __init__(
        self,
        registry: RuleRegistry,
        discovery: SupportsEntryPointDiscovery | None = None,
    ) -> None:
        """Initialize the plugin manager.

        Args:
            registry: The rule registry to register plugin rules into.
            discovery: Entry point discovery mechanism. If None, uses
                importlib.metadata.
        """
        self._registry = registry
        self._discovery = discovery or _ImportLibDiscovery()
        self._plugins: dict[tuple[str, str], PluginInfo] = {}
        self._loaded: set[tuple[str, str]] = set()
        self._loaded_objects: dict[tuple[str, str], object] = {}
        self._errors: list[str] = []

    def discover_all(self) -> list[PluginInfo]:
        """Discover all plugins from all entry point groups.

        Returns:
            A sorted list of discovered PluginInfo objects.
        """
        for plugin_type, group in _ENTRY_POINT_GROUPS.items():
            self._discover_group(plugin_type, group)

        return sorted(self._plugins.values(), key=lambda p: (p.group, p.name))

    def discover_group(self, plugin_type: PluginType) -> list[PluginInfo]:
        """Discover plugins for a specific type.

        Args:
            plugin_type: The type of plugins to discover.

        Returns:
            A list of discovered PluginInfo objects for that type.
        """
        group = _ENTRY_POINT_GROUPS[plugin_type]
        self._discover_group(plugin_type, group)
        return [p for p in self._plugins.values() if p.group == group]

    def _discover_group(self, plugin_type: PluginType, group: str) -> None:
        """Discover entry points for a group and store PluginInfo.

        Args:
            plugin_type: The plugin type.
            group: The entry point group name.
        """
        try:
            entry_points = self._discovery.discover(group)
        except Exception as exc:
            self._errors.append(f"Failed to discover entry points for '{group}': {exc}")
            logger.warning("Failed to discover entry points for '%s': %s", group, exc)
            return

        for ep in entry_points:
            key = (group, ep.name)
            if key in self._plugins:
                continue

            module, _, attr = ep.value.partition(":")
            info = PluginInfo(
                name=ep.name,
                type=plugin_type,
                module=module,
                attr=attr or ep.name,
                group=group,
            )
            self._plugins[key] = info

    def load_plugin(self, plugin: PluginInfo) -> object:
        """Load a plugin module and return the target object.

        Args:
            plugin: The plugin to load.

        Returns:
            The loaded object (class or function).

        Raises:
            PluginLoadError: If the module cannot be imported.
        """
        key = (plugin.group, plugin.name)
        if key in self._loaded:
            return self._get_loaded_object(plugin)

        try:
            module_obj = importlib.import_module(plugin.module)
            target = getattr(module_obj, plugin.attr)
        except ImportError as exc:
            error = PluginLoadError(plugin.name, str(exc))
            self._errors.append(str(error))
            self._plugins[key] = PluginInfo(
                name=plugin.name,
                type=plugin.type,
                module=plugin.module,
                attr=plugin.attr,
                group=plugin.group,
                loaded=False,
                error=str(error),
            )
            warnings.warn(str(error), stacklevel=2)
            raise error from exc
        except AttributeError as exc:
            error = PluginLoadError(
                plugin.name,
                f"Attribute '{plugin.attr}' not found in '{plugin.module}': {exc}",
            )
            self._errors.append(str(error))
            self._plugins[key] = PluginInfo(
                name=plugin.name,
                type=plugin.type,
                module=plugin.module,
                attr=plugin.attr,
                group=plugin.group,
                loaded=False,
                error=str(error),
            )
            warnings.warn(str(error), stacklevel=2)
            raise error from exc

        self._loaded.add(key)
        self._plugins[key] = PluginInfo(
            name=plugin.name,
            type=plugin.type,
            module=plugin.module,
            attr=plugin.attr,
            group=plugin.group,
            loaded=True,
        )
        self._loaded_objects[key] = target
        return target

    def _get_loaded_object(self, plugin: PluginInfo) -> object:
        """Get a previously loaded object.

        Args:
            plugin: The plugin to look up.

        Returns:
            The previously loaded target object.
        """
        return self._loaded_objects[(plugin.group, plugin.name)]

    def register_rules(self, plugin: PluginInfo) -> int:
        """Load a rules plugin and register its rules.

        The plugin target can be either a Rule subclass directly or a
        registration function that returns a list of Rule subclasses.

        Args:
            plugin: The rules plugin to register.

        Returns:
            Number of rules successfully registered.

        Raises:
            PluginLoadError: If the plugin cannot be loaded.
            PluginRegistrationError: If registration fails.
        """
        if plugin.type is not PluginType.RULES:
            return 0

        target = self.load_plugin(plugin)

        rule_classes: list[type[Rule]] = []

        if isinstance(target, type) and issubclass(target, Rule):
            rule_classes = [target]
        elif callable(target):
            try:
                result = target()
            except Exception as exc:
                error = PluginRegistrationError(plugin.name, str(exc))
                self._errors.append(str(error))
                warnings.warn(str(error), stacklevel=2)
                raise error from exc

            if isinstance(result, list):
                rule_classes = [
                    rc for rc in result if isinstance(rc, type) and issubclass(rc, Rule)
                ]
            elif isinstance(result, type) and issubclass(result, Rule):
                rule_classes = [result]
        else:
            error = PluginRegistrationError(
                plugin.name,
                f"Expected Rule subclass or registration function, got {type(target)}",
            )
            self._errors.append(str(error))
            warnings.warn(str(error), stacklevel=2)
            raise error

        count = 0
        for rule_class in rule_classes:
            if self._registry.register(rule_class, source=plugin.name):
                count += 1

        return count

    def load_all(self) -> tuple[int, list[str]]:
        """Load and register all discovered plugins.

        Returns:
            A tuple of (total_rules_registered, list_of_errors).
        """
        total = 0
        errors: list[str] = []

        for plugin in sorted(self._plugins.values(), key=lambda p: (p.group, p.name)):
            if plugin.type is PluginType.RULES:
                try:
                    total += self.register_rules(plugin)
                except (PluginLoadError, PluginRegistrationError) as exc:
                    errors.append(str(exc))
                    logger.warning("Plugin '%s' failed: %s", plugin.name, exc)
            else:
                try:
                    self.load_plugin(plugin)
                except PluginLoadError as exc:
                    errors.append(str(exc))
                    logger.warning("Plugin '%s' failed: %s", plugin.name, exc)

        self._errors.extend(errors)
        return total, errors

    @property
    def discovered_plugins(self) -> list[PluginInfo]:
        """All discovered plugins.

        Returns:
            A sorted list of PluginInfo objects.
        """
        return sorted(self._plugins.values(), key=lambda p: (p.group, p.name))

    @property
    def errors(self) -> list[str]:
        """All errors encountered during loading and registration.

        Returns:
            A list of error message strings.
        """
        return list(self._errors)

    def __len__(self) -> int:
        """Number of discovered plugins."""
        return len(self._plugins)


__all__ = ["PluginManager"]
