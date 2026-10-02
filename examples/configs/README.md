# Example Configs

Sample `[tool.behave-lint]` configurations. Copy the section you need
into your project's `pyproject.toml`.

| File | Purpose |
|------|---------|
| [minimal.toml](minimal.toml) | Empty section — all defaults. |
| [strict.toml](strict.toml) | Strict profile, error-only failure, warning budget. |
| [ci.toml](ci.toml) | CI pipeline: JSON report, excludes, warnings. |
