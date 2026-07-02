"""Unit tests for the CLI argument parser."""

from __future__ import annotations

import pytest

from behave_lint.cli.parser import create_parser, parse_args


class TestParseArgs:
    """Tests for parse_args."""

    def test_no_args(self) -> None:
        args = parse_args([])
        assert args.paths == []
        assert args.select == []
        assert args.ignore == []
        assert args.output == "console"
        assert args.output_file is None
        assert args.config is None
        assert args.color is False
        assert args.no_color is False
        assert args.verbose is False
        assert args.quiet is False
        assert args.statistics is False
        assert args.no_cache is False
        assert args.clear_cache is False
        assert args.fix is False
        assert args.unsafe_fixes is False
        assert args.list_rules is False
        assert args.explain is None
        assert args.fail_on == "warning"

    def test_paths(self) -> None:
        args = parse_args(["features/", "tests/"])
        assert args.paths == ["features/", "tests/"]

    def test_single_path(self) -> None:
        args = parse_args(["features/login.feature"])
        assert args.paths == ["features/login.feature"]

    def test_select(self) -> None:
        args = parse_args(["--select", "BC001,BS001", "features/"])
        assert args.select == ["BC001", "BS001"]

    def test_ignore(self) -> None:
        args = parse_args(["--ignore", "BC001", "features/"])
        assert args.ignore == ["BC001"]

    def test_select_with_spaces(self) -> None:
        args = parse_args(["--select", "BC001, BS001", "features/"])
        assert args.select == ["BC001", "BS001"]

    def test_output(self) -> None:
        args = parse_args(["--output", "json", "features/"])
        assert args.output == "json"

    def test_output_file(self) -> None:
        args = parse_args(["--output-file", "results.json", "features/"])
        assert args.output_file == "results.json"

    def test_json_shortcut(self) -> None:
        args = parse_args(["--json", "features/"])
        assert args.output == "json"

    def test_sarif_shortcut(self) -> None:
        args = parse_args(["--sarif", "features/"])
        assert args.output == "sarif"

    def test_config(self) -> None:
        args = parse_args(["--config", "pyproject.toml", "features/"])
        assert args.config == "pyproject.toml"

    def test_color(self) -> None:
        args = parse_args(["--color", "features/"])
        assert args.color is True

    def test_no_color(self) -> None:
        args = parse_args(["--no-color", "features/"])
        assert args.no_color is True

    def test_verbose(self) -> None:
        args = parse_args(["--verbose", "features/"])
        assert args.verbose is True

    def test_quiet(self) -> None:
        args = parse_args(["--quiet", "features/"])
        assert args.quiet is True

    def test_statistics(self) -> None:
        args = parse_args(["--statistics", "features/"])
        assert args.statistics is True

    def test_no_cache(self) -> None:
        args = parse_args(["--no-cache", "features/"])
        assert args.no_cache is True

    def test_clear_cache(self) -> None:
        args = parse_args(["--clear-cache", "features/"])
        assert args.clear_cache is True

    def test_fix(self) -> None:
        args = parse_args(["--fix", "features/"])
        assert args.fix is True

    def test_unsafe_fixes(self) -> None:
        args = parse_args(["--unsafe-fixes", "features/"])
        assert args.unsafe_fixes is True

    def test_list_rules(self) -> None:
        args = parse_args(["--list-rules"])
        assert args.list_rules is True

    def test_explain(self) -> None:
        args = parse_args(["--explain", "BC001"])
        assert args.explain == "BC001"

    def test_fail_on(self) -> None:
        args = parse_args(["--fail-on", "error", "features/"])
        assert args.fail_on == "error"

    def test_fail_on_invalid(self) -> None:
        with pytest.raises(SystemExit):
            parse_args(["--fail-on", "critical", "features/"])

    def test_multiple_flags(self) -> None:
        args = parse_args(
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
            ]
        )
        assert args.select == ["BC001"]
        assert args.ignore == ["BS001"]
        assert args.output == "json"
        assert args.output_file == "out.json"
        assert args.verbose is True
        assert args.statistics is True
        assert args.paths == ["features/"]


class TestCreateParser:
    """Tests for create_parser."""

    def test_parser_has_prog(self) -> None:
        parser = create_parser()
        assert parser.prog == "behave-lint"

    def test_parser_has_description(self) -> None:
        parser = create_parser()
        assert parser.description is not None
        assert "linter" in parser.description.lower()

    def test_parser_has_epilog(self) -> None:
        parser = create_parser()
        assert parser.epilog is not None
        assert "Examples:" in parser.epilog
