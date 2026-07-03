"""Internationalization rules - BI18N001-BI18N499.

Rules that detect internationalization issues in Gherkin feature files,
such as hardcoded locale-specific text or non-ASCII characters that may
cause encoding problems.

Default severity: WARNING.
"""

from __future__ import annotations

import re
from typing import Any

from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import AutoFixCapability, Category, Severity
from behave_lint.models.rule_metadata import RuleExample, RuleMetadata
from behave_lint.rules.base import Rule

_NON_ASCII_PATTERN = re.compile(r"[^\x00-\x7F]")

_LOCALE_SPECIFIC_PATTERN = re.compile(
    r"\b(?:"
    r"\$\d+(?:\.\d{2})?"  # $10.99
    r"|\xe2\x82\xac\d+"  # euro sign + digits
    r"|\d{1,2}/\d{1,2}/\d{2,4}"  # date formats
    r"|\d{4}-\d{2}-\d{2}"  # ISO date
    r"|\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM|am|pm)"  # time
    r")\b"
)

_CURRENCY_SYMBOLS = re.compile(r"[$\u20ac\u00a3\u00a5\u20a6\u20a9\u20b9]")


class HardcodedDateFormatRule(Rule):
    """BI18N001: Detect hardcoded date and time formats in steps.

    Steps that contain hardcoded date or time formats (e.g.,
    ``12/31/2024`` or ``2024-12-31``) are locale-specific and may
    not work correctly in different regions. Use placeholders or
    parameterized values instead.
    """

    metadata = RuleMetadata(
        rule_id="BI18N001",
        name="hardcoded-date-format",
        title="Hardcoded date and time formats in steps",
        description=(
            "Detects steps that contain hardcoded date or time formats. "
            "Date formats are locale-specific and may cause failures "
            "in different regions or time zones."
        ),
        category=Category.I18N,
        default_severity=Severity.WARNING,
        motivation=(
            "Hardcoded dates assume a specific locale and format. "
            "Different regions use different date formats (MM/DD/YYYY "
            "vs DD/MM/YYYY), leading to ambiguity and test failures."
        ),
        since="2.4.0",
        examples=[
            RuleExample(
                before=(
                    "Feature: Booking\n\n"
                    "  Scenario: Book on a date\n"
                    '    Given the booking date is "12/31/2024"\n'
                ),
                after=(
                    "Feature: Booking\n\n"
                    "  Scenario: Book on a date\n"
                    '    Given the booking date is "<booking_date>"\n'
                ),
                description="Replace hardcoded date with a placeholder.",
            ),
        ],
        tags=["i18n", "date", "locale"],
        auto_fix=AutoFixCapability.NONE,
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            for step in steps:
                text = getattr(step, "name", "")
                if _LOCALE_SPECIFIC_PATTERN.search(text):
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Step contains a hardcoded date/time "
                                f"format: '{text.strip()}'"
                            ),
                            node=step,
                            suggestion=(
                                "Replace the hardcoded date/time with a "
                                "placeholder or parameterized value."
                            ),
                        )
                    )

        return diagnostics


class HardcodedCurrencyRule(Rule):
    """BI18N002: Detect hardcoded currency symbols in steps.

    Steps that contain hardcoded currency symbols (e.g., $, EUR, GBP)
    are locale-specific. Use placeholders or parameterized values to
    support multiple currencies.
    """

    metadata = RuleMetadata(
        rule_id="BI18N002",
        name="hardcoded-currency",
        title="Hardcoded currency symbols in steps",
        description=(
            "Detects steps that contain hardcoded currency symbols "
            "like $, EUR, or GBP. Currency symbols are locale-specific "
            "and may not be appropriate for all regions."
        ),
        category=Category.I18N,
        default_severity=Severity.WARNING,
        motivation=(
            "Hardcoded currency symbols assume a specific locale. "
            "Tests should use placeholders to support multiple "
            "currencies and locales."
        ),
        since="2.4.0",
        examples=[
            RuleExample(
                before=(
                    "Feature: Payment\n\n"
                    '  Scenario: Pay amount\n'
                    '    Given the total is "$99.99"\n'
                ),
                after=(
                    "Feature: Payment\n\n"
                    '  Scenario: Pay amount\n'
                    '    Given the total is "<amount>"\n'
                ),
                description="Replace hardcoded currency with a placeholder.",
            ),
        ],
        tags=["i18n", "currency", "locale"],
        auto_fix=AutoFixCapability.NONE,
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            for step in steps:
                text = getattr(step, "name", "")
                if _CURRENCY_SYMBOLS.search(text):
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Step contains a hardcoded currency "
                                f"symbol: '{text.strip()}'"
                            ),
                            node=step,
                            suggestion=(
                                "Replace the currency symbol with a "
                                "placeholder or parameterized value."
                            ),
                        )
                    )

        return diagnostics


class NonAsciiStepTextRule(Rule):
    """BI18N003: Detect non-ASCII characters in step text.

    Steps that contain non-ASCII characters (e.g., accented letters,
    CJK characters, emoji) may cause encoding issues in some test
    runners or CI environments. Ensure proper UTF-8 encoding is used.
    """

    metadata = RuleMetadata(
        rule_id="BI18N003",
        name="non-ascii-step-text",
        title="Non-ASCII characters in step text",
        description=(
            "Detects steps that contain non-ASCII characters. While "
            "UTF-8 is widely supported, non-ASCII characters can cause "
            "encoding issues in some test runners, CI environments, "
            "or when sharing files across platforms."
        ),
        category=Category.I18N,
        default_severity=Severity.INFO,
        motivation=(
            "Non-ASCII characters may cause encoding issues in "
            "environments that do not properly handle UTF-8. This "
            "rule helps identify potential encoding problems early."
        ),
        since="2.4.0",
        examples=[
            RuleExample(
                before=(
                    "Feature: Caf\u00e9 menu\n\n"
                    "  Scenario: Order coffee\n"
                    "    Given the customer selects \"caf\u00e9 au lait\"\n"
                ),
                after=(
                    "Feature: Cafe menu\n\n"
                    "  Scenario: Order coffee\n"
                    '    Given the customer selects "cafe au lait"\n'
                ),
                description="Replace non-ASCII characters with ASCII equivalents.",
            ),
        ],
        tags=["i18n", "encoding", "ascii"],
        auto_fix=AutoFixCapability.NONE,
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            for step in steps:
                text = getattr(step, "name", "")
                if _NON_ASCII_PATTERN.search(text):
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Step contains non-ASCII characters: "
                                f"'{text.strip()}'"
                            ),
                            node=step,
                            suggestion=(
                                "Ensure UTF-8 encoding is used, or "
                                "replace non-ASCII characters with "
                                "ASCII equivalents."
                            ),
                            severity=Severity.INFO,
                        )
                    )

        return diagnostics


__all__ = [
    "HardcodedCurrencyRule",
    "HardcodedDateFormatRule",
    "NonAsciiStepTextRule",
]
