"""Unit tests for domain enums — Severity, Category, AutoFixCapability.

See API.md Section 4 and RULE_TAXONOMY.md Sections 3-5.
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


class TestSeverity:
    """Tests for the Severity enum."""

    def test_members(self) -> None:
        assert Severity.ERROR.value == "error"
        assert Severity.WARNING.value == "warning"
        assert Severity.INFO.value == "info"
        assert Severity.OFF.value == "off"

    def test_from_string_valid(self) -> None:
        assert Severity.from_string("error") is Severity.ERROR
        assert Severity.from_string("WARNING") is Severity.WARNING
        assert Severity.from_string("Info") is Severity.INFO
        assert Severity.from_string("off") is Severity.OFF

    def test_from_string_invalid(self) -> None:
        with pytest.raises(ValueError, match="Invalid severity"):
            Severity.from_string("critical")

    def test_from_string_empty(self) -> None:
        with pytest.raises(ValueError, match="Invalid severity"):
            Severity.from_string("")

    def test_member_count(self) -> None:
        assert len(list(Severity)) == 4


class TestCategory:
    """Tests for the Category enum."""

    def test_members(self) -> None:
        assert Category.CORRECTNESS.value == "correctness"
        assert Category.STYLE.value == "style"
        assert Category.COMPLEXITY.value == "complexity"
        assert Category.CONSISTENCY.value == "consistency"
        assert Category.PEDANTIC.value == "pedantic"
        assert Category.STEP_DEFINITIONS.value == "step_definitions"

    def test_code_property(self) -> None:
        assert Category.CORRECTNESS.code == "C"
        assert Category.STYLE.code == "S"
        assert Category.COMPLEXITY.code == "X"
        assert Category.CONSISTENCY.code == "K"
        assert Category.PEDANTIC.code == "P"
        assert Category.STEP_DEFINITIONS.code == "D"

    def test_default_severity(self) -> None:
        assert Category.CORRECTNESS.default_severity is Severity.ERROR
        assert Category.STYLE.default_severity is Severity.WARNING
        assert Category.COMPLEXITY.default_severity is Severity.WARNING
        assert Category.CONSISTENCY.default_severity is Severity.WARNING
        assert Category.PEDANTIC.default_severity is Severity.OFF
        assert Category.STEP_DEFINITIONS.default_severity is Severity.WARNING

    def test_from_string_valid(self) -> None:
        assert Category.from_string("correctness") is Category.CORRECTNESS
        assert Category.from_string("STYLE") is Category.STYLE

    def test_from_string_invalid(self) -> None:
        with pytest.raises(ValueError, match="Invalid category"):
            Category.from_string("performance")

    def test_from_code_valid(self) -> None:
        assert Category.from_code("C") is Category.CORRECTNESS
        assert Category.from_code("S") is Category.STYLE
        assert Category.from_code("X") is Category.COMPLEXITY
        assert Category.from_code("K") is Category.CONSISTENCY
        assert Category.from_code("P") is Category.PEDANTIC
        assert Category.from_code("D") is Category.STEP_DEFINITIONS

    def test_from_code_invalid(self) -> None:
        with pytest.raises(ValueError, match="Invalid category code"):
            Category.from_code("Z")

    def test_member_count(self) -> None:
        assert len(list(Category)) == 6


class TestAutoFixCapability:
    """Tests for the AutoFixCapability enum."""

    def test_members(self) -> None:
        assert AutoFixCapability.NONE.value == "none"
        assert AutoFixCapability.SAFE.value == "safe"
        assert AutoFixCapability.UNSAFE.value == "unsafe"

    def test_member_count(self) -> None:
        assert len(list(AutoFixCapability)) == 3


class TestFixCost:
    """Tests for the FixCost enum."""

    def test_members(self) -> None:
        assert FixCost.TRIVIAL.value == "trivial"
        assert FixCost.LOW.value == "low"
        assert FixCost.MEDIUM.value == "medium"
        assert FixCost.HIGH.value == "high"


class TestPerformanceImpact:
    """Tests for the PerformanceImpact enum."""

    def test_members(self) -> None:
        assert PerformanceImpact.NEGLIGIBLE.value == "negligible"
        assert PerformanceImpact.LOW.value == "low"
        assert PerformanceImpact.MEDIUM.value == "medium"
        assert PerformanceImpact.HIGH.value == "high"


class TestEducationalValue:
    """Tests for the EducationalValue enum."""

    def test_members(self) -> None:
        assert EducationalValue.NONE.value == "none"
        assert EducationalValue.LOW.value == "low"
        assert EducationalValue.MEDIUM.value == "medium"
        assert EducationalValue.HIGH.value == "high"
