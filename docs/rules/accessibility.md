# Accessibility Rules

Rules that detect accessibility and inclusive design concerns in Gherkin
feature files, such as ableist language or missing accessibility test
coverage.

**Default severity:** WARNING

| Rule | Name | Severity | Auto-fix |
|------|------|----------|----------|
| BACC001 | [ableist-language](#bacc001-ableist-language) | WARNING | No |
| BACC002 | [missing-accessibility-scenario](#bacc002-missing-accessibility-scenario) | WARNING | No |
| BACC003 | [color-only-contrast](#bacc003-color-only-contrast) | WARNING | No |

## BACC001: ableist-language

Detects ableist terms in step text and scenario names. Ableist language
reinforces stereotypes and should be replaced with person-first or
identity-first language.

### Example

```gherkin
# Bad
Scenario: Register disabled user
  Given a disabled user

# Good
Scenario: Register user with a disability
  Given a user with a disability
```

## BACC002: missing-accessibility-scenario

Detects features with UI-related tags (`@ui`, `@frontend`, `@web`) that
lack accessibility test scenarios (tagged `@accessibility` or `@a11y`).

### Example

```gherkin
# Bad
@ui
Feature: Login form
  Scenario: Successful login
    Given the user is on the login page

# Good
@ui
Feature: Login form
  Scenario: Successful login
    Given the user is on the login page

  @accessibility
  Scenario: Login form is keyboard accessible
    Given the user is on the login page
    Then the form can be completed with the keyboard
```

## BACC003: color-only-contrast

Detects steps that reference color alone to convey information. Relying
solely on color is inaccessible to users with color blindness.

### Example

```gherkin
# Bad
Then the button is red

# Good
Then the button is red and shows "Error"
```
