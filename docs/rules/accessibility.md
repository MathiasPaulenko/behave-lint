# Accessibility Rules (BACC001–BACC003)

Rules that detect accessibility and inclusive design concerns in Gherkin
feature files, such as ableist language, missing accessibility test
coverage, and color-only information.

Default severity: **WARNING**

---

## BACC001: ableist-language

Detects ableist terms in step text and scenario names. Ableist language
reinforces stereotypes and should be replaced with person-first or
identity-first language.

The rule checks for the following terms and suggests inclusive
alternatives:

| Term | Suggested alternative |
|------|----------------------|
| `disabled` | `person with a disability` |
| `handicapped` | `person with a disability` |
| `crippled` | `person with a mobility impairment` |
| `mute` | `person with a speech impairment` |
| `deaf-mute` | `person who is deaf and non-speaking` |
| `wheelchair-bound` | `wheelchair user` |
| `confined to a wheelchair` | `wheelchair user` |
| `suffering from` | `living with` |
| `afflicted with` | `living with` |
| `victim of` | `person affected by` |
| `normal person` | `person without disabilities` |
| `able-bodied` | `person without disabilities` |

**Tags:** `accessibility`, `inclusive-language`, `ableism`

**Since:** 2.4.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
    Feature: User management

      Scenario: Register disabled user
        Given a disabled user
        When they register
    ```

    **After:**

    ```gherkin
    Feature: User management

      Scenario: Register user with a disability
        Given a user with a disability
        When they register
    ```

### How it works

1. Iterates over all scenarios.
2. Checks the scenario **name** for ableist terms.
3. Checks each **step text** for ableist terms.
4. Reports a diagnostic with the matched term and its inclusive
   alternative.

### Configuration

This rule has no configurable parameters.

---

## BACC002: missing-accessibility-scenario

Detects features with UI-related tags (`@ui`, `@frontend`, `@web`,
`@e2e`) that lack accessibility test scenarios (tagged
`@accessibility` or `@a11y`). Accessibility testing should be part
of UI feature coverage.

**Tags:** `accessibility`, `coverage`, `ui`

**Since:** 2.4.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
    @ui
    Feature: Login form

      Scenario: Successful login
        Given the user is on the login page
    ```

    **After:**

    ```gherkin
    @ui
    Feature: Login form

      Scenario: Successful login
        Given the user is on the login page

      @accessibility
      Scenario: Login form is keyboard accessible
        Given the user is on the login page
        Then the form can be completed with the keyboard
    ```

### How it works

1. Collects all tags from the feature and its scenarios.
2. Checks if any tag matches the UI tags set: `ui`, `frontend`, `web`,
   `e2e`.
3. Checks if any tag matches the accessibility tags set:
   `accessibility`, `a11y`.
4. If UI tags are present but no accessibility tags are found, reports
   a diagnostic on the feature suggesting to add an accessibility
   scenario.

### Configuration

This rule has no configurable parameters.

---

## BACC003: color-only-contrast

Detects steps that reference color alone to convey information (e.g.,
"the button is red"). Relying solely on color is inaccessible to users
with color vision deficiency. Tests should verify that information is
also conveyed through text, icons, patterns, or other non-color cues.

The rule checks for color words (`red`, `green`, `blue`, `yellow`,
`orange`, `purple`, `pink`, `black`, `white`, `gray`, `grey`, `brown`)
and non-color indicators (`text`, `label`, `icon`, `symbol`, `message`,
`error`, `warning`, `success`, `border`, `underline`, `pattern`,
`shape`). If a step contains a color word but no non-color indicator,
it is flagged.

**Tags:** `accessibility`, `color`, `contrast`

**Since:** 2.4.0

### Example

??? example "Before → After"

    **Before:**

    ```gherkin
    Feature: Status display

      Scenario: Error state
        Then the button is red
    ```

    **After:**

    ```gherkin
    Feature: Status display

      Scenario: Error state
        Then the button is red and shows "Error"
    ```

### How it works

1. Iterates over all scenarios and their steps.
2. For each step, checks if the text contains a color word.
3. If a color word is found, checks if the text also contains a
   non-color indicator (e.g., `text`, `label`, `icon`, `error`).
4. If color is present but no non-color indicator is found, reports a
   diagnostic suggesting to add a text, icon, or pattern indicator.

### Configuration

This rule has no configurable parameters.
