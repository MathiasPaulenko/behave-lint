"""Unit tests for the exception hierarchy.

See API.md Section 11.
"""

from __future__ import annotations

import pytest

from behave_lint.exceptions import (
    BehaveLintError,
    CacheError,
    ConfigError,
    FileDiscoveryError,
    InternalError,
    InvalidConfigValueError,
    NoFilesFoundError,
    ParseError,
    PluginError,
    PluginLoadError,
    PluginRegistrationError,
    ReporterError,
    RuleError,
    RuleExecutionError,
    RuleNotFoundError,
    UnknownConfigKeyError,
    UnknownRuleError,
)


class TestHierarchy:
    """Tests that all exceptions inherit from BehaveLintError."""

    @pytest.mark.parametrize(
        "exc_class",
        [
            ConfigError,
            InvalidConfigValueError,
            UnknownConfigKeyError,
            UnknownRuleError,
            NoFilesFoundError,
            InternalError,
            RuleError,
            RuleNotFoundError,
            RuleExecutionError,
            ParseError,
            FileDiscoveryError,
            CacheError,
            ReporterError,
            PluginError,
            PluginLoadError,
            PluginRegistrationError,
        ],
    )
    def test_inherits_base(self, exc_class: type[Exception]) -> None:
        assert issubclass(exc_class, BehaveLintError)

    def test_config_error_subclasses(self) -> None:
        assert issubclass(InvalidConfigValueError, ConfigError)
        assert issubclass(UnknownConfigKeyError, ConfigError)
        assert issubclass(UnknownRuleError, ConfigError)

    def test_rule_error_subclasses(self) -> None:
        assert issubclass(RuleNotFoundError, RuleError)
        assert issubclass(RuleExecutionError, RuleError)

    def test_plugin_error_subclasses(self) -> None:
        assert issubclass(PluginLoadError, PluginError)
        assert issubclass(PluginRegistrationError, PluginError)


class TestConfigErrors:
    """Tests for config error messages and attributes."""

    def test_invalid_config_value(self) -> None:
        err = InvalidConfigValueError(
            "severity", "critical", "error, warning, info, off"
        )
        assert err.key == "severity"
        assert err.value == "critical"
        assert err.expected == "error, warning, info, off"
        assert "critical" in str(err)
        assert "severity" in str(err)

    def test_unknown_config_key(self) -> None:
        err = UnknownConfigKeyError("unknown_key")
        assert err.key == "unknown_key"
        assert "unknown_key" in str(err)

    def test_unknown_rule_with_suggestion(self) -> None:
        err = UnknownRuleError("BC001", suggestion="BS001")
        assert err.rule_id == "BC001"
        assert err.suggestion == "BS001"
        assert "BC001" in str(err)
        assert "BS001" in str(err)

    def test_unknown_rule_without_suggestion(self) -> None:
        err = UnknownRuleError("BC999")
        assert err.rule_id == "BC999"
        assert err.suggestion is None
        assert "BC999" in str(err)


class TestNoFilesFoundError:
    """Tests for NoFilesFoundError."""

    def test_attributes(self) -> None:
        err = NoFilesFoundError(["features/", "tests/features/"])
        assert err.paths == ["features/", "tests/features/"]
        assert "features/" in str(err)


class TestInternalError:
    """Tests for InternalError."""

    def test_attributes(self) -> None:
        err = InternalError("parsing AST", "0.1.0")
        assert err.operation == "parsing AST"
        assert err.version == "0.1.0"
        assert "parsing AST" in str(err)
        assert "0.1.0" in str(err)


class TestRuleErrors:
    """Tests for rule error messages."""

    def test_rule_not_found(self) -> None:
        err = RuleNotFoundError("BC999")
        assert err.rule_id == "BC999"
        assert "BC999" in str(err)

    def test_rule_execution_error(self) -> None:
        err = RuleExecutionError("BC001", "unexpected None")
        assert err.rule_id == "BC001"
        assert "BC001" in str(err)
        assert "unexpected None" in str(err)


class TestParseError:
    """Tests for ParseError."""

    def test_with_line(self) -> None:
        err = ParseError("features/bad.feature", line=42)
        assert err.file_path == "features/bad.feature"
        assert err.line == 42
        assert "42" in str(err)

    def test_without_line(self) -> None:
        err = ParseError("features/bad.feature")
        assert err.file_path == "features/bad.feature"
        assert err.line is None


class TestPluginErrors:
    """Tests for plugin error messages."""

    def test_plugin_load_error(self) -> None:
        err = PluginLoadError("acme-rules", "ModuleNotFoundError")
        assert err.plugin_name == "acme-rules"
        assert "acme-rules" in str(err)

    def test_plugin_registration_error(self) -> None:
        err = PluginRegistrationError("acme-rules", "duplicate rule ID")
        assert err.plugin_name == "acme-rules"
        assert "acme-rules" in str(err)
