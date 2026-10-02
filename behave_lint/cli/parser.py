"""CLI argument parser — Typer-based parser for behave-lint.

Supports all linting, reporting and informational flags. Uses
progressive disclosure: common flags are prominent, advanced flags
are documented but less visible.
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
        exclude: Glob patterns or directory prefixes to exclude.
        profile: Profile name (e.g. "recommended", "strict", "minimal").
        group: Group names (e.g. ["correctness", "style"]).
        output: Output format (None = use config/default).
        output_file: Output file path (None = stdout).
        config: Explicit path to pyproject.toml.
        color: Force enable colored output.
        no_color: Force disable colored output.
        verbose: Show progress and timing information.
        quiet: Suppress all output, including diagnostics.
        statistics: Show diagnostic statistics.
        no_cache: Disable cache for this run.
        clear_cache: Clear cache before running.
        fix: Apply safe auto-fixes.
        unsafe_fixes: Apply unsafe auto-fixes too.
        dry_run: Preview fixes without writing files.
        watch: Watch for file changes and re-lint automatically.
        jobs: Thread pool size for rule execution (None = CPU count).
        list_rules: List all available rules and exit.
        explain: Show documentation for a rule and exit.
        fail_on: Minimum severity that causes non-zero exit
            (None = use config/default).
        version: Print version and exit.
    """

    paths: list[str] = field(default_factory=list)
    select: list[str] = field(default_factory=list)
    ignore: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    profile: str = "none"
    group: list[str] = field(default_factory=list)
    output: str | None = None
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
    dry_run: bool = False
    watch: bool = False
    jobs: int | None = None
    list_rules: bool = False
    explain: str | None = None
    fail_on: str | None = None
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
    exclude: Annotated[
        str | None,
        typer.Option(
            "--exclude",
            help="Exclude files/dirs (comma-separated globs or prefixes).",
        ),
    ] = None,
    profile: Annotated[
        str | None,
        typer.Option(
            "--profile",
            help="Use a built-in profile: recommended, strict, minimal.",
        ),
    ] = None,
    group: Annotated[
        str | None,
        typer.Option(
            "--group",
            help=(
                "Select rules by group (comma-separated). "
                "Categories: correctness, style, pedantic, "
                "step-definitions, consistency, complexity, security, "
                "i18n, accessibility. "
                "Tags: naming, tags, steps, background, description, "
                "documentation, formatting, examples, scenarios, "
                "readability."
            ),
        ),
    ] = None,
    fail_on: Annotated[
        FailOn | None,
        typer.Option(
            "--fail-on", help="Minimum severity for non-zero exit."
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            help=(
                "Output format: console, json, markdown, sarif, github, "
                "or a plugin-provided format."
            ),
        ),
    ] = None,
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
        bool,
        typer.Option(
            "--quiet", help="Suppress all output (including diagnostics)."
        ),
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
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Preview fixes without writing files."),
    ] = False,
    jobs: Annotated[
        int | None,
        typer.Option("--jobs", help="Thread pool size for rule execution."),
    ] = None,
    watch: Annotated[
        bool,
        typer.Option("--watch", help="Watch for changes and re-lint automatically."),
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
        exclude=_parse_rule_list(exclude) if exclude else [],
        profile=profile if profile else "none",
        group=_parse_rule_list(group) if group else [],
        output=output,
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
        dry_run=dry_run,
        watch=watch,
        jobs=jobs,
        list_rules=list_rules,
        explain=explain,
        fail_on=fail_on.value if fail_on else None,
        version=False,
    )
    return run_lint(args)


__all__ = ["CLIArgs", "FailOn", "OutputFormat", "app"]
