# Auto-Fix

`behave-lint` can automatically fix certain rule violations in your
`.feature` files.

## Usage

```bash
# Apply safe fixes only
behave-lint features/ --fix

# Apply safe and unsafe fixes
behave-lint features/ --fix --unsafe-fixes
```

## Safe vs. unsafe fixes

| Category | Description |
|----------|-------------|
| **Safe** | Deterministic transformations that cannot change test semantics. Applied with `--fix`. |
| **Unsafe** | Transformations that may change behavior or require human review. Only applied with `--unsafe-fixes`. |

## Rules with auto-fix support

### Safe fixes

| Rule | Fix |
|------|-----|
| **BC004** (invalid-tag-syntax) | Replace invalid characters in tags with `_`. |
| **BD004** (step-parameter-convention) | Convert `{param}` to `<param>` when both conventions are mixed. |
| **BD005** (step-trailing-punctuation) | Remove trailing punctuation from step text. |
| **BS001** (tag-casing) | Convert tags to lowercase `snake_case`. |
| **BS006** (step-keyword-casing) | Capitalize step keywords (e.g., `given` → `Given`). |
| **BS007** (trailing-whitespace) | Remove trailing whitespace from lines. |
| **BS008** (tab-indentation) | Replace tab indentation with spaces (2 per level). |

### Unsafe fixes

| Rule | Fix |
|------|-----|
| **BS002** (keyword-ordering) | Reorder steps to Given → When → Then. |
| **BS003** (step-phrasing) | Rewrite first-person steps to third-person. |
| **BS004** (background-name) | Insert `Background: Common setup` as a placeholder name. |
| **BS005** (feature-description) | Insert a template As a / I want / So that description. |

## Conflict resolution

When multiple fixes target overlapping lines in the same file,
`behave-lint` applies only the first fix and skips conflicting ones.
A warning is printed for each skipped fix.

## Examples

### Fix tag casing (BS001)

Before:

```gherkin
@SmokeTest
Feature: Login
```

After `--fix`:

```gherkin
@smoke_test
Feature: Login
```

### Fix invalid tag syntax (BC004)

Before:

```gherkin
@smoke-test
Feature: Login
```

After `--fix`:

```gherkin
@smoke_test
Feature: Login
```

### Fix trailing punctuation (BD005)

Before:

```gherkin
  Scenario: Login
    Given a user.
    When I click submit.
```

After `--fix`:

```gherkin
  Scenario: Login
    Given a user
    When I click submit
```

### Fix mixed parameter convention (BD004)

Before:

```gherkin
  Scenario Outline: Test <value>
    Given a <value> with {count} items
```

After `--fix`:

```gherkin
  Scenario Outline: Test <value>
    Given a <value> with <count> items
```

### Fix step keyword casing (BS006)

Before:

```gherkin
  Scenario: Login
    given a user
    when I click submit
    then I see the dashboard
```

After `--fix`:

```gherkin
  Scenario: Login
    Given a user
    When I click submit
    Then I see the dashboard
```

### Fix trailing whitespace (BS007)

Before:

```gherkin
Feature: Login   
  Scenario: Test  
    Given a step
```

After `--fix`:

```gherkin
Feature: Login
  Scenario: Test
    Given a step
```

### Fix tab indentation (BS008)

Before:

```gherkin
Feature: Login
	Scenario: Test
		Given a step
```

After `--fix`:

```gherkin
Feature: Login
  Scenario: Test
    Given a step
```
