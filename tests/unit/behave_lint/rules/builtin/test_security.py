"""Unit tests for security rules (BSEC001-BSEC003)."""

from __future__ import annotations

from pathlib import Path

from behave_lint.models.config import Config
from behave_lint.models.enums import Category, Severity
from behave_lint.rules.builtin.security import (
    HardcodedSecretsRule,
    SensitiveTagRule,
    UrlWithCredentialsRule,
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


class TestHardcodedSecretsRule:
    """Tests for BSEC001 - Hardcoded Secrets."""

    def test_detects_hardcoded_password(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Login\n"
            '    Given the user enters password = "hunter2pass"\n',
        )
        rule = HardcodedSecretsRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BSEC001"
        assert "hardcoded secret" in diags[0].message.lower()

    def test_detects_api_key(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: API call\n"
            '    Given the api_key = "sk_live_abc123def456ghi789jkl"\n',
        )
        rule = HardcodedSecretsRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BSEC001"

    def test_no_false_positive_placeholder(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Login\n"
            '    Given the user enters password = "<password>"\n',
        )
        rule = HardcodedSecretsRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_no_false_positive_no_sensitive_keyword(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: Config\n"
            '    Given the value = "abcdefgh123"\n',
        )
        rule = HardcodedSecretsRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_category_and_severity(self) -> None:
        rule = HardcodedSecretsRule()
        assert rule.metadata.category is Category.SECURITY
        assert rule.metadata.default_severity is Severity.ERROR


class TestUrlWithCredentialsRule:
    """Tests for BSEC002 - URL with embedded credentials."""

    def test_detects_url_with_credentials(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: API\n"
            '    Given the url is "https://admin:secret@api.example.com"\n',
        )
        rule = UrlWithCredentialsRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BSEC002"
        assert "embedded credentials" in diags[0].message.lower()

    def test_no_false_positive_clean_url(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n"
            "  Scenario: API\n"
            '    Given the url is "https://api.example.com"\n',
        )
        rule = UrlWithCredentialsRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_category_and_severity(self) -> None:
        rule = UrlWithCredentialsRule()
        assert rule.metadata.category is Category.SECURITY
        assert rule.metadata.default_severity is Severity.ERROR


class TestSensitiveTagRule:
    """Tests for BSEC003 - Sensitive tags."""

    def test_detects_production_tag_on_feature(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "@production\nFeature: Test\n\n  Scenario: A\n    Given a step\n",
        )
        rule = SensitiveTagRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BSEC003"
        assert "production" in diags[0].message.lower()

    def test_detects_live_tag_on_scenario(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "Feature: Test\n\n  @live\n  Scenario: A\n    Given a step\n",
        )
        rule = SensitiveTagRule()
        diags = rule.check(feature, Config())
        assert len(diags) == 1
        assert diags[0].rule_id == "BSEC003"

    def test_no_false_positive_safe_tag(self, tmp_path: Path) -> None:
        feature = _load_feature(
            tmp_path,
            "@staging\nFeature: Test\n\n  Scenario: A\n    Given a step\n",
        )
        rule = SensitiveTagRule()
        diags = rule.check(feature, Config())
        assert diags == []

    def test_category_and_severity(self) -> None:
        rule = SensitiveTagRule()
        assert rule.metadata.category is Category.SECURITY
        assert rule.metadata.default_severity is Severity.WARNING


class TestRegisterSecurityRules:
    """Test that security rules are registered."""

    def test_all_security_rules_registered(self) -> None:
        from behave_lint.rules.builtin import register_builtins

        registry = RuleRegistry()
        register_builtins(registry)
        assert len(registry) == 50
        assert "BSEC001" in registry
        assert "BSEC002" in registry
        assert "BSEC003" in registry
