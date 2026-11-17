"""Diagnostic filters — severity, rule-level, file-level, inline disables.

Each filter is a pure function that takes a list of diagnostics and
configuration, and returns the filtered list. Filters are composable
and independent.
"""

from __future__ import annotations

import re
from pathlib import PurePath

from behave_lint.constants import PARSE_ERROR_RULE_ID
from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Severity

# --- Inline disable comment parsing ---

_DISABLE_PATTERN = re.compile(
    r"#\s*behave-lint:\s*(off|on)\s*([A-Z][A-Z0-9]*\d{3}(?:\s*,\s*[A-Z][A-Z0-9]*\d{3})*)?",
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

    def _covers(self, rule_id: str, line: int) -> bool:
        """Whether the region's range and rule set cover ``rule_id``."""
        if line < self.start_line:
            return False
        if self.end_line is not None and line > self.end_line:
            return False
        if not self.rule_ids:
            return True
        return rule_id in self.rule_ids

    def is_disabled(self, rule_id: str, line: int) -> bool:
        """Check if a rule at a given line is within this disable region.

        Args:
            rule_id: The rule ID to check.
            line: The line number of the diagnostic.

        Returns:
            True if the diagnostic is within this disable region and
            the rule is affected.
        """
        return self._covers(rule_id, line)


class EnableRegion(DisableRegion):
    """A region where specific rules are re-enabled inside a global
    disable (``# behave-lint: on RULE`` while ``off`` is active).

    Enable regions never suppress diagnostics themselves; they carve
    exceptions out of overlapping ``DisableRegion`` objects.
    """

    def is_disabled(self, rule_id: str, line: int) -> bool:
        """Enable regions never disable a rule.

        Args:
            rule_id: The rule ID to check.
            line: The line number of the diagnostic.

        Returns:
            Always False.
        """
        return False

    def reenables(self, rule_id: str, line: int) -> bool:
        """Whether this region re-enables ``rule_id`` at ``line``.

        Args:
            rule_id: The rule ID to check.
            line: The line number of the diagnostic.

        Returns:
            True if the line is inside the region and the rule is
            listed in it.
        """
        return bool(self.rule_ids) and self._covers(rule_id, line)


_DOCSTRING_DELIMITERS = ('"""', "'''", "```")


def parse_disable_comments(
    lines: list[str],
) -> list[DisableRegion]:
    """Parse inline disable comments from feature file lines.

    Supported comment forms:
    - `# behave-lint: off` — disables all rules from the next line on.
    - `# behave-lint: off BC001` — disables specific rule(s).
    - `# behave-lint: off BC001,BS001` — disables multiple rules.
    - `# behave-lint: on` — re-enables everything.
    - `# behave-lint: on BC001` — re-enables only that rule; other
      rules stay disabled if a global or specific ``off`` is active.

    Directives appearing inside Gherkin docstrings (``\"\"\"``, ``'''``
    or ````` ``` ```` blocks) are ignored — they are content, not comments.

    Args:
        lines: Lines of the feature file.

    Returns:
        List of regions. ``EnableRegion`` items express re-enabled
        rules inside a global disable; all other items are
        ``DisableRegion`` objects.
    """
    regions: list[DisableRegion] = []
    global_off_start: int | None = None
    specific_off: dict[str, int] = {}
    reenabled: dict[str, int] = {}
    in_docstring = False

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if any(stripped.startswith(d) for d in _DOCSTRING_DELIMITERS):
            in_docstring = not in_docstring
            continue
        if in_docstring:
            continue

        match = _DISABLE_PATTERN.search(line)
        if match is None:
            continue

        action = match.group(1).lower()
        rules_str = match.group(2)
        rule_ids = (
            [r.strip().upper() for r in rules_str.split(",")] if rules_str else None
        )

        if action == "off":
            if rule_ids is None:
                if global_off_start is None:
                    global_off_start = i
            else:
                for rid in rule_ids:
                    enable_start = reenabled.pop(rid) if rid in reenabled else None
                    if enable_start is not None:
                        regions.append(EnableRegion(enable_start, i, frozenset({rid})))
                    specific_off.setdefault(rid, i)
        else:
            if rule_ids is None:
                if global_off_start is not None:
                    regions.append(DisableRegion(global_off_start, i, frozenset()))
                    global_off_start = None
                for rid, start in specific_off.items():
                    regions.append(DisableRegion(start, i, frozenset({rid})))
                specific_off.clear()
                for rid, start in reenabled.items():
                    regions.append(EnableRegion(start, i, frozenset({rid})))
                reenabled.clear()
            else:
                for rid in rule_ids:
                    off_start = specific_off.pop(rid) if rid in specific_off else None
                    if off_start is not None:
                        regions.append(DisableRegion(off_start, i, frozenset({rid})))
                    elif global_off_start is not None:
                        reenabled.setdefault(rid, i)

    if global_off_start is not None:
        regions.append(DisableRegion(global_off_start, None, frozenset()))
    for rid, start in specific_off.items():
        regions.append(DisableRegion(start, None, frozenset({rid})))
    for rid, start in reenabled.items():
        regions.append(EnableRegion(start, None, frozenset({rid})))

    return _merge_regions(regions)


def _merge_regions(regions: list[DisableRegion]) -> list[DisableRegion]:
    """Merge regions with identical range and kind into one.

    Directives like ``off BC001,BS001`` are tracked per rule so a
    later ``on BC001`` can re-enable just one of them; regions that
    still share the same range are merged back for a compact result.

    Args:
        regions: Regions in emission order.

    Returns:
        Regions with per-(kind, start, end) rule-id sets unified.
    """
    merged: list[DisableRegion] = []
    for region in regions:
        for existing in merged:
            if (
                type(existing) is type(region)
                and existing.start_line == region.start_line
                and existing.end_line == region.end_line
                and bool(existing.rule_ids) == bool(region.rule_ids)
            ):
                existing.rule_ids = existing.rule_ids | region.rule_ids
                break
        else:
            merged.append(region)
    return merged


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
        Parse-error diagnostics (``B000``) always pass through: they
        are produced by the parser, not by a selectable rule.
    """
    return [
        d
        for d in diagnostics
        if d.rule_id == PARSE_ERROR_RULE_ID or config.is_rule_enabled(d.rule_id)
    ]


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
        normalized = str(pure).replace("\\", "/")
        name = pure.name
        for pattern in exclude_patterns:
            pat = pattern.replace("\\", "/")
            if fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(normalized, pat):
                return True
            if fnmatch.fnmatch(name, pat):
                return True
            # Prefix match, same semantics as file discovery:
            # "features/wip" excludes that path and anything beneath it.
            prefix = pat.rstrip("/")
            if prefix and (normalized == prefix or normalized.startswith(prefix + "/")):
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
        ) and not any(
            region.reenables(diag.rule_id, diag.line)
            for region in regions
            if isinstance(region, EnableRegion)
        )
        if not is_suppressed:
            result.append(diag)

    return result


__all__ = [
    "DisableRegion",
    "EnableRegion",
    "filter_by_severity",
    "filter_disabled_rules",
    "filter_excluded_files",
    "filter_inline_disables",
    "parse_disable_comments",
]
