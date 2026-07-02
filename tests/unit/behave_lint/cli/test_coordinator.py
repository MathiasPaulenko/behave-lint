"""Unit tests for the CLI coordinator."""

from __future__ import annotations

from behave_lint.cli.coordinator import main
from behave_lint.constants import (
    EXIT_CODE_SUCCESS,
)


class TestMain:
    """Tests for the main() coordinator function."""

    def test_no_args_returns_zero(self, capsys) -> None:  # type: ignore[no-untyped-def]
        exit_code = main([])
        assert exit_code == EXIT_CODE_SUCCESS
        captured = capsys.readouterr()
        assert "No paths" in captured.err

    def test_with_paths_returns_zero(self, capsys) -> None:  # type: ignore[no-untyped-def]
        exit_code = main(["features/"])
        assert exit_code == EXIT_CODE_SUCCESS
        captured = capsys.readouterr()
        # Engine runs but finds no .feature files in features/ (if it doesn't exist)
        # or produces no diagnostics (if it does). Either way, exit 0.
        assert "not yet implemented" not in captured.err

    def test_version_flag_returns_zero(self, capsys) -> None:  # type: ignore[no-untyped-def]
        exit_code = main(["--version"])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "behave-lint" in captured.out

    def test_help_flag_returns_zero(self, capsys) -> None:  # type: ignore[no-untyped-def]
        exit_code = main(["--help"])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "usage" in captured.out.lower()

    def test_list_rules_returns_zero(self, capsys) -> None:  # type: ignore[no-untyped-def]
        exit_code = main(["--list-rules"])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Rule ID" in captured.out
        assert "BC001" in captured.out

    def test_explain_unknown_rule_returns_two(self, capsys) -> None:  # type: ignore[no-untyped-def]
        exit_code = main(["--explain", "UNKNOWN001"])
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "Unknown rule ID" in captured.out

    def test_explain_known_rule_returns_zero(self, capsys) -> None:  # type: ignore[no-untyped-def]
        exit_code = main(["--explain", "BC001"])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "BC001" in captured.out
        assert "duplicate-scenario-names" in captured.out

    def test_multiple_paths(self, capsys) -> None:  # type: ignore[no-untyped-def]
        exit_code = main(["features/", "tests/"])
        assert exit_code == EXIT_CODE_SUCCESS
        captured = capsys.readouterr()
        assert "not yet implemented" not in captured.err

    def test_select_and_ignore_flags(self, capsys) -> None:  # type: ignore[no-untyped-def]
        exit_code = main(["--select", "BC001", "--ignore", "BS001", "features/"])
        assert exit_code == EXIT_CODE_SUCCESS

    def test_verbose_flag(self, capsys) -> None:  # type: ignore[no-untyped-def]
        exit_code = main(["--verbose", "features/"])
        assert exit_code == EXIT_CODE_SUCCESS

    def test_quiet_flag(self, capsys) -> None:  # type: ignore[no-untyped-def]
        exit_code = main(["--quiet", "features/"])
        assert exit_code == EXIT_CODE_SUCCESS

    def test_statistics_flag(self, capsys) -> None:  # type: ignore[no-untyped-def]
        exit_code = main(["--statistics", "features/"])
        assert exit_code == EXIT_CODE_SUCCESS

    def test_json_output_flag(self, capsys) -> None:  # type: ignore[no-untyped-def]
        exit_code = main(["--output", "json", "features/"])
        assert exit_code == EXIT_CODE_SUCCESS

    def test_invalid_flag_returns_error_code(self, capsys) -> None:  # type: ignore[no-untyped-def]
        exit_code = main(["--nonexistent-flag"])
        assert exit_code == 2
