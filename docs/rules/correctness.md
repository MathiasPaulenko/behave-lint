# Correctness Rules (BC001–BC006)

Rules that detect definitively wrong structures causing runtime errors
or test failures.

Default severity: **ERROR**

---

## BC001: duplicate-scenario-names

Detects scenarios (including scenario outlines) that share the same name
within a single feature file. Duplicate names cause ambiguity in test
execution and reporting.

**Tags:** `scenarios`, `naming`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
    Feature: Login

      Scenario: Successful login
        Given a user

      Scenario: Successful login
        Given an admin
    ```

    **After:**

    ```gherkin
    Feature: Login

      Scenario: Successful user login
        Given a user

      Scenario: Successful admin login
        Given an admin
    ```

---

## BC002: empty-feature

Detects feature files that contain no scenarios or scenario outlines.
An empty feature file may indicate an incomplete or abandoned feature.

**Tags:** `feature`, `completeness`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
    Feature: User Profile
    ```

    **After:**

    ```gherkin
    Feature: User Profile

      Scenario: View profile
        Given a logged-in user
        When I navigate to the profile page
        Then I see my profile information
    ```

---

## BC003: scenario-outline-without-examples

Detects Scenario Outlines that lack at least one Examples table. A
Scenario Outline without Examples cannot execute.

**Tags:** `scenario-outline`, `examples`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
    Feature: Login

      Scenario Outline: Successful login
        Given a user with username <username>
        When I log in
        Then I see the dashboard
    ```

    **After:**

    ```gherkin
    Feature: Login

      Scenario Outline: Successful login
        Given a user with username <username>
        When I log in
        Then I see the dashboard

        Examples:
          | username |
          | alice    |
          | bob      |
    ```

---

## BC004: invalid-tag-syntax

Detects tags that do not follow the valid syntax: `@` followed by
alphanumeric characters and underscores.

**Tags:** `tags`, `syntax`

**Since:** 0.5.0

**Auto-fix:** Safe — replaces invalid characters with `_`.

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
    @smoke-test
    Feature: Login
    ```

    **After:**

    ```gherkin
    @smoke_test
    Feature: Login
    ```

---

## BC005: duplicate-feature-names

Detects feature files that share the same feature name. Duplicate
feature names cause confusion in test reports.

**Tags:** `feature`, `naming`, `cross-file`

**Scope:** Cross-file

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before** (`features/login.feature`):

    ```gherkin
    Feature: Authentication
    ```

    **Before** (`features/signup.feature`):

    ```gherkin
    Feature: Authentication
    ```

    **After** (`features/login.feature`):

    ```gherkin
    Feature: User Login
    ```

    **After** (`features/signup.feature`):

    ```gherkin
    Feature: User Registration
    ```

---

## BC006: invalid-example-table

Detects Examples tables with empty headers, no data rows, or mismatched
column counts between headers and data rows.

**Tags:** `examples`, `table`, `syntax`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
      Scenario Outline: Login
        Given a user with <username> and <password>

        Examples:
          | username | password |
          | alice    |
          | bob      | secret   | extra |
    ```

    **After:**

    ```gherkin
      Scenario Outline: Login
        Given a user with <username> and <password>

        Examples:
          | username | password |
          | alice    | pass123  |
          | bob      | secret   |
    ```
