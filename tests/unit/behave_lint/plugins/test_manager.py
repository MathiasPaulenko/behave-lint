"""Unit tests for the PluginManager."""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import pytest

from behave_lint.exceptions import PluginLoadError, PluginRegistrationError
from behave_lint.models.enums import Category, Severity
from behave_lint.models.rule_metadata import RuleMetadata
from behave_lint.plugins.manager import PluginManager
from behave_lint.plugins.plugin_info import PluginInfo, PluginType
from behave_lint.rules.base import Rule
from behave_lint.rules.registry import RuleRegistry


@dataclass
class FakeEntryPoint:
    """Fake entry point for testing."""

    name: str
    value: str
    group: str


class FakeDiscovery:
    """Fake entry point discovery for testing."""

    def __init__(self, entry_points: list[FakeEntryPoint] | None = None) -> None:
        self._entry_points = entry_points or []
        self._call_count = 0

    def discover(self, group: str) -> list[FakeEntryPoint]:
        self._call_count += 1
        return [ep for ep in self._entry_points if ep.group == group]

    @property
    def call_count(self) -> int:
        return self._call_count


def _make_metadata(rule_id: str = "XC001") -> RuleMetadata:
    return RuleMetadata(
        rule_id=rule_id,
        name="test-rule",
        title="Test Rule",
        description="A test rule",
        category=Category.CORRECTNESS,
        default_severity=Severity.ERROR,
        since="1.0.0",
        motivation="Testing",
    )


class FakeRule(Rule):
    """A fake rule for testing plugin registration."""

    metadata = _make_metadata()

    def check(self, ctx: object) -> list[object]:  # type: ignore[override]
        return []


class AnotherFakeRule(Rule):
    """Another fake rule."""

    metadata = _make_metadata("XC002")

    def check(self, ctx: object) -> list[object]:  # type: ignore[override]
        return []


def _register_two_rules() -> list[type[Rule]]:
    """Registration function returning two rule classes."""
    return [FakeRule, AnotherFakeRule]


class TestPluginManagerDiscovery:
    """Tests for plugin discovery."""

    def test_discover_all_empty(self) -> None:
        registry = RuleRegistry()
        discovery = FakeDiscovery([])
        manager = PluginManager(registry, discovery)
        plugins = manager.discover_all()
        assert plugins == []
        assert len(manager) == 0

    def test_discover_all_finds_plugins(self) -> None:
        registry = RuleRegistry()
        eps = [
            FakeEntryPoint(
                name="acme-rules",
                value="acme_lint:register_rules",
                group="behave_lint.rules",
            ),
            FakeEntryPoint(
                name="acme-reporter",
                value="acme_lint:AcmeReporter",
                group="behave_lint.reporters",
            ),
        ]
        discovery = FakeDiscovery(eps)
        manager = PluginManager(registry, discovery)
        plugins = manager.discover_all()

        assert len(plugins) == 2
        rules_plugins = [p for p in plugins if p.type is PluginType.RULES]
        reporter_plugins = [p for p in plugins if p.type is PluginType.REPORTERS]
        assert len(rules_plugins) == 1
        assert len(reporter_plugins) == 1

    def test_discover_group_specific(self) -> None:
        registry = RuleRegistry()
        eps = [
            FakeEntryPoint(
                name="acme-rules",
                value="acme_lint:register_rules",
                group="behave_lint.rules",
            ),
        ]
        discovery = FakeDiscovery(eps)
        manager = PluginManager(registry, discovery)
        plugins = manager.discover_group(PluginType.RULES)
        assert len(plugins) == 1
        assert plugins[0].name == "acme-rules"

    def test_discover_deduplicates(self) -> None:
        registry = RuleRegistry()
        ep = FakeEntryPoint(
            name="dup",
            value="mod:attr",
            group="behave_lint.rules",
        )
        discovery = FakeDiscovery([ep])
        manager = PluginManager(registry, discovery)
        manager.discover_all()
        manager.discover_all()
        assert len(manager) == 1

    def test_discover_parses_module_attr(self) -> None:
        registry = RuleRegistry()
        eps = [
            FakeEntryPoint(
                name="test",
                value="my_module:my_function",
                group="behave_lint.rules",
            ),
        ]
        discovery = FakeDiscovery(eps)
        manager = PluginManager(registry, discovery)
        plugins = manager.discover_all()
        assert plugins[0].module == "my_module"
        assert plugins[0].attr == "my_function"

    def test_discover_no_attr_defaults_to_name(self) -> None:
        registry = RuleRegistry()
        eps = [
            FakeEntryPoint(
                name="test",
                value="my_module",
                group="behave_lint.rules",
            ),
        ]
        discovery = FakeDiscovery(eps)
        manager = PluginManager(registry, discovery)
        plugins = manager.discover_all()
        assert plugins[0].attr == "test"

    def test_discover_handles_exception(self) -> None:
        class FailingDiscovery:
            def discover(self, group: str) -> list[FakeEntryPoint]:
                raise RuntimeError("discovery failed")

        registry = RuleRegistry()
        manager = PluginManager(registry, FailingDiscovery())
        plugins = manager.discover_all()
        assert plugins == []
        assert len(manager.errors) > 0


class TestPluginManagerLoading:
    """Tests for plugin loading."""

    def test_load_plugin_success(self) -> None:
        registry = RuleRegistry()
        manager = PluginManager(registry, FakeDiscovery())
        plugin = PluginInfo(
            name="test",
            type=PluginType.RULES,
            module="behave_lint.rules.registry",
            attr="RuleRegistry",
            group="behave_lint.rules",
        )
        manager._plugins[("behave_lint.rules", "test")] = plugin
        target = manager.load_plugin(plugin)
        assert target is RuleRegistry
        assert plugin.name in [p.name for p in manager.discovered_plugins]

    def test_load_plugin_import_error(self) -> None:
        registry = RuleRegistry()
        manager = PluginManager(registry, FakeDiscovery())
        plugin = PluginInfo(
            name="broken",
            type=PluginType.RULES,
            module="nonexistent_module_xyz",
            attr="something",
            group="behave_lint.rules",
        )
        manager._plugins[("behave_lint.rules", "broken")] = plugin
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with pytest.raises(PluginLoadError, match="Failed to load plugin"):
                manager.load_plugin(plugin)

    def test_load_plugin_attribute_error(self) -> None:
        registry = RuleRegistry()
        manager = PluginManager(registry, FakeDiscovery())
        plugin = PluginInfo(
            name="bad-attr",
            type=PluginType.RULES,
            module="behave_lint.rules.registry",
            attr="NonExistentAttr",
            group="behave_lint.rules",
        )
        manager._plugins[("behave_lint.rules", "bad-attr")] = plugin
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with pytest.raises(PluginLoadError, match="Failed to load plugin"):
                manager.load_plugin(plugin)

    def test_load_plugin_cached(self) -> None:
        registry = RuleRegistry()
        manager = PluginManager(registry, FakeDiscovery())
        plugin = PluginInfo(
            name="cached",
            type=PluginType.RULES,
            module="behave_lint.rules.registry",
            attr="RuleRegistry",
            group="behave_lint.rules",
        )
        manager._plugins[("behave_lint.rules", "cached")] = plugin
        target1 = manager.load_plugin(plugin)
        target2 = manager.load_plugin(plugin)
        assert target1 is target2


class TestPluginManagerRegistration:
    """Tests for plugin rule registration."""

    def test_register_via_function(self) -> None:
        registry = RuleRegistry()
        manager = PluginManager(registry, FakeDiscovery())
        plugin = PluginInfo(
            name="func-plugin",
            type=PluginType.RULES,
            module="tests.unit.behave_lint.plugins.test_manager",
            attr="_register_two_rules",
            group="behave_lint.rules",
        )
        manager._plugins[("behave_lint.rules", "func-plugin")] = plugin
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            count = manager.register_rules(plugin)
        assert count == 2
        assert "XC001" in registry
        assert "XC002" in registry

    def test_register_non_rules_plugin_returns_zero(self) -> None:
        registry = RuleRegistry()
        manager = PluginManager(registry, FakeDiscovery())
        plugin = PluginInfo(
            name="reporter-plugin",
            type=PluginType.REPORTERS,
            module="some_module",
            attr="SomeReporter",
            group="behave_lint.reporters",
        )
        manager._plugins[("behave_lint.reporters", "reporter-plugin")] = plugin
        # Should return 0 since it's not a rules plugin
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            count = manager.register_rules(plugin)
        assert count == 0

    def test_register_function_raises_registration_error(self) -> None:
        registry = RuleRegistry()
        manager = PluginManager(registry, FakeDiscovery())

        def bad_register() -> list[type[Rule]]:
            raise RuntimeError("registration failed")

        import sys

        sys.modules["_test_bad_plugin"] = type(sys)("_test_bad_plugin")
        sys.modules["_test_bad_plugin"].bad_register = bad_register  # type: ignore[attr-defined]

        plugin = PluginInfo(
            name="bad-plugin",
            type=PluginType.RULES,
            module="_test_bad_plugin",
            attr="bad_register",
            group="behave_lint.rules",
        )
        manager._plugins[("behave_lint.rules", "bad-plugin")] = plugin
        with (
            warnings.catch_warnings(),
            pytest.raises(PluginRegistrationError, match="registration failed"),
        ):
            warnings.simplefilter("ignore")
            manager.register_rules(plugin)
        del sys.modules["_test_bad_plugin"]


class TestPluginManagerLoadAll:
    """Tests for load_all."""

    def test_load_all_empty(self) -> None:
        registry = RuleRegistry()
        manager = PluginManager(registry, FakeDiscovery([]))
        manager.discover_all()
        total, errors = manager.load_all()
        assert total == 0
        assert errors == []

    def test_load_all_with_plugins(self) -> None:
        registry = RuleRegistry()
        eps = [
            FakeEntryPoint(
                name="func-plugin",
                value="tests.unit.behave_lint.plugins.test_manager:_register_two_rules",
                group="behave_lint.rules",
            ),
        ]
        discovery = FakeDiscovery(eps)
        manager = PluginManager(registry, discovery)
        manager.discover_all()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            total, errors = manager.load_all()
        assert total == 2
        assert errors == []

    def test_load_all_isolates_failures(self) -> None:
        registry = RuleRegistry()
        eps = [
            FakeEntryPoint(
                name="broken",
                value="nonexistent_module_xyz:register",
                group="behave_lint.rules",
            ),
        ]
        discovery = FakeDiscovery(eps)
        manager = PluginManager(registry, discovery)
        manager.discover_all()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            total, errors = manager.load_all()
        assert total == 0
        assert len(errors) == 1
        assert "broken" in errors[0]


class TestPluginManagerProperties:
    """Tests for PluginManager properties."""

    def test_discovered_plugins_sorted(self) -> None:
        registry = RuleRegistry()
        eps = [
            FakeEntryPoint("z-plugin", "mod:attr", "behave_lint.rules"),
            FakeEntryPoint("a-plugin", "mod:attr", "behave_lint.rules"),
        ]
        discovery = FakeDiscovery(eps)
        manager = PluginManager(registry, discovery)
        manager.discover_all()
        plugins = manager.discovered_plugins
        assert plugins[0].name == "a-plugin"
        assert plugins[1].name == "z-plugin"

    def test_errors_property(self) -> None:
        registry = RuleRegistry()
        manager = PluginManager(registry, FakeDiscovery())
        assert manager.errors == []

    def test_len(self) -> None:
        registry = RuleRegistry()
        eps = [
            FakeEntryPoint("p1", "mod:attr", "behave_lint.rules"),
            FakeEntryPoint("p2", "mod:attr", "behave_lint.reporters"),
        ]
        discovery = FakeDiscovery(eps)
        manager = PluginManager(registry, discovery)
        manager.discover_all()
        assert len(manager) == 2
