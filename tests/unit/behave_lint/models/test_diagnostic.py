"""Unit tests for the Diagnostic dataclass.

See API.md Section 4 and DIAGNOSTIC_ENGINE.md Section 3.
"""

from __future__ import annotations

import pytest

from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity


class TestDiagnosticCreation:
    """Tests for Diagnostic construction."""

    def test_minimal(self) -> None:
        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="Duplicate scenario name",
            file_path="features/login.feature",
            line=15,
            category=Category.CORRECTNESS,
        )
        assert diag.rule_id == "BC001"
        assert diag.severity is Severity.ERROR
        assert diag.message == "Duplicate scenario name"
        assert diag.file_path == "features/login.feature"
        assert diag.line == 15
        assert diag.category is Category.CORRECTNESS
        assert diag.column is None
        assert diag.end_line is None
        assert diag.end_column is None
        assert diag.suggestion is None
        assert diag.doc_url is None

    def test_full(self) -> None:
        diag = Diagnostic(
            rule_id="BS001",
            severity=Severity.WARNING,
            message="Tab indentation",
            file_path="features/login.feature",
            line=3,
            category=Category.STYLE,
            column=1,
            end_line=3,
            end_column=4,
            suggestion="Use spaces instead of tabs.",
            doc_url="https://behave-lint.dev/rules/BS001",
        )
        assert diag.column == 1
        assert diag.end_line == 3
        assert diag.end_column == 4
        assert diag.suggestion == "Use spaces instead of tabs."
        assert diag.doc_url == "https://behave-lint.dev/rules/BS001"


class TestDiagnosticImmutability:
    """Tests that Diagnostic is frozen."""

    def test_frozen(self) -> None:
        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="test",
            file_path="f.feature",
            line=1,
            category=Category.CORRECTNESS,
        )
        with pytest.raises(AttributeError):
            diag.message = "changed"  # type: ignore[misc]


class TestDiagnosticValidation:
    """Tests for Diagnostic field validation."""

    def test_line_must_be_positive(self) -> None:
        with pytest.raises(ValueError, match="line must be >= 1"):
            Diagnostic(
                rule_id="BC001",
                severity=Severity.ERROR,
                message="test",
                file_path="f.feature",
                line=0,
                category=Category.CORRECTNESS,
            )

    def test_column_must_be_positive(self) -> None:
        with pytest.raises(ValueError, match="column must be >= 1"):
            Diagnostic(
                rule_id="BC001",
                severity=Severity.ERROR,
                message="test",
                file_path="f.feature",
                line=1,
                column=0,
                category=Category.CORRECTNESS,
            )

    def test_end_line_must_be_ge_line(self) -> None:
        with pytest.raises(ValueError, match="end_line"):
            Diagnostic(
                rule_id="BC001",
                severity=Severity.ERROR,
                message="test",
                file_path="f.feature",
                line=5,
                end_line=3,
                category=Category.CORRECTNESS,
            )

    def test_end_column_requires_column(self) -> None:
        with pytest.raises(ValueError, match="end_column requires column"):
            Diagnostic(
                rule_id="BC001",
                severity=Severity.ERROR,
                message="test",
                file_path="f.feature",
                line=1,
                end_column=5,
                category=Category.CORRECTNESS,
            )


class TestDiagnosticProperties:
    """Tests for Diagnostic computed properties."""

    def test_location_without_column(self) -> None:
        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="test",
            file_path="features/login.feature",
            line=15,
            category=Category.CORRECTNESS,
        )
        assert diag.location == "features/login.feature:15"

    def test_location_with_column(self) -> None:
        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="test",
            file_path="features/login.feature",
            line=15,
            column=3,
            category=Category.CORRECTNESS,
        )
        assert diag.location == "features/login.feature:15:3"

    def test_is_error(self) -> None:
        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="test",
            file_path="f.feature",
            line=1,
            category=Category.CORRECTNESS,
        )
        assert diag.is_error is True
        assert diag.is_warning is False
        assert diag.is_info is False

    def test_is_warning(self) -> None:
        diag = Diagnostic(
            rule_id="BS001",
            severity=Severity.WARNING,
            message="test",
            file_path="f.feature",
            line=1,
            category=Category.STYLE,
        )
        assert diag.is_error is False
        assert diag.is_warning is True
        assert diag.is_info is False

    def test_is_info(self) -> None:
        diag = Diagnostic(
            rule_id="BS001",
            severity=Severity.INFO,
            message="test",
            file_path="f.feature",
            line=1,
            category=Category.STYLE,
        )
        assert diag.is_error is False
        assert diag.is_warning is False
        assert diag.is_info is True
