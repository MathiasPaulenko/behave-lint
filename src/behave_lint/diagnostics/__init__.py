"""Diagnostic model, collector, filtering, sorting.

Domain layer — component C07.

See COMPONENT_DESIGN.md Section 7 and DIAGNOSTIC_ENGINE.md.
"""

from __future__ import annotations

from behave_lint.diagnostics.collector import DiagnosticCollector
from behave_lint.diagnostics.dedup import deduplicate_diagnostics
from behave_lint.diagnostics.filters import (
    DisableRegion,
    filter_by_severity,
    filter_disabled_rules,
    filter_excluded_files,
    filter_inline_disables,
    parse_disable_comments,
)
from behave_lint.diagnostics.sorting import sort_diagnostics
from behave_lint.diagnostics.validation import (
    validate_diagnostic,
    validate_diagnostics,
)

__all__ = [
    "DiagnosticCollector",
    "DisableRegion",
    "deduplicate_diagnostics",
    "filter_by_severity",
    "filter_disabled_rules",
    "filter_excluded_files",
    "filter_inline_disables",
    "parse_disable_comments",
    "sort_diagnostics",
    "validate_diagnostic",
    "validate_diagnostics",
]
