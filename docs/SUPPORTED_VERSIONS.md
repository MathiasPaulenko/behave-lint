# Supported Versions

## Python

| Version | Status | First Supported |
|---|---|---|
| 3.13 | Active | 0.1.0 |
| 3.12 | Active | 0.1.0 |
| 3.11 | Active (minimum) | 0.1.0 |
| 3.10 | Not supported | — |
| 3.9 | Not supported | — |

**Rationale:** Python 3.11 is the minimum version because it provides
`tomllib` (standard library TOML parser), exception groups, and
`TaskGroup`. This matches `behave-model`'s minimum version
requirement.

## behave-model

| Version | Status |
|---|---|
| 0.1.x – 0.x | Active (runtime dependency) |

**Rationale:** `behave-model` is the only runtime dependency. The
version range is pinned to a compatible major version.

## Operating Systems

| OS | Status |
|---|---|
| Linux | Active (CI tested) |
| macOS | Active (CI tested) |
| Windows | Active (CI tested) |

## Tooling

| Tool | Version | Purpose |
|---|---|---|
| Ruff | >= 0.6 | Formatter + linter |
| Mypy | >= 1.10 | Static type checker |
| Pytest | >= 8.0 | Test runner |
| hatchling | >= 1.21 | Build backend |
| uv | latest | Package manager |
| pre-commit | >= 3.7 | Pre-commit hooks |
