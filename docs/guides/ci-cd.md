# CI/CD Integration

How to integrate `behave-lint` into your CI/CD pipeline.

## GitHub Actions

### Basic usage

```yaml
name: Lint Feature Files
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install behave-lint
      - run: behave-lint features/
```

### With SARIF annotations

Upload SARIF results to GitHub Code Scanning:

```yaml
name: Lint Feature Files
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install behave-lint
      - run: behave-lint features/ --output sarif --output-file behave-lint.sarif
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: behave-lint.sarif
```

### With inline annotations

Use the `github` output format for inline PR annotations:

```yaml
      - run: behave-lint features/ --output github
```

## GitLab CI

```yaml
behave-lint:
  image: python:3.12
  script:
    - pip install behave-lint
    - behave-lint features/ --output json --output-file behave-lint-report.json
  artifacts:
    reports:
      junit: behave-lint-report.json
```

## Pre-merge gate

Fail the pipeline if any errors are found:

```yaml
      - run: behave-lint features/ --fail-on error
```

## Caching

Cache the behave-lint cache directory between runs:

```yaml
      - uses: actions/cache@v4
        with:
          path: .behave-lint-cache
          key: behave-lint-${{ hashFiles('features/**/*.feature') }}
```
