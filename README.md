# behave-lint

[![CI](https://github.com/MathiasPaulenko/behave-lint/actions/workflows/ci.yml/badge.svg)](https://github.com/MathiasPaulenko/behave-lint/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)

> A fast, opinionated, extensible linter for Gherkin `.feature` files and Behave test suites.

**behave-lint** statically analyzes your Gherkin feature files for
correctness, consistency, complexity, and style — without executing a
single test. It ships with **41 built-in rules** across 6 categories,
supports **auto-fix** for common violations, and outputs in **5 formats**
including SARIF for GitHub Code Scanning.

## Why behave-lint?

| Without behave-lint | With behave-lint |
|---|---|
| Duplicate step definitions cause silent match failures | **BD001** detects duplicates at lint time |
| Inconsistent tag casing breaks CI filters | **BS001** auto-fixes to `snake_case` |
| Trailing punctuation in steps clutters reports | **BD005** strips it automatically |
| No Given-When-Then ordering enforcement | **BC001** catches structural violations |
| Feature files grow unchecked in complexity | **BX001-BX005** enforce limits |

## Installation

```bash
pip install behave-lint
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add behave-lint
```

## Quick start

```bash
# Lint all feature files
behave-lint features/

# Apply safe auto-fixes
behave-lint features/ --fix

# JSON output for CI integration
behave-lint features/ --json --output-file report.json

# SARIF for GitHub Code Scanning
behave-lint features/ --sarif --output-file results.sarif

# List all available rules
behave-lint --list-rules

# Explain a specific rule
behave-lint --explain BC001
```

## Features

- **41 built-in rules** across 6 categories: correctness, step
  definitions, consistency, complexity, style, and pedantic.
- **Auto-fix** — safe, deterministic fixes for common violations
  (`--fix`). Unsafe fixes require `--unsafe-fixes`.
- **5 output formats** — console (colored), JSON, SARIF, Markdown, and
  GitHub Actions inline annotations.
- **Zero-config** — sensible defaults work out of the box. Override
  anything via `[tool.behave-lint]` in `pyproject.toml`.
- **Plugin system** — write custom rules and reporters as Python
  packages. Register via entry points.
- **CI/CD ready** — deterministic output, clear exit codes, SARIF
  integration with GitHub Code Scanning.
- **Fast** — sub-second on typical projects through caching and
  parallel execution.

## Rules

| Category | Prefix | Rules | Default Severity |
|----------|--------|-------|------------------|
| [Correctness](docs/rules/correctness.md) | BC | 6 | Error |
| [Step Definitions](docs/rules/step-definitions.md) | BD | 5 | Warning |
| [Consistency](docs/rules/consistency.md) | BK | 5 | Warning / Info |
| [Complexity](docs/rules/complexity.md) | BX | 5 | Warning |
| [Style](docs/rules/style.md) | BS | 5 | Warning |
| [Pedantic](docs/rules/pedantic.md) | BP | 5 | Info |

### Auto-fixable rules

| Rule | Fix | Safety |
|------|-----|--------|
| BC004 | Replace invalid tag characters with `_` | Safe |
| BD004 | Convert `{param}` → `<param>` | Safe |
| BD005 | Remove trailing punctuation from steps | Safe |
| BS001 | Convert tags to `snake_case` | Safe |

## Configuration

Configure behave-lint in your `pyproject.toml`:

```toml
[tool.behave-lint]
select = ["BC001", "BC002", "BS001"]
ignore = ["BP001", "BP002"]
fail-on = "warning"
exclude = ["features/wip/"]

[tool.behave-lint.severity]
BK001 = "info"

[tool.behave-lint.rules]
BX001 = { max-steps = 8 }
BP003 = { min-length = 5 }
```

**Precedence** (lowest → highest):

1. Built-in defaults
2. `pyproject.toml` `[tool.behave-lint]`
3. Environment variables (`BEHAVE_LINT_*`)
4. CLI flags

See the [Configuration guide](docs/usage/configuration.md) for all
options.

## CI/CD integration

### GitHub Actions with SARIF

```yaml
- run: pip install behave-lint
- run: behave-lint features/ --sarif --output-file behave-lint.sarif
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: behave-lint.sarif
```

### Inline annotations

```yaml
- run: behave-lint features/ --output github
```

See the [CI/CD guide](docs/guides/ci-cd.md) for full workflows.

## Output formats

| Format | Flag | Use case |
|--------|------|----------|
| Console | `--output console` | Local development (default) |
| JSON | `--json` | CI pipelines, custom tooling |
| SARIF | `--sarif` | GitHub Code Scanning |
| Markdown | `--output markdown` | PR comments, reports |
| GitHub | `--output github` | Inline PR annotations |

See the [Output Formats reference](docs/usage/output-formats.md) for
schema details.

## Examples

Runnable example projects in the [`examples/`](examples/) directory:

| Example | Description |
|---------|-------------|
| [basic-usage](examples/basic-usage/) | Minimal project with configuration |
| [auto-fix](examples/auto-fix/) | Before/after demo of `--fix` |
| [ci-cd](examples/ci-cd/) | GitHub Actions with SARIF upload |
| [custom-rules](examples/custom-rules/) | Custom rule plugin with entry points |

## Documentation

### User guide

- [Installation](docs/getting-started/installation.md)
- [Quick Start](docs/getting-started/quick-start.md)
- [CLI Reference](docs/usage/cli-reference.md)
- [Configuration](docs/usage/configuration.md)
- [Output Formats](docs/usage/output-formats.md)
- [Auto-Fix](docs/usage/auto-fix.md)

### Rules

- [Rules Overview](docs/rules/index.md)
- [Correctness (BC)](docs/rules/correctness.md)
- [Step Definitions (BD)](docs/rules/step-definitions.md)
- [Consistency (BK)](docs/rules/consistency.md)
- [Complexity (BX)](docs/rules/complexity.md)
- [Style (BS)](docs/rules/style.md)
- [Pedantic (BP)](docs/rules/pedantic.md)

### Guides

- [CI/CD Integration](docs/guides/ci-cd.md)
- [Pre-commit Hook](docs/guides/pre-commit.md)
- [Custom Rules](docs/guides/custom-rules.md)
- [Plugin Development](docs/guides/plugin-development.md)

### Design documents

- [Vision](ref/VISION.md) — project vision and mission
- [Specification](ref/SPECIFICATION.md) — full feature specification
- [Architecture](ref/ARCHITECTURE.md) — internal architecture
- [API](ref/API.md) — public API specification
- [Rule Engine Design](ref/RULE_ENGINE.md) — rule lifecycle and execution
- [Rule Taxonomy](ref/RULE_TAXONOMY.md) — rule categories and metadata
- [Configuration System](ref/CONFIGURATION_SYSTEM.md) — configuration schema
- [Implementation Roadmap](ref/IMPLEMENTATION_ROADMAP.md) — milestone plan

## Development

```bash
git clone https://github.com/MathiasPaulenko/behave-lint.git
cd behave-lint
uv sync
uv run pre-commit install

# Run tests
uv run pytest

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/

# Build docs
uv run mkdocs build --strict
```

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed contribution
guidelines, coding standards, and PR workflow.

## License

[MIT](LICENSE)