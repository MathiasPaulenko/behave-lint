"""CLI Coordinator — Presentation layer (component C01).

Parses command-line arguments, routes commands, invokes the engine,
renders output, and determines exit codes.

See COMPONENT_DESIGN.md Section 4 and API.md Section 10.
"""

from __future__ import annotations

from behave_lint.cli.coordinator import main, run
from behave_lint.cli.exit_codes import (
    config_error_exit_code,
    determine_exit_code,
    internal_error_exit_code,
)
from behave_lint.cli.parser import CLIArgs, create_parser, parse_args
from behave_lint.cli.router import route_command

__all__ = [
    "CLIArgs",
    "config_error_exit_code",
    "create_parser",
    "determine_exit_code",
    "internal_error_exit_code",
    "main",
    "parse_args",
    "route_command",
    "run",
]
