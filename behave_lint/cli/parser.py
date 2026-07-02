"""CLI argument parser — Typer-based parser for behave-lint.

Supports all flags defined in SPECIFICATION.md Section 10 and API.md
Section 10. Uses progressive disclosure: common flags are prominent,
advanced flags are documented but less visible.

See COMPONENT_DESIGN.md C01 and SPECIFICATION.md Section 10.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Annotated

import typer

from behave_lint import __version__


@dataclass(frozen=True, slots=True)
class CLIArgs:
    """Parsed CLI arguments.

    Attributes:
        paths: Files or directories to lint.
        select: Rule IDs to enable (comma-separated).
        ignore: Rule IDs to disable (comma-separated).
        output: Output format(s).
        output_file: Output file path (None = stdout).
        config: Explicit path to pyproject.toml.
        color: Force enable colored output.
        no_color: Force disable colored output.
        verbose: Show progress and timing information.
        quiet: Suppress all output except diagnostics.
        statistics: Show diagnostic statistics.
        no_cache: Disable cache for this run.
        clear_cache: Clear cache before running.
        fix: Apply safe auto-fixes (future).
        unsafe_fixes: Apply unsafe auto-fixes (future).
        list_rules: List all available rules and exit.
        explain: Show documentation for a rule and exit.
        fail_on: Minimum severity that causes non-zero exit.
        version: Print version and exit.
    """

    paths: list[str] = field(default_factory=list)
    select: list[str] = field(default_factory=list)
    ignore: list[str] = field(default_factory=list)
    output: str = "console"
    output_file: str | None = None
    config: str | None = None
    color: bool = False
    no_color: bool = False
    verbose: bool = False
    quiet: bool = False
    statistics: bool = False
    no_cache: bool = False
    clear_cache: bool = False
    fix: bool = False
    unsafe_fixes: bool = False
    list_rules: bool = False
    explain: str | None = None
    fail_on: str = "warning"
    version: bool = False


def _parse_rule_list(value: str) -> list[str]:
    """Parse a comma-separated rule ID list.

    Args:
        value: Comma-separated string of rule IDs.

    Returns:
        List of rule IDs, stripped of whitespace.
    """
    if not value:
        return []
    return [r.strip() for r in value.split(",") if r.strip()]


class OutputFormat(StrEnum):
    console = "console"
    json = "json"
    markdown = "markdown"
    sarif = "sarif"
    github = "github"


class FailOn(StrEnum):
    error = "error"
    warning = "warning"
    info = "info"
    off = "off"


app = typer.Typer(
    name="behave-lint",
    help=(
        "A linter for Gherkin/Behave feature files. "
        "Checks style, correctness, and best practices."
    ),
    no_args_is_help=False,
    add_completion=False,
)


def _version_callback(value: bool) -> None:
    if value:
        print(f"behave-lint {__version__}")
        raise typer.Exit


@app.command()
def lint(
    paths: Annotated[
        list[str] | None,
        typer.Argument(help="Files or directories to lint."),
    ] = None,
    select: Annotated[
        str | None,
        typer.Option("--select", help="Enable specific rules (comma-separated)."),
    ] = None,
    ignore: Annotated[
        str | None,
        typer.Option("--ignore", help="Disable specific rules (comma-separated)."),
    ] = None,
    fail_on: Annotated[
        FailOn,
        typer.Option("--fail-on", help="Minimum severity for non-zero exit."),
    ] = FailOn.warning,
    output: Annotated[
        OutputFormat,
        typer.Option("--output", help="Output format."),
    ] = OutputFormat.console,
    output_file: Annotated[
        str | None,
        typer.Option("--output-file", help="Write output to file instead of stdout."),
    ] = None,
    color: Annotated[
        bool, typer.Option("--color", help="Force enable colored output.")
    ] = False,
    no_color: Annotated[
        bool, typer.Option("--no-color", help="Force disable colored output.")
    ] = False,
    verbose: Annotated[
        bool, typer.Option("--verbose", help="Show progress and timing info.")
    ] = False,
    quiet: Annotated[
        bool, typer.Option("--quiet", help="Suppress all output except diagnostics.")
    ] = False,
    statistics: Annotated[
        bool, typer.Option("--statistics", help="Show diagnostic statistics.")
    ] = False,
    config: Annotated[
        str | None,
        typer.Option("--config", help="Explicit path to pyproject.toml."),
    ] = None,
    no_cache: Annotated[
        bool, typer.Option("--no-cache", help="Disable cache for this run.")
    ] = False,
    clear_cache: Annotated[
        bool, typer.Option("--clear-cache", help="Clear cache before running.")
    ] = False,
    fix: Annotated[
        bool, typer.Option("--fix", help="Apply safe auto-fixes to .feature files.")
    ] = False,
    unsafe_fixes: Annotated[
        bool,
        typer.Option("--unsafe-fixes", help="Apply unsafe auto-fixes too."),
    ] = False,
    list_rules: Annotated[
        bool, typer.Option("--list-rules", help="List all available rules and exit.")
    ] = False,
    explain: Annotated[
        str | None,
        typer.Option("--explain", help="Show documentation for a rule and exit."),
    ] = None,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Print version and exit.",
        ),
    ] = None,
) -> int:
    """Lint Gherkin/Behave feature files."""
    from behave_lint.cli.coordinator import run_lint

    args = CLIArgs(
        paths=list(paths) if paths else [],
        select=_parse_rule_list(select) if select else [],
        ignore=_parse_rule_list(ignore) if ignore else [],
        output=output.value,
        output_file=output_file,
        config=config,
        color=color,
        no_color=no_color,
        verbose=verbose,
        quiet=quiet,
        statistics=statistics,
        no_cache=no_cache,
        clear_cache=clear_cache,
        fix=fix,
        unsafe_fixes=unsafe_fixes,
        list_rules=list_rules,
        explain=explain,
        fail_on=fail_on.value,
        version=False,
    )
    return run_lint(args)


__all__ = ["CLIArgs", "FailOn", "OutputFormat", "app"]
