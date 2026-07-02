"""Unit tests for the command router."""

from __future__ import annotations

from behave_lint.cli.parser import CLIArgs
from behave_lint.cli.router import route_command
from behave_lint.models.enums import Category, Severity
from behave_lint.models.rule_metadata import RuleMetadata


class FakeRegistry:
    """Fake registry for testing."""

    def __init__(
        self,
        rules: list[tuple[type, RuleMetadata, str]] | None = None,
    ) -> None:
        self._rules = rules or []

    def get_all(self) -> list[tuple[type, RuleMetadata, str]]:
        return list(self._rules)

    def get(self, rule_id: str) -> tuple[type, RuleMetadata, str] | None:
        for rule_class, metadata, source in self._rules:
            if metadata.rule_id == rule_id:
                return rule_class, metadata, source
        return None


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
        description="A test rule for unit testing.",
        category=category,
        default_severity=severity,
        motivation="To ensure correctness.",
        since="0.1.0",
    )


class TestRouteCommand:
    """Tests for route_command."""

    def test_list_rules_returns_zero(self, capsys) -> None:  # type: ignore[no-untyped-def]
        registry = FakeRegistry(
            [
                (type("R", (), {}), _make_metadata("BC001", "rule-one"), "built-in"),
                (type("R", (), {}), _make_metadata("BS001", "rule-two"), "built-in"),
            ]
        )
        args = CLIArgs(list_rules=True)

        exit_code = route_command(args, registry)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "BC001" in captured.out
        assert "BS001" in captured.out

    def test_list_rules_empty_registry(self, capsys) -> None:  # type: ignore[no-untyped-def]
        registry = FakeRegistry([])
        args = CLIArgs(list_rules=True)

        exit_code = route_command(args, registry)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "No rules" in captured.out

    def test_explain_existing_rule(self, capsys) -> None:  # type: ignore[no-untyped-def]
        metadata = _make_metadata("BC001", "test-rule")
        registry = FakeRegistry([(type("R", (), {}), metadata, "built-in")])
        args = CLIArgs(explain="BC001")

        exit_code = route_command(args, registry)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "BC001" in captured.out
        assert "Test Rule" in captured.out
        assert "correctness" in captured.out

    def test_explain_unknown_rule(self, capsys) -> None:  # type: ignore[no-untyped-def]
        registry = FakeRegistry()
        args = CLIArgs(explain="UNKNOWN001")

        exit_code = route_command(args, registry)

        assert exit_code == 2
        captured = capsys.readouterr()
        assert "Unknown rule ID" in captured.out

    def test_lint_command_returns_sentinel(self) -> None:
        registry = FakeRegistry()
        args = CLIArgs(paths=["features/"])

        exit_code = route_command(args, registry)

        assert exit_code == -1

    def test_explain_shows_deprecated_info(self, capsys) -> None:  # type: ignore[no-untyped-def]
        metadata = RuleMetadata(
            rule_id="BC001",
            name="old-rule",
            title="Old Rule",
            description="A deprecated rule.",
            category=Category.CORRECTNESS,
            default_severity=Severity.WARNING,
            motivation="Historical reasons.",
            since="0.1.0",
            deprecated=True,
            replaced_by="BC002",
            deprecated_version="1.0.0",
        )
        registry = FakeRegistry([(type("R", (), {}), metadata, "built-in")])
        args = CLIArgs(explain="BC001")

        exit_code = route_command(args, registry)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Deprecated" in captured.out
        assert "BC002" in captured.out
