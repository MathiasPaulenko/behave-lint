Feature: Login

  Scenario: Successful login
    Given a registered user
    When they enter valid credentials
    Then they are logged in
