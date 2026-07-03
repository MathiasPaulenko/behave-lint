"""Functional tests for profiles — CLI + real .feature files.

Tests the full pipeline: CLI --profile flag → config resolution →
rule selection → lint execution → diagnostic output → exit code.

Verifies that profiles actually change which rules run against
real feature files.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from behave_lint.cli.coordinator import main
from behave_lint.cli.parser import app

runner = CliRunner()

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def feature_with_style_issue(tmp_path: Path) -> Path:
    """A feature file that triggers BS006 (trailing whitespace in step)."""
    feature = tmp_path / "style_issue.feature"
    feature.write_text(
        "Feature: Style Issue Feature\n"
        "  A feature with a style issue.\n\n"
        "  Scenario: Trailing whitespace\n"
        "    Given a step with trailing space   \n"
        "    Then another step\n",
        encoding="utf-8",
    )
    return feature


@pytest.fixture
def feature_with_pedantic_issue(tmp_path: Path) -> Path:
    """A feature file that triggers BP001 (no assertion in then step)."""
    feature = tmp_path / "pedantic_issue.feature"
    feature.write_text(
        "Feature: Pedantic Issue Feature\n"
        "  A feature with a pedantic issue.\n\n"
        "  Scenario: No assertion\n"
        "    Given a step\n"
        "    Then something happens\n",
        encoding="utf-8",
    )
    return feature


@pytest.fixture
def clean_feature(tmp_path: Path) -> Path:
    """A clean feature file that triggers no diagnostics."""
    feature = tmp_path / "clean.feature"
    feature.write_text(
        "Feature: Clean Feature\n"
        "  A clean feature for testing.\n\n"
        "  Scenario: A scenario\n"
        "    Given a step\n"
        "    Then another step\n",
        encoding="utf-8",
    )
    return feature


@pytest.fixture
def feature_with_correctness_issue(tmp_path: Path) -> Path:
    """A feature file that triggers BC001 (duplicate scenario names)."""
    feature = tmp_path / "correctness_issue.feature"
    feature.write_text(
        "Feature: Correctness Issue Feature\n"
        "  A feature with duplicate scenario names.\n\n"
        "  Scenario: Same Name\n"
        "    Given a step\n"
        "\n"
        "  Scenario: Same Name\n"
        "    Given another step\n",
        encoding="utf-8",
    )
    return feature


# ---------------------------------------------------------------------------
# CLI parser tests for --profile
# ---------------------------------------------------------------------------


class TestCLIProfileFlag:
    """Test that --profile flag is accepted by the CLI parser."""

    def test_profile_recommended_accepted(self) -> None:
        result = runner.invoke(app, ["--profile", "recommended", "features/"])
        assert result.exit_code == 0

    def test_profile_strict_accepted(self) -> None:
        result = runner.invoke(app, ["--profile", "strict", "features/"])
        assert result.exit_code == 0

    def test_profile_minimal_accepted(self) -> None:
        result = runner.invoke(app, ["--profile", "minimal", "features/"])
        assert result.exit_code == 0

    def test_profile_none_accepted(self) -> None:
        result = runner.invoke(app, ["--profile", "none", "features/"])
        assert result.exit_code == 0

    def test_profile_shown_in_help(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("NO_COLOR", "1")
        monkeypatch.setenv("TERM", "dumb")
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        output = _strip_ansi(result.output)
        assert "--profile" in output or "profile" in output.lower()

    def test_help_mentions_profile_options(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("NO_COLOR", "1")
        monkeypatch.setenv("TERM", "dumb")
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        output = _strip_ansi(result.output)
        assert "recommended" in output or "recommended" in _strip_ansi(result.stdout)
        assert "strict" in output or "strict" in _strip_ansi(result.stdout)
        assert "minimal" in output or "minimal" in _strip_ansi(result.stdout)

    def test_profile_option_exists_in_command_params(self) -> None:
        cmd = typer.main.get_command(app)
        opts = [p.name for p in cmd.params]
        assert "profile" in opts


# ---------------------------------------------------------------------------
# CLI coordinator tests for --profile
# ---------------------------------------------------------------------------


class TestCLIProfileCoordinator:
    """Test --profile through the coordinator main() function."""

    def test_profile_recommended_returns_zero(
        self, clean_feature: Path, capsys: object
    ) -> None:
        exit_code = main(["--profile", "recommended", str(clean_feature)])
        assert exit_code == 0

    def test_profile_strict_returns_zero(
        self, clean_feature: Path, capsys: object
    ) -> None:
        exit_code = main(["--profile", "strict", str(clean_feature)])
        assert exit_code == 0

    def test_profile_minimal_returns_zero(
        self, clean_feature: Path, capsys: object
    ) -> None:
        exit_code = main(["--profile", "minimal", str(clean_feature)])
        assert exit_code == 0

    def test_profile_with_json_output(
        self, clean_feature: Path, tmp_path: Path
    ) -> None:
        output_file = tmp_path / "output.json"
        exit_code = main(
            [
                "--profile",
                "recommended",
                "--output",
                "json",
                "--output-file",
                str(output_file),
                str(clean_feature),
            ]
        )
        assert exit_code == 0
        assert output_file.exists()
        data = json.loads(output_file.read_text(encoding="utf-8"))
        assert "diagnostics" in data
        assert "summary" in data


# ---------------------------------------------------------------------------
# Profile affects rule execution
# ---------------------------------------------------------------------------


class TestProfileRuleExecution:
    """Verify that profiles actually change which rules run."""

    def test_minimal_profile_does_not_trigger_style_rules(
        self, feature_with_style_issue: Path
    ) -> None:
        """BS006 (trailing whitespace) should NOT fire under minimal."""
        main(
            [
                "--profile",
                "minimal",
                "--output",
                "json",
                "--output-file",
                str(feature_with_style_issue.parent / "out.json"),
                str(feature_with_style_issue),
            ]
        )
        output_file = feature_with_style_issue.parent / "out.json"
        data = json.loads(output_file.read_text(encoding="utf-8"))
        diagnostics = data.get("diagnostics", [])
        bs_diags = [d for d in diagnostics if d.get("rule_id", "").startswith("BS")]
        assert bs_diags == []

    def test_recommended_profile_triggers_style_rules(
        self, feature_with_style_issue: Path
    ) -> None:
        """BS006 (trailing whitespace) SHOULD fire under recommended."""
        output_file = feature_with_style_issue.parent / "out_rec.json"
        main(
            [
                "--profile",
                "recommended",
                "--output",
                "json",
                "--output-file",
                str(output_file),
                str(feature_with_style_issue),
            ]
        )
        data = json.loads(output_file.read_text(encoding="utf-8"))
        diagnostics = data.get("diagnostics", [])
        bs_diags = [d for d in diagnostics if d.get("rule_id", "").startswith("BS")]
        assert len(bs_diags) > 0

    def test_recommended_profile_does_not_trigger_pedantic_rules(
        self, feature_with_pedantic_issue: Path
    ) -> None:
        """BP rules should NOT fire under recommended."""
        output_file = feature_with_pedantic_issue.parent / "out_rec_bp.json"
        main(
            [
                "--profile",
                "recommended",
                "--output",
                "json",
                "--output-file",
                str(output_file),
                str(feature_with_pedantic_issue),
            ]
        )
        data = json.loads(output_file.read_text(encoding="utf-8"))
        diagnostics = data.get("diagnostics", [])
        bp_diags = [d for d in diagnostics if d.get("rule_id", "").startswith("BP")]
        assert bp_diags == []

    def test_strict_profile_triggers_pedantic_rules(
        self, feature_with_pedantic_issue: Path
    ) -> None:
        """BP rules SHOULD fire under strict."""
        output_file = feature_with_pedantic_issue.parent / "out_strict_bp.json"
        main(
            [
                "--profile",
                "strict",
                "--output",
                "json",
                "--output-file",
                str(output_file),
                str(feature_with_pedantic_issue),
            ]
        )
        data = json.loads(output_file.read_text(encoding="utf-8"))
        diagnostics = data.get("diagnostics", [])
        bp_diags = [d for d in diagnostics if d.get("rule_id", "").startswith("BP")]
        assert len(bp_diags) > 0

    def test_minimal_profile_triggers_correctness_rules(
        self, feature_with_correctness_issue: Path
    ) -> None:
        """BC001 (duplicate scenario names) SHOULD fire under minimal."""
        output_file = feature_with_correctness_issue.parent / "out_min_bc.json"
        main(
            [
                "--profile",
                "minimal",
                "--output",
                "json",
                "--output-file",
                str(output_file),
                str(feature_with_correctness_issue),
            ]
        )
        data = json.loads(output_file.read_text(encoding="utf-8"))
        diagnostics = data.get("diagnostics", [])
        bc_diags = [d for d in diagnostics if d.get("rule_id", "").startswith("BC")]
        assert len(bc_diags) > 0

    def test_strict_profile_triggers_more_rules_than_recommended(
        self, feature_with_pedantic_issue: Path
    ) -> None:
        """Strict should produce >= diagnostics than recommended."""
        rec_file = feature_with_pedantic_issue.parent / "out_rec_cmp.json"
        strict_file = feature_with_pedantic_issue.parent / "out_strict_cmp.json"

        main(
            [
                "--profile",
                "recommended",
                "--output",
                "json",
                "--output-file",
                str(rec_file),
                str(feature_with_pedantic_issue),
            ]
        )
        main(
            [
                "--profile",
                "strict",
                "--output",
                "json",
                "--output-file",
                str(strict_file),
                str(feature_with_pedantic_issue),
            ]
        )

        rec_data = json.loads(rec_file.read_text(encoding="utf-8"))
        strict_data = json.loads(strict_file.read_text(encoding="utf-8"))

        rec_count = len(rec_data.get("diagnostics", []))
        strict_count = len(strict_data.get("diagnostics", []))
        assert strict_count >= rec_count


# ---------------------------------------------------------------------------
# Profile + --select / --ignore combination
# ---------------------------------------------------------------------------


class TestProfileWithSelectIgnore:
    """Test combining --profile with --select and --ignore."""

    def test_profile_with_select_overrides(
        self, feature_with_style_issue: Path
    ) -> None:
        """--select with --profile should only run selected rules."""
        output_file = feature_with_style_issue.parent / "out_sel.json"
        main(
            [
                "--profile",
                "recommended",
                "--select",
                "BC001",
                "--output",
                "json",
                "--output-file",
                str(output_file),
                str(feature_with_style_issue),
            ]
        )
        data = json.loads(output_file.read_text(encoding="utf-8"))
        diagnostics = data.get("diagnostics", [])
        rule_ids = {d.get("rule_id") for d in diagnostics}
        assert rule_ids.issubset({"BC001"})

    def test_profile_with_ignore_overrides(
        self, feature_with_style_issue: Path
    ) -> None:
        """--ignore should suppress rules even under a profile."""
        output_file = feature_with_style_issue.parent / "out_ign.json"
        main(
            [
                "--profile",
                "recommended",
                "--ignore",
                "BS006,BS007,BS008",
                "--output",
                "json",
                "--output-file",
                str(output_file),
                str(feature_with_style_issue),
            ]
        )
        data = json.loads(output_file.read_text(encoding="utf-8"))
        diagnostics = data.get("diagnostics", [])
        for d in diagnostics:
            assert d.get("rule_id") not in {"BS006", "BS007", "BS008"}


# ---------------------------------------------------------------------------
# Profile via pyproject.toml
# ---------------------------------------------------------------------------


class TestProfileViaPyproject:
    """Test that profile in pyproject.toml is picked up during linting."""

    def test_profile_in_pyproject_toml(
        self, tmp_path: Path, feature_with_style_issue: Path
    ) -> None:
        """Profile in pyproject.toml should affect rule execution."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[tool.behave-lint]\nprofile = "minimal"\n',
            encoding="utf-8",
        )
        output_file = tmp_path / "out_pp.json"
        main(
            [
                "--config",
                str(pyproject),
                "--output",
                "json",
                "--output-file",
                str(output_file),
                str(feature_with_style_issue),
            ]
        )
        data = json.loads(output_file.read_text(encoding="utf-8"))
        diagnostics = data.get("diagnostics", [])
        bs_diags = [d for d in diagnostics if d.get("rule_id", "").startswith("BS")]
        assert bs_diags == []


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestProfileErrors:
    """Test error handling for invalid profiles via CLI."""

    def test_invalid_profile_returns_error_code(
        self, clean_feature: Path, capsys: object
    ) -> None:
        exit_code = main(["--profile", "nonexistent", str(clean_feature)])
        assert exit_code != 0
        assert exit_code != 1  # Not a lint failure, a config error

    def test_invalid_profile_via_pyproject_returns_error(
        self, tmp_path: Path, clean_feature: Path
    ) -> None:
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[tool.behave-lint]\nprofile = "bogus"\n',
            encoding="utf-8",
        )
        exit_code = main(["--config", str(pyproject), str(clean_feature)])
        assert exit_code != 0
        assert exit_code != 1
