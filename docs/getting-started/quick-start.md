# Quick Start

## Lint your feature files

Navigate to your Behave project and run:

```bash
behave-lint features/
```

This scans all `.feature` files under `features/` and reports diagnostics
to the console.

## Filter by severity

By default, `behave-lint` fails on warnings and errors. Use `--fail-on`
to change the threshold:

```bash
# Only fail on errors
behave-lint features/ --fail-on error

# Fail on any diagnostic (including info)
behave-lint features/ --fail-on info
```

## Select specific rules

```bash
behave-lint features/ --select BC001,BC004,BS001
```

## Ignore rules

```bash
behave-lint features/ --ignore BP001,BP002
```

## Output formats

```bash
# JSON
behave-lint features/ --json

# SARIF (for GitHub Code Scanning)
behave-lint features/ --sarif

# Markdown report
behave-lint features/ --output markdown --output-file report.md
```

## Auto-fix

Apply safe auto-fixes directly to your feature files:

```bash
behave-lint features/ --fix
```

See the [Auto-Fix guide](../usage/auto-fix.md) for details.

## List available rules

```bash
behave-lint --list-rules
```

## Explain a specific rule

```bash
behave-lint --explain BC004
```

## Next steps

- [Configuration](../usage/configuration.md) — set up `pyproject.toml`
- [Output Formats](../usage/output-formats.md) — console, JSON, SARIF, Markdown, GitHub
- [Rules Overview](../rules/index.md) — browse all 31 built-in rules
- [CI/CD Integration](../guides/ci-cd.md) — automate in your pipeline
