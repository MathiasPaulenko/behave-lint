"""Reporter Manager and built-in reporters (console, JSON, Markdown, SARIF).

Application layer — component C08.

See COMPONENT_DESIGN.md Section 5 and API.md Section 8.
"""

from __future__ import annotations

from behave_lint.reporters.base import Reporter
from behave_lint.reporters.console import ConsoleReporter
from behave_lint.reporters.github import GitHubActionsReporter
from behave_lint.reporters.json_reporter import SCHEMA_VERSION, JSONReporter
from behave_lint.reporters.manager import ReporterManager
from behave_lint.reporters.markdown import MarkdownReporter
from behave_lint.reporters.sarif import SARIF_SCHEMA, SARIF_VERSION, SARIFReporter

__all__ = [
    "SARIF_SCHEMA",
    "SARIF_VERSION",
    "SCHEMA_VERSION",
    "ConsoleReporter",
    "GitHubActionsReporter",
    "JSONReporter",
    "MarkdownReporter",
    "Reporter",
    "ReporterManager",
    "SARIFReporter",
]
