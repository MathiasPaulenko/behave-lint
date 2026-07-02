# Examples

Runnable example projects demonstrating `behave-lint` features.

## Examples

| Example | Description |
|---------|-------------|
| [basic-usage](basic-usage/) | Minimal project with configuration and clean feature files |
| [auto-fix](auto-fix/) | Before/after feature files showing `--fix` in action |
| [ci-cd](ci-cd/) | GitHub Actions workflow with SARIF upload |
| [custom-rules](custom-rules/) | Custom rule plugin with entry point registration |

## Prerequisites

```bash
# Install behave-lint from the project root
pip install -e .
```

## Running an example

Each example has its own `README.md` with specific instructions. In
general:

```bash
cd examples/<example-name>
behave-lint features/
```

## What you'll learn

- **basic-usage**: How to configure `behave-lint` via `pyproject.toml`,
  select rules, and override severities.
- **auto-fix**: Which rules are auto-fixable and what the transformed
  output looks like.
- **ci-cd**: How to integrate `behave-lint` into GitHub Actions with
  SARIF output for Code Scanning.
- **custom-rules**: How to write a custom rule, register it as an entry
  point, and use it in a project.
