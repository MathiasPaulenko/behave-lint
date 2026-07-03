# Incremental Cache

behave-lint supports incremental caching to speed up repeated lint runs.
When enabled, only files that have changed since the last run are
re-linted. Unchanged files reuse cached diagnostics.

## How It Works

1. On each run, behave-lint computes a SHA-256 hash of every `.feature`
   file's content.
2. If the hash matches a previous run **and** the configuration hasn't
   changed, the cached diagnostics are reused — rule execution is
   skipped entirely for that file.
3. If the hash doesn't match (file modified) or the config changed
   (different rules, severities, etc.), the file is re-linted and the
   cache is updated.

The cache is stored as a JSON file in the cache directory
(`.behave-lint-cache/` by default).

## Configuration

### CLI Flags

```bash
# Enable cache (default when not using --fix)
behave-lint features/

# Disable cache for this run
behave-lint --no-cache features/

# Clear cache before running
behave-lint --clear-cache features/
```

### Configuration File

```toml
[tool.behave_lint]
cache = true
cache_dir = ".behave-lint-cache"
```

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `BEHAVE_LINT_NO_CACHE` | `0` | Set to `1` to disable cache. |
| `BEHAVE_LINT_CACHE_DIR` | `.behave-lint-cache` | Cache directory path. |

## Cache Invalidation

The cache is automatically invalidated when:

- **File content changes** — any modification to a `.feature` file
  produces a different hash.
- **Configuration changes** — the cache stores a hash of relevant config
  fields (select, ignore, profile, group, severity overrides, rule
  params, fail_on). Changing any of these invalidates all entries.
- **Cache version mismatch** — if the cache format changes between
  releases, old caches are ignored.

## Limitations

- **Auto-fix mode** — the cache is automatically disabled when using
  `--fix` or `--unsafe-fixes`, since fixes require rule execution to
  collect `FixEdit` objects.
- **Cross-file rules** — cross-file rules (e.g., consistency rules) are
  not cached individually. They run on every uncached run.
- **Cache size** — the cache grows with the number of unique file
  versions. Use `--clear-cache` periodically or add the cache directory
  to `.gitignore`.

## Statistics

Cache hits and misses are reported in the summary when using
`--statistics`:

```
Found 13 diagnostics (6 warning, 7 info) in 10 files in 0.02s.
Cache: 8 hits, 2 misses.
```
