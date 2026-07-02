@SmokeTest
Feature: Auto-Fix Demo

  This feature file contains violations that can be
  automatically fixed by behave-lint.

  @WIP
  Scenario: Tag casing and syntax
    Given a user.
    When I click submit.

  @smoke-test
  Scenario: Invalid tag characters
    Given a registered user
    When the user submits the form.
    Then the form is accepted.

  Scenario Outline: Mixed parameter conventions
    Given a user with {value}
    When the user selects <option>

    Examples:
      | value | option |
      | alice | yes    |
      | bob   | no     |
