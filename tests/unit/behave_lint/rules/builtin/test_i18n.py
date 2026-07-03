"""Unit tests for i18n rules (BI18N001-BI18N003)."""

from __future__ import annotations

from pathlib import Path

from behave_lint.models.config import Config
from behave_lint.models.enums import Category, Severity
from behave_lint.rules.builtin.i18n import (
    HardcodedCurrencyRule,
    HardcodedDateFormatRule,
    NonAsciiStepTextRule,
)
from behave_lint.rules.registry import RuleRegistry


def _load_feature(tmp_path: Path, content: str) -> object:
    """Helper: write a .feature file and load it via behave-model."""
    from behave_lint.infrastructure.project_loader import load_single

    f = tmp_path / "test.feature"
    f.write_text(content, encoding="utf-8")
    feature = load_single(str(f))
    assert feature is not None, f"Failed to parse feature:\n{content}"
    return feature


class TestHardcodedDateFormatRule:
    """Tests for BI18N001 - Hardcoded date/time formats."""

    def test_detects_slash_date(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Booking\n"
            '    Given the date is "12/31/2024"\n',
        )
        rule = HardcodedDateFormatRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BI18N001"

    def test_detects_iso_date(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Booking\n"
            '    Given the date is "2024-12-31"\n',
        )
        rule = HardcodedDateFormatRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BI18N001"

    def test_no_false_positive_placeholder(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Booking\n"
            '    Given the date is "<booking_date>"\n',
        )
        rule = HardcodedDateFormatRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_category_and_severity(self) -> None:
        rule = HardcodedDateFormatRule()
        assert rule.metadata.category is Category.I18N
        assert rule.metadata.default_severity is Severity.WARNING


class TestHardcodedCurrencyRule:
    """Tests for BI18N002 - Hardcoded currency symbols."""

    def test_detects_dollar_sign(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            'Feature: Test\n\n  Scenario: Pay\n    Given the total is "$99.99"\n',
        )
        rule = HardcodedCurrencyRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BI18N002"

    def test_detects_euro_sign(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            'Feature: Test\n\n  Scenario: Pay\n    Given the total is "\u20ac50"\n',
        )
        rule = HardcodedCurrencyRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BI18N002"

    def test_no_false_positive_no_currency(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            'Feature: Test\n\n  Scenario: Pay\n    Given the total is "<amount>"\n',
        )
        rule = HardcodedCurrencyRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_category_and_severity(self) -> None:
        rule = HardcodedCurrencyRule()
        assert rule.metadata.category is Category.I18N
        assert rule.metadata.default_severity is Severity.WARNING


class TestNonAsciiStepTextRule:
    """Tests for BI18N003 - Non-ASCII characters in step text."""

    def test_detects_accented_text(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Order\n"
            '    Given the customer selects "caf\u00e9 au lait"\n',
        )
        rule = NonAsciiStepTextRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BI18N003"
        assert diags[0].severity is Severity.INFO

    def test_no_false_positive_ascii(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Order\n"
            '    Given the customer selects "coffee"\n',
        )
        rule = NonAsciiStepTextRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_category_and_severity(self) -> None:
        rule = NonAsciiStepTextRule()
        assert rule.metadata.category is Category.I18N
        assert rule.metadata.default_severity is Severity.INFO


class TestRegisterI18nRules:
    """Test that i18n rules are registered."""

    def test_all_i18n_rules_registered(self) -> None:
        from behave_lint.rules.builtin import register_builtins

        registry = RuleRegistry()
        register_builtins(registry)
        assert len(registry) == 50
        assert "BI18N001" in registry
        assert "BI18N002" in registry
        assert "BI18N003" in registry
