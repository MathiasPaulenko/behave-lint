"""Unit tests for rule metadata validation."""

from __future__ import annotations

import warnings

import pytest

from behave_lint.models.enums import Category, Severity
from behave_lint.models.rule_metadata import RuleMetadata
from behave_lint.rules.validation import validate_metadata


def _valid_metadata() -> RuleMetadata:
    return RuleMetadata(
        rule_id="BC001",
        name="test-rule",
        title="Test Rule",
        description="A test rule.",
        category=Category.CORRECTNESS,
        default_severity=Severity.ERROR,
        motivation="For testing.",
        since="0.1.0",
    )


class TestValidateMetadata:
    """Tests for validate_metadata."""

    def test_valid_metadata(self) -> None:
        metadata = _valid_metadata()
        assert validate_metadata(metadata) is True

    def test_empty_rule_id(self) -> None:
        with pytest.raises(ValueError, match="rule_id must be a non-empty"):
            RuleMetadata(
                rule_id="",
                name="test-rule",
                title="T",
                description="d",
                category=Category.CORRECTNESS,
                default_severity=Severity.ERROR,
                motivation="m",
                since="0.1.0",
            )

    def test_invalid_rule_id_format(self) -> None:
        with pytest.warns(UserWarning, match="naming convention"):
            metadata = RuleMetadata(
                rule_id="bad",
                name="test-rule",
                title="T",
                description="d",
                category=Category.CORRECTNESS,
                default_severity=Severity.ERROR,
                motivation="m",
                since="0.1.0",
            )
            assert validate_metadata(metadata) is False

    def test_empty_name(self) -> None:
        with pytest.raises(ValueError, match="name must be a non-empty"):
            RuleMetadata(
                rule_id="BC001",
                name="",
                title="T",
                description="d",
                category=Category.CORRECTNESS,
                default_severity=Severity.ERROR,
                motivation="m",
                since="0.1.0",
            )

    def test_non_kebab_name(self) -> None:
        with pytest.warns(UserWarning, match="kebab-case"):
            metadata = RuleMetadata(
                rule_id="BC001",
                name="TestRule",
                title="T",
                description="d",
                category=Category.CORRECTNESS,
                default_severity=Severity.ERROR,
                motivation="m",
                since="0.1.0",
            )
            assert validate_metadata(metadata) is False

    def test_empty_description(self) -> None:
        with pytest.raises(ValueError, match="description must be a non-empty"):
            RuleMetadata(
                rule_id="BC001",
                name="test-rule",
                title="T",
                description="",
                category=Category.CORRECTNESS,
                default_severity=Severity.ERROR,
                motivation="m",
                since="0.1.0",
            )

    def test_empty_motivation(self) -> None:
        with pytest.raises(ValueError, match="motivation must be a non-empty"):
            RuleMetadata(
                rule_id="BC001",
                name="test-rule",
                title="T",
                description="d",
                category=Category.CORRECTNESS,
                default_severity=Severity.ERROR,
                motivation="",
                since="0.1.0",
            )

    def test_invalid_since(self) -> None:
        with pytest.warns(UserWarning, match="semver"):
            metadata = RuleMetadata(
                rule_id="BC001",
                name="test-rule",
                title="T",
                description="d",
                category=Category.CORRECTNESS,
                default_severity=Severity.ERROR,
                motivation="m",
                since="abc",
            )
            assert validate_metadata(metadata) is False

    def test_valid_rule_id_formats(self) -> None:
        for rule_id in [
            "BC001",
            "BS001",
            "BX001",
            "BK001",
            "BP001",
            "BD001",
            "ACME001",
        ]:
            metadata = RuleMetadata(
                rule_id=rule_id,
                name="test-rule",
                title="T",
                description="d",
                category=Category.CORRECTNESS,
                default_severity=Severity.ERROR,
                motivation="m",
                since="0.1.0",
            )
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                assert validate_metadata(metadata) is True, f"{rule_id} should be valid"

    def test_valid_kebab_names(self) -> None:
        for name in [
            "test-rule",
            "no-empty-feature",
            "max-steps-per-scenario",
            "a1-b2",
        ]:
            metadata = RuleMetadata(
                rule_id="BC001",
                name=name,
                title="T",
                description="d",
                category=Category.CORRECTNESS,
                default_severity=Severity.ERROR,
                motivation="m",
                since="0.1.0",
            )
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                assert validate_metadata(metadata) is True, f"{name} should be valid"
