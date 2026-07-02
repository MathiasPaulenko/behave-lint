Feature: User Registration

  As a new visitor
  I want to create an account
  So that I can use the platform

  @smoke
  Scenario: Register with valid data
    Given no user with email "new@example.com"
    When the user submits the registration form with valid data
    Then the account is created
    And a welcome email is sent to "new@example.com"

  @regression
  Scenario: Register with existing email
    Given a user with email "existing@example.com"
    When the user submits the registration form with email "existing@example.com"
    Then an error message "Email already registered" is shown
