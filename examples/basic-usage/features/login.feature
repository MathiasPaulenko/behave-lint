Feature: User Login

  As a registered user
  I want to log in to my account
  So that I can access the dashboard

  @smoke
  Scenario: Successful login with valid credentials
    Given a registered user with username "alice"
    When the user submits the login form with valid credentials
    Then the dashboard is displayed

  @regression
  Scenario: Failed login with invalid password
    Given a registered user with username "alice"
    When the user submits the login form with an invalid password
    Then an error message "Invalid credentials" is shown

  @regression
  Scenario: Failed login with non-existent user
    Given no user with username "unknown"
    When the user submits the login form with username "unknown"
    Then an error message "User not found" is shown
