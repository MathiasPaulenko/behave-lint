"""SARIF reporter — SARIF 2.1.0 format for GitHub Code Scanning.

Produces a SARIF v2.1.0 compliant JSON document with results, rules,
and tool metadata. Compatible with GitHub Actions code scanning.

See SPECIFICATION.md Section 12 and API.md Section 8.
"""

from __future__ import annotations

import json
from typing import ClassVar

from behave_lint import __version__
from behave_lint.models.enums import Severity
from behave_lint.models.lint_result import LintResult
from behave_lint.reporters.base import Reporter

SARIF_VERSION = "2.1.0"
SARIF_SCHEMA = (
    "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/"
    "Schemata/sarif-schema-2.1.0.json"
)

_SEVERITY_TO_LEVEL: dict[Severity, str] = {
    Severity.ERROR: "error",
    Severity.WARNING: "warning",
    Severity.INFO: "note",
    Severity.OFF: "none",
}


class SARIFReporter(Reporter):
    """SARIF v2.1.0 output for GitHub Code Scanning integration."""

    name: ClassVar[str] = "sarif"
    supports_file_output: ClassVar[bool] = True
    supports_stdout: ClassVar[bool] = True

    @staticmethod
    def _build_rules(result: LintResult) -> list[dict[str, object]]:
        """Build the SARIF rules array from diagnostics.

        Args:
            result: The lint result.

        Returns:
            A list of rule descriptor dictionaries.
        """
        seen: set[str] = set()
        rules: list[dict[str, object]] = []

        for diag in result.diagnostics:
            if diag.rule_id in seen:
                continue
            seen.add(diag.rule_id)

            rule: dict[str, object] = {
                "id": diag.rule_id,
                "name": diag.rule_id,
                "shortDescription": {"text": diag.message},
                "properties": {
                    "category": diag.category.value,
                },
            }
            if diag.doc_url:
                rule["helpUri"] = diag.doc_url
            rules.append(rule)

        return rules

    @staticmethod
    def _build_results(result: LintResult) -> list[dict[str, object]]:
        """Build the SARIF results array from diagnostics.

        Args:
            result: The lint result.

        Returns:
            A list of result dictionaries.
        """
        results: list[dict[str, object]] = []

        for diag in result.diagnostics:
            region: dict[str, int] = {"startLine": diag.line}
            if diag.column is not None:
                region["startColumn"] = diag.column
            if diag.end_line is not None:
                region["endLine"] = diag.end_line
            if diag.end_column is not None:
                region["endColumn"] = diag.end_column

            location: dict[str, object] = {
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": diag.file_path,
                    },
                    "region": region,
                },
            }

            entry: dict[str, object] = {
                "ruleId": diag.rule_id,
                "level": _SEVERITY_TO_LEVEL.get(diag.severity, "warning"),
                "message": {"text": diag.message},
                "locations": [location],
            }
            if diag.suggestion:
                entry["fixes"] = [
                    {
                        "description": {"text": diag.suggestion},
                    }
                ]
            results.append(entry)

        return results

    def render(self, result: LintResult, output_file: str | None = None) -> None:
        """Render diagnostics to SARIF output.

        Args:
            result: The lint result containing diagnostics and summary.
            output_file: Path to write SARIF to. If None, writes to
                stdout.
        """
        rules = self._build_rules(result)
        results = self._build_results(result)

        sarif = {
            "$schema": SARIF_SCHEMA,
            "version": SARIF_VERSION,
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "behave-lint",
                            "version": __version__,
                            "informationUri": "https://github.com/MathiasPaulenko/behave-lint",
                            "rules": rules,
                        },
                    },
                    "results": results,
                }
            ],
        }

        content = json.dumps(sarif, indent=2, ensure_ascii=False)
        self._write_output(content, output_file)


__all__ = ["SARIF_SCHEMA", "SARIF_VERSION", "SARIFReporter"]
