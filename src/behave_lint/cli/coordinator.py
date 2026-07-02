"""CLI coordinator — entry point for command-line usage.

Parses arguments, routes commands, orchestrates the pipeline, and
manages exit codes. This is the only component that interacts with
the terminal.

See COMPONENT_DESIGN.md C01 and SPECIFICATION.md Section 10.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence

from behave_lint.cli.exit_codes import (
    config_error_exit_code,
    determine_exit_code,
    internal_error_exit_code,
)
from behave_lint.cli.parser import parse_args
from behave_lint.cli.router import route_command
from behave_lint.constants import (
    EXIT_CODE_SUCCESS,
)
from behave_lint.rules.builtin import register_builtins


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the behave-lint CLI.

    Args:
        argv: Command-line arguments (default: sys.argv[1:]).

    Returns:
        Exit code (0, 1, 2, or 3).
    """
    if argv is None:
        argv = sys.argv[1:]

    # Parse arguments
    try:
        args = parse_args(list(argv))
    except SystemExit as exc:
        # argparse calls sys.exit on --help and --version
        code = exc.code if isinstance(exc.code, int) else 0
        return code

    # Route informational commands (--list-rules, --explain)
    # These don't require a full lint engine but need rules registered
    if args.list_rules or args.explain is not None:
        try:
            from behave_lint.plugins.manager import PluginManager
            from behave_lint.rules.registry import RuleRegistry

            registry = RuleRegistry()
            register_builtins(registry)

            plugin_mgr = PluginManager(registry)
            plugin_mgr.discover_all()
            plugin_mgr.load_all()

            exit_code = route_command(args, registry)
            return exit_code
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return internal_error_exit_code()

    # Determine paths
    paths = list(args.paths) if args.paths else []
    if not paths:
        print(
            "No paths specified. Use 'behave-lint features/' or "
            "configure default paths in pyproject.toml.",
            file=sys.stderr,
        )
        return EXIT_CODE_SUCCESS

    # Lint command — run the full pipeline
    try:
        return _run_lint(args, paths)
    except Exception as exc:
        print(f"Internal error: {exc}", file=sys.stderr)
        return internal_error_exit_code()


def _run_lint(args: object, paths: list[str]) -> int:
    """Run the full lint pipeline.

    Args:
        args: Parsed CLIArgs object.
        paths: Paths to lint.

    Returns:
        Exit code from the lint run.
    """
    from behave_lint.configuration.loader import load_config
    from behave_lint.engine.lint_engine import LintEngine
    from behave_lint.models.enums import Severity as Sev
    from behave_lint.reporters.manager import ReporterManager
    from behave_lint.rules.registry import RuleRegistry

    # Build configuration overrides from CLI args
    overrides: dict[str, object] = {}
    if args.select:  # type: ignore[attr-defined]
        overrides["select"] = args.select  # type: ignore[attr-defined]
    if args.ignore:  # type: ignore[attr-defined]
        overrides["ignore"] = args.ignore  # type: ignore[attr-defined]
    if args.output != "console":  # type: ignore[attr-defined]
        overrides["output"] = args.output  # type: ignore[attr-defined]
    if args.output_file is not None:  # type: ignore[attr-defined]
        overrides["output_file"] = args.output_file  # type: ignore[attr-defined]
    if args.fail_on:  # type: ignore[attr-defined]
        overrides["fail_on"] = args.fail_on  # type: ignore[attr-defined]

    # Load configuration
    try:
        config = load_config(
            config_path=args.config,  # type: ignore[attr-defined]
            overrides=overrides,
        )
    except Exception as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return config_error_exit_code()

    # Create registry and register built-in rules
    registry = RuleRegistry()
    register_builtins(registry)

    # Discover and load plugins
    from behave_lint.plugins.manager import PluginManager

    plugin_mgr = PluginManager(registry)
    plugin_mgr.discover_all()
    plugin_mgr.load_all()

    # Run the lint engine
    engine = LintEngine(config, registry)
    want_fix = args.fix or args.unsafe_fixes  # type: ignore[attr-defined]
    result = engine.lint(paths, collect_fixes=want_fix)

    # Apply auto-fixes if requested
    if want_fix and result.fixes:
        from behave_lint.autofix.coordinator import FixCoordinator

        fix_coord = FixCoordinator(
            allow_unsafe=args.unsafe_fixes,  # type: ignore[attr-defined]
            dry_run=False,
        )
        fix_result = fix_coord.apply_edits(result.fixes)

        if not args.quiet:  # type: ignore[attr-defined]
            print(
                f"Applied {fix_result.applied_count} fix(es), "
                f"skipped {fix_result.skipped_count}, "
                f"failed {fix_result.failed_count}.",
                file=sys.stderr,
            )
            if fix_result.files_modified:
                print(
                    f"Modified {len(fix_result.files_modified)} file(s): "
                    + ", ".join(sorted(fix_result.files_modified)),
                    file=sys.stderr,
                )

    # Render output
    reporter_mgr = ReporterManager()
    output_format = args.output  # type: ignore[attr-defined]
    output_file = args.output_file  # type: ignore[attr-defined]

    if not args.quiet:  # type: ignore[attr-defined]
        reporter_mgr.render(result, [output_format], output_file)

    # Determine exit code
    fail_on_map = {
        "error": Sev.ERROR,
        "warning": Sev.WARNING,
        "info": Sev.INFO,
        "off": Sev.OFF,
    }
    fail_on = fail_on_map.get(args.fail_on, Sev.WARNING)  # type: ignore[attr-defined]
    exit_code = determine_exit_code(result.diagnostics, fail_on)

    return exit_code


def run() -> None:
    """Entry point for console scripts. Calls main() and exits."""
    sys.exit(main())


__all__ = ["main", "run"]
