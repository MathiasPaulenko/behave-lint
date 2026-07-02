"""Unit tests for configuration schema validation.

See CONFIGURATION_SYSTEM.md Section 12.
"""

from __future__ import annotations

import warnings

import pytest

from behave_lint.configuration.schema import (
    check_unknown_keys,
    normalize_keys,
    validate_fail_on,
    validate_severity_overrides,
    validate_types,
)
from behave_lint.exceptions import InvalidConfigValueError
from behave_lint.models.enums import Severity


class TestNormalizeKeys:
    """Tests for normalize_keys()."""

    def test_kebab_to_snake(self) -> None:
        raw = {"output-file": "results.json", "cache-dir": "/tmp"}
        result = normalize_keys(raw)
        assert "output_file" in result
        assert "cache_dir" in result
        assert "output-file" not in result

    def test_snake_case_unchanged(self) -> None:
        raw = {"select": ["BC001"], "output": "json"}
        result = normalize_keys(raw)
        assert result == raw

    def test_mixed(self) -> None:
        raw = {"output-file": "r.json", "select": ["BC001"], "fail-on": "error"}
        result = normalize_keys(raw)
        assert "output_file" in result
        assert "fail_on" in result
        assert "select" in result


class TestCheckUnknownKeys:
    """Tests for check_unknown_keys()."""

    def test_no_unknowns(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            unknown = check_unknown_keys({"select": [], "ignore": []})
        assert unknown == []

    def test_unknown_key_warns(self) -> None:
        with pytest.warns(UserWarning, match="Unknown configuration key"):
            unknown = check_unknown_keys({"unknwon_key": 1})
        assert unknown == ["unknwon_key"]

    def test_multiple_unknowns(self) -> None:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            unknown = check_unknown_keys({"foo": 1, "bar": 2, "select": []})
        assert set(unknown) == {"foo", "bar"}
        assert len(w) == 2


class TestValidateTypes:
    """Tests for validate_types()."""

    def test_valid_types(self) -> None:
        validate_types(
            {
                "select": ["BC001"],
                "ignore": [],
                "output": "json",
                "cache": True,
                "paths": ["features/"],
            }
        )

    def test_invalid_select_type(self) -> None:
        with pytest.raises(InvalidConfigValueError, match="select"):
            validate_types({"select": "BC001"})

    def test_invalid_cache_type(self) -> None:
        with pytest.raises(InvalidConfigValueError, match="cache"):
            validate_types({"cache": "yes"})

    def test_invalid_output_type(self) -> None:
        with pytest.raises(InvalidConfigValueError, match="output"):
            validate_types({"output": 123})


class TestValidateSeverityOverrides:
    """Tests for validate_severity_overrides()."""

    def test_valid(self) -> None:
        result = validate_severity_overrides({"BC001": "error", "BS001": "info"})
        assert result["BC001"] is Severity.ERROR
        assert result["BS001"] is Severity.INFO

    def test_invalid_severity(self) -> None:
        with pytest.raises(InvalidConfigValueError, match=r"severity\.BC001"):
            validate_severity_overrides({"BC001": "critical"})

    def test_empty(self) -> None:
        result = validate_severity_overrides({})
        assert result == {}


class TestValidateFailOn:
    """Tests for validate_fail_on()."""

    def test_valid(self) -> None:
        assert validate_fail_on("error") is Severity.ERROR
        assert validate_fail_on("warning") is Severity.WARNING
        assert validate_fail_on("info") is Severity.INFO
        assert validate_fail_on("off") is Severity.OFF

    def test_invalid(self) -> None:
        with pytest.raises(InvalidConfigValueError, match="fail_on"):
            validate_fail_on("critical")
