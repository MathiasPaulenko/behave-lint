"""Unit tests for the Config dataclass.

See API.md Section 4 and CONFIGURATION_SYSTEM.md.
"""

from __future__ import annotations

import pytest

from behave_lint.models.config import Config
from behave_lint.models.enums import Severity


class TestConfigDefaults:
    """Tests for Config default values."""

    def test_defaults(self) -> None:
        config = Config()
        assert config.select == []
        assert config.ignore == []
        assert config.severity_overrides == {}
        assert config.output == "console"
        assert config.output_file is None
        assert config.paths == ["features/"]
        assert config.step_definitions is None
        assert config.cache is True
        assert config.cache_dir == ".behave-lint-cache"
        assert config.plugins == {}
        assert config.rule_params == {}
        assert config.fail_on is Severity.WARNING
        assert config.max_warnings == -1

    def test_custom_values(self) -> None:
        config = Config(
            select=["BC001", "BS001"],
            ignore=["BX001"],
            severity_overrides={"BS001": Severity.INFO},
            output="json",
            output_file="results.json",
            paths=["tests/features/"],
            step_definitions="steps/",
            cache=False,
            cache_dir="/tmp/cache",
            plugins={"acme-rules": True},
            rule_params={"BC001": {"max_scenarios": 10}},
            fail_on=Severity.ERROR,
            max_warnings=50,
        )
        assert config.select == ["BC001", "BS001"]
        assert config.ignore == ["BX001"]
        assert config.severity_overrides == {"BS001": Severity.INFO}
        assert config.output == "json"
        assert config.output_file == "results.json"
        assert config.paths == ["tests/features/"]
        assert config.step_definitions == "steps/"
        assert config.cache is False
        assert config.cache_dir == "/tmp/cache"
        assert config.plugins == {"acme-rules": True}
        assert config.rule_params == {"BC001": {"max_scenarios": 10}}
        assert config.fail_on is Severity.ERROR
        assert config.max_warnings == 50


class TestConfigImmutability:
    """Tests that Config is frozen."""

    def test_frozen(self) -> None:
        config = Config()
        with pytest.raises(AttributeError):
            config.output = "json"  # type: ignore[misc]


class TestConfigIsRuleEnabled:
    """Tests for Config.is_rule_enabled()."""

    def test_default_all_enabled(self) -> None:
        config = Config()
        assert config.is_rule_enabled("BC001") is True

    def test_ignore_disables(self) -> None:
        config = Config(ignore=["BC001"])
        assert config.is_rule_enabled("BC001") is False
        assert config.is_rule_enabled("BS001") is True

    def test_select_enables_only_listed(self) -> None:
        config = Config(select=["BC001"])
        assert config.is_rule_enabled("BC001") is True
        assert config.is_rule_enabled("BS001") is False

    def test_select_and_ignore(self) -> None:
        config = Config(select=["BC001", "BS001"], ignore=["BS001"])
        assert config.is_rule_enabled("BC001") is True
        assert config.is_rule_enabled("BS001") is False


class TestConfigGetSeverity:
    """Tests for Config.get_severity()."""

    def test_no_override(self) -> None:
        config = Config()
        assert config.get_severity("BC001", Severity.ERROR) is Severity.ERROR

    def test_with_override(self) -> None:
        config = Config(severity_overrides={"BC001": Severity.INFO})
        assert config.get_severity("BC001", Severity.ERROR) is Severity.INFO

    def test_override_only_for_specified_rule(self) -> None:
        config = Config(severity_overrides={"BC001": Severity.INFO})
        assert config.get_severity("BS001", Severity.WARNING) is Severity.WARNING
