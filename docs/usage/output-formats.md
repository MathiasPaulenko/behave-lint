# Output Formats

`behave-lint` supports five output formats. Use `--output FORMAT` or
the shortcut flags (`--json`, `--sarif`).

## Console

Human-readable output for terminal use. Diagnostics are grouped and
formatted with optional ANSI color support.

```bash
behave-lint features/
behave-lint features/ --color
behave-lint features/ --no-color
```

**File output:** Not supported (always stdout).

**Features:**

- Auto-detects terminal for color support
- Severity labels: `error` (red), `warning` (yellow), `info` (blue)
- Summary line with counts and timing

## JSON

Machine-readable JSON with a stable, versioned schema.

```bash
behave-lint features/ --json
behave-lint features/ --json --output-file report.json
```

**File output:** Supported.

**Schema version:** `1.0.0`

### Schema

```json
{
  "schemaVersion": "1.0.0",
  "tool": {
    "name": "behave-lint",
    "version": "0.9.0"
  },
  "timestamp": "2024-01-15T10:30:00+00:00",
  "diagnostics": [
    {
      "rule_id": "BC001",
      "severity": "error",
      "message": "Duplicate scenario name 'Login'",
      "file_path": "features/login.feature",
      "line": 15,
      "category": "correctness",
      "column": 3,
      "end_line": 20,
      "end_column": 1,
      "suggestion": "Rename one of the scenarios.",
      "doc_url": "https://github.com/MathiasPaulenko/behave-lint/blob/main/docs/rules/correctness.md"
    }
  ],
  "summary": {
    "total_files": 5,
    "files_with_issues": 2,
    "total_diagnostics": 3,
    "error_count": 1,
    "warning_count": 1,
    "info_count": 1,
    "rules_executed": 31,
    "duration_ms": 42.5,
    "cache_hits": 3,
    "cache_misses": 2
  },
  "exit_code": 1
}
```

### Diagnostic fields

| Field | Type | Always present | Description |
|-------|------|----------------|-------------|
| `rule_id` | str | Yes | Rule identifier (e.g., `BC001`). |
| `severity` | str | Yes | `error`, `warning`, `info`. |
| `message` | str | Yes | Human-readable description. |
| `file_path` | str | Yes | Path to the `.feature` file. |
| `line` | int | Yes | 1-based line number. |
| `category` | str | Yes | Rule category. |
| `column` | int | No | 1-based column number. |
| `end_line` | int | No | End line for multi-line issues. |
| `end_column` | int | No | End column for multi-line issues. |
| `suggestion` | str | No | Fix suggestion. |
| `doc_url` | str | No | URL to rule documentation. |

### Summary fields

| Field | Type | Description |
|-------|------|-------------|
| `total_files` | int | Number of files analyzed. |
| `files_with_issues` | int | Files with at least one diagnostic. |
| `total_diagnostics` | int | Total diagnostics found. |
| `error_count` | int | Diagnostics with ERROR severity. |
| `warning_count` | int | Diagnostics with WARNING severity. |
| `info_count` | int | Diagnostics with INFO severity. |
| `rules_executed` | int | Number of rules that ran. |
| `duration_ms` | float | Execution time in milliseconds. |
| `cache_hits` | int | Cache hits. |
| `cache_misses` | int | Cache misses. |

## SARIF

SARIF v2.1.0 format for GitHub Code Scanning integration.

```bash
behave-lint features/ --sarif
behave-lint features/ --sarif --output-file behave-lint.sarif
```

**File output:** Supported.

**SARIF version:** `2.1.0`

**Schema:** `https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/Schemata/sarif-schema-2.1.0.json`

### Severity mapping

| behave-lint | SARIF level |
|-------------|-------------|
| ERROR | `error` |
| WARNING | `warning` |
| INFO | `note` |
| OFF | `none` |

### Structure

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "behave-lint",
          "version": "0.9.0",
          "informationUri": "https://github.com/MathiasPaulenko/behave-lint",
          "rules": [...]
        }
      },
      "results": [...]
    }
  ]
}
```

Each result includes `ruleId`, `level`, `message`, `locations` with
`physicalLocation` (artifact URI + region), and optional `fixes` with
the suggestion text.

## Markdown

Markdown report for GitHub Actions summaries and PR comments.

```bash
behave-lint features/ --output markdown --output-file report.md
```

**File output:** Supported.

**Features:**

- Summary table with counts and timing
- Diagnostics table with file, line, rule, severity, message
- Severity emojis: ❌ (error), ⚠️ (warning), ℹ️ (info)

## GitHub Actions

Inline PR annotations using GitHub Actions workflow commands.

```bash
behave-lint features/ --output github
```

**File output:** Not supported (always stdout).

**Commands:**

| Severity | Command |
|----------|---------|
| ERROR | `::error` |
| WARNING | `::warning` |
| INFO | `::notice` |

### Example output

```
::error file=features/login.feature,line=15::BC001: Duplicate scenario name 'Login'
::warning file=features/login.feature,line=20::BS001: Tag '@SmokeTest' should be lowercase
::notice::behave-lint found 2 diagnostics (1 error, 1 warning, 0 info) in 1 files
```

GitHub Actions renders these as inline annotations in the PR review
interface.
