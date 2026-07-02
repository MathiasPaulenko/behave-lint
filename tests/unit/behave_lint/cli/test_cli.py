"""Smoke test — verify CLI entry point exists and returns 0."""

from __future__ import annotations

from behave_lint.cli import main


def test_cli_main_no_args_returns_zero() -> None:
    """The CLI main function returns 0 with no arguments."""
    exit_code = main([])
    assert exit_code == 0


def test_cli_main_with_paths_returns_zero() -> None:
    """The CLI main function returns 0 with paths (lint not yet implemented)."""
    exit_code = main(["features/"])
    assert exit_code == 0
