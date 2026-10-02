# Enterprise Example

A multi-suite project layout showing a stricter `behave-lint`
configuration: a `legacy/` directory excluded from linting, a warning
budget (`max-warnings`), a per-rule severity override, and a tuned rule
parameter.

## Structure

```text
enterprise/
  pyproject.toml
  features/
    checkout.feature
    legacy/
      old.feature
```

## Run

```bash
cd enterprise
behave-lint --statistics
```

`features/legacy/old.feature` is skipped via `exclude`, and warnings do
not fail the build (`fail-on = "error"`), unless more than 50 warnings
accumulate (`max-warnings`).
