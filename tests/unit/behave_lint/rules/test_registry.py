"""Unit tests for the RuleRegistry."""

from __future__ import annotations

import warnings

import pytest

from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.rule_metadata import RuleMetadata
from behave_lint.rules.base import Rule
from behave_lint.rules.registry import RuleRegistry


def _make_metadata(
    rule_id: str = "BC001",
    name: str = "test-rule",
    category: Category = Category.CORRECTNESS,
    severity: Severity = Severity.ERROR,
    experimental: bool = False,
    deprecated: bool = False,
) -> RuleMetadata:
    return RuleMetadata(
        rule_id=rule_id,
        name=name,
        title="Test Rule",
        description="A test rule.",
        category=category,
        default_severity=severity,
        motivation="For testing.",
        since="0.1.0",
        experimental=experimental,
        deprecated=deprecated,
    )


def _make_rule_class(
    meta: RuleMetadata | None = None,
) -> type[Rule]:
    md = meta or _make_metadata()

    class TestRule(Rule):
        metadata = md

        def check(self, feature: object, config: Config) -> list[Diagnostic]:
            return []

    return TestRule


class TestRuleRegistry:
    """Tests for RuleRegistry."""

    def test_register_and_lookup(self) -> None:
        registry = RuleRegistry()
        rule_class = _make_rule_class()
        assert registry.register(rule_class) is True

        result = registry.get("BC001")
        assert result is not None
        assert result[0] is rule_class
        assert result[1].rule_id == "BC001"
        assert result[2] == "built-in"

    def test_register_with_custom_source(self) -> None:
        registry = RuleRegistry()
        rule_class = _make_rule_class()
        assert registry.register(rule_class, source="plugin:acme") is True

        result = registry.get("BC001")
        assert result is not None
        assert result[2] == "plugin:acme"

    def test_duplicate_id_rejected(self) -> None:
        registry = RuleRegistry()
        rule1 = _make_rule_class(_make_metadata(rule_id="BC001", name="rule-one"))
        rule2 = _make_rule_class(_make_metadata(rule_id="BC001", name="rule-two"))

        assert registry.register(rule1) is True
        with pytest.warns(UserWarning, match="Duplicate rule ID"):
            assert registry.register(rule2) is False

        assert len(registry) == 1

    def test_duplicate_name_warns_but_registers(self) -> None:
        registry = RuleRegistry()
        rule1 = _make_rule_class(_make_metadata(rule_id="BC001", name="same-name"))
        rule2 = _make_rule_class(_make_metadata(rule_id="BC002", name="same-name"))

        assert registry.register(rule1) is True
        with pytest.warns(UserWarning, match="Duplicate rule name"):
            assert registry.register(rule2) is True

        assert len(registry) == 2

    def test_register_no_metadata(self) -> None:
        registry = RuleRegistry()

        class NoMetadataRule(Rule):
            def check(self, feature: object, config: Config) -> list[Diagnostic]:
                return []

        with pytest.warns(UserWarning, match="no metadata"):
            assert registry.register(NoMetadataRule) is False

    def test_get_by_name(self) -> None:
        registry = RuleRegistry()
        rule_class = _make_rule_class(_make_metadata(name="my-rule"))
        registry.register(rule_class)

        result = registry.get_by_name("my-rule")
        assert result is not None
        assert result[1].rule_id == "BC001"

    def test_get_by_name_not_found(self) -> None:
        registry = RuleRegistry()
        assert registry.get_by_name("nonexistent") is None

    def test_get_not_found(self) -> None:
        registry = RuleRegistry()
        assert registry.get("NON999") is None

    def test_get_all(self) -> None:
        registry = RuleRegistry()
        r1 = _make_rule_class(_make_metadata(rule_id="BC001", name="r1"))
        r2 = _make_rule_class(_make_metadata(rule_id="BS001", name="r2"))
        registry.register(r1)
        registry.register(r2)

        all_rules = registry.get_all()
        assert len(all_rules) == 2

    def test_get_by_category(self) -> None:
        registry = RuleRegistry()
        r1 = _make_rule_class(
            _make_metadata(rule_id="BC001", name="r1", category=Category.CORRECTNESS)
        )
        r2 = _make_rule_class(
            _make_metadata(rule_id="BS001", name="r2", category=Category.STYLE)
        )
        registry.register(r1)
        registry.register(r2)

        correctness = registry.get_by_category(Category.CORRECTNESS)
        assert len(correctness) == 1
        assert correctness[0][1].rule_id == "BC001"

    def test_get_enabled_all(self) -> None:
        registry = RuleRegistry()
        r1 = _make_rule_class(_make_metadata(rule_id="BC001", name="r1"))
        r2 = _make_rule_class(_make_metadata(rule_id="BS001", name="r2"))
        registry.register(r1)
        registry.register(r2)

        enabled = registry.get_enabled(Config())
        assert len(enabled) == 2

    def test_get_enabled_with_select(self) -> None:
        registry = RuleRegistry()
        r1 = _make_rule_class(_make_metadata(rule_id="BC001", name="r1"))
        r2 = _make_rule_class(_make_metadata(rule_id="BS001", name="r2"))
        registry.register(r1)
        registry.register(r2)

        config = Config(select=["BC001"])
        enabled = registry.get_enabled(config)
        assert len(enabled) == 1
        assert enabled[0][1].rule_id == "BC001"

    def test_get_enabled_with_ignore(self) -> None:
        registry = RuleRegistry()
        r1 = _make_rule_class(_make_metadata(rule_id="BC001", name="r1"))
        r2 = _make_rule_class(_make_metadata(rule_id="BS001", name="r2"))
        registry.register(r1)
        registry.register(r2)

        config = Config(ignore=["BC001"])
        enabled = registry.get_enabled(config)
        assert len(enabled) == 1
        assert enabled[0][1].rule_id == "BS001"

    def test_get_enabled_experimental_not_in_default(self) -> None:
        registry = RuleRegistry()
        r1 = _make_rule_class(
            _make_metadata(rule_id="BX001", name="r1", experimental=True)
        )
        registry.register(r1)

        # Not selected by default
        enabled = registry.get_enabled(Config())
        assert len(enabled) == 0

        # Explicitly selected
        enabled = registry.get_enabled(Config(select=["BX001"]))
        assert len(enabled) == 1

    def test_get_enabled_deprecated_not_in_default(self) -> None:
        registry = RuleRegistry()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r1 = _make_rule_class(
                _make_metadata(rule_id="BC001", name="r1", deprecated=True)
            )
            registry.register(r1)

        enabled = registry.get_enabled(Config())
        assert len(enabled) == 0

        enabled = registry.get_enabled(Config(select=["BC001"]))
        assert len(enabled) == 1

    def test_get_enabled_ordering(self) -> None:
        registry = RuleRegistry()
        # Register out of order
        for rule_id, name, cat in [
            ("BS001", "s1", Category.STYLE),
            ("BX001", "x1", Category.COMPLEXITY),
            ("BC001", "c1", Category.CORRECTNESS),
            ("BC002", "c2", Category.CORRECTNESS),
        ]:
            registry.register(
                _make_rule_class(
                    _make_metadata(rule_id=rule_id, name=name, category=cat)
                )
            )

        enabled = registry.get_enabled(Config())
        # Correctness first, then by rule_id
        assert [e[1].rule_id for e in enabled] == ["BC001", "BC002", "BS001", "BX001"]

    def test_contains(self) -> None:
        registry = RuleRegistry()
        registry.register(_make_rule_class())
        assert "BC001" in registry
        assert "NON999" not in registry

    def test_len(self) -> None:
        registry = RuleRegistry()
        assert len(registry) == 0
        registry.register(_make_rule_class())
        assert len(registry) == 1
