"""Security rules - BSEC001-BSEC499.

Rules that detect security concerns and sensitive data exposure in
Gherkin feature files.

Default severity: ERROR.
"""

from __future__ import annotations

import re
from typing import Any, ClassVar

from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import AutoFixCapability, Category, Severity
from behave_lint.models.rule_metadata import RuleExample, RuleMetadata
from behave_lint.rules.base import Rule

_SENSITIVE_KEYWORDS = re.compile(
    r"\b(password|passwd|pwd|secret|api[_-]?key|access[_-]?token|"
    r"auth[_-]?token|private[_-]?key|credit[_-]?card|ssn|"
    r"social[_-]?security)\b",
    re.IGNORECASE,
)

_HARDCODED_VALUE_PATTERN = re.compile(
    r"=\s*[\"'](?:[A-Za-z0-9+/=_-]{8,}|[A-Fa-f0-9]{32,}|"
    r"sk_[A-Za-z0-9_]{20,}|ghp_[A-Za-z0-9_]{20,}|"
    r"AKIA[A-Z0-9]{12,})[\"']",
)

_URL_CREDENTIALS_PATTERN = re.compile(
    r"https?://[^:/@\s]+:([^/@\s]+)@",
)


class HardcodedSecretsRule(Rule):
    """BSEC001: Detect hardcoded secrets and credentials in steps.

    Steps that contain literal passwords, API keys, tokens, or other
    sensitive values are a security risk. Use placeholders or
    environment variables instead.
    """

    metadata = RuleMetadata(
        rule_id="BSEC001",
        name="hardcoded-secrets",
        title="Hardcoded secrets and credentials in steps",
        description=(
            "Detects steps that contain literal passwords, API keys, "
            "tokens, or other sensitive values. Hardcoded secrets are "
            "a security risk and should be replaced with placeholders "
            "or environment variables."
        ),
        category=Category.SECURITY,
        default_severity=Severity.ERROR,
        motivation=(
            "Hardcoded secrets in test files can be committed to "
            "version control and leaked. Even in test scenarios, "
            "real credentials should never appear in feature files."
        ),
        since="2.4.0",
        examples=[
            RuleExample(
                before=(
                    "Feature: Login\n\n"
                    "  Scenario: Login with credentials\n"
                    "    Given the user enters password \"hunter2\"\n"
                ),
                after=(
                    "Feature: Login\n\n"
                    "  Scenario: Login with credentials\n"
                    "    Given the user enters password \"<password>\"\n"
                ),
                description="Replace hardcoded password with a placeholder.",
            ),
        ],
        tags=["security", "secrets", "credentials"],
        auto_fix=AutoFixCapability.NONE,
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            for step in steps:
                text = getattr(step, "name", "")
                if _SENSITIVE_KEYWORDS.search(text) and _HARDCODED_VALUE_PATTERN.search(
                    text
                ):
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Step contains a hardcoded secret near "
                                f"a sensitive keyword: '{text.strip()}'"
                            ),
                            node=step,
                            suggestion=(
                                "Replace the hardcoded value with a "
                                "placeholder or environment variable."
                            ),
                        )
                    )

        return diagnostics


class UrlWithCredentialsRule(Rule):
    """BSEC002: Detect URLs with embedded credentials in steps.

    Steps that contain URLs with embedded usernames and passwords
    (e.g., ``https://user:pass@host``) expose credentials in test
    files.
    """

    metadata = RuleMetadata(
        rule_id="BSEC002",
        name="url-with-credentials",
        title="URLs with embedded credentials in steps",
        description=(
            "Detects steps that contain URLs with embedded credentials "
            "(e.g., https://user:password@host). Credentials in URLs "
            "are visible in logs and version control."
        ),
        category=Category.SECURITY,
        default_severity=Severity.ERROR,
        motivation=(
            "URLs with embedded credentials expose sensitive data in "
            "logs, browser history, and version control. Use "
            "environment variables or configuration files instead."
        ),
        since="2.4.0",
        examples=[
            RuleExample(
                before=(
                    "Feature: API test\n\n"
                    "  Scenario: Fetch data\n"
                    '    Given the API endpoint is "https://admin:pass@api.example.com"\n'
                ),
                after=(
                    "Feature: API test\n\n"
                    "  Scenario: Fetch data\n"
                    '    Given the API endpoint is "<api_url>"\n'
                ),
                description="Replace URL credentials with a placeholder.",
            ),
        ],
        tags=["security", "url", "credentials"],
        auto_fix=AutoFixCapability.NONE,
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            steps = getattr(scenario, "steps", [])
            for step in steps:
                text = getattr(step, "name", "")
                match = _URL_CREDENTIALS_PATTERN.search(text)
                if match:
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Step contains a URL with embedded "
                                f"credentials: '{text.strip()}'"
                            ),
                            node=step,
                            suggestion=(
                                "Replace the URL credentials with a "
                                "placeholder or environment variable."
                            ),
                        )
                    )

        return diagnostics


class SensitiveTagRule(Rule):
    """BSEC003: Detect sensitive tags that may leak test context.

    Tags like @production, @live, @real-data, or @sensitive indicate
    that the scenario may interact with real systems or data. These
    tags should be reviewed to prevent accidental execution against
    production environments.
    """

    metadata = RuleMetadata(
        rule_id="BSEC003",
        name="sensitive-tags",
        title="Sensitive tags that may indicate production interaction",
        description=(
            "Detects tags like @production, @live, @real-data, or "
            "@sensitive that suggest the scenario may interact with "
            "real systems or data. These tags should be reviewed to "
            "prevent accidental execution against production."
        ),
        category=Category.SECURITY,
        default_severity=Severity.WARNING,
        motivation=(
            "Tags that indicate production interaction or sensitive "
            "data should be explicitly reviewed. Accidental execution "
            "of these scenarios in production can cause data leaks or "
            "system disruption."
        ),
        since="2.4.0",
        examples=[
            RuleExample(
                before=(
                    "@production\n"
                    "Feature: Data migration\n\n"
                    "  Scenario: Migrate records\n"
                    "    Given the database is ready\n"
                ),
                after=(
                    "@staging\n"
                    "Feature: Data migration\n\n"
                    "  Scenario: Migrate records\n"
                    "    Given the database is ready\n"
                ),
                description="Use @staging instead of @production.",
            ),
        ],
        tags=["security", "tags", "production"],
        auto_fix=AutoFixCapability.NONE,
    )

    _SENSITIVE_TAGS: ClassVar[frozenset[str]] = frozenset(
        {"production", "live", "real-data", "sensitive", "prod"}
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        feature_tags = getattr(feature, "tags", [])
        for tag in feature_tags:
            tag_name = getattr(tag, "name", str(tag)).lstrip("@").lower()
            if tag_name in self._SENSITIVE_TAGS:
                diagnostics.append(
                    self.diagnostic(
                        message=(
                            f"Sensitive tag '@{tag_name}' may indicate "
                            f"production interaction"
                        ),
                        node=feature,
                        suggestion=(
                            "Review this tag. Consider using @staging "
                            "or @test instead."
                        ),
                        severity=Severity.WARNING,
                    )
                )

        for scenario in feature.all_scenarios():
            scenario_tags = getattr(scenario, "tags", [])
            for tag in scenario_tags:
                tag_name = getattr(tag, "name", str(tag)).lstrip("@").lower()
                if tag_name in self._SENSITIVE_TAGS:
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Sensitive tag '@{tag_name}' may indicate "
                                f"production interaction"
                            ),
                            node=scenario,
                            suggestion=(
                                "Review this tag. Consider using @staging "
                                "or @test instead."
                            ),
                            severity=Severity.WARNING,
                        )
                    )

        return diagnostics


__all__ = [
    "HardcodedSecretsRule",
    "SensitiveTagRule",
    "UrlWithCredentialsRule",
]
