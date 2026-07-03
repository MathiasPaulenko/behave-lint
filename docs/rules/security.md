# Security Rules

Rules that detect security concerns and sensitive data exposure in Gherkin
feature files.

**Default severity:** ERROR

| Rule | Name | Severity | Auto-fix |
|------|------|----------|----------|
| BSEC001 | [hardcoded-secrets](#bsec001-hardcoded-secrets) | ERROR | No |
| BSEC002 | [url-with-credentials](#bsec002-url-with-credentials) | ERROR | No |
| BSEC003 | [sensitive-tags](#bsec003-sensitive-tags) | WARNING | No |

## BSEC001: hardcoded-secrets

Detects steps that contain literal passwords, API keys, tokens, or other
sensitive values. Hardcoded secrets are a security risk and should be
replaced with placeholders or environment variables.

### Example

```gherkin
# Bad
Given the user enters password = "hunter2pass"

# Good
Given the user enters password = "<password>"
```

## BSEC002: url-with-credentials

Detects steps that contain URLs with embedded credentials
(e.g., `https://user:password@host`). Credentials in URLs are visible in
logs and version control.

### Example

```gherkin
# Bad
Given the url is "https://admin:secret@api.example.com"

# Good
Given the url is "<api_url>"
```

## BSEC003: sensitive-tags

Detects tags like `@production`, `@live`, `@real-data`, or `@sensitive`
that suggest the scenario may interact with real systems or data.

### Example

```gherkin
# Bad
@production
Feature: Data migration

# Good
@staging
Feature: Data migration
```
