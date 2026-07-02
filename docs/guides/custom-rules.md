# Custom Rules

How to write and register custom rules for `behave-lint`.

## Rule base class

Custom rules inherit from `behave_lint.rules.base.Rule` and implement
a `check` method that receives a `behave_model` feature node and a
`Config` object, returning a list of `Diagnostic` objects.

```python
from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.rule_metadata import RuleMetadata, RuleExample
from behave_lint.rules.base import Rule


class NoGivenInThenRule(Rule):
    """MY001: Detect 'Given' steps appearing after 'Then' steps."""

    metadata = RuleMetadata(
        rule_id="MY001",
        name="no-given-in-then",
        title="Given steps should not appear after Then steps",
        description=(
            "Detects Given steps that appear after a Then step, "
            "which breaks the Given-When-Then convention."
        ),
        category=Category.STYLE,
        default_severity=Severity.WARNING,
        motivation="Given steps after Then steps are confusing.",
        since="1.0.0",
        examples=[
            RuleExample(
                before=(
                    "  Scenario: Test\n"
                    "    Given a user\n"
                    "    Then I see results\n"
                    "    Given another user\n"
                ),
                after=(
                    "  Scenario: Test\n"
                    "    Given a user\n"
                    "    And another user\n"
                    "    Then I see results\n"
                ),
                description="Move Given steps before Then.",
            ),
        ],
        tags=["steps", "ordering", "custom"],
    )

    def check(self, feature, config: Config) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for scenario in feature.all_scenarios():
            seen_then = False
            for step in getattr(scenario, "steps", []):
                keyword = getattr(step, "keyword", "").strip().lower()
                if keyword == "then":
                    seen_then = True
                if seen_then and keyword == "given":
                    diagnostics.append(
                        self.diagnostic(
                            message=(
                                f"Given step '{step.name}' appears "
                                "after a Then step"
                            ),
                            node=step,
                            suggestion="Move Given steps before Then.",
                        )
                    )
        return diagnostics
```

## Registration

Register rules via the `behave_lint.rules` entry point in your
`pyproject.toml`:

```toml
[project.entry-points."behave_lint.rules"]
no-given-in-then = "my_package.rules:NoGivenInThenRule"
```

## Auto-fix support

To add auto-fix support, implement the `get_fixes` method:

```python
from behave_lint.autofix.models import FixEdit
from behave_lint.models.enums import AutoFixCapability


def get_fixes(self, feature, config, diagnostics):
    # Return list[FixEdit] for safe or unsafe fixes
    ...
```

See the [Auto-Fix guide](../usage/auto-fix.md) for details.

## Rule base class API

The `Rule` base class provides:

| Attribute/Method | Type | Description |
|-----------------|------|-------------|
| `metadata` | `RuleMetadata` | Rule identity and docs (required). |
| `scope` | `RuleScope` | `SINGLE_FILE` (default) or `CROSS_FILE`. |
| `default_params` | `dict[str, Any]` | Default configurable parameters. |
| `check(feature, config)` | `list[Diagnostic]` | Analyze and return diagnostics (required). |
| `get_fixes(feature, config, diagnostics)` | `list[FixEdit]` | Return auto-fix edits (optional). |
| `diagnostic(message, node, ...)` | `Diagnostic` | Create a diagnostic with metadata pre-filled. |
| `rule_id` | `str` | Property — rule ID from metadata. |
| `category` | `Category` | Property — category from metadata. |
| `default_severity` | `Severity` | Property — default severity from metadata. |

### `diagnostic()` parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `message` | `str` | What is wrong (factual statement). |
| `node` | `HasLocation \| None` | A behave-model element with `file_path` and `line`. |
| `line` | `int \| None` | Explicit line number (overrides node). |
| `column` | `int \| None` | Explicit column number. |
| `file_path` | `str \| None` | Explicit file path (overrides node). |
| `end_line` | `int \| None` | End line for multi-line diagnostics. |
| `end_column` | `int \| None` | End column for multi-line diagnostics. |
| `suggestion` | `str \| None` | How to fix it (actionable guidance). |
| `doc_url` | `str \| None` | URL to rule documentation. |
| `severity` | `Severity \| None` | Override severity (defaults to rule's default). |

## RuleMetadata fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rule_id` | `str` | Yes | Stable, unique identifier (e.g., `"BC001"`). |
| `name` | `str` | Yes | Short, human-readable, kebab-case name. |
| `title` | `str` | Yes | One-line summary for CLI and docs. |
| `description` | `str` | Yes | One-paragraph description of what the rule checks. |
| `category` | `Category` | Yes | Rule category enum. |
| `default_severity` | `Severity` | Yes | Default severity when enabled. |
| `motivation` | `str` | Yes | Why the rule exists — the problem it solves. |
| `since` | `str` | Yes | Version when the rule was introduced. |
| `examples` | `list[RuleExample]` | No | Before/after examples for documentation. |
| `auto_fix` | `AutoFixCapability` | No | Auto-fix capability. Default: `NONE`. |
| `tags` | `list[str]` | No | Free-form tags for filtering and grouping. |
| `references` | `list[str]` | No | External references (URLs, standards). |
| `configurable` | `bool` | No | Whether the rule accepts parameters. Default: `False`. |
| `experimental` | `bool` | No | Whether the rule is experimental. Default: `False`. |
| `deprecated` | `bool` | No | Whether the rule is deprecated. Default: `False`. |
| `deprecated_version` | `str \| None` | No | Version in which deprecated. |
| `replaced_by` | `str \| None` | No | Rule ID that replaces this one. |
| `aliases` | `list[str]` | No | Alternative names for backward compatibility. |
| `dependencies` | `list[str]` | No | Rule IDs that must execute before this rule. |
| `conflicts` | `list[str]` | No | Rule IDs that conflict with this rule. |
| `doc_url` | `str \| None` | No | URL to rule documentation. |
| `author` | `str \| None` | No | Author or maintainer. |
| `min_version` | `str \| None` | No | Minimum behave-lint version required. |
| `estimated_fix_cost` | `FixCost` | No | Estimated effort to fix. Default: `LOW`. |
| `performance_impact` | `PerformanceImpact` | No | Execution cost. Default: `NEGLIGIBLE`. |
| `educational_value` | `EducationalValue` | No | Pedagogical value. Default: `NONE`. |

## RuleScope

| Value | Description |
|-------|-------------|
| `SINGLE_FILE` | Rule analyzes one feature file at a time. Parallelized across (rule, file) pairs. |
| `CROSS_FILE` | Rule analyzes the entire project at once. Executed sequentially after all single-file rules. |

## FixEdit fields

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | `str` | Path to the file to modify. |
| `start_line` | `int` | 1-based start line of the region to replace. |
| `end_line` | `int` | 1-based end line (inclusive). |
| `old_text` | `str` | Original text being replaced (for validation). |
| `new_text` | `str` | Replacement text. |
| `safety` | `AutoFixCapability` | `SAFE` or `UNSAFE`. |
| `rule_id` | `str` | The rule that produced this fix. |
| `diagnostic_line` | `int` | The diagnostic line number that triggered this fix. |

## Testing

Write unit tests that:

1. Create a `.feature` file with the violation.
2. Load it with `load_features`.
3. Run `rule.check(feature, config)`.
4. Assert the expected diagnostics.

See the existing rule tests in `tests/unit/behave_lint/rules/` for
examples.
