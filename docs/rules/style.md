# Style Rules (BS001–BS008)

Rules that enforce style and convention preferences.

Default severity: **WARNING**

---

## BS001: tag-casing

Detects tags that do not follow the lowercase `snake_case` convention
(e.g., `@smoke_test`). Mixed-case or kebab-case tags are flagged.

**Tags:** `tags`, `naming`, `convention`

**Since:** 0.5.0

**Auto-fix:** Safe — converts tags to lowercase `snake_case`
(camelCase and kebab-case → snake_case).

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
    @SmokeTest
    Feature: Login
    ```

    **After:**

    ```gherkin
    @smoke_test
    Feature: Login
    ```

---

## BS002: keyword-ordering

Detects scenarios where steps do not follow the Given-When-Then ordering
convention. Steps using "And" or "But" inherit the preceding keyword's
position.

**Tags:** `steps`, `keywords`, `ordering`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
      Scenario: Login
        When I click the login button
        Given a user
        Then I see the dashboard
    ```

    **After:**

    ```gherkin
      Scenario: Login
        Given a user
        When I click the login button
        Then I see the dashboard
    ```

---

## BS003: step-phrasing

Detects steps that start with "I " (first-person phrasing). Third-person
phrasing (e.g., "the user clicks") is preferred for readability and
reusability.

**Tags:** `steps`, `phrasing`, `readability`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
      Scenario: Login
        Given I am a registered user
        When I click the login button
        Then I see the dashboard
    ```

    **After:**

    ```gherkin
      Scenario: Login
        Given a registered user
        When the user clicks the login button
        Then the dashboard is displayed
    ```

---

## BS004: background-name

Detects Background sections that lack a descriptive name. A named
background improves readability and helps team members understand the
common setup.

**Tags:** `background`, `naming`, `readability`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
    Feature: Login

      Background:
        Given a registered user
    ```

    **After:**

    ```gherkin
    Feature: Login

      Background: Authenticated user
        Given a registered user
    ```

---

## BS005: feature-description-formatting

Detects features that lack a description. A description explains the
feature's purpose and provides context for the scenarios below.

**Tags:** `feature`, `description`, `documentation`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
    Feature: Login

      Scenario: Successful login
        ...
    ```

    **After:**

    ```gherkin
    Feature: Login

      As a registered user
      I want to log in to my account
      So that I can access my dashboard

      Scenario: Successful login
        ...
    ```

---

## BS006: step-keyword-casing

Detects step keywords that are not properly capitalized. Gherkin
keywords (Given, When, Then, And, But) should start with an uppercase
letter.

**Auto-fixable:** Yes — capitalizes the first letter of step keywords.

**Tags:** `steps`, `keywords`, `casing`

**Since:** 1.2.0

---

## BS007: trailing-whitespace

Detects lines in feature files that have trailing whitespace (spaces
or tabs at the end of the line). Trailing whitespace causes unnecessary
diff noise.

**Auto-fixable:** Yes — removes trailing whitespace from each line.

**Tags:** `whitespace`, `formatting`

**Since:** 1.2.0

---

## BS008: tab-indentation

Detects lines that use tab characters for indentation. Spaces are the
standard indentation for Gherkin feature files.

**Auto-fixable:** Yes — replaces tabs with spaces (2 per level).

**Tags:** `indentation`, `tabs`, `formatting`

**Since:** 1.2.0
