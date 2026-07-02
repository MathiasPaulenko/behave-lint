"""Unit tests for diagnostic validation.

See DIAGNOSTIC_ENGINE.md Section 2 (Validation stage).
"""

from __future__ import annotations

import warnings

import pytest

from behave_lint.diagnostics.validation import (
    validate_diagnostic,
    validate_diagnostics,
)
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity


def _make_diag(**overrides: object) -> Diagnostic:
    defaults: dict[str, object] = {
        "rule_id": "BC001",
        "severity": Severity.ERROR,
        "message": "Duplicate scenario name",
        "file_path": "features/login.feature",
        "line": 15,
        "category": Category.CORRECTNESS,
    }
    defaults.update(overrides)
    return Diagnostic(**defaults)  # type: ignore[arg-type]


class TestValidateDiagnostic:
    """Tests for validate_diagnostic()."""

    def test_valid_diagnostic(self) -> None:
        diag = _make_diag()
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            assert validate_diagnostic(diag) is True

    def test_empty_rule_id(self) -> None:
        diag = _make_diag(rule_id="")
        with pytest.warns(UserWarning, match="rule_id"):
            assert validate_diagnostic(diag) is False

    def test_empty_message(self) -> None:
        diag = _make_diag(message="")
        with pytest.warns(UserWarning, match="message"):
            assert validate_diagnostic(diag) is False

    def test_empty_file_path(self) -> None:
        diag = _make_diag(file_path="")
        with pytest.warns(UserWarning, match="file_path"):
            assert validate_diagnostic(diag) is False

    def test_line_validation_in_dataclass(self) -> None:
        # Diagnostic dataclass already validates line >= 1 in __post_init__
        with pytest.raises(ValueError, match="line must be >= 1"):
            _make_diag(line=0)

        with pytest.raises(ValueError, match="line must be >= 1"):
            _make_diag(line=-1)

    def test_valid_with_optional_fields(self) -> None:
        diag = _make_diag(
            column=3,
            end_line=20,
            end_column=10,
            suggestion="Rename the scenario",
            doc_url="https://behave-lint.dev/rules/BC001",
        )
        assert validate_diagnostic(diag) is True


class TestValidateDiagnostics:
    """Tests for validate_diagnostics()."""

    def test_all_valid(self) -> None:
        diags = [_make_diag(), _make_diag(rule_id="BS001")]
        result = validate_diagnostics(diags)
        assert len(result) == 2

    def test_filters_invalid(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            diags = [_make_diag(), _make_diag(rule_id="")]
            result = validate_diagnostics(diags)
        assert len(result) == 1
        assert result[0].rule_id == "BC001"

    def test_empty_list(self) -> None:
        result = validate_diagnostics([])
        assert result == []
