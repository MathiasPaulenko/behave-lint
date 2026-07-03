"""Tests for the LSP server module."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from behave_lint.models.enums import Severity


@pytest.fixture
def valid_feature_content() -> str:
    """Feature file content that produces no diagnostics."""
    return (
        "@login\n"
        "Feature: User authentication flow\n\n"
        "  Background:\n    Given the user is on the login page\n\n"
        "  @smoke\n  Scenario: Successful login\n"
        "    Given the user is on the login page\n"
        "    When the user enters valid credentials\n"
        "    Then the user should be redirected to the dashboard\n"
    )


@pytest.fixture
def invalid_feature_content() -> str:
    """Invalid feature file content that produces parse errors."""
    return "This is not valid Gherkin at all\n"


class TestDiagnosticConversion:
    """Tests for _diagnostic_to_lsp conversion."""

    def test_error_severity_maps_to_lsp_error(self) -> None:
        """ERROR severity should map to LSP DiagnosticSeverity.Error."""
        from behave_lint.lsp.server import _diagnostic_to_lsp
        from behave_lint.models.diagnostic import Diagnostic
        from behave_lint.models.enums import Category

        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="Test error",
            file_path="test.feature",
            line=5,
            category=Category.CORRECTNESS,
        )
        result = _diagnostic_to_lsp(diag)
        assert result.severity == 1  # DiagnosticSeverity.Error
        assert result.code == "BC001"
        assert result.source == "behave-lint"
        assert result.message == "Test error"

    def test_warning_severity_maps_to_lsp_warning(self) -> None:
        """WARNING severity should map to LSP DiagnosticSeverity.Warning."""
        from behave_lint.lsp.server import _diagnostic_to_lsp
        from behave_lint.models.diagnostic import Diagnostic
        from behave_lint.models.enums import Category

        diag = Diagnostic(
            rule_id="BS001",
            severity=Severity.WARNING,
            message="Test warning",
            file_path="test.feature",
            line=3,
            category=Category.STYLE,
        )
        result = _diagnostic_to_lsp(diag)
        assert result.severity == 2  # DiagnosticSeverity.Warning

    def test_info_severity_maps_to_lsp_information(self) -> None:
        """INFO severity should map to LSP DiagnosticSeverity.Information."""
        from behave_lint.lsp.server import _diagnostic_to_lsp
        from behave_lint.models.diagnostic import Diagnostic
        from behave_lint.models.enums import Category

        diag = Diagnostic(
            rule_id="BP001",
            severity=Severity.INFO,
            message="Test info",
            file_path="test.feature",
            line=2,
            category=Category.PEDANTIC,
        )
        result = _diagnostic_to_lsp(diag)
        assert result.severity == 3  # DiagnosticSeverity.Information

    def test_line_is_zero_indexed(self) -> None:
        """LSP uses 0-indexed lines, behave-lint uses 1-indexed."""
        from behave_lint.lsp.server import _diagnostic_to_lsp
        from behave_lint.models.diagnostic import Diagnostic
        from behave_lint.models.enums import Category

        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="Test",
            file_path="test.feature",
            line=10,
            category=Category.CORRECTNESS,
        )
        result = _diagnostic_to_lsp(diag)
        assert result.range.start.line == 9  # 0-indexed

    def test_column_is_zero_indexed(self) -> None:
        """LSP uses 0-indexed columns, behave-lint uses 1-indexed."""
        from behave_lint.lsp.server import _diagnostic_to_lsp
        from behave_lint.models.diagnostic import Diagnostic
        from behave_lint.models.enums import Category

        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="Test",
            file_path="test.feature",
            line=5,
            column=3,
            category=Category.CORRECTNESS,
        )
        result = _diagnostic_to_lsp(diag)
        assert result.range.start.character == 2  # 0-indexed


class TestLintContent:
    """Tests for _lint_content function."""

    def test_valid_content_returns_no_error_diagnostics(
        self, valid_feature_content: str
    ) -> None:
        """Valid feature content should produce no error diagnostics."""
        from behave_lint.lsp.server import _lint_content

        diagnostics = _lint_content(valid_feature_content, "file:///test.feature")
        error_diags = [d for d in diagnostics if d.severity == 1]  # Error
        assert error_diags == []

    def test_invalid_content_returns_diagnostics(
        self, invalid_feature_content: str
    ) -> None:
        """Invalid feature content should produce parse error diagnostics."""
        from behave_lint.lsp.server import _lint_content

        diagnostics = _lint_content(invalid_feature_content, "file:///test.feature")
        assert len(diagnostics) >= 1
        assert diagnostics[0].code == "B000"
        assert diagnostics[0].source == "behave-lint"

    def test_empty_content_returns_diagnostics(self) -> None:
        """Empty content should produce parse error."""
        from behave_lint.lsp.server import _lint_content

        diagnostics = _lint_content("", "file:///test.feature")
        assert len(diagnostics) >= 1


class TestCreateServer:
    """Tests for create_server function."""

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_server_has_correct_name(self) -> None:
        """Server should be named 'behave-lint'."""
        from behave_lint.lsp.server import create_server

        server = create_server()
        assert server.name == "behave-lint"

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_server_has_version(self) -> None:
        """Server should have a version string."""
        from behave_lint.lsp.server import create_server

        server = create_server()
        assert server.version is not None
        assert len(server.version) > 0


class TestPublishDiagnostics:
    """Tests for _publish_diagnostics function."""

    def test_non_feature_file_skipped(self) -> None:
        """Non-.feature files should be skipped."""
        from behave_lint.lsp.server import _publish_diagnostics

        ls = MagicMock()
        doc = MagicMock()
        doc.uri = "file:///test.py"
        doc.source = "print('hello')"

        _publish_diagnostics(ls, doc)
        ls.text_document_publish_diagnostics.assert_not_called()

    def test_feature_file_publishes_diagnostics(
        self, valid_feature_content: str
    ) -> None:
        """Feature files should trigger publish_diagnostics."""
        from behave_lint.lsp.server import _publish_diagnostics

        ls = MagicMock()
        doc = MagicMock()
        doc.uri = "file:///test.feature"
        doc.source = valid_feature_content

        _publish_diagnostics(ls, doc)
        ls.text_document_publish_diagnostics.assert_called_once()

    def test_invalid_feature_publishes_error_diagnostics(
        self, invalid_feature_content: str
    ) -> None:
        """Invalid feature files should publish error diagnostics."""
        from behave_lint.lsp.server import _publish_diagnostics

        ls = MagicMock()
        doc = MagicMock()
        doc.uri = "file:///bad.feature"
        doc.source = invalid_feature_content

        _publish_diagnostics(ls, doc)
        call_args = ls.text_document_publish_diagnostics.call_args
        params = call_args[0][0]
        assert len(params.diagnostics) >= 1
        assert params.diagnostics[0].severity == 1  # Error
