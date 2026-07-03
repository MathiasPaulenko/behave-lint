# behave-lint

A fast, opinionated, extensible linter for Gherkin `.feature` files and
Behave test suites.

## Features

- **41 built-in rules** across 6 categories: correctness, step
  definitions, consistency, complexity, style, and pedantic.
- **Auto-fix** support for 14 rules (safe and unsafe).
- **Watch mode** — re-lint on file changes with `--watch`.
- **Multiple output formats**: console, JSON, SARIF, Markdown, GitHub
  Actions annotations.
- **Plugin system** for custom rules and reporters.
- **Configurable** via `pyproject.toml` (`[tool.behave-lint]` section).
- **Fast** — caches parsed models for incremental linting.

## Quick start

```bash
pip install behave-lint
behave-lint features/
```

## Documentation

- [Installation](getting-started/installation.md)
- [Quick Start](getting-started/quick-start.md)
- [CLI Reference](usage/cli-reference.md)
- [Configuration](usage/configuration.md)
- [Auto-Fix](usage/auto-fix.md)
- [Watch Mode](usage/cli-reference.md#watch-mode)
- [Output Formats](usage/output-formats.md)
- [Rules](rules/index.md)
- [Guides](guides/index.md)
