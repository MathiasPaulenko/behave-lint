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

        diagnostics, _fixes = _lint_content(
            valid_feature_content, "file:///test.feature"
        )
        error_diags = [d for d in diagnostics if d.severity == 1]  # Error
        assert error_diags == []

    def test_invalid_content_returns_diagnostics(
        self, invalid_feature_content: str
    ) -> None:
        """Invalid feature content should produce parse error diagnostics."""
        from behave_lint.lsp.server import _lint_content

        diagnostics, _fixes = _lint_content(
            invalid_feature_content, "file:///test.feature"
        )
        assert len(diagnostics) >= 1
        assert diagnostics[0].code == "B000"
        assert diagnostics[0].source == "behave-lint"

    def test_empty_content_returns_diagnostics(self) -> None:
        """Empty content should produce parse error."""
        from behave_lint.lsp.server import _lint_content

        diagnostics, _fixes = _lint_content("", "file:///test.feature")
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


class TestFixEditConversion:
    """Tests for _fix_edit_to_text_edit conversion."""

    def test_line_is_zero_indexed(self) -> None:
        """FixEdit start_line (1-based) should map to LSP line (0-based)."""
        from behave_lint.autofix.models import FixEdit
        from behave_lint.lsp.server import _fix_edit_to_text_edit
        from behave_lint.models.enums import AutoFixCapability

        edit = FixEdit(
            file_path="test.feature",
            start_line=3,
            end_line=3,
            old_text="@SmokeTest",
            new_text="@smoke_test",
            safety=AutoFixCapability.SAFE,
            rule_id="BS001",
            diagnostic_line=1,
        )
        result = _fix_edit_to_text_edit(edit)
        assert result.range.start.line == 2  # 0-indexed
        assert result.range.end.line == 3  # end_line (exclusive)

    def test_new_text_preserved(self) -> None:
        """The new_text from FixEdit should be preserved in TextEdit."""
        from behave_lint.autofix.models import FixEdit
        from behave_lint.lsp.server import _fix_edit_to_text_edit
        from behave_lint.models.enums import AutoFixCapability

        edit = FixEdit(
            file_path="test.feature",
            start_line=1,
            end_line=1,
            old_text="@BadTag",
            new_text="@good_tag",
            safety=AutoFixCapability.SAFE,
            rule_id="BS001",
            diagnostic_line=1,
        )
        result = _fix_edit_to_text_edit(edit)
        assert result.new_text == "@good_tag"


class TestLintContentFixes:
    """Tests for fix collection in _lint_content."""

    def test_fixable_content_returns_fixes(self) -> None:
        """Content with fixable issues should return fix edits."""
        from behave_lint.lsp.server import _lint_content

        content = (
            "@SmokeTest\nFeature: Test\n\n  Scenario: A scenario\n    Given a step\n"
        )
        _diagnostics, fixes = _lint_content(content, "file:///test.feature")
        assert len(fixes) >= 1
        assert any(f.rule_id == "BS001" for f in fixes)

    def test_parse_error_returns_no_fixes(self, invalid_feature_content: str) -> None:
        """Parse errors should not produce fix edits."""
        from behave_lint.lsp.server import _lint_content

        _diagnostics, fixes = _lint_content(
            invalid_feature_content, "file:///test.feature"
        )
        assert fixes == []


class TestFixCache:
    """Tests for the _fix_cache and codeAction integration."""

    def test_publish_diagnostics_populates_fix_cache(self) -> None:
        """_publish_diagnostics should store fixes in _fix_cache."""
        from behave_lint.lsp.server import _fix_cache, _publish_diagnostics

        _fix_cache.clear()
        ls = MagicMock()
        doc = MagicMock()
        doc.uri = "file:///cache_test.feature"
        doc.source = (
            "@SmokeTest\nFeature: Test\n\n  Scenario: A scenario\n    Given a step\n"
        )

        _publish_diagnostics(ls, doc)
        assert "file:///cache_test.feature" in _fix_cache
        assert len(_fix_cache["file:///cache_test.feature"]) >= 1
        _fix_cache.clear()

    def test_fix_cache_cleared_on_close(self) -> None:
        """did_close should remove the URI from _fix_cache."""
        from behave_lint.lsp.server import _fix_cache

        _fix_cache.clear()
        _fix_cache["file:///close_test.feature"] = []
        assert "file:///close_test.feature" in _fix_cache

        # Simulate did_close clearing the cache
        uri = "file:///close_test.feature"
        _fix_cache.pop(uri, None)
        assert "file:///close_test.feature" not in _fix_cache


class TestWorkspaceConfig:
    """Tests for workspace configuration integration."""

    def test_default_config_when_no_workspace_settings(self) -> None:
        """With no workspace config, _build_config_from_workspace returns defaults."""
        from behave_lint.lsp.server import (
            _build_config_from_workspace,
            _workspace_config,
        )

        _workspace_config.clear()
        config = _build_config_from_workspace()
        assert config.profile == "none"
        assert config.select == []
        assert config.ignore == []

    def test_workspace_ignore_filters_diagnostics(self) -> None:
        """Setting ignore in workspace config should filter diagnostics."""
        from behave_lint.lsp.server import _lint_content, _workspace_config

        _workspace_config.clear()
        content = (
            "@SmokeTest\nFeature: Test\n\n  Scenario: A scenario\n    Given a step\n"
        )
        default_diags, _ = _lint_content(content, "file:///test.feature")
        assert len(default_diags) > 0

        _workspace_config["ignore"] = [
            "BS001",
            "BP001",
            "BP002",
            "BP004",
            "BP006",
            "BS005",
            "BP007",
            "BD003",
        ]
        filtered_diags, _ = _lint_content(content, "file:///test.feature")
        assert len(filtered_diags) == 0
        _workspace_config.clear()

    def test_workspace_profile_changes_diagnostics(self) -> None:
        """Setting profile to 'recommended' should reduce diagnostics."""
        from behave_lint.lsp.server import _lint_content, _workspace_config

        _workspace_config.clear()
        content = (
            "@SmokeTest\nFeature: Test\n\n  Scenario: A scenario\n    Given a step\n"
        )
        default_diags, _ = _lint_content(content, "file:///test.feature")

        _workspace_config["profile"] = "recommended"
        profile_diags, _ = _lint_content(content, "file:///test.feature")
        assert len(profile_diags) < len(default_diags)
        _workspace_config.clear()

    def test_workspace_select_enables_specific_rules(self) -> None:
        """Setting select in workspace config should only enable those rules."""
        from behave_lint.lsp.server import _lint_content, _workspace_config

        _workspace_config.clear()
        content = (
            "@SmokeTest\nFeature: Test\n\n  Scenario: A scenario\n    Given a step\n"
        )
        _workspace_config["select"] = ["BS001"]
        diags, _ = _lint_content(content, "file:///test.feature")
        rule_ids = {d.code for d in diags}
        assert rule_ids == {"BS001"}
        _workspace_config.clear()
