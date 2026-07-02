"""Generate test fixture .feature files for benchmarks and golden tests.

This script creates a configurable number of .feature files with
varying complexity for use in performance benchmarks and golden tests.

Usage:
    python scripts/generate_fixtures.py [--count N] [--output DIR]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_TEMPLATES = [
    """Feature: Login Feature {idx}

  As a registered user
  I want to log in to my account
  So that I can access the dashboard

  @smoke
  Scenario: Successful login with valid credentials
    Given a registered user with username "user{idx}"
    When the user submits the login form with valid credentials
    Then the dashboard is displayed
    And a welcome message is shown

  @regression
  Scenario: Failed login with invalid password
    Given a registered user with username "user{idx}"
    When the user submits the login form with an invalid password
    Then an error message "Invalid credentials" is shown

  Scenario Outline: Login with multiple users
    Given a user with username "<username>"
    When the user logs in with password "<password>"
    Then the result is "<result>"

    Examples: Valid users
      | username | password | result    |
      | alice    | secret1  | welcome   |
      | bob      | secret2  | welcome   |

    Examples: Invalid users
      | username | password | result             |
      | alice    | wrong    | Invalid credentials |
      | hacker   | exploit  | User not found     |
""",
    """Feature: Shopping Cart Feature {idx}

  As a shopper
  I want to manage my shopping cart
  So that I can review items before checkout

  Background:
    Given the user is logged in
    And the cart is empty

  @smoke
  Scenario: Add item to empty cart
    When the user adds "Laptop" to the cart
    Then the cart contains 1 item
    And the cart total is $999.00

  @regression
  Scenario: Remove item from cart
    Given a shopping cart with 3 items
    When the user removes the first item
    Then the cart contains 2 items

  Scenario Outline: Apply discount codes
    Given a shopping cart with a total of $<total>
    When the user applies discount code "<code>"
    Then the cart total is $<discounted>

    Examples: Percentage discounts
      | total | code   | discounted |
      | 100   | SAVE10 | 90.00      |
      | 200   | SAVE20 | 160.00     |
      | 50    | SAVE10 | 45.00      |
""",
    """Feature: Search Feature {idx}

  As a visitor
  I want to search for products
  So that I can find what I need

  @smoke
  Scenario: Search with results
    Given the catalog has products matching "laptop"
    When the user searches for "laptop"
    Then 5 results are displayed
    And the results are sorted by relevance

  @regression
  Scenario: Search with no results
    Given the catalog has no products matching "xyz123"
    When the user searches for "xyz123"
    Then a "No results found" message is displayed

  Scenario Outline: Filter search results
    Given search results for "<query>"
    When the user filters by "<filter>"
    Then only "<expected>" results are shown

    Examples:
      | query   | filter   | expected |
      | laptop  | brand    | 3        |
      | laptop  | price    | 2        |
      | phone   | brand    | 5        |
""",
]


def generate_feature_file(index: int) -> str:
    """Generate a single .feature file content.

    Args:
        index: The feature file index for unique naming.

    Returns:
        The .feature file content as a string.
    """
    template = _TEMPLATES[index % len(_TEMPLATES)]
    return template.format(idx=index)


def main() -> None:
    """Generate fixture .feature files."""
    parser = argparse.ArgumentParser(
        description="Generate .feature fixture files for benchmarks."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of .feature files to generate (default: 10)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("benchmarks/fixtures"),
        help="Output directory (default: benchmarks/fixtures)",
    )
    args = parser.parse_args()

    output_dir: Path = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    for i in range(args.count):
        feature_path = output_dir / f"feature_{i:04d}.feature"
        feature_path.write_text(generate_feature_file(i), encoding="utf-8")

    print(f"Generated {args.count} .feature files in {output_dir}")


if __name__ == "__main__":
    sys.exit(main() or 0)
