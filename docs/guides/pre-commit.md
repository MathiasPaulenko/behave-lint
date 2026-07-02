# Pre-commit Hook

Use `behave-lint` as a [pre-commit](https://pre-commit.com/) hook to
catch issues before they reach your repository.

## Configuration

Add this to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/MathiasPaulenko/behave-lint
    rev: v0.1.0
    hooks:
      - id: behave-lint
        args: ["features/"]
```

## With auto-fix

Apply safe fixes automatically on commit:

```yaml
repos:
  - repo: https://github.com/MathiasPaulenko/behave-lint
    rev: v0.1.0
    hooks:
      - id: behave-lint
        args: ["--fix", "features/"]
```

## Selecting specific rules

```yaml
repos:
  - repo: https://github.com/MathiasPaulenko/behave-lint
    rev: v0.1.0
    hooks:
      - id: behave-lint
        args: ["--select", "BC001,BC004,BS001", "features/"]
```

## Installation

```bash
pip install pre-commit
pre-commit install
```

Now `behave-lint` runs automatically on every commit.
