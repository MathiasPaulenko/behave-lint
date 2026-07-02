"""Unit tests for the DiagnosticFactory."""

from __future__ import annotations

from behave_lint.models.enums import Category, Severity
from behave_lint.rules.diagnostic_factory import DiagnosticFactory


class FakeNode:
    """Fake behave-model node for testing."""

    def __init__(
        self,
        file_path: str = "features/test.feature",
        line: int = 10,
        column: int | None = 3,
    ) -> None:
        self.file_path = file_path
        self.line = line
        self.column = column


class TestDiagnosticFactory:
    """Tests for DiagnosticFactory."""

    def test_create_with_node(self) -> None:
        factory = DiagnosticFactory(
            rule_id="BC001",
            category=Category.CORRECTNESS,
            severity=Severity.ERROR,
        )
        node = FakeNode()
        diag = factory.create("Duplicate scenario", node=node)

        assert diag.rule_id == "BC001"
        assert diag.severity == Severity.ERROR
        assert diag.category == Category.CORRECTNESS
        assert diag.message == "Duplicate scenario"
        assert diag.file_path == "features/test.feature"
        assert diag.line == 10
        assert diag.column == 3

    def test_create_without_node(self) -> None:
        factory = DiagnosticFactory(
            rule_id="BS001",
            category=Category.STYLE,
            severity=Severity.WARNING,
            file_path="features/login.feature",
        )
        diag = factory.create("Bad formatting", line=5)

        assert diag.rule_id == "BS001"
        assert diag.severity == Severity.WARNING
        assert diag.file_path == "features/login.feature"
        assert diag.line == 5
        assert diag.column is None

    def test_create_explicit_overrides_node(self) -> None:
        factory = DiagnosticFactory(
            rule_id="BC001",
            category=Category.CORRECTNESS,
            severity=Severity.ERROR,
        )
        node = FakeNode(file_path="features/a.feature", line=20)
        diag = factory.create(
            "Issue",
            node=node,
            file_path="features/b.feature",
            line=30,
            column=5,
        )

        assert diag.file_path == "features/b.feature"
        assert diag.line == 30
        assert diag.column == 5

    def test_create_with_suggestion_and_doc_url(self) -> None:
        factory = DiagnosticFactory(
            rule_id="BC001",
            category=Category.CORRECTNESS,
            severity=Severity.ERROR,
        )
        diag = factory.create(
            "Duplicate name",
            line=1,
            file_path="test.feature",
            suggestion="Rename to be unique.",
            doc_url="https://example.com/rules/BC001",
        )

        assert diag.suggestion == "Rename to be unique."
        assert diag.doc_url == "https://example.com/rules/BC001"

    def test_create_uses_factory_file_path_when_no_node(self) -> None:
        factory = DiagnosticFactory(
            rule_id="BC001",
            category=Category.CORRECTNESS,
            severity=Severity.ERROR,
            file_path="features/default.feature",
        )
        diag = factory.create("Issue", line=1)

        assert diag.file_path == "features/default.feature"

    def test_create_node_without_file_path_uses_factory(self) -> None:
        factory = DiagnosticFactory(
            rule_id="BC001",
            category=Category.CORRECTNESS,
            severity=Severity.ERROR,
            file_path="features/fallback.feature",
        )

        class NodeNoPath:
            line = 5
            file_path = ""  # empty

        diag = factory.create("Issue", node=NodeNoPath())

        assert diag.file_path == "features/fallback.feature"
        assert diag.line == 5

    def test_create_with_end_line_and_end_column(self) -> None:
        factory = DiagnosticFactory(
            rule_id="BC001",
            category=Category.CORRECTNESS,
            severity=Severity.ERROR,
        )
        diag = factory.create(
            "Multi-line issue",
            line=10,
            column=3,
            file_path="test.feature",
            end_line=12,
            end_column=20,
        )

        assert diag.end_line == 12
        assert diag.end_column == 20
