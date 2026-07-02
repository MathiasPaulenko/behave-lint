Feature: Checkout Flow

  As a customer
  I want to complete my purchase
  So that I receive my products

  @smoke
  Scenario: Successful checkout
    Given a shopping cart with 3 items
    When the user proceeds to checkout
    And the user enters valid payment details
    Then the order is confirmed
    And a confirmation email is sent

  @regression
  Scenario: Checkout with empty cart
    Given an empty shopping cart
    When the user proceeds to checkout
    Then an error message "Cart is empty" is shown
