"""CLI argument parser — argparse-based parser for behave-lint.

Supports all flags defined in SPECIFICATION.md Section 10 and API.md
Section 10. Uses progressive disclosure: common flags are prominent,
advanced flags are documented but less visible.

See COMPONENT_DESIGN.md C01 and SPECIFICATION.md Section 10.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field

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


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for behave-lint.

    Returns:
        A configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="behave-lint",
        description=(
            "A linter for Gherkin/Behave feature files. "
            "Checks style, correctness, and best practices."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  behave-lint features/\n"
            "  behave-lint --output json --output-file results.json features/\n"
            "  behave-lint --select BC001,BS001 features/\n"
            "  behave-lint --list-rules\n"
            "  behave-lint --explain BC001\n"
        ),
    )

    # Positional arguments
    parser.add_argument(
        "paths",
        nargs="*",
        default=[],
        help=(
            "Files or directories to lint. "
            "Defaults to 'features/' if it exists, else current directory."
        ),
    )

    # Rule selection
    rules_group = parser.add_argument_group("Rule Selection")
    rules_group.add_argument(
        "--select",
        type=str,
        default=None,
        help="Enable specific rules (comma-separated). Overrides configuration.",
    )
    rules_group.add_argument(
        "--ignore",
        type=str,
        default=None,
        help="Disable specific rules (comma-separated). Overrides configuration.",
    )
    rules_group.add_argument(
        "--fail-on",
        type=str,
        default="warning",
        choices=["error", "warning", "info", "off"],
        help="Minimum severity that causes non-zero exit (default: warning).",
    )

    # Output
    output_group = parser.add_argument_group("Output")
    output_group.add_argument(
        "--output",
        type=str,
        default="console",
        choices=["console", "json", "markdown", "sarif", "github"],
        help="Output format (default: console).",
    )
    output_group.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Write output to file instead of stdout.",
    )
    output_group.add_argument(
        "--json",
        action="store_const",
        const="json",
        dest="output",
        help="Shortcut for --output json.",
    )
    output_group.add_argument(
        "--sarif",
        action="store_const",
        const="sarif",
        dest="output",
        help="Shortcut for --output sarif.",
    )
    output_group.add_argument(
        "--color",
        action="store_true",
        default=False,
        help="Force enable colored output.",
    )
    output_group.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Force disable colored output.",
    )
    output_group.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Show progress and timing information.",
    )
    output_group.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress all output except diagnostics.",
    )
    output_group.add_argument(
        "--statistics",
        action="store_true",
        default=False,
        help="Show diagnostic statistics by rule and severity.",
    )

    # Configuration
    config_group = parser.add_argument_group("Configuration")
    config_group.add_argument(
        "--config",
        type=str,
        default=None,
        help="Explicit path to pyproject.toml.",
    )
    config_group.add_argument(
        "--no-cache",
        action="store_true",
        default=False,
        help="Disable cache for this run.",
    )
    config_group.add_argument(
        "--clear-cache",
        action="store_true",
        default=False,
        help="Clear cache before running.",
    )

    # Auto-fix
    fix_group = parser.add_argument_group("Auto-Fix")
    fix_group.add_argument(
        "--fix",
        action="store_true",
        default=False,
        help="Apply safe auto-fixes to .feature files.",
    )
    fix_group.add_argument(
        "--unsafe-fixes",
        action="store_true",
        default=False,
        help="Apply unsafe auto-fixes in addition to safe ones.",
    )

    # Informational
    info_group = parser.add_argument_group("Informational")
    info_group.add_argument(
        "--list-rules",
        action="store_true",
        default=False,
        help="List all available rules and exit.",
    )
    info_group.add_argument(
        "--explain",
        type=str,
        default=None,
        metavar="RULE_ID",
        help="Show documentation for the specified rule and exit.",
    )
    info_group.add_argument(
        "--version",
        action="version",
        version=f"behave-lint {__version__}",
    )

    return parser


def parse_args(argv: list[str] | None = None) -> CLIArgs:
    """Parse command-line arguments into a CLIArgs object.

    Args:
        argv: Argument list (default: sys.argv[1:]).

    Returns:
        Parsed CLIArgs object.
    """
    parser = create_parser()
    ns = parser.parse_args(argv)

    return CLIArgs(
        paths=list(ns.paths) if ns.paths else [],
        select=_parse_rule_list(ns.select) if ns.select else [],
        ignore=_parse_rule_list(ns.ignore) if ns.ignore else [],
        output=ns.output,
        output_file=ns.output_file,
        config=ns.config,
        color=ns.color,
        no_color=ns.no_color,
        verbose=ns.verbose,
        quiet=ns.quiet,
        statistics=ns.statistics,
        no_cache=ns.no_cache,
        clear_cache=ns.clear_cache,
        fix=ns.fix,
        unsafe_fixes=ns.unsafe_fixes,
        list_rules=ns.list_rules,
        explain=ns.explain,
        fail_on=ns.fail_on,
        version=False,
    )


__all__ = ["CLIArgs", "create_parser", "parse_args"]
