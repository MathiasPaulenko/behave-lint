"""Unit tests for LintEngine (C03)."""

from __future__ import annotations

from pathlib import Path

from behave_lint.engine.lint_engine import LintEngine
from behave_lint.models.config import Config
from behave_lint.rules.registry import RuleRegistry


class TestLintEngine:
    """Tests for LintEngine pipeline."""

    def test_no_paths_returns_empty(self) -> None:
        config = Config()
        registry = RuleRegistry()
        engine = LintEngine(config, registry)
        result = engine.lint([])
        assert result.diagnostics == []
        assert result.summary.total_files == 0
        assert result.exit_code == 0

    def test_nonexistent_path_returns_empty(self) -> None:
        config = Config()
        registry = RuleRegistry()
        engine = LintEngine(config, registry)
        result = engine.lint(["nonexistent_xyz"])
        assert result.diagnostics == []
        assert result.summary.total_files == 0

    def test_valid_feature_no_rules(self, tmp_path: Path) -> None:
        feature = tmp_path / "test.feature"
        feature.write_text(
            "Feature: Test\n\n  Scenario: A scenario\n    Given a step\n",
            encoding="utf-8",
        )
        config = Config()
        registry = RuleRegistry()
        engine = LintEngine(config, registry)
        result = engine.lint([str(tmp_path)])
        assert result.summary.total_files == 1
        assert result.diagnostics == []
        assert result.exit_code == 0

    def test_parse_error_produces_diagnostic(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.feature"
        bad.write_text("This is not valid Gherkin at all\n", encoding="utf-8")
        config = Config()
        registry = RuleRegistry()
        engine = LintEngine(config, registry)
        result = engine.lint([str(bad)])
        assert result.summary.total_files == 1
        assert len(result.diagnostics) >= 1
        assert result.diagnostics[0].rule_id == "B000"
        assert result.diagnostics[0].severity.name == "ERROR"

    def test_multiple_files(self, tmp_path: Path) -> None:
        for i in range(3):
            f = tmp_path / f"f{i}.feature"
            f.write_text(
                f"Feature: F{i}\n\n  Scenario: S{i}\n    Given step\n",
                encoding="utf-8",
            )
        config = Config()
        registry = RuleRegistry()
        engine = LintEngine(config, registry)
        result = engine.lint([str(tmp_path)])
        assert result.summary.total_files == 3
        assert result.diagnostics == []

    def test_mixed_valid_and_invalid(self, tmp_path: Path) -> None:
        good = tmp_path / "good.feature"
        good.write_text(
            "Feature: Good\n\n  Scenario: S\n    Given step\n",
            encoding="utf-8",
        )
        bad = tmp_path / "bad.feature"
        bad.write_text("Not valid Gherkin\n", encoding="utf-8")
        config = Config()
        registry = RuleRegistry()
        engine = LintEngine(config, registry)
        result = engine.lint([str(tmp_path)])
        assert result.summary.total_files == 2
        assert len(result.diagnostics) == 1
        assert result.diagnostics[0].file_path.endswith("bad.feature")

    def test_summary_has_duration(self, tmp_path: Path) -> None:
        feature = tmp_path / "test.feature"
        feature.write_text(
            "Feature: Test\n\n  Scenario: S\n    Given step\n",
            encoding="utf-8",
        )
        config = Config()
        registry = RuleRegistry()
        engine = LintEngine(config, registry)
        result = engine.lint([str(feature)])
        assert result.summary.duration_ms >= 0.0

    def test_uses_config_paths_when_none_given(self, tmp_path: Path) -> None:
        feature = tmp_path / "test.feature"
        feature.write_text(
            "Feature: Test\n\n  Scenario: S\n    Given step\n",
            encoding="utf-8",
        )
        config = Config(paths=[str(tmp_path)])
        registry = RuleRegistry()
        engine = LintEngine(config, registry)
        result = engine.lint()
        assert result.summary.total_files == 1

    def test_exclude_patterns(self, tmp_path: Path) -> None:
        vendor = tmp_path / "vendor"
        vendor.mkdir()
        (vendor / "v.feature").write_text(
            "Feature: V\n\n  Scenario: S\n    Given step\n", encoding="utf-8"
        )
        (tmp_path / "main.feature").write_text(
            "Feature: M\n\n  Scenario: S\n    Given step\n", encoding="utf-8"
        )
        config = Config()
        registry = RuleRegistry()
        engine = LintEngine(config, registry)
        result = engine.lint([str(tmp_path)], exclude=["**/vendor/**"])
        assert result.summary.total_files == 1
