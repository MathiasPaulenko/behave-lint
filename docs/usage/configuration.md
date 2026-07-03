# Configuration

`behave-lint` reads configuration from `pyproject.toml` under the
`[tool.behave-lint]` section. Configuration is merged from multiple
sources with well-defined precedence.

## Configuration sources

Configuration is resolved in order of increasing precedence (higher
overrides lower):

1. **Built-in defaults** (lowest)
2. **Profile** (if specified via `--profile`, `profile` in config, or `BEHAVE_LINT_PROFILE`)
3. **`pyproject.toml`** — `[tool.behave-lint]` section
4. **Environment variables** — `BEHAVE_LINT_*` prefix
5. **CLI flags** (highest)

### Merge rules

- **Scalars** (str, bool, int): highest precedence wins (replaces).
- **Lists** (`select`, `ignore`, `paths`, `exclude`): highest precedence
  wins (replaces, no concatenation).
- **Dicts** (`severity`, `plugins`, `rules`): merged (highest precedence
  keys override matching lower keys).

## Configuration file

`behave-lint` searches for `pyproject.toml` starting from the current
directory and walking up to the filesystem root. The first
`pyproject.toml` containing a `[tool.behave-lint]` section is used.

```toml
[tool.behave-lint]
profile = "recommended"
select = ["BC001", "BC004", "BS001"]
ignore = ["BP001", "BP002"]
fail-on = "warning"
output = "console"
paths = ["features/"]
exclude = ["features/legacy/"]
```

Use `--config` to specify an explicit path:

```bash
behave-lint --config /path/to/pyproject.toml features/
```

## Options

### Rule selection

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `select` | list[str] | `[]` (all) | Rule IDs to enable. Empty means all defaults. |
| `ignore` | list[str] | `[]` | Rule IDs to disable. |
| `profile` | str | `"none"` | Built-in profile: `recommended`, `strict`, `minimal`. See [Profiles](profiles.md). |
| `exclude` | list[str] | `[]` | Paths to exclude from linting. |

### Severity

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `fail-on` | str | `"warning"` | Minimum severity for non-zero exit: `error`, `warning`, `info`. |
| `severity` | dict | `{}` | Per-rule severity overrides. |
| `max-warnings` | int | `-1` | Max warnings before non-zero exit (`-1` = no limit). |

#### Severity overrides

The TOML key is `severity` (not `severity-overrides`):

```toml
[tool.behave-lint.severity]
BC001 = "warning"
BX001 = "error"
BD003 = "info"
```

Valid severity values: `error`, `warning`, `info`, `off`.

### Rule parameters

Some rules are configurable with parameters. The TOML key is `rules`
(not `rule-params`):

```toml
[tool.behave-lint.rules]
BX001 = { max-steps = 8 }
BX002 = { max-scenarios = 5 }
BX003 = { max-example-rows = 15 }
BX004 = { max-step-length = 100 }
BX005 = { max-tags = 5 }
BP003 = { min-length = 10 }
BP004 = { min-length = 10 }
```

| Rule | Parameter | Default | Description |
|------|-----------|---------|-------------|
| BX001 | `max-steps` | 10 | Maximum steps per scenario. |
| BX002 | `max-scenarios` | 10 | Maximum scenarios per feature. |
| BX003 | `max-example-rows` | 20 | Maximum rows per Examples table. |
| BX004 | `max-step-length` | 120 | Maximum step text length (characters). |
| BX005 | `max-tags` | 5 | Maximum tags per element. |
| BP003 | `min-length` | 10 | Minimum scenario name length (characters). |
| BP004 | `min-length` | 10 | Minimum feature name length (characters). |

### Output

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output` | str | `"console"` | Output format: `console`, `json`, `markdown`, `sarif`, `github`. |
| `output-file` | str | `null` | Write output to file instead of stdout. |

### Paths

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `paths` | list[str] | `["features/"]` | Default paths to lint. |
| `step-definitions` | str | `null` | Step definitions directory. |

### Cache

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `cache` | bool | `true` | Enable caching. |
| `cache-dir` | str | `".behave-lint-cache"` | Cache directory. |

### Plugins

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `plugins` | dict | `{}` | Plugin enable/disable map. |

```toml
[tool.behave-lint]
plugins = { "my-plugin" = true, "deprecated-plugin" = false }
```

### Extends

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `extends` | str | `null` | Path to another config file to extend. |

## Environment variables

All environment variables use the `BEHAVE_LINT_` prefix:

| Variable | Maps to | Type | Description |
|----------|---------|------|-------------|
| `BEHAVE_LINT_OUTPUT` | `output` | str | Output format. |
| `BEHAVE_LINT_OUTPUT_FILE` | `output_file` | str | Output file path. |
| `BEHAVE_LINT_NO_CACHE` | `cache` | bool (inverted) | Set to `1`/`true`/`yes` to disable cache. |
| `BEHAVE_LINT_CACHE_DIR` | `cache_dir` | str | Cache directory. |
| `BEHAVE_LINT_FAIL_ON` | `fail_on` | str | Fail-on severity level. |

Example:

```bash
BEHAVE_LINT_OUTPUT=json BEHAVE_LINT_FAIL_ON=error behave-lint features/
```

## Key aliases

Some keys accept both kebab-case and snake_case in TOML:

| Kebab-case | Snake_case |
|------------|------------|
| `output-file` | `output_file` |
| `step-definitions` | `step_definitions` |
| `cache-dir` | `cache_dir` |
| `fail-on` | `fail_on` |

## CLI overrides

All configuration options can be overridden via CLI flags. CLI flags
take precedence over the configuration file and environment variables.
See the [CLI Reference](cli-reference.md) for details.
