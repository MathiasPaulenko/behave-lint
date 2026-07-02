"""Unit tests for the RuleExecutor."""

from __future__ import annotations

import warnings
from typing import Any

import pytest

from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.rule_metadata import RuleMetadata
from behave_lint.rules.base import Rule
from behave_lint.rules.executor import RuleExecutor
from behave_lint.rules.registry import RuleRegistry
from behave_lint.rules.scope import RuleScope


class FakeFeature:
    """Fake feature model for testing."""

    def __init__(
        self,
        name: str = "Test Feature",
        file_path: str = "features/test.feature",
        line: int = 1,
        scenarios: list[Any] | None = None,
    ) -> None:
        self.name = name
        self.file_path = file_path
        self.line = line
        self.scenarios = scenarios or []


class FakeProject:
    """Fake project model for testing."""

    def __init__(self, features: list[Any] | None = None) -> None:
        self.features = features or []


def _make_metadata(
    rule_id: str = "BC001",
    name: str = "test-rule",
    category: Category = Category.CORRECTNESS,
    severity: Severity = Severity.ERROR,
    deprecated: bool = False,
    replaced_by: str | None = None,
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
        deprecated=deprecated,
        replaced_by=replaced_by,
    )


def _make_rule_class(
    metadata: RuleMetadata,
    scope: RuleScope = RuleScope.SINGLE_FILE,
    diagnostics: list[Diagnostic] | None = None,
    raises: type[Exception] | None = None,
) -> type[Rule]:
    class TestRule(Rule):
        pass

    TestRule.metadata = metadata
    TestRule.scope = scope

    if raises:

        def check(self: Rule, feature: Any, config: Config) -> list[Diagnostic]:
            raise raises("Rule failed")

        TestRule.check = check  # type: ignore[method-assign]
    elif diagnostics is not None:

        def check(self: Rule, feature: Any, config: Config) -> list[Diagnostic]:
            return list(diagnostics)

        TestRule.check = check  # type: ignore[method-assign]
    else:

        def check(self: Rule, feature: Any, config: Config) -> list[Diagnostic]:
            return []

        TestRule.check = check  # type: ignore[method-assign]

    return TestRule


class TestRuleExecutor:
    """Tests for RuleExecutor."""

    def test_execute_single_file_rule(self) -> None:
        registry = RuleRegistry()
        metadata = _make_metadata()
        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="Test issue",
            file_path="features/test.feature",
            line=5,
            category=Category.CORRECTNESS,
        )
        rule_class = _make_rule_class(metadata, diagnostics=[diag])
        registry.register(rule_class)

        executor = RuleExecutor(registry, Config())
        features = [FakeFeature()]
        results, fixes = executor.execute(features)

        assert len(results) == 1
        assert results[0].rule_id == "BC001"
        assert results[0].message == "Test issue"
        assert fixes == []

    def test_execute_multiple_features(self) -> None:
        registry = RuleRegistry()
        metadata = _make_metadata()
        diag1 = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="Issue 1",
            file_path="features/a.feature",
            line=1,
            category=Category.CORRECTNESS,
        )
        diag2 = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="Issue 2",
            file_path="features/b.feature",
            line=2,
            category=Category.CORRECTNESS,
        )

        class MultiDiagRule(Rule):
            pass

        MultiDiagRule.metadata = metadata

        def check(self: Rule, feature: Any, config: Config) -> list[Diagnostic]:
            if feature.file_path == "features/a.feature":
                return [diag1]
            return [diag2]

        MultiDiagRule.check = check  # type: ignore[method-assign]
        registry.register(MultiDiagRule)

        executor = RuleExecutor(registry, Config())
        features = [
            FakeFeature(file_path="features/a.feature"),
            FakeFeature(file_path="features/b.feature"),
        ]
        results, _fixes = executor.execute(features)

        assert len(results) == 2
        messages = {r.message for r in results}
        assert messages == {"Issue 1", "Issue 2"}

    def test_execute_cross_file_rule(self) -> None:
        registry = RuleRegistry()
        metadata = _make_metadata(rule_id="BK001", name="cross-rule")
        diag = Diagnostic(
            rule_id="BK001",
            severity=Severity.WARNING,
            message="Cross-file issue",
            file_path="features/test.feature",
            line=1,
            category=Category.CONSISTENCY,
        )
        rule_class = _make_rule_class(
            metadata, scope=RuleScope.CROSS_FILE, diagnostics=[diag]
        )
        registry.register(rule_class)

        executor = RuleExecutor(registry, Config())
        project = FakeProject(features=[FakeFeature()])
        results, _fixes = executor.execute([], project=project)

        assert len(results) == 1
        assert results[0].rule_id == "BK001"

    def test_execute_rule_failure_isolated(self) -> None:
        registry = RuleRegistry()
        metadata_good = _make_metadata(rule_id="BC001", name="good-rule")
        metadata_bad = _make_metadata(rule_id="BC002", name="bad-rule")

        good_diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="Good",
            file_path="features/test.feature",
            line=1,
            category=Category.CORRECTNESS,
        )

        good_rule = _make_rule_class(metadata_good, diagnostics=[good_diag])
        bad_rule = _make_rule_class(metadata_bad, raises=RuntimeError)
        registry.register(good_rule)
        registry.register(bad_rule)

        executor = RuleExecutor(registry, Config())
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            results, _fixes = executor.execute([FakeFeature()])

        # Only the good rule's diagnostics
        assert len(results) == 1
        assert results[0].rule_id == "BC001"

    def test_execute_stamps_rule_id_and_category(self) -> None:
        registry = RuleRegistry()
        metadata = _make_metadata(rule_id="BC001", category=Category.CORRECTNESS)

        # Diagnostic with wrong rule_id and category
        wrong_diag = Diagnostic(
            rule_id="WRONG",
            severity=Severity.ERROR,
            message="Test",
            file_path="features/test.feature",
            line=1,
            category=Category.STYLE,
        )
        rule_class = _make_rule_class(metadata, diagnostics=[wrong_diag])
        registry.register(rule_class)

        executor = RuleExecutor(registry, Config())
        results, _fixes = executor.execute([FakeFeature()])

        assert len(results) == 1
        assert results[0].rule_id == "BC001"
        assert results[0].category == Category.CORRECTNESS

    def test_execute_empty_features(self) -> None:
        registry = RuleRegistry()
        metadata = _make_metadata()
        registry.register(_make_rule_class(metadata))

        executor = RuleExecutor(registry, Config())
        results, _fixes = executor.execute([])

        assert results == []

    def test_execute_no_enabled_rules(self) -> None:
        registry = RuleRegistry()
        metadata = _make_metadata()
        registry.register(_make_rule_class(metadata))

        config = Config(ignore=["BC001"])
        executor = RuleExecutor(registry, config)
        results, _fixes = executor.execute([FakeFeature()])

        assert results == []

    def test_execute_severity_override(self) -> None:
        registry = RuleRegistry()
        metadata = _make_metadata(severity=Severity.ERROR)
        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="Test",
            file_path="features/test.feature",
            line=1,
            category=Category.CORRECTNESS,
        )
        registry.register(_make_rule_class(metadata, diagnostics=[diag]))

        config = Config(severity_overrides={"BC001": Severity.WARNING})
        executor = RuleExecutor(registry, config)
        results, _fixes = executor.execute([FakeFeature()])

        assert len(results) == 1
        assert results[0].severity == Severity.WARNING

    def test_execute_deprecated_rule_warns(self) -> None:
        registry = RuleRegistry()
        metadata = _make_metadata(deprecated=True, replaced_by="BC002")
        registry.register(_make_rule_class(metadata))

        config = Config(select=["BC001"])
        executor = RuleExecutor(registry, config)
        with (
            pytest.warns(DeprecationWarning, match="deprecated"),
            warnings.catch_warnings(),
        ):
            warnings.simplefilter("ignore", UserWarning)
            results, _fixes = executor.execute([FakeFeature()])

        assert results == []

    def test_execute_returns_empty_when_check_returns_none(self) -> None:
        registry = RuleRegistry()
        metadata = _make_metadata()

        class NoneRule(Rule):
            pass

        NoneRule.metadata = metadata

        def check(self: Rule, feature: Any, config: Config) -> list[Diagnostic]:
            return None  # type: ignore[return-value]

        NoneRule.check = check  # type: ignore[method-assign]
        registry.register(NoneRule)

        executor = RuleExecutor(registry, Config())
        results, _fixes = executor.execute([FakeFeature()])

        assert results == []

    def test_execute_instantiation_failure_isolated(self) -> None:
        registry = RuleRegistry()
        metadata = _make_metadata(rule_id="BC002", name="bad-init")

        class BadInitRule(Rule):
            pass

        BadInitRule.metadata = metadata

        def __init__(self: Rule) -> None:
            raise RuntimeError("Cannot init")

        BadInitRule.__init__ = __init__  # type: ignore[method-assign]
        registry.register(BadInitRule)

        # Also register a good rule
        good_metadata = _make_metadata(rule_id="BC001", name="good")
        good_diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="Good",
            file_path="features/test.feature",
            line=1,
            category=Category.CORRECTNESS,
        )
        registry.register(_make_rule_class(good_metadata, diagnostics=[good_diag]))

        executor = RuleExecutor(registry, Config())
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            results, _fixes = executor.execute([FakeFeature()])

        assert len(results) == 1
        assert results[0].rule_id == "BC001"
