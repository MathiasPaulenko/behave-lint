"""Unit tests for diagnostic sorting.

See DIAGNOSTIC_ENGINE.md Section 9.
"""

from __future__ import annotations

from behave_lint.diagnostics.sorting import sort_diagnostics
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity


def _make_diag(**overrides: object) -> Diagnostic:
    defaults: dict[str, object] = {
        "rule_id": "BC001",
        "severity": Severity.ERROR,
        "message": "Issue",
        "file_path": "features/a.feature",
        "line": 10,
        "category": Category.CORRECTNESS,
    }
    defaults.update(overrides)
    return Diagnostic(**defaults)  # type: ignore[arg-type]


class TestSortDiagnostics:
    """Tests for sort_diagnostics()."""

    def test_sort_by_file_path(self) -> None:
        diags = [
            _make_diag(file_path="features/b.feature"),
            _make_diag(file_path="features/a.feature"),
        ]
        result = sort_diagnostics(diags)
        assert result[0].file_path == "features/a.feature"
        assert result[1].file_path == "features/b.feature"

    def test_sort_by_line(self) -> None:
        diags = [
            _make_diag(line=20),
            _make_diag(line=5),
        ]
        result = sort_diagnostics(diags)
        assert result[0].line == 5
        assert result[1].line == 20

    def test_sort_by_column(self) -> None:
        diags = [
            _make_diag(column=10),
            _make_diag(column=3),
        ]
        result = sort_diagnostics(diags)
        assert result[0].column == 3
        assert result[1].column == 10

    def test_none_column_sorts_first(self) -> None:
        diags = [
            _make_diag(column=5),
            _make_diag(column=None),
        ]
        result = sort_diagnostics(diags)
        assert result[0].column is None
        assert result[1].column == 5

    def test_sort_by_rule_id_tiebreaker(self) -> None:
        diags = [
            _make_diag(rule_id="BS001"),
            _make_diag(rule_id="BC001"),
        ]
        result = sort_diagnostics(diags)
        assert result[0].rule_id == "BC001"
        assert result[1].rule_id == "BS001"

    def test_full_sort(self) -> None:
        diags = [
            _make_diag(file_path="features/b.feature", line=5, rule_id="BC001"),
            _make_diag(file_path="features/a.feature", line=20, rule_id="BC001"),
            _make_diag(file_path="features/a.feature", line=5, rule_id="BS001"),
            _make_diag(file_path="features/a.feature", line=5, rule_id="BC001"),
        ]
        result = sort_diagnostics(diags)
        assert result[0].file_path == "features/a.feature"
        assert result[0].line == 5
        assert result[0].rule_id == "BC001"
        assert result[1].file_path == "features/a.feature"
        assert result[1].line == 5
        assert result[1].rule_id == "BS001"
        assert result[2].file_path == "features/a.feature"
        assert result[2].line == 20
        assert result[3].file_path == "features/b.feature"

    def test_empty_list(self) -> None:
        result = sort_diagnostics([])
        assert result == []

    def test_single_diagnostic(self) -> None:
        diags = [_make_diag()]
        result = sort_diagnostics(diags)
        assert len(result) == 1

    def test_deterministic(self) -> None:
        diags = [
            _make_diag(file_path="features/a.feature", line=5, rule_id="BC001"),
            _make_diag(file_path="features/a.feature", line=5, rule_id="BS001"),
        ]
        result1 = sort_diagnostics(diags)
        result2 = sort_diagnostics(list(reversed(diags)))
        assert result1 == result2
