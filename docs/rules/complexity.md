# Complexity Rules (BX001–BX006)

Rules that detect overly complex features and scenarios.

Default severity: **WARNING**

All complexity rules are **configurable** — see
[Configuration](../usage/configuration.md#rule-parameters) for
parameters.

---

## BX001: too-many-steps

Detects scenarios that exceed the maximum number of steps. Complex
scenarios are hard to understand and maintain.

**Tags:** `scenario`, `steps`, `complexity`

**Configurable:** `max-steps` (default: `10`)

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before** (12 steps, exceeds `max-steps = 10`):

    ```gherkin
      Scenario: Checkout
        Given a user
        And a product in the cart
        When I go to checkout
        And I enter shipping address
        And I select shipping method
        And I enter payment details
        And I review the order
        And I confirm the order
        Then the order is placed
        And I see a confirmation
        And I receive an email
        And the cart is empty
    ```

    **After:** Split into two scenarios (e.g., "Fill checkout form" and
    "Confirm order").

    Or increase the threshold:

    ```toml
    [tool.behave-lint.rules]
    BX001 = { max-steps = 15 }
    ```

---

## BX002: too-many-scenarios

Detects features that exceed the maximum number of scenarios. Large
features should be split into smaller, focused features.

**Tags:** `feature`, `scenarios`, `complexity`

**Configurable:** `max-scenarios` (default: `10`)

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:** A single feature file with 15 scenarios covering login,
    registration, password reset, and profile management.

    **After:** Split into separate feature files:
    `features/login.feature`, `features/registration.feature`,
    `features/password-reset.feature`, `features/profile.feature`.

---

## BX003: too-many-example-rows

Detects example tables that exceed the maximum number of data rows.
Large example tables are hard to maintain and slow down test execution.

**Tags:** `examples`, `table`, `complexity`

**Configurable:** `max-example-rows` (default: `20`)

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:** An Examples table with 50 rows of test data.

    **After:** Split into multiple named Examples blocks:

    ```gherkin
      Examples: Valid logins
        | username | password |
        | alice    | pass1    |
        ...

      Examples: Invalid logins
        | username | password |
        | alice    | wrong    |
        ...
    ```

---

## BX004: long-step-text

Detects steps with text exceeding the maximum length. Long step text
reduces readability.

**Tags:** `steps`, `readability`, `complexity`

**Configurable:** `max-step-length` (default: `120`)

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
      Given a user with username "alice" and password "secret123" and email "alice@example.com" and role "admin" and department "engineering"
    ```

    **After:**

    ```gherkin
      Given a registered admin user
    ```

    Or use a data table:

    ```gherkin
      Given a user with the following details:
        | username | alice         |
        | password | secret123     |
        | email    | alice@x.com   |
        | role     | admin         |
        | dept     | engineering   |
    ```

---

## BX005: too-many-tags

Detects features or scenarios that exceed the maximum number of tags.
Too many tags reduce clarity.

**Tags:** `tags`, `complexity`

**Configurable:** `max-tags` (default: `5`)

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
    @smoke @regression @login @auth @slow @nightly @critical
    Feature: Login
    ```

    **After:**

    ```gherkin
    @smoke @login @critical
    Feature: Login
    ```

---

## BX006: feature-file-too-long

Detects feature files that exceed the maximum number of lines. Long
files are hard to navigate and should be split into smaller, focused
feature files.

**Configurable:** `max_file_lines` (default: 300)

**Tags:** `feature`, `file`, `complexity`

**Since:** 1.2.0
