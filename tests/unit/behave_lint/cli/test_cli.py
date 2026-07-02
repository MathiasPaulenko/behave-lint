"""Smoke tests — verify CLI entry point and Typer app work correctly."""

from __future__ import annotations

from typer.testing import CliRunner

from behave_lint.cli import main
from behave_lint.cli.parser import app

runner = CliRunner()


def test_cli_main_no_args_returns_zero() -> None:
    """The CLI main function returns 0 with no arguments."""
    exit_code = main([])
    assert exit_code == 0


def test_cli_main_with_paths_returns_zero() -> None:
    """The CLI main function returns 0 with paths (lint not yet implemented)."""
    exit_code = main(["features/"])
    assert exit_code == 0


def test_typer_app_version() -> None:
    """The Typer app --version flag prints version and exits 0."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "behave-lint" in result.stdout


def test_typer_app_help() -> None:
    """The Typer app --help flag shows help and exits 0."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "lint" in result.stdout.lower()


def test_typer_app_no_args() -> None:
    """The Typer app with no args runs lint and exits 0."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
