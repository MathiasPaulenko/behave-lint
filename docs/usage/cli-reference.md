# CLI Reference

## Synopsis

```
behave-lint [OPTIONS] [PATHS]...
```

## Positional arguments

| Argument | Description |
|----------|-------------|
| `PATHS`  | Files or directories to lint. Defaults to the `paths` configuration value (`features/` by default). |

## Rule selection

| Option | Description |
|--------|-------------|
| `--select RULES` | Enable specific rules (comma-separated). Overrides configuration. |
| `--ignore RULES` | Disable specific rules (comma-separated). Overrides configuration. |
| `--exclude PATTERNS` | Exclude files/dirs (comma-separated globs or directory prefixes). Added to the configured `exclude` list. |
| `--profile NAME` | Use a built-in profile: `recommended`, `strict`, `minimal`. |
| `--group GROUPS` | Select rules by group (comma-separated): `correctness`, `style`, `pedantic`, `step-definitions`, `consistency`, `complexity`, `security`, `i18n`, `accessibility`, or tag groups (`naming`, `tags`, `steps`, `background`, `description`, `documentation`, `formatting`, `examples`, `scenarios`, `readability`). |
| `--fail-on LEVEL` | Exit with non-zero code if diagnostics at or above this severity are found. One of `error`, `warning`, `info`, `off`. Default: `warning`. |

## Output

| Option | Description |
|--------|-------------|
| `--output FORMAT` | Output format: `console`, `json`, `markdown`, `sarif`, `github`. Default: `console`. |
| `--output-file FILE` | Write output to file instead of stdout. |
| `--color` | Force enable colored output. |
| `--no-color` | Force disable colored output. |
| `--verbose` | Show progress and timing information. |
| `--quiet` | Suppress all output, including diagnostics. The exit code still applies. |
| `--statistics` | Show a statistics summary (diagnostics, rules executed, cache hits/misses). |

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
| `--dry-run` | Preview fixes without writing any files. |

## Watch mode

| Option | Description |
|--------|-------------|
| `--watch` | Watch for file changes and re-lint automatically. Requires `watchdog` (`pip install behave-lint[watch]`). |

## Performance

|| Option | Description |
||--------|-------------|
|| `--jobs N` | Thread pool size for rule execution. Default: CPU count. |

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
| 0 | No diagnostics at or above the `--fail-on` threshold, and the warning count is within `max-warnings`. |
| 1 | Diagnostics found at or above the threshold, or warnings above `max-warnings`. Syntax/parse errors (`B000`) are errors and therefore also exit 1. |
| 2 | Configuration or user error (invalid config file, unknown option, unknown rule). |
| 3 | Internal error — indicates a bug in behave-lint. |

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
