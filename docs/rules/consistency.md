# Consistency Rules (BK001–BK005)

Rules that detect inconsistencies across scenarios within a feature.

---

## BK001: inconsistent-step-text

Detects steps that use different text for the same action. Consistent
step text improves readability and enables better step definition reuse.

**Severity:** WARNING

**Tags:** `steps`, `consistency`, `naming`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
      Scenario: Login
        Given a registered user
        When I click the login button

      Scenario: Admin login
        Given an admin user
        When I press the login button
    ```

    **After:**

    ```gherkin
      Scenario: Login
        Given a registered user
        When I click the login button

      Scenario: Admin login
        Given a registered admin user
        When I click the login button
    ```

---

## BK002: inconsistent-tag-usage

Detects scenarios that may be missing tags that similar scenarios have.
This is a heuristic rule based on scenario name similarity.

**Severity:** INFO

**Tags:** `tags`, `consistency`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
      @smoke
      Scenario: User can log in
        Given a user

      Scenario: User can log out
        Given a user
    ```

    **After:**

    ```gherkin
      @smoke
      Scenario: User can log in
        Given a user

      @smoke
      Scenario: User can log out
        Given a user
    ```

---

## BK003: inconsistent-naming-convention

Detects features where scenario names follow different conventions
(e.g., some start with "Given" and others don't). Consistent naming
improves readability.

**Severity:** WARNING

**Tags:** `naming`, `consistency`, `scenarios`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
      Scenario: Given a user is logged in
        ...

      Scenario: User views dashboard
        ...
    ```

    **After:**

    ```gherkin
      Scenario: User is logged in
        ...

      Scenario: User views dashboard
        ...
    ```

---

## BK004: inconsistent-scenario-length

Detects features where scenarios have very different numbers of steps.
Large disparities indicate inconsistent test granularity.

**Severity:** INFO

**Tags:** `scenarios`, `consistency`, `complexity`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
      Scenario: Quick check
        Given a user

      Scenario: Full flow
        Given a user
        When I navigate to settings
        And I click privacy
        And I select delete data
        And I confirm deletion
        Then my data is deleted
        And I see a confirmation
    ```

    **After:**

    Split the long scenario into smaller, focused scenarios with similar
    step counts.

---

## BK005: duplicate-step-text

Detects scenarios that contain the same step text multiple times. This
is usually a mistake or indicates a missing "And" continuation.

**Severity:** WARNING

**Tags:** `steps`, `duplicates`, `consistency`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
      Scenario: Add items
        Given a shopping cart
        When I add an item
        When I add an item
        Then the cart has two items
    ```

    **After:**

    ```gherkin
      Scenario: Add items
        Given a shopping cart
        When I add an item
        And I add another item
        Then the cart has two items
    ```
