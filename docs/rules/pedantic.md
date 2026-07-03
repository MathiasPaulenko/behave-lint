# Pedantic Rules (BP001–BP007)

Strict best-practice rules for teams that want thorough enforcement.

Default severity: **INFO**

---

## BP001: missing-scenario-tags

Detects scenarios that do not have any tags. Tags help filter and
categorize scenarios for targeted test execution.

**Tags:** `tags`, `scenarios`, `pedantic`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
      Scenario: User login
        Given a user
        When I click login
    ```

    **After:**

    ```gherkin
      @smoke
      Scenario: User login
        Given a user
        When I click login
    ```

---

## BP002: missing-background

Detects features that lack a Background section. Common setup steps
should be extracted into a Background to avoid duplication.

**Tags:** `background`, `pedantic`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
    Feature: Dashboard

      Scenario: View profile
        Given a logged-in user
        When I click profile
        Then I see my profile

      Scenario: View settings
        Given a logged-in user
        When I click settings
        Then I see my settings
    ```

    **After:**

    ```gherkin
    Feature: Dashboard

      Background: Authenticated user
        Given a logged-in user

      Scenario: View profile
        When I click profile
        Then I see my profile

      Scenario: View settings
        When I click settings
        Then I see my settings
    ```

---

## BP003: short-scenario-name

Detects scenarios with names shorter than the minimum length. Short
names are often vague and uninformative.

**Tags:** `naming`, `scenarios`, `pedantic`

**Configurable:** `min-length` (default: `10`)

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
      Scenario: Login
        ...
    ```

    **After:**

    ```gherkin
      Scenario: User logs in successfully
        ...
    ```

    Or lower the threshold:

    ```toml
    [tool.behave-lint.rules]
    BP003 = { min-length = 5 }
    ```

---

## BP004: short-feature-name

Detects features with names shorter than the minimum length. Short
names are often vague and uninformative.

**Tags:** `naming`, `feature`, `pedantic`

**Configurable:** `min-length` (default: `10`)

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
    Feature: Auth
    ```

    **After:**

    ```gherkin
    Feature: User Authentication
    ```

---

## BP005: missing-examples-name

Detects Examples sections that lack a descriptive name. Named examples
improve readability by grouping related data.

**Tags:** `examples`, `naming`, `pedantic`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
      Scenario Outline: Login
        Given a user with <username>

        Examples:
          | username |
          | alice    |
          | bob      |
    ```

    **After:**

    ```gherkin
      Scenario Outline: Login
        Given a user with <username>

        Examples: Valid users
          | username |
          | alice    |
          | bob      |
    ```

---

## BP006: missing-feature-description

Detects features that lack a description block. A description explains
the feature's purpose and improves readability for non-technical
stakeholders.

**Tags:** `feature`, `description`, `pedantic`

**Since:** 1.2.0

---

## BP007: scenario-without-assertion

Detects scenarios that do not contain at least one `Then` step. Without
an assertion, the scenario does not verify any expected outcome.

**Tags:** `scenarios`, `assertion`, `pedantic`

**Since:** 1.2.0
