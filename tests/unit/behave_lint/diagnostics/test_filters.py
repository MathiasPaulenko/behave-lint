"""Unit tests for diagnostic filters.

See DIAGNOSTIC_ENGINE.md Section 8.
"""

from __future__ import annotations

from behave_lint.diagnostics.filters import (
    DisableRegion,
    filter_by_severity,
    filter_disabled_rules,
    filter_excluded_files,
    filter_inline_disables,
    parse_disable_comments,
)
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


class TestFilterBySeverity:
    """Tests for filter_by_severity()."""

    def test_removes_off(self) -> None:
        diags = [_make_diag(severity=Severity.OFF), _make_diag()]
        result = filter_by_severity(diags)
        assert len(result) == 1
        assert result[0].severity is Severity.ERROR

    def test_min_info_keeps_all_non_off(self) -> None:
        diags = [
            _make_diag(severity=Severity.ERROR),
            _make_diag(severity=Severity.WARNING, rule_id="BS001"),
            _make_diag(severity=Severity.INFO, rule_id="BX001"),
            _make_diag(severity=Severity.OFF, rule_id="BP001"),
        ]
        result = filter_by_severity(diags, min_severity=Severity.INFO)
        assert len(result) == 3

    def test_min_warning(self) -> None:
        diags = [
            _make_diag(severity=Severity.ERROR),
            _make_diag(severity=Severity.WARNING, rule_id="BS001"),
            _make_diag(severity=Severity.INFO, rule_id="BX001"),
        ]
        result = filter_by_severity(diags, min_severity=Severity.WARNING)
        assert len(result) == 2
        severities = {d.severity for d in result}
        assert Severity.INFO not in severities

    def test_min_error(self) -> None:
        diags = [
            _make_diag(severity=Severity.ERROR),
            _make_diag(severity=Severity.WARNING, rule_id="BS001"),
        ]
        result = filter_by_severity(diags, min_severity=Severity.ERROR)
        assert len(result) == 1
        assert result[0].severity is Severity.ERROR

    def test_empty_list(self) -> None:
        result = filter_by_severity([])
        assert result == []


class TestFilterDisabledRules:
    """Tests for filter_disabled_rules()."""

    def test_keeps_enabled(self) -> None:
        config = Config()
        diags = [_make_diag()]
        result = filter_disabled_rules(diags, config)
        assert len(result) == 1

    def test_removes_ignored(self) -> None:
        config = Config(ignore=["BC001"])
        diags = [_make_diag()]
        result = filter_disabled_rules(diags, config)
        assert len(result) == 0

    def test_keeps_selected(self) -> None:
        config = Config(select=["BC001"])
        diags = [_make_diag(), _make_diag(rule_id="BS001")]
        result = filter_disabled_rules(diags, config)
        assert len(result) == 1
        assert result[0].rule_id == "BC001"

    def test_removes_non_selected(self) -> None:
        config = Config(select=["BS001"])
        diags = [_make_diag()]
        result = filter_disabled_rules(diags, config)
        assert len(result) == 0


class TestFilterExcludedFiles:
    """Tests for filter_excluded_files()."""

    def test_no_patterns(self) -> None:
        diags = [_make_diag()]
        result = filter_excluded_files(diags, [])
        assert len(result) == 1

    def test_exact_match(self) -> None:
        diags = [_make_diag(file_path="features/legacy/login.feature")]
        result = filter_excluded_files(diags, ["features/legacy/login.feature"])
        assert len(result) == 0

    def test_glob_match(self) -> None:
        diags = [
            _make_diag(file_path="features/legacy/login.feature"),
            _make_diag(file_path="features/login.feature", rule_id="BS001"),
        ]
        result = filter_excluded_files(diags, ["features/legacy/**"])
        assert len(result) == 1
        assert result[0].file_path == "features/login.feature"

    def test_wildcard_match(self) -> None:
        diags = [
            _make_diag(file_path="features/wip.feature"),
            _make_diag(file_path="features/login.feature", rule_id="BS001"),
        ]
        result = filter_excluded_files(diags, ["**/wip.feature"])
        assert len(result) == 1
        assert result[0].file_path == "features/login.feature"


class TestParseDisableComments:
    """Tests for parse_disable_comments()."""

    def test_no_comments(self) -> None:
        lines = ["Feature: Test", "  Scenario: Foo"]
        regions = parse_disable_comments(lines)
        assert regions == []

    def test_off_all(self) -> None:
        lines = [
            "# behave-lint: off",
            "Feature: Test",
            "  Scenario: Foo",
            "# behave-lint: on",
        ]
        regions = parse_disable_comments(lines)
        assert len(regions) == 1
        assert regions[0].start_line == 1
        assert regions[0].end_line == 4
        assert regions[0].rule_ids == frozenset()

    def test_off_specific_rule(self) -> None:
        lines = [
            "# behave-lint: off BC001",
            "Feature: Test",
            "# behave-lint: on BC001",
        ]
        regions = parse_disable_comments(lines)
        assert len(regions) == 1
        assert regions[0].rule_ids == frozenset({"BC001"})

    def test_off_multiple_rules(self) -> None:
        lines = [
            "# behave-lint: off BC001,BS001",
            "Feature: Test",
            "# behave-lint: on BC001,BS001",
        ]
        regions = parse_disable_comments(lines)
        assert len(regions) == 1
        assert regions[0].rule_ids == frozenset({"BC001", "BS001"})

    def test_unclosed_disable(self) -> None:
        lines = ["# behave-lint: off", "Feature: Test"]
        regions = parse_disable_comments(lines)
        assert len(regions) == 1
        assert regions[0].start_line == 1
        assert regions[0].end_line is None


class TestDisableRegion:
    """Tests for DisableRegion.is_disabled()."""

    def test_within_region_all_rules(self) -> None:
        region = DisableRegion(start_line=1, end_line=10)
        assert region.is_disabled("BC001", 5) is True

    def test_outside_region_before(self) -> None:
        region = DisableRegion(start_line=5, end_line=10)
        assert region.is_disabled("BC001", 3) is False

    def test_outside_region_after(self) -> None:
        region = DisableRegion(start_line=1, end_line=10)
        assert region.is_disabled("BC001", 15) is False

    def test_specific_rule_disabled(self) -> None:
        region = DisableRegion(start_line=1, end_line=10, rule_ids=frozenset({"BC001"}))
        assert region.is_disabled("BC001", 5) is True
        assert region.is_disabled("BS001", 5) is False

    def test_unclosed_region(self) -> None:
        region = DisableRegion(
            start_line=1, end_line=None, rule_ids=frozenset({"BC001"})
        )
        assert region.is_disabled("BC001", 100) is True


class TestFilterInlineDisables:
    """Tests for filter_inline_disables()."""

    def test_suppressed_diagnostic_removed(self) -> None:
        diags = [_make_diag(line=3)]
        file_contents = {
            "features/login.feature": [
                "# behave-lint: off BC001",
                "Feature: Test",
                "  Scenario: Foo",
                "# behave-lint: on BC001",
            ]
        }
        result = filter_inline_disables(diags, file_contents)
        assert len(result) == 0

    def test_non_suppressed_kept(self) -> None:
        diags = [_make_diag(line=10)]
        file_contents = {
            "features/login.feature": [
                "# behave-lint: off BC001",
                "Feature: Test",
                "# behave-lint: on BC001",
                "  Scenario: Foo",
            ]
        }
        result = filter_inline_disables(diags, file_contents)
        assert len(result) == 1

    def test_different_rule_not_suppressed(self) -> None:
        diags = [_make_diag(rule_id="BS001", line=3)]
        file_contents = {
            "features/login.feature": [
                "# behave-lint: off BC001",
                "Feature: Test",
                "  Scenario: Foo",
                "# behave-lint: on BC001",
            ]
        }
        result = filter_inline_disables(diags, file_contents)
        assert len(result) == 1

    def test_no_file_contents(self) -> None:
        diags = [_make_diag()]
        result = filter_inline_disables(diags, {})
        assert len(result) == 1
