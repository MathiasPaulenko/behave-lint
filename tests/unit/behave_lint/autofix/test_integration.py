"""Integration tests for auto-fix CLI workflow."""

from __future__ import annotations

from pathlib import Path

import pytest

from behave_lint.autofix.coordinator import FixCoordinator
from behave_lint.autofix.models import FixEdit
from behave_lint.cli.coordinator import main
from behave_lint.models.config import Config
from behave_lint.models.enums import AutoFixCapability
from behave_lint.rules.base import Rule


@pytest.fixture
def feature_file(tmp_path: Path) -> Path:
    """Create a .feature file with trailing punctuation."""
    f = tmp_path / "test.feature"
    f.write_text(
        "Feature: Test\n\n"
        "  Scenario: Test scenario\n"
        "    Given a user.\n"
        "    When I click submit.\n"
        "    Then I see results.\n",
        encoding="utf-8",
    )
    return f


@pytest.fixture
def tag_file(tmp_path: Path) -> Path:
    """Create a .feature file with bad tag casing."""
    f = tmp_path / "tags.feature"
    f.write_text(
        "@SmokeTest\nFeature: Test\n\n  Scenario: Test scenario\n    Given a step\n",
        encoding="utf-8",
    )
    return f


@pytest.fixture
def invalid_tag_file(tmp_path: Path) -> Path:
    """Create a .feature file with invalid tag syntax (dash not allowed)."""
    f = tmp_path / "invalid_tags.feature"
    f.write_text(
        "@smoke-test\nFeature: Test\n\n  Scenario: Test scenario\n    Given a step\n",
        encoding="utf-8",
    )
    return f


@pytest.fixture
def mixed_param_file(tmp_path: Path) -> Path:
    """Create a .feature file mixing {param} and <param> conventions."""
    f = tmp_path / "mixed_params.feature"
    f.write_text(
        "Feature: Test\n\n"
        "  Scenario Outline: Test <value>\n"
        "    Given a <value> with {count} items\n"
        "    Then it is processed\n\n"
        "    Examples:\n"
        "      | value | count |\n"
        "      | box   | 3     |\n",
        encoding="utf-8",
    )
    return f


class TestCLIFixIntegration:
    """End-to-end tests for --fix CLI flag."""

    def test_fix_applies_safe_fixes(
        self, feature_file: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        exit_code = main(["--fix", str(feature_file)])
        # Exit code may be non-zero due to remaining diagnostics
        assert exit_code != 2

        content = feature_file.read_text(encoding="utf-8")
        assert "Given a user." not in content
        assert "Given a user" in content
        assert "When I click submit" in content
        assert "Then I see results" in content

    def test_fix_reports_applied_count(
        self, feature_file: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        main(["--fix", str(feature_file)])
        captured = capsys.readouterr()
        assert "Applied" in captured.err

    def test_no_fix_flag_does_not_modify_file(self, feature_file: Path) -> None:
        original = feature_file.read_text(encoding="utf-8")
        main([str(feature_file)])
        assert feature_file.read_text(encoding="utf-8") == original

    def test_fix_tag_casing(self, tag_file: Path) -> None:
        main(["--fix", str(tag_file)])
        content = tag_file.read_text(encoding="utf-8")
        assert "@smoke_test" in content
        assert "@SmokeTest" not in content

    def test_fix_invalid_tag_syntax(self, invalid_tag_file: Path) -> None:
        main(["--fix", str(invalid_tag_file)])
        content = invalid_tag_file.read_text(encoding="utf-8")
        assert "@smoke_test" in content
        assert "@smoke-test" not in content

    def test_fix_mixed_param_convention(self, mixed_param_file: Path) -> None:
        main(["--fix", str(mixed_param_file)])
        content = mixed_param_file.read_text(encoding="utf-8")
        assert "<count>" in content
        assert "{count}" not in content


class TestFixCoordinatorIntegration:
    """Direct tests for FixCoordinator with real edits."""

    def test_apply_safe_edits(self, feature_file: Path) -> None:
        lines = feature_file.read_text(encoding="utf-8").splitlines(keepends=True)
        edits = [
            FixEdit(
                file_path=str(feature_file),
                start_line=4,
                end_line=4,
                old_text=lines[3],
                new_text=lines[3].rstrip(".\r\n") + "\n",
                safety=AutoFixCapability.SAFE,
                rule_id="BD005",
                diagnostic_line=4,
            ),
        ]

        coord = FixCoordinator(allow_unsafe=False, dry_run=False)
        result = coord.apply_edits(edits)

        assert result.applied_count == 1
        assert result.failed_count == 0
        assert str(feature_file) in result.files_modified

    def test_unsafe_edits_skipped_without_flag(self, feature_file: Path) -> None:
        lines = feature_file.read_text(encoding="utf-8").splitlines(keepends=True)
        edits = [
            FixEdit(
                file_path=str(feature_file),
                start_line=4,
                end_line=4,
                old_text=lines[3],
                new_text=lines[3].rstrip(".\r\n") + "\n",
                safety=AutoFixCapability.UNSAFE,
                rule_id="BD005",
                diagnostic_line=4,
            ),
        ]

        coord = FixCoordinator(allow_unsafe=False, dry_run=False)
        result = coord.apply_edits(edits)

        assert result.applied_count == 0

    def test_unsafe_edits_applied_with_flag(self, feature_file: Path) -> None:
        lines = feature_file.read_text(encoding="utf-8").splitlines(keepends=True)
        edits = [
            FixEdit(
                file_path=str(feature_file),
                start_line=4,
                end_line=4,
                old_text=lines[3],
                new_text=lines[3].rstrip(".\r\n") + "\n",
                safety=AutoFixCapability.UNSAFE,
                rule_id="BD005",
                diagnostic_line=4,
            ),
        ]

        coord = FixCoordinator(allow_unsafe=True, dry_run=False)
        result = coord.apply_edits(edits)

        assert result.applied_count == 1

    def test_conflicting_edits_resolved(self, feature_file: Path) -> None:
        lines = feature_file.read_text(encoding="utf-8").splitlines(keepends=True)
        edits = [
            FixEdit(
                file_path=str(feature_file),
                start_line=4,
                end_line=4,
                old_text=lines[3],
                new_text="    Given a user\n",
                safety=AutoFixCapability.SAFE,
                rule_id="BD005",
                diagnostic_line=4,
            ),
            FixEdit(
                file_path=str(feature_file),
                start_line=4,
                end_line=4,
                old_text=lines[3],
                new_text="    Given a different user\n",
                safety=AutoFixCapability.SAFE,
                rule_id="BX001",
                diagnostic_line=4,
            ),
        ]

        coord = FixCoordinator(allow_unsafe=False, dry_run=False)
        result = coord.apply_edits(edits)

        assert result.applied_count == 1
        assert result.skipped_count == 1


class TestRuleGetFixes:
    """Test that rules produce correct FixEdit objects."""

    def test_bd005_get_fixes_returns_edits(self, feature_file: Path) -> None:
        from behave_lint.infrastructure.project_loader import load_features
        from behave_lint.rules.builtin.step_definitions import (
            StepTrailingPunctuationRule,
        )

        load_result = load_features([str(feature_file)])
        assert len(load_result.features) == 1

        feature = load_result.features[0]
        rule = StepTrailingPunctuationRule()
        config = Config()
        diagnostics = rule.check(feature, config)
        assert len(diagnostics) == 3

        fixes = rule.get_fixes(feature, config, diagnostics)
        assert len(fixes) == 3
        assert all(f.safety == AutoFixCapability.SAFE for f in fixes)
        assert all(f.rule_id == "BD005" for f in fixes)

    def test_bs001_get_fixes_returns_edits(self, tag_file: Path) -> None:
        from behave_lint.infrastructure.project_loader import load_features
        from behave_lint.rules.builtin.style import TagCasingRule

        load_result = load_features([str(tag_file)])
        assert len(load_result.features) == 1

        feature = load_result.features[0]
        rule = TagCasingRule()
        config = Config()
        diagnostics = rule.check(feature, config)
        assert len(diagnostics) >= 1

        fixes = rule.get_fixes(feature, config, diagnostics)
        assert len(fixes) >= 1
        assert all(f.safety == AutoFixCapability.SAFE for f in fixes)
        assert all(f.rule_id == "BS001" for f in fixes)

    def test_bc004_get_fixes_returns_edits(self, invalid_tag_file: Path) -> None:
        from behave_lint.infrastructure.project_loader import load_features
        from behave_lint.rules.builtin.correctness import InvalidTagSyntaxRule

        load_result = load_features([str(invalid_tag_file)])
        assert len(load_result.features) == 1

        feature = load_result.features[0]
        rule = InvalidTagSyntaxRule()
        config = Config()
        diagnostics = rule.check(feature, config)
        assert len(diagnostics) >= 1

        fixes = rule.get_fixes(feature, config, diagnostics)
        assert len(fixes) >= 1
        assert all(f.safety == AutoFixCapability.SAFE for f in fixes)
        assert all(f.rule_id == "BC004" for f in fixes)

    def test_bd004_get_fixes_returns_edits(self, mixed_param_file: Path) -> None:
        from behave_lint.infrastructure.project_loader import load_features
        from behave_lint.rules.builtin.step_definitions import (
            StepParameterConventionRule,
        )

        load_result = load_features([str(mixed_param_file)])
        assert len(load_result.features) == 1

        feature = load_result.features[0]
        rule = StepParameterConventionRule()
        config = Config()
        diagnostics = rule.check(feature, config)
        assert len(diagnostics) >= 1

        fixes = rule.get_fixes(feature, config, diagnostics)
        assert len(fixes) >= 1
        assert all(f.safety == AutoFixCapability.SAFE for f in fixes)
        assert all(f.rule_id == "BD004" for f in fixes)

    def test_default_get_fixes_returns_empty(self) -> None:
        """Base Rule.get_fixes() should return empty list by default."""

        class DummyRule(Rule):
            pass

        rule = DummyRule()
        assert rule.get_fixes(None, Config(), []) == []
