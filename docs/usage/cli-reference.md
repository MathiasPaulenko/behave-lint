# CLI Reference

## Synopsis

```
behave-lint [OPTIONS] [PATHS]...
```

## Positional arguments

| Argument | Description |
|----------|-------------|
| `PATHS`  | Files or directories to lint. Defaults to current directory. |

## Rule selection

| Option | Description |
|--------|-------------|
| `--select RULES` | Enable specific rules (comma-separated). Overrides configuration. |
| `--ignore RULES` | Disable specific rules (comma-separated). Overrides configuration. |
| `--profile NAME` | Use a built-in profile: `recommended`, `strict`, `minimal`. |
| `--fail-on LEVEL` | Exit with non-zero code if diagnostics at or above this severity are found. One of `error`, `warning`, `info`. Default: `warning`. |

## Output

| Option | Description |
|--------|-------------|
| `--output FORMAT` | Output format: `console`, `json`, `markdown`, `sarif`, `github`. Default: `console`. |
| `--output-file FILE` | Write output to file instead of stdout. |
| `--color` | Force enable colored output. |
| `--no-color` | Force disable colored output. |
| `--verbose` | Show progress and timing information. |
| `--quiet` | Suppress all output except diagnostics. |
| `--statistics` | Show rule statistics summary. |

## Configuration

| Option | Description |
|--------|-------------|
| `--config FILE` | Explicit path to `pyproject.toml`. |
| `--no-cache` | Disable cache for this run. |
| `--clear-cache` | Clear cache before running. |

## Auto-fix

| Option | Description |
|--------|-------------|
| `--fix` | Apply safe auto-fixes to `.feature` files. |
| `--unsafe-fixes` | Also apply unsafe auto-fixes (use with caution). |

## Watch mode

| Option | Description |
|--------|-------------|
| `--watch` | Watch for file changes and re-lint automatically. Requires `watchdog` (`pip install behave-lint[watch]`). |

## Informational

| Option | Description |
|--------|-------------|
| `--list-rules` | List all available rules and exit. |
| `--explain RULE_ID` | Show documentation for the specified rule and exit. |
| `--version` | Show version and exit. |
| `--help` | Show help message and exit. |

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | No diagnostics at or above the `--fail-on` threshold. |
| 1 | Diagnostics found at or above the threshold. |
| 2 | Internal error (invalid arguments, parse failure, etc.). |

## Examples

```bash
# Lint all features in the current directory
behave-lint .

# Lint with JSON output to a file
behave-lint features/ --output json --output-file report.json

# Apply safe fixes
behave-lint features/ --fix

# Lint with only correctness rules
behave-lint features/ --select BC001,BC002,BC003,BC004,BC005,BC006

# Use the strict profile (all rules including pedantic)
behave-lint features/ --profile strict

# Use the minimal profile (only correctness + step definitions)
behave-lint features/ --profile minimal

# Explain a rule
behave-lint --explain BD005

# Watch for changes and re-lint automatically
behave-lint features/ --watch
```
