"""Diagnostic filters — severity, rule-level, file-level, inline disables.

Each filter is a pure function that takes a list of diagnostics and
configuration, and returns the filtered list. Filters are composable
and independent.

See DIAGNOSTIC_ENGINE.md Section 8.
"""

from __future__ import annotations

import re
from pathlib import PurePath

from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Severity

# --- Inline disable comment parsing ---

_DISABLE_PATTERN = re.compile(
    r"#\s*behave-lint:\s*(off|on)\s*([A-Z]{2}\d{3}(?:\s*,\s*[A-Z]{2}\d{3})*)?",
    re.IGNORECASE,
)


class DisableRegion:
    """Represents a region where specific rules are disabled.

    Attributes:
        start_line: Line where the disable comment appears.
        end_line: Line where the re-enable comment appears (or None
            if disabled until end of file).
        rule_ids: Set of rule IDs disabled. Empty set means all rules.
    """

    __slots__ = ("end_line", "rule_ids", "start_line")

    def __init__(
        self,
        start_line: int,
        end_line: int | None,
        rule_ids: frozenset[str] | None = None,
    ) -> None:
        self.start_line = start_line
        self.end_line = end_line
        self.rule_ids = rule_ids or frozenset()

    def is_disabled(self, rule_id: str, line: int) -> bool:
        """Check if a rule at a given line is within this disable region.

        Args:
            rule_id: The rule ID to check.
            line: The line number of the diagnostic.

        Returns:
            True if the diagnostic is within this disable region and
            the rule is affected.
        """
        if line < self.start_line:
            return False
        if self.end_line is not None and line > self.end_line:
            return False
        if not self.rule_ids:
            return True
        return rule_id in self.rule_ids


def parse_disable_comments(
    lines: list[str],
) -> list[DisableRegion]:
    """Parse inline disable comments from feature file lines.

    Supported comment forms:
    - `# behave-lint: off` — disables all rules for the next block.
    - `# behave-lint: off BC001` — disables specific rule.
    - `# behave-lint: off BC001,BS001` — disables multiple rules.
    - `# behave-lint: on` — re-enables all rules.
    - `# behave-lint: on BC001` — re-enables specific rule.

    Args:
        lines: Lines of the feature file.

    Returns:
        List of DisableRegion objects.
    """
    regions: list[DisableRegion] = []
    open_disables: dict[frozenset[str] | None, int] = {}

    for i, line in enumerate(lines, start=1):
        match = _DISABLE_PATTERN.search(line)
        if match is None:
            continue

        action = match.group(1).lower()
        rules_str = match.group(2)

        rule_ids: frozenset[str] | None = None
        if rules_str:
            rule_ids = frozenset(r.strip().upper() for r in rules_str.split(","))

        if action == "off":
            open_disables[rule_ids] = i
        elif action == "on":
            # Close any open disable with matching rule set
            keys_to_close = [k for k in open_disables if k == rule_ids or k is None]
            if rule_ids is None:
                # "on" closes everything
                keys_to_close = list(open_disables.keys())
            for key in keys_to_close:
                start = open_disables.pop(key, None)
                if start is not None:
                    regions.append(
                        DisableRegion(
                            start_line=start,
                            end_line=i,
                            rule_ids=key,
                        )
                    )

    # Close any remaining open disables (until end of file)
    for rule_set, start in open_disables.items():
        regions.append(
            DisableRegion(
                start_line=start,
                end_line=None,
                rule_ids=rule_set,
            )
        )

    return regions


# --- Filters ---


def filter_by_severity(
    diagnostics: list[Diagnostic],
    *,
    min_severity: Severity = Severity.INFO,
) -> list[Diagnostic]:
    """Filter out diagnostics below the minimum severity.

    Diagnostics with severity OFF are always filtered out.
    Diagnostics at or above min_severity are retained.

    Args:
        diagnostics: List of diagnostics.
        min_severity: Minimum severity to retain (inclusive).

    Returns:
        Filtered list of diagnostics.
    """
    severity_order = {
        Severity.OFF: 0,
        Severity.INFO: 1,
        Severity.WARNING: 2,
        Severity.ERROR: 3,
    }
    min_level = severity_order.get(min_severity, 1)
    return [
        d
        for d in diagnostics
        if d.severity is not Severity.OFF
        and severity_order.get(d.severity, 0) >= min_level
    ]


def filter_disabled_rules(
    diagnostics: list[Diagnostic],
    config: Config,
) -> list[Diagnostic]:
    """Filter out diagnostics from disabled rules (safety net).

    Args:
        diagnostics: List of diagnostics.
        config: Configuration object with rule selection.

    Returns:
        Filtered list — diagnostics from rules not enabled are removed.
    """
    return [d for d in diagnostics if config.is_rule_enabled(d.rule_id)]


def filter_excluded_files(
    diagnostics: list[Diagnostic],
    exclude_patterns: list[str],
) -> list[Diagnostic]:
    """Filter out diagnostics from excluded file paths.

    Uses glob-style pattern matching against file paths.

    Args:
        diagnostics: List of diagnostics.
        exclude_patterns: Glob patterns for files to exclude.

    Returns:
        Filtered list.
    """
    if not exclude_patterns:
        return diagnostics

    import fnmatch

    def is_excluded(path: str) -> bool:
        pure = PurePath(path)
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(path, pattern):
                return True
            # Also match against the path with forward slashes
            normalized = str(pure).replace("\\", "/")
            if fnmatch.fnmatch(normalized, pattern):
                return True
        return False

    return [d for d in diagnostics if not is_excluded(d.file_path)]


def filter_inline_disables(
    diagnostics: list[Diagnostic],
    file_contents: dict[str, list[str]],
) -> list[Diagnostic]:
    """Filter out diagnostics suppressed by inline disable comments.

    Args:
        diagnostics: List of diagnostics.
        file_contents: Dict mapping file paths to their lines.

    Returns:
        Filtered list.
    """
    # Parse disable regions per file
    regions_by_file: dict[str, list[DisableRegion]] = {}
    for file_path, lines in file_contents.items():
        regions_by_file[file_path] = parse_disable_comments(lines)

    result: list[Diagnostic] = []
    for diag in diagnostics:
        regions = regions_by_file.get(diag.file_path, [])
        is_suppressed = any(
            region.is_disabled(diag.rule_id, diag.line) for region in regions
        )
        if not is_suppressed:
            result.append(diag)

    return result


__all__ = [
    "DisableRegion",
    "filter_by_severity",
    "filter_disabled_rules",
    "filter_excluded_files",
    "filter_inline_disables",
    "parse_disable_comments",
]
