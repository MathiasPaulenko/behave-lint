"""Unit tests for PluginInfo and PluginType."""

from __future__ import annotations

from behave_lint.plugins.plugin_info import PluginInfo, PluginType


class TestPluginType:
    """Tests for PluginType enum."""

    def test_rules_value(self) -> None:
        assert PluginType.RULES.value == "rules"

    def test_reporters_value(self) -> None:
        assert PluginType.REPORTERS.value == "reporters"

    def test_config_value(self) -> None:
        assert PluginType.CONFIG.value == "config"

    def test_all_members(self) -> None:
        assert len(PluginType) == 3


class TestPluginInfo:
    """Tests for PluginInfo dataclass."""

    def test_basic_creation(self) -> None:
        info = PluginInfo(
            name="acme-rules",
            type=PluginType.RULES,
            module="acme_lint_rules",
            attr="register_rules",
            group="behave_lint.rules",
        )
        assert info.name == "acme-rules"
        assert info.type is PluginType.RULES
        assert info.module == "acme_lint_rules"
        assert info.attr == "register_rules"
        assert info.group == "behave_lint.rules"
        assert info.loaded is False
        assert info.error is None

    def test_frozen(self) -> None:
        info = PluginInfo(
            name="test",
            type=PluginType.RULES,
            module="test_mod",
            attr="test_attr",
            group="behave_lint.rules",
        )
        try:
            info.name = "other"  # type: ignore[misc]
            raise AssertionError("Should have raised FrozenInstanceError")
        except AttributeError:
            pass

    def test_with_error(self) -> None:
        info = PluginInfo(
            name="broken",
            type=PluginType.RULES,
            module="broken_mod",
            attr="register",
            group="behave_lint.rules",
            loaded=False,
            error="ImportError: No module named 'broken_mod'",
        )
        assert info.error is not None
        assert "ImportError" in info.error

    def test_loaded_state(self) -> None:
        info = PluginInfo(
            name="loaded-plugin",
            type=PluginType.REPORTERS,
            module="my_reporter",
            attr="MyReporter",
            group="behave_lint.reporters",
            loaded=True,
        )
        assert info.loaded is True
