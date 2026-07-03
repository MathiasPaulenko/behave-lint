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
- `textDocument/codeAction` — quick fixes for fixable diagnostics
- `workspace/didChangeConfiguration` — update settings and re-lint all open documents

## Features

- **Real-time diagnostics** — errors, warnings, and info from all 41
  built-in rules
- **Quick fixes** — `textDocument/codeAction` returns `QuickFix` actions
  with `TextEdit`s for all 14 auto-fixable rules. Click the lightbulb in
  your editor to apply safe and unsafe fixes.
- **Workspace configuration** — configure `select`, `ignore`, `profile`,
  `group`, `severityOverrides`, and `ruleParams` directly from editor
  settings (e.g. VS Code `settings.json`). Changes trigger re-linting of
  all open `.feature` documents.
- **Full document sync** — the server receives the complete document
  content on every change
- **Source attribution** — all diagnostics are tagged with
  `source: behave-lint`
- **Rule codes** — each diagnostic includes the rule ID (e.g. `BC001`,
  `BS001`) as the diagnostic code

## Editor Configuration

The LSP server reads workspace configuration sent by the editor. The
following settings are supported (under the `behave-lint` section):

| Setting | Type | Description |
|---|---|---|
| `select` | `string[]` | Rule IDs to enable (empty = all) |
| `ignore` | `string[]` | Rule IDs to disable |
| `profile` | `string` | Profile name: `recommended`, `strict`, `minimal` |
| `group` | `string[]` | Group names: `correctness`, `style`, `pedantic` |
| `severityOverrides` | `object` | Per-rule severity overrides |
| `ruleParams` | `object` | Per-rule parameters |

### VS Code example

```json
{
  "behave-lint": {
    "profile": "recommended",
    "ignore": ["BD003"]
  }
}
```

### Neovim example

```lua
vim.lsp.config('behave-lint', {
  settings = {
    ['behave-lint'] = {
      profile = 'recommended',
      ignore = { 'BD003' },
    }
  }
})
```

## Limitations

- Full document sync only (no incremental sync)
