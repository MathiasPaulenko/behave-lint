# SPECIFICATION.md — behave-lint

> The functional specification for the definitive linting solution for the
> Behave BDD ecosystem.

**Version:** 1.0.0-draft
**Status:** Contractual definition — all future implementation must comply.
**Date:** 2026-07-02

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Product Vision](#2-product-vision)
3. [Product Scope](#3-product-scope)
4. [Target Users](#4-target-users)
5. [User Personas](#5-user-personas)
6. [Use Cases](#6-use-cases)
7. [Functional Requirements](#7-functional-requirements)
8. [Rule System](#8-rule-system)
9. [Configuration](#9-configuration)
10. [CLI Experience](#10-cli-experience)
11. [Diagnostics](#11-diagnostics)
12. [Output Formats](#12-output-formats)
13. [Performance Requirements](#13-performance-requirements)
14. [Reliability](#14-reliability)
15. [Extensibility](#15-extensibility)
16. [Integration](#16-integration)
17. [Documentation](#17-documentation)
18. [Error Handling](#18-error-handling)
19. [Accessibility](#19-accessibility)
20. [Internationalization](#20-internationalization)
21. [Security](#21-security)
22. [Non-Functional Requirements](#22-non-functional-requirements)
23. [Success Metrics](#23-success-metrics)
24. [Risks](#24-risks)
25. [Future Roadmap](#25-future-roadmap)

---

## 1. Executive Summary

### What is behave-lint?

behave-lint is a static analysis tool for Gherkin `.feature` files and
Behave test suites. It detects structural, semantic, and stylistic issues
in BDD specifications without executing any tests. It consumes the
canonical domain model produced by `behave-model` and produces structured
diagnostics suitable for human review, CI/CD gating, and machine-readable
reporting.

### Why does it exist?

The Behave ecosystem has a canonical domain model (`behave-model`), an
opinionated formatter (`behave-format`), and a suite of modern report
libraries (JSON, HTML, Markdown, Console). It lacks a dedicated linter.
Teams currently rely on ad-hoc scripts, manual code review, or simply
tolerate inconsistent feature files. This leads to quality drift,
maintainability problems, and onboarding friction.

behave-lint fills this gap by providing a purpose-built linter with a
comprehensive rule set, configurable severity, plugin support, and
CI-native output formats.

### Which problems does it solve?

- **Inconsistent feature files across teams** — without enforcement,
  naming conventions, tag usage, and step phrasing diverge over time.
- **Gherkin anti-patterns go undetected** — empty scenarios, duplicate
  names, missing backgrounds, overly long scenarios, vague steps, unused
  tags, and orphaned examples are easy to introduce and hard to catch in
  review.
- **No quality gate for CI/CD** — teams using Behave in CI lack a
  quality gate for their specifications. Tests may pass, but the
  specifications themselves may be malformed or incomplete.
- **Custom rules require forking** — when teams need domain-specific
  rules, they write one-off scripts that are not reusable or maintained.
- **Step definitions drift from feature files** — unused step definitions
  and undefined steps accumulate over time.

### Why should the community adopt it?

- **Zero configuration to start** — sensible defaults work immediately.
- **Ecosystem-native** — built on `behave-model`, integrates with
  `behave-format` and all report libraries.
- **Fast** — sub-second on typical projects, suitable for pre-commit and
  IDE integration.
- **Extensible** — custom rules are simple to write and distribute as
  plugins.
- **CI-friendly** — exit codes, JSON, SARIF, GitHub Actions integration.
- **Open source** — MIT-licensed, community-driven, transparent
  governance.

**Rationale:** The Behave ecosystem has matured to the point where a
dedicated linter is the natural next step. The domain model exists, the
formatter exists, the reports exist. The missing piece is quality
enforcement. behave-lint completes the toolchain.

**Constraints:** behave-lint MUST use `behave-model` as its single source
of truth. It MUST NEVER parse `.feature` files directly. It MUST NOT
execute tests. It MUST NOT modify files (auto-fix is a future goal, not a
v1 feature).

**Future considerations:** Auto-fix, SARIF output, LSP support, IDE
integration, AI-assisted recommendations, and a rule marketplace are
envisioned in later phases but are out of scope for the initial
specification.

---

## 2. Product Vision

### One Year

Within one year of the initial release, behave-lint should be:

- The default linter for any professional Behave project.
- Installed via `pip install behave-lint` with zero configuration.
- Running in CI pipelines across hundreds of projects.
- Providing 15-25 high-value built-in rules covering the most common
  Gherkin quality issues.
- Supporting plugins via Python entry points.
- Producing console, JSON, and GitHub Actions output.
- Integrated with pre-commit hooks.

### Three Years

Within three years, behave-lint should be:

- The canonical linter for the Behave ecosystem, with no credible
  alternative.
- Supporting SARIF output and GitHub Code Scanning integration.
- Providing an LSP implementation for real-time IDE feedback.
- Supporting auto-fix for safe, non-semantic-changing rules.
- Featuring a plugin ecosystem with community-published rule packages.
- Integrated with VS Code, PyCharm, and other major IDEs.
- Providing incremental caching for sub-100ms re-linting of changed
  files.
- Referenced in Behave's official documentation as the recommended
  linter.

### Five Years

Within five years, behave-lint should be:

- The standard quality tool for Gherkin across the Python BDD community.
- Supporting AI-assisted recommendations for step phrasing, tag
  suggestions, and scenario structure.
- Featuring a rule marketplace with curated, domain-specific rule
  packages (API testing, UI testing, mobile testing, etc.).
- Providing a declarative rule definition system for non-developers.
- Integrated with the broader BDD tooling ecosystem beyond Behave
  (Cucumber, SpecFlow) through shared rule definitions.
- Recognized as a model for domain-specific linting in the Python
  community.

**Rationale:** A phased vision prevents scope creep and ensures each
release delivers tangible value. The one-year goal is a functional,
useful linter. The three-year goal is ecosystem dominance and IDE
integration. The five-year goal is platform status and AI augmentation.

**Constraints:** The vision is bounded by the Behave ecosystem's health.
If Behave itself becomes inactive, the vision must adapt. The vision
assumes `behave-model` remains actively maintained.

**Future considerations:** The vision may expand to support other Gherkin
runners (Cucumber, SpecFlow) if the domain model abstraction proves
sufficient. This is explicitly out of scope for the initial phases.

---

## 3. Product Scope

### Included

- Static analysis of `.feature` files via `behave-model`'s parsed
  `Project` tree.
- A comprehensive set of built-in rules covering structural, semantic,
  and stylistic issues.
- Per-rule severity configuration (error, warning, info, off).
- Rule categories for selective enabling/disabling.
- CLI tool with multiple output formats (console, JSON, Markdown,
  GitHub Actions).
- `pyproject.toml` configuration with sensible defaults.
- Plugin system for custom rules via Python entry points.
- Pre-commit hook support.
- CI/CD integration (exit codes, structured output).
- Cross-file analysis (duplicate steps across features, step definition
  drift).
- Rule documentation generation.
- Inline disable/enable comments in `.feature` files.
- Caching for incremental runs.

### Not Included

- Parsing `.feature` files directly (delegated to `behave-model`).
- Formatting `.feature` files (delegated to `behave-format`).
- Executing tests (behave-lint is a static analysis tool).
- Generating visual reports (delegated to report libraries).
- Modifying files (auto-fix is a future goal, not v1).
- Security scanning (Gherkin files are specifications, not executable
  code).
- Python code linting (delegated to Ruff, mypy, etc.).
- General-purpose Gherkin linting for non-Behave runners (initially
  Behave-specific).
- AI-powered features (future phase).

### Future Possibilities

- Auto-fix for safe, non-semantic-changing rules.
- SARIF output for GitHub Code Scanning.
- LSP implementation for IDE integration.
- VS Code and PyCharm extensions.
- AI-assisted step recommendations and scenario optimization.
- Rule marketplace with community-published packages.
- Declarative rule definition (YAML/TOML-based rules for simple patterns).
- Quality trend tracking across commits.
- Integration with `behave-modern-json-report` for unified quality
  dashboards.
- Cross-runner support (Cucumber, SpecFlow) via shared rule definitions.

**Rationale:** The scope is deliberately narrow for v1 — detect issues,
report them, do not fix them. This ensures the tool is reliable, fast,
and trustworthy. Auto-fix, IDE integration, and AI features are
significant undertakings that require a stable foundation first.

**Constraints:** The scope is bounded by the `behave-model` API surface.
If `behave-model` does not expose certain information (e.g., step
definition source locations), behave-lint cannot analyze it without
duplicating parsing logic, which violates the core constraint.

**Future considerations:** As `behave-model` evolves, the scope may
expand to cover new Gherkin features or Behave capabilities. The
specification is designed to accommodate growth without breaking
changes.

---

## 4. Target Users

### Open Source Developers

Developers contributing to Behave-related projects who need to maintain
feature file quality across community contributions. They need a linter
that is easy for contributors to run locally, provides clear guidance in
PR reviews, and can be distributed as a plugin.

### QA Engineers

QA professionals maintaining large suites of `.feature` files who need
to enforce naming conventions, tag taxonomies, and step reuse patterns.
They need CI integration, configurable rules, and clear reporting.

### Automation Engineers

Engineers building and maintaining automated test suites who need to
detect anti-patterns, step definition drift, and structural issues before
they cause maintenance problems. They need fast, reliable, automated
feedback.

### Tech Leads

Technical leads who want to enforce organizational standards across BDD
projects. They need configurable rules, shareable presets, and quality
metrics for their teams.

### Software Architects

Architects designing BDD strategies who need to ensure specifications
are well-structured, maintainable, and aligned with business objectives.
They need cross-file analysis, trend tracking, and integration with
broader quality dashboards.

### CI/CD Engineers

DevOps professionals managing CI pipelines who need machine-readable
output, deterministic behavior, clear exit codes, and integration with
GitHub Actions, GitLab CI, Azure DevOps, and Jenkins.

### Consultants

BDD consultants working with multiple organizations who need to express
each client's unique conventions as rules. They need a custom rule SDK,
per-project configuration, and easy onboarding for new teams.

### Large Enterprises

Enterprise teams with hundreds of feature files, multiple repositories,
and strict quality requirements. They need performance at scale,
caching, parallel execution, and integration with enterprise CI/CD
platforms.

**Rationale:** The target users span from individual contributors to
enterprise teams. The tool must be approachable for a single developer
running it locally, yet powerful enough for enterprise CI pipelines.

**Constraints:** The tool cannot assume any particular CI provider,
editor, or project structure. It must work in diverse environments with
minimal configuration.

**Future considerations:** Enterprise features (quality trend tracking,
team dashboards, centralized configuration) may require integration with
external platforms. These are future phase items.

---

## 5. User Personas

### Persona 1: Marta — QA Automation Lead

**Role:** QA Automation Lead at a mid-size SaaS company.
**Team:** 8 QA engineers, 15 repositories, 2,000+ scenarios.

**Goals:**
- Enforce consistent naming conventions across all repositories.
- Maintain a tag taxonomy (e.g., `@smoke`, `@regression`, `@api`).
- Detect duplicate steps and scenarios before they cause maintenance
  issues.
- Gate CI on quality — no merge if lint fails.

**Frustrations:**
- Feature files are inconsistent across teams.
- Duplicate scenarios accumulate silently.
- Tag usage is chaotic — some teams use `@smoke`, others use `@SMOKE`.
- No automated way to enforce conventions; relies on manual review.

**Typical workflow:**
1. Configures `behave-lint` in `pyproject.toml` with team conventions.
2. Adds `behave-lint` to CI pipeline as a quality gate.
3. Reviews lint output in GitHub Actions summaries.
4. Iterates on rules as the team adopts the tool.
5. Writes custom rules for domain-specific conventions.

**Expected benefits:**
- Consistent feature files across all repositories.
- Reduced manual review burden.
- Clear, actionable feedback for team members.
- Measurable quality improvement over time.

### Persona 2: David — Backend Developer

**Role:** Backend developer at a startup, writes features alongside code.
**Team:** 5 developers, 1 repository, 200 scenarios.

**Goals:**
- Get instant feedback when writing a malformed scenario.
- Avoid vague steps and missing tags.
- Keep feature files clean without reading documentation.

**Frustrations:**
- Does not know Gherkin best practices.
- Steps are sometimes vague or redundant.
- No feedback until code review.

**Typical workflow:**
1. Installs `behave-lint` via `pip install behave-lint`.
2. Runs `behave-lint features/` before committing.
3. Reads the diagnostics, fixes issues.
4. Eventually adds `behave-lint` to pre-commit hook.

**Expected benefits:**
- Learns Gherkin best practices through diagnostic messages.
- Catches mistakes before code review.
- No configuration needed — defaults work.

### Persona 3: Priya — DevOps Engineer

**Role:** DevOps engineer managing CI/CD for 30+ projects.
**Team:** Platform team, 30+ repositories using Behave.

**Goals:**
- Add a quality gate to all Behave projects in CI.
- Get machine-readable output for dashboards.
- Fail builds on quality issues with clear exit codes.
- Run linting in parallel with tests.

**Frustrations:**
- No standard quality tool for Behave projects.
- Ad-hoc scripts are inconsistent across projects.
- No structured output for dashboards.

**Typical workflow:**
1. Creates a reusable CI template with `behave-lint`.
2. Configures JSON output for dashboard ingestion.
3. Sets exit code thresholds (fail on errors, warn on warnings).
4. Monitors lint trends across projects.

**Expected benefits:**
- Standardized quality gate across all projects.
- Machine-readable output for dashboards.
- Fast execution that does not slow down CI.

### Persona 4: Kenji — Open Source Maintainer

**Role:** Maintainer of a Behave-related open source project.
**Team:** Solo maintainer, community contributors.

**Goals:**
- Enforce project conventions on community-contributed feature files.
- Make it easy for contributors to run the linter locally.
- Provide clear guidance in PR reviews.
- Ship custom rules as a plugin.

**Frustrations:**
- Contributors submit inconsistent feature files.
- Manual review is time-consuming.
- No way to distribute project-specific rules.

**Typical workflow:**
1. Configures `behave-lint` with project conventions.
2. Adds pre-commit hook for contributors.
3. Publishes custom rules as a plugin package.
4. Contributors install the plugin automatically.

**Expected benefits:**
- Consistent contributions.
- Reduced review burden.
- Distributable custom rules.

### Persona 5: Elena — BDD Consultant

**Role:** Independent BDD consultant working with multiple clients.
**Team:** Works with 5-10 organizations per year.

**Goals:**
- Express each client's unique conventions as rules.
- Onboard new teams quickly with sensible presets.
- Document conventions as living, executable specifications.
- Demonstrate value through measurable quality improvements.

**Frustrations:**
- Each client has different conventions.
- Custom rules are hard to write and distribute.
- No standard tool to recommend.

**Typical workflow:**
1. Assesses client's current feature file quality.
2. Configures `behave-lint` with client-specific rules.
3. Writes custom rules for domain-specific conventions.
4. Trains the team on using the linter.
5. Monitors quality improvement over time.

**Expected benefits:**
- Rapid onboarding of new clients.
- Distributable custom rule packages.
- Measurable quality improvements.

**Rationale:** Personas are drawn from real-world roles in the Behave
ecosystem. They represent different team sizes, technical depths, and
use cases. Each persona's needs inform specific functional requirements.

**Constraints:** The tool cannot optimize for one persona at the expense
of others. The default experience must serve David (zero-config), while
the configuration depth must serve Marta and Elena.

**Future considerations:** As the tool evolves, personas may shift. IDE
integration will attract more individual developers. The rule
marketplace will attract more consultants and open source maintainers.

---

## 6. Use Cases

### UC-1: Running Locally (Developer Workflow)

A developer runs `behave-lint` on their local machine before committing.
They expect fast execution, clear output, and actionable diagnostics.
They may not have any configuration — the defaults must work.

**Flow:** Developer runs `behave-lint features/` → tool loads project
via `behave-model` → runs all enabled rules → prints diagnostics to
console → exits with code 0 (no issues) or 1 (issues found).

### UC-2: CI/CD Pipeline (Quality Gate)

A CI pipeline runs `behave-lint` on every push and PR. The tool must
produce deterministic output, clear exit codes, and optionally
machine-readable output (JSON, SARIF) for dashboards and PR comments.

**Flow:** CI runs `behave-lint --json --output lint-results.json
features/` → tool produces JSON diagnostics → CI parses JSON → fails
build if errors found → optionally posts PR comment with diagnostics.

### UC-3: Pre-commit Hook

A developer configures `behave-lint` as a pre-commit hook. The tool runs
on staged `.feature` files before each commit. It must be fast (sub-second)
and only lint changed files when possible.

**Flow:** Developer stages files → pre-commit runs `behave-lint` on
staged `.feature` files → if issues found, commit is blocked → developer
fixes issues → commits again.

### UC-4: Pull Request Review

A PR triggers `behave-lint` in CI. The diagnostics are posted as a PR
comment or inline review comments. Reviewers can see quality issues
without running the tool locally.

**Flow:** PR opened → CI runs `behave-lint` → diagnostics posted as PR
comment → reviewer sees issues → developer fixes → CI re-runs →
diagnostics updated.

### UC-5: Code Review Education

A developer receives lint diagnostics and learns Gherkin best practices
from the messages. Each diagnostic includes a clear explanation and a
documentation reference.

**Flow:** Developer runs `behave-lint` → reads diagnostics → follows
documentation reference → learns the rule's rationale → applies the fix
→ understands the pattern for future.

### UC-6: BDD Coaching

A BDD consultant uses `behave-lint` to assess a team's current
specification quality, identify common anti-patterns, and configure
custom rules for the team's conventions.

**Flow:** Consultant runs `behave-lint --statistics features/` → reviews
summary of issues by category and frequency → identifies top issues →
configures rules to enforce conventions → trains team on the tool.

### UC-7: Enterprise Quality Gates

An enterprise configures `behave-lint` across multiple repositories with
centralized configuration. Quality metrics are aggregated into a
dashboard. Builds fail on quality threshold breaches.

**Flow:** Enterprise configures shared `pyproject.toml` base → each
repository extends or overrides → CI runs `behave-lint` → JSON output
sent to aggregation dashboard → quality trends tracked over time.

### UC-8: Custom Rule Development

A developer writes a custom rule for a domain-specific convention (e.g.,
"all `@smoke` scenarios must have fewer than 5 steps"). They package it
as a plugin and distribute it via PyPI.

**Flow:** Developer reads custom rule SDK docs → writes rule → tests it
with fixture files → packages as pip-installable plugin → publishes to
PyPI → teams install and configure.

### UC-9: Migration from Ad-hoc Scripts

A team has existing custom validation scripts. They want to migrate to
`behave-lint` without losing their custom checks. They rewrite their
checks as `behave-lint` rules or plugins.

**Flow:** Team reviews existing scripts → maps each check to a
`behave-lint` rule (built-in or custom) → configures `behave-lint` →
removes ad-hoc scripts → validates parity.

### UC-10: Large Repository Performance

A monorepo with 5,000+ feature files needs linting. The tool must handle
this scale without excessive memory usage or execution time. Caching and
incremental analysis are essential.

**Flow:** First run lints all files → cache is built → subsequent runs
only re-lint changed files → results are merged with cached results →
full diagnostics produced.

**Rationale:** Use cases are derived from the personas and target users.
Each use case maps to specific functional requirements. The tool must
serve all use cases without requiring different configurations or modes.

**Constraints:** Pre-commit and IDE use cases demand sub-second
performance. CI use cases demand deterministic output and structured
formats. Enterprise use cases demand scalability and caching.

**Future considerations:** IDE integration (LSP) will add a real-time
use case. Auto-fix will add a `--fix` use case. The rule marketplace
will add a rule discovery and installation use case.

---

## 7. Functional Requirements

### FR-1: Project Loading

**Purpose:** Load a Behave project from the filesystem into the domain
model for analysis.

**Inputs:** One or more paths to directories or `.feature` files.

**Outputs:** An in-memory representation of the project suitable for
rule analysis.

**Expected behaviour:**
- The tool delegates parsing to `behave-model`'s `load_project` or
  `load_feature` functions.
- If a directory is specified, all `.feature` files within it (and
  subdirectories) are loaded.
- If a file is specified, only that file is loaded.
- Multiple paths are supported and merged into a single project view.
- The tool MUST NOT parse `.feature` files directly under any
  circumstances.

**Constraints:** Depends on `behave-model`. Cannot operate without it.
Must handle parse errors gracefully (see Error Handling).

**Dependencies:** `behave-model >= 1.0.0`.

**Priority:** P0 (critical for v1).

**Future extensions:** Support for loading projects from JSON
serializations (via `behave-model`'s `JsonSerializer`) for use cases
where parsing has already been done.

### FR-2: Rule Execution

**Purpose:** Run all enabled rules against the loaded project and
collect diagnostics.

**Inputs:** The loaded project, the set of enabled rules, and the
configuration for each rule.

**Outputs:** A collection of diagnostics, each containing rule ID,
severity, location, message, and optional suggestion.

**Expected behaviour:**
- Rules are executed in a deterministic order (by rule ID, unless
  overridden).
- Each rule receives the project and its own configuration.
- Rules may traverse the project tree, query elements, or perform
  cross-file analysis.
- Rule execution is independent — one rule's failure does not prevent
  other rules from running.
- Rules may be executed in parallel for performance.

**Constraints:** Rule execution must be deterministic. The same project
and configuration must always produce the same diagnostics.

**Dependencies:** `behave-model` (for project tree, visitor pattern,
query API).

**Priority:** P0.

**Future extensions:** Parallel execution, incremental execution (only
re-run rules affected by changed files), rule profiling.

### FR-3: Configuration Loading and Validation

**Purpose:** Load configuration from `pyproject.toml`, validate it, and
provide it to the rule engine.

**Inputs:** `pyproject.toml` file, CLI arguments, environment variables.

**Outputs:** A validated configuration object.

**Expected behaviour:**
- Configuration is loaded from the `[tool.behave-lint]` section of
  `pyproject.toml`.
- CLI arguments override configuration file values.
- Environment variables override CLI arguments (for CI-specific
  overrides).
- Invalid configuration produces a clear error message with the
  location of the problem and guidance for fixing it.
- Unknown configuration keys produce a warning, not an error.

**Constraints:** Configuration must be deterministic and reproducible.
The same configuration file and CLI arguments must always produce the
same effective configuration.

**Dependencies:** None beyond the standard library.

**Priority:** P0.

**Future extensions:** Configuration schema versioning, configuration
validation against a JSON schema, shared configuration presets.

### FR-4: Diagnostic Filtering and Sorting

**Purpose:** Filter, sort, and organize diagnostics for output.

**Inputs:** Raw diagnostics from rule execution, output format
preferences.

**Outputs:** Filtered and sorted diagnostics ready for rendering.

**Expected behaviour:**
- Diagnostics are sorted by file path, then by line number, then by
  rule ID.
- Diagnostics can be filtered by severity (e.g., only errors).
- Diagnostics can be filtered by rule ID (e.g., only specific rules).
- Diagnostics can be filtered by file path (e.g., only specific files).
- Inline disable comments suppress diagnostics for specific rules on
  specific lines.

**Constraints:** Filtering and sorting must be deterministic.

**Dependencies:** None.

**Priority:** P0.

**Future extensions:** Diagnostic grouping by rule, diagnostic
deduplication, diagnostic severity escalation.

### FR-5: Output Generation

**Purpose:** Render diagnostics in the requested output format.

**Inputs:** Filtered diagnostics, output format, output destination.

**Outputs:** Formatted diagnostics written to stdout, a file, or both.

**Expected behaviour:**
- Console output is the default, with color support and readable
  formatting.
- JSON output is structured, stable, and documented.
- Markdown output is suitable for GitHub Actions summaries and PR
  comments.
- GitHub Actions output uses the `::error` and `::warning` syntax for
  inline PR annotations.
- Output can be written to a file via `--output` or to stdout.
- Multiple output formats can be requested simultaneously.

**Constraints:** Each output format must be stable and documented.
Breaking changes to output structure require a major version bump.

**Dependencies:** None beyond the standard library.

**Priority:** P0 (console, JSON), P1 (Markdown, GitHub Actions), P2
(SARIF).

**Future extensions:** HTML output, custom output formats via plugins,
streaming output for large projects.

### FR-6: Exit Codes

**Purpose:** Provide meaningful exit codes for CI/CD integration.

**Inputs:** Diagnostics, severity thresholds.

**Outputs:** Process exit code.

**Expected behaviour:**
- Exit 0: No diagnostics, or only diagnostics below the failure
  threshold.
- Exit 1: Diagnostics at or above the failure severity (default: error).
- Exit 2: Internal error (configuration error, parse error, unexpected
  exception).
- The failure severity is configurable (e.g., fail on warnings).

**Constraints:** Exit codes must be stable and documented.

**Dependencies:** None.

**Priority:** P0.

**Future extensions:** Configurable exit codes per rule, exit code
based on diagnostic count thresholds.

### FR-7: Statistics and Summary

**Purpose:** Provide a summary of linting results for quick assessment.

**Inputs:** Diagnostics, project metadata.

**Outputs:** Summary including: total files linted, total diagnostics by
severity, diagnostics by rule, diagnostics by category, execution time.

**Expected behaviour:**
- Summary is printed to console by default after diagnostics.
- Summary can be output in JSON format.
- Summary includes counts by severity (error, warning, info).
- Summary includes top N most frequent rules.
- Summary includes execution time.

**Constraints:** Summary must be deterministic.

**Dependencies:** None.

**Priority:** P1.

**Future extensions:** Trend tracking (compare with previous run),
quality score, badge generation.

### FR-8: Inline Disable/Enable Comments

**Purpose:** Allow developers to suppress specific diagnostics in
`.feature` files using comments.

**Inputs:** `.feature` files with inline comments.

**Outputs:** Suppressed diagnostics.

**Expected behaviour:**
- Comments of the form `# behave-lint: disable=rule-id` suppress the
  specified rule on the next line.
- Comments of the form `# behave-lint: disable=rule-id` with a
  matching `# behave-lint: enable=rule-id` suppress the rule between
  the two comments.
- Comments of the form `# behave-lint: disable-all` suppress all rules
  on the next line or within a block.
- Suppressed diagnostics are not included in the output unless
  `--show-suppressed` is specified.
- Suppression comments themselves are linted: a suppression for an
  unknown rule ID produces a warning.

**Constraints:** Suppression comments must be in `.feature` file
comments, which are preserved by `behave-model`.

**Dependencies:** `behave-model` (for comment preservation).

**Priority:** P1.

**Future extensions:** Suppression with expiration (e.g., `# behave-lint:
  disable=rule-id until=2026-12-01`), suppression with reason (e.g.,
  `# behave-lint: disable=rule-id reason="temporary workaround"`).

### FR-9: Caching and Incremental Analysis

**Purpose:** Speed up subsequent runs by caching results and only
re-analyzing changed files.

**Inputs:** File modification times, file content hashes, previous
results.

**Outputs:** Cached and fresh diagnostics merged into a complete result
set.

**Expected behaviour:**
- The tool caches analysis results keyed by file content hash and
  configuration hash.
- On subsequent runs, only files that have changed (different content
  hash) are re-analyzed.
- Cross-file rules (e.g., duplicate step detection) are re-run when any
  relevant file changes.
- The cache is stored in a well-known location (e.g.,
  `.behave-lint-cache/` or a user-specified directory).
- The cache can be disabled via `--no-cache`.
- The cache can be cleared via `--clear-cache`.

**Constraints:** Caching must not produce stale results. If the
configuration changes, the cache is invalidated. If `behave-model` is
updated, the cache is invalidated.

**Dependencies:** None beyond the standard library.

**Priority:** P2 (post-v1).

**Future extensions:** Remote caching, cache sharing across CI runs,
cache compression.

### FR-10: Plugin Discovery and Loading

**Purpose:** Discover and load custom rules from installed Python
packages.

**Inputs:** Python entry points for `behave_lint.rules`.

**Outputs:** Additional rules registered in the rule engine.

**Expected behaviour:**
- Plugins are discovered via Python entry points (the standard mechanism
  used by pytest, flake8, etc.).
- Each plugin can register one or more rules.
- Plugin rules are treated identically to built-in rules for
  configuration, execution, and output.
- Plugin metadata (name, version, author) is available for
  documentation and debugging.
- Plugin load failures produce a clear error message but do not crash
  the tool.

**Constraints:** Plugins must be pip-installable. The entry point
interface must be stable across minor versions.

**Dependencies:** Python packaging infrastructure (entry points).

**Priority:** P1.

**Future extensions:** Plugin validation, plugin sandboxing, plugin
dependency resolution, plugin marketplace integration.

### FR-11: Step Definition Analysis

**Purpose:** Cross-reference `.feature` files with Python step
definitions to detect drift.

**Inputs:** Path to step definitions directory (default:
`features/steps/`), loaded project.

**Outputs:** Diagnostics for undefined steps, unused step definitions,
and inconsistent parameter patterns.

**Expected behaviour:**
- The tool scans Python files in the step definitions directory for
  `@given`, `@when`, `@then`, and `@step` decorators.
- Step patterns are extracted and compared against steps used in
  `.feature` files.
- Undefined steps (used in features but not defined in Python) are
  reported.
- Unused step definitions (defined in Python but not used in features)
  are reported.
- This analysis is opt-in (disabled by default) because it requires
  knowledge of the project structure.

**Constraints:** Step definition analysis is heuristic. Step patterns
may use regex or string templates, and matching is not always exact.
False positives are possible and must be clearly communicated.

**Dependencies:** Python AST parsing (standard library).

**Priority:** P1.

**Future extensions:** Step definition similarity detection (fuzzy
matching for near-duplicates), step definition complexity analysis,
step definition coverage metrics.

**Rationale:** Each functional requirement is derived from a use case
or persona need. Requirements are prioritized P0 (must have for v1),
P1 (should have for v1), P2 (nice to have for v1 or future). Every
requirement specifies its purpose, inputs, outputs, expected behaviour,
constraints, dependencies, priority, and future extensions to ensure
unambiguous implementation.

**Constraints:** The specification defines *what* the tool does, not
*how* it does it. Implementation details (classes, packages, algorithms)
are deliberately omitted.

**Future considerations:** As the tool evolves, new functional
requirements will be added through a formal RFC process. Breaking
changes to existing requirements require a major version bump.

---

## 8. Rule System

### Rule IDs

Every rule has a unique, stable identifier. Rule IDs follow the
convention `B<category><number>` (e.g., `B001`, `B002`), where:

- `B` is the prefix for behave-lint rules (distinguishing them from
  plugin rules, which use their own prefix).
- `<category>` is a single letter representing the rule category.
- `<number>` is a zero-padded three-digit number assigned sequentially.

Plugin rules use their own prefix (e.g., `ACME001`) to avoid collisions
with built-in rules.

**Rationale:** Stable, unique IDs are essential for configuration,
inline disable comments, and documentation references. The
`B<category><number>` convention is inspired by Ruff's rule naming
and provides a compact, memorable identifier.

**Constraints:** Rule IDs are immutable once assigned. A rule's ID
cannot change between versions. Deprecated rules retain their ID.

**Future considerations:** A rule registry may be published online for
discoverability and cross-referencing.

### Rule Categories

Rules are organized into categories for selective enabling and
disabling:

| Category | Code | Description |
|----------|------|-------------|
| Correctness | `C` | Rules that detect definitively wrong structures (e.g., invalid tables, duplicate names). |
| Style | `S` | Rules that enforce stylistic conventions (e.g., tag casing, keyword usage). |
| Complexity | `X` | Rules that detect overly complex specifications (e.g., too many steps, too many scenarios). |
| Consistency | `K` | Rules that enforce cross-file consistency (e.g., duplicate steps, tag taxonomy). |
| Pedantic | `P` | Rules that enforce strict best practices (opt-in, not enabled by default). |
| Step Definitions | `D` | Rules that cross-reference feature files with step definitions. |

**Rationale:** Categories allow teams to enable or disable groups of
rules without listing each one individually. This mirrors Clippy's
pedantic groups and Ruff's rule selectors.

**Constraints:** Each rule belongs to exactly one category. The category
is immutable.

**Future considerations:** New categories may be added in future
versions. Custom categories may be supported for plugins.

### Severity

Each rule has a default severity:

| Severity | Description | Exit code impact |
|----------|-------------|------------------|
| `error` | Definitively wrong. Must be fixed. | Exit 1 |
| `warning` | Likely wrong. Should be reviewed. | Exit 0 (default) or 1 (configurable) |
| `info` | Suggestion. Optional. | Exit 0 |
| `off` | Rule is disabled. | No effect |

Severity is configurable per rule. A rule's default severity is part of
its metadata and is documented.

**Rationale:** Severity levels provide flexibility. A team may downgrade
a rule from error to warning during adoption, or upgrade a warning to
error once the team is compliant.

**Constraints:** The default severity for each rule is chosen to
minimize false positives. Correctness rules default to error. Style
rules default to warning. Pedantic rules default to off.

**Future considerations:** Custom severity levels may be supported
(e.g., `critical` for security-adjacent rules).

### Configuration

Rules are configured in `pyproject.toml` under `[tool.behave-lint]`:

- Individual rules can be enabled, disabled, or have their severity
  changed.
- Categories can be enabled or disabled wholesale.
- Rules may accept rule-specific parameters (e.g., max step count for
  complexity rules).
- Configuration is validated at load time.

**Rationale:** Per-rule configuration provides fine-grained control
without requiring a complex configuration schema. The
`pyproject.toml` location follows modern Python tooling conventions.

**Constraints:** Configuration keys must be stable. Adding new
configuration options is a minor version change. Changing existing
options is a major version change.

**Future considerations:** Shareable configuration presets (e.g.,
`extends = "strict"`), configuration inheritance, per-directory
overrides.

### Auto-Fix Capability

Some rules may be auto-fixable in future versions. Each rule's metadata
declares whether it is auto-fixable:

- **Not fixable:** The rule detects an issue that requires human
  judgment (e.g., vague step text).
- **Safe fixable:** The rule can fix the issue without changing
  semantics (e.g., sorting tags, normalizing keyword casing).
- **Unsafe fixable:** The rule can fix the issue but may change
  semantics (e.g., removing unused tags). Requires `--unsafe-fixes`.

Auto-fix is a future feature (Phase 5). The rule metadata is defined now
to ensure rules are designed with auto-fix in mind.

**Rationale:** Declaring auto-fix capability in rule metadata ensures
that the rule system is designed for auto-fix from the start, even
though the feature is implemented later.

**Constraints:** Auto-fix must never change the semantic meaning of a
feature file. Safe fixes are limited to non-semantic changes.

**Future considerations:** Auto-fix integration with `behave-format`
(format after fix), fix preview, selective fixing by rule.

### Documentation

Every rule is self-documenting through its metadata:

- **Name:** Human-readable name.
- **ID:** Stable rule identifier.
- **Category:** Rule category.
- **Default severity:** The default severity level.
- **Description:** What the rule detects.
- **Rationale:** Why the rule exists.
- **Example (before):** A `.feature` snippet that triggers the rule.
- **Example (after):** The corrected `.feature` snippet.
- **Configuration:** Available configuration options.
- **Auto-fix:** Whether the rule is auto-fixable.
- **Since:** Version in which the rule was introduced.
- **Deprecated:** Whether the rule is deprecated, and in which version.

This metadata drives:

- CLI `--explain <rule-id>` output.
- Online documentation generation.
- IDE hover tooltips (future).
- JSON output metadata.

**Rationale:** Self-documenting rules ensure that documentation is
always accurate and available. This is inspired by Ruff's rule
catalog and Clippy's educational messages.

**Constraints:** Rule metadata must be complete at the time of rule
introduction. Incomplete metadata blocks inclusion.

**Future considerations:** Interactive rule explorer (web UI), rule
documentation in multiple languages.

### Rule Lifecycle

Rules progress through a defined lifecycle:

1. **Proposed:** A rule is proposed via an issue or RFC. It is discussed
   and vetted by the community.
2. **Experimental:** The rule is implemented behind an opt-in flag. It
   may produce false positives. It is not included in default
   configurations.
3. **Stable:** The rule has been validated by real-world usage. It is
   included in default configurations (if appropriate). Its behavior is
   frozen — changes require a major version bump.
4. **Deprecated:** The rule is superseded or no longer relevant. It
   remains functional but produces a deprecation warning. It is
   scheduled for removal in the next major version.
5. **Removed:** The rule is removed in a major version. Its ID is
   permanently retired and cannot be reused.

**Rationale:** A formal lifecycle ensures that rules are vetted before
becoming defaults, and that breaking changes are communicated
clearly. This is inspired by Rust's stability model.

**Constraints:** Stable rules cannot have their behavior changed in a
minor version. Deprecated rules must produce a warning. Removed rule
IDs are permanently retired.

**Future considerations:** A rule maturity dashboard showing the
lifecycle stage of each rule.

### Rule Versioning

- Rules are versioned independently of the tool. Each rule has a "since"
  version (when it was introduced).
- Rule behavior changes (not bug fixes) require a new rule ID. The old
  rule is deprecated, and the new rule is introduced with a new ID.
- This allows teams to migrate gradually.

**Rationale:** Independent rule versioning prevents silent behavior
changes. If a rule's behavior changes, teams need to explicitly opt
into the new behavior by enabling the new rule ID.

**Constraints:** Bug fixes (where a rule was not doing what it was
supposed to do) do not require a new rule ID. Behavior changes (where
a rule was doing X and now does Y) do require a new rule ID.

**Future considerations:** Rule changelog generation, rule migration
guides.

### Rule Deprecation

When a rule is deprecated:

- The rule's metadata includes a `deprecated` field with the version
  and a replacement rule ID (if applicable).
- The rule continues to function but produces a deprecation warning in
  the tool's output.
- The rule is removed in the next major version.
- The rule's ID is permanently retired and cannot be reused.

**Rationale:** Deprecation with a grace period allows teams to migrate
without breaking builds. Permanent ID retirement prevents confusion.

**Constraints:** Deprecated rules must remain functional until removal.
Removal only occurs in major versions.

**Future considerations:** Automated migration suggestions (e.g.,
"replace B001 with B002 in your configuration").

### Rule Discoverability

Users can discover rules through:

- `behave-lint --list-rules` — lists all available rules (built-in and
  plugin) with their metadata.
- `behave-lint --explain <rule-id>` — shows detailed documentation for a
  specific rule.
- `behave-lint --list-rules --json` — machine-readable rule catalog.
- Online documentation (generated from rule metadata).
- IDE hover tooltips (future).

**Rationale:** Discoverability is critical for adoption. Users cannot
configure rules they do not know exist.

**Constraints:** The rule list must include all registered rules
(built-in and plugin) and must be deterministic.

**Future considerations:** Rule search (by keyword, category, or
severity), rule recommendations based on project analysis.

### Rule Naming Conventions

Rule names (human-readable) follow these conventions:

- Use imperative mood: "Detect duplicate scenario names" (not "Detects
  duplicate scenario names").
- Be specific: "Detect duplicate scenario names within a feature" (not
  "Check for duplicates").
- Be concise: "Detect duplicate scenario names" (not "Detect scenarios
  that have the same name as another scenario in the same feature").
- Use Gherkin terminology: "scenario" (not "test case"), "step" (not
  "line"), "feature" (not "file").

**Rationale:** Consistent naming improves documentation quality and
searchability.

**Constraints:** Rule names are immutable once a rule is stable.

**Future considerations:** Localized rule names (see
Internationalization).

---

## 9. Configuration

### Configuration Philosophy

behave-lint follows a **minimal configuration** philosophy:

- **Zero configuration works.** The default configuration is sensible
  for the majority of projects. A developer can install the tool and
  run it without any configuration.
- **Configuration is opt-in, not opt-out.** Rules are enabled by
  default only if they have near-zero false positives. Opinionated or
  heuristic rules are disabled by default.
- **Configuration is code.** Configuration lives in `pyproject.toml`,
  is version-controlled, and is reviewed in PRs.
- **Configuration is simple.** A flat key-value structure, no nested
  overrides, no inheritance (initially). Complexity is the enemy of
  adoption.

**Rationale:** Configuration complexity is the primary complaint about
ESLint and golangci-lint. behave-lint avoids this by starting simple
and adding complexity only when justified by real-world demand.

**Constraints:** The configuration schema must be stable within a major
version. New keys can be added in minor versions. Existing keys
cannot change meaning or be removed without a major version.

**Future considerations:** Shareable presets, per-directory overrides,
configuration composition.

### Project Configuration

Configuration is stored in `pyproject.toml` under `[tool.behave-lint]`:

- **Rule selection:** Enable, disable, or set severity for individual
  rules or categories.
- **Rule parameters:** Rule-specific settings (e.g., max step count,
  required tags).
- **Output preferences:** Default output format, color settings.
- **Paths:** Default paths to lint, step definitions directory.
- **Cache:** Cache directory, cache enable/disable.
- **Plugins:** Explicit plugin enable/disable (plugins are auto-
  discovered but can be explicitly disabled).

**Rationale:** `pyproject.toml` is the modern standard for Python tool
configuration. It is already used by Ruff, Black, mypy, pytest, and
`behave-format`.

**Constraints:** Only one `pyproject.toml` is read (the one in the
current directory or the nearest ancestor). No cascading
configuration.

**Future considerations:** Configuration presets (`extends = "strict"`),
configuration validation against a published JSON schema.

### CLI Overrides

CLI arguments override configuration file values:

- `--select <rule-id>` — enable specific rules (overrides config).
- `--ignore <rule-id>` — disable specific rules (overrides config).
- `--severity <rule-id>=<severity>` — change rule severity.
- `--output <format>` — output format (console, json, markdown,
  github-actions).
- `--output-file <path>` — write output to file.
- `--no-cache` — disable caching.
- `--clear-cache` — clear cache before running.
- `--fix` — apply auto-fixes (future).
- `--statistics` — show statistics summary.
- `--list-rules` — list available rules.
- `--explain <rule-id>` — show rule documentation.
- `--config <path>` — path to configuration file (default:
  `pyproject.toml`).
- `--color` / `--no-color` — enable/disable colored output.
- `--quiet` — suppress output except errors.
- `--verbose` — show additional information.

**Rationale:** CLI overrides are essential for one-off runs, debugging,
and CI-specific configurations. They follow the conventions of Ruff
and ESLint.

**Constraints:** CLI overrides do not modify the configuration file.
They are ephemeral.

**Future considerations:** `--preset <name>` for applying a preset from
the command line.

### Environment Variables

Environment variables provide a last-resort override mechanism for CI
environments where CLI arguments are impractical:

- `BEHAVE_LINT_CONFIG` — path to configuration file.
- `BEHAVE_LINT_OUTPUT` — output format.
- `BEHAVE_LINT_OUTPUT_FILE` — output file path.
- `BEHAVE_LINT_NO_CACHE` — disable caching.
- `BEHAVE_LINT_NO_COLOR` — disable colored output.
- `BEHAVE_LINT_SELECT` — comma-separated rule IDs to select.
- `BEHAVE_LINT_IGNORE` — comma-separated rule IDs to ignore.

**Rationale:** Environment variables are useful in CI environments
where modifying the command line is impractical (e.g., shared CI
templates).

**Constraints:** Environment variables have the lowest precedence. They
do not override CLI arguments or configuration file values (unless
the configuration file does not specify a value).

**Future considerations:** `BEHAVE_LINT_PRESET` for applying a preset
via environment variable.

### Default Behaviour

With no configuration and no CLI arguments:

- All stable correctness, style, and consistency rules are enabled with
  their default severities.
- Pedantic rules are disabled.
- Step definition analysis is disabled.
- Output format is console with color.
- Caching is enabled (if implemented).
- Exit code is 1 if any error-severity diagnostics are found.

**Rationale:** The default behavior must be useful immediately. A
developer who installs the tool and runs `behave-lint features/`
should get valuable feedback without reading any documentation.

**Constraints:** The default rule set must have near-zero false
positives. A single false positive in the default set can cause a
team to abandon the tool.

**Future considerations:** The default rule set may expand over time as
rules graduate from experimental to stable.

### Configuration Precedence

Precedence (highest to lowest):

1. CLI arguments.
2. Environment variables.
3. `pyproject.toml` configuration.
4. Built-in defaults.

**Rationale:** Clear precedence prevents confusion. CLI arguments are
the most explicit, so they take precedence. Environment variables are
less explicit but more specific than configuration files. Defaults
are the fallback.

**Constraints:** Precedence is per-key, not global. A CLI argument for
output format does not override a configuration file value for rule
selection.

**Future considerations:** Configuration composition (merging multiple
sources with explicit precedence rules).

### Configuration Validation

Configuration is validated at load time:

- Unknown keys produce a warning (not an error) to allow forward
  compatibility.
- Invalid values (e.g., severity "critical" when only "error",
  "warning", "info", "off" are valid) produce an error with a clear
  message.
- Unknown rule IDs in `select` or `ignore` produce a warning.
- Missing required parameters for rules produce an error.

**Rationale:** Strict validation catches configuration mistakes early.
Warnings for unknown keys allow the tool to be used with newer
configuration without errors on older versions.

**Constraints:** Validation must be fast (no network calls, no file
system access beyond reading the configuration file).

**Future considerations:** JSON schema publication for IDE
autocompletion, configuration migration tool.

### Configuration Error Reporting

When configuration is invalid:

- The tool exits with code 2 (configuration error).
- The error message includes: the configuration file path, the invalid
  key or value, the expected format, and a suggestion for fixing it.
- The error message is printed to stderr.
- No diagnostics are produced (the tool cannot run with invalid
  configuration).

**Rationale:** Clear configuration errors are essential for developer
experience. A cryptic error frustrates users and blocks adoption.

**Constraints:** Error messages must be actionable. They must tell the
user exactly what is wrong and how to fix it.

**Future considerations:** Configuration lint mode (`behave-lint
--config-check`) that validates configuration without running rules.

---

## 10. CLI Experience

### Command Structure

The primary command is `behave-lint`. It accepts paths to lint and
optional flags.

### Basic Usage

```
behave-lint
behave-lint features/
behave-lint features/login.feature
behave-lint features/login.feature features/auth/
behave-lint --json --output lint.json features/
behave-lint --select B001,B002 features/
behave-lint --ignore B003 features/
behave-lint --statistics features/
behave-lint --list-rules
behave-lint --explain B001
behave-lint --fix features/
behave-lint --sarif --output lint.sarif features/
behave-lint --quiet features/
behave-lint --verbose features/
```

### Behaviour

- **No arguments:** Lint the current directory (or `features/` if it
  exists). If neither has `.feature` files, print a message and exit 0.
- **Path arguments:** Lint the specified paths. Directories are
  searched recursively for `.feature` files. Files are linted directly.
- **Multiple paths:** All paths are linted in a single run. Cross-file
  rules see all files together.
- **`--select`:** Only the specified rules are enabled, overriding
  configuration. Other rules are disabled.
- **`--ignore`:** The specified rules are disabled, overriding
  configuration. Other rules retain their configured state.
- **`--output`:** Specifies the output format. Multiple formats can be
  specified by repeating the flag or using comma separation.
- **`--output-file`:** Specifies the file to write output to. If not
  specified, output goes to stdout. Console output always goes to
  stdout.
- **`--fix`:** Apply auto-fixes (future). Only safe fixes are applied
  unless `--unsafe-fixes` is also specified. A diff is shown before
  applying (unless `--quiet`).
- **`--json`:** Shortcut for `--output json`.
- **`--sarif`:** Shortcut for `--output sarif`.
- **`--statistics`:** Print a summary after diagnostics. Includes counts
  by severity, top rules, and execution time.
- **`--list-rules`:** List all available rules and exit. No linting is
  performed.
- **`--explain`:** Show documentation for the specified rule and exit.
  No linting is performed.
- **`--quiet`:** Suppress all output except error-severity diagnostics
  and the final summary.
- **`--verbose`:** Show additional information: loaded configuration,
  rule execution times, cache hits/misses.
- **`--color` / `--no-color`:** Enable or disable colored output.
  Default: enabled when stdout is a terminal, disabled when piped.
- **`--config`:** Path to a configuration file. Default: `pyproject.toml`
  in the current directory or nearest ancestor.
- **`--no-cache`:** Disable caching for this run.
- **`--clear-cache`:** Clear the cache before running.
- **`--version`:** Print version and exit.
- **`--help`:** Print help and exit.

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No diagnostics at or above the failure severity. |
| 1 | Diagnostics at or above the failure severity (default: error). |
| 2 | Internal error (configuration error, parse error, unexpected exception). |

### Help Text

The `--help` output must be:

- Concise but complete.
- Organized by category (paths, rules, output, configuration, other).
- Include examples for common use cases.
- Follow standard Python CLI help conventions (argparse-style).

**Rationale:** The CLI is the primary interface for most users. It must
be intuitive, fast, and well-documented. The design follows
conventions established by Ruff, ESLint, and other popular linters.

**Constraints:** The CLI must work on Windows, macOS, and Linux. Paths
must be handled correctly across platforms.

**Future considerations:** Shell completion (bash, zsh, fish, powershell),
interactive mode, watch mode (`--watch` for continuous linting).

---

## 11. Diagnostics

### Diagnostic Structure

Every diagnostic contains the following fields:

| Field | Required | Description |
|-------|----------|-------------|
| `rule_id` | Yes | The stable identifier of the rule that produced the diagnostic. |
| `severity` | Yes | One of: `error`, `warning`, `info`. |
| `message` | Yes | A human-readable description of the issue. |
| `file_path` | Yes | The path to the `.feature` file containing the issue. |
| `line` | Yes | The 1-based line number where the issue occurs. |
| `column` | Optional | The 1-based column number, if applicable. |
| `end_line` | Optional | The 1-based end line number, for multi-line issues. |
| `end_column` | Optional | The 1-based end column number, for multi-line issues. |
| `suggestion` | Optional | A suggested fix or action, in human-readable form. |
| `doc_url` | Optional | A URL to the rule's documentation. |
| `category` | Yes | The rule's category (correctness, style, etc.). |

**Rationale:** A structured diagnostic is essential for machine-readable
output (JSON, SARIF) and for IDE integration. Every field has a clear
purpose. Optional fields are optional because not all issues have a
precise column or a suggestion.

**Constraints:** The diagnostic structure must be stable. Adding fields
is a minor version change. Removing or renaming fields is a major
version change.

**Future considerations:** `fix` field containing a machine-readable
fix description (for auto-fix), `related` field containing related
diagnostics, `source` field containing the source line text.

### Diagnostic Presentation

#### Console Output

Diagnostics are presented in the console in a readable, scannable
format:

```
features/login.feature:12:1  B001  error  Duplicate scenario name 'Login'
features/login.feature:25:3  B005  warning  Scenario has more than 10 steps (12)
features/auth.feature:3:1    B010  info  Tag '@wip' is deprecated

Found 3 diagnostics (1 error, 1 warning, 1 info) in 2 files in 0.12s
```

- **Location** is shown first (file:line:column) for quick navigation.
- **Rule ID** is shown next for quick identification.
- **Severity** is shown as a label (error, warning, info) with color
  support.
- **Message** is shown last, in natural language.
- A **summary line** is printed at the end with counts and timing.

#### JSON Output

JSON output is structured as a stable, documented schema:

- Top-level object with `schemaVersion`, `diagnostics` array, and
  `summary` object.
- Each diagnostic is an object with the fields defined above.
- The schema is versioned independently of the tool.

#### Markdown Output

Markdown output is suitable for GitHub Actions summaries and PR
comments:

- A summary table with counts by severity.
- A table of diagnostics with columns: file, line, rule, severity,
  message.
- Collapsible sections for long diagnostic lists.

#### GitHub Actions Output

GitHub Actions output uses the `::error` and `::warning` syntax for
inline PR annotations:

```
::error file=features/login.feature,line=12,col=1::B001: Duplicate scenario name 'Login'
::warning file=features/login.feature,line=25,col=3::B005: Scenario has more than 10 steps (12)
```

#### SARIF Output (Future)

SARIF (Static Analysis Results Interchange Format) output for GitHub
Code Scanning integration. SARIF is a JSON-based standard for
representing static analysis results.

**Rationale:** Different output formats serve different consumers.
Console is for developers. JSON is for machines and dashboards.
Markdown is for PR comments. GitHub Actions is for inline annotations.
SARIF is for security scanning integration.

**Constraints:** Each format must be deterministic and stable. The same
diagnostics must always produce the same output for a given format.

**Future considerations:** HTML output, custom output formats via
plugins, streaming output for large projects.

---

## 12. Output Formats

### Console

**Purpose:** Human-readable output for terminal use.

**Consumers:** Developers running the tool locally, CI logs.

**Limitations:** Not machine-readable. Color support varies by
terminal. Not suitable for parsing by other tools.

**Features:**

- Colored severity labels (red for error, yellow for warning, blue for
  info).
- File:line:column location format.
- Summary line with counts and timing.
- Optional statistics output.
- Respects `--color` / `--no-color` and terminal detection.

### JSON

**Purpose:** Machine-readable output for CI dashboards, custom
integrations, and tooling.

**Consumers:** CI pipelines, dashboards, custom tools, IDE extensions.

**Limitations:** Not human-readable for large outputs. Requires
schema documentation for consumers.

**Features:**

- Stable, versioned schema (`schemaVersion` field).
- Complete diagnostic information.
- Summary with counts by severity, rule, and category.
- Execution metadata (tool version, configuration, timing).
- Pretty-print or compact mode.

### Markdown

**Purpose:** Human-readable output for GitHub Actions summaries, PR
comments, wikis, and documentation.

**Consumers:** GitHub Actions summaries, PR comments, wikis, issue
trackers.

**Limitations:** Not machine-readable. Limited formatting (no
interactive elements).

**Features:**

- Summary table with counts by severity.
- Diagnostic table with file, line, rule, severity, message.
- Collapsible sections for long lists.
- Links to rule documentation.

### SARIF (Future)

**Purpose:** Standardized output for GitHub Code Scanning and other
security/quality platforms.

**Consumers:** GitHub Code Scanning, Azure DevOps, SonarQube, other
SARIF-consuming platforms.

**Limitations:** Complex schema. Overhead for small projects. Requires
SARIF SDK for generation.

**Features:**

- SARIF v2.1.0 compliant.
- Rule metadata embedded in the report.
- Inline location information.
- GitHub Code Scanning integration.

### GitHub Actions (Future)

**Purpose:** Inline PR annotations using GitHub Actions workflow
commands.

**Consumers:** GitHub Actions, PR review interface.

**Limitations:** GitHub-specific. Limited to 10 annotations per file
(GitHub limit).

**Features:**

- `::error` and `::warning` workflow commands.
- File, line, and column information.
- Rule ID and message in the annotation text.

### Future Formats

- **HTML:** Visual lint report with filtering, grouping, and search.
- **JUnit XML:** For CI systems that consume JUnit-style test results.
- **CSV:** For spreadsheet analysis and reporting.
- **Custom:** Via plugin output format extensions.

**Rationale:** Multiple output formats ensure the tool integrates with
any workflow. Console for humans, JSON for machines, Markdown for PRs,
SARIF for security platforms. Each format has a clear purpose and
consumer.

**Constraints:** Each format must be independently testable and stable.
Adding a new format is a minor version change. Changing an existing
format's schema is a major version change.

**Future considerations:** Output format plugins, streaming output,
incremental output (emit diagnostics as they are found rather than at
the end).

---

## 13. Performance Requirements

### Scalability

behave-lint must scale from a single file to thousands of feature files
without degradation:

- **Small project (10 files):** Less than 100ms.
- **Medium project (100 files):** Less than 500ms.
- **Large project (1,000 files):** Less than 2s.
- **Enterprise project (5,000+ files):** Less than 10s (without cache),
  less than 2s (with cache, incremental).

**Rationale:** Performance is a feature. If the tool is slow, it will
not be used in pre-commit hooks or IDEs. The targets are based on
Ruff's performance characteristics and the expectation that
`behave-model` parsing is the primary cost.

**Constraints:** Performance targets assume a modern CI runner (2+ CPU
cores, 4GB+ RAM). Performance on slower hardware may differ.

**Future considerations:** Rust/C extension for parsing hotspots (if
Python proves insufficient), lazy loading of features, parallel file
loading.

### Memory Usage

- **Small project:** Less than 50MB.
- **Medium project:** Less than 100MB.
- **Large project:** Less than 500MB.
- **Enterprise project:** Less than 2GB.

**Rationale:** Memory usage must be bounded to avoid OOM kills in CI
containers. The primary memory consumer is the parsed project tree
from `behave-model`.

**Constraints:** Memory usage is dominated by `behave-model`'s parsed
representation. behave-lint must not duplicate the project tree
unnecessarily.

**Future considerations:** Streaming analysis (analyze one feature at
a time for single-file rules), memory-mapped file loading.

### Execution Time

Execution time is dominated by:

1. **Project loading** (parsing via `behave-model`) — approximately 60%
   of total.
2. **Rule execution** — approximately 30% of total.
3. **Output generation** — approximately 10% of total.

Optimization efforts should focus on project loading (caching) and
rule execution (parallelization).

**Rationale:** Understanding the time breakdown guides optimization
efforts. Parsing is the bottleneck, which is delegated to
`behave-model` — so caching at the behave-lint level is the primary
mitigation.

**Constraints:** The tool cannot control `behave-model`'s parsing
speed. It can only cache results and avoid re-parsing unchanged
files.

**Future considerations:** Pre-parsed project caching (serialize the
`Project` tree to disk and reload it), incremental parsing support
in `behave-model`.

### Parallel Execution

- Rules that operate on individual features or scenarios can be
  executed in parallel.
- Cross-file rules (e.g., duplicate step detection) must be executed
  after single-file rules, in a sequential pass.
- The number of parallel workers is configurable (default: number of
  CPU cores).
- Parallel execution must not affect diagnostic ordering or content.

**Rationale:** Parallel execution can significantly speed up rule
execution on multi-core machines. The distinction between single-file
and cross-file rules ensures correctness.

**Constraints:** Parallel execution must be deterministic. The same
diagnostics must be produced regardless of the number of workers.

**Future considerations:** Parallel file loading, parallel output
generation, work stealing for load balancing.

### Caching

Caching is essential for incremental analysis:

- **Cache key:** File content hash + configuration hash + behave-model
  version.
- **Cache content:** Diagnostics for each file.
- **Cache invalidation:** When any component of the cache key changes.
- **Cache location:** `.behave-lint-cache/` in the project root
  (configurable).
- **Cache format:** Internal, not guaranteed to be stable across
  versions.

**Rationale:** Caching enables sub-second re-linting of changed files,
which is essential for pre-commit hooks and IDE integration.

**Constraints:** The cache must not produce stale results. If in doubt,
the cache is invalidated. Cache corruption is detected and handled
gracefully (re-analyze from scratch).

**Future considerations:** Remote caching (share cache across CI runs),
cache compression, cache analytics.

### Large Repositories

For repositories with 5,000+ feature files:

- The tool must not load all files into memory simultaneously if
  possible (streaming analysis for single-file rules).
- Cross-file rules may require loading all files, but memory usage must
  be bounded.
- Progress indication is essential for long-running analyses.
- The tool must be interruptible (Ctrl+C) and clean up gracefully.

**Rationale:** Large repositories are a reality in enterprise
environments. The tool must handle them without crashing or
hanging.

**Constraints:** Streaming analysis is limited by `behave-model`'s API.
If `behave-model` does not support incremental loading, all files
must be loaded at once.

**Future considerations:** Incremental loading support in
`behave-model`, memory-mapped file access, distributed analysis for
very large repositories.

---

## 14. Reliability

### Deterministic Execution

- The same project, configuration, and tool version must always produce
  the same diagnostics.
- Rule execution order is deterministic (sorted by rule ID, unless
  overridden).
- Diagnostic sorting is deterministic (by file, line, rule ID).
- No randomness, no time-based behavior, no network calls.

**Rationale:** Determinism is essential for CI. Non-deterministic
output causes flaky CI, erodes trust, and prevents reliable
comparisons across runs.

**Constraints:** Determinism must hold even with parallel execution.
Parallel execution must not affect the set or order of diagnostics.

**Future considerations:** Deterministic mode flag that disables any
non-deterministic features (e.g., timing in output).

### Repeatability

- Running the tool twice on the same project must produce identical
  output.
- Caching must not affect the output (only the speed).
- Environment variables must not affect diagnostics (only
  configuration).

**Rationale:** Repeatability is a corollary of determinism. If the
output changes between runs, users cannot trust the tool.

**Constraints:** The tool must not depend on external state (network,
system locale, time zone) for diagnostic generation.

**Future considerations:** Reproducible output hash (a hash of the
diagnostics that can be compared across runs).

### Stable Rule Ordering

- Rules are executed in a stable, documented order.
- The default order is: correctness rules first, then style, then
  complexity, then consistency, then pedantic, then step definitions.
- Within each category, rules are ordered by rule ID.
- Rule order can be overridden in configuration (rarely needed).

**Rationale:** Stable rule ordering ensures that diagnostics are
presented consistently. It also ensures that rules that depend on
the output of other rules (future) can rely on execution order.

**Constraints:** Rule order must not change between minor versions.

**Future considerations:** Rule dependency declaration (rule B depends
on rule A having run first).

### Predictable Diagnostics

- A rule must produce the same diagnostics for the same input.
- Rules must not produce different diagnostics based on the presence or
  absence of other rules.
- Rules must not modify the project tree (rules are read-only).

**Rationale:** Predictable diagnostics are essential for trust. If a
rule's output changes based on which other rules are enabled, the
tool becomes unpredictable and hard to configure.

**Constraints:** Rules must be pure functions of (project,
configuration) to diagnostics. No side effects, no shared mutable
state.

**Future considerations:** Rule isolation (sandbox rule execution to
catch rules that modify the project tree).

---

## 15. Extensibility

### New Rules

Contributors can add new rules through:

1. **Built-in rules:** Contributed to the behave-lint project via PR.
   Must follow the rule lifecycle (proposed, experimental, stable).
2. **Plugin rules:** Distributed as separate pip packages. Discovered
   via Python entry points. Do not require modifying behave-lint.

Both paths use the same rule interface. The only difference is
distribution.

**Rationale:** Two paths for adding rules ensure that broadly useful
rules become built-in, while domain-specific rules can be distributed
without contributing to the core project.

**Constraints:** The rule interface must be stable across minor
versions. Breaking changes require a major version bump and migration
guide.

**Future considerations:** Rule review process, rule quality criteria,
rule graduation criteria.

### New Output Formats

Contributors can add new output formats through:

1. **Built-in formats:** Contributed to the behave-lint project via PR.
2. **Plugin formats:** Distributed as separate pip packages. Discovered
   via Python entry points.

Output format plugins receive the full set of diagnostics and metadata
and are responsible for rendering them.

**Rationale:** Output format plugins enable integration with
platform-specific formats (e.g., JUnit XML, TeamCity) without
bloating the core project.

**Constraints:** Output format plugins must not affect diagnostic
generation or rule execution.

**Future considerations:** Output format validation, output format
testing framework.

### New Configuration Options

Configuration options can be added through:

1. **Built-in options:** Added to the configuration schema via PR.
2. **Plugin options:** Plugins can declare configuration keys that are
   validated and passed to the plugin's rules.

**Rationale:** Plugin configuration allows rules to be parameterized
without hardcoding options in the core configuration schema.

**Constraints:** Plugin configuration keys must be namespaced (e.g.,
`plugins.my-plugin.max-steps`) to avoid collisions.

**Future considerations:** Configuration schema auto-generation from
plugin metadata.

### Plugin System

The plugin system is based on Python entry points — the standard
mechanism used by pytest, flake8, and other Python tools:

- **Rule plugins:** Register one or more rules.
- **Output format plugins:** Register a new output format.
- **Configuration plugins:** Register new configuration options.

Plugins are auto-discovered from installed packages. They can be
explicitly disabled in configuration.

**Rationale:** Entry points are the Python standard for plugin
discovery. They are well-understood, well-supported by packaging
tools, and do not require custom infrastructure.

**Constraints:** Plugin discovery must be fast (no file system
scanning, no network calls). Plugin load failures must not crash the
tool.

**Future considerations:** Plugin validation, plugin sandboxing,
plugin marketplace, plugin dependency resolution.

### New Diagnostic Types

Future versions may support new diagnostic types beyond the standard
(error, warning, info):

- **Hints:** Subtle suggestions that are not issues per se (e.g., "this
  scenario could be split into two").
- **Metrics:** Non-issue observations (e.g., "this feature has 15
  scenarios, which is above average").

**Rationale:** New diagnostic types enable richer feedback without
overloading the severity system.

**Constraints:** New diagnostic types must not break existing output
formats. Consumers that do not understand a diagnostic type must
ignore it gracefully.

**Future considerations:** Custom diagnostic types via plugins.

---

## 16. Integration

### behave-model

behave-lint depends on `behave-model` as its single source of truth:

- **Parsing:** behave-lint calls `behave-model`'s `load_project` or
  `load_feature` to parse `.feature` files. It never parses directly.
- **Domain model:** behave-lint uses `behave-model`'s dataclasses
  (`Project`, `Feature`, `Scenario`, `Step`, etc.) for analysis.
- **Visitor pattern:** behave-lint uses `behave-model`'s visitor pattern
  for tree traversal in rules.
- **Query API:** behave-lint uses `behave-model`'s query functions for
  efficient element location.
- **Validation framework:** behave-lint extends `behave-model`'s
  `ValidationRule` and `ValidationIssue` with richer diagnostics,
  configuration, and plugin support.

**Rationale:** Using `behave-model` as the single source of truth
eliminates parsing duplication, ensures consistency across ecosystem
tools, and allows behave-lint to benefit from `behave-model`'s
improvements.

**Constraints:** behave-lint is limited by `behave-model`'s API
surface. If `behave-model` does not expose certain information,
behave-lint cannot analyze it without violating the "no direct
parsing" constraint.

**Future considerations:** Deeper integration with `behave-model`'s
validation framework, shared rule definitions, co-development of new
model features.

### behave-format

behave-lint and behave-format are complementary:

- **behave-format** handles style (whitespace, indentation, table
  alignment, tag sorting). It modifies files.
- **behave-lint** handles semantics and structure (duplicate names,
  missing tags, anti-patterns). It reports issues without modifying
  files.
- The recommended workflow is: format first, then lint.

**Rationale:** Clear separation prevents overlap and confusion. If an
issue can be auto-fixed by formatting, it belongs in behave-format.
If it requires human judgment, it belongs in behave-lint.

**Constraints:** behave-lint must not duplicate behave-format's
functionality. Style rules in behave-lint should detect issues that
behave-format cannot fix (e.g., inconsistent tag naming conventions).

**Future considerations:** `behave-lint --fix` integration with
behave-format (run format after applying fixes), shared configuration
for overlapping concerns.

### GitHub Actions

behave-lint integrates with GitHub Actions through:

- **GitHub Actions output format:** Uses `::error` and `::warning`
  workflow commands for inline PR annotations.
- **GitHub Actions action:** A reusable GitHub Action
  (`uses: behave-lint/action@v1`) for one-step setup.
- **SARIF output:** For GitHub Code Scanning integration (future).
- **PR comment bot:** Posts a summary comment on PRs with lint results
  (future).

**Rationale:** GitHub Actions is the most popular CI platform for open
source projects. First-class integration is essential for adoption.

**Constraints:** GitHub Actions integration must work with both
push and pull_request events. It must not require special
permissions beyond the default.

**Future considerations:** GitHub Actions cache integration, GitHub
Actions job summary support.

### GitLab CI

behave-lint integrates with GitLab CI through:

- **JSON output:** Parsed by GitLab CI scripts for custom reporting.
- **Code Quality report:** GitLab's code quality format (future).
- **MR (Merge Request) comments:** Via GitLab API (future).

**Rationale:** GitLab CI is widely used in enterprise environments.
JSON output provides basic integration; native Code Quality support
is a future enhancement.

**Constraints:** GitLab integration must not require special GitLab
features available only in premium tiers.

**Future considerations:** Native GitLab Code Quality report format,
GitLab MR approval rule integration.

### Azure DevOps

behave-lint integrates with Azure DevOps through:

- **JSON output:** Parsed by Azure Pipelines scripts.
- **Logging commands:** Azure DevOps `##vso[task.logissue]` commands
  for inline annotations (future).

**Rationale:** Azure DevOps is common in enterprise environments.
Basic integration via JSON output is sufficient initially.

**Constraints:** Azure DevOps integration must work with both hosted
and self-hosted agents.

**Future considerations:** Native Azure DevOps task, Azure DevOps
pull request integration.

### pre-commit

behave-lint integrates with pre-commit through:

- **pre-commit hook configuration:** A `.pre-commit-hooks.yaml` file
  in the behave-lint repository for easy `pre-commit` integration.
- **Fast execution:** The tool must be fast enough for pre-commit (sub-
  second on changed files).
- **Staged files only:** When run via pre-commit, only staged `.feature`
  files are linted.

**Rationale:** pre-commit is the standard pre-commit hook framework
for Python projects. Integration is essential for developer
workflow.

**Constraints:** The pre-commit hook must not require network access
(beyond initial installation). It must work with pre-commit's
isolated environment model.

**Future considerations:** pre-commit cache integration, pre-commit
autoupdate support.

### Editors and IDEs

behave-lint integrates with editors and IDEs through:

- **CLI integration:** Any editor that can run shell commands can use
  behave-lint (VS Code tasks, Vim neomake, Emacs flycheck).
- **LSP implementation:** A Language Server Protocol implementation
  for real-time feedback (future).
- **VS Code extension:** A VS Code extension using the LSP
  implementation (future).
- **PyCharm plugin:** A PyCharm/IntelliJ plugin using the LSP
  implementation (future).

**Rationale:** IDE integration is the most requested feature for any
linter. CLI integration works initially, but LSP provides real-time
feedback that developers expect.

**Constraints:** LSP implementation must be performant (sub-100ms per
file change). It must work with VS Code, Neovim, Emacs, and any LSP-
compatible editor.

**Future considerations:** LSP auto-fix, LSP rule documentation on
hover, LSP configuration UI.

---

## 17. Documentation

### README

The README must include:

- **Project description:** What behave-lint is and why it exists.
- **Installation:** `pip install behave-lint`.
- **Quick start:** One-command usage with zero configuration.
- **Features:** A concise list of key features.
- **Configuration:** A brief overview with a link to detailed docs.
- **CLI usage:** Common commands and flags.
- **Integration:** Links to CI, pre-commit, and IDE integration guides.
- **Ecosystem:** Links to `behave-model`, `behave-format`, and report
  libraries.
- **Contributing:** Link to the contribution guide.
- **License:** MIT.

**Rationale:** The README is the first thing users see. It must get
them from install to value in under 5 minutes.

**Constraints:** The README must be kept in sync with the tool's
capabilities. Stale READMEs erode trust.

**Future considerations:** Interactive README (executable examples),
localized READMEs.

### Rule Documentation

Rule documentation is generated from rule metadata:

- **Rule catalog:** A complete list of all rules with their metadata.
- **Individual rule pages:** One page per rule with description,
  rationale, examples, configuration, and auto-fix capability.
- **Category pages:** One page per category with the list of rules in
  that category.
- **Search:** Full-text search across rule documentation.
- **CLI access:** `behave-lint --explain <rule-id>` and `behave-lint
  --list-rules`.

**Rationale:** Generated documentation is always accurate. Manual
documentation drifts from the implementation.

**Constraints:** Rule metadata must be complete at the time of rule
introduction. Incomplete metadata blocks inclusion.

**Future considerations:** Interactive rule explorer, rule
documentation in multiple languages, rule recommendation engine.

### Examples

The documentation must include:

- **Quick start example:** Zero-config usage.
- **Configuration examples:** Common configuration patterns.
- **CI examples:** GitHub Actions, GitLab CI, Azure DevOps, Jenkins.
- **Pre-commit example:** `.pre-commit-config.yaml` snippet.
- **Custom rule example:** A complete custom rule with tests.
- **Plugin example:** A complete plugin package with setup
  configuration.

**Rationale:** Examples are the most effective documentation. Users
copy, paste, and adapt.

**Constraints:** Examples must be tested and kept in sync with the
tool's capabilities.

**Future considerations:** Example gallery, community examples
repository.

### Migration Guides

Migration guides are required for:

- **Major version upgrades:** When breaking changes occur.
- **Rule deprecations:** When rules are deprecated or removed.
- **Configuration changes:** When the configuration schema changes.
- **From ad-hoc scripts:** How to migrate from custom validation
  scripts to behave-lint.

**Rationale:** Migration guides reduce the pain of breaking changes
and encourage adoption.

**Constraints:** Migration guides must be published before the
breaking change is released.

**Future considerations:** Automated migration tool, migration guide
generator.

### Contribution Guide

The contribution guide must include:

- **Development setup:** How to clone, install, and run tests.
- **Code style:** Ruff configuration, type checking, formatting.
- **Adding a rule:** Step-by-step guide with examples.
- **Adding a plugin:** How to create and distribute a plugin.
- **Testing:** How to write tests for rules and the engine.
- **Pull request process:** Branch naming, commit messages, review
  criteria.
- **Release process:** How releases are cut and published.

**Rationale:** A clear contribution guide lowers the barrier for
community participation.

**Constraints:** The contribution guide must be accurate and kept in
sync with the project's processes.

**Future considerations:** Contributor onboarding program, mentorship
for first-time contributors.

### FAQ

The FAQ must address:

- **Common configuration questions.**
- **Common rule questions.**
- **Performance questions.**
- **Integration questions.**
- **Comparison with other tools.**
- **"Why is rule X not enabled by default?"**
- **"How do I suppress a diagnostic?"**
- **"How do I write a custom rule?"**

**Rationale:** An FAQ reduces support burden and helps users
self-serve.

**Constraints:** The FAQ must be updated based on real user questions,
not hypothetical ones.

**Future considerations:** Community-driven FAQ (GitHub Discussions),
searchable FAQ.

### Best Practices

Best practices documentation must include:

- **Gherkin best practices:** How to write good feature files.
- **Tag taxonomy best practices:** How to organize tags.
- **Step reuse best practices:** How to avoid duplication.
- **CI/CD best practices:** How to integrate behave-lint in CI.
- **Team adoption best practices:** How to roll out behave-lint
  gradually.

**Rationale:** Best practices documentation provides value beyond the
tool itself. It positions behave-lint as an authority on BDD
quality.

**Constraints:** Best practices must be evidence-based, not
opinionated without justification.

**Future considerations:** Best practices benchmarks, community best
practices contributions.

---

## 18. Error Handling

### Invalid Configuration

- **Detection:** Configuration is validated at load time.
- **Behaviour:** The tool exits with code 2 and prints a clear error
  message to stderr.
- **Error message:** Includes the configuration file path, the invalid
  key or value, the expected format, and a suggestion for fixing it.
- **No diagnostics are produced.** The tool cannot run with invalid
  configuration.

**Rationale:** Clear configuration errors are essential for developer
experience. Cryptic errors frustrate users and block adoption.

**Constraints:** Error messages must be actionable. They must tell the
user exactly what is wrong and how to fix it.

**Future considerations:** Configuration lint mode, configuration
auto-correction.

### Internal Failures

- **Detection:** Unexpected exceptions during rule execution or output
  generation.
- **Behaviour:** The tool exits with code 2 and prints a clear error
  message to stderr, including a stack trace in verbose mode.
- **Partial results:** If some rules completed successfully, their
  diagnostics may be output (configurable: `--emit-partial-results`).
- **Error reporting:** The error message includes guidance for filing
  a bug report (link to GitHub Issues).

**Rationale:** Internal failures should be rare but must be handled
gracefully. A crash with no guidance erodes trust.

**Constraints:** Internal failures must not produce incorrect
diagnostics. It is better to produce no diagnostics than wrong ones.

**Future considerations:** Automatic error reporting (opt-in), crash
report generation.

### Corrupted Projects

- **Detection:** Parse errors from `behave-model` (malformed Gherkin,
  file encoding issues, file not found).
- **Behaviour:** The tool reports the parse error as a diagnostic
  (severity: error, rule: `B000` — parse error) and continues linting
  other files.
- **Partial results:** Files that parsed successfully are linted
  normally. Files that failed to parse are skipped.
- **Summary:** The summary includes the count of files that failed to
  parse.

**Rationale:** A single malformed file should not prevent linting of
the rest of the project. This is especially important in CI, where
a single parse error should not mask other quality issues.

**Constraints:** Parse errors must be clearly distinguished from lint
diagnostics. They use a reserved rule ID (`B000`).

**Future considerations:** Parse error recovery (lint what can be
parsed from a malformed file), encoding detection.

### Unknown Rules

- **Detection:** A rule ID referenced in configuration (select, ignore,
  severity) is not found in the registered rules.
- **Behaviour:** The tool prints a warning to stderr and continues.
  The unknown rule ID is ignored.
- **Warning message:** "Unknown rule 'B999' in configuration. Did you
  mean 'B009'?"

**Rationale:** Unknown rules are likely typos or references to rules
from a different version. A warning with a suggestion helps users
correct the mistake without blocking the run.

**Constraints:** Unknown rules must not cause a hard failure. This
allows configuration to be forward-compatible (referencing rules
from a newer version does not break on an older version).

**Future considerations:** Fuzzy matching for rule ID suggestions,
rule ID validation against a published registry.

### Unsupported Features

- **Detection:** The tool encounters a Gherkin feature that it does not
  support (e.g., a new Gherkin keyword not yet handled by
  `behave-model`).
- **Behaviour:** The tool prints an informational message and continues.
  The unsupported feature is skipped.
- **No diagnostics are produced for the unsupported feature.**

**Rationale:** The tool must not crash on unknown Gherkin constructs.
It should gracefully degrade and continue linting what it can.

**Constraints:** Unsupported features must be clearly communicated so
users understand why certain files are not fully linted.

**Future considerations:** Unsupported feature reporting, compatibility
matrix.

### Graceful Degradation

The tool must degrade gracefully in all error scenarios:

- **Parse error in one file:** Continue linting other files.
- **Rule execution failure:** Continue executing other rules.
- **Plugin load failure:** Continue without the plugin's rules.
- **Output generation failure:** Print diagnostics to stderr as a
  fallback.
- **Cache corruption:** Discard the cache and re-analyze from scratch.

**Rationale:** Graceful degradation ensures that the tool is reliable
in real-world conditions. A single failure should not invalidate the
entire run.

**Constraints:** Graceful degradation must not produce incorrect
diagnostics. When in doubt, skip rather than guess.

**Future considerations:** Error recovery mode (attempt to produce
partial results in all scenarios), error analytics.

---

## 19. Accessibility

### Readable Console Output

- Diagnostics are presented in a clear, scannable format.
- Information is ordered by importance: location, rule, severity,
  message.
- Long messages are wrapped at the terminal width.
- Summary line is always at the end, clearly separated.
- Color is used to enhance, not replace, text labels. Severity is
  always indicated by a text label, not color alone.

**Rationale:** Readable output benefits all users, not just those with
accessibility needs. Clear formatting reduces cognitive load.

**Constraints:** Output must be readable in terminals with as few as
80 columns.

**Future considerations:** Configurable output formatting, compact
mode, detailed mode.

### Color Support

- Color is enabled by default when stdout is a terminal.
- Color is disabled when stdout is piped or redirected.
- Color can be explicitly enabled or disabled via `--color` /
  `--no-color`.
- Color codes follow the ANSI standard (widely supported).
- Colors are chosen for sufficient contrast on both light and dark
  terminal backgrounds.

**Rationale:** Color improves readability but must not be required for
understanding. Disabling color when piped ensures machine-readable
output is clean.

**Constraints:** Color must not be the sole indicator of severity.
Text labels are always present.

**Future considerations:** Custom color themes, truecolor support,
terminal theme detection.

### Color Blind Friendly Output

- Severity is indicated by text labels (error, warning, info), not
  color alone.
- Color choices avoid red-green confusion (the most common color
  blindness).
- A `--color-blind` mode may be offered that uses patterns or icons
  in addition to color (future).

**Rationale:** Approximately 8% of men have some form of color vision
deficiency. The tool must be usable by all developers.

**Constraints:** The default color scheme must be readable by users
with deuteranopia and protanopia.

**Future considerations:** Pattern-based severity indicators (e.g.,
`E:`, `W:`, `I:`), icon-based indicators.

### Screen Readers

- Console output is designed to be readable by screen readers.
- Information is presented in a logical order: file, line, severity,
  rule, message.
- No essential information is conveyed solely through visual
  formatting (color, indentation).
- JSON output is available for tools that provide screen-reader-
  friendly interfaces.

**Rationale:** Screen reader compatibility ensures the tool is
accessible to visually impaired developers.

**Constraints:** Console output must not use control characters that
confuse screen readers (beyond standard ANSI color codes).

**Future considerations:** Screen reader mode (optimized output
format), integration with accessibility tools.

### Terminal Compatibility

- The tool works in all major terminals: Windows Terminal, PowerShell,
  cmd.exe, macOS Terminal, iTerm2, GNOME Terminal, Konsole, Alacritty,
  Kitty, tmux, screen.
- ANSI color codes are used (supported by all modern terminals).
- On legacy Windows terminals (cmd.exe without virtual terminal
  support), color is automatically disabled.
- Unicode characters are used sparingly and only when widely supported.
  ASCII alternatives are available.

**Rationale:** Terminal compatibility ensures the tool works in all
environments without configuration.

**Constraints:** The tool must not require a specific terminal or
font.

**Future considerations:** Unicode feature detection, terminal
capability detection, fallback rendering.

### Unicode Support

- File paths with Unicode characters are supported.
- Feature file content with Unicode characters is supported.
- Diagnostic messages use ASCII by default for maximum compatibility.
- Unicode characters (e.g., checkmarks, arrows) may be used in console
  output when the terminal supports them, with ASCII fallbacks.

**Rationale:** Unicode support is essential for international users
and projects with non-ASCII content.

**Constraints:** Unicode must not break output parsing or machine-
readable formats.

**Future considerations:** Unicode detection, locale-aware output,
emoji support (opt-in).

---

## 20. Internationalization

### Language Support

- The tool's CLI, diagnostics, and documentation are in English
  (initially).
- Feature file content in any language is supported (Gherkin supports
  multiple languages via `# language:` header).
- Rule messages are in English (initially).
- Diagnostic messages are designed to be translatable (no hardcoded
  grammar assumptions).

**Rationale:** English is the lingua franca of open source software.
Starting with English ensures the widest initial reach. Designing
for translatability ensures future localization is possible without
redesigning the message system.

**Constraints:** The tool must not assume English grammar (word order,
pluralization rules) in its message generation. Messages must use
interpolation, not concatenation.

**Future considerations:** Message catalog system, community
translations.

### Localization Strategy

- **Phase 1 (v1):** English only. Messages are designed for
  translatability.
- **Phase 2 (v2+):** Message catalog system (gettext-style). Messages
  are externalized into translation files.
- **Phase 3 (v3+):** Community translations. Translations are
  contributed and maintained by the community. The tool ships with
  available translations and falls back to English for untranslated
  messages.

**Rationale:** A phased approach allows the tool to launch quickly
while keeping the door open for localization. Designing for
translatability from the start avoids costly refactoring later.

**Constraints:** Localization must not affect diagnostic structure or
machine-readable output. Rule IDs, severities, and locations are
always in a canonical format.

**Future considerations:** Right-to-left language support, locale-aware
date/time formatting in output.

### Future Translations

- Translation files are hosted in the behave-lint repository.
- Translations are contributed via PR.
- A translation review process ensures quality.
- The tool selects the language based on the system locale (overridable
  via configuration or environment variable).
- Untranslated messages fall back to English.

**Rationale:** Community-driven translations are the most sustainable
model for open source projects.

**Constraints:** Translations must be maintained. Stale translations
are removed if not updated within two major versions.

**Future considerations:** Translation platform integration
(Weblate, Crowdin), translation statistics, translation
contributor recognition.

---

## 21. Security

### Safe Execution

- behave-lint does not execute arbitrary code.
- behave-lint does not evaluate Python expressions from `.feature`
  files.
- behave-lint does not import or execute step definition files (it
  performs static analysis via AST parsing, not import).
- behave-lint does not make network requests.
- behave-lint does not write to files (except the cache and explicitly
  requested output files).

**Rationale:** Safety is paramount for a tool that runs in CI
pipelines and developer machines. Any code execution vulnerability
would be catastrophic for adoption.

**Constraints:** The tool must be auditable. All file system access
must be explicit and documented.

**Future considerations:** Security audit, supply chain security
(SBOM), dependency scanning.

### No Code Execution

- Step definition analysis uses Python's `ast` module (standard
  library) to parse Python files without importing or executing them.
- No `eval`, `exec`, `import`, or `subprocess` calls on user-
  provided content.
- Plugin code is executed (plugins are Python packages), but plugins
  are explicitly installed by the user via `pip install`. This is the
  same trust model as any Python package.

**Rationale:** The distinction between static analysis (safe) and code
execution (unsafe) is critical. Step definition analysis must never
import the step definition modules, as they may have side effects or
dependencies that are not available in the linting environment.

**Constraints:** AST parsing is limited to syntax analysis. It cannot
detect runtime behavior (e.g., dynamically registered steps). This
limitation is documented.

**Future considerations:** Plugin sandboxing, plugin permission model.

### Safe Parsing Through behave-model

- All parsing is delegated to `behave-model`, which wraps Behave's
  parser.
- behave-lint never reads or parses `.feature` file content directly.
- Parse errors from `behave-model` are handled gracefully (see Error
  Handling).

**Rationale:** Delegating parsing to `behave-model` ensures that
behave-lint benefits from `behave-model`'s security and correctness.
It also eliminates the risk of behave-lint introducing parsing
vulnerabilities.

**Constraints:** behave-lint is dependent on `behave-model`'s security
posture. If `behave-model` has a vulnerability, behave-lint inherits
it.

**Future considerations:** Dependency vulnerability scanning, security
policy (SECURITY.md).

### Dependency Philosophy

- **Minimal dependencies:** behave-lint depends on `behave-model` and
  the Python standard library. No additional runtime dependencies for
  v1.
- **No network dependencies:** The tool does not require network
  access for any feature.
- **Auditable dependencies:** All dependencies are pinned with version
  ranges. Dependency updates are reviewed.
- **No telemetry:** The tool does not collect or transmit usage data.

**Rationale:** Minimal dependencies reduce the attack surface and
maintenance burden. No telemetry respects user privacy and builds
trust.

**Constraints:** Future features (SARIF, LSP) may require additional
dependencies. Each dependency must be justified and reviewed.

**Future considerations:** Software Bill of Materials (SBOM),
dependency vulnerability alerts, reproducible builds.

---

## 22. Non-Functional Requirements

### Platform Support

behave-lint must run on:

- **Operating systems:** Windows 10+, macOS 11+, Linux (any modern
  distribution with Python 3.11+).
- **Python versions:** 3.11, 3.12, 3.13, and future versions as they
  are released.
- **CI environments:** GitHub Actions, GitLab CI, Azure DevOps,
  Jenkins, CircleCI, Travis CI, and any environment that supports
  Python.
- **Terminal types:** All major terminals (see Accessibility → Terminal
  Compatibility).

**Rationale:** Broad platform support ensures the tool is usable by all
teams regardless of their technology stack. Python 3.11+ aligns with
`behave-model`'s minimum version.

**Constraints:** The tool must not use platform-specific APIs. Any
platform-specific behavior (e.g., color support on Windows) must
degrade gracefully.

**Future considerations:** Python 3.14+ support, WASM/WASI support for
browser-based usage.

### Python Version Compatibility

- The minimum Python version is 3.11 (matching `behave-model`).
- Each release is tested against all supported Python versions.
- Support for a Python version is dropped only in a major version bump,
  following Python's end-of-life schedule.

**Rationale:** Matching `behave-model`'s minimum version ensures
compatibility without imposing additional constraints. Following
Python's EOL schedule is standard practice.

**Constraints:** Dropping Python version support requires a major
version bump and a migration guide.

**Future considerations:** Automated compatibility testing matrix,
Python beta version support.

### Installation

- **Primary method:** `pip install behave-lint`.
- **Development method:** `pip install -e .` from a clone.
- **Pre-commit method:** Listed in pre-commit's hook repository.
- **No external dependencies beyond `behave-model`** for v1.

**Rationale:** `pip install` is the standard Python package
installation method. Minimal dependencies ensure fast installation
and a small footprint.

**Constraints:** Installation must not require compilation (no C
extensions for v1). Installation must work in virtual environments,
containers, and CI runners.

**Future considerations:** `uv` support, `pipx` recommendation for
standalone installation, Homebrew formula, conda-forge package.

### Packaging

- **Build system:** `hatchling` (matching `behave-model`).
- **Package format:** Wheel and sdist.
- **Package metadata:** `pyproject.toml` with all standard fields
  (name, version, description, authors, license, classifiers,
  dependencies, optional dependencies).
- **Entry point:** `behave-lint` console script.

**Rationale:** `hatchling` is the modern Python build backend used by
`behave-model`. Wheel + sdist ensures compatibility with all
installation methods.

**Constraints:** The package must be reproducible — the same source
must produce identical wheels.

**Future considerations:** Signed packages (sigstore), reproducible
build verification.

### Versioning

behave-lint follows **Semantic Versioning 2.0.0**:

- **Major (X.0.0):** Breaking changes — rule behavior changes, removed
  rules, configuration schema changes, diagnostic structure changes,
  Python version drops.
- **Minor (0.X.0):** New features — new rules, new output formats, new
  CLI flags, new configuration options. Backward-compatible.
- **Patch (0.0.X):** Bug fixes — rule false positive fixes, performance
  improvements, documentation updates. Backward-compatible.

**Rationale:** Semantic versioning provides clear expectations for
users upgrading between versions. It is the standard for Python
packages.

**Constraints:** Pre-1.0 versions (0.x.y) may include breaking changes
in minor versions, following common Python practice. Once 1.0 is
reached, strict semver applies.

**Future considerations:** Version changelog automation, release
candidate process, LTS (Long Term Support) releases.

### Backward Compatibility

- **Rule behavior:** Stable rules do not change behavior in minor or
  patch versions.
- **Configuration:** Configuration keys are stable within a major
  version. New keys may be added in minor versions.
- **Diagnostic structure:** Fields are stable within a major version.
  New fields may be added in minor versions.
- **CLI:** Flags are stable within a major version. New flags may be
  added in minor versions. Removed flags require a major version.
- **Output formats:** Schemas are versioned independently. Schema
  changes require a schema version bump.

**Rationale:** Backward compatibility is essential for CI stability.
Users must be able to upgrade minor versions without breaking their
pipelines.

**Constraints:** Bug fixes (where a rule was not doing what it was
supposed to do) are not considered breaking changes, even if they
change the output for some projects. This is documented in the
changelog.

**Future considerations:** Compatibility testing framework,
deprecation cycle automation.

### Release Cadence

- **Minor releases:** Every 1-2 months, or when significant features
  are ready.
- **Patch releases:** As needed for bug fixes.
- **Major releases:** When breaking changes are justified, with at
  least 3 months of deprecation warnings in the prior major version.

**Rationale:** A regular release cadence keeps the tool relevant and
fixes issues quickly. Major releases are infrequent to minimize
upgrade burden.

**Constraints:** Releases must not be rushed. Each release is tested
against the full test suite and compatibility matrix.

**Future considerations:** Scheduled releases (calendar-based),
release candidate process, automated release pipeline.

### Licensing

- **License:** MIT (matching `behave-model` and other ecosystem
  projects).
- **Contributions:** Licensed under the same MIT license.
- **Third-party dependencies:** Must be MIT, BSD, or Apache 2.0
  licensed. GPL or LGPL dependencies are not accepted.

**Rationale:** MIT is the most permissive widely-used license. It
encourages adoption and contribution. Matching the ecosystem ensures
consistency.

**Constraints:** The license must not change without unanimous
consent of all contributors.

**Future considerations:** Contributor License Agreement (CLA),
Software Package Data Exchange (SPDX) metadata.

---

## 23. Success Metrics

### Adoption Metrics

- **Downloads:** PyPI download count (tracked via PyPI statistics).
- **GitHub stars:** Indicator of community interest.
- **Forks:** Indicator of community engagement.
- **Contributors:** Number of unique contributors over time.
- **Issues/PRs:** Number of open and closed issues/PRs as a health
  indicator.
- **Pre-commit installations:** Number of projects using behave-lint
  via pre-commit (estimated from hook download counts).

**Rationale:** Adoption metrics indicate whether the tool is reaching
its target audience and gaining traction.

**Constraints:** Download counts are approximate and include CI runs.
They should be treated as trends, not exact numbers.

**Future considerations:** Usage analytics (opt-in), ecosystem
dashboard, community survey.

### Performance Metrics

- **Execution time:** Measured against benchmark projects of varying
  sizes (10, 100, 1000, 5000 files).
- **Memory usage:** Peak memory usage during analysis.
- **Cache hit rate:** Percentage of cache hits in incremental runs.
- **Startup time:** Time from CLI invocation to first diagnostic.

**Rationale:** Performance metrics ensure the tool meets its
performance targets and does not regress over time.

**Constraints:** Performance benchmarks must be run in a controlled
environment (CI runner with consistent specs).

**Future considerations:** Performance regression detection in CI,
performance comparison dashboard.

### Rule Coverage Metrics

- **Number of rules:** Total rules available (by category, by
  lifecycle stage).
- **Rule usage:** Which rules are most/least enabled (from community
  surveys, not telemetry).
- **False positive rate:** Reported false positives per rule (from
  GitHub issues).
- **Auto-fix coverage:** Percentage of rules that are auto-fixable.

**Rationale:** Rule coverage metrics indicate the breadth and quality
of the rule set.

**Constraints:** Usage data is collected through community surveys,
not telemetry. Privacy is respected.

**Future considerations:** Rule effectiveness analysis, rule impact
survey.

### Documentation Quality Metrics

- **Documentation coverage:** Percentage of rules with complete
  metadata.
- **Documentation freshness:** Time since last documentation update.
- **README effectiveness:** Time from install to first successful run
  (measured via user testing).
- **FAQ effectiveness:** Reduction in support issues over time.

**Rationale:** Documentation quality directly impacts adoption and
user satisfaction.

**Constraints:** Some metrics (e.g., time to first run) require user
testing and are not automatable.

**Future considerations:** Documentation analytics, user feedback
widget, documentation contribution program.

### Community Health Metrics

- **Time to first response:** Average time for a maintainer to respond
  to an issue or PR.
- **Time to merge:** Average time from PR submission to merge.
- **Contributor retention:** Percentage of contributors who contribute
  more than once.
- **Issue resolution time:** Average time to close an issue.

**Rationale:** Community health metrics indicate whether the project
is sustainable and welcoming.

**Constraints:** Community health metrics are qualitative and require
human judgment alongside the numbers.

**Future considerations:** Community health dashboard, contributor
recognition program.

### Ecosystem Integration Metrics

- **behave-model compatibility:** Always compatible with the latest
  `behave-model` release.
- **behave-format compatibility:** No overlapping functionality.
  Complementary workflow documented.
- **CI integration:** Number of CI templates that include behave-lint
  (community-maintained).
- **IDE integration:** Number of editors/IDEs with behave-lint support
  (future, post-LSP).

**Rationale:** Ecosystem integration metrics ensure behave-lint is a
good citizen of the Behave ecosystem.

**Constraints:** Some metrics (e.g., CI template adoption) are
difficult to measure precisely.

**Future considerations:** Ecosystem compatibility testing, ecosystem
dashboard, integration partner program.

---

## 24. Risks

### Dependency Risks

**Risk:** behave-lint is critically dependent on `behave-model`. If
`behave-model` is abandoned, changes its API incompatibly, or has
performance issues, behave-lint is directly affected.

**Mitigation:**

- Maintain a close relationship with `behave-model` maintainers.
- Pin `behave-model` to compatible version ranges.
- Contribute to `behave-model` to ensure needed features are
  available.
- Maintain a compatibility matrix documenting which behave-lint
  versions work with which behave-model versions.

**Impact:** High. Loss of `behave-model` support would require
behave-lint to implement its own parsing, violating the core
architecture principle.

**Future considerations:** Fork `behave-model` if abandoned (last
resort), co-maintenance agreement.

### Adoption Risks

**Risk:** The Behave ecosystem is small compared to Cucumber/Java,
Cypress, or Playwright. The total addressable market for a Behave-
specific linter is limited.

**Mitigation:**

- Position behave-lint as the definitive BDD linter for Python.
- Ensure zero-config usability to minimize adoption friction.
- Provide clear value over ad-hoc validation scripts.
- Market through Behave community channels (GitHub Discussions,
  Python communities).
- Support Gherkin files from non-Behave tools (e.g., Cucumber Python)
  if they use standard Gherkin syntax.

**Impact:** Medium. Low adoption limits community contributions and
long-term sustainability.

**Future considerations:** Cross-framework Gherkin linting (support
Cucumber Python, other Gherkin-based tools), broader BDD community
outreach.

### Performance Risks

**Risk:** Python's performance may be insufficient for very large
projects (5,000+ files), especially if `behave-model`'s parsing is
slow.

**Mitigation:**

- Implement caching from day one to minimize re-parsing.
- Parallelize rule execution.
- Profile and optimize hotspots.
- Set clear performance targets and track them.
- If Python proves insufficient, consider Rust/C extension for
  parsing hotspots (future).

**Impact:** Medium. Poor performance limits use in pre-commit hooks
and IDEs, which are key adoption channels.

**Future considerations:** Rust-based parsing backend, incremental
parsing in `behave-model`, lazy evaluation.

### Maintenance Risks

**Risk:** The project may become unmaintained if the maintainer loses
interest or availability. This is the most common failure mode for
open source tools.

**Mitigation:**

- Build a community of contributors from the start.
- Document all processes (development, release, contribution).
- Keep the codebase clean and well-tested.
- Avoid bus factor of 1 by onboarding co-maintainers.
- Keep the scope focused — do not try to be everything to everyone.

**Impact:** High. An unmaintained linter becomes a liability in CI
pipelines.

**Future considerations:** Maintainer succession plan, project
governance model, sustainability funding (GitHub Sponsors, Open
Collective).

### Rule Quality Risks

**Risk:** Rules with high false positive rates cause teams to abandon
the tool. Rules that are too lenient provide no value. Finding the
right balance is difficult.

**Mitigation:**

- Start with a conservative default rule set (near-zero false
  positives).
- Use the experimental → stable lifecycle to vet rules before
  including them in defaults.
- Provide clear configuration to adjust or disable rules.
- Track false positive reports and act on them quickly.
- Document the rationale for each rule so users understand its
  purpose.

**Impact:** High. False positives are the #1 complaint about linters
and the #1 reason for abandonment.

**Future considerations:** False positive tracking dashboard, rule
quality criteria, community rule review process.

### Ecosystem Fragmentation Risk

**Risk:** The Behave ecosystem may fragment if multiple competing
tools emerge (e.g., multiple linters, multiple formatters). This
dilutes effort and confuses users.

**Mitigation:**

- Position behave-lint as the canonical linter for the Behave
  ecosystem.
- Collaborate with `behave-model` and `behave-format` maintainers to
  ensure clear separation of concerns.
- Welcome contributions rather than competing with forks.
- Document the ecosystem clearly so users know which tool does what.

**Impact:** Medium. Fragmentation reduces the effectiveness of all
ecosystem tools.

**Future considerations:** Ecosystem governance, ecosystem website,
ecoscosystem compatibility testing.

### Configuration Complexity Risk

**Risk:** Over time, configuration may become complex (like ESLint),
making the tool difficult to adopt and maintain.

**Mitigation:**

- Start with a flat, simple configuration schema.
- Add complexity only when justified by real-world demand.
- Provide sensible defaults so zero-config works.
- Resist feature creep in configuration.
- Provide presets for common configurations (future).

**Impact:** Medium. Configuration complexity is a barrier to adoption
and a source of user frustration.

**Future considerations:** Configuration complexity audit,
configuration simplification process, preset system.

---

## 25. Future Roadmap

### Phase 1: MVP (v0.1)

**Goal:** A usable linter with core rules and console output.

**Scope:**

- CLI with path arguments, `--select`, `--ignore`, `--output`,
  `--output-file`, `--color`/`--no-color`, `--version`, `--help`.
- `pyproject.toml` configuration under `[tool.behave-lint]`.
- 10-15 built-in rules covering correctness, style, and complexity.
- Console output format with color support.
- JSON output format.
- Markdown output format.
- Exit codes 0, 1, 2.
- `--list-rules` and `--explain` commands.
- Basic caching (file content hash).
- Integration with `behave-model` for parsing.
- Comprehensive test suite.
- README with quick start guide.
- MIT license.

**Success criteria:**

- Zero-config usage produces valuable feedback on a real project.
- All 10-15 rules have complete metadata.
- Performance: < 500ms on 100 files.
- No false positives in default rule set on well-formed feature files.

**Rationale:** The MVP establishes the tool's value proposition and
core functionality. It must be useful immediately to attract early
adopters.

**Future considerations:** Community feedback drives Phase 2
priorities.

### Phase 2: CI Integration (v0.2-v0.3)

**Goal:** First-class CI integration and expanded rule set.

**Scope:**

- GitHub Actions output format (`::error`, `::warning`).
- GitHub Actions reusable action (`uses: behave-lint/action@v1`).
- pre-commit hook configuration.
- 25-30 built-in rules covering all categories.
- Plugin system (rule plugins via entry points).
- `--statistics` flag.
- `--verbose` and `--quiet` flags.
- Environment variable support.
- Configuration validation with clear errors.
- Step definition analysis (opt-in).
- Rule lifecycle: experimental → stable graduation process.
- Contribution guide.
- Rule documentation (generated from metadata).

**Success criteria:**

- GitHub Actions integration works with zero configuration beyond
  adding the action.
- pre-commit integration works with a 3-line config.
- At least 3 community-contributed rules or plugins.
- Performance: < 2s on 1000 files.

**Rationale:** CI integration is the primary adoption channel for
linters. Expanding the rule set and plugin system enables community
growth.

**Future considerations:** GitLab CI native support, Azure DevOps
native support.

### Phase 3: Maturity (v0.4-v0.5)

**Goal:** Production-ready with comprehensive rules and reliability.

**Scope:**

- 40-50 built-in rules.
- SARIF output format.
- Parallel rule execution.
- Advanced caching (configuration hash, incremental analysis).
- Rule deprecation process.
- Migration guides.
- FAQ.
- Best practices documentation.
- Performance benchmarks and regression testing.
- Configuration presets (`extends = "strict"`, `extends = "minimal"`).
- `--config-check` flag.
- Fuzzy matching for unknown rule ID suggestions.
- Comprehensive edge case handling.

**Success criteria:**

- Used by 100+ projects (estimated from PyPI stats and pre-commit
  usage).
- No open data-loss or crash bugs.
- Performance: < 10s on 5000 files (without cache), < 2s (with
  cache).
- Community of 10+ contributors.

**Rationale:** Maturity phase focuses on reliability, performance, and
comprehensive coverage. This is where the tool becomes the
definitive BDD linter for Python.

**Future considerations:** 1.0 release readiness assessment.

### Phase 4: 1.0 Release

**Goal:** Stable, reliable, and feature-complete for 1.0.

**Scope:**

- Freezing of all public APIs (CLI, configuration, diagnostic
  structure, output schemas).
- Comprehensive documentation (README, rule catalog, examples,
  migration guides, FAQ, best practices).
- Security audit.
- Performance audit.
- 50+ built-in rules.
- Full plugin system (rules, output formats, configuration).
- All major CI platforms supported.
- Semver 2.0.0 compliance.
- LTS commitment (at least 12 months of patch support for 1.x).

**Success criteria:**

- No breaking changes planned for 12 months.
- All success metrics from Phase 3 met or exceeded.
- Community survey satisfaction score > 4/5.
- Used by 500+ projects.

**Rationale:** 1.0 signals stability and commitment. It gives
organizations confidence to adopt the tool in production.

**Future considerations:** 1.0 release event, community celebration,
ecosystem summit.

### Phase 5: Auto-Fix and IDE (v1.1+)

**Goal:** Auto-fix capabilities and IDE integration.

**Scope:**

- `--fix` and `--unsafe-fixes` flags.
- Auto-fix for safe-fixable rules.
- Integration with `behave-format` (format after fix).
- LSP implementation.
- VS Code extension.
- PyCharm plugin (community-maintained).
- Watch mode (`--watch`).
- HTML output format.
- JUnit XML output format.
- Custom output format plugins.
- Rule recommendations based on project analysis.
- Configuration auto-correction.
- Shell completion (bash, zsh, fish, powershell).

**Success criteria:**

- LSP provides sub-100ms feedback on file changes.
- VS Code extension has 1000+ installs.
- Auto-fix resolves 50%+ of reported diagnostics without manual
  intervention.

**Rationale:** Auto-fix and IDE integration are the most requested
features for any linter. They represent the next level of developer
experience.

**Future considerations:** AI-assisted rule suggestions, natural
language rule creation, project health dashboard.

### Phase 6: Ecosystem Expansion (v2.0+)

**Goal:** Broader ecosystem integration and advanced features.

**Scope:**

- Localization (message catalogs, community translations).
- Remote caching (share cache across CI runs).
- Distributed analysis for very large repositories.
- Cross-framework Gherkin linting (support non-Behave Gherkin files).
- BDD quality metrics and reporting.
- Integration with `behave-modern-report` (lint results in HTML
  reports).
- Custom diagnostic types (hints, metrics).
- Rule marketplace.
- Ecosystem governance model.

**Success criteria:**

- Translations available in 5+ languages.
- Remote caching reduces CI time by 50%+ for large projects.
- Cross-framework support enables linting of Cucumber Python
  projects.

**Rationale:** Ecosystem expansion positions behave-lint as the
central hub for BDD quality in the Python ecosystem and beyond.

**Future considerations:** BDD quality summit, ecosystem
certification program, academic research collaboration.

---

## Appendix A: Rule ID Convention

| Prefix | Source | Example |
|--------|--------|---------|
| `B` | behave-lint built-in rules | `BC001` (Correctness #001) |
| `B000` | Reserved for parse errors | `B000` (parse error) |
| `<custom>` | Plugin rules | `ACME001` (ACME plugin #001) |

Category codes: `C` (Correctness), `S` (Style), `X` (Complexity),
`K` (Consistency), `P` (Pedantic), `D` (Step Definitions).

## Appendix B: Configuration Schema Summary

```toml
[tool.behave-lint]
# Rule selection
select = ["BC001", "BS001"]          # Enable specific rules
ignore = ["BX001"]                    # Disable specific rules
severity = { BC001 = "error", BS001 = "warning" }  # Override severity

# Rule parameters
[tool.behave-lint.rules.BX001]
max-steps = 10                        # Max steps per scenario

[tool.behave-lint.rules.BX002]
max-scenarios = 50                    # Max scenarios per feature

# Output
output = "console"                    # Default output format
output-file = ""                      # Default output file (stdout)

# Paths
paths = ["features/"]                 # Default paths to lint
step-definitions = "features/steps/"  # Step definitions directory

# Cache
cache = true                          # Enable caching
cache-dir = ".behave-lint-cache"      # Cache directory

# Plugins
[tool.behave-lint.plugins]
"my-plugin" = { enabled = true }      # Enable/disable plugins
```

## Appendix C: Glossary

| Term | Definition |
|------|------------|
| **Behave** | A Python BDD framework for writing tests in Gherkin syntax. |
| **Gherkin** | A structured language for writing executable specifications, using Given/When/Then syntax. |
| **Feature file** | A `.feature` file containing Gherkin specifications. |
| **Step definition** | Python code that implements a Gherkin step using `@given`, `@when`, `@then`, or `@step` decorators. |
| **behave-model** | The canonical domain model for Behave projects, providing parsing, traversal, and validation. |
| **behave-format** | The opinionated formatter for Behave `.feature` files. |
| **Diagnostic** | A single issue reported by behave-lint, containing rule ID, severity, message, and location. |
| **Rule** | A single check that detects a specific pattern or anti-pattern in feature files. |
| **Rule ID** | A stable, unique identifier for a rule (e.g., `BC001`). |
| **Severity** | The importance level of a diagnostic: error, warning, info, or off. |
| **Category** | A grouping of rules by concern: correctness, style, complexity, consistency, pedantic, step definitions. |
| **Plugin** | A separately distributed package that adds rules, output formats, or configuration options to behave-lint. |
| **Auto-fix** | A feature that automatically applies fixes for certain rules (future). |
| **LSP** | Language Server Protocol — a standard for editor/IDE integration. |
| **SARIF** | Static Analysis Results Interchange Format — a JSON-based standard for static analysis results. |
| **Pre-commit** | A framework for managing and maintaining multi-language pre-commit hooks. |
| **Semver** | Semantic Versioning — a versioning scheme that communicates breaking changes through version numbers. |
