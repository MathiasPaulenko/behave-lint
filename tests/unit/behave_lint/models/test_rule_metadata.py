"""Unit tests for RuleMetadata and RuleExample.

See API.md Section 4, RULE_ENGINE.md Section 4, RULE_TAXONOMY.md Section 5.
"""

from __future__ import annotations

import pytest

from behave_lint.models.enums import (
    AutoFixCapability,
    Category,
    EducationalValue,
    FixCost,
    PerformanceImpact,
    Severity,
)
from behave_lint.models.rule_metadata import RuleExample, RuleMetadata


def _make_metadata(**overrides: object) -> RuleMetadata:
    defaults: dict[str, object] = {
        "rule_id": "BC001",
        "name": "duplicate-scenario-name",
        "title": "Duplicate Scenario Name",
        "description": "Detects scenarios with the same name within a feature.",
        "category": Category.CORRECTNESS,
        "default_severity": Severity.ERROR,
        "motivation": "Duplicate scenario names cause confusion.",
        "since": "0.1.0",
    }
    defaults.update(overrides)
    return RuleMetadata(**defaults)  # type: ignore[arg-type]


class TestRuleExample:
    """Tests for RuleExample."""

    def test_creation(self) -> None:
        example = RuleExample(
            before="Scenario: Login",
            after="Scenario: Login successful",
            description="Rename to be unique.",
        )
        assert example.before == "Scenario: Login"
        assert example.after == "Scenario: Login successful"
        assert example.description == "Rename to be unique."

    def test_frozen(self) -> None:
        example = RuleExample(before="a", after="b", description="c")
        with pytest.raises(AttributeError):
            example.before = "x"  # type: ignore[misc]


class TestRuleMetadataCreation:
    """Tests for RuleMetadata construction."""

    def test_minimal(self) -> None:
        meta = _make_metadata()
        assert meta.rule_id == "BC001"
        assert meta.name == "duplicate-scenario-name"
        assert meta.title == "Duplicate Scenario Name"
        assert meta.category is Category.CORRECTNESS
        assert meta.default_severity is Severity.ERROR
        assert meta.auto_fix is AutoFixCapability.NONE
        assert meta.experimental is False
        assert meta.deprecated is False
        assert meta.replaced_by is None
        assert meta.examples == []
        assert meta.tags == []
        assert meta.configurable is False

    def test_full(self) -> None:
        meta = _make_metadata(
            auto_fix=AutoFixCapability.SAFE,
            tags=["scenario", "feature"],
            references=["https://cucumber.io/docs/bdd/"],
            configurable=True,
            experimental=True,
            estimated_fix_cost=FixCost.LOW,
            performance_impact=PerformanceImpact.NEGLIGIBLE,
            educational_value=EducationalValue.MEDIUM,
            examples=[
                RuleExample(
                    before="Scenario: Login",
                    after="Scenario: Login successful",
                    description="Rename to be unique.",
                ),
            ],
        )
        assert meta.auto_fix is AutoFixCapability.SAFE
        assert meta.tags == ["scenario", "feature"]
        assert meta.references == ["https://cucumber.io/docs/bdd/"]
        assert meta.configurable is True
        assert meta.experimental is True
        assert meta.estimated_fix_cost is FixCost.LOW
        assert meta.performance_impact is PerformanceImpact.NEGLIGIBLE
        assert meta.educational_value is EducationalValue.MEDIUM
        assert len(meta.examples) == 1


class TestRuleMetadataValidation:
    """Tests for RuleMetadata field validation."""

    def test_empty_rule_id(self) -> None:
        with pytest.raises(ValueError, match="rule_id"):
            _make_metadata(rule_id="")

    def test_empty_name(self) -> None:
        with pytest.raises(ValueError, match="name"):
            _make_metadata(name="")

    def test_empty_description(self) -> None:
        with pytest.raises(ValueError, match="description"):
            _make_metadata(description="")

    def test_empty_motivation(self) -> None:
        with pytest.raises(ValueError, match="motivation"):
            _make_metadata(motivation="")

    def test_empty_since(self) -> None:
        with pytest.raises(ValueError, match="since"):
            _make_metadata(since="")


class TestRuleMetadataImmutability:
    """Tests that RuleMetadata is frozen."""

    def test_frozen(self) -> None:
        meta = _make_metadata()
        with pytest.raises(AttributeError):
            meta.rule_id = "BC002"  # type: ignore[misc]
