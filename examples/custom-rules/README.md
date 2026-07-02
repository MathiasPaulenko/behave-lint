# Custom Rules Example

A complete example showing how to write, package, and register a custom
rule for `behave-lint`.

## Structure

```
examples/custom-rules/
├── README.md
├── pyproject.toml                          # Plugin package definition
├── src/
│   └── behave_lint_ex001/
│       └── __init__.py                     # Custom rule implementation
└── features/
    ├── pyproject.toml                      # Config that selects EX001
    └── demo.feature                        # Feature with violations
```

## Install the plugin

```bash
cd examples/custom-rules
pip install -e .
```

## Run

```bash
# Run with the custom rule selected
cd examples/custom-rules/features
behave-lint . --config pyproject.toml
```

Expected output: a warning for `EX001` on the "Given another user" step
in the first scenario.

## What this demonstrates

- Subclassing `Rule` and implementing `check()`
- Defining `RuleMetadata` with all required fields
- Registering via `[project.entry-points."behave_lint.rules"]`
- Using `self.diagnostic()` to create diagnostics
- Selecting a custom rule via `select` in configuration
