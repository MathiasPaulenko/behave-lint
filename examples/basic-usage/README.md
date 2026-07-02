# Basic Usage Example

A minimal project showing how to configure and run `behave-lint`.

## Structure

```
examples/basic-usage/
├── pyproject.toml      # Configuration
└── features/
    ├── login.feature   # Clean feature file
    └── cart.feature    # Feature with Scenario Outlines
```

## Run

```bash
# From the behave-lint project root
python -m behave_lint examples/basic-usage/features/ --config examples/basic-usage/pyproject.toml

# Or cd into the example and run from there
cd examples/basic-usage
behave-lint features/
```

## What this demonstrates

- A `[tool.behave-lint]` section in `pyproject.toml`
- Rule selection with `select` and `ignore`
- Per-rule severity overrides with `severity`
- Feature files with tags, Scenario Outlines, and Examples
