# Security Rules (BSEC001–BSEC003)

Rules that detect security concerns and sensitive data exposure in Gherkin
feature files.

Default severity: **ERROR**

---

## BSEC001: hardcoded-secrets

Detects steps that contain literal passwords, API keys, tokens, or other
sensitive values. Hardcoded secrets are a security risk and should be
replaced with placeholders or environment variables.

The rule looks for a **sensitive keyword** (e.g., `password`, `secret`,
`api_key`, `access_token`, `private_key`, `credit_card`, `ssn`) near a
**hardcoded value** (a quoted string of 8+ characters, a hex string of
32+ characters, or known key prefixes like `sk_`, `ghp_`, `AKIA`).

**Tags:** `security`, `secrets`, `credentials`

**Since:** 2.4.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
    Feature: Login

      Scenario: Login with credentials
        Given the user enters password = "hunter2pass"
    ```

    **After:**

    ```gherkin
    Feature: Login

      Scenario: Login with credentials
        Given the user enters password = "<password>"
    ```

### How it works

1. Iterates over all scenarios and their steps.
2. For each step, checks if the step text contains a sensitive keyword
   (e.g., `password`, `api_key`, `secret`) **and** a hardcoded value
   (a quoted string matching the secret pattern).
3. Placeholders like `<password>` are **not** flagged — only literal
   values that look like real secrets.

### Configuration

This rule has no configurable parameters.

---

## BSEC002: url-with-credentials

Detects steps that contain URLs with embedded credentials
(e.g., `https://user:password@host`). Credentials in URLs are visible
in logs, browser history, and version control.

**Tags:** `security`, `url`, `credentials`

**Since:** 2.4.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
    Feature: API test

      Scenario: Fetch data
        Given the API endpoint is "https://admin:pass@api.example.com"
    ```

    **After:**

    ```gherkin
    Feature: API test

      Scenario: Fetch data
        Given the API endpoint is "<api_url>"
    ```

### How it works

1. Iterates over all scenarios and their steps.
2. Searches each step text for a URL pattern of the form
   `https://user:password@host` using a regex.
3. Reports a diagnostic with the matching step text and a suggestion
   to use a placeholder or environment variable.

### Configuration

This rule has no configurable parameters.

---

## BSEC003: sensitive-tags

Detects tags like `@production`, `@live`, `@real-data`, `@sensitive`,
or `@prod` that suggest the scenario may interact with real systems
or data. These tags should be reviewed to prevent accidental execution
against production environments.

**Tags:** `security`, `tags`, `production`

**Since:** 2.4.0

**Default severity:** WARNING

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
    @production
    Feature: Data migration

      Scenario: Migrate records
        Given the database is ready
    ```

    **After:**

    ```gherkin
    @staging
    Feature: Data migration

      Scenario: Migrate records
        Given the database is ready
    ```

### How it works

1. Checks both feature-level tags and scenario-level tags.
2. Compares each tag name (without `@`) against the sensitive tags set:
   `production`, `live`, `real-data`, `sensitive`, `prod`.
3. Reports a WARNING diagnostic for each matching tag, suggesting
   `@staging` or `@test` as alternatives.

### Configuration

This rule has no configurable parameters.
