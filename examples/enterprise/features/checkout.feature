Feature: Checkout

  Scenario: Pay by card
    Given a cart with items
    When the customer pays by card
    Then the order is confirmed
