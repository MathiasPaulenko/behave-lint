# Language Server Protocol

behave-lint includes an LSP server for real-time diagnostics in any
LSP-compatible editor (VS Code, Neovim, Emacs, etc.).

## Installation

Install with the `lsp` optional dependency:

```bash
pip install behave-lint[lsp]
```

Or with uv:

```bash
uv add 'behave-lint[lsp]'
```

## Usage

The LSP server communicates over stdio:

```bash
behave-lint-lsp
```

## Editor configuration

### VS Code

Add the following to `.vscode/settings.json`:

```json
{
  "gherkin-lint.server.path": "behave-lint-lsp",
  "gherkin-lint.enabled": true
}
```

Or use a custom extension that connects to the server.

### Neovim (nvim-lspconfig)

```lua
local lspconfig = require('lspconfig')
lspconfig.behave_lint.setup({
  cmd = { 'behave-lint-lsp' },
  filetypes = { 'gherkin', 'feature' },
  root_dir = function(bufnr, callback)
    callback(vim.fn.getcwd())
  end,
})
```

### Emacs (eglot)

```elisp
(with-eval-after-load 'eglot
  (add-to-list 'eglot-server-programs
               '((feature-mode) "behave-lint-lsp")))
```

### Generic LSP client

Any LSP client that supports stdio transport can connect to
`behave-lint-lsp`. The server advertises:

- `textDocument/didOpen` — lint on file open
- `textDocument/didChange` — re-lint on every edit (full sync)
- `textDocument/didSave` — re-lint on save
- `textDocument/didClose` — clear diagnostics

## Features

- **Real-time diagnostics** — errors, warnings, and info from all 41
  built-in rules
- **Full document sync** — the server receives the complete document
  content on every change
- **Source attribution** — all diagnostics are tagged with
  `source: behave-lint`
- **Rule codes** — each diagnostic includes the rule ID (e.g. `BC001`,
  `BS001`) as the diagnostic code

## Limitations

- No auto-fix via LSP yet (planned for future versions)
- No configuration via LSP workspace configuration yet (uses
  `pyproject.toml` if present, otherwise defaults)
- Full document sync only (no incremental sync)
