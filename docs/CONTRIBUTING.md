# Contributing to behave-lint

Thank you for your interest in contributing to behave-lint! This
document describes how to set up your development environment and how
to contribute effectively.

## Development Environment

### Prerequisites

- Python 3.11, 3.12, or 3.13
- [uv](https://docs.astral.sh/uv/) package manager
- Git

### Setup

```bash
git clone https://github.com/MathiasPaulenko/behave-lint.git
cd behave-lint
uv sync
uv run pre-commit install
```

### Running Tests

```bash
# All tests
uv run pytest

# Unit tests only
uv run pytest -m unit

# Integration tests only
uv run pytest -m integration

# With coverage
uv run pytest --cov=src

# Parallel execution
uv run pytest -n auto
```

### Code Quality

```bash
# Format
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/
```

## How to Contribute

### Reporting Bugs

Open a [bug report issue](https://github.com/MathiasPaulenko/behave-lint/issues/new?template=bug_report.md).
Include:

- behave-lint version (`behave-lint --version`)
- Python version
- Operating system
- Minimal reproduction case
- Expected behavior vs. actual behavior

### Requesting Features

Open a [feature request issue](https://github.com/MathiasPaulenko/behave-lint/issues/new?template=feature_request.md).
Describe the use case and the desired behavior.

### Pull Requests

1. Fork the repository and create a branch from `main`.
2. Make your changes following the guidelines below.
3. Ensure all checks pass: `ruff check`, `ruff format`, `mypy`,
   `pytest`.
4. Update the changelog if your change is user-visible.
5. Open a pull request with a clear description.

## Coding Standards

Follow the development guidelines in the project for all code
contributions. Key points:

- Type hints are mandatory on all public functions.
- Follow PEP 8 naming conventions.
- One responsibility per module.
- Respect the architectural layering rules.
- Write tests for all new functionality.
- Keep functions small and focused.

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`,
`perf`, `ci`, `build`.

## Branch Naming

- Feature: `feat/<description>`
- Bug fix: `fix/<description>`
- Documentation: `docs/<description>`
- Refactor: `refactor/<description>`

## Code Review

All PRs require at least one maintainer approval. See the pull request
template in the repository for the review checklist.

## License

By contributing, you agree that your contributions will be licensed
under the [MIT License](LICENSE).
