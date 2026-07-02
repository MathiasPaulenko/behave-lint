"""Unit tests for DiagnosticCollector pipeline.

See DIAGNOSTIC_ENGINE.md Section 2 and COMPONENT_DESIGN.md C07.
"""

from __future__ import annotations

import warnings

from behave_lint.diagnostics.collector import DiagnosticCollector
from behave_lint.models.config import Config
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


class TestDiagnosticCollector:
    """Tests for DiagnosticCollector."""

    def test_empty_collect(self) -> None:
        config = Config()
        collector = DiagnosticCollector(config)
        result = collector.collect()
        assert result == []

    def test_collect_valid_diagnostics(self) -> None:
        config = Config()
        collector = DiagnosticCollector(config)
        collector.add_diagnostics([_make_diag(), _make_diag(rule_id="BS001")])
        result = collector.collect()
        assert len(result) == 2

    def test_collect_filters_invalid(self) -> None:
        config = Config()
        collector = DiagnosticCollector(config)
        collector.add_diagnostics(
            [
                _make_diag(),
                _make_diag(rule_id=""),
            ]
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = collector.collect()
        assert len(result) == 1
        assert result[0].rule_id == "BC001"

    def test_collect_filters_off_severity(self) -> None:
        config = Config()
        collector = DiagnosticCollector(config)
        collector.add_diagnostics(
            [
                _make_diag(),
                _make_diag(severity=Severity.OFF, rule_id="BP001"),
            ]
        )
        result = collector.collect()
        assert len(result) == 1

    def test_collect_filters_disabled_rules(self) -> None:
        config = Config(ignore=["BC001"])
        collector = DiagnosticCollector(config)
        collector.add_diagnostics([_make_diag()])
        result = collector.collect()
        assert len(result) == 0

    def test_collect_deduplicates(self) -> None:
        config = Config()
        collector = DiagnosticCollector(config)
        collector.add_diagnostics([_make_diag(), _make_diag()])
        result = collector.collect()
        assert len(result) == 1

    def test_collect_sorts(self) -> None:
        config = Config()
        collector = DiagnosticCollector(config)
        collector.add_diagnostics(
            [
                _make_diag(file_path="features/b.feature", line=20),
                _make_diag(file_path="features/a.feature", line=5, rule_id="BS001"),
                _make_diag(file_path="features/a.feature", line=5),
            ]
        )
        result = collector.collect()
        assert result[0].file_path == "features/a.feature"
        assert result[0].line == 5
        assert result[0].rule_id == "BC001"
        assert result[1].file_path == "features/a.feature"
        assert result[1].rule_id == "BS001"
        assert result[2].file_path == "features/b.feature"

    def test_collect_with_inline_disables(self) -> None:
        config = Config()
        collector = DiagnosticCollector(config)
        collector.add_diagnostics([_make_diag(line=3)])
        collector.add_file_contents(
            "features/login.feature",
            [
                "# behave-lint: off BC001",
                "Feature: Test",
                "  Scenario: Foo",
                "# behave-lint: on BC001",
            ],
        )
        result = collector.collect()
        assert len(result) == 0

    def test_collect_from_convenience(self) -> None:
        config = Config()
        collector = DiagnosticCollector(config)
        result = collector.collect_from([_make_diag(), _make_diag(rule_id="BS001")])
        assert len(result) == 2

    def test_full_pipeline(self) -> None:
        config = Config(select=["BC001", "BS001"])
        collector = DiagnosticCollector(config)
        collector.add_diagnostics(
            [
                _make_diag(file_path="features/b.feature", line=20),
                _make_diag(file_path="features/a.feature", line=5, rule_id="BS001"),
                _make_diag(file_path="features/a.feature", line=5),
                _make_diag(),  # duplicate of BC001 at features/login.feature:15
                _make_diag(rule_id="BP001", severity=Severity.OFF),
                _make_diag(rule_id="BX001"),  # not selected
                _make_diag(rule_id="", message=""),  # invalid
            ]
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = collector.collect()
        # After pipeline: invalid dropped, OFF dropped, BX001 not selected,
        # duplicate removed, sorted
        rule_ids = [d.rule_id for d in result]
        assert "BP001" not in rule_ids
        assert "BX001" not in rule_ids
        assert "" not in rule_ids
        assert len(result) == 4
        # Sorted: a.feature:5:BC001, a.feature:5:BS001,
        # b.feature:20:BC001, login.feature:15:BC001
        assert result[0].file_path == "features/a.feature"
        assert result[0].rule_id == "BC001"
        assert result[1].file_path == "features/a.feature"
        assert result[1].rule_id == "BS001"
        assert result[2].file_path == "features/b.feature"
        assert result[3].file_path == "features/login.feature"
