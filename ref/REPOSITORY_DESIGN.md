# behave-lint — Repository & Package Design

> **Status:** Canonical repository and package organization specification.
> **Audience:** Core maintainers, contributors, plugin authors, CI engineers,
> and packaging engineers.
> **Scope:** The complete repository layout, Python package organization,
> module boundaries, naming conventions, build strategy, test organization,
> documentation structure, and tooling configuration for behave-lint. This
> document does not define implementation, code, concrete rules, or internal
> architecture — those belong to other documents.
> **Dependencies:** This document follows VISION.md, SPECIFICATION.md,
> ARCHITECTURE.md, API.md, RULE_ENGINE.md, DIAGNOSTIC_ENGINE.md,
> CONFIGURATION_SYSTEM.md, and COMPONENT_DESIGN.md. Inconsistencies, if any,
> are reported in **Appendix A**.

---

## Table of Contents

1. [Repository Philosophy](#1-repository-philosophy)
2. [Repository Layout](#2-repository-layout)
3. [Python Package Layout](#3-python-package-layout)
4. [Module Boundaries](#4-module-boundaries)
5. [Naming Conventions](#5-naming-conventions)
6. [Build Strategy](#6-build-strategy)
7. [Testing Layout](#7-testing-layout)
8. [Documentation Layout](#8-documentation-layout)
9. [Examples](#9-examples)
10. [Tooling](#10-tooling)
11. [Dependency Management](#11-dependency-management)
12. [CI/CD](#12-cicd)
13. [Release Process](#13-release-process)
14. [Future Evolution](#14-future-evolution)

---

## 1. Repository Philosophy

### Why This Organization

The behave-lint repository follows a **single-package, src-layout**
organization with a clear separation between source code, tests,
documentation, examples, and tooling. This organization was chosen
for four reasons:

**1. Contributor clarity.** A new contributor should be able to
locate any file within seconds. The top-level directory names are
self-explanatory: `src/` contains source, `tests/` contains tests,
`docs/` contains documentation, `examples/` contains examples. No
hidden conventions, no ambiguous locations.

**2. Packaging correctness.** The `src/` layout prevents implicit
imports from the working directory. Without it, tests might import
the package from the repository root rather than from the installed
location, masking packaging errors. The `src/` layout ensures that
the package is imported exactly as a user would import it after
`pip install`.

**3. Scalability.** The repository is organized to grow from a v1
with 20 components and ~50 rules to a v5+ with 100+ rules, plugin
SDK, LSP server, and marketplace integration. Each growth area has
a designated location — new rules go in `src/behave_lint/rules/`,
new reporters in `src/behave_lint/reporters/`, new tests in the
corresponding `tests/` subdirectory.

**4. CI-friendliness.** The repository structure is designed for
fast, parallel CI pipelines. Tests are organized by type (unit,
integration, golden, performance) so that CI can run them in
parallel jobs. The `src/` layout ensures that `pip install -e .`
works correctly in CI without path manipulation.

### How It Scales

| Growth area | Where it goes | How it scales |
|---|---|---|
| New rules | `src/behave_lint/rules/` | One module per rule category; one file per rule |
| New reporters | `src/behave_lint/reporters/` | One file per reporter |
| New tests | `tests/unit/`, `tests/integration/`, etc. | Mirror the source structure |
| New documentation | `docs/` | One file per document; numbered by phase |
| New examples | `examples/` | One directory per example project |
| New CI workflows | `.github/workflows/` | One file per workflow |
| New tooling config | Root files or `pyproject.toml` | Tool-specific sections |

### How Contributors Benefit

- **Onboarding:** A contributor reads `CONTRIBUTING.md`, navigates
  to `src/behave_lint/`, finds the relevant module, and starts
  coding. The structure is self-documenting.
- **Testing:** Tests mirror the source structure. A contributor
  working on `src/behave_lint/rules/correctness/duplicate_scenario.py`
  knows the test is at `tests/unit/rules/correctness/test_duplicate_scenario.py`.
- **Review:** Pull requests are scoped by directory. A rule change
  touches `src/behave_lint/rules/` and `tests/unit/rules/`. A
  documentation change touches `docs/`. Reviewers are assigned by
  directory ownership (CODEOWNERS).

### Design Validation

**Why src-layout over flat layout?** The `src/` layout prevents
implicit imports from the working directory, ensuring that tests
import the installed package, not the local directory. This catches
packaging errors early (e.g., missing `__init__.py`, incorrect
relative imports) that would otherwise surface only after
publication to PyPI.

**Alternatives considered:**

- *Flat layout (package at repository root):* Simpler but allows
  implicit imports. Rejected — masks packaging errors.
- *Monorepo (multiple packages):* Premature for v1. behave-lint is
  a single package. A monorepo adds tooling complexity (workspace
  management, cross-package testing). Considered for v3+ if the
  plugin SDK or LSP server becomes a separate package.

**Trade-offs:** The `src/` layout adds one level of directory
nesting. This is a minor inconvenience outweighed by the packaging
correctness benefit.

**Long-term impact:** The `src/` layout is the standard for modern
Python projects (Ruff, Pytest, FastAPI all use it). It scales
indefinitely and supports future package splitting without
restructuring.

---

## 2. Repository Layout

### Complete Top-Level Layout

```
behave-lint/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # Main CI pipeline
│   │   ├── release.yml         # Release automation
│   │   ├── docs.yml            # Documentation deployment
│   │   └── nightly.yml         # Nightly performance benchmarks
│   ├── CODEOWNERS              # Directory ownership
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       ├── feature_request.md
│       └── rule_proposal.md
├── docs/
│   ├── VISION.md
│   ├── SPECIFICATION.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── RULE_ENGINE.md
│   ├── DIAGNOSTIC_ENGINE.md
│   ├── CONFIGURATION_SYSTEM.md
│   ├── PLUGIN_SYSTEM.md        # (planned)
│   ├── COMPONENT_DESIGN.md
│   ├── REPOSITORY_DESIGN.md
│   ├── CONTRIBUTING.md
│   ├── DEVELOPER_GUIDE.md
│   ├── MIGRATION_GUIDE.md
│   ├── FAQ.md
│   └── CHANGELOG.md
├── examples/
│   ├── minimal/                # Minimal .feature project
│   ├── enterprise/             # Multi-team enterprise setup
│   ├── plugin_rule/            # Custom rule plugin
│   ├── plugin_reporter/        # Custom reporter plugin
│   ├── plugin_config/          # Custom configuration plugin
│   └── configs/                # Configuration examples
├── scripts/
│   ├── generate_fixtures.py    # Generate test fixtures
│   ├── benchmark.py            # Run performance benchmarks
│   └── release.py              # Release helper script
├── src/
│   └── behave_lint/
│       ├── __init__.py         # Public API exports
│       ├── __main__.py         # `python -m behave_lint` entry
│       ├── cli/                # Presentation layer
│       ├── engine/             # Application layer
│       ├── rules/              # Domain layer (rules)
│       ├── diagnostics/        # Domain layer (diagnostics)
│       ├── configuration/      # Application layer (config)
│       ├── reporters/          # Application layer (output)
│       ├── plugins/            # Infrastructure layer (plugins)
│       ├── infrastructure/     # Infrastructure layer (loader, cache)
│       ├── models/             # Domain layer (data models)
│       ├── services/           # Utilities layer (logging, profiling)
│       ├── metadata/           # Domain layer (rule metadata)
│       ├── statistics/         # Application layer (metrics)
│       ├── autofix/            # Application layer (future)
│       └── utils/              # Utilities layer
├── tests/
│   ├── unit/                   # Unit tests (mirror src/ structure)
│   ├── integration/            # Integration tests
│   ├── golden/                 # Golden output tests
│   ├── snapshot/               # Diagnostic snapshot tests
│   ├── performance/            # Performance benchmarks
│   ├── regression/             # Bug regression tests
│   ├── architecture/           # Architecture rule tests
│   ├── fixtures/               # Shared test fixtures
│   └── conftest.py             # Pytest configuration
├── benchmarks/
│   ├── projects/               # Generated benchmark projects
│   └── results/                # Benchmark result history
├── .gitignore
├── .pre-commit-config.yaml     # Pre-commit hooks
├── CODE_OF_CONDUCT.md
├── LICENSE
├── README.md
├── pyproject.toml              # Build, deps, tooling config
└── CHANGELOG.md
```

### Top-Level Directory Purposes

| Directory | Purpose | Mutable? |
|---|---|---|
| `.github/` | GitHub-specific files: workflows, templates, codeowners | Yes |
| `docs/` | All design documents, guides, and reference material | Yes |
| `examples/` | Example projects for users and contributors | Yes |
| `scripts/` | Developer automation scripts (not shipped) | Yes |
| `src/` | Source code (the Python package) | Yes |
| `tests/` | All test suites | Yes |
| `benchmarks/` | Performance benchmark projects and results | Yes |

### Root File Purposes

| File | Purpose |
|---|---|
| `.gitignore` | Git ignore rules (cache, build artifacts, virtualenvs) |
| `.pre-commit-config.yaml` | Pre-commit hook configuration (ruff, format check) |
| `CODE_OF_CONDUCT.md` | Community code of conduct |
| `LICENSE` | MIT license text |
| `README.md` | Project overview, quick start, badges |
| `pyproject.toml` | Build system, dependencies, tooling config |
| `CHANGELOG.md` | User-facing changelog (Keep a Changelog format) |

### Design Validation

**Why `docs/` at the root rather than inline?** Design documents
(VISION, SPECIFICATION, ARCHITECTURE, etc.) are project-level
artifacts, not source code. Placing them in `docs/` keeps the
repository root clean and separates documentation from code. This
matches the convention used by Ruff, FastAPI, and Pytest.

**Why `benchmarks/` separate from `tests/performance/`?**
Benchmark projects are large generated datasets (10–5000 feature
files) that should not be part of the test suite. They are
generated by `scripts/generate_fixtures.py` and stored in
`benchmarks/projects/`. Performance tests in `tests/performance/`
reference these projects but do not contain them.

**Alternatives considered:**

- *Inline documentation (docs in `src/`):* Rejected — mixes
  documentation with code, makes navigation harder.
- *No separate benchmarks directory:* Rejected — benchmark data is
  too large for `tests/` and has different lifecycle (generated,
  not hand-maintained).

**Trade-offs:** More top-level directories means more places to
look. Mitigated by self-explanatory names and the table above.

**Long-term impact:** The layout scales to accommodate future
directories (e.g., `lsp/` for LSP server, `sdk/` for plugin SDK)
without restructuring.

---

## 3. Python Package Layout

### Package Overview

The `behave_lint` package is organized into subpackages that map
directly to the architectural layers defined in ARCHITECTURE.md
Section 4 and the components defined in COMPONENT_DESIGN.md Section
2.

### Subpackage Map

| Subpackage | Layer | Components | Responsibility |
|---|---|---|---|
| `behave_lint.cli` | Presentation | C01 | CLI argument parsing, command routing, exit codes |
| `behave_lint.engine` | Application | C03, C04, C05, C17, C20 | Lint engine, rule registry, rule executor, validation, error handler |
| `behave_lint.configuration` | Application | C02 | Configuration loading, merging, validation |
| `behave_lint.reporters` | Application | C08 | Reporter selection, coordination, built-in reporters |
| `behave_lint.statistics` | Application | C13 | Run-level metrics collection |
| `behave_lint.autofix` | Application | C18 | Auto-fix coordination (future) |
| `behave_lint.rules` | Domain | C06, C19 | Rule base class, built-in rules, visitor engine, documentation provider |
| `behave_lint.diagnostics` | Domain | C07 | Diagnostic model, collector, filtering, sorting |
| `behave_lint.models` | Domain | — | Shared data models (Severity, Category, enums) |
| `behave_lint.metadata` | Domain | C16 | Rule metadata registry |
| `behave_lint.infrastructure` | Infrastructure | C10, C11, C12 | File discovery, project loader, cache manager |
| `behave_lint.plugins` | Infrastructure | C09 | Plugin discovery, loading, isolation |
| `behave_lint.services` | Utilities | C14, C15 | Logging manager, performance monitor |

### Subpackage Details

#### `behave_lint.cli` — Presentation Layer

**Responsibility:** Parse command-line arguments, route commands
(lint, list-rules, explain, version, help), invoke the engine,
render output, and determine exit codes.

**Boundary:** This is the only subpackage that interacts with the
terminal. It depends on `engine`, `configuration`, `reporters`,
and `services`. It does not depend on `infrastructure` or `rules`
directly.

**Public exports:** The CLI entry point (`behave-lint` command) is
declared in `pyproject.toml` and points to a function in this
subpackage.

#### `behave_lint.engine` — Application Layer

**Responsibility:** Orchestrate the lint pipeline. Contains the
lint engine (C03), rule registry (C04), rule executor (C05),
validation engine (C17), and error handler (C20).

**Boundary:** Depends on `diagnostics`, `rules`, `infrastructure`,
`configuration`, `services`. Does not depend on `cli`.

#### `behave_lint.rules` — Domain Layer (Rules)

**Responsibility:** Contains the Rule base class, the visitor
engine (C06), the rule documentation provider (C19), and all
built-in rules organized by category.

**Internal structure:**

- `base.py` — Rule base class, RuleContext, RuleResult
- `visitors.py` — Visitor abstractions for tree traversal
- `documentation.py` — Rule documentation provider (C19)
- `correctness/` — Correctness rules (category code `C`)
- `style/` — Style rules (category code `S`)
- `complexity/` — Complexity rules (category code `X`)
- `consistency/` — Consistency rules (category code `K`)
- `pedantic/` — Pedantic rules (category code `P`)
- `step_definitions/` — Step definition rules (category code `D`)

**Boundary:** Depends on `diagnostics`, `models`, `metadata`. Does
not depend on `engine`, `cli`, `infrastructure`, or `configuration`.

#### `behave_lint.diagnostics` — Domain Layer (Diagnostics)

**Responsibility:** Diagnostic data model, diagnostic collector
(C07), filtering, sorting, and deduplication.

**Boundary:** Depends on `models` only. No dependencies on
`engine`, `cli`, `infrastructure`, or `rules`.

#### `behave_lint.configuration` — Application Layer (Config)

**Responsibility:** Configuration manager (C02) — loading,
merging, validation, and defaults from `pyproject.toml`,
environment variables, and CLI arguments.

**Boundary:** Depends on `models`, `services`. Does not depend on
`engine`, `rules`, `diagnostics`, or `cli`.

#### `behave_lint.reporters` — Application Layer (Output)

**Responsibility:** Reporter manager (C08) and built-in reporters
(console, JSON, Markdown, SARIF).

**Internal structure:**

- `manager.py` — Reporter selection and coordination
- `console.py` — Console reporter
- `json_reporter.py` — JSON reporter
- `markdown.py` — Markdown reporter
- `sarif.py` — SARIF reporter

**Boundary:** Depends on `diagnostics`, `models`, `services`. Does
not depend on `engine` or `cli`.

#### `behave_lint.infrastructure` — Infrastructure Layer

**Responsibility:** File discovery (C10), project loader (C11),
cache manager (C12). Integrates with `behave-model` and the file
system.

**Boundary:** Depends on `models`, `services`, and
`behave-model` (external). Does not depend on `engine`, `cli`, or
`rules`.

#### `behave_lint.plugins` — Infrastructure Layer (Plugins)

**Responsibility:** Plugin manager (C09) — entry point discovery,
lazy loading, registration, and isolation.

**Boundary:** Depends on `engine` (for rule registration),
`reporters` (for reporter registration), `configuration` (for
config plugin registration), and `services`. Does not depend on
`cli`.

#### `behave_lint.models` — Domain Layer (Shared Models)

**Responsibility:** Shared enums and data structures used across
layers: `Severity`, `Category`, `RuleMetadata`, `Diagnostic`,
`LintResult`, `Config`.

**Boundary:** Depends on nothing (innermost domain layer). All
other subpackages may depend on `models`.

#### `behave_lint.metadata` — Domain Layer (Rule Metadata)

**Responsibility:** Rule metadata registry (C16) — stores and
provides rule metadata for documentation and validation.

**Boundary:** Depends on `models` only.

#### `behave_lint.statistics` — Application Layer (Metrics)

**Responsibility:** Statistics engine (C13) — collects and
aggregates run-level metrics (diagnostic counts, timing, cache
hits/misses).

**Boundary:** Depends on `models`, `services`.

#### `behave_lint.autofix` — Application Layer (Future)

**Responsibility:** Auto-fix coordinator (C18) — fix collection,
conflict detection, application, rollback. Future component, not
in v1.

**Boundary:** Will depend on `diagnostics`, `services`, `engine`.

#### `behave_lint.services` — Utilities Layer

**Responsibility:** Logging manager (C15) and performance monitor
(C14). Cross-cutting services used by all layers.

**Boundary:** Depends on nothing (innermost utilities layer). All
other subpackages may depend on `services`.

### Design Validation

**Why one subpackage per architectural layer?** The subpackage
boundaries enforce the layering rules defined in ARCHITECTURE.md
Section 4. Import rules can be checked by static analysis (import
inspection in architecture tests). A violation (e.g., `rules`
importing from `engine`) is immediately visible.

**Why `models` separate from `diagnostics`?** `models` contains
shared enums and data structures used by all layers. `diagnostics`
contains the diagnostic collector and processing logic. Separating
them prevents a circular dependency: `rules` depends on `models`
(for `Severity`) but not on `diagnostics` (for the collector).

**Why `rules` in the Domain layer rather than Application?** Rules
are pure functions of (project model, configuration) → diagnostics.
They contain no orchestration logic and no I/O. They depend only
on domain concepts. This matches ARCHITECTURE.md Section 4, which
places visitors and rule metadata in the Domain layer.

**Alternatives considered:**

- *Flat package (no subpackages):* Rejected — 20 components in one
  flat package is un navigable. Subpackages provide boundaries.
- *One subpackage per component:* Rejected — 20 subpackages is
  over-fragmented. Grouping by layer is more natural.
- *Separate packages per layer (monorepo):* Rejected for v1 —
  adds packaging complexity. Considered for v3+ if the plugin SDK
  or LSP server becomes a separate distribution.

**Trade-offs:** Subpackage grouping by layer means some
subpackages contain multiple components (e.g., `engine` contains
C03, C04, C05, C17, C20). This is acceptable because the
components are cohesive (they collaborate closely within the
application layer).

**Long-term impact:** The subpackage structure maps 1:1 to the
architectural layers, making it easy to verify layering rules
automatically and to split packages in the future.

---

## 4. Module Boundaries

### Allowed Imports

Imports follow the dependency direction defined in ARCHITECTURE.md
Section 4 and COMPONENT_DESIGN.md Section 6: **inward and
downward**.

```
cli → engine, configuration, reporters, services, models
engine → diagnostics, rules, infrastructure, configuration, services, models, metadata
configuration → models, services
reporters → diagnostics, models, services
rules → diagnostics, models, metadata, services
diagnostics → models, services
metadata → models
infrastructure → models, services, behave-model (external)
plugins → engine, reporters, configuration, services
statistics → models, services
autofix → diagnostics, services, models
services → (nothing)
models → (nothing)
```

### Forbidden Imports

| Rule | Description |
|---|---|
| No upward imports | `rules` must not import from `engine` |
| No skip-level imports | `cli` must not import from `infrastructure` |
| No circular imports | `engine` → `rules` → `engine` is forbidden |
| No cross-layer imports | `diagnostics` must not import from `configuration` |
| No `behave-model` outside infrastructure | Only `infrastructure` imports `behave-model` |
| No private imports | Public modules must not import from underscore-prefixed modules |

### Circular Dependency Prevention

Circular dependencies are prevented by three mechanisms:

**1. Layering rules.** The dependency direction is acyclic by
design (ARCHITECTURE.md Section 4). If a cycle is detected, it
indicates a design error.

**2. Architecture tests.** The test suite includes architecture
tests (`tests/architecture/`) that use import inspection to verify
dependency rules. These tests run in CI and fail if architectural
rules are violated.

**3. Code review.** The CODEOWNERS file assigns ownership by
directory. Reviewers are responsible for enforcing import rules
during review.

If a cycle is detected, it must be resolved by:
1. Extracting the shared dependency into a lower layer.
2. Introducing an interface (Dependency Inversion) to break the
   cycle.
3. Merging the cyclic modules if they are tightly coupled.

### Public vs. Internal Modules

**Public modules** are importable by users and plugins. They are
exported via `behave_lint/__init__.py` and documented in API.md.

| Public module | Exported via |
|---|---|
| `behave_lint` (top-level) | `__init__.py` — `lint()`, `load_config()`, `Linter`, `Config`, `Diagnostic`, `Severity`, `Category`, `LintResult` |
| `behave_lint.rules` | `rules/__init__.py` — `Rule`, `RuleContext`, `RuleResult`, built-in rule IDs |
| `behave_lint.reporters` | `reporters/__init__.py` — `Reporter`, built-in reporters |
| `behave_lint.errors` | `errors/__init__.py` — Error hierarchy |
| `behave_lint.config` | `config/__init__.py` — Configuration objects |

**Internal modules** are not exported and may change without
notice. They are either:

- Underscore-prefixed (e.g., `_internal.py`)
- Not listed in `__init__.py` `__all__`
- In subpackages not listed as public in API.md

### Design Validation

**Why enforce import rules via architecture tests?** Manual
enforcement is unreliable — a contributor may add an import
without understanding the layering rules. Architecture tests
catch violations automatically in CI.

**Why no `behave-model` imports outside infrastructure?**
ARCHITECTURE.md Section 5 states that only the Project Loader
(C11, in `infrastructure`) imports `behave-model`. All other
components use the returned domain objects. This isolates
`behave-model` API changes to one module.

**Alternatives considered:**

- *No import enforcement:* Rejected — leads to tangled
  dependencies over time.
- *Linting tool for import rules (e.g., `import-linter`):*
  Considered for v1.1+. Architecture tests are sufficient for v1
  and have no additional dependency.

**Trade-offs:** Strict import rules may require pass-through
imports (e.g., `cli` imports `models` via `engine` rather than
directly). This is acceptable — it preserves the architectural
integrity.

**Long-term impact:** The module boundaries ensure that the
codebase remains structured as it grows. New modules are placed
in the appropriate subpackage and follow the import rules.

---

## 5. Naming Conventions

### Packages

- **Python package:** `behave_lint` (snake_case, matches PyPI name
  with hyphens replaced by underscores).
- **Subpackages:** `cli`, `engine`, `rules`, `diagnostics`,
  `configuration`, `reporters`, `infrastructure`, `plugins`,
  `models`, `metadata`, `statistics`, `autofix`, `services` — all
  lowercase, single words where possible.

### Modules

- **Lowercase, snake_case:** `duplicate_scenario.py`,
  `json_reporter.py`, `cache_manager.py`.
- **One responsibility per module:** Each module has a single,
  clear purpose.
- **No abbreviations:** `configuration.py` not `config.py`
  (except for the public API alias `behave_lint.config`).

### Classes

- **PascalCase:** `LintEngine`, `RuleRegistry`, `DiagnosticCollector`.
- **Suffix conventions:** `Manager` (orchestrator), `Registry`
  (lookup), `Collector` (aggregator), `Provider` (data source),
  `Engine` (processor), `Handler` (error/event processor).
- **Rule classes:** `<DescriptiveName>Rule` — e.g.,
  `DuplicateScenarioNameRule`, `MissingBackgroundRule`.

### Functions

- **snake_case:** `load_config()`, `lint()`, `discover_plugins()`.
- **Verb-first naming:** `load_`, `validate_`, `collect_`,
  `filter_`, `sort_`, `report_`.
- **Boolean predicates:** `is_enabled()`, `has_fix()`,
  `can_fix()`.

### Constants

- **UPPER_SNAKE_CASE:** `DEFAULT_SEVERITY`, `MAX_CACHE_SIZE`,
  `EXIT_CODE_SUCCESS`.
- **Module-level only:** Constants are defined at the module
  level, not inside classes or functions.

### Rule IDs

Per SPECIFICATION.md Appendix A:

- **Built-in rules:** `B<category><number>` — e.g., `BC001`
  (Correctness #001), `BS001` (Style #001).
- **Category codes:** `C` (Correctness), `S` (Style), `X`
  (Complexity), `K` (Consistency), `P` (Pedantic), `D` (Step
  Definitions).
- **Plugin rules:** `<custom_prefix><number>` — e.g., `ACME001`.
- **Reserved:** `B000` for parse errors.

### Configuration Keys

Per CONFIGURATION_SYSTEM.md and SPECIFICATION.md Appendix B:

- **kebab-case in TOML:** `max-steps`, `cache-dir`,
  `step-definitions`.
- **snake_case in Python:** `max_steps`, `cache_dir`,
  `step_definitions`.
- **Environment variables:** `BEHAVE_LINT_` prefix, uppercase,
  hyphens to underscores — e.g., `BEHAVE_LINT_CACHE_DIR`.

### Plugin Identifiers

- **Entry point groups:** `behave_lint.rules`,
  `behave_lint.reporters`, `behave_lint.config`.
- **Plugin names:** Lowercase, hyphenated — e.g.,
  `behave-lint-acme-rules`. Matches the PyPI package name.

### CLI Commands

- **Main command:** `behave-lint` (hyphenated, matches PyPI name).
- **Subcommands:** `lint` (default), `--list-rules`, `--explain
  <rule-id>`, `--version`, `--help`.
- **Flags:** `--select`, `--ignore`, `--output`, `--output-file`,
  `--config`, `--cache`, `--no-cache`, `--clear-cache`, `--fix`,
  `--unsafe-fixes`, `--dry-run`, `--verbose`, `--quiet`, `--trace`.

### Design Validation

**Why snake_case for modules and PascalCase for classes?** This
is the Python convention (PEP 8). Following it ensures
consistency with the Python ecosystem and IDE autocomplete
expectations.

**Why kebab-case for TOML keys but snake_case for Python?** TOML
convention uses kebab-case for keys. Python convention uses
snake_case for attributes. The Configuration Manager translates
between them (CONFIGURATION_SYSTEM.md Section 5).

**Alternatives considered:**

- *CamelCase for modules:* Rejected — violates PEP 8.
- *Flat rule IDs (no category prefix):* Rejected — category
  prefix provides semantic grouping and is defined in
  SPECIFICATION.md Appendix A.

**Trade-offs:** The naming conventions are standard Python
practice. No significant trade-offs.

**Long-term impact:** Consistent naming reduces cognitive load
for contributors and enables IDE autocomplete to work effectively.

---

## 6. Build Strategy

### Build System

The build system is **hatchling** (Hatch's build backend), as
specified in ARCHITECTURE.md Section 17. Hatchling is a modern,
standards-compliant PEP 517/518 build backend.

**Why hatchling?**

- Standards-compliant (PEP 517, PEP 518, PEP 621).
- Fast (Rust-based core).
- Supports `src/` layout natively.
- Minimal configuration (all config in `pyproject.toml`).
- Used by modern Python projects (Ruff, Polars, etc.).

### Packaging

The package is defined entirely in `pyproject.toml`:

- **Name:** `behave-lint`
- **Version:** Semantic versioning (see Section 13)
- **Python requirement:** `>=3.11` (matching `behave-model`)
- **Runtime dependency:** `behave-model>=x.y,<x.z`
- **Entry point:** `behave-lint = "behave_lint.cli:main"`
- **Entry point groups:** `behave_lint.rules`,
  `behave_lint.reporters`, `behave_lint.config`

### Versioning

The version follows **Semantic Versioning 2.0.0**:

- **Major:** Breaking changes to the public API (removals,
  signature changes, behavior changes).
- **Minor:** New features, new rules, new reporters (backward
  compatible).
- **Patch:** Bug fixes, performance improvements (backward
  compatible).

The version is defined in `pyproject.toml` under
`[project] version`. It is the single source of truth for the
package version.

### Distribution

**PyPI:** The package is published to PyPI as `behave-lint`.
Publication is automated via GitHub Actions (see Section 12).

**Wheels:** Pure Python wheel (`*.whl`) and sdist (`*.tar.gz`).
No platform-specific wheels are needed (pure Python, no C
extensions).

**Editable installs:** `pip install -e .` works with the `src/`
layout and hatchling. This is the primary development setup.

### Developer Setup

The developer setup is designed to be minimal:

1. Clone the repository.
2. `pip install -e ".[dev]"` — installs the package in editable
   mode with all development dependencies.
3. `pre-commit install` — installs pre-commit hooks (ruff, format
   check).
4. `pytest` — runs the full test suite.

No virtualenv management scripts are provided. Developers are
expected to manage their own virtual environments (venv, conda,
uv, etc.).

### Release Artifacts

Each release produces:

- **PyPI package:** `behave-lint-x.y.z` (wheel + sdist).
- **GitHub Release:** Tagged release with changelog excerpt.
- **Documentation:** Updated docs deployed to GitHub Pages (or
  ReadTheDocs).

### Design Validation

**Why hatchling over setuptools?** Setuptools is legacy and
requires more configuration. Hatchling is modern,
standards-compliant, and minimal. It is the build backend used
by Ruff and other modern Python projects.

**Why pure Python (no compiled extensions)?** behave-lint is a
static analysis tool with no performance-critical code that
would benefit from C extensions. The bottleneck is parsing
(delegated to `behave-model`). Pure Python simplifies
packaging, distribution, and installation.

**Alternatives considered:**

- *setuptools:* Rejected — legacy, more configuration, less
  standards-compliant.
- *flit:* Rejected — does not support `src/` layout as naturally.
- *Poetry:* Rejected — build backend is not PEP 517 compliant
  in all cases; adds unnecessary project management features.

**Trade-offs:** Hatchling is newer than setuptools, meaning fewer
community resources. This is outweighed by its simplicity and
standards compliance.

**Long-term impact:** The build strategy supports future
compiled extensions (if needed for performance) by adding a
build extension to hatchling. The `pyproject.toml`-based
configuration is future-proof.

---

## 7. Testing Layout

### Test Organization

Tests are organized by type and mirror the source structure
within each type:

```
tests/
├── unit/                   # Unit tests (mirror src/ structure)
│   ├── cli/
│   ├── engine/
│   ├── rules/
│   │   ├── correctness/
│   │   ├── style/
│   │   ├── complexity/
│   │   ├── consistency/
│   │   ├── pedantic/
│   │   └── step_definitions/
│   ├── diagnostics/
│   ├── configuration/
│   ├── reporters/
│   ├── infrastructure/
│   ├── plugins/
│   ├── models/
│   ├── metadata/
│   ├── statistics/
│   └── services/
├── integration/            # End-to-end pipeline tests
│   ├── test_pipeline.py
│   ├── test_config_loading.py
│   ├── test_plugin_discovery.py
│   ├── test_cache_behavior.py
│   └── test_cli.py
├── golden/                 # Golden output tests
│   ├── fixtures/           # Input .feature files
│   ├── expected/           # Expected output (console, JSON, etc.)
│   └── test_golden.py
├── snapshot/               # Diagnostic snapshot tests
│   ├── fixtures/           # Input .feature files
│   ├── snapshots/          # Expected diagnostic sets
│   └── test_snapshots.py
├── performance/            # Performance benchmarks
│   ├── test_perf_small.py  # 10 files
│   ├── test_perf_medium.py # 100 files
│   ├── test_perf_large.py  # 1000 files
│   └── test_perf_xlarge.py # 5000 files
├── regression/             # Bug regression tests
│   ├── test_issue_001.py
│   ├── test_issue_042.py
│   └── ...
├── architecture/           # Architecture rule tests
│   ├── test_import_rules.py
│   ├── test_no_circular_imports.py
│   ├── test_layer_separation.py
│   └── test_no_global_state.py
├── fixtures/               # Shared test fixtures
│   ├── feature_files/      # Sample .feature files
│   ├── projects/           # Sample project structures
│   ├── configs/            # Sample configuration files
│   └── helpers/            # Test helper utilities
└── conftest.py             # Pytest configuration and shared fixtures
```

### Test Types

| Type | Scope | What is tested | How |
|---|---|---|---|
| Unit | Individual components | Each rule, reporter, config loader, cache, etc. | Mock inputs; no real files |
| Integration | Multiple components | Full pipeline, config loading, plugin discovery, CLI | Real `.feature` files; real `behave-model` |
| Golden | Output stability | Console, JSON, Markdown, SARIF output | Compare against expected output files |
| Snapshot | Diagnostic stability | Diagnostic sets for representative inputs | Compare against snapshot files |
| Performance | Execution time/memory | Benchmark projects (10–5000 files) | Measure time/memory; compare against targets |
| Regression | Bug fixes | Each bug fix has a test | Reproduce bug; verify fix |
| Architecture | Architectural rules | Import direction, layer separation, no global state | Import inspection; static analysis |

### Fixtures

**Shared fixtures** are in `tests/fixtures/`:

- `feature_files/` — Sample `.feature` files covering various
  Gherkin constructs and anti-patterns.
- `projects/` — Sample project structures (minimal, multi-feature,
  enterprise).
- `configs/` — Sample `pyproject.toml` files with various
  configurations.
- `helpers/` — Test utility functions (project model builders,
  diagnostic assertion helpers, mock file systems).

**Pytest fixtures** are defined in `conftest.py` files at each
level:

- `tests/conftest.py` — Global fixtures (logger, temp directory,
  mock config).
- `tests/unit/rules/conftest.py` — Rule-specific fixtures (sample
  project models, visitor helpers).

### Coverage

- **Target:** 90%+ for core components (engine, rule engine,
  configuration, diagnostics).
- **Measurement:** `pytest-cov` with branch coverage.
- **Enforcement:** CI fails if coverage drops below the target
  for core components.

### Design Validation

**Why mirror the source structure in `tests/unit/`?** A
contributor working on
`src/behave_lint/rules/correctness/duplicate_scenario.py` knows
the test is at
`tests/unit/rules/correctness/test_duplicate_scenario.py`. This
1:1 mapping makes it trivial to locate tests.

**Why separate golden and snapshot tests?** Golden tests verify
output format (console, JSON, Markdown). Snapshot tests verify
diagnostic content (which diagnostics are produced). They catch
different classes of bugs — a format change breaks golden tests
but not snapshot tests, and vice versa.

**Why architecture tests?** ARCHITECTURE.md Section 18 specifies
architecture tests for dependency direction, layer separation,
and no global state. These tests are the enforcement mechanism
for the module boundaries defined in Section 4 of this document.

**Alternatives considered:**

- *All tests in one directory:* Rejected — makes it hard to run
  specific test types in CI.
- *No separate regression tests:* Rejected — regression tests
  provide traceability (issue/PR number) and are never deleted.

**Trade-offs:** Multiple test directories means more
configuration. Mitigated by `conftest.py` and `pyproject.toml`
pytest configuration.

**Long-term impact:** The test layout supports future test types
(property-based testing, mutation testing, fuzzing) by adding
new directories.

---

## 8. Documentation Layout

### Documentation Structure

```
docs/
├── VISION.md               # Project vision and mission
├── SPECIFICATION.md        # Full feature specification
├── ARCHITECTURE.md         # Internal architecture
├── API.md                  # Public API specification
├── RULE_ENGINE.md          # Rule engine design
├── DIAGNOSTIC_ENGINE.md    # Diagnostic engine design
├── CONFIGURATION_SYSTEM.md # Configuration system design
├── PLUGIN_SYSTEM.md        # Plugin system design (planned)
├── COMPONENT_DESIGN.md     # Component architecture
├── REPOSITORY_DESIGN.md    # This document
├── CONTRIBUTING.md         # How to contribute
├── DEVELOPER_GUIDE.md      # Guide for core developers
├── MIGRATION_GUIDE.md      # Version migration guides
├── FAQ.md                  # Frequently asked questions
└── CHANGELOG.md            # User-facing changelog
```

### Document Categories

| Category | Documents | Audience | Stability |
|---|---|---|---|
| Design | VISION, SPECIFICATION, ARCHITECTURE, API, RULE_ENGINE, DIAGNOSTIC_ENGINE, CONFIGURATION_SYSTEM, PLUGIN_SYSTEM, COMPONENT_DESIGN, REPOSITORY_DESIGN | Core maintainers, architects | Immutable after publication |
| Guide | CONTRIBUTING, DEVELOPER_GUIDE, MIGRATION_GUIDE | Contributors, developers | Evolving |
| Reference | FAQ, CHANGELOG | All users | Evolving |

### README.md

The repository root `README.md` is the first thing a visitor sees.
It contains:

- Project name and one-line description.
- Badges (CI status, PyPI version, Python versions, license).
- Quick start (install + run in 3 commands).
- Feature overview (bullet list).
- Links to documentation (docs/ directory).
- Link to CONTRIBUTING.md.
- License (MIT).

### Contributing Guide

`docs/CONTRIBUTING.md` contains:

- How to set up the development environment.
- How to run tests (unit, integration, golden, performance).
- How to add a new rule (step-by-step).
- How to add a new reporter.
- How to report bugs and request features.
- Coding standards (naming, formatting, type hints).
- Pull request process (branch naming, commit messages, review
  criteria).

### Developer Guide

`docs/DEVELOPER_GUIDE.md` contains:

- Architecture overview (links to ARCHITECTURE.md).
- Component map (links to COMPONENT_DESIGN.md).
- How to debug rules (tracing, verbose mode).
- How to profile performance (`--trace`, benchmark scripts).
- How to add a new component (design process, validation
  requirements).
- How to release a new version (release process, checklist).

### Migration Guide

`docs/MIGRATION_GUIDE.md` contains:

- Breaking changes between major versions.
- How to migrate configuration between versions.
- How to migrate custom rules between API versions.
- Deprecated features and their removal timeline.

### Changelog

`CHANGELOG.md` (at repository root for visibility) follows the
[Keep a Changelog](https://keepachangelog.com/) format:

- Sections: Added, Changed, Deprecated, Removed, Fixed, Security.
- Versions: Listed in reverse chronological order.
- Each entry links to the relevant PR or issue.

### Design Validation

**Why documentation in `docs/` rather than a wiki?** Documentation
in the repository is versioned with the code. A contributor can
read the documentation for any version by checking out the
corresponding tag. Wiki documentation is unversioned and can drift
from the code.

**Why design documents as Markdown rather than a documentation
generator (Sphinx, MkDocs)?** Markdown is readable in any text
editor, renders natively on GitHub, and requires no build step.
Design documents are for maintainers and contributors, not end
users. A documentation generator may be added for user-facing
documentation in the future.

**Alternatives considered:**

- *Sphinx documentation:* Considered for v1.1+ for user-facing
  docs (rule reference, configuration guide). Design documents
  remain in Markdown.
- *GitHub wiki:* Rejected — unversioned, not in the repository,
  harder to search.

**Trade-offs:** Markdown lacks cross-referencing and indexing.
For design documents, this is acceptable — they are read
linearly.

**Long-term impact:** The documentation layout supports future
Sphinx/MkDocs integration by keeping Markdown files that can be
included in a documentation site.

---

## 9. Examples

### Example Structure

```
examples/
├── minimal/                # Minimal .feature project
│   ├── features/
│   │   └── login.feature
│   └── pyproject.toml      # Minimal behave-lint config
├── enterprise/             # Multi-team enterprise setup
│   ├── features/
│   │   ├── auth/
│   │   ├── billing/
│   │   └── reporting/
│   ├── pyproject.toml      # Enterprise config (select, ignore, severity)
│   └── README.md           # Explanation of enterprise setup
├── plugin_rule/            # Custom rule plugin example
│   ├── src/
│   │   └── acme_lint_rules/
│   │       ├── __init__.py
│   │       └── no_todo_steps.py
│   └── pyproject.toml      # Entry point declaration
├── plugin_reporter/        # Custom reporter plugin example
│   ├── src/
│   │   └── custom_reporter/
│   │       ├── __init__.py
│   │       └── html_reporter.py
│   └── pyproject.toml
├── plugin_config/          # Custom configuration plugin example
│   ├── src/
│   │   └── strict_config/
│   │       └── __init__.py
│   └── pyproject.toml
└── configs/                # Configuration examples
    ├── strict.toml         # All rules enabled, error severity
    ├── minimal.toml        # Only correctness rules
    ├── recommended.toml    # Recommended defaults
    └── ci.toml             # CI-optimized (JSON output, no cache)
```

### Example Descriptions

| Example | Purpose | Audience |
|---|---|---|
| `minimal/` | Show the simplest possible setup | New users |
| `enterprise/` | Show a realistic multi-team configuration | Enterprise users, CI engineers |
| `plugin_rule/` | Show how to write and package a custom rule | Plugin authors |
| `plugin_reporter/` | Show how to write and package a custom reporter | Reporter authors |
| `plugin_config/` | Show how to write a configuration plugin | Plugin authors |
| `configs/` | Show various configuration profiles | All users |

### Design Validation

**Why include plugin examples?** Plugin development is the primary
extension mechanism (ARCHITECTURE.md Section 13). Examples reduce
the barrier to entry for plugin authors by providing working
templates.

**Why not a cookiecutter template?** A cookiecutter template is a
future enhancement (ARCHITECTURE.md Section 20: Custom Rule SDK).
For v1, examples in the repository are sufficient and simpler.

**Alternatives considered:**

- *No examples:* Rejected — examples are critical for adoption
  and contributor onboarding.
- *Examples in documentation:* Rejected — runnable examples in
  the repository are more useful than code blocks in Markdown.

**Trade-offs:** Examples require maintenance to stay current with
API changes. This is acceptable — examples are small and changes
are infrequent within a major version.

**Long-term impact:** Examples serve as the foundation for a
future plugin SDK and cookiecutter template.

---

## 10. Tooling

### Formatting

- **Tool:** Ruff (formatter + linter).
- **Configuration:** `[tool.ruff]` in `pyproject.toml`.
- **Scope:** All Python files in `src/` and `tests/`.
- **Enforcement:** Pre-commit hook + CI check.

### Linting

- **Tool:** Ruff (linting rules).
- **Rules:** Selected rule sets (E, W, F, I, UP, B, SIM, RUF).
- **Configuration:** `[tool.ruff.lint]` in `pyproject.toml`.
- **Enforcement:** Pre-commit hook + CI check.

### Type Checking

- **Tool:** Mypy (static type checker).
- **Configuration:** `[tool.mypy]` in `pyproject.toml`.
- **Strictness:** `strict = true` for `src/`, default for
  `tests/`.
- **Enforcement:** CI check (not pre-commit, to keep pre-commit
  fast).

### Testing

- **Tool:** Pytest.
- **Configuration:** `[tool.pytest.ini_options]` in
  `pyproject.toml`.
- **Plugins:** `pytest-cov` (coverage), `pytest-xdist` (parallel
  test execution).
- **Markers:** `@pytest.mark.unit`, `@pytest.mark.integration`,
  `@pytest.mark.golden`, `@pytest.mark.snapshot`,
  `@pytest.mark.performance`, `@pytest.mark.regression`,
  `@pytest.mark.architecture`.

### Coverage

- **Tool:** `pytest-cov`.
- **Configuration:** `[tool.coverage]` in `pyproject.toml`.
- **Target:** 90%+ for core components.
- **Report:** Terminal + XML (for CI integration).

### Benchmarks

- **Tool:** Custom benchmark script (`scripts/benchmark.py`).
- **Projects:** Generated by `scripts/generate_fixtures.py` in
  `benchmarks/projects/`.
- **Metrics:** Execution time, memory usage, cache hit rate.
- **Frequency:** Nightly CI run + on-demand.

### Documentation Generation

- **Current:** Markdown (no generation needed).
- **Future:** MkDocs or Sphinx for user-facing documentation
  (rule reference, configuration guide). Design documents remain
  in Markdown.

### Release Automation

- **Tool:** GitHub Actions + `scripts/release.py`.
- **Process:** Tag push → CI → build → publish to PyPI → GitHub
  Release.
- **Details:** See Section 12 (CI/CD) and Section 13 (Release
  Process).

### Design Validation

**Why Ruff over Black + Flake8?** Ruff is a single tool that
replaces both a formatter (Black) and a linter (Flake8 + plugins).
It is faster (Rust-based), has fewer dependencies, and is used by
modern Python projects (FastAPI, Pydantic, etc.).

**Why Mypy over Pyright?** Mypy is the standard Python type
checker with the widest ecosystem support. Pyright is faster but
less configurable. Mypy is sufficient for behave-lint's needs.

**Why pytest-xdist for parallel tests?** The test suite includes
performance tests that are slow. Parallel execution reduces CI
time. `pytest-xdist` is the standard parallel execution plugin
for pytest.

**Alternatives considered:**

- *Black + Flake8:* Rejected — two tools, slower, more
  configuration.
- *Pyright:* Considered for v1.1+ if Mypy performance becomes an
  issue.
- *No coverage enforcement:* Rejected — coverage targets prevent
  quality degradation.

**Trade-offs:** Ruff is newer than Black/Flake8, meaning fewer
community resources. This is outweighed by its speed and
all-in-one nature.

**Long-term impact:** The tooling configuration is in
`pyproject.toml`, following modern Python conventions. New tools
can be added by adding sections to `pyproject.toml`.

---

## 11. Dependency Management

### Internal Dependencies

Internal dependencies follow the layering rules (Section 4).
The dependency graph is acyclic and enforced by architecture
tests.

### External Dependencies

| Dependency | Type | Purpose | Required? |
|---|---|---|---|
| `behave-model` | Runtime | Domain model, parsing, validation | Yes |
| Python stdlib | Runtime | All other functionality | Yes |
| `hatchling` | Build | Package building | Dev only |
| `pytest` | Dev | Testing | Dev only |
| `pytest-cov` | Dev | Coverage measurement | Dev only |
| `pytest-xdist` | Dev | Parallel test execution | Dev only |
| `ruff` | Dev | Formatting + linting | Dev only |
| `mypy` | Dev | Type checking | Dev only |
| `pre-commit` | Dev | Pre-commit hooks | Dev only |

### Optional Dependencies

| Dependency | Purpose | When |
|---|---|---|
| `behave-lint-sdk` | Plugin SDK (base classes, utilities) | Future (v1.1+) |
| `behave-lint-lsp` | LSP server | Future (v2.0+) |

Optional dependencies are declared as `extras` in
`pyproject.toml`:

- `[project.optional-dependencies] dev = [...]` — development
  dependencies.
- Future: `sdk = [...]`, `lsp = [...]`.

### Plugin Dependencies

Plugins are separate packages installed via `pip install`. They
declare their own dependencies in their `pyproject.toml`.
behave-lint does not manage plugin dependencies — plugins are
regular Python packages.

### Version Constraints

- **`behave-model`:** `>=x.y,<x.z` — compatible version range,
  updated when `behave-model` releases new versions.
- **Python:** `>=3.11` — matching `behave-model` (ARCHITECTURE.md
  Section 17).
- **Dev dependencies:** Not pinned to specific versions (latest
  compatible). Ruff, pytest, mypy are fast-moving and pinning
  creates maintenance burden.

### Design Validation

**Why minimal runtime dependencies?** ARCHITECTURE.md Section 17
states: "Minimal dependencies reduce the attack surface,
maintenance burden, and installation time." The only runtime
dependency is `behave-model` (required for parsing). All other
functionality uses the Python standard library.

**Why not pin dev dependencies?** Dev dependencies (ruff, pytest,
mypy) are tools, not libraries. Pinning them creates maintenance
burden (frequent version bumps) without benefit. The latest
compatible version is always used.

**Alternatives considered:**

- *Pinning all dependencies (lockfile):* Rejected for v1 — adds
  complexity. Considered for v1.1+ if reproducibility becomes
  critical.
- *uv for dependency management:* Considered for v1.1+ — faster
  than pip, supports lockfiles. Not needed for v1.

**Trade-offs:** Not pinning dev dependencies means CI may break
when a new version of ruff or mypy introduces changes. This is
mitigated by CI running on every PR and catching issues early.

**Long-term impact:** The minimal dependency strategy ensures
the tool runs in restricted environments (air-gapped CI, minimal
containers). Future dependencies are added only when justified.

---

## 12. CI/CD

### GitHub Actions Workflows

```
.github/workflows/
├── ci.yml              # Main CI pipeline (runs on every PR)
├── release.yml         # Release automation (runs on tag push)
├── docs.yml            # Documentation deployment (runs on main push)
└── nightly.yml         # Nightly performance benchmarks
```

### CI Pipeline (`ci.yml`)

The CI pipeline runs on every pull request and every push to
`main`. It consists of parallel jobs:

| Job | Purpose | Matrix |
|---|---|---|
| lint | Ruff format check + lint check | Python 3.11 |
| typecheck | Mypy strict check | Python 3.11 |
| test-unit | Unit tests + coverage | Python 3.11, 3.12, 3.13 |
| test-integration | Integration tests | Python 3.11, 3.12, 3.13 |
| test-golden | Golden output tests | Python 3.11 |
| test-snapshot | Diagnostic snapshot tests | Python 3.11 |
| test-architecture | Architecture rule tests | Python 3.11 |
| test-regression | Regression tests | Python 3.11 |
| test-os | Cross-platform tests | Python 3.11 × Windows, macOS, Linux |

**Quality gates:** All jobs must pass for a PR to be mergeable.
Coverage must be ≥ 90% for core components.

### Release Workflow (`release.yml`)

Triggered by a tag push (`v*.*.*`):

1. **Build:** Build wheel + sdist using hatchling.
2. **Test:** Run full test suite on the built artifacts.
3. **Publish:** Upload to PyPI using trusted publishing (OIDC).
4. **Release:** Create GitHub Release with changelog excerpt.

### Documentation Deployment (`docs.yml`)

Triggered by a push to `main`:

1. **Build:** (Future) Build MkDocs/Sphinx site.
2. **Deploy:** Deploy to GitHub Pages.

For v1, documentation is Markdown in `docs/` and is browsable on
GitHub directly. A documentation site is a future enhancement.

### Nightly Benchmarks (`nightly.yml`)

Triggered nightly:

1. **Generate:** Generate benchmark projects (10–5000 files).
2. **Benchmark:** Run `scripts/benchmark.py` against generated
   projects.
3. **Compare:** Compare results against previous night.
4. **Alert:** Open an issue if performance regresses by > 10%.

### Trusted Publishing

PyPI publishing uses **trusted publishing (OIDC)** — no API
tokens stored in GitHub secrets. The GitHub Actions workflow
authenticates to PyPI using OIDC identity. This is the
recommended publishing method (PEP 517 + PyPI trusted
publishing).

### Design Validation

**Why parallel CI jobs?** A sequential pipeline would take 10+
minutes for the full test suite. Parallel jobs reduce wall-clock
time to 2–3 minutes, improving developer experience.

**Why trusted publishing over API tokens?** API tokens are
secrets that must be rotated and can be leaked. Trusted
publishing uses OIDC identity — no secrets, no rotation, no
leakage risk.

**Why nightly benchmarks?** Performance regressions can be
introduced gradually (a small slowdown in each PR). Nightly
benchmarks catch trends that individual PR checks miss.

**Alternatives considered:**

- *Sequential CI:* Rejected — too slow for developer experience.
- *API token publishing:* Rejected — security risk.
- *No nightly benchmarks:* Rejected — performance regressions
  would go unnoticed.

**Trade-offs:** Parallel CI jobs require more CI runners
(increased cost). Acceptable for an open-source project with
GitHub-hosted runners.

**Long-term impact:** The CI/CD setup scales to additional jobs
(coverage reporting, mutation testing, fuzzing) by adding
parallel jobs.

---

## 13. Release Process

### Semantic Versioning

behave-lint follows **Semantic Versioning 2.0.0**:

- **Major (x.0.0):** Breaking changes to the public API. Rule
  behavior changes that alter diagnostics for existing inputs.
  Removal of deprecated features.
- **Minor (0.y.0):** New rules, new reporters, new configuration
  options, new CLI flags. All backward compatible.
- **Patch (0.0.z):** Bug fixes, performance improvements,
  documentation updates. No new features.

### Branching Strategy

- **`main`:** The stable, always-releasable branch. All PRs
  merge into `main`.
- **Feature branches:** `feature/<name>` — short-lived, merged
  via PR.
- **Bug fix branches:** `fix/<issue-number>` — short-lived,
  merged via PR.
- **Release branches:** `release/v<x.y.z>` — created from `main`
  for release stabilization. Only bug fixes are cherry-picked.

No `develop` branch — `main` is always releasable (trunk-based
development).

### Release Candidates

For minor and major releases:

1. Create `release/v<x.y.z>` branch from `main`.
2. Publish a release candidate: `v<x.y.z-rc1>` to PyPI as a
   pre-release.
3. Test the RC in CI and manually.
4. If issues are found, fix on the release branch and publish
   `rc2`.
5. When stable, tag `v<x.y.z>` and publish the final release.

Patch releases do not require RCs — they are bug fixes that go
directly from `main` to release.

### Stable Releases

1. Tag `v<x.y.z>` on the release branch (or `main` for patches).
2. The `release.yml` workflow triggers automatically.
3. Build, test, publish to PyPI, create GitHub Release.
4. Update `CHANGELOG.md` with the release entries.
5. Announce the release (GitHub Release, blog post, social
   media).

### Hotfixes

1. Create `fix/v<x.y.z+1>` branch from the release tag.
2. Apply the fix.
3. Tag `v<x.y.z+1>`.
4. Publish as a patch release.
5. Cherry-pick the fix to `main`.

### Support Policy

- **Latest major version:** Fully supported (bug fixes, new
  features).
- **Previous major version:** Security fixes only, for 6 months
  after the next major release.
- **Older major versions:** No support. Users must upgrade.

### Design Validation

**Why trunk-based development over GitFlow?** Trunk-based
development is simpler, encourages small PRs, and keeps `main`
always releasable. GitFlow's `develop` branch adds complexity
without benefit for a single-package project.

**Why release candidates for minor/major but not patch?** RCs
add time to the release process. Patch releases are low-risk
(bug fixes only) and do not need RCs. Minor and major releases
introduce new behavior that benefits from community testing.

**Why 6-month support for previous major?** Gives users time to
migrate without indefinite maintenance burden. Matches the
support policy of modern Python tools (Ruff, Pytest).

**Alternatives considered:**

- *GitFlow:* Rejected — adds complexity, `develop` branch is
  unnecessary for a single-package project.
- *No RCs:* Rejected — community testing catches issues that CI
  cannot.
- *Indefinite support:* Rejected — unsustainable for a small
  maintainer team.

**Trade-offs:** Trunk-based development requires discipline
(small PRs, continuous integration). This is already the
contribution model.

**Long-term impact:** The release process scales to a larger
maintainer team and supports future enterprise LTS releases.

---

## 14. Future Evolution

### Short-Term (v1.1–v1.x)

- **Plugin SDK:** A separate `behave-lint-sdk` package with base
  classes, utilities, and testing helpers for plugin authors.
  This package would live in the same repository (monorepo) or a
  separate repository, depending on packaging requirements.
- **Additional reporters:** HTML reporter, JUnit XML reporter.
  Each reporter is a new file in `src/behave_lint/reporters/`.
- **Additional rules:** New rules added per category in
  `src/behave_lint/rules/<category>/`.
- **MkDocs documentation site:** User-facing documentation
  generated from Markdown files in `docs/`.
- **Cookiecutter template:** `behave-lint-plugin-template`
  repository for scaffolding new plugins.

### Medium-Term (v2.0–v3.x)

- **LSP server:** A separate `behave-lint-lsp` package providing
  Language Server Protocol support. This would be a new
  subpackage or separate package that depends on the application
  layer.
- **Auto-fix:** The `autofix/` subpackage is populated with the
  Auto-Fix Coordinator (C18). New files in
  `src/behave_lint/autofix/`.
- **Watch mode:** Long-running process that re-lints on file
  change. Implemented in `cli/` as a new command.
- **Distributed analysis:** Remote cache and distributed
  execution. New infrastructure in `infrastructure/`.
- **Monorepo split:** If the plugin SDK or LSP server becomes a
  separate package, the repository may transition to a monorepo
  using a workspace tool (e.g., `uv` workspaces).

### Long-Term (v4.0–v5+)

- **Rule marketplace:** A web platform for discovering and
  installing community rules. The repository structure supports
  this — marketplace rules are standard Python packages
  discovered via entry points.
- **AI rule engine:** AI-assisted rule creation and anomaly
  detection. New subpackage `src/behave_lint/ai/` (or separate
  package).
- **Cloud execution:** Cloud-based linting service. The thin
  application layer (ARCHITECTURE.md Section 12) supports this —
  the application layer can be invoked from a cloud function.
- **Enterprise features:** Configuration profiles, policy
  enforcement, reporting dashboards. New subpackages as needed.

### Repository Evolution

| Evolution | Impact on repository | When |
|---|---|---|
| Plugin SDK | New subpackage or separate package | v1.1+ |
| LSP server | New subpackage or separate package | v2.0+ |
| Auto-fix | Populate existing `autofix/` subpackage | v2.0+ |
| MkDocs site | New `mkdocs.yml` + `docs/` restructure | v1.1+ |
| Monorepo | Repository restructure (workspace tooling) | v3.0+ if needed |
| AI engine | New `ai/` subpackage | v4.0+ |

### Design Validation

**Why design future evolution now?** The repository structure
must accommodate years of growth. Designing extension points
(new subpackages, new test directories, new CI jobs) is cheap;
restructuring the repository is expensive.

**Why not split into a monorepo now?** A monorepo adds tooling
complexity (workspace management, cross-package testing,
dependency resolution) that is unnecessary for a single-package
project. The current structure supports future splitting by
keeping subpackages independent.

**Alternatives considered:**

- *YAGNI (no future design):* Rejected — the repository must
  support 10+ years of evolution (VISION.md Section 16).
- *Monorepo from the start:* Rejected — premature. Split when
  there is a clear need (separate package with different release
  cadence).

**Trade-offs:** Designing for evolution adds some complexity
(reserved subpackages, future directories). This is acceptable
because the complexity is bounded and the benefit (years of
maintainable evolution) is significant.

**Long-term impact:** The repository structure ensures that
behave-lint can grow from a v1 linter to a v5+ platform (LSP,
cloud, AI, marketplace) without fundamental restructuring.

---

## Appendix A: Consistency Check

The following consistency checks were performed against VISION.md,
SPECIFICATION.md, ARCHITECTURE.md, API.md, RULE_ENGINE.md,
DIAGNOSTIC_ENGINE.md, CONFIGURATION_SYSTEM.md, and
COMPONENT_DESIGN.md:

1. **Architectural layers:** REPOSITORY_DESIGN.md defines
   subpackages matching the 5 layers in ARCHITECTURE.md Section 4
   (Presentation, Application, Domain, Infrastructure, Utilities).
   **Consistent.**

2. **Component mapping:** REPOSITORY_DESIGN.md maps all 20
   components from COMPONENT_DESIGN.md Section 2 to subpackages.
   **Consistent.**

3. **Public API:** REPOSITORY_DESIGN.md defines public modules
   matching API.md Section 3 (`behave_lint`, `behave_lint.rules`,
   `behave_lint.reporters`, `behave_lint.errors`, `behave_lint.config`).
   **Consistent.**

4. **Dependency strategy:** REPOSITORY_DESIGN.md Section 11
   matches ARCHITECTURE.md Section 17 (minimal dependencies,
   `behave-model` as only runtime dependency, Python >=3.11).
   **Consistent.**

5. **Testing architecture:** REPOSITORY_DESIGN.md Section 7
   matches ARCHITECTURE.md Section 18 (unit, integration, golden,
   snapshot, performance, regression, architecture tests).
   **Consistent.**

6. **Configuration:** REPOSITORY_DESIGN.md references
   `pyproject.toml` as the configuration file, matching
   CONFIGURATION_SYSTEM.md Section 2 and SPECIFICATION.md
   Appendix B. **Consistent.**

7. **Rule IDs:** REPOSITORY_DESIGN.md Section 5 references the
   rule ID convention from SPECIFICATION.md Appendix A.
   **Consistent.**

8. **Plugin system:** REPOSITORY_DESIGN.md references entry
   point groups (`behave_lint.rules`, `behave_lint.reporters`,
   `behave_lint.config`) matching ARCHITECTURE.md Section 13.
   **Consistent.**

9. **Build system:** REPOSITORY_DESIGN.md Section 6 specifies
   hatchling, matching ARCHITECTURE.md Section 17.
   **Consistent.**

10. **Error handling:** REPOSITORY_DESIGN.md places the Error
    Handler (C20) in the `engine` subpackage, matching
    COMPONENT_DESIGN.md. **Consistent.**

11. **PLUGIN_SYSTEM.md:** Listed as an immutable document in the
    task specification but does not exist in the repository at
    the time of writing. **Note: Not found.** The plugin system
    design is covered in ARCHITECTURE.md Section 13 and
    COMPONENT_DESIGN.md C09. This does not contradict any
    existing document but should be resolved when
    PLUGIN_SYSTEM.md is created.

---

## Appendix B: Glossary

| Term | Definition |
|---|---|
| **src-layout** | A Python package layout where the package source is in `src/` rather than at the repository root. |
| **Trunk-based development** | A branching strategy where all developers merge to `main` (trunk) frequently. |
| **Trusted publishing** | PyPI publishing using OIDC identity instead of API tokens. |
| **Hatchling** | A PEP 517/518 build backend for Python packages. |
| **Entry point** | A Python packaging mechanism for declaring discoverable plugins. |
| **Architecture test** | A test that verifies architectural rules (import direction, layer separation). |
| **Golden test** | A test that compares output against a known-good expected output. |
| **Snapshot test** | A test that compares diagnostics against a stored snapshot. |
| **CODEOWNERS** | A GitHub file that maps directories to team members responsible for review. |
