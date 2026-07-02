# CI/CD Example

A project showing how to integrate `behave-lint` into GitHub Actions with
SARIF upload for GitHub Code Scanning.

## Structure

```
examples/ci-cd/
├── README.md
├── pyproject.toml                    # Configuration
├── features/
│   ├── checkout.feature
│   └── registration.feature
└── .github/workflows/
    └── lint.yml                      # GitHub Actions workflow
```

## Run locally

```bash
cd examples/ci-cd
behave-lint features/
```

## GitHub Actions

The workflow in `.github/workflows/lint.yml`:

1. Runs `behave-lint` with console output (fails on warnings)
2. Generates SARIF output for GitHub Code Scanning
3. Uploads SARIF results using `github/codeql-action/upload-sarif`

Copy the workflow to your own repository's `.github/workflows/` directory.

## What this demonstrates

- GitHub Actions integration with `behave-lint`
- SARIF output for GitHub Code Scanning
- `fail-on` to control exit codes
- `exclude` to skip work-in-progress features
