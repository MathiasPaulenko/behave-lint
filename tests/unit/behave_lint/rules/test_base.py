"""Unit tests for the Rule base class."""

from __future__ import annotations

from typing import ClassVar

from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.rule_metadata import RuleMetadata
from behave_lint.rules.base import Rule
from behave_lint.rules.diagnostic_factory import DiagnosticFactory
from behave_lint.rules.scope import RuleScope


class FakeNode:
    """Fake behave-model node for testing."""

    def __init__(
        self,
        file_path: str = "features/test.feature",
        line: int = 10,
        column: int | None = None,
    ) -> None:
        self.file_path = file_path
        self.line = line
        self.column = column


def _make_metadata(
    rule_id: str = "BC001",
    name: str = "test-rule",
    category: Category = Category.CORRECTNESS,
    severity: Severity = Severity.ERROR,
) -> RuleMetadata:
    return RuleMetadata(
        rule_id=rule_id,
        name=name,
        title="Test Rule",
        description="A test rule.",
        category=category,
        default_severity=severity,
        motivation="For testing.",
        since="0.1.0",
    )


class TestRuleBase:
    """Tests for the Rule base class."""

    def test_rule_subclass_with_check(self) -> None:
        class MyRule(Rule):
            metadata = _make_metadata()

            def check(self, feature: object, config: Config) -> list[Diagnostic]:
                return [self.diagnostic("Found issue", node=FakeNode())]

        rule = MyRule()
        config = Config()
        diags = rule.check(None, config)

        assert len(diags) == 1
        assert diags[0].rule_id == "BC001"
        assert diags[0].severity == Severity.ERROR
        assert diags[0].category == Category.CORRECTNESS
        assert diags[0].message == "Found issue"

    def test_rule_diagnostic_with_factory(self) -> None:
        class MyRule(Rule):
            metadata = _make_metadata()

            def check(self, feature: object, config: Config) -> list[Diagnostic]:
                return []

        rule = MyRule()
        factory = DiagnosticFactory(
            rule_id="BC001",
            category=Category.CORRECTNESS,
            severity=Severity.WARNING,
        )
        rule._set_diagnostic_factory(factory)
        diag = rule.diagnostic("Test issue", node=FakeNode(line=5))

        assert diag.rule_id == "BC001"
        assert diag.severity == Severity.WARNING
        assert diag.line == 5

    def test_rule_diagnostic_without_factory(self) -> None:
        class MyRule(Rule):
            metadata = _make_metadata()

            def check(self, feature: object, config: Config) -> list[Diagnostic]:
                return []

        rule = MyRule()
        diag = rule.diagnostic("Fallback", line=3, file_path="test.feature")

        assert diag.rule_id == "BC001"
        assert diag.severity == Severity.ERROR
        assert diag.file_path == "test.feature"
        assert diag.line == 3

    def test_rule_diagnostic_with_severity_override(self) -> None:
        class MyRule(Rule):
            metadata = _make_metadata()

            def check(self, feature: object, config: Config) -> list[Diagnostic]:
                return []

        rule = MyRule()
        factory = DiagnosticFactory(
            rule_id="BC001",
            category=Category.CORRECTNESS,
            severity=Severity.ERROR,
        )
        rule._set_diagnostic_factory(factory)
        diag = rule.diagnostic("Test", line=1, file_path="t.f", severity=Severity.INFO)

        assert diag.severity == Severity.INFO

    def test_rule_properties(self) -> None:
        class MyRule(Rule):
            metadata = _make_metadata(
                rule_id="BS001",
                name="my-rule",
                category=Category.STYLE,
                severity=Severity.WARNING,
            )

            def check(self, feature: object, config: Config) -> list[Diagnostic]:
                return []

        rule = MyRule()
        assert rule.rule_id == "BS001"
        assert rule.category == Category.STYLE
        assert rule.default_severity == Severity.WARNING

    def test_rule_default_scope(self) -> None:
        class MyRule(Rule):
            metadata = _make_metadata()

            def check(self, feature: object, config: Config) -> list[Diagnostic]:
                return []

        assert MyRule.scope == RuleScope.SINGLE_FILE

    def test_rule_custom_scope(self) -> None:
        class MyRule(Rule):
            metadata = _make_metadata()
            scope = RuleScope.CROSS_FILE

            def check(self, feature: object, config: Config) -> list[Diagnostic]:
                return []

        assert MyRule.scope == RuleScope.CROSS_FILE

    def test_rule_base_check_raises_not_implemented(self) -> None:
        class MyRule(Rule):
            metadata = _make_metadata()

        rule = MyRule()
        try:
            rule.check(None, Config())
            raise AssertionError("Should have raised NotImplementedError")
        except NotImplementedError:
            pass

    def test_rule_default_params(self) -> None:
        class MyRule(Rule):
            metadata = _make_metadata()
            default_params: ClassVar[dict[str, int]] = {"max_steps": 10}

            def check(self, feature: object, config: Config) -> list[Diagnostic]:
                return []

        assert MyRule.default_params == {"max_steps": 10}
