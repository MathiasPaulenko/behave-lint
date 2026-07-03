"""LSP server for behave-lint.

Implements a Language Server Protocol server that provides real-time
diagnostics for Gherkin .feature files. Uses pygls for LSP transport
and the behave-lint engine for analysis.

Run with::

    behave-lint-lsp
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from behave_lint.autofix.models import FixEdit
from behave_lint.engine.lint_engine import LintEngine
from behave_lint.models.config import Config
from behave_lint.models.enums import Severity
from behave_lint.rules.registry import RuleRegistry

if TYPE_CHECKING:
    from behave_lint.models.diagnostic import Diagnostic as BLDiagnostic

logger = logging.getLogger(__name__)

try:
    from lsprotocol import types as lsp
    from pygls.lsp.server import LanguageServer
    from pygls.workspace import TextDocument
except ImportError as exc:
    raise ImportError(
        "pygls and lsprotocol are required for LSP support. "
        "Install with: pip install behave-lint[lsp]"
    ) from exc

_SEVERITY_MAP: dict[Severity, lsp.DiagnosticSeverity] = {
    Severity.ERROR: lsp.DiagnosticSeverity.Error,
    Severity.WARNING: lsp.DiagnosticSeverity.Warning,
    Severity.INFO: lsp.DiagnosticSeverity.Information,
    Severity.OFF: lsp.DiagnosticSeverity.Hint,
}


def _diagnostic_to_lsp(diag: BLDiagnostic) -> lsp.Diagnostic:
    """Convert a behave-lint Diagnostic to an LSP Diagnostic.

    Args:
        diag: The behave-lint diagnostic.

    Returns:
        An LSP Diagnostic object.
    """
    line = max(0, diag.line - 1)
    end_line = max(0, (diag.end_line or diag.line) - 1)
    end_col = diag.end_column or (diag.column or 1)
    col = max(0, (diag.column or 1) - 1)

    return lsp.Diagnostic(
        range=lsp.Range(
            start=lsp.Position(line=line, character=col),
            end=lsp.Position(line=end_line, character=end_col),
        ),
        severity=_SEVERITY_MAP.get(diag.severity, lsp.DiagnosticSeverity.Warning),
        code=diag.rule_id,
        source="behave-lint",
        message=diag.message,
    )


def _fix_edit_to_text_edit(edit: FixEdit) -> lsp.TextEdit:
    """Convert a behave-lint FixEdit to an LSP TextEdit.

    Args:
        edit: The fix edit to convert.

    Returns:
        An LSP TextEdit object.
    """
    return lsp.TextEdit(
        range=lsp.Range(
            start=lsp.Position(line=edit.start_line - 1, character=0),
            end=lsp.Position(line=edit.end_line, character=0),
        ),
        new_text=edit.new_text,
    )


def _lint_content(
    content: str, file_uri: str
) -> tuple[list[lsp.Diagnostic], list[FixEdit]]:
    """Lint feature file content and return LSP diagnostics plus fixes.

    Writes content to a temporary .feature file, runs the lint engine,
    and converts diagnostics to LSP format.

    Args:
        content: The feature file content.
        file_uri: The URI of the document (for filtering diagnostics).

    Returns:
        A tuple of (LSP diagnostics, fix edits) for this document.
    """
    config = Config()
    registry = RuleRegistry()
    from behave_lint.rules.builtin import register_builtins

    register_builtins(registry)
    engine = LintEngine(config, registry)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".feature", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = engine.lint([tmp_path], collect_fixes=True)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    diagnostics: list[lsp.Diagnostic] = []
    for diag in result.diagnostics:
        if diag.file_path.endswith(tmp_path) or diag.file_path == tmp_path:
            diagnostics.append(_diagnostic_to_lsp(diag))

    fixes = [f for f in result.fixes if f.file_path == tmp_path]

    return diagnostics, fixes


def _publish_diagnostics(ls: LanguageServer, doc: TextDocument) -> None:
    """Lint a document and publish diagnostics to the client.

    Also stores fix edits for later use by codeAction requests.

    Args:
        ls: The language server instance.
        doc: The text document to lint.
    """
    if not doc.uri.endswith(".feature"):
        return

    diagnostics, fixes = _lint_content(doc.source, doc.uri)
    ls.text_document_publish_diagnostics(
        lsp.PublishDiagnosticsParams(uri=doc.uri, diagnostics=diagnostics)
    )
    _fix_cache[doc.uri] = fixes


_fix_cache: dict[str, list[FixEdit]] = {}


def create_server() -> LanguageServer:
    """Create and configure the behave-lint language server.

    Returns:
        A configured LanguageServer instance ready to start.
    """
    server = LanguageServer(
        name="behave-lint",
        version="2.1.0",
        text_document_sync_kind=lsp.TextDocumentSyncKind.Full,
    )

    @server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
    def did_open(ls: LanguageServer, params: lsp.DidOpenTextDocumentParams) -> None:
        """Handle textDocument/didOpen — lint and publish diagnostics."""
        doc = ls.workspace.get_text_document(params.text_document.uri)
        _publish_diagnostics(ls, doc)

    @server.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
    def did_change(ls: LanguageServer, params: lsp.DidChangeTextDocumentParams) -> None:
        """Handle textDocument/didChange — re-lint and publish diagnostics."""
        doc = ls.workspace.get_text_document(params.text_document.uri)
        _publish_diagnostics(ls, doc)

    @server.feature(lsp.TEXT_DOCUMENT_DID_SAVE)
    def did_save(ls: LanguageServer, params: lsp.DidSaveTextDocumentParams) -> None:
        """Handle textDocument/didSave — re-lint and publish diagnostics."""
        doc = ls.workspace.get_text_document(params.text_document.uri)
        _publish_diagnostics(ls, doc)

    @server.feature(lsp.TEXT_DOCUMENT_DID_CLOSE)
    def did_close(ls: LanguageServer, params: lsp.DidCloseTextDocumentParams) -> None:
        """Handle textDocument/didClose — clear diagnostics and fix cache."""
        uri = params.text_document.uri
        _fix_cache.pop(uri, None)
        ls.text_document_publish_diagnostics(
            lsp.PublishDiagnosticsParams(uri=uri, diagnostics=[])
        )

    @server.feature(
        lsp.TEXT_DOCUMENT_CODE_ACTION,
        lsp.CodeActionOptions(code_action_kinds=[lsp.CodeActionKind.QuickFix]),
    )
    def code_action(
        ls: LanguageServer,
        params: lsp.CodeActionParams,
    ) -> list[lsp.CodeAction]:
        """Handle textDocument/codeAction — return available quick fixes."""
        uri = params.text_document.uri
        fixes = _fix_cache.get(uri, [])
        if not fixes:
            return []

        actions: list[lsp.CodeAction] = []
        for fix in fixes:
            title = f"Fix {fix.rule_id}: {fix.safety.name.lower()} fix"
            text_edit = _fix_edit_to_text_edit(fix)
            actions.append(
                lsp.CodeAction(
                    title=title,
                    kind=lsp.CodeActionKind.QuickFix,
                    edit=lsp.WorkspaceEdit(
                        changes={uri: [text_edit]},
                    ),
                )
            )
        return actions

    return server


def main() -> None:
    """Entry point for the LSP server."""
    server = create_server()
    server.start_io()


__all__ = ["_fix_edit_to_text_edit", "_lint_content", "create_server", "main"]
