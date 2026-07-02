# behave-lint — Development Guidelines

> **Status:** Canonical engineering standards for all contributors and
> AI assistants.
> **Audience:** Every engineer and AI agent that writes, reviews, or
> modifies code in the behave-lint repository.
> **Scope:** Mandatory conventions for Python code, tests,
> documentation, dependencies, error handling, logging, code review,
> and AI-assisted development. This document does not define
> implementation, architecture, or lint rules.
> **Dependencies:** This document follows VISION.md, SPECIFICATION.md,
> ARCHITECTURE.md, API.md, RULE_ENGINE.md, DIAGNOSTIC_ENGINE.md,
> CONFIGURATION_SYSTEM.md, PLUGIN_SYSTEM.md, COMPONENT_DESIGN.md,
> REPOSITORY_DESIGN.md, RULE_TAXONOMY.md, and
> IMPLEMENTATION_ROADMAP.md. Inconsistencies, if any, are reported in
> **Appendix A**.

---

## Table of Contents

1. [Engineering Philosophy](#1-engineering-philosophy)
2. [Python Standards](#2-python-standards)
3. [Coding Style](#3-coding-style)
4. [Project Conventions](#4-project-conventions)
5. [Testing Standards](#5-testing-standards)
6. [Documentation Standards](#6-documentation-standards)
7. [Performance Guidelines](#7-performance-guidelines)
8. [Error Handling](#8-error-handling)
9. [Logging](#9-logging)
10. [Dependency Policy](#10-dependency-policy)
11. [Code Review Checklist](#11-code-review-checklist)
12. [AI-Assisted Development](#12-ai-assisted-development)
13. [Definition of Done](#13-definition-of-done)
14. [Future Evolution](#14-future-evolution)

---

## 1. Engineering Philosophy

### Guiding Principles

behave-lint is built to last ten or more years. Every line of code
must be written with the assumption that a stranger will read it
eighteen months from now, with no context, at midnight, under
pressure. The following principles guide every decision.

**Simplicity.** The simplest correct solution is always preferred.
Complexity is the enemy of long-term maintainability. When two
approaches solve the same problem, the simpler one wins — even if
the more complex one is more "elegant" or "clever." Complexity is
justified only when it solves a problem that simplicity cannot.

**Readability.** Code is read far more often than it is written.
Optimize for the reader, not the writer. Prefer explicit over
implicit, descriptive names over short ones, linear flow over clever
comprehensions. A reader should understand what a function does
without reading its implementation — the name and signature should
tell the story.

**Maintainability.** Every change should make the next change
easier, not harder. This means avoiding tight coupling, minimizing
public API surface, and preferring small, composable units over
large, monolithic ones. When in doubt, make it easy to change later
rather than hard-coding a solution that will need to be unwound.

**Explicitness.** No hidden state, no global mutable variables, no
implicit imports, no magic. If a function depends on something, that
dependency is visible in its signature. If a behavior is configured,
it is configured explicitly, not inferred from the environment.

**Pragmatism.** Principles guide; they do not dictate. When a
principle conflicts with delivering correct, timely value to users,
the principle yields — with a documented rationale. Dogma is not a
substitute for judgment.

### SOLID Principles

behave-lint applies SOLID at the component and module level:

- **Single Responsibility:** Each module and class has one reason to
  change. COMPONENT_DESIGN.md Section 2 defines 20 components, each
  with a distinct responsibility. Merging responsibilities is a
  design error.
- **Open/Closed:** New rules, reporters, and plugins are added
  without modifying the engine. Extension is through subclassing and
  entry points, not through editing core code.
- **Liskov Substitution:** A plugin rule must work anywhere a
  built-in rule works. The Rule base class contract is the
  specification; subclasses must honor it.
- **Interface Segregation:** The Rule SDK exposes only what rule
  authors need. The Reporter SDK exposes only what reporter authors
  need. No "god object" interface.
- **Dependency Inversion:** The application layer depends on domain
  abstractions, not infrastructure concrete classes.
  ARCHITECTURE.md Section 4 defines the dependency direction:
  inward and downward, never the reverse.

### Composition Over Inheritance

Classes are composed at runtime through dependency injection and
registry patterns, not through deep class hierarchies
(ARCHITECTURE.md Section 2). Inheritance is used only when a genuine
"is-a" relationship exists (e.g., `DuplicateScenarioNameRule` is a
`Rule`). Deep inheritance chains (more than two levels) are
prohibited.

**Why:** Composition enables independent testing, runtime
replacement, and parallel development. Inheritance creates tight
coupling and fragile base-class problems.

**Trade-off:** Composition adds indirection (interfaces vs. direct
calls). This is acceptable — the overhead is negligible and the
benefits are significant.

### Domain-Driven Thinking

The domain is Gherkin/BDD specification quality. Code must use
domain vocabulary: "feature," "scenario," "step," "tag," "background,"
"example." No generic terms ("item," "element," "node") when a
domain term is available. This ensures code, documentation, and user
output share a consistent vocabulary.

---

## 2. Python Standards

### Supported Versions

Python **3.11, 3.12, and 3.13** are supported (matching
`behave-model`). The minimum version is 3.11 because it provides
`tomllib` (standard library TOML parser), exception groups, and
`TaskGroup`.

**Why:** Matching `behave-model`'s minimum ensures ecosystem
compatibility. Python 3.11+ provides sufficient language features
without requiring the latest version.

**Trade-off:** Excluding Python 3.10 and earlier limits the user
base. This is acceptable — `behave-model` already requires 3.11+.

### Type Hints

Type hints are **mandatory** on all public functions, methods, and
class attributes. Internal (underscore-prefixed) functions should
also be typed. Mypy with `strict = true` enforces this in CI
(REPOSITORY_DESIGN.md Section 10).

- Use modern syntax: `list[str]` not `List[str]`, `dict[str, int]`
  not `Dict[str, int]`.
- Use `X | None` not `Optional[X]`.
- Use `|` for unions, not `Union[X, Y]`.
- Use `TypeAlias` for type aliases, not bare assignments.
- Use `dataclasses.dataclass` for structured data, not typed dicts.

**Why:** Type hints enable IDE autocomplete, static analysis, and
self-documenting signatures. They are the primary defense against
runtime type errors.

### pathlib

Use `pathlib.Path` for all file path operations. Never use
`os.path.join`, `os.path.exists`, or string concatenation for paths.

**Why:** `pathlib` is more readable, cross-platform, and type-safe
than `os.path`. It is the modern Python standard.

### Dataclasses

Use `@dataclass` for all structured data containers (Diagnostic,
Config, RuleMetadata). Use `@dataclass(frozen=True)` for immutable
data. Use `@dataclass(slots=True)` for performance-critical data
that is frequently allocated.

**Why:** Dataclasses provide `__init__`, `__repr__`, `__eq__`, and
type hints in a single declaration. They are the Pythonic
alternative to manual constructors and boilerplate.

### Enum

Use `enum.Enum` for all finite value sets: `Severity`, `Category`,
`FixKind` (`SAFE`, `UNSAFE`, `NONE`). Use `enum.StrEnum` when
string values are needed (e.g., for serialization). Enums are
immutable after definition — new members may be added in minor
versions.

**Why:** Enums prevent invalid values, enable exhaustive `match`
statements, and provide a named type for documentation.

### Typing and Protocol

Use `typing.Protocol` for structural typing when a formal base class
is unnecessary. Use `typing.runtime_checkable` on protocols that
need `isinstance` checks. Use `typing.TypeVar` and `typing.Generic`
for generic types.

**Why:** Protocols enable duck typing with static analysis support.
They are preferred over ABCs when the relationship is structural
rather than hierarchical.

### Exceptions

Exceptions are typed, specific, and actionable. See Section 8 for
the full error handling policy.

### Context Managers

Use context managers (`with` statements) for all resource
acquisition: file handles, locks, temporary directories. Implement
`__enter__` / `__exit__` (or `@contextmanager`) for any class that
manages resources.

**Why:** Context managers guarantee resource cleanup, even on
exceptions. They are the Pythonic way to manage lifecycle.

### Generics

Generics are used where type safety adds value: `list[Diagnostic]`,
`dict[str, Rule]`, `Registry[Rule]`. Avoid over-generic code — if a
type parameter is always the same type, it does not need to be
generic.

### Pattern Matching

`match` / `case` (Python 3.10+) is preferred over long `if` /
`elif` chains for discriminated unions. Particularly useful for
handling node types in the visitor engine and severity/category
dispatch.

**Why:** Pattern matching is more readable and exhaustive than
if-elif chains. The compiler warns about non-exhaustive matches in
some type checkers.

### Async Policy

behave-lint is **synchronous** in v1. There is no async/await in the
codebase. The tool is CPU-bound (static analysis), not I/O-bound.
Parallelism is achieved through thread pools (ARCHITECTURE.md
Section 15), not async.

**Why:** Async adds complexity (event loops, async-aware testing,
async context managers) without benefit for a CPU-bound workload.
Thread pools are simpler and sufficient.

**Trade-off:** If behave-lint adds network features (remote cache,
cloud rules) in the future, async may be reconsidered. That decision
would require a major version change.

---

## 3. Coding Style

### Naming

All naming conventions follow PEP 8 and are detailed in
REPOSITORY_DESIGN.md Section 5. Summary:

| Element | Convention | Example |
|---|---|---|
| Modules | snake_case | `diagnostic_collector.py` |
| Classes | PascalCase | `LintEngine`, `DuplicateScenarioNameRule` |
| Functions | snake_case, verb-first | `load_config()`, `is_enabled()` |
| Constants | UPPER_SNAKE_CASE | `DEFAULT_SEVERITY`, `EXIT_CODE_SUCCESS` |
| Type aliases | PascalCase | `DiagnosticList`, `RuleMap` |
| Rule classes | `<Name>Rule` | `MissingBackgroundRule` |
| Boolean predicates | `is_`/`has_`/`can_` prefix | `is_enabled()`, `has_fix()` |

No abbreviations except well-established ones (`URL`, `ID`, `API`).
`configuration.py` not `config.py` (except the public API alias
`behave_lint.config`).

### Imports

- **Standard library first**, then third-party, then local —
  separated by blank lines (isort convention, enforced by Ruff).
- **Absolute imports** preferred. Relative imports (`from . import`)
  allowed within a package for internal modules.
- **No wildcard imports** (`from x import *`).
- **No circular imports.** Architecture tests enforce this.
- **Import only what you need.** `from collections.abc import
  Sequence` not `import collections`.

### Constants

Constants are defined at the module level, never inside classes or
functions. They are `UPPER_SNAKE_CASE`. Constants that are
configuration defaults belong in the configuration module, not
scattered across the codebase.

### Modules and Packages

- One responsibility per module (REPOSITORY_DESIGN.md Section 4).
- One class per file for major components (e.g., `lint_engine.py`
  contains `LintEngine`).
- `__init__.py` files export the public API of the package. They do
  not contain logic.
- No `__all__` in internal modules. Use `__all__` only in public API
  packages to explicitly declare the public surface.

### Public vs. Internal APIs

- **Public:** Anything importable from `behave_lint` or its
  documented subpackages (`behave_lint.rules`, `behave_lint.reporters`,
  `behave_lint.errors`, `behave_lint.config`). Documented in API.md.
- **Internal:** Anything underscore-prefixed (`_helper.py`,
  `_internal_func()`) or in undocumented subpackages. May change
  without notice.
- **Enforcement:** The public namespace is explicitly declared in
  `__init__.py` files. Underscore-prefixed modules are never
  re-exported.

**Why:** A small, explicit public API is stable. A large, implicit
public API is a maintenance trap — users depend on internals, and
every change is a breaking change.

### Docstrings

- **Format:** Google style (Args, Returns, Raises, Example
  sections).
- **Public API:** Every public class, function, and method has a
  docstring. No exceptions.
- **Internal:** Docstrings recommended but not required. Use them
  when the purpose is not obvious from the name.
- **Length:** One-line summary for simple functions. Multi-line for
  anything with parameters, return values, or non-obvious behavior.
- **No redundant docstrings.** `get_name(self) -> str: """Returns
  the name."""` is redundant. Use `"""Human-readable name."""` or
  omit if the signature is self-explanatory.

### Comments

- **Comments explain why, not what.** The code already says what.
  Comments provide rationale, context, or warnings.
- **No stale comments.** If you change code, update or remove the
  comment.
- **No commented-out code.** Version control remembers it. Delete
  it.
- **TODO comments** must include an issue number:
  `# TODO(#42): handle empty feature files`.

### Logging

Logging uses Python's standard `logging` module. See Section 9 for
the full logging policy.

### Error Messages

Error messages are **actionable**: they state what went wrong, where
it went wrong, and how to fix it. They never blame the user. They
never contain stack traces (those go in debug mode). They are
written in plain English, not jargon.

---

## 4. Project Conventions

### Dependency Direction

Dependencies flow **inward and downward** through the five
architectural layers (ARCHITECTURE.md Section 4):

1. Presentation → Application
2. Application → Domain
3. Application → Infrastructure
4. Infrastructure → Domain
5. Domain → Utilities

**No reverse dependencies.** The Domain layer never imports from
Application or Infrastructure. **No skip-level dependencies.**
Presentation never imports from Domain or Infrastructure directly
(it goes through Application). **No circular dependencies.**
Architecture tests enforce all three rules.

### Layering Rules

| Layer | May Import From | May Not Import From |
|---|---|---|
| Presentation | Application, Utilities | Domain, Infrastructure |
| Application | Domain, Infrastructure, Utilities | Presentation |
| Domain | Utilities, behave-model (types only) | Application, Infrastructure, Presentation |
| Infrastructure | Domain, Utilities, behave-model | Application, Presentation |
| Utilities | Standard library only | All other layers |

### Allowed Imports

- **Standard library:** Always allowed.
- **behave-model:** Only in the Infrastructure layer (specifically
  the Project Loader component, C11). Domain layer may import
  behave-model types for type hints, but never for runtime behavior.
- **Internal modules:** Per layering rules above.

### Forbidden Imports

- **No third-party runtime imports** except `behave-model`.
  ARCHITECTURE.md Section 17: "The tool depends on `behave-model`
  (required for parsing) and the Python standard library."
- **No `import *`** anywhere.
- **No dynamic imports** (`importlib.import_module`) except in the
  Plugin Manager (C09) for plugin discovery.
- **No `os.system` or `subprocess`** — behave-lint never spawns
  processes (ARCHITECTURE.md Section 19).
- **No `eval` or `exec`** — behave-lint never evaluates arbitrary
  code.
- **No `requests`, `urllib`, or network calls** — behave-lint makes
  no network requests.

### Module Responsibilities

Each module maps to a component defined in COMPONENT_DESIGN.md
Section 2. A module's responsibilities are exactly those of its
component. If a module's code does not fit a component's
responsibilities, it belongs in a different module.

### Public API Boundaries

The public API is defined in API.md Section 3. The boundary is
enforced by:

- `__init__.py` files that explicitly export public names.
- Mypy strict mode on `src/`.
- Architecture tests that verify no internal modules are exported.
- Code review: any change to `__init__.py` requires maintainer
  approval.

**Why:** The public API is a stability contract (API.md Section 2:
Semantic Versioning). Leaking internals through `__init__.py` turns
them into de facto public API, making every refactor a breaking
change.

---

## 5. Testing Standards

### Test Pyramid

behave-lint follows the testing pyramid from ARCHITECTURE.md Section
18:

| Level | What | How Many | Speed |
|---|---|---|---|
| Unit | Individual components | Most tests | Fast (<1s each) |
| Integration | Multi-component pipeline | Moderate | Medium (<5s each) |
| Golden | Output stability | One per format × fixture | Fast |
| Snapshot | Diagnostic stability | One per fixture | Fast |
| Performance | Time/memory benchmarks | One per project size | Slow (nightly) |
| Regression | Bug reproduction | One per bug fix | Fast |
| Architecture | Import rules | Few, static | Fast |

### Unit Tests

- **Scope:** One component in isolation. Mocks for all dependencies.
- **Naming:** `test_<function>_<scenario>()` — e.g.,
  `test_filter_diagnostics_by_severity_error_only()`.
- **Structure:** Arrange-Act-Assert (AAA). Separate sections with
  blank lines.
- **One assertion concept per test.** A test may have multiple
  `assert` statements, but they should all verify one behavior.
- **No shared mutable state.** Each test is independent. Use
  fixtures for setup, not module-level variables.
- **Coverage target:** 90%+ for core components (engine, rule
  engine, configuration, diagnostics). 80%+ for non-core.

### Integration Tests

- **Scope:** Multiple components working together. Real `.feature`
  files, real `behave-model` parsing.
- **Naming:** `test_<feature>_<scenario>()` — e.g.,
  `test_pipeline_loads_and_lints_multiple_files()`.
- **Location:** `tests/integration/`.
- **Fixtures:** Use shared fixtures from `tests/fixtures/`.

### Golden Tests

- **Scope:** Output format stability (console, JSON, Markdown, SARIF).
- **Process:** Run the tool on a fixture → compare output to
  expected file → fail if different. Update expected files
  explicitly when output intentionally changes.
- **Location:** `tests/golden/` with `fixtures/` and `expected/`
  subdirectories.
- **Why:** Prevents accidental output changes that would break
  downstream consumers (CI scripts, dashboards).

### Snapshot Tests

- **Scope:** Diagnostic content stability (which diagnostics are
  produced, not how they are formatted).
- **Process:** Run rules on a fixture → compare diagnostic set to
  snapshot → fail if different. Update snapshots explicitly when
  rule behavior intentionally changes.
- **Location:** `tests/snapshot/` with `fixtures/` and `snapshots/`
  subdirectories.

### Regression Tests

- **Scope:** Each bug fix includes a test that reproduces the bug.
- **Naming:** `test_issue_<number>.py` — e.g.,
  `test_issue_042.py`.
- **Policy:** Regression tests are **never deleted**, even if the
  rule is removed (they become no-ops or move to a legacy suite).
- **Location:** `tests/regression/`.

### Performance Tests

- **Scope:** Execution time and memory for benchmark projects (10,
  100, 1000, 5000 files).
- **Targets:** Per SPECIFICATION.md Section 13: <1s for 100 files,
  <5s for 1000 files, <30s for 5000 files.
- **Location:** `tests/performance/`.
- **Frequency:** Nightly CI run + on-demand.

### Test Organization

Tests mirror the source structure within each test type
(REPOSITORY_DESIGN.md Section 7). A contributor working on
`src/behave_lint/rules/correctness/duplicate_scenario.py` knows the
unit test is at
`tests/unit/rules/correctness/test_duplicate_scenario.py`.

### Test Markers

Use pytest markers to categorize tests (REPOSITORY_DESIGN.md Section
10): `@pytest.mark.unit`, `@pytest.mark.integration`,
`@pytest.mark.golden`, `@pytest.mark.snapshot`,
`@pytest.mark.performance`, `@pytest.mark.regression`,
`@pytest.mark.architecture`.

---

## 6. Documentation Standards

### README

The repository root `README.md` is the project's front door
(REPOSITORY_DESIGN.md Section 8). It contains: project name,
one-line description, badges, quick start, feature overview, links
to documentation, contributing link, and license. It is kept
concise — details belong in `docs/`.

### Module Documentation

Every module starts with a module-level docstring that states the
module's purpose and the component it implements (referencing
COMPONENT_DESIGN.md). Example structure:

```text
"""Diagnostic Collector — aggregates, filters, and sorts diagnostics.

Implements component C07 from COMPONENT_DESIGN.md Section 2.
"""
```

### API Documentation

Public API documentation is generated from docstrings. Every public
class, function, and method has a Google-style docstring with Args,
Returns, Raises, and Example sections as applicable. The public API
is documented in API.md; the docstrings are the inline reference.

### Rule Documentation

Rule documentation is **metadata-driven** (RULE_TAXONOMY.md Section
10). The `RuleMetadata` dataclass contains all fields needed to
generate documentation: `title`, `description`, `motivation`,
`examples`, `references`, `tags`. The `behave-lint explain <rule-id>`
command and the documentation site both render from metadata. Rule
authors must fill all metadata fields.

### Architecture Updates

If a change affects the architecture (new component, changed
dependency, new layer), the relevant design document must be updated
in the same PR. Design documents are immutable after publication
(REPOSITORY_DESIGN.md Section 8), so architectural changes require a
new document version or an addendum.

### Changelog Entries

`CHANGELOG.md` follows the [Keep a Changelog](https://keepachangelog.com/)
format with sections: Added, Changed, Deprecated, Removed, Fixed,
Security. Every PR that changes user-visible behavior adds an entry.
Entries are written from the user's perspective, not the developer's.

---

## 7. Performance Guidelines

### Memory Usage

- **Streaming output:** For large diagnostic sets, reporters stream
  output instead of buffering everything in memory
  (ARCHITECTURE.md Section 15).
- **Object reuse:** The project model is shared across all rules
  (read-only). No deep copies are made.
- **Lazy parsing:** Files are parsed only on cache miss.
- **No unnecessary collections:** Prefer generators over lists when
  the consumer only iterates once. Use `collections.abc.Iterable`
  in signatures rather than `list` when the consumer does not need
  indexing.

### Algorithmic Complexity

- **File discovery:** O(n) in number of files — directory listing.
- **Content hashing:** O(n) in file size — parallelized.
- **Rule execution:** O(r × f) where r = rules, f = files —
  parallelized for single-file rules.
- **Diagnostic sorting:** O(d log d) where d = diagnostics — stable
  sort with tiebreakers.
- **Cache lookup:** O(1) — hash-based.

Avoid O(n²) algorithms. If an operation is O(n²), document why and
whether it is acceptable for the expected input size.

### Lazy Evaluation

- Rules are loaded only when enabled (ARCHITECTURE.md Section 15).
- Plugins are imported only when their rules are enabled.
- Visitors skip node types with no interested rules.
- Reporters are instantiated only when selected.

**Why:** Lazy evaluation ensures the tool starts fast and only does
work that contributes to the result.

### Caching

The cache is the primary performance optimization
(ARCHITECTURE.md Section 15). Cache key: file content hash +
configuration hash + behave-model version + behave-lint version.
Cache value: diagnostics for that file under that configuration.

When adding new features, consider cache impact: if a new
configuration key affects diagnostics, it must be part of the cache
key. Otherwise, stale results will be served.

### Avoiding Unnecessary Allocations

- Prefer tuples over lists for fixed-size collections.
- Prefer `frozenset` over `set` for immutable membership tests.
- Use `__slots__` (via `@dataclass(slots=True)`) for
  frequently-allocated dataclasses.
- Avoid string concatenation in loops; use `str.join`.
- Avoid creating intermediate lists in comprehensions; use
  generator expressions where possible.

---

## 8. Error Handling

### Error Categories

behave-lint distinguishes four error categories
(ARCHITECTURE.md Section 14):

| Category | Cause | Example | Handling |
|---|---|---|---|
| **User error** | User provides invalid input | Non-existent path, malformed feature file | Clear message, exit code 1 |
| **Configuration error** | Invalid configuration | Unknown rule ID, invalid severity value | Actionable message with file path and expected format, exit code 2 |
| **Internal error** | Bug in the tool | Unexpected exception, assertion failure | Error message with context, stack trace in verbose mode, link to file issue, exit code 3 |
| **Programming error** | Misuse of internal API | Calling private method, violating contract | AssertionError or TypeError, fail fast |

### Design Rules

- **Fail isolated, not fail fast** (ARCHITECTURE.md Section 14). A
  linter's value is comprehensive feedback. If one file fails to
  parse, lint the other 99 files. If one rule crashes, continue with
  the remaining rules.
- **Never swallow exceptions.** Every `except` block must log the
  error. Silent recovery is worse than no recovery.
- **Never catch `Exception` or `BaseException`.** Catch specific
  exception types. The only exception is the top-level error
  handler in the CLI Coordinator, which catches all exceptions to
  produce a user-friendly message.
- **Custom exceptions** inherit from a common `BehaveLintError` base
  class. They are defined in `behave_lint.errors` (API.md Section
  11). Each exception has a clear name and an actionable message.
- **Error messages** include: what went wrong, where (file path,
  line number if applicable), and how to fix it. They are written
  in plain English. They never contain internal jargon or stack
  traces (those go in `--verbose` mode).

### Propagation

- **User errors** are reported as diagnostics or CLI messages, not
  raised as exceptions.
- **Configuration errors** raise `ConfigurationError`, caught by
  the CLI Coordinator, reported with exit code 2.
- **Internal errors** propagate to the top-level handler. The
  handler reports the error with context and exits with code 3.
- **Programming errors** (assertion failures, type errors) are not
  caught — they crash with a full traceback, signaling a bug.

---

## 9. Logging

### Philosophy

Logging provides **observable, debuggable execution** without
affecting diagnostic output or performance (ARCHITECTURE.md Section
16). Logs go to **stderr** — stdout is reserved for diagnostic
output. Mixing logs with diagnostics would make machine-readable
output unreliable.

### Levels

| Level | Purpose | Default Visibility |
|---|---|---|
| `error` | Fatal errors, internal failures | Always |
| `warning` | Non-fatal issues (unknown rules, plugin failures) | Always |
| `info` | Progress information (files loaded, rules executed) | `--verbose` |
| `debug` | Detailed execution info (cache hits/misses, rule timing) | `--verbose` |
| `trace` | Maximum detail (visitor traversal, node dispatching) | `BEHAVE_LINT_TRACE=1` only |

### Usage Rules

- Use `logger.warning()` for non-fatal issues the user should know
  about (plugin failed to load, unknown rule ID in config).
- Use `logger.info()` for progress information useful in verbose
  mode (loaded N files, executed R rules).
- Use `logger.debug()` for detailed diagnostic information (cache
  hit/miss, per-rule timing).
- Use `logger.error()` for errors that prevent the tool from
  completing its task.
- **Never use `print()`** for logging. Always use the `logging`
  module.
- **Never log at INFO level by default.** Default verbosity shows
  only warnings and errors. INFO and DEBUG require `--verbose`.

### Structured Logging

v1 uses the standard `logging` module with text output. Structured
(JSON) logging is a future enhancement. Log messages should be
self-contained and parseable (include relevant identifiers like
rule IDs, file paths, and counts).

### Debug Mode

`--verbose` enables info and debug logging. It displays: effective
configuration, rule execution times, cache hits/misses, plugin
discovery, and file parsing times. Debug mode does not change
behavior — it only increases log verbosity.

---

## 10. Dependency Policy

### Core Principle

**Minimal dependencies.** behave-lint depends on `behave-model`
(required for parsing) and the Python standard library. No
additional runtime dependencies are added without strong
justification (ARCHITECTURE.md Section 17).

### When to Use the Standard Library

Always prefer the standard library. It is stable, documented,
universally available, and has no supply-chain risk. If the
standard library can do the job — even with slightly more code —
use it.

### Evaluating Third-Party Libraries

Before adding a third-party dependency, answer all of the following:

1. **Is the standard library insufficient?** Document what it
   cannot do.
2. **Is the library actively maintained?** Check last commit date,
   open issue count, and release frequency.
3. **Is the library widely adopted?** Check PyPI download stats and
   GitHub stars. Obscure libraries are maintenance risks.
4. **Is the license compatible?** MIT, BSD, Apache 2.0 are
   compatible. GPL is not.
5. **Is the dependency tree small?** A library that pulls in 20
   transitive dependencies is a liability.
6. **Is the security posture acceptable?** Check for known CVEs.
7. **Can we vendor or inline the functionality?** For small
   utilities, inlining 50 lines of code is better than adding a
   dependency.

If all questions are answered satisfactorily, the dependency may be
added with maintainer approval. The decision is documented in the
PR description.

### Version Pinning

- **Runtime dependency (`behave-model`):** Pinned to a compatible
  version range (`>=x.y,<x.z`). The range is updated when
  `behave-model` releases new versions.
- **Dev dependencies:** Not pinned to specific versions (latest
  compatible). This ensures we catch issues with new versions
  early.
- **Python:** Minimum version 3.11, tested against 3.11, 3.12,
  3.13.

### Supply-Chain Security

- Dependencies are installed from PyPI only.
- No `--index-url` overrides in CI.
- `pip-audit` runs in CI to detect known vulnerabilities.
- New dependencies require a review of the dependency tree.

---

## 11. Code Review Checklist

Every PR must pass this checklist before merging. Reviewers
explicitly verify each item.

### Functionality

- [ ] Does the code do what the PR description says?
- [ ] Are edge cases handled (empty input, None, large input)?
- [ ] Does the change match the relevant design document?
- [ ] Are there new public API changes? If so, is API.md updated?

### Architecture

- [ ] Does the code respect layer boundaries (Section 4)?
- [ ] Are imports in the correct direction (inward and downward)?
- [ ] No circular imports?
- [ ] No new third-party runtime dependencies (unless approved)?
- [ ] Does the change fit the component's defined responsibilities?

### Code Quality

- [ ] Type hints on all public functions and methods?
- [ ] Naming follows conventions (Section 3)?
- [ ] No commented-out code?
- [ ] No `print()` statements (use `logging`)?
- [ ] No `except Exception` (catch specific exceptions)?
- [ ] No `eval`, `exec`, `subprocess`, or network calls?
- [ ] Functions are small and single-responsibility?
- [ ] No unnecessary complexity (simplest correct solution)?

### Testing

- [ ] Unit tests added for new functionality?
- [ ] Integration tests added for cross-component changes?
- [ ] Golden/snapshot tests updated if output changed?
- [ ] Regression test added for bug fixes?
- [ ] All tests pass locally?
- [ ] Coverage does not drop below targets?

### Tooling

- [ ] `ruff format` applied?
- [ ] `ruff check` passes (no violations)?
- [ ] `mypy` passes (no errors)?
- [ ] Pre-commit hooks pass?

### Documentation

- [ ] Docstrings added/updated for public API?
- [ ] Changelog entry added if user-visible change?
- [ ] Design documents updated if architecture changed?
- [ ] Module docstring present for new modules?

---

## 12. AI-Assisted Development

### Context

AI assistants (including Cascade, Copilot, and similar tools) are
welcome contributors to behave-lint. However, AI-generated code
carries specific risks that these rules mitigate.

### Mandatory Rules

1. **Never invent architecture.** AI must follow the existing
   design documents. If a design document is ambiguous, ask for
   clarification rather than guessing. Do not create new components,
   layers, or patterns not defined in the design.

2. **Follow existing specifications.** All immutable documents
   (VISION.md through IMPLEMENTATION_ROADMAP.md) are the source of
   truth. AI must not contradict them. If a contradiction is
   detected, report it rather than working around it.

3. **Preserve backward compatibility.** AI must not make breaking
   changes to the public API without explicit instruction. Public
   API changes require maintainer review and API.md updates.

4. **Keep commits focused.** One PR addresses one concern. AI must
   not bundle unrelated changes. If a task requires changes to
   multiple components, split into multiple PRs.

5. **Generate tests with production code.** Every new function,
   class, or rule must include tests in the same PR. AI must not
   defer testing to a follow-up.

6. **Avoid speculative abstractions.** Do not add interfaces,
   protocols, or base classes "for future use." Add abstractions
   when there are at least two concrete implementations. YAGNI
   (You Aren't Gonna Need It) applies.

7. **No AI signatures.** Do not add comments like "Generated by
   Copilot" or "AI-assisted." Code authorship is tracked by Git.
   The code must stand on its own quality.

8. **Verify before asserting.** AI must not claim "this function
   exists" or "this import works" without verification. Use tools
   to read files and check imports before making assertions.

9. **Respect the dependency direction.** AI must not introduce
   imports that violate the layering rules (Section 4).
   Architecture tests will catch violations, but AI should not
   create them in the first place.

10. **Document deviations.** If AI deviates from any guideline
    (with justification), the deviation must be documented in the
    PR description.

### Why These Rules Exist

AI assistants are powerful but can produce plausible-looking code
that violates architectural constraints. The rules above ensure
AI-generated code meets the same standards as human-generated code.
The primary risk is not bad code — it is code that looks good but
violates invisible constraints (layering, API stability, dependency
direction).

---

## 13. Definition of Done

A feature, bug fix, or change is **done** when all of the following
are true. No exceptions.

### Code

- [ ] Implementation complete and reviewed.
- [ ] Type hints on all public functions and methods.
- [ ] No `mypy` errors (`mypy src/`).
- [ ] No `ruff` violations (`ruff check src/ tests/`).
- [ ] `ruff format` applied (`ruff format src/ tests/`).
- [ ] No commented-out code.
- [ ] No `print()` statements.
- [ ] No `TODO` without an issue number.

### Tests

- [ ] Unit tests pass (`pytest -m unit`).
- [ ] Integration tests pass (`pytest -m integration`).
- [ ] Golden tests pass (`pytest -m golden`).
- [ ] Snapshot tests pass (`pytest -m snapshot`).
- [ ] Architecture tests pass (`pytest -m architecture`).
- [ ] Coverage targets met (90%+ core, 80%+ non-core).
- [ ] Regression test added for bug fixes.

### Documentation

- [ ] Public API changes documented in docstrings.
- [ ] API.md updated if public API changed.
- [ ] Changelog entry added for user-visible changes.
- [ ] Module docstrings added for new modules.
- [ ] Design documents updated if architecture changed.

### CI

- [ ] CI pipeline green on all platforms (Windows, macOS, Linux).
- [ ] CI pipeline green on all Python versions (3.11, 3.12, 3.13).
- [ ] No performance regression (if benchmarks apply).

### Review

- [ ] At least one maintainer approval.
- [ ] All review comments addressed.
- [ ] PR description explains what, why, and how.

---

## 14. Future Evolution

### How These Guidelines Evolve

These guidelines are **evolving** (not immutable like the design
documents). Changes follow this process:

1. **Propose:** Open an issue describing the proposed change, its
   rationale, and its impact.
2. **Discuss:** Maintainers and contributors discuss the proposal.
   Disagreements are resolved by the principal maintainer.
3. **Document:** Update this document with the change. The PR
   includes the rationale and a summary of the discussion.
4. **Announce:** Significant changes are announced in the changelog
   and discussed in the next contributor meeting.

### What May Change

- **Python version support:** New Python versions are added when
  `behave-model` supports them. Old versions are dropped in major
  releases.
- **Tooling:** Ruff, mypy, and pytest versions are updated as new
  versions are released. Configuration may change to adopt new
  rules.
- **Testing practices:** New test types (property-based, mutation,
  fuzzing) may be added as the project matures.
- **Performance targets:** Targets may be tightened as the tool
  matures and user expectations grow.
- **AI-assisted development rules:** Rules may be refined as AI
  tools evolve and their capabilities and limitations become
  clearer.

### What Must Not Change

- **Layering rules** (Section 4): These are architectural and
  defined by ARCHITECTURE.md (immutable).
- **Public API stability** commitment: Semantic Versioning is a
  contract, not a guideline.
- **Minimal dependency policy** (Section 10): Adding runtime
  dependencies requires strong justification and maintainer
  approval. This policy is a core project value.
- **Fail isolated principle** (Section 8): This is a user experience
  commitment, not a convenience.

### Versioning of Guidelines

This document is versioned with the code. Changes to guidelines
that affect contributor workflow are mentioned in the changelog
under "Changed" or "Added."

---

## Appendix A: Consistency Check

| # | Check | Result |
|---|---|---|
| 1 | Python version support (3.11+) matches REPOSITORY_DESIGN.md Section 6 and ARCHITECTURE.md Section 17 | Consistent |
| 2 | Layering rules match ARCHITECTURE.md Section 4 (five layers, inward and downward) | Consistent |
| 3 | Component responsibilities match COMPONENT_DESIGN.md Section 2 (C01–C20) | Consistent |
| 4 | Naming conventions match REPOSITORY_DESIGN.md Section 5 | Consistent |
| 5 | Testing pyramid matches ARCHITECTURE.md Section 18 and REPOSITORY_DESIGN.md Section 7 | Consistent |
| 6 | Error handling (fail isolated, exit codes) matches ARCHITECTURE.md Section 14 | Consistent |
| 7 | Logging levels and destinations match ARCHITECTURE.md Section 16 | Consistent |
| 8 | Dependency policy (minimal, behave-model only) matches ARCHITECTURE.md Section 17 | Consistent |
| 9 | Tooling (Ruff, mypy, pytest) matches REPOSITORY_DESIGN.md Section 10 | Consistent |
| 10 | Public API boundaries match API.md Section 3 | Consistent |
| 11 | Performance targets match SPECIFICATION.md Section 13 | Consistent |
| 12 | Security constraints (no eval, no subprocess, no network) match ARCHITECTURE.md Section 19 | Consistent |
| 13 | Rule documentation (metadata-driven) matches RULE_TAXONOMY.md Section 10 | Consistent |
| 14 | Changelog format (Keep a Changelog) matches REPOSITORY_DESIGN.md Section 8 | Consistent |
| 15 | Coverage targets (90%+ core, 80%+ non-core) match REPOSITORY_DESIGN.md Section 7 | Consistent |

**No inconsistencies detected.**
