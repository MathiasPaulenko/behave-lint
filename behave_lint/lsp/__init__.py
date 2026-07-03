"""Language Server Protocol support for behave-lint.

Provides real-time diagnostics for .feature files in any LSP-compatible
editor (VS Code, Neovim, Emacs, etc.).

Install with::

    pip install behave-lint[lsp]

Run with::

    behave-lint-lsp
"""

from behave_lint.lsp.server import create_server, main

__all__ = ["create_server", "main"]
