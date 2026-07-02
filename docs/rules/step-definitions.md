# Step Definition Rules (BD001–BD005)

Rules that detect potential step definition issues by analyzing step
text patterns.

Default severity: **WARNING**

---

## BD001: undefined-step-pattern

Detects steps that use placeholder syntax (`<value>`) outside of
Scenario Outline contexts, which likely indicates a missing or incorrect
step definition.

**Tags:** `steps`, `definitions`, `placeholders`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
      Scenario: User login
        Given a user with <username>
        When I click the login button
    ```

    **After:**

    ```gherkin
      Scenario Outline: User login
        Given a user with <username>
        When I click the login button

        Examples:
          | username |
          | alice    |
    ```

    Or, if not intended as an outline, remove the placeholders:

    ```gherkin
      Scenario: User login
        Given a user with username "alice"
        When I click the login button
    ```

---

## BD002: ambiguous-step-pattern

Detects steps with very generic text that could match multiple step
definitions, leading to ambiguous matches at runtime.

**Tags:** `steps`, `definitions`, `ambiguous`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
      Scenario: Test
        Given a thing
        When I do something
        Then it works
    ```

    **After:**

    ```gherkin
      Scenario: Test
        Given a registered user
        When I submit the login form
        Then I see the dashboard
    ```

---

## BD003: unused-step-definition

Detects step text that appears only once in the entire feature. While
not necessarily wrong, low reuse may indicate missing step definition
reuse.

**Severity:** INFO

**Tags:** `steps`, `definitions`, `reuse`

**Since:** 0.5.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
      Scenario: Login
        Given a user named Alice
        When I enter password "secret"
        Then I see the dashboard

      Scenario: Logout
        Given a user named Bob
        When I click the logout button
        Then I see the login page
    ```

    **After:**

    ```gherkin
      Scenario: Login
        Given a registered user
        When I submit the login form
        Then I see the dashboard

      Scenario: Logout
        Given a registered user
        When I click the logout button
        Then I see the login page
    ```

    Reusing "Given a registered user" across scenarios improves step
    definition reuse.

---

## BD004: step-parameter-convention

Detects steps that mix different parameter conventions (`{param}` vs
`<param>`) within the same scenario. Consistent parameter syntax
improves readability.

**Tags:** `steps`, `parameters`, `conventions`

**Since:** 0.5.0

**Auto-fix:** Safe — converts `{param}` to `<param>` when both
conventions are mixed in the same scenario.

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
      Scenario Outline: Test <value>
        Given a <value> with {count} items
    ```

    **After:**

    ```gherkin
      Scenario Outline: Test <value>
        Given a <value> with <count> items
    ```

---

## BD005: step-trailing-punctuation

Detects steps that end with punctuation marks like periods or commas.
Trailing punctuation can cause step matching failures.

**Tags:** `steps`, `punctuation`, `definitions`

**Since:** 0.5.0

**Auto-fix:** Safe — removes trailing punctuation from step text.

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
      Scenario: Login
        Given a user.
        When I click submit.
    ```

    **After:**

    ```gherkin
      Scenario: Login
        Given a user
        When I click submit
    ```
