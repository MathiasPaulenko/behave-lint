# behave-lint — Public API Specification

> **Status:** Canonical public API specification.
> **Audience:** Library users, plugin authors, reporter authors, CLI
> users, and downstream integrators.
> **Scope:** Every public interface exposed by behave-lint. This
> document defines *what* is public, *how* it is used, and *why* it
> exists. It does not define internal implementation, architecture, or
> folder structure.
> **Dependencies:** This document follows VISION.md, SPECIFICATION.md,
> and ARCHITECTURE.md. If inconsistencies are detected, they are
> reported explicitly in **Appendix A**.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [API Goals](#2-api-goals)
3. [API Surface](#3-api-surface)
4. [Core Objects](#4-core-objects)
5. [Main Functions](#5-main-functions)
6. [Configuration API](#6-configuration-api)
7. [Rule SDK](#7-rule-sdk)
8. [Reporter SDK](#8-reporter-sdk)
9. [Plugin API](#9-plugin-api)
10. [CLI API](#10-cli-api)
11. [Error API](#11-error-api)
12. [Diagnostic API](#12-diagnostic-api)
13. [Auto-Fix API](#13-auto-fix-api)
14. [Extension Points](#14-extension-points)
15. [Versioning](#15-versioning)
16. [Examples](#16-examples)
17. [Future API](#17-future-api)

---

## 1. Executive Summary

### API Philosophy

behave-lint exposes a **minimal, layered public API** designed around
three entry points: the **CLI** for command-line use, the **Python
library** for programmatic embedding, and the **Plugin SDK** for
extension. Each layer is self-contained — the CLI delegates to the
library, the library delegates to the engine, and plugins extend the
library through stable interfaces.

The API is designed to be **obvious to a Python developer who has
never used the tool before**. A user who installs behave-lint and
runs `behave-lint features/` should get useful output with zero
configuration. A developer who imports `behave_lint` should be able
to lint a project in three lines of code. A plugin author should be
able to write a rule by subclassing one class and implementing one
method.

### Design Principles

- **Pythonic first.** The API uses standard Python conventions:
  keyword arguments, context managers, dataclasses, enums, and
  `__repr__`/`__str__` for debugging. No custom DSLs, no XML-style
  configuration, no Java-style factories.

- **Explicit over implicit.** No hidden state, no global registries
  accessible via side effects, no monkey-patching. If a user wants
  rules, they ask for rules. If a user wants diagnostics, they run
  the linter and get diagnostics.

- **Stable surface, extensible interior.** The public API is small
  (few objects, few functions). Extension is through well-defined
  interfaces (Rule, Reporter, Plugin) that are also public and
  stable. Internal implementation details are private (underscore-
  prefixed or not exported).

- **Type-safe.** All public objects use type hints. The API is
  designed for IDE autocomplete and static type checking (mypy,
  pyright). Enums are used for finite value sets. Dataclasses are
  used for structured data.

- **Fail clearly.** Errors are specific, typed, and actionable. No
  generic `Exception` raises. Every error class communicates *what*
  went wrong and *how to fix it*.

### Validation

**Why this approach?** A minimal, layered API is the easiest to
learn, the easiest to maintain, and the most resistant to breaking
changes. Users interact with the layer appropriate to their needs —
CLI users never see the library API; library users never see the
plugin SDK unless they need it.

**Could it remain stable for five years?** Yes. The API surface is
small and focused. New rules, new reporters, and new output formats
do not require API changes. Future features (auto-fix, LSP, watch
mode) are additive, not breaking.

---

## 2. API Goals

### Simplicity

The API must be usable without reading documentation. A developer
who types `import behave_lint` and uses tab-completion should be
able to discover the available functions and objects.

**Target:** Zero-to-first-diagnostic in under 2 minutes for a
developer who has never used the tool.

### Stability

The public API follows Semantic Versioning 2.0.0. Within a major
version:

- No public object is removed.
- No public function signature changes incompatibly.
- No public field is removed from a dataclass.
- New fields may be added to dataclasses (with defaults).
- New functions and objects may be added.
- New enum members may be added (users must handle unknown members).

### Extensibility

Extension is through three public interfaces:

- **Rule:** Subclass to create a new lint rule.
- **Reporter:** Implement to create a new output format.
- **Plugin:** Package-level entry point to distribute extensions.

These interfaces are stable and versioned. A plugin written for v1.0
works with v1.x without modification.

### Readability

Public objects have clear names: `Linter`, `Diagnostic`, `Severity`,
`Rule`, `Reporter`, `Config`. No abbreviations, no jargon, no
internal naming leaking into the public surface.

### Testability

The library API is designed for testability:

- All functions are pure (same inputs → same outputs).
- No file system side effects unless explicitly requested.
- Configuration is an object, not a global.
- The linter can be instantiated with an in-memory configuration.

---

## 3. API Surface

### Entry Points

| Entry point | Audience | Stability |
|---|---|---|
| CLI (`behave-lint` command) | End users, CI | Stable |
| Python library (`import behave_lint`) | Integrators, library users | Stable |
| Rule SDK (`behave_lint.rules.Rule`) | Rule authors, plugin authors | Stable |
| Reporter SDK (`behave_lint.reporters.Reporter`) | Reporter authors | Stable |
| Plugin API (entry points) | Plugin authors | Stable |
| Configuration API (`behave_lint.Config`) | All | Stable |
| Diagnostic API (`behave_lint.Diagnostic`) | All | Stable |
| Error API (`behave_lint.errors`) | All | Stable |
| Auto-Fix API | Future (v1.1+) | Reserved |
| LSP API | Future (v2.0+) | Reserved |

### Public Namespace

The public namespace is `behave_lint`. Everything importable from
`behave_lint` or its documented subpackages is public. Everything
else (underscore-prefixed modules, undocumented subpackages) is
private and may change without notice.

**Public subpackages:**

- `behave_lint` — top-level objects and functions
- `behave_lint.rules` — Rule base class, metadata, built-in rule IDs
- `behave_lint.reporters` — Reporter interface, built-in reporters
- `behave_lint.errors` — Error hierarchy
- `behave_lint.config` — Configuration objects

---

## 4. Core Objects

### Severity

**Purpose:** Represents the importance level of a diagnostic.

**Type:** Enum.

**Members:**

| Member | Value | Description |
|---|---|---|
| `ERROR` | `"error"` | Must be fixed; causes non-zero exit code. |
| `WARNING` | `"warning"` | Should be fixed; does not cause non-zero exit by default. |
| `INFO` | `"info"` | Informational; never affects exit code. |
| `OFF` | `"off"` | Rule is disabled; no diagnostics are produced. |

**Lifecycle:** Immutable enum. New members may be added in minor
versions (e.g., `HINT` in the future). Consumers must handle unknown
members gracefully.

**Usage:**

```python
from behave_lint import Severity

diag = Diagnostic(
    rule_id="BC001",
    severity=Severity.ERROR,
    message="Duplicate scenario name",
    file_path="features/login.feature",
    line=15,
)
```

**Validation:** Why public? Severity is used in configuration, rule
metadata, diagnostics, and output. It is the most fundamental concept
in the tool. Could it remain stable for five years? Yes — the four
levels are standard across all linters (ESLint, Ruff, Clippy).

### Category

**Purpose:** Groups rules by concern.

**Type:** Enum.

**Members:**

| Member | Value | Description |
|---|---|---|
| `CORRECTNESS` | `"correctness"` | Definitively wrong structures. |
| `STYLE` | `"style"` | Stylistic conventions. |
| `COMPLEXITY` | `"complexity"` | Overly complex specifications. |
| `CONSISTENCY` | `"consistency"` | Cross-file consistency. |
| `PEDANTIC` | `"pedantic"` | Strict best practices (opt-in). |
| `STEP_DEFINITIONS` | `"step_definitions"` | Cross-reference with step defs. |

**Lifecycle:** Immutable enum. New categories may be added in minor
versions.

**Validation:** Why public? Category is used in rule metadata,
diagnostics, and output. It drives documentation organization and
CLI filtering. Stable for five years? Yes — these categories are
comprehensive and aligned with SPECIFICATION.md.

### Diagnostic

**Purpose:** Represents a single issue found by a rule.

**Type:** Frozen dataclass (immutable).

**Fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `rule_id` | `str` | Yes | Stable rule identifier (e.g., `"BC001"`). |
| `severity` | `Severity` | Yes | Severity level. |
| `message` | `str` | Yes | Human-readable description. |
| `file_path` | `str` | Yes | Path to the `.feature` file. |
| `line` | `int` | Yes | 1-based line number. |
| `column` | `int \| None` | No | 1-based column number. |
| `end_line` | `int \| None` | No | End line for multi-line issues. |
| `end_column` | `int \| None` | No | End column for multi-line issues. |
| `suggestion` | `str \| None` | No | Human-readable fix suggestion. |
| `doc_url` | `str \| None` | No | URL to rule documentation. |
| `category` | `Category` | Yes | Rule category. |

**Lifecycle:** Created by rules during execution. Immutable once
created. Passed to reporters for output. Never modified by the
engine or reporters.

**Relationships:** A `Linter` produces a list of `Diagnostic`
objects. A `Reporter` consumes them. A `Rule` creates them.

**Usage:**

```python
from behave_lint import Diagnostic, Severity, Category

diag = Diagnostic(
    rule_id="BC001",
    severity=Severity.ERROR,
    message="Duplicate scenario name: 'Login successful'",
    file_path="features/login.feature",
    line=15,
    category=Category.CORRECTNESS,
    suggestion="Rename one of the scenarios to be unique.",
    doc_url="https://behave-lint.dev/rules/BC001",
)
```

**Validation:** Why public? Diagnostics are the primary output of
the tool. They are consumed by reporters, displayed to users, and
serialized to JSON/SARIF. The field set matches ARCHITECTURE.md
Section 9 exactly. Stable for five years? Yes — new fields may be
added (with defaults), but existing fields will not change or be
removed.

### Config

**Purpose:** Represents the resolved configuration for a lint run.

**Type:** Frozen dataclass (immutable).

**Fields (key subset):**

| Field | Type | Default | Description |
|---|---|---|---|
| `select` | `list[str]` | `[]` | Rule IDs to enable (empty = all defaults). |
| `ignore` | `list[str]` | `[]` | Rule IDs to disable. |
| `severity_overrides` | `dict[str, Severity]` | `{}` | Per-rule severity overrides. |
| `output` | `str` | `"console"` | Output format(s), comma-separated. |
| `output_file` | `str \| None` | `None` | Output file path (None = stdout). |
| `paths` | `list[str]` | `["features/"]` | Default paths to lint. |
| `step_definitions` | `str \| None` | `None` | Step definitions directory. |
| `cache` | `bool` | `True` | Enable caching. |
| `cache_dir` | `str` | `".behave-lint-cache"` | Cache directory. |
| `plugins` | `dict[str, bool]` | `{}` | Plugin enable/disable. |
| `rule_params` | `dict[str, dict]` | `{}` | Per-rule parameters. |

**Lifecycle:** Created by `load_config()` or `Config()`. Immutable
once created. Passed to `Linter` at construction time.

**Usage:**

```python
from behave_lint import Config, Severity

config = Config(
    select=["BC001", "BS001"],
    ignore=["BX001"],
    severity_overrides={"BS001": Severity.INFO},
    output="json",
    output_file="lint-results.json",
)
```

**Validation:** Why public? Configuration is the primary way users
customize the tool. The `Config` object is the programmatic
equivalent of `pyproject.toml [tool.behave-lint]`. Stable for five
years? Yes — new fields may be added with defaults; existing fields
will not change.

### LintResult

**Purpose:** Represents the result of a lint run.

**Type:** Frozen dataclass (immutable).

**Fields:**

| Field | Type | Description |
|---|---|---|
| `diagnostics` | `list[Diagnostic]` | All diagnostics, sorted by file/line/rule. |
| `summary` | `LintSummary` | Execution summary. |
| `exit_code` | `int` | Exit code (0, 1, or 2). |

**Lifecycle:** Created by `Linter.lint()`. Returned to the caller.
Immutable.

**Usage:**

```python
result = linter.lint("features/")
for diag in result.diagnostics:
    print(f"{diag.file_path}:{diag.line}: {diag.message}")
print(f"Exit code: {result.exit_code}")
```

### LintSummary

**Purpose:** Summarizes a lint run for reporting.

**Type:** Frozen dataclass (immutable).

**Fields:**

| Field | Type | Description |
|---|---|---|
| `total_files` | `int` | Number of files analyzed. |
| `files_with_issues` | `int` | Number of files with at least one diagnostic. |
| `total_diagnostics` | `int` | Total diagnostics produced. |
| `error_count` | `int` | Diagnostics with severity ERROR. |
| `warning_count` | `int` | Diagnostics with severity WARNING. |
| `info_count` | `int` | Diagnostics with severity INFO. |
| `rules_executed` | `int` | Number of rules that ran. |
| `duration_ms` | `float` | Execution time in milliseconds. |
| `cache_hits` | `int` | Number of cache hits. |
| `cache_misses` | `int` | Number of cache misses. |

### RuleMetadata

**Purpose:** Describes a rule's identity, documentation, and
configuration.

**Type:** Frozen dataclass (immutable).

**Fields:**

| Field | Type | Description |
|---|---|---|
| `rule_id` | `str` | Stable rule identifier. |
| `name` | `str` | Short human-readable name. |
| `description` | `str` | One-paragraph description. |
| `category` | `Category` | Rule category. |
| `default_severity` | `Severity` | Default severity. |
| `since` | `str` | Version when introduced. |
| `deprecated` | `bool` | Whether the rule is deprecated. |
| `replaced_by` | `str \| None` | Rule ID that replaces this one. |
| `auto_fix` | `AutoFixCapability` | Auto-fix capability. |
| `examples` | `list[RuleExample]` | Before/after examples. |
| `doc_url` | `str \| None` | URL to documentation. |

### AutoFixCapability

**Purpose:** Declares a rule's auto-fix support.

**Type:** Enum.

**Members:**

| Member | Value | Description |
|---|---|---|
| `NONE` | `"none"` | Not fixable. |
| `SAFE` | `"safe"` | Fix does not change semantics. |
| `UNSAFE` | `"unsafe"` | Fix may change semantics. |

---

## 5. Main Functions

### `lint()`

**Purpose:** Lint feature files and return diagnostics.

**Signature:**

```python
def lint(
    paths: str | list[str] | None = None,
    *,
    config: Config | None = None,
    select: list[str] | None = None,
    ignore: list[str] | None = None,
    output: str | None = None,
    output_file: str | None = None,
) -> LintResult: ...
```

**Inputs:**

- `paths`: File or directory paths to lint. Defaults to `config.paths`
  or `"features/"`.
- `config`: A resolved `Config` object. If `None`, loads configuration
  from `pyproject.toml` with defaults.
- `select`, `ignore`, `output`, `output_file`: Convenience overrides
  that merge with `config`. Explicit arguments take precedence.

**Outputs:** `LintResult` containing diagnostics, summary, and exit
code.

**Exceptions:**

- `ConfigError`: If configuration is invalid.
- `NoFilesFoundError`: If no `.feature` files are found in paths.
- `InternalError`: For unexpected internal failures.

**Examples:**

```python
import behave_lint

# Zero-config: use pyproject.toml or defaults
result = behave_lint.lint("features/")

# Programmatic config
result = behave_lint.lint(
    "features/",
    select=["BC001", "BS001"],
    output="json",
    output_file="results.json",
)

if result.exit_code != 0:
    for diag in result.diagnostics:
        print(diag)
```

**Best practices:**

- Pass `config` explicitly for testability.
- Use `Linter` class (below) for repeated runs (reuses cache).
- Do not catch `InternalError` in application code — let it
  propagate.

### `load_config()`

**Purpose:** Load and resolve configuration from all sources.

**Signature:**

```python
def load_config(
    *,
    config_path: str | None = None,
    overrides: dict | None = None,
) -> Config: ...
```

**Inputs:**

- `config_path`: Explicit path to a `pyproject.toml`. If `None`,
  searches the current directory and ancestors.
- `overrides`: Dictionary of configuration overrides (same keys as
  `Config` fields).

**Outputs:** `Config` object.

**Exceptions:**

- `ConfigError`: If configuration is invalid (unknown key, invalid
  value, unknown rule ID).

**Examples:**

```python
from behave_lint import load_config

config = load_config()
config = load_config(config_path="pyproject.toml")
config = load_config(overrides={"select": ["BC001"], "output": "json"})
```

### `list_rules()`

**Purpose:** Return metadata for all registered rules.

**Signature:**

```python
def list_rules(
    *,
    category: Category | None = None,
    severity: Severity | None = None,
    include_deprecated: bool = False,
) -> list[RuleMetadata]: ...
```

**Outputs:** List of `RuleMetadata` objects, sorted by rule ID.

**Examples:**

```python
from behave_lint import list_rules, Category

for rule in list_rules(category=Category.CORRECTNESS):
    print(f"{rule.rule_id}: {rule.name}")
```

### `explain_rule()`

**Purpose:** Return detailed documentation for a single rule.

**Signature:**

```python
def explain_rule(rule_id: str) -> RuleMetadata: ...
```

**Exceptions:**

- `UnknownRuleError`: If the rule ID is not registered.

**Examples:**

```python
from behave_lint import explain_rule

rule = explain_rule("BC001")
print(rule.description)
for example in rule.examples:
    print(f"Before: {example.before}")
    print(f"After:  {example.after}")
```

---

## 6. Configuration API

### Configuration Loading

Configuration is loaded from four sources, merged by precedence:

1. CLI arguments (highest)
2. Environment variables (`BEHAVE_LINT_*`)
3. `pyproject.toml` `[tool.behave-lint]`
4. Built-in defaults (lowest)

The `load_config()` function performs this merge and returns a `Config`
object. The `Config` object is the single source of truth for a lint
run — no other component reads configuration sources directly.

### Environment Variables

| Variable | Maps to | Example |
|---|---|---|
| `BEHAVE_LINT_OUTPUT` | `output` | `BEHAVE_LINT_OUTPUT=json` |
| `BEHAVE_LINT_OUTPUT_FILE` | `output_file` | `BEHAVE_LINT_OUTPUT_FILE=results.json` |
| `BEHAVE_LINT_NO_CACHE` | `cache` | `BEHAVE_LINT_NO_CACHE=1` |
| `BEHAVE_LINT_CACHE_DIR` | `cache_dir` | `BEHAVE_LINT_CACHE_DIR=/tmp/cache` |
| `BEHAVE_LINT_TRACE` | (internal) | `BEHAVE_LINT_TRACE=1` |

### Validation

Configuration is validated at load time:

- **Unknown keys:** Warning (forward compatibility).
- **Invalid values:** `ConfigError` with actionable message.
- **Unknown rule IDs:** Warning with fuzzy-match suggestion.
- **Invalid severity values:** `ConfigError`.

### Defaults

| Key | Default |
|---|---|
| `select` | `[]` (all default-enabled rules) |
| `ignore` | `[]` |
| `output` | `"console"` |
| `output_file` | `None` (stdout) |
| `paths` | `["features/"]` |
| `cache` | `True` |
| `cache_dir` | `".behave-lint-cache"` |

### Profiles (Future)

Reserved for future versions:

```toml
[tool.behave-lint]
extends = "strict"   # or "minimal", "recommended"
```

Profiles are predefined configuration bundles. Not implemented in v1.
The `Config` object and `load_config()` function are designed to
support profiles without API changes.

### Validation

**Why is `Config` a frozen dataclass?** Immutability ensures that
configuration does not change during a lint run. This makes the tool
deterministic and testable. The alternative — a mutable config object
— would allow accidental modification during execution.

**Why not a dict?** A dataclass provides type safety, IDE
autocomplete, and validation. A dict is error-prone (typos in keys
are not caught) and harder to document.

---

## 7. Rule SDK

### Rule Base Class

**Purpose:** Base class for all lint rules.

**Contract:** Subclass `Rule`, implement `check()`, and provide
metadata via class attributes.

**Pseudo-code:**

```python
from behave_lint.rules import Rule, RuleMetadata, Severity, Category, AutoFixCapability

class DuplicateScenarioNameRule(Rule):
    """Detects scenarios with duplicate names within a feature."""

    metadata = RuleMetadata(
        rule_id="BC001",
        name="duplicate-scenario-name",
        description="Scenarios within a feature must have unique names.",
        category=Category.CORRECTNESS,
        default_severity=Severity.ERROR,
        since="0.1.0",
        auto_fix=AutoFixCapability.NONE,
    )

    def check(self, feature, config) -> list[Diagnostic]:
        seen = {}
        diagnostics = []
        for scenario in feature.scenarios:
            if scenario.name in seen:
                diagnostics.append(self.diagnostic(
                    message=f"Duplicate scenario name: '{scenario.name}'",
                    node=scenario,
                    suggestion="Rename to be unique within the feature.",
                ))
            seen[scenario.name] = scenario
        return diagnostics
```

### Rule Metadata

Metadata is declared as a class attribute (`metadata`) and must be a
`RuleMetadata` object. The rule engine validates metadata at
registration time.

Required fields: `rule_id`, `name`, `description`, `category`,
`default_severity`, `since`.

### Rule Execution

The `check()` method receives:

- `feature` (or `project` for cross-file rules): The parsed model
  from `behave-model`. Read-only.
- `config`: The resolved `Config` object. Read-only.

Returns: `list[Diagnostic]` (possibly empty).

The `self.diagnostic()` helper method constructs a `Diagnostic` with
the rule's ID, category, and severity pre-filled. Rules only need to
provide `message`, `node` (for location), and optional `suggestion`.

### Rule Scope

Rules declare their scope via a class attribute:

```python
class MyRule(Rule):
    scope = RuleScope.SINGLE_FILE  # default; receives one feature at a time
    # or
    scope = RuleScope.CROSS_FILE   # receives the entire project
```

Single-file rules are parallelized. Cross-file rules run sequentially
after all single-file rules complete.

### Rule Parameters

Rules can declare configurable parameters:

```python
class MaxStepsPerScenarioRule(Rule):
    metadata = RuleMetadata(...)

    default_params = {
        "max_steps": 10,
    }

    def check(self, feature, config) -> list[Diagnostic]:
        max_steps = config.rule_params.get(
            self.metadata.rule_id, {}
        ).get("max_steps", self.default_params["max_steps"])
        ...
```

Users configure parameters in `pyproject.toml`:

```toml
[tool.behave-lint.rules.BX001]
max_steps = 5
```

### Rule Lifecycle

Rules follow the lifecycle defined in SPECIFICATION.md:

- **Experimental:** Opt-in, not in default set.
- **Stable:** Default-enabled (if severity > OFF).
- **Deprecated:** Still functional, emits deprecation warning.
- **Removed:** Rule ID permanently retired.

### Rule Registration

Built-in rules are registered automatically at import time. Plugin
rules are registered via entry points (Section 9).

### Validation

**Why a class instead of a function?** A class carries metadata
naturally (class attributes), supports configuration parameters
(instance attributes), and can implement helper methods
(`self.diagnostic()`). A function would require a separate metadata
mechanism, adding boilerplate.

**Why `check()` instead of `__call__()`?** `check()` is explicit and
discoverable. `__call__()` is implicit and harder to document.

**Stable for five years?** Yes. The `Rule` base class, `check()`
method, and `RuleMetadata` are the minimal interface needed. New
features (auto-fix, dependencies) are additive — new optional methods
with default implementations.

---

## 8. Reporter SDK

### Reporter Interface

**Purpose:** Interface for custom output formats.

**Contract:** Implement `render()` to transform diagnostics into
output.

**Pseudo-code:**

```python
from behave_lint.reporters import Reporter
from behave_lint import LintResult

class MyReporter(Reporter):
    """Custom reporter for my CI system."""

    name = "my-format"

    def render(self, result: LintResult, output_file: str | None) -> None:
        lines = []
        for diag in result.diagnostics:
            lines.append(f"{diag.severity.value}|{diag.rule_id}|{diag.file_path}:{diag.line}|{diag.message}")
        content = "\n".join(lines)

        if output_file:
            Path(output_file).write_text(content)
        else:
            print(content)
```

### Reporter Lifecycle

1. **Discovery:** Reporter is registered (built-in or via plugin entry
   point).
2. **Selection:** User selects reporter via `--output <name>` or
   `Config.output`.
3. **Instantiation:** Reporter is instantiated by the reporting layer.
4. **Rendering:** `render()` is called with the `LintResult` and
   optional output file path.
5. **Completion:** Reporter writes output and returns.

### Reporter Registration

Built-in reporters are registered automatically. Plugin reporters are
registered via entry points:

```toml
# pyproject.toml of a plugin package
[project.entry-points."behave_lint.reporters"]
my-format = "my_plugin.reporter:MyReporter"
```

### Capabilities

Reporters declare capabilities via class attributes:

| Attribute | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | (required) | Unique format name. |
| `supports_file_output` | `bool` | `True` | Can write to a file. |
| `supports_stdout` | `bool` | `True` | Can write to stdout. |
| `supports_streaming` | `bool` | `False` | Can stream large outputs. |

### Serialization

Reporters are responsible for all serialization. The `LintResult`
provides a canonical, format-agnostic representation. Reporters
transform it to their target format (JSON, XML, text, HTML).

### Validation

**Why a class instead of a function?** Reporters need metadata
(`name`, `supports_file_output`) and may need initialization state.
A class is the natural fit.

**Stable for five years?** Yes. The `render()` method receives a
`LintResult`, which is stable. New `LintSummary` fields are additive.

---

## 9. Plugin API

### Plugin Discovery

Plugins are discovered via Python entry points — the standard
mechanism used by pytest, flake8, and other tools.

**Entry point groups:**

| Group | Purpose |
|---|---|
| `behave_lint.rules` | Register rule classes. |
| `behave_lint.reporters` | Register reporter classes. |
| `behave_lint.config` | Register configuration extensions. |

**Example `pyproject.toml`:**

```toml
[project.entry-points."behave_lint.rules"]
acme-rules = "acme_lint_rules:register_rules"

[project.entry-points."behave_lint.reporters"]
acme-format = "acme_lint_reporters:AcmeReporter"
```

### Registration

For rules, the entry point can point to either a `Rule` subclass
directly or to a registration function that returns a list of `Rule`
subclasses. The registration function pattern supports plugins that
register multiple rules:

```python
def register_rules():
    return [AcmeRule001, AcmeRule002, AcmeRule003]
```

For reporters, the entry point points to a `Reporter` subclass
directly.

### Capabilities

A plugin can provide:

- **Rules:** New lint checks.
- **Reporters:** New output formats.
- **Configuration extensions:** New configuration keys (future).

A single plugin package can provide all three.

### Compatibility

Plugins must declare their compatible behave-lint version range:

```toml
[project]
dependencies = ["behave-lint>=1.0,<2.0"]
```

The plugin API is stable within a major version. Plugins written for
v1.x work with any v1.y (y >= x).

### Isolation

- Plugin load failures are isolated — a broken plugin does not crash
  the tool.
- Plugin rule failures are isolated — a rule exception does not affect
  other rules.
- Plugin configuration is namespaced under `[tool.behave-lint.plugins]`.

### Versioning

The plugin API follows the same semver as the core API. Breaking
changes to the `Rule` or `Reporter` interfaces require a major version
bump.

### Validation

**Why entry points?** They are the Python standard for plugin
discovery. Well-supported by pip, hatch, and all modern packaging
tools. No custom infrastructure needed.

**Stable for five years?** Yes. Entry points are a stable Python
feature. The `Rule` and `Reporter` interfaces are stable within a
major version.

---

## 10. CLI API

### Overview

The CLI is the primary interface for end users. It is thin — all
logic is in the library API. The CLI parses arguments, calls
`lint()` or equivalent functions, and exits with the appropriate code.

### Commands

#### `behave-lint [paths...]`

**Purpose:** Lint feature files (default command).

**Arguments:**

| Argument | Type | Description |
|---|---|---|
| `paths` | positional, optional | Files or directories to lint. Defaults to `config.paths` or `features/`. |

**Flags:**

| Flag | Description |
|---|---|
| `--select <rule-ids>` | Enable specific rules (comma-separated). |
| `--ignore <rule-ids>` | Disable specific rules (comma-separated). |
| `--output <format>` | Output format: `console`, `json`, `markdown`, `sarif`, `github`. |
| `--output-file <path>` | Write output to file instead of stdout. |
| `--config <path>` | Explicit path to `pyproject.toml`. |
| `--color` / `--no-color` | Force enable/disable colored output. |
| `--verbose` | Show progress and timing information. |
| `--quiet` | Suppress all output except diagnostics. |
| `--statistics` | Show diagnostic statistics by rule and severity. |
| `--no-cache` | Disable cache for this run. |
| `--clear-cache` | Clear cache before running. |
| `--fix` | Apply safe auto-fixes (future). |
| `--unsafe-fixes` | Apply unsafe auto-fixes (future). |
| `--version` | Print version and exit. |
| `--help` | Print help and exit. |

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | No diagnostics at or above failure severity. |
| 1 | Diagnostics at or above failure severity. |
| 2 | Internal error (config, unexpected exception). |

**Examples:**

```bash
# Lint default paths
behave-lint

# Lint specific directory
behave-lint features/login/

# Lint with JSON output
behave-lint --output json --output-file results.json features/

# Lint with specific rules
behave-lint --select BC001,BS001 features/

# Lint without cache
behave-lint --no-cache features/
```

#### `behave-lint rules`

**Purpose:** List all available rules.

**Flags:**

| Flag | Description |
|---|---|
| `--category <cat>` | Filter by category. |
| `--severity <sev>` | Filter by default severity. |
| `--all` | Include deprecated and experimental rules. |
| `--format <fmt>` | Output format: `table` (default), `json`. |

**Exit codes:** 0 (always, unless internal error).

**Example:**

```bash
behave-lint rules
behave-lint rules --category correctness
behave-lint rules --format json
```

#### `behave-lint explain <rule-id>`

**Purpose:** Show detailed documentation for a rule.

**Arguments:**

| Argument | Type | Description |
|---|---|---|
| `rule-id` | positional, required | Rule ID to explain. |

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | Rule found and displayed. |
| 2 | Unknown rule ID. |

**Example:**

```bash
behave-lint explain BC001
```

#### `behave-lint doctor` (Future)

**Purpose:** Diagnose behave-lint installation and configuration.

**Checks:**

- behave-lint version and Python version.
- behave-model version and compatibility.
- Configuration file found and valid.
- Plugin discovery and loading.
- Cache directory writable.
- Terminal color support.

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | All checks passed. |
| 2 | One or more checks failed. |

**Example:**

```bash
behave-lint doctor
```

### Validation

**Why no subcommands for v1?** The tool has one primary action (lint).
Subcommands add complexity without benefit. `rules` and `explain` are
implemented as flags (`--list-rules`, `--explain`) in v1 and may
become subcommands in v2 if the CLI grows.

**Consistency with SPECIFICATION.md:** The SPECIFICATION.md describes
`--list-rules` and `--explain` as flags. The CLI API here presents
them as both flags and conceptual commands. This is intentional — the
flag form is the v1 implementation; the command form is the conceptual
model. No inconsistency.

---

## 11. Error API

### Error Hierarchy

```
BehaveLintError (base)
├── ConfigError
│   ├── InvalidConfigValueError
│   ├── UnknownConfigKeyError
│   └── UnknownRuleError
├── NoFilesFoundError
├── InternalError
└── PluginError
    ├── PluginLoadError
    └── PluginRegistrationError
```

### Base Error

**`BehaveLintError`**: Base class for all public errors. All
behave-lint errors inherit from this class, allowing users to catch
all tool errors with a single `except` clause.

### ConfigError

**Purpose:** Configuration is invalid and cannot be used.

**Subclasses:**

- `InvalidConfigValueError`: A config value is invalid (e.g.,
  severity `"critical"`). Includes the key, invalid value, and
  expected values.
- `UnknownConfigKeyError`: An unknown key in `pyproject.toml`.
  Forward-compatible — produces a warning, not a fatal error.
- `UnknownRuleError`: A rule ID in `select` or `ignore` is not
  registered. Includes a fuzzy-match suggestion.

**Recovery:** Fix the configuration and re-run. The tool does not
proceed with invalid configuration.

**Example message:**

```
ConfigError: Invalid value 'critical' for key 'severity'.
Expected one of: error, warning, info, off.
In: pyproject.toml [tool.behave-lint]
```

### NoFilesFoundError

**Purpose:** No `.feature` files found in the specified paths.

**Recovery:** Check the paths argument or `config.paths`.

### InternalError

**Purpose:** An unexpected internal failure. Indicates a bug.

**Guidance:** The error message includes:

- What operation was being performed.
- Tool version and platform.
- A link to GitHub Issues for filing a bug report.

### PluginError

**Purpose:** A plugin failed to load or register.

**Subclasses:**

- `PluginLoadError`: Plugin module could not be imported.
- `PluginRegistrationError`: Plugin's registration function failed.

**Recovery:** The tool continues without the plugin. A warning is
emitted. The user should fix or remove the plugin.

### Validation

**Why a typed hierarchy?** Users need to catch specific errors
(config errors vs. internal errors) without parsing error messages.
The hierarchy allows `except ConfigError` to catch all configuration
issues while letting `InternalError` propagate.

**Stable for five years?** Yes. New error subclasses may be added
under existing parent classes. Existing error classes will not be
removed or renamed within a major version.

---

## 12. Diagnostic API

### Diagnostic Object

The `Diagnostic` object is defined in Section 4 (Core Objects). This
section covers the diagnostic API in detail.

### Fields

All fields are defined in the `Diagnostic` dataclass (Section 4).
Key design decisions:

- **Immutable:** Diagnostics are frozen dataclasses. Once created,
  they cannot be modified. This ensures that filtering, sorting, and
  serialization do not alter diagnostic content.

- **`file_path` is always a string:** Relative or absolute, as
  provided by the user. The tool does not normalize paths (to preserve
  the user's path format in output).

- **`line` is 1-based:** Matches Gherkin convention and editor
  conventions. `column` is also 1-based.

- **`end_line` / `end_column`:** Optional. Used for multi-line issues
  (e.g., a table with formatting problems). When omitted, the issue
  is assumed to be on a single line.

### Filtering

Diagnostics are filtered by the engine after aggregation:

- **Severity threshold:** Diagnostics below the failure severity are
  retained in output but do not affect the exit code.
- **Inline disable comments:** `# behave-lint: off` comments in
  feature files suppress diagnostics for the next block.
- **File-level exclusions:** Files matching exclusion patterns are
  not analyzed.

### Sorting

Diagnostics are sorted deterministically:

1. `file_path` (lexicographic)
2. `line` (ascending)
3. `column` (ascending, if present)
4. `rule_id` (lexicographic)

This order is stable and documented. It does not depend on rule
execution order or parallelism.

### Serialization

The `Diagnostic` object serializes to:

- **JSON:** All fields as a JSON object. The JSON schema is versioned
  independently (`schemaVersion` field in the output envelope).
- **SARIF:** Mapped to SARIF `result` objects with `ruleId`,
  `level`, `message`, and `locations`.
- **Console:** Formatted as `file:line:column: severity rule_id
  message`.
- **Markdown:** Table rows with file, line, severity, rule, message.

### Diagnostic Creation Helper

Rules create diagnostics using `self.diagnostic()`:

```python
self.diagnostic(
    message="Duplicate scenario name",
    node=scenario,          # extracts file_path, line, column
    suggestion="Rename to be unique.",
)
```

The helper pre-fills `rule_id`, `severity` (from config or default),
and `category` from the rule's metadata. It extracts `file_path`,
`line`, and `column` from the `node` (a `behave-model` element).

---

## 13. Auto-Fix API

> **Status:** Reserved for v1.1+. The API is designed now to ensure
> rules can be written with auto-fix in mind. No auto-fix
> functionality is implemented in v1.0.

### Capabilities

Auto-fix is declared per-rule via `AutoFixCapability`:

- `NONE`: The rule cannot auto-fix.
- `SAFE`: The fix does not change semantics (e.g., normalizing keyword
  casing). Applied with `--fix`.
- `UNSAFE`: The fix may change semantics (e.g., removing unused tags).
  Applied only with `--unsafe-fixes`.

### Safety

- **Safe fixes** can be applied automatically in CI and pre-commit.
- **Unsafe fixes** require explicit opt-in (`--unsafe-fixes`).
- **No fix** is applied without the user's explicit request.

### Conflict Resolution

When two rules produce conflicting fixes for the same location:

1. Fixes are applied in rule execution order (by category, then rule
   ID).
2. The first fix wins. Subsequent fixes for the same location are
   skipped and a warning is emitted.
3. The user is informed of skipped fixes.

### Preview Mode

`--fix --dry-run` (future) shows what would be changed without
modifying files. Output includes a diff for each file.

### API Surface (Future)

```python
def lint(
    ...,
    fix: bool = False,           # Apply safe fixes
    unsafe_fixes: bool = False,  # Also apply unsafe fixes
    dry_run: bool = False,       # Show fixes without applying
) -> LintResult: ...
```

`LintResult` will include a `fixes_applied` field (future) listing
the fixes that were applied.

### Validation

**Why design the API now if it's not implemented?** Rules need to
declare their auto-fix capability from day one so that the metadata
is available for documentation and future use. Adding `AutoFixCapability`
later would require updating all existing rules.

**Stable for five years?** The `AutoFixCapability` enum and the
`--fix` / `--unsafe-fixes` flags are designed to be stable. The
internal fix application mechanism is private and may change.

---

## 14. Extension Points

### Current Extension Points

| Extension point | Interface | Stability |
|---|---|---|
| Custom rules | `Rule` subclass | Stable (v1) |
| Custom reporters | `Reporter` subclass | Stable (v1) |
| Configuration plugins | Entry point `behave_lint.config` | Stable (v1) |
| Rule parameters | `default_params` + `config.rule_params` | Stable (v1) |

### Future Extension Points

| Extension point | Interface | Target version |
|---|---|---|
| Fix providers | `FixProvider` interface | v1.1+ |
| Metric collectors | `MetricCollector` interface | v2.0+ |
| LSP server | `behave_lint.lsp` module | v2.0+ |
| Watch mode | `Linter.watch()` method | v1.2+ |
| Custom visitors | `Visitor` subclass | v1.1+ |

### Deprecation Policy

- Deprecated APIs emit a `DeprecationWarning` with guidance on
  migration.
- Deprecated APIs remain functional for at least one minor version.
- Removed APIs are removed in a major version bump.
- Deprecated rule IDs are permanently retired (never reused).

### Migration Strategy

- Each breaking change includes a migration guide in the changelog.
- Automated migration tools are provided when feasible (e.g., a
  `behave-lint migrate` command for config format changes).
- Breaking changes are communicated in release notes with at least 3
  months of deprecation warnings in the prior version.

### Validation

**Why are extension points public?** Extension is a first-class use
case. Plugin authors need stable interfaces to build on. Hiding
extension points would force plugins to use private APIs, which would
break on every release.

**Stable for five years?** The `Rule` and `Reporter` interfaces are
minimal and additive. New optional methods can be added with default
implementations. Existing methods will not change signature.

---

## 15. Versioning

### Semantic Versioning

behave-lint follows Semantic Versioning 2.0.0:

| Version bump | When |
|---|---|
| **Major (X.0.0)** | Breaking API changes. |
| **Minor (0.X.0)** | New features, new rules, new reporters. Backward-compatible. |
| **Patch (0.0.X)** | Bug fixes, performance improvements. Backward-compatible. |

### API Stability Guarantees

Within a major version:

- **Public objects:** `Severity`, `Category`, `Diagnostic`, `Config`,
  `LintResult`, `LintSummary`, `RuleMetadata` — fields are stable.
  New fields may be added with defaults.
- **Public functions:** `lint()`, `load_config()`, `list_rules()`,
  `explain_rule()` — signatures are stable. New optional parameters
  may be added.
- **Rule SDK:** `Rule` base class, `check()` method,
  `RuleMetadata` — stable. New optional methods may be added with
  default implementations.
- **Reporter SDK:** `Reporter` interface, `render()` method — stable.
- **Error API:** Error class hierarchy — stable. New subclasses may
  be added.
- **CLI:** Flags are stable. New flags may be added. Removed flags
  require a major version.
- **Configuration:** Keys are stable. New keys may be added. Removed
  keys require a major version.

### Pre-1.0 Policy

Before 1.0, breaking changes may occur in minor versions (0.x → 0.y).
This follows common Python practice. Once 1.0 is reached, strict
semver applies.

### Deprecation Policy

- **Deprecation:** An API is marked deprecated in a minor version. It
  emits `DeprecationWarning` with migration guidance.
- **Removal:** A deprecated API is removed in the next major version.
- **Rule deprecation:** A deprecated rule remains functional but is
  not in the default set. Its rule ID is permanently retired when
  removed.

### Breaking Changes

The following are **not** considered breaking changes:

- Adding a new rule (may produce new diagnostics).
- Adding a new field to a dataclass (with a default).
- Adding a new optional parameter to a function.
- Adding a new enum member.
- Adding a new error subclass.
- Adding a new CLI flag.
- Adding a new configuration key.
- Changing the internal implementation of any public function.
- Changing diagnostic messages (they are human-readable text, not
  machine-parseable contracts).

The following **are** breaking changes:

- Removing a public object, function, field, flag, or config key.
- Changing a function signature (parameter name, type, order).
- Changing a dataclass field name or type.
- Changing an error class name or parent.
- Changing the exit code semantics.
- Changing the diagnostic sort order.

### Migration Strategy

For each major version:

- A migration guide is published in the changelog.
- Deprecated APIs from the prior major version are removed.
- New APIs are documented with examples.
- Automated migration tools are provided when feasible.

---

## 16. Examples

### Python API — Basic

```python
import behave_lint

result = behave_lint.lint("features/")
for diag in result.diagnostics:
    print(f"{diag.file_path}:{diag.line}: {diag.message}")
print(f"Exit code: {result.exit_code}")
```

### Python API — Custom Config

```python
from behave_lint import lint, Config, Severity

config = Config(
    select=["BC001", "BS001", "BX001"],
    severity_overrides={"BX001": Severity.WARNING},
    output="json",
    output_file="lint-results.json",
)

result = lint("features/", config=config)
```

### CLI — Basic

```bash
behave-lint features/
```

### CLI — CI Mode

```bash
behave-lint --output github --output-file lint.json features/
```

### CLI — Statistics

```bash
behave-lint --statistics features/
```

Output:

```
Diagnostics by severity:
  error:   3
  warning: 12
  info:    5

Diagnostics by rule:
  BC001  duplicate-scenario-name       2
  BS001  missing-feature-description    5
  BX001  too-many-steps                 8

Files analyzed: 45
Files with issues: 18
Duration: 0.32s
```

### pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/your-org/behave-lint
    rev: v0.1.0
    hooks:
      - id: behave-lint
        args: ["--output", "console"]
```

### GitHub Actions

```yaml
# .github/workflows/lint.yml
name: Lint Feature Files
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install behave-lint
      - run: behave-lint --output github features/
```

### Large Repositories

```bash
# Use cache for fast incremental runs
behave-lint --output json --output-file results.json features/

# Disable cache for clean CI run
behave-lint --no-cache --output sarif --output-file results.sarif features/
```

### Custom Rule

```python
from behave_lint.rules import Rule, RuleMetadata, Severity, Category, AutoFixCapability, RuleScope

class NoEmptyFeatureRule(Rule):
    """Detects features with no scenarios."""

    metadata = RuleMetadata(
        rule_id="BC002",
        name="no-empty-feature",
        description="Features should contain at least one scenario.",
        category=Category.CORRECTNESS,
        default_severity=Severity.WARNING,
        since="0.1.0",
        auto_fix=AutoFixCapability.NONE,
    )

    scope = RuleScope.SINGLE_FILE

    def check(self, feature, config) -> list:
        if not feature.scenarios:
            return [self.diagnostic(
                message=f"Feature '{feature.name}' has no scenarios.",
                node=feature,
            )]
        return []
```

### Custom Reporter

```python
from behave_lint.reporters import Reporter
from behave_lint import LintResult
from pathlib import Path

class CsvReporter(Reporter):
    """Export diagnostics as CSV."""

    name = "csv"
    supports_file_output = True
    supports_stdout = True

    def render(self, result: LintResult, output_file: str | None) -> None:
        lines = ["severity,rule_id,file,line,message"]
        for d in result.diagnostics:
            lines.append(f"{d.severity.value},{d.rule_id},{d.file_path},{d.line},{d.message}")
        content = "\n".join(lines) + "\n"

        if output_file:
            Path(output_file).write_text(content)
        else:
            print(content)
```

### Plugin Package

```toml
# pyproject.toml
[project]
name = "acme-lint-rules"
version = "1.0.0"
dependencies = ["behave-lint>=1.0,<2.0"]

[project.entry-points."behave_lint.rules"]
acme-rules = "acme_lint_rules:register_rules"
```

```python
# acme_lint_rules/__init__.py
from behave_lint.rules import Rule

class AcmeRule001(Rule):
    metadata = RuleMetadata(
        rule_id="ACME001",
        name="acme-tag-required",
        description="All features must have an @acme tag.",
        category=Category.CONSISTENCY,
        default_severity=Severity.WARNING,
        since="1.0.0",
        auto_fix=AutoFixCapability.NONE,
    )

    def check(self, feature, config) -> list:
        if "@acme" not in [t.name for t in feature.tags]:
            return [self.diagnostic(
                message="Feature is missing required @acme tag.",
                node=feature,
            )]
        return []

def register_rules():
    return [AcmeRule001]
```

---

## 17. Future API

### Reserved APIs

The following APIs are intentionally reserved for future versions.
They are documented here to signal intent and prevent accidental
naming collisions.

### `Linter` Class (v1.0)

A stateful linter that reuses cache and configuration across
multiple runs. Designed for watch mode, LSP, and repeated
invocations.

```python
class Linter:
    def __init__(self, config: Config | None = None): ...
    def lint(self, paths: str | list[str] | None = None) -> LintResult: ...
    def clear_cache(self) -> None: ...
```

**Why reserved?** The `Linter` class is more efficient than the
`lint()` function for repeated use but adds statefulness. The `lint()`
function covers the common case (single run). `Linter` is public from
v1.0 but may gain additional methods in the future.

### Watch Mode (v1.2+)

```python
linter = Linter(config)
for result in linter.watch("features/"):
    # Called on each file change
    print(result.diagnostics)
```

**Why postponed?** Watch mode requires file system monitoring, which
adds complexity and platform-specific dependencies. It is not needed
for v1.0 (CI and pre-commit are the primary use cases).

### LSP API (v2.0+)

```python
from behave_lint.lsp import LSPServer

server = LSPServer(config)
server.start()  # Runs LSP protocol over stdio
```

**Why postponed?** LSP is a significant feature that requires its own
specification. The library API is designed to support LSP (the LSP
server uses the same `Linter` class), but the LSP-specific API is not
stabilized until v2.0.

### Fix Provider API (v1.1+)

```python
class FixProvider:
    def provide_fixes(self, diagnostic: Diagnostic) -> list[Fix]: ...
```

**Why postponed?** Auto-fix is Phase 5 in the roadmap. The metadata
(`AutoFixCapability`) is defined now, but the fix application
mechanism is not stabilized until v1.1.

### Metric Collector API (v2.0+)

```python
class MetricCollector:
    def collect(self, project) -> dict[str, float]: ...
```

**Why postponed?** Metrics (e.g., step reuse rate, scenario
complexity score) are a future feature. The API is reserved to
prevent naming collisions.

### Rule Marketplace API (v2.0+)

```python
def install_rule(package: str) -> None: ...
def search_rules(query: str) -> list[RuleMetadata]: ...
```

**Why postponed?** A rule marketplace requires infrastructure (a
registry, search, ratings) that is beyond v1 scope. The plugin system
(entry points) is the v1 mechanism for distributing rules.

### Validation

**Why document future APIs?** Documenting reserved APIs prevents
naming collisions (e.g., a plugin defining `Linter` would conflict
with the future public class). It also signals the project's
direction to users and contributors.

**Stable for five years?** The current API (v1) is stable. Future
APIs are reserved — their signatures may change before they are
released. Once released, they follow the same stability guarantees
as the v1 API.

---

## Appendix A: Consistency Check

The following consistency checks were performed against
VISION.md, SPECIFICATION.md, and ARCHITECTURE.md:

1. **Rule ID convention:** API.md uses `B<category><number>` (e.g.,
   `BC001`) matching SPECIFICATION.md Appendix A. **Consistent.**

2. **Categories:** API.md defines 6 categories (correctness, style,
   complexity, consistency, pedantic, step_definitions) matching
   SPECIFICATION.md and ARCHITECTURE.md. **Consistent.**

3. **Severity levels:** API.md defines 4 levels (error, warning,
   info, off) matching SPECIFICATION.md. **Consistent.**

4. **Diagnostic fields:** API.md defines the same 11 fields as
   ARCHITECTURE.md Section 9. **Consistent.**

5. **Configuration keys:** API.md `Config` fields match
   SPECIFICATION.md Appendix B. **Consistent.**

6. **CLI flags:** API.md CLI section matches SPECIFICATION.md
   Section 10 (CLI Experience). **Consistent.**

7. **Plugin entry points:** API.md uses `behave_lint.rules`,
   `behave_lint.reporters`, `behave_lint.config` matching
   ARCHITECTURE.md Section 13. **Consistent.**

8. **Exit codes:** API.md defines 0, 1, 2 matching SPECIFICATION.md
   and ARCHITECTURE.md. **Consistent.**

9. **Auto-fix capability:** API.md defines `NONE`, `SAFE`, `UNSAFE`
   matching ARCHITECTURE.md Section 7. **Consistent.**

**No inconsistencies detected.**
