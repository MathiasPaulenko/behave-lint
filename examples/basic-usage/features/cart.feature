Feature: Shopping Cart

  As a shopper
  I want to manage my shopping cart
  So that I can review items before checkout

  @smoke
  Scenario: Add item to empty cart
    Given an empty shopping cart
    When the user adds "Laptop" to the cart
    Then the cart contains 1 item
    And the cart total is $999.00

  @regression
  Scenario: Remove item from cart
    Given a shopping cart with 2 items
    When the user removes the first item
    Then the cart contains 1 item

  @regression
  Scenario Outline: Apply discount code
    Given a shopping cart with a total of $<total>
    When the user applies discount code "<code>"
    Then the cart total is $<discounted>

    Examples: Percentage discounts
      | total | code    | discounted |
      | 100   | SAVE10  | 90.00      |
      | 200   | SAVE20  | 160.00     |
      | 50    | SAVE10  | 45.00      |

    Examples: Fixed discounts
      | total | code     | discounted |
      | 100   | FLAT10   | 90.00      |
      | 200   | FLAT25   | 175.00     |
