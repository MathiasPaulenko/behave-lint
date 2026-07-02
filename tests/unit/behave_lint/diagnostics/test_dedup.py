"""Unit tests for diagnostic deduplication.

See DIAGNOSTIC_ENGINE.md Section 8.
"""

from __future__ import annotations

from behave_lint.diagnostics.dedup import deduplicate_diagnostics
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity


def _make_diag(**overrides: object) -> Diagnostic:
    defaults: dict[str, object] = {
        "rule_id": "BC001",
        "severity": Severity.ERROR,
        "message": "Duplicate scenario name",
        "file_path": "features/login.feature",
        "line": 15,
        "category": Category.CORRECTNESS,
    }
    defaults.update(overrides)
    return Diagnostic(**defaults)  # type: ignore[arg-type]


class TestDeduplicateDiagnostics:
    """Tests for deduplicate_diagnostics()."""

    def test_no_duplicates(self) -> None:
        diags = [_make_diag(), _make_diag(rule_id="BS001")]
        result = deduplicate_diagnostics(diags)
        assert len(result) == 2

    def test_exact_duplicate_removed(self) -> None:
        d = _make_diag()
        diags = [d, d]
        result = deduplicate_diagnostics(diags)
        assert len(result) == 1

    def test_same_key_different_object_removed(self) -> None:
        diags = [_make_diag(), _make_diag()]
        result = deduplicate_diagnostics(diags)
        assert len(result) == 1

    def test_different_message_kept(self) -> None:
        diags = [
            _make_diag(message="Issue A"),
            _make_diag(message="Issue B"),
        ]
        result = deduplicate_diagnostics(diags)
        assert len(result) == 2

    def test_different_line_kept(self) -> None:
        diags = [
            _make_diag(line=10),
            _make_diag(line=20),
        ]
        result = deduplicate_diagnostics(diags)
        assert len(result) == 2

    def test_different_rule_id_kept(self) -> None:
        diags = [_make_diag(), _make_diag(rule_id="BS001")]
        result = deduplicate_diagnostics(diags)
        assert len(result) == 2

    def test_different_column_kept(self) -> None:
        diags = [
            _make_diag(column=1),
            _make_diag(column=5),
        ]
        result = deduplicate_diagnostics(diags)
        assert len(result) == 2

    def test_preserves_first_occurrence(self) -> None:
        diags = [
            _make_diag(message="First"),
            _make_diag(message="First"),
        ]
        result = deduplicate_diagnostics(diags)
        assert len(result) == 1
        assert result[0].message == "First"

    def test_empty_list(self) -> None:
        result = deduplicate_diagnostics([])
        assert result == []
