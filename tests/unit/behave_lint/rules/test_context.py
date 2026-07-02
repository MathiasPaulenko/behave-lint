"""Unit tests for RuleScope enum and RuleContext."""

from __future__ import annotations

from behave_lint.models.config import Config
from behave_lint.models.enums import Category, Severity
from behave_lint.rules.context import RuleContext
from behave_lint.rules.diagnostic_factory import DiagnosticFactory
from behave_lint.rules.scope import RuleScope


class TestRuleScope:
    """Tests for RuleScope enum."""

    def test_single_file(self) -> None:
        assert RuleScope.SINGLE_FILE.value == "single_file"

    def test_cross_file(self) -> None:
        assert RuleScope.CROSS_FILE.value == "cross_file"

    def test_distinct_members(self) -> None:
        assert RuleScope.SINGLE_FILE is not RuleScope.CROSS_FILE


class TestRuleContext:
    """Tests for RuleContext."""

    def test_init_with_defaults(self) -> None:
        config = Config()
        ctx = RuleContext(config=config, severity=Severity.ERROR)

        assert ctx.config is config
        assert ctx.severity == Severity.ERROR
        assert ctx.rule_params == {}
        assert ctx.feature is None
        assert ctx.project is None
        assert ctx.file_path is None
        assert ctx.step_definitions is None
        assert ctx.diagnostic_factory is not None

    def test_init_with_all_fields(self) -> None:
        config = Config()
        factory = DiagnosticFactory(
            rule_id="BC001",
            category=Category.CORRECTNESS,
            severity=Severity.ERROR,
        )
        ctx = RuleContext(
            config=config,
            severity=Severity.WARNING,
            rule_params={"max_steps": 10},
            file_path="features/test.feature",
            step_definitions=[],
            diagnostic_factory=factory,
        )

        assert ctx.severity == Severity.WARNING
        assert ctx.rule_params == {"max_steps": 10}
        assert ctx.file_path == "features/test.feature"
        assert ctx.step_definitions == []
        assert ctx.diagnostic_factory is factory

    def test_default_diagnostic_factory(self) -> None:
        config = Config()
        ctx = RuleContext(
            config=config,
            severity=Severity.WARNING,
            file_path="features/test.feature",
        )

        assert ctx.diagnostic_factory.severity == Severity.WARNING
        assert ctx.diagnostic_factory.file_path == "features/test.feature"
