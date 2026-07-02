"""Unit tests for the Typer-based CLI parser."""

from __future__ import annotations

from typer.testing import CliRunner

from behave_lint.cli.parser import app

runner = CliRunner()


class TestTyperApp:
    """Tests for the Typer app."""

    def test_no_args_exits_zero(self) -> None:
        result = runner.invoke(app, [])
        assert result.exit_code == 0

    def test_paths_argument(self) -> None:
        result = runner.invoke(app, ["features/", "tests/"])
        assert result.exit_code == 0

    def test_single_path(self) -> None:
        result = runner.invoke(app, ["features/login.feature"])
        assert result.exit_code == 0

    def test_select_option(self) -> None:
        result = runner.invoke(app, ["--select", "BC001,BS001", "features/"])
        assert result.exit_code == 0

    def test_ignore_option(self) -> None:
        result = runner.invoke(app, ["--ignore", "BC001", "features/"])
        assert result.exit_code == 0

    def test_select_with_spaces(self) -> None:
        result = runner.invoke(app, ["--select", "BC001, BS001", "features/"])
        assert result.exit_code == 0

    def test_output_option(self) -> None:
        result = runner.invoke(app, ["--output", "json", "features/"])
        assert result.exit_code == 0

    def test_output_file_option(self) -> None:
        result = runner.invoke(app, ["--output-file", "results.json", "features/"])
        assert result.exit_code == 0

    def test_config_option(self) -> None:
        result = runner.invoke(app, ["--config", "pyproject.toml", "features/"])
        assert result.exit_code == 0

    def test_color_flag(self) -> None:
        result = runner.invoke(app, ["--color", "features/"])
        assert result.exit_code == 0

    def test_no_color_flag(self) -> None:
        result = runner.invoke(app, ["--no-color", "features/"])
        assert result.exit_code == 0

    def test_verbose_flag(self) -> None:
        result = runner.invoke(app, ["--verbose", "features/"])
        assert result.exit_code == 0

    def test_quiet_flag(self) -> None:
        result = runner.invoke(app, ["--quiet", "features/"])
        assert result.exit_code == 0

    def test_statistics_flag(self) -> None:
        result = runner.invoke(app, ["--statistics", "features/"])
        assert result.exit_code == 0

    def test_no_cache_flag(self) -> None:
        result = runner.invoke(app, ["--no-cache", "features/"])
        assert result.exit_code == 0

    def test_clear_cache_flag(self) -> None:
        result = runner.invoke(app, ["--clear-cache", "features/"])
        assert result.exit_code == 0

    def test_fix_flag(self) -> None:
        result = runner.invoke(app, ["--fix", "features/"])
        assert result.exit_code == 0

    def test_unsafe_fixes_flag(self) -> None:
        result = runner.invoke(app, ["--unsafe-fixes", "features/"])
        assert result.exit_code == 0

    def test_list_rules_flag(self) -> None:
        result = runner.invoke(app, ["--list-rules"])
        assert result.exit_code == 0

    def test_explain_option(self) -> None:
        result = runner.invoke(app, ["--explain", "BC001"])
        # Exit code 2 = unknown rule (no rules registered in test)
        assert result.exit_code in (0, 2)

    def test_fail_on_option(self) -> None:
        result = runner.invoke(app, ["--fail-on", "error", "features/"])
        assert result.exit_code == 0

    def test_fail_on_invalid(self) -> None:
        result = runner.invoke(app, ["--fail-on", "critical", "features/"])
        assert result.exit_code != 0

    def test_multiple_flags(self) -> None:
        result = runner.invoke(
            app,
            [
                "--select",
                "BC001",
                "--ignore",
                "BS001",
                "--output",
                "json",
                "--output-file",
                "out.json",
                "--verbose",
                "--statistics",
                "features/",
            ],
        )
        assert result.exit_code == 0

    def test_version_flag(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "behave-lint" in result.stdout

    def test_help_flag(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "lint" in result.stdout.lower()
