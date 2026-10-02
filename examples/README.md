# Examples

Runnable example projects demonstrating `behave-lint` features.

## Examples

| Example | Description |
|---------|-------------|
| [minimal](minimal/) | Single feature file + minimal `pyproject.toml` |
| [basic-usage](basic-usage/) | Minimal project with configuration and clean feature files |
| [auto-fix](auto-fix/) | Before/after feature files showing `--fix` in action |
| [ci-cd](ci-cd/) | GitHub Actions workflow with SARIF upload |
| [configs](configs/) | Sample `[tool.behave-lint]` configurations |
| [enterprise](enterprise/) | Stricter config: excludes, severity overrides, warning budget |
| [custom-rules](custom-rules/) | Custom rule plugin with entry point registration |
| [plugin_reporter](plugin_reporter/) | Reporter plugin adding a `csv` output format |
| [plugin_config](plugin_config/) | Config-provider plugin injecting shared defaults |

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
