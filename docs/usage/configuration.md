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
| `group` | list[str] or str | `[]` | Rule groups to enable (additive to `select`). See [Groups](groups.md). |
| `exclude` | list[str] | `[]` | Paths to exclude from linting (globs or directory prefixes). |

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
| `paths` | list[str] | `["features/"]` | Default paths to lint when no positional arguments are given. |
| `step-definitions` | str | `null` | Directory (or file) of Python step definitions. When set, BD001 flags steps with no matching definition and BD002 flags steps matching multiple definitions. Patterns are extracted via `ast` parsing — modules are never imported or executed. |

### Cache

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `cache` | bool | `true` | Enable caching. |
| `cache-dir` | str | `".behave-lint-cache"` | Cache directory. |

### Plugins

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `plugins` | dict | `{}` | Plugin enable/disable map, keyed by entry point name. |

```toml
[tool.behave-lint]
plugins = { "deprecated-plugin" = false }

# Enable only "my-plugin", disable everything else:
plugins = { "*" = false, "my-plugin" = true }
```

### Extends

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `extends` | str | `null` | Path to a parent config file to extend (relative to the file that declares it). The parent may be another `pyproject.toml` (its `[tool.behave-lint]` section is used) or a plain TOML file whose top-level keys are the config. Parent values act as defaults: the local file wins per key, and chains are supported. Cyclic or missing parents are configuration errors. |

```toml
# pyproject.toml
[tool.behave-lint]
extends = "../shared-lint.toml"
```

## Environment variables

All environment variables use the `BEHAVE_LINT_` prefix:

| Variable | Maps to | Type | Description |
|----------|---------|------|-------------|
| `BEHAVE_LINT_OUTPUT` | `output` | str | Output format. |
| `BEHAVE_LINT_OUTPUT_FILE` | `output_file` | str | Output file path. |
| `BEHAVE_LINT_NO_CACHE` | `cache` | bool (inverted) | Set to `1`/`true`/`yes` to disable cache. |
| `BEHAVE_LINT_CACHE_DIR` | `cache_dir` | str | Cache directory. |
| `BEHAVE_LINT_FAIL_ON` | `fail_on` | str | Fail-on severity level. |
| `BEHAVE_LINT_PROFILE` | `profile` | str | Built-in profile name. |
| `BEHAVE_LINT_GROUP` | `group` | str | Comma-separated rule groups. |
| `BEHAVE_LINT_CONFIG` | — | str | Path to the configuration file (used when `--config` is absent). |
| `BEHAVE_LINT_TRACE` | — | bool | Set to `1`/`true`/`yes` for debug logging. |

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
| `max-warnings` | `max_warnings` |
| `severity` | `severity_overrides` |
| `rules` | `rule_params` |

Parameter keys inside `[tool.behave-lint.rules.<RULE>]` tables may be
written in kebab-case (`max-steps`) or snake_case (`max_steps`) — both
are normalized to snake_case before reaching the rules.

## CLI overrides

All configuration options can be overridden via CLI flags. CLI flags
take precedence over the configuration file and environment variables.
See the [CLI Reference](cli-reference.md) for details.
