"""Unit tests for the exit code manager."""

from __future__ import annotations

from behave_lint.cli.exit_codes import (
    config_error_exit_code,
    determine_exit_code,
    internal_error_exit_code,
)
from behave_lint.constants import (
    EXIT_CODE_CONFIG_ERROR,
    EXIT_CODE_INTERNAL_ERROR,
    EXIT_CODE_SUCCESS,
    EXIT_CODE_USER_ERROR,
)
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity


def _make_diag(severity: Severity) -> Diagnostic:
    return Diagnostic(
        rule_id="BC001",
        severity=severity,
        message="Test",
        file_path="test.feature",
        line=1,
        category=Category.CORRECTNESS,
    )


class TestDetermineExitCode:
    """Tests for determine_exit_code."""

    def test_no_diagnostics(self) -> None:
        assert determine_exit_code([], Severity.WARNING) == EXIT_CODE_SUCCESS

    def test_error_diag_with_warning_threshold(self) -> None:
        diags = [_make_diag(Severity.ERROR)]
        assert determine_exit_code(diags, Severity.WARNING) == EXIT_CODE_USER_ERROR

    def test_warning_diag_with_warning_threshold(self) -> None:
        diags = [_make_diag(Severity.WARNING)]
        assert determine_exit_code(diags, Severity.WARNING) == EXIT_CODE_USER_ERROR

    def test_info_diag_with_warning_threshold(self) -> None:
        diags = [_make_diag(Severity.INFO)]
        assert determine_exit_code(diags, Severity.WARNING) == EXIT_CODE_SUCCESS

    def test_error_diag_with_error_threshold(self) -> None:
        diags = [_make_diag(Severity.ERROR)]
        assert determine_exit_code(diags, Severity.ERROR) == EXIT_CODE_USER_ERROR

    def test_warning_diag_with_error_threshold(self) -> None:
        diags = [_make_diag(Severity.WARNING)]
        assert determine_exit_code(diags, Severity.ERROR) == EXIT_CODE_SUCCESS

    def test_info_diag_with_info_threshold(self) -> None:
        diags = [_make_diag(Severity.INFO)]
        assert determine_exit_code(diags, Severity.INFO) == EXIT_CODE_USER_ERROR

    def test_off_threshold_always_success(self) -> None:
        diags = [_make_diag(Severity.ERROR)]
        assert determine_exit_code(diags, Severity.OFF) == EXIT_CODE_SUCCESS

    def test_mixed_diagnostics(self) -> None:
        diags = [
            _make_diag(Severity.INFO),
            _make_diag(Severity.WARNING),
            _make_diag(Severity.ERROR),
        ]
        assert determine_exit_code(diags, Severity.WARNING) == EXIT_CODE_USER_ERROR

    def test_mixed_diagnostics_below_threshold(self) -> None:
        diags = [
            _make_diag(Severity.INFO),
            _make_diag(Severity.WARNING),
        ]
        assert determine_exit_code(diags, Severity.ERROR) == EXIT_CODE_SUCCESS


class TestConfigErrorExitCode:
    """Tests for config_error_exit_code."""

    def test_returns_config_error_code(self) -> None:
        assert config_error_exit_code() == EXIT_CODE_CONFIG_ERROR


class TestInternalErrorExitCode:
    """Tests for internal_error_exit_code."""

    def test_returns_internal_error_code(self) -> None:
        assert internal_error_exit_code() == EXIT_CODE_INTERNAL_ERROR
