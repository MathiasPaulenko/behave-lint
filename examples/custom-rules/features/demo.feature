Feature: Custom Rule Demo

  @smoke
  Scenario: Given after Then violation
    Given a user
    Then I see the dashboard
    Given another user

  @regression
  Scenario: Correct ordering
    Given a user
    When I click login
    Then I see the dashboard
