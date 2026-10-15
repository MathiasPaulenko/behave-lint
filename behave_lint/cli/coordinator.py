"""CLI coordinator — entry point for command-line usage.

Parses arguments, routes commands, orchestrates the pipeline, and
manages exit codes. This is the only component that interacts with
the terminal.
"""

from __future__ import annotations

import logging
import os
import sys
from collections.abc import Sequence

from behave_lint.cli.exit_codes import (
    config_error_exit_code,
    internal_error_exit_code,
)
from behave_lint.cli.parser import CLIArgs
from behave_lint.cli.router import route_command
from behave_lint.constants import (
    ENV_PREFIX,
    EXIT_CODE_SUCCESS,
    TRACE_ENV_VAR,
)
from behave_lint.models.config import Config
from behave_lint.rules.builtin import register_builtins

logger = logging.getLogger(__name__)


def _env_flag(name: str) -> bool:
    """Return True if an environment variable is set to a truthy value."""
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes")


def _build_overrides(args: CLIArgs) -> dict[str, object]:
    """Build the config-overrides dict from CLI arguments."""
    overrides: dict[str, object] = {}
    if args.select:
        overrides["select"] = args.select
    if args.ignore:
        overrides["ignore"] = args.ignore
    if args.profile and args.profile != "none":
        overrides["profile"] = args.profile
    if args.group:
        overrides["group"] = args.group
    if args.output is not None:
        overrides["output"] = args.output
    if args.output_file is not None:
        overrides["output_file"] = args.output_file
    if args.fail_on:
        overrides["fail_on"] = args.fail_on
    return overrides


def _config_path_arg(args: CLIArgs) -> str | None:
    """Explicit --config path, falling back to BEHAVE_LINT_CONFIG."""
    return args.config or os.environ.get(f"{ENV_PREFIX}CONFIG")


def run_lint(args: CLIArgs) -> int:
    """Run the full lint flow: routing + lint pipeline.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code (0, 1, 2, or 3).
    """
    if _env_flag(TRACE_ENV_VAR):
        logging.basicConfig(level=logging.DEBUG)

    # Route informational commands (--list-rules, --explain)
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

    # Determine paths: positional args, then configured defaults.
    paths = list(args.paths)
    config = None
    if not paths:
        try:
            config = _load_config(args)
        except Exception as exc:
            print(f"Configuration error: {exc}", file=sys.stderr)
            return config_error_exit_code()
        paths = list(config.paths)
    if not paths:
        print(
            "No paths specified. Use 'behave-lint features/' or "
            "configure default paths in pyproject.toml.",
            file=sys.stderr,
        )
        return EXIT_CODE_SUCCESS

    # Lint command — run the full pipeline
    try:
        if args.watch:
            from behave_lint.cli.watch import WatchMode

            watcher = WatchMode(args, paths)
            return watcher.run()
        return _run_lint(args, paths, config=config)
    except Exception as exc:
        print(f"Internal error: {exc}", file=sys.stderr)
        return internal_error_exit_code()


def _load_config(args: CLIArgs) -> Config:
    """Load the resolved configuration for a run."""
    from behave_lint.configuration.loader import load_config

    return load_config(
        config_path=_config_path_arg(args),
        overrides=_build_overrides(args),
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the behave-lint CLI.

    Args:
        argv: Command-line arguments (default: sys.argv[1:]).

    Returns:
        Exit code (0, 1, 2, or 3).
    """
    from behave_lint.cli.parser import app

    if argv is None:
        argv = sys.argv[1:]

    try:
        result = app(args=list(argv), standalone_mode=False)
        return result if isinstance(result, int) else 0
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 0
        return code
    except Exception as exc:
        if "No such option" in str(exc) or "Invalid value" in str(exc):
            print(f"Error: {exc}", file=sys.stderr)
            return config_error_exit_code()
        print(f"Internal error: {exc}", file=sys.stderr)
        return internal_error_exit_code()


def _run_lint(args: CLIArgs, paths: list[str], config: Config | None = None) -> int:
    """Run the full lint pipeline.

    Args:
        args: Parsed CLIArgs object.
        paths: Paths to lint.
        config: Pre-loaded configuration, or None to load it here.

    Returns:
        Exit code from the lint run.
    """
    from behave_lint.engine.lint_engine import LintEngine
    from behave_lint.reporters.manager import ReporterManager
    from behave_lint.rules.registry import RuleRegistry

    # Create registry and register built-in rules
    registry = RuleRegistry()
    register_builtins(registry)

    # Discover plugins; config-provider plugins feed into load_config.
    from behave_lint.plugins.manager import PluginManager

    plugin_mgr = PluginManager(registry)
    plugin_mgr.discover_all()
    plugin_overrides = plugin_mgr.load_config_plugins()

    # Load configuration (unless the caller already resolved it — in
    # that case re-apply plugin-provided overrides on top of it).
    try:
        if config is None or plugin_overrides:
            merged_overrides = dict(plugin_overrides)
            merged_overrides.update(_build_overrides(args))
            from behave_lint.configuration.loader import load_config

            config = load_config(
                config_path=_config_path_arg(args),
                overrides=merged_overrides or None,
            )
    except Exception as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return config_error_exit_code()

    plugin_mgr.load_all(plugin_config=config.plugins)

    if args.verbose:
        print(
            f"[verbose] paths={paths} exclude={list(config.exclude)}",
            file=sys.stderr,
        )
        print(
            f"[verbose] plugins discovered: {len(plugin_mgr)}",
            file=sys.stderr,
        )

    # Run the lint engine
    engine = LintEngine(config, registry)
    want_fix = args.fix or args.unsafe_fixes
    result = engine.lint(
        paths,
        exclude=list(args.exclude),
        max_workers=args.jobs,
        collect_fixes=want_fix,
        use_cache=not args.no_cache,
        clear_cache=args.clear_cache,
    )

    # Apply auto-fixes if requested
    if want_fix and result.fixes:
        from behave_lint.autofix.coordinator import FixCoordinator

        fix_coord = FixCoordinator(
            allow_unsafe=args.unsafe_fixes,
            dry_run=args.dry_run,
        )
        fix_result = fix_coord.apply_edits(result.fixes)

        if not args.quiet:
            verb = "Would apply" if args.dry_run else "Applied"
            print(
                f"{verb} {fix_result.applied_count} fix(es), "
                f"skipped {fix_result.skipped_count}, "
                f"failed {fix_result.failed_count}.",
                file=sys.stderr,
            )
            if fix_result.files_modified and not args.dry_run:
                print(
                    f"Modified {len(fix_result.files_modified)} file(s): "
                    + ", ".join(sorted(fix_result.files_modified)),
                    file=sys.stderr,
                )

    if result.summary.total_files == 0 and not args.quiet:
        print(
            "No .feature files found in the given paths.",
            file=sys.stderr,
        )

    # The engine already stamped the exit code (fail_on and
    # max_warnings from the resolved config) into the result.
    exit_code = result.exit_code

    # Render output
    use_color: bool | None = None
    if args.color:
        use_color = True
    elif args.no_color:
        use_color = False
    reporter_mgr = ReporterManager(use_color=use_color)
    plugin_mgr.register_reporters(reporter_mgr, plugin_config=config.plugins)

    output_spec = config.output or "console"
    formats = [f.strip() for f in output_spec.split(",") if f.strip()]
    output_file = args.output_file or config.output_file

    try:
        if not args.quiet:
            reporter_mgr.render(result, formats, output_file)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return config_error_exit_code()

    if args.statistics and not args.quiet:
        s = result.summary
        print(
            f"Statistics: {s.total_diagnostics} diagnostics "
            f"({s.error_count} error, {s.warning_count} warning, "
            f"{s.info_count} info), {s.total_files} files, "
            f"{s.rules_executed} rules, {s.duration_ms:.1f} ms. "
            f"Cache: {s.cache_hits} hits, {s.cache_misses} misses.",
            file=sys.stderr,
        )

    return exit_code


def run() -> None:
    """Entry point for console scripts. Calls main() and exits."""
    sys.exit(main())


__all__ = ["main", "run", "run_lint"]
