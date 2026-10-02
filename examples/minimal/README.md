# Minimal Example

A minimal Behave project demonstrating basic `behave-lint` usage.

## Structure

```text
minimal/
  features/
    login.feature
  pyproject.toml
```

## Run

```bash
cd minimal
behave-lint
```

No positional argument is needed: `paths` comes from `pyproject.toml`.
