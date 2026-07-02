"""Correctness rules - BC001-BC499.

Rules that detect definitively wrong structures causing runtime errors
or test failures.

See RULE_TAXONOMY.md Section 3 and IMPLEMENTATION_ROADMAP.md E7.1.
"""

from __future__ import annotations

import re
from typing import Any

from behave_lint.autofix.models import FixEdit
from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import AutoFixCapability, Category, Severity
from behave_lint.models.rule_metadata import RuleExample, RuleMetadata
from behave_lint.rules.base import Rule
from behave_lint.rules.scope import RuleScope

_TAG_PATTERN = re.compile(r"^@[A-Za-z0-9_]+$")


class DuplicateScenarioNamesRule(Rule):
    """BC001: Detect duplicate scenario names within a feature.

    Two scenarios with the same name in the same feature cause ambiguity
    in test execution and reporting. Behave may execute only one of them
    or produce confusing output.
    """

    metadata = RuleMetadata(
        rule_id="BC001",
        name="duplicate-scenario-names",
        title="Duplicate scenario names within a feature",
        description=(
            "Detects scenarios (including scenario outlines) that share "
            "the same name within a single feature file. Duplicate names "
            "cause ambiguity in test execution and reporting."
        ),
        category=Category.CORRECTNESS,
        default_severity=Severity.ERROR,
        motivation=(
            "Duplicate scenario names make it impossible to reliably "
            "target a specific scenario for execution or debugging. "
            "Test reports become ambiguous."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "Feature: Login\n\n"
                    "  Scenario: Successful login\n"
                    "    Given a user\n\n"
                    "  Scenario: Successful login\n"
                    "    Given an admin\n"
                ),
                after=(
                    "Feature: Login\n\n"
                    "  Scenario: Successful user login\n"
                    "    Given a user\n\n"
                    "  Scenario: Successful admin login\n"
                    "    Given an admin\n"
                ),
                description="Rename one of the duplicate scenarios to be unique.",
            ),
        ],
        tags=["scenarios", "naming"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        seen: dict[str, int] = {}
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            name = scenario.name or ""
            if not name:
                continue
            if name in seen:
                diagnostics.append(
                    self.diagnostic(
                        message=(
                            f"Duplicate scenario name '{name}' "
                            f"(first defined at line {seen[name]})"
                        ),
                        node=scenario,
                        suggestion=(
                            "Rename this scenario to have a unique name "
                            "within the feature."
                        ),
                    )
                )
            else:
                location = getattr(scenario, "location", None)
                line = getattr(location, "line", 1) if location else 1
                seen[name] = line

        return diagnostics


class EmptyFeatureRule(Rule):
    """BC002: Detect feature files with no scenarios.

    A feature file without any scenarios (or outlines) contributes
    nothing to the test suite and may indicate an incomplete or
    abandoned feature.
    """

    metadata = RuleMetadata(
        rule_id="BC002",
        name="empty-feature",
        title="Feature file has no scenarios",
        description=(
            "Detects feature files that contain no scenarios or "
            "scenario outlines. An empty feature file may indicate "
            "an incomplete or abandoned feature."
        ),
        category=Category.CORRECTNESS,
        default_severity=Severity.ERROR,
        motivation=(
            "Empty feature files add noise to the test suite without "
            "providing any test coverage. They may confuse CI systems "
            "that expect at least one scenario per feature."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before="Feature: User Management\n",
                after=(
                    "Feature: User Management\n\n"
                    "  Scenario: Create a user\n"
                    "    Given no users exist\n"
                    "    When I create a user\n"
                    "    Then a user should exist\n"
                ),
                description="Add at least one scenario to the feature.",
            ),
        ],
        tags=["feature", "completeness"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        scenarios = list(feature.all_scenarios())
        if not scenarios:
            return [
                self.diagnostic(
                    message="Feature has no scenarios or scenario outlines",
                    node=feature,
                    suggestion=(
                        "Add at least one scenario to this feature, or "
                        "remove the file if it is no longer needed."
                    ),
                )
            ]
        return []


class ScenarioOutlineWithoutExamplesRule(Rule):
    """BC003: Detect scenario outlines without Examples tables.

    A Scenario Outline without at least one Examples table cannot
    execute — behave will report an error at runtime.
    """

    metadata = RuleMetadata(
        rule_id="BC003",
        name="scenario-outline-without-examples",
        title="Scenario Outline has no Examples table",
        description=(
            "Detects Scenario Outlines that lack at least one Examples "
            "table. A Scenario Outline without Examples cannot execute."
        ),
        category=Category.CORRECTNESS,
        default_severity=Severity.ERROR,
        motivation=(
            "A Scenario Outline without Examples is a runtime error "
            "in behave. The outline placeholders cannot be resolved "
            "without example data."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "Feature: Data\n\n"
                    "  Scenario Outline: Processing <item>\n"
                    "    Given a <item>\n"
                    "    Then it is processed\n"
                ),
                after=(
                    "Feature: Data\n\n"
                    "  Scenario Outline: Processing <item>\n"
                    "    Given a <item>\n"
                    "    Then it is processed\n\n"
                    "    Examples:\n"
                    "      | item |\n"
                    "      | box  |\n"
                    "      | bag  |\n"
                ),
                description="Add an Examples table with at least one row.",
            ),
        ],
        tags=["scenario-outline", "examples"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            examples = getattr(scenario, "examples", None)
            if examples is None:
                continue

            if not examples:
                diagnostics.append(
                    self.diagnostic(
                        message=(
                            f"Scenario Outline '{scenario.name}' has no Examples table"
                        ),
                        node=scenario,
                        suggestion=(
                            "Add at least one Examples block with a "
                            "table containing header and data rows."
                        ),
                    )
                )

        return diagnostics


class InvalidTagSyntaxRule(Rule):
    """BC004: Detect tags with invalid syntax.

    Tags must start with '@' followed by alphanumeric characters
    and underscores. Invalid tag syntax can cause parsing issues
    or be silently ignored by behave.
    """

    metadata = RuleMetadata(
        rule_id="BC004",
        name="invalid-tag-syntax",
        title="Tag does not follow valid syntax",
        description=(
            "Detects tags that do not follow the valid syntax: "
            "@ followed by alphanumeric characters and underscores."
        ),
        category=Category.CORRECTNESS,
        default_severity=Severity.ERROR,
        motivation=(
            "Invalid tag syntax can cause parsing issues or result "
            "in tags being silently ignored by behave, leading to "
            "incorrect test selection."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "Feature: Test\n\n"
                    "  @invalid tag\n"
                    "  Scenario: A scenario\n"
                    "    Given a step\n"
                ),
                after=(
                    "Feature: Test\n\n"
                    "  @invalid_tag\n"
                    "  Scenario: A scenario\n"
                    "    Given a step\n"
                ),
                description="Replace spaces and special characters with underscores.",
            ),
        ],
        tags=["tags", "syntax"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        all_tags: list[Any] = []

        feature_tags = getattr(feature, "tags", [])
        if feature_tags:
            all_tags.extend(feature_tags)

        for scenario in feature.all_scenarios():
            scenario_tags = getattr(scenario, "tags", [])
            if scenario_tags:
                all_tags.extend(scenario_tags)

            examples = getattr(scenario, "examples", None)
            if examples:
                for example in examples:
                    example_tags = getattr(example, "tags", [])
                    if example_tags:
                        all_tags.extend(example_tags)

        for tag in all_tags:
            tag_name = getattr(tag, "name", str(tag))
            if not _TAG_PATTERN.match(tag_name):
                diagnostics.append(
                    self.diagnostic(
                        message=(
                            f"Invalid tag syntax: '{tag_name}'. "
                            "Tags must start with '@' followed by "
                            "alphanumeric characters and underscores."
                        ),
                        node=tag,
                        suggestion=(
                            "Use only letters, numbers, and underscores "
                            "after the '@' symbol."
                        ),
                    )
                )

        return diagnostics

    def get_fixes(
        self, feature: Any, config: Config, diagnostics: list[Diagnostic]
    ) -> list[FixEdit]:
        from pathlib import Path

        fixes: list[FixEdit] = []
        file_path = getattr(feature, "file_path", None)
        if not file_path:
            location = getattr(feature, "location", None)
            if location is not None:
                file_path = getattr(location, "filename", None)
        if not file_path:
            return fixes

        try:
            content = Path(file_path).read_text(encoding="utf-8")
            lines = content.splitlines(keepends=True)
        except OSError:
            return fixes

        diag_lines = {d.line for d in diagnostics if d.rule_id == "BC004"}

        all_tags: list[Any] = []
        feature_tags = getattr(feature, "tags", [])
        if feature_tags:
            all_tags.extend(feature_tags)
        for scenario in feature.all_scenarios():
            scenario_tags = getattr(scenario, "tags", [])
            if scenario_tags:
                all_tags.extend(scenario_tags)
            examples = getattr(scenario, "examples", None)
            if examples:
                for example in examples:
                    example_tags = getattr(example, "tags", [])
                    if example_tags:
                        all_tags.extend(example_tags)

        for tag in all_tags:
            tag_name = getattr(tag, "name", str(tag))
            if _TAG_PATTERN.match(tag_name):
                continue

            tag_line = getattr(tag, "line", None)
            if tag_line is None:
                loc = getattr(tag, "location", None)
                if loc is not None:
                    tag_line = getattr(loc, "line", None)
            if tag_line is None or tag_line not in diag_lines:
                continue

            idx = tag_line - 1
            if idx < 0 or idx >= len(lines):
                continue

            old_line = lines[idx]
            without_at = tag_name[1:] if tag_name.startswith("@") else tag_name
            fixed = re.sub(r"[^A-Za-z0-9_]", "_", without_at)
            new_tag = f"@{fixed}"

            if tag_name in old_line:
                new_line = old_line.replace(tag_name, new_tag)
                fixes.append(
                    FixEdit(
                        file_path=file_path,
                        start_line=tag_line,
                        end_line=tag_line,
                        old_text=old_line,
                        new_text=new_line,
                        safety=AutoFixCapability.SAFE,
                        rule_id="BC004",
                        diagnostic_line=tag_line,
                    )
                )

        return fixes


class DuplicateFeatureNamesRule(Rule):
    """BC005: Detect duplicate feature names across files.

    Two feature files with the same feature name can cause confusion
    in test reports and make it difficult to identify which feature
    failed.
    """

    metadata = RuleMetadata(
        rule_id="BC005",
        name="duplicate-feature-names",
        title="Duplicate feature names across files",
        description=(
            "Detects feature files that share the same feature name. "
            "Duplicate feature names cause confusion in test reports."
        ),
        category=Category.CORRECTNESS,
        default_severity=Severity.ERROR,
        motivation=(
            "Duplicate feature names make it difficult to identify "
            "which feature failed in test reports, especially in CI "
            "environments with many feature files."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "# file1.feature\n"
                    "Feature: Login\n\n"
                    "# file2.feature\n"
                    "Feature: Login\n"
                ),
                after=(
                    "# file1.feature\n"
                    "Feature: User Login\n\n"
                    "# file2.feature\n"
                    "Feature: Admin Login\n"
                ),
                description="Rename one of the duplicate features.",
            ),
        ],
        tags=["feature", "naming", "cross-file"],
    )

    scope = RuleScope.CROSS_FILE

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        if not hasattr(feature, "features"):
            return []

        seen: dict[str, str] = {}
        diagnostics: list[Diagnostic] = []

        for feat in feature.features:
            name = feat.name or ""
            if not name:
                continue
            if name in seen:
                diagnostics.append(
                    self.diagnostic(
                        message=(
                            f"Duplicate feature name '{name}' "
                            f"(first defined in {seen[name]})"
                        ),
                        node=feat,
                        suggestion=(
                            "Rename this feature to have a unique name "
                            "across all feature files."
                        ),
                    )
                )
            else:
                location = getattr(feat, "location", None)
                filename = getattr(location, "filename", "") if location else ""
                seen[name] = filename

        return diagnostics


class InvalidExampleTableStructureRule(Rule):
    """BC006: Detect invalid example table structure.

    Example tables must have at least one header row and one data row.
    Tables with empty headers or no data rows will cause runtime errors.
    """

    metadata = RuleMetadata(
        rule_id="BC006",
        name="invalid-example-table",
        title="Example table has invalid structure",
        description=(
            "Detects Examples tables with empty headers, no data rows, "
            "or mismatched column counts between headers and data rows."
        ),
        category=Category.CORRECTNESS,
        default_severity=Severity.ERROR,
        motivation=(
            "Invalid example tables cause runtime errors in behave. "
            "Empty headers make columns unreferenceable, and column "
            "count mismatches indicate data integrity issues."
        ),
        since="0.5.0",
        examples=[
            RuleExample(
                before=(
                    "  Scenario Outline: Test <value>\n"
                    "    Given a <value>\n\n"
                    "    Examples:\n"
                    "      | |\n"
                    "      | a |\n"
                ),
                after=(
                    "  Scenario Outline: Test <value>\n"
                    "    Given a <value>\n\n"
                    "    Examples:\n"
                    "      | value |\n"
                    "      | a     |\n"
                ),
                description="Provide a non-empty header name for each column.",
            ),
        ],
        tags=["examples", "table", "syntax"],
    )

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for scenario in feature.all_scenarios():
            examples = getattr(scenario, "examples", None)
            if not examples:
                continue

            for example in examples:
                table = getattr(example, "table", None)
                if table is None:
                    continue

                headers = getattr(table, "headers", [])
                rows = getattr(table, "rows", [])

                if not headers:
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Examples table in '{scenario.name}' has no header row"
                            ),
                            node=table,
                            suggestion=(
                                "Add a header row with column names "
                                "matching the placeholders in the "
                                "scenario outline."
                            ),
                        )
                    )
                    continue

                empty_headers = [h for h in headers if not h or not h.strip()]
                if empty_headers:
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Examples table in '{scenario.name}' "
                                "has empty column headers"
                            ),
                            node=table,
                            suggestion=(
                                "Provide a non-empty name for each "
                                "column in the header row."
                            ),
                        )
                    )

                if not rows:
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Examples table in '{scenario.name}' has no data rows"
                            ),
                            node=table,
                            suggestion=(
                                "Add at least one data row to the Examples table."
                            ),
                        )
                    )

                header_count = len(headers)
                for row in rows:
                    cells = getattr(row, "cells", [])
                    if len(cells) != header_count:
                        diagnostics.append(
                            self.diagnostic(
                                message=(
                                    f"Row in Examples table of "
                                    f"'{scenario.name}' has "
                                    f"{len(cells)} columns but header "
                                    f"has {header_count}"
                                ),
                                node=row,
                                suggestion=(
                                    "Ensure each data row has the same "
                                    "number of columns as the header row."
                                ),
                            )
                        )

        return diagnostics


__all__ = [
    "DuplicateFeatureNamesRule",
    "DuplicateScenarioNamesRule",
    "EmptyFeatureRule",
    "InvalidExampleTableStructureRule",
    "InvalidTagSyntaxRule",
    "ScenarioOutlineWithoutExamplesRule",
]
