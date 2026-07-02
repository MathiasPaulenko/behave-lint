# VISION.md — behave-lint

> The definitive linting solution for the Behave BDD ecosystem.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Vision Statement](#2-vision-statement)
3. [Mission](#3-mission)
4. [Target Audience](#4-target-audience)
5. [Personas](#5-personas)
6. [Problems Solved](#6-problems-solved)
7. [Non-Goals](#7-non-goals)
8. [Product Philosophy](#8-product-philosophy)
9. [Guiding Principles](#9-guiding-principles)
10. [Ecosystem Positioning](#10-ecosystem-positioning)
11. [Relationship with behave-model](#11-relationship-with-behave-model)
12. [Relationship with behave-format](#12-relationship-with-behave-format)
13. [Relationship with Report Libraries](#13-relationship-with-report-libraries)
14. [Competitive Analysis](#14-competitive-analysis)
15. [Risks](#15-risks)
16. [Long-Term Roadmap](#16-long-term-roadmap)
17. [Success Metrics](#17-success-metrics)
18. [Acceptance Criteria](#18-acceptance-criteria)

---

## 1. Executive Summary

**behave-lint** is a fast, opinionated, extensible linter for Gherkin `.feature`
files and Behave test suites. It is the missing quality gate in the Behave
ecosystem — the tool that catches structural, semantic, and stylistic problems
in BDD specifications *before* they reach CI, code review, or production.

The Behave ecosystem already has a canonical domain model
(`behave-model`), an opinionated formatter (`behave-format`), and a suite of
modern report libraries (JSON, HTML, Markdown, Console). What it lacks is a
dedicated linter: a tool that analyzes the domain model and reports issues
with precise locations, clear messages, severity levels, and actionable
guidance.

`behave-lint` fills this gap. It consumes `behave-model` as its single source
of truth, runs a configurable set of rules against the parsed project tree,
and produces structured diagnostics suitable for human consumption, CI/CD
gating, and machine-readable reporting. It is designed to be as fast as
Ruff, as extensible as ESLint, as opinionated as Clippy, and as Pythonic as
the ecosystem it serves.

The project is open source, MIT-licensed, and built to be the definitive
linting solution for anyone using Behave and Gherkin in professional
environments.

---

## 2. Vision Statement

> **To make every Behave test suite clean, consistent, and maintainable by
> providing the fastest, most extensible linter for Gherkin — one that every
> team adopts by default and every contributor trusts.**

We envision a future where running `behave-lint` is as automatic and expected
as running `ruff check` on Python code or `gofmt` on Go code. Where CI
pipelines fail on malformed Gherkin before a human ever reviews it. Where
custom rules are as easy to write as a Python function. And where the Behave
ecosystem has a quality toolchain that rivals any language community.

---

## 3. Mission

The mission of `behave-lint` is to:

- **Detect** structural, semantic, and stylistic issues in Gherkin feature
  files and Behave test suites with high precision and zero false positives
  by default.
- **Enforce** team conventions and best practices through configurable rules
  that are opinionated out of the box but adaptable to any project.
- **Integrate** seamlessly with the existing Behave ecosystem —
  `behave-model`, `behave-format`, and all report libraries — without
  duplicating parsing, formatting, or reporting logic.
- **Empower** teams to write custom rules with minimal boilerplate, enabling
  domain-specific quality gates without forking the project.
- **Operate** at the speed of modern CI/CD — sub-second on typical projects,
  fast enough to run on every commit, every push, and every PR.

---

## 4. Target Audience

`behave-lint` targets:

- **QA engineers and automation teams** using Behave for BDD who need to
  maintain large suites of `.feature` files across multiple teams and
  repositories.
- **Development teams practicing BDD** who want their Gherkin specifications
  to be as clean and maintainable as their production code.
- **Open source maintainers** in the Behave ecosystem who need a reliable
  quality gate for community-contributed feature files.
- **DevOps and platform engineers** who need CI-integrated quality gates with
  structured output, exit codes, and machine-readable formats.
- **Technical leads and architects** who want to enforce organizational
  standards (naming conventions, tag taxonomies, step reuse policies) across
  BDD projects.

---

## 5. Personas

### Persona 1: Marta — QA Automation Lead

Marta leads a team of 8 QA engineers maintaining 2,000+ scenarios across 15
repositories. She needs consistent naming conventions, tag taxonomies, and
step reuse patterns enforced across all projects. She wants a linter that
runs in CI, fails on violations, and produces a report her team can act on.
She does not want to write custom parsers — she wants to write rules.

**Needs:** CI integration, configurable rules, tag taxonomy enforcement,
duplicate step detection, clear reporting, fast execution.

### Persona 2: David — Backend Developer

David writes features alongside code. He wants instant feedback in his
editor when he writes a malformed scenario, uses a vague step, or forgets a
tag. He wants the linter to be as fast as his IDE's Python linter —
sub-100ms on a single file. He does not want to read a 50-page
configuration manual.

**Needs:** IDE integration (or at least fast CLI), sensible defaults, zero
configuration to start, clear error messages with suggestions.

### Persona 3: Priya — DevOps Engineer

Priya manages CI/CD pipelines for 30+ projects using Behave. She needs a
linter that produces machine-readable output (JSON, SARIF), integrates with
GitHub Actions / GitLab CI, and gates merges on quality. She needs
deterministic behavior, clear exit codes, and the ability to run the linter
in parallel with tests.

**Needs:** SARIF output, JSON output, CI-friendly exit codes, parallel
execution, GitHub Actions integration, caching.

### Persona 4: Kenji — Open Source Maintainer

Kenji maintains a Behave-related open source project. He receives
community-contributed feature files of varying quality. He wants a linter
that enforces his project's conventions, is easy for contributors to run
locally, and provides clear guidance in PR reviews. He wants to ship custom
rules as a plugin that contributors install automatically.

**Needs:** Plugin system, custom rule distribution, pre-commit hooks,
contributor-friendly documentation, rule documentation generation.

### Persona 5: Elena — BDD Coach and Consultant

Elena works with multiple organizations adopting BDD. She needs to express
each client's unique conventions as rules: specific Given/When/Then
patterns, mandatory tags per scenario type, maximum step count per
scenario, business-readable step language. She needs a rule SDK that lets
her write and distribute custom rules without patching the linter itself.

**Needs:** Custom rule SDK, rule packages, per-project configuration,
rule documentation, easy onboarding for new teams.

---

## 6. Problems Solved

### 6.1 No Canonical Linter Exists for Behave

The Behave ecosystem has no dedicated linter. Teams either rely on ad-hoc
scripts, manual code review, or simply tolerate inconsistent feature files.
This leads to quality drift over time.

**behave-lint** provides a purpose-built linter with a comprehensive rule
set that covers the most common Gherkin quality issues out of the box.

### 6.2 Inconsistent Feature Files Across Teams

Without enforcement, feature files diverge: different naming conventions,
tag usage, step phrasing, scenario structure. This makes suites harder to
maintain, harder to search, and harder to reuse.

**behave-lint** enforces consistency through configurable rules that can be
checked into version control alongside the project.

### 6.3 Gherkin Anti-Patterns Go Undetected

Common anti-patterns — empty scenarios, duplicate scenario names, missing
Background, overly long scenarios, vague step text, unused tags, orphaned
examples — are easy to introduce and hard to catch in review.

**behave-lint** detects these anti-patterns with precise location
information and actionable messages.

### 6.4 No Quality Gate for CI/CD

Teams using Behave in CI lack a quality gate for their specifications. Tests
may pass, but the specifications themselves may be malformed, inconsistent,
or incomplete.

**behave-lint** provides CI-friendly output (exit codes, JSON, SARIF), runs
in seconds, and integrates with any CI provider.

### 6.5 Custom Rules Require Forking

When teams need domain-specific rules (e.g., "all `@smoke` scenarios must
have fewer than 5 steps"), they typically write one-off scripts that are
not reusable, not shared, and not maintained.

**behave-lint** provides a rule SDK and plugin system that lets teams write,
package, and distribute custom rules without forking the project.

### 6.6 Step Definitions Drift from Feature Files

Step definitions in Python can drift from the steps used in feature files —
unused step definitions, undefined steps, inconsistent parameter patterns.

**behave-lint** cross-references feature files with step definitions to
detect drift, unused definitions, and undefined steps.

---

## 7. Non-Goals

To maintain focus and avoid scope creep, the following are explicitly
**non-goals** for `behave-lint`:

- **Not a formatter.** `behave-format` is the formatter. `behave-lint` does
  not write files, does not modify whitespace, does not sort tags. It
  detects issues; it does not fix them (auto-fix is a future goal, not a
  v1 goal).
- **Not a parser.** `behave-model` is the parser. `behave-lint` does not
  parse Gherkin. It consumes the parsed domain model.
- **Not a test runner.** `behave-lint` does not execute tests. It performs
  static analysis on the specification files and step definitions.
- **Not a report generator.** The report libraries handle reporting.
  `behave-lint` produces diagnostics, not visual reports.
- **Not a general-purpose Gherkin linter.** While the rules are Gherkin-
  aware, the tool is designed for the Behave ecosystem specifically. It is
  not a generic Cucumber/Gherkin linter (though it may inspire one).
- **Not a style enforcer for Python code.** Ruff, Black, and mypy handle
  Python code quality. `behave-lint` is concerned with `.feature` files and
  their relationship to step definitions.
- **Not an AI-powered tool (initially).** AI-assisted recommendations are a
  future vision item, not a launch feature.

---

## 8. Product Philosophy

### Extremely Fast

Speed is a feature. `behave-lint` must be fast enough to run on every file
save in an IDE, every commit in a pre-commit hook, and every push in CI
without noticeable delay. Target: sub-second on projects with hundreds of
feature files. This means efficient rule execution, minimal I/O, and no
unnecessary parsing (the model is already parsed by `behave-model`).

### Predictable

The same input must always produce the same output. Rules must be
deterministic. Configuration must be explicit and discoverable. No hidden
state, no network calls, no side effects. A developer who runs
`behave-lint` locally should get the same results as CI.

### Easy to Extend

Writing a custom rule should be as simple as writing a Python class with a
`check` method. The rule SDK should have minimal boilerplate, clear
documentation, and first-class support for common patterns (visitor-based,
query-based, cross-file). Plugins should be installable via `pip` and
auto-discovered.

### Production Ready

`behave-lint` is built for real-world use from day one: comprehensive test
coverage, semantic versioning, stable API, clear migration paths, and
professional documentation. It is not a prototype or an experiment.

### CI/CD Friendly

First-class CI integration is a requirement, not an afterthought. Exit
codes, JSON output, SARIF support, GitHub Actions integration, pre-commit
hooks, and caching are core features. The tool must work in containers,
on CI runners, and in ephemeral environments without special configuration.

### Plugin Ready

The plugin system is a first-class citizen, not a bolt-on. Plugins can
define rules, configuration schemas, and metadata. The plugin discovery
mechanism is based on Python entry points — the standard, well-understood
mechanism used by pytest, flake8, and other Python tools.

### Pythonic

`behave-lint` follows Python conventions: PEP 8, type hints, dataclasses,
context managers where appropriate, and a CLI that follows standard Python
tooling patterns. The API feels natural to Python developers. The
configuration uses `pyproject.toml` as the primary source, consistent with
modern Python tooling.

### Opinionated Where Appropriate

`behave-lint` ships with sensible defaults that work for the majority of
projects. Teams should be able to install it, run it, and get value
immediately without reading documentation. However, every rule is
configurable: severity can be changed, rules can be disabled, and custom
rules can be added. Opinionated but not dictatorial.

---

## 9. Guiding Principles

1. **Single source of truth.** `behave-model` is the canonical domain model.
   `behave-lint` never re-parses Gherkin. It operates on the `Project` tree
   produced by `behave-model`. This eliminates parsing duplication and
   ensures consistency across all ecosystem tools.

2. **Separation of concerns.** `behave-lint` detects. `behave-format`
   fixes. `behave-model` models. Report libraries report. Each tool does
   one thing well. No tool duplicates another's responsibility.

3. **Rules are data, not configuration.** Each rule carries its own
   metadata: name, description, severity default, rationale, and examples.
   This metadata drives documentation generation, IDE tooltips, and
   machine-readable output. Rules are self-describing.

4. **Diagnostics are structured.** Every diagnostic includes: rule ID,
   severity, message, file path, line number, column (if applicable), and
   optional fix suggestion. This structure is consistent across all output
   formats (text, JSON, SARIF).

5. **Zero false positives by default.** The default rule set must have
   near-zero false positives. Rules that are heuristic or opinion-based
   should be opt-in, not opt-out. Trust is hard to build and easy to lose.

6. **Configuration is code.** Configuration lives in `pyproject.toml`,
   follows standard Python tooling conventions, and is version-controlled.
   No hidden config files, no environment-dependent behavior.

7. **Documentation is generated, not hand-written.** Rule documentation is
   generated from rule metadata. This ensures documentation is always
   accurate, always up-to-date, and always available — in the CLI, in the
   docs site, and in IDE tooltips.

8. **Backward compatibility is sacred.** Rule additions are minor versions.
   Rule removals or behavior changes are major versions with migration
   guides. Configuration schemas are backward-compatible within a major
   version.

9. **Performance is a feature, not a metric.** If a feature makes the linter
   2x slower, it needs strong justification. Performance regressions are
   treated as bugs.

10. **Community-driven rule evolution.** New rules are proposed, discussed,
    and vetted through the project's contribution process. The default rule
    set evolves based on real-world usage, not theoretical purity.

---

## 10. Ecosystem Positioning

`behave-lint` is one tool in a cohesive ecosystem. Each tool has a clear,
non-overlapping responsibility:

```
                     ┌─────────────────┐
                     │  .feature files │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │  behave-model   │  ← Canonical domain model
                     │  (parse, query, │     Single source of truth
                     │   validate)     │
                     └────────┬────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
                    ▼         ▼         ▼
           ┌──────────┐ ┌──────────┐ ┌────────────────────┐
           │behave-   │ │behave-   │ │ behave-modern-     │
           │format    │ │lint      │ │ json-report        │
           │(format)  │ │(analyze) │ │ (execution model)  │
           └──────────┘ └─────┬────┘ └─────────┬──────────┘
                              │                │
                              ▼                ▼
                    ┌─────────────────┐  ┌──────────────────┐
                    │ Diagnostics     │  │ JSON / Cucumber  │
                    │ (text, JSON,    │  │ JSON             │
                    │  SARIF)         │  └────────┬─────────┘
                    └─────────────────┘           │
                                       ┌──────────┼──────────┐
                                       │          │          │
                                       ▼          ▼          ▼
                                 ┌──────┐  ┌──────┐  ┌──────┐
                                 │ HTML │  │  MD  │  │Console│
                                 │report│  │report│  │report │
                                 └──────┘  └──────┘  └──────┘
```

**The flow:**

1. `.feature` files are parsed by `behave-model` into a `Project` tree.
2. `behave-format` transforms the `Project` tree into formatted `.feature`
   files (deterministic, idempotent).
3. `behave-lint` analyzes the `Project` tree and produces diagnostics
   (errors, warnings, info).
4. When tests run, `behave-modern-json-report` captures execution results
   as a structured JSON model.
5. The JSON model is consumed by HTML, Markdown, and Console report
   formatters for human-readable output.

`behave-lint` operates at step 3 — **after parsing, before execution**. It
is a static analysis tool that runs without executing any tests. This makes
it fast, safe, and suitable for pre-commit hooks and early CI stages.

---

## 11. Relationship with behave-model

`behave-model` is the foundation of the entire ecosystem and the single
source of truth for `behave-lint`.

### What behave-lint consumes from behave-model

- **`Project`** — the root of the parsed domain model, containing all
  features, scenarios, steps, tags, tables, and metadata.
- **`load_project()` / `load_feature()`** — the parsing entry points.
  `behave-lint` calls these to load the project; it never parses Gherkin
  directly.
- **`Visitor` pattern** — `behave-lint` rules traverse the project tree
  using the visitor pattern provided by `behave-model`, ensuring
  consistent traversal semantics across all ecosystem tools.
- **`Query API`** — rules can use the query functions (`find_scenarios`,
  `find_steps`, `find_scenarios_with_tag`, etc.) to efficiently locate
  elements without manual tree traversal.
- **`ValidationIssue` / `ValidationRule` / `Validator`** — `behave-model`
  already provides a basic validation framework with 5 built-in rules.
  `behave-lint` extends this framework with a much larger rule set,
  richer diagnostics, configuration, and plugin support.

### What behave-lint does NOT duplicate

- **Parsing** — `behave-lint` never parses `.feature` files. It relies on
  `behave-model`'s parser (which wraps Behave's own parser).
- **Domain model** — `behave-lint` does not define its own `Feature`,
  `Scenario`, `Step`, etc. It uses `behave-model`'s dataclasses directly.
- **Basic validation** — `behave-lint` does not reimplement the 5 rules
  in `behave-model`. It may wrap or extend them, but the canonical
  implementations remain in `behave-model`.

### The boundary

`behave-model` provides the *mechanism* for validation (the `Validator`
class, `ValidationRule` base class, `ValidationIssue` dataclass).
`behave-lint` provides the *rules, configuration, CLI, and ecosystem*
that make validation practical and comprehensive.

In other words: `behave-model` defines *how* to validate;
`behave-lint` defines *what* to validate and *how to act on it*.

---

## 12. Relationship with behave-format

`behave-format` and `behave-lint` are complementary tools that share the
same domain model but serve different purposes.

| Aspect | behave-format | behave-lint |
|--------|---------------|-------------|
| Purpose | Format `.feature` files | Detect issues in `.feature` files |
| Action | Modifies files (in-place or `--check`) | Reports issues (no modification) |
| Output | Formatted `.feature` text | Diagnostics (text, JSON, SARIF) |
| Opinion | Strongly opinionated, minimal config | Opinionated defaults, highly configurable |
| Relationship to model | Consumes `Project`, produces text | Consumes `Project`, produces diagnostics |
| CI mode | `--check` (exit 1 if formatting needed) | `--ci` (exit 1 if errors found) |

### Non-overlapping responsibilities

`behave-format` handles *style* (whitespace, indentation, table alignment,
tag sorting). `behave-lint` handles *semantics and structure* (duplicate
names, missing tags, step reuse, anti-patterns, step definition drift).

There is a deliberate gray zone: some rules could be considered both style
and semantic (e.g., "scenarios should have a blank line before them"). The
principle is: **if `behave-format` can fix it automatically, it belongs in
`behave-format`. If it requires human judgment, it belongs in
`behave-lint`.**

### Recommended workflow

The recommended workflow for teams is:

1. Run `behave-format` to normalize formatting (automated, no judgment).
2. Run `behave-lint` to detect structural and semantic issues (requires
   human review).
3. Fix lint issues manually (or with future auto-fix).
4. Commit.

This mirrors the Python workflow: `black` (format) → `ruff` (lint) →
commit.

---

## 13. Relationship with Report Libraries

`behave-lint` is a static analysis tool and does not execute tests.
However, it integrates with the report ecosystem in several ways:

### 13.1 behave-modern-json-report

`behave-lint` can produce JSON output that follows a structured schema,
making it consumable by dashboards, analytics platforms, and custom
integrations. While `behave-modern-json-report` captures *execution*
results, `behave-lint` captures *static analysis* results. Together, they
provide a complete quality picture:

- **Static quality** (behave-lint): Is the specification well-structured?
- **Execution quality** (behave-modern-json-report): Did the tests pass?

A future integration could merge both reports into a unified quality
dashboard.

### 13.2 HTML Reports (behave-modern-report)

While `behave-lint` does not generate HTML reports itself, its JSON output
can be consumed by a future HTML renderer (or by `behave-modern-report`
via a plugin) to produce a visual lint report. This is a future vision
item, not a v1 feature.

### 13.3 Markdown Reports (behave-modern-md-report)

`behave-lint` can produce Markdown output suitable for GitHub Actions
summaries, PR comments, and wiki pages. This aligns with the ecosystem's
philosophy of CI-native, human-readable output.

### 13.4 Console Reports (behave-modern-console-report)

`behave-lint`'s default output is console-based, with colored diagnostics,
progress indicators, and a summary. While it does not use
`behave-modern-console-report` directly (as it does not execute tests),
it follows the same design philosophy: modern, readable, CI-friendly
terminal output.

---

## 14. Competitive Analysis

### 14.1 Ruff (Python)

**What makes it successful:**
Ruff replaced flake8, isort, pyupgrade, and dozens of other tools by being
10-100x faster (written in Rust), having zero configuration by default,
and providing both linting and formatting. Its success comes from:
- Extreme speed (Rust implementation)
- Unified tooling (lint + format in one binary)
- Rule parity with established tools (flake8 plugins)
- Excellent documentation and rule catalog
- Active community and rapid adoption

**What should inspire behave-lint:**
- Speed as a primary feature — sub-second on large projects
- Rule catalog with clear IDs, descriptions, and examples
- Zero-config defaults that work immediately
- `--fix` mode for rules that can be auto-fixed
- Unified tooling (lint + future auto-fix in one tool)
- Rule selection/deselection by ID or category

**What should NOT be copied:**
- Rewriting in Rust — `behave-lint` should be pure Python to stay
  accessible to the Behave community (which is Python). Performance is
  achieved through efficient algorithms, not language choice.
- Competing with the formatter — Ruff's formatter competes with Black.
  `behave-lint` should not compete with `behave-format`. Clear separation
  of concerns.
- Overwhelming rule count — Ruff has 800+ rules. `behave-lint` should
  start with a focused, high-value set and grow based on demand.

### 14.2 ESLint (JavaScript)

**What makes it successful:**
ESLint is the most extensible linter in any language community. Its success
comes from:
- Plugin architecture that allows anyone to publish rules
- Per-rule configuration (error, warn, off)
- `--fix` for auto-fixable rules
- Inline disable/enable comments
- Rich ecosystem of plugins (TypeScript, React, Vue, etc.)
- Shareable configurations (presets)

**What should inspire behave-lint:**
- Plugin system based on standard package distribution (pip / entry points)
- Per-rule severity configuration (error, warning, info, off)
- Inline disable comments in `.feature` files (e.g., `# behave-lint:
  disable=rule-name`)
- Shareable configurations (presets that teams can publish and reuse)
- Rule metadata that drives documentation and IDE integration

**What should NOT be copied:**
- Configuration complexity — ESLint's configuration has become notoriously
  complex (eslintrc, flat config, overrides). `behave-lint` should use
  a single, simple `pyproject.toml` section.
- Runtime performance — ESLint is slow on large projects. `behave-lint`
  must be fast from the start.
- JavaScript-specific patterns — ESLint's AST-based rules are powerful but
  tightly coupled to JavaScript's AST. `behave-lint` operates on a domain
  model, not an AST, which is simpler and more stable.

### 14.3 Clippy (Rust)

**What makes it successful:**
Clippy is beloved by the Rust community for being opinionated, pedantic
when desired, and genuinely helpful. Its success comes from:
- Tight integration with the compiler (uses the same AST)
- Pedantic groups (style, correctness, complexity, perf, pedantic)
- Clear, educational error messages that teach Rust best practices
- Strong defaults that improve code quality without configuration
- Community-driven rule proposals

**What should inspire behave-lint:**
- Rule groups/categories (correctness, style, complexity, pedantic)
- Educational messages that explain *why* a rule exists, not just *what*
  is wrong
- Strong defaults that work without configuration
- Pedantic mode for teams that want stricter enforcement
- Community-driven rule evolution

**What should NOT be copied:**
- Compiler integration — `behave-lint` is not integrated with Behave's
  runtime. It is a standalone tool. Tight coupling to a specific runtime
  would limit portability.
- Rust-specific pedantry — Clippy's rules are deeply tied to Rust's
  semantics. `behave-lint`'s rules should be tied to Gherkin/Behave
  semantics, not general programming principles.
- Aggressive defaults — Clippy can be overwhelming for beginners.
  `behave-lint` should be approachable by default, with pedantic rules
  as opt-in.

### 14.4 SonarLint (Multi-language)

**What makes it successful:**
SonarLint provides deep semantic analysis across many languages, with IDE
integration and connection to SonarQube/SonarCloud for team-wide quality
tracking. Its success comes from:
- IDE integration (real-time feedback as you type)
- Quality gates and technical debt tracking
- Security-focused rules (CVE detection, hotspots)
- Team-wide quality dashboards
- Cross-file analysis

**What should inspire behave-lint:**
- IDE integration as a first-class goal (LSP support in the roadmap)
- Quality gate concept (pass/fail thresholds)
- Technical debt tracking (optional, via JSON output + external tools)
- Cross-file analysis (detecting duplicate steps across features)

**What should NOT be copied:**
- Heavyweight platform dependency — SonarLint requires SonarQube/
  SonarCloud for team features. `behave-lint` must work standalone.
- Security scanning — `behave-lint` is not a security tool. Gherkin
  files are specifications, not executable code.
- Proprietary ecosystem — SonarLint's best features are locked behind
  commercial products. `behave-lint` is open source, period.
- Rule complexity — SonarLint rules can be extremely complex (data flow
  analysis, taint tracking). `behave-lint` rules should be simple,
  focused, and fast.

### 14.5 golangci-lint (Go)

**What makes it successful:**
golangci-lint is a meta-linter that runs multiple Go linters in parallel,
aggregates results, and provides a unified configuration. Its success
comes from:
- Aggregation of multiple linters in one tool
- Parallel execution for speed
- Unified configuration and output
- Pre-configured presets (e.g., "enable-all", "disable-all")
- CI integration with GitHub Actions, GitLab CI
- Caching of results for incremental runs

**What should inspire behave-lint:**
- Parallel rule execution for speed
- Caching for incremental runs (only re-lint changed files)
- Presets for easy configuration ("strict", "relaxed", "minimal")
- GitHub Actions integration as a first-class feature
- Unified output format regardless of rule source

**What should NOT be copied:**
- Meta-linter approach — `behave-lint` is not a wrapper around multiple
  linters. It is a single linter with its own rule set. The complexity of
  managing multiple external linters is not justified for the Behave
  ecosystem.
- Go-specific tooling — golangci-lint's configuration and execution model
  is deeply tied to Go's toolchain. `behave-lint` should follow Python
  conventions.
- Configuration complexity — golangci-lint's configuration can be
  overwhelming. `behave-lint` should have a flat, simple configuration
  schema.

### Competitive Analysis Summary

| Feature | Ruff | ESLint | Clippy | SonarLint | golangci-lint | behave-lint (target) |
|---------|------|--------|--------|-----------|---------------|---------------------|
| Speed | Extreme (Rust) | Slow | Fast | Medium | Fast | Fast (Python) |
| Extensibility | Moderate | Extreme | Low | Moderate | High (meta) | High (plugins) |
| Auto-fix | Yes | Yes | No | Limited | Varies | Future |
| IDE integration | Yes (via LSP) | Yes (native) | Yes (compiler) | Yes (native) | No | Future (LSP) |
| CI integration | Yes | Yes | Yes | Yes | Yes | Yes (v1) |
| Configuration | Simple | Complex | Simple | Medium | Complex | Simple |
| Opinionated defaults | Yes | No | Yes | No | No | Yes |
| Rule documentation | Excellent | Good | Educational | Good | Varies | Generated |
| Plugin system | No | Yes | No | Yes | Yes (meta) | Yes (v1) |
| SARIF output | No | Yes | No | Yes | No | Future |
| Language | Rust | JS | Rust | Java | Go | Python |

---

## 15. Risks

### 15.1 Adoption Risk

The Behave community is smaller than the Python, JavaScript, or Go
communities. Adoption may be slow if teams do not see the value of linting
Gherkin files.

**Mitigation:** Ship with immediately useful defaults. Provide clear
before/after examples. Integrate with the existing ecosystem seamlessly.
Target the most common pain points first (duplicate names, empty scenarios,
missing tags).

### 15.2 Scope Creep

There is a temptation to add formatting, auto-fixing, test generation, and
AI features too early. This dilutes focus and delays the v1 release.

**Mitigation:** Clearly defined non-goals. Phased roadmap. Each feature
must justify its inclusion against the core mission of detecting issues.

### 15.3 Rule Quality

Poorly written rules (false positives, unclear messages, inconsistent
behavior) erode trust quickly. One bad rule can cause a team to abandon
the tool.

**Mitigation:** Every rule must have tests, documentation, and a
justification. Rules are reviewed before inclusion in the default set.
Heuristic rules are opt-in. A "stable" rule set is clearly distinguished
from "experimental" rules.

### 15.4 Ecosystem Coupling

`behave-lint` depends on `behave-model`. If `behave-model` changes its API
or domain model, `behave-lint` must adapt. This coupling is intentional
but creates maintenance overhead.

**Mitigation:** Depend on `behave-model` with a version range, not a
floating latest. Pin major versions. Maintain a compatibility matrix.
Participate in `behave-model`'s development to anticipate breaking changes.

### 15.5 Performance Regression

As the rule set grows, performance may degrade. Rules that seem fast
individually can be slow in aggregate, especially on large projects.

**Mitigation:** Performance benchmarks in CI. Rule execution profiling.
Parallel rule execution. Caching of parsed models. Performance
regressions are treated as bugs and block releases.

### 15.6 Configuration Fragmentation

If teams use vastly different configurations, the ecosystem fragments and
rules become less useful as shared knowledge.

**Mitigation:** Ship opinionated presets. Encourage teams to start with
defaults and diverge only when necessary. Document the rationale for each
default so teams understand what they are changing.

### 15.7 Behave Itself Becoming Inactive

Behave (the framework) has a slow release cadence. If Behave becomes
inactive or abandoned, the entire ecosystem loses momentum.

**Mitigation:** `behave-lint` depends on `behave-model`, not directly on
Behave. `behave-model` wraps Behave's parser but could be adapted to
other Gherkin parsers if needed. The domain model is the abstraction
layer that insulates the ecosystem from Behave's development pace.

---

## 16. Long-Term Roadmap

### Phase 1: Foundation (v1.0)

- Core linter engine consuming `behave-model.Project`
- 15-20 high-value built-in rules covering:
  - Duplicate scenario/feature names
  - Empty scenarios and features
  - Invalid tables (column count mismatches)
  - Missing Background when scenarios share Given steps
  - Tag taxonomy enforcement (required tags, forbidden tags)
  - Step count limits (scenarios too long)
  - Vague step detection (steps without Given/When/Then keywords)
  - Unused tags (tags defined but never referenced)
  - Orphaned examples (Examples tables without matching placeholders)
  - Step definition drift (undefined steps, unused step definitions)
- CLI with text, JSON, and GitHub Actions output
- `pyproject.toml` configuration
- Per-rule severity configuration
- Exit codes for CI integration
- Pre-commit hook support
- Comprehensive test suite
- Documentation site with generated rule catalog

### Phase 2: Extensibility (v1.x)

- Plugin system via Python entry points
- Custom rule SDK with documentation and examples
- Rule presets (strict, relaxed, minimal, pedantic)
- Inline disable/enable comments in `.feature` files
- Rule documentation generation (Markdown + HTML)
- `--explain` flag for detailed rule rationale
- Caching for incremental runs (only re-lint changed files)
- Parallel rule execution

### Phase 3: CI/CD Deep Integration (v2.0)

- SARIF output for GitHub Code Scanning integration
- GitHub Actions action (one-step setup)
- GitLab CI template
- Quality gates (fail on N+ warnings, fail on specific rules)
- Trend tracking (compare lint results across commits)
- PR comment bot (inline diagnostics on PR diffs)
- Badge generation for README files

### Phase 4: IDE Integration (v2.x)

- LSP (Language Server Protocol) implementation
- VS Code extension
- PyCharm/IntelliJ plugin (via LSP)
- Real-time linting on file save
- Quick-fix suggestions in editor
- Rule documentation on hover
- Inline disable/enable in editor

### Phase 5: Auto-Fix (v3.0)

- `--fix` mode for auto-fixable rules
- Safe fixes only (never change semantics)
- Diff preview before applying fixes
- Integration with `behave-format` (format after fix)
- Fix report (what was changed, what was not, why)

### Phase 6: AI-Assisted Recommendations (v3.x+)

- AI-powered step suggestions (suggest clearer phrasing for vague steps)
- Duplicate scenario detection beyond exact name matching (semantic
  similarity)
- Smart tag recommendations based on scenario content
- Natural language rule description (describe a rule in English, get a
  rule implementation)
- This phase is exploratory and depends on the maturity of AI tooling
  and community interest

### Phase 7: Rule Marketplace (v4.0+)

- Centralized registry for community-published rule packages
- `behave-lint install rules-package-name` command
- Rule package metadata (author, version, compatibility, description)
- Rating and review system
- Curated "official" rule packages for common domains (API testing,
  UI testing, mobile testing, etc.)

### Phase 8: Custom Rule SDK (ongoing)

- Declarative rule definition (YAML or TOML-based rules for simple
  patterns)
- Visual rule builder (web UI for non-developers)
- Rule testing framework (test custom rules with fixture files)
- Rule debugging tools (trace rule execution, inspect intermediate state)
- Rule migration tools (update custom rules when the SDK evolves)

---

## 17. Success Metrics

### Adoption Metrics

- **PyPI downloads:** 10,000+ monthly downloads within 12 months of v1.0
- **GitHub stars:** 500+ within 12 months of v1.0
- **Contributors:** 10+ external contributors within 12 months
- **Plugin packages:** 5+ community-published rule packages within
  18 months

### Quality Metrics

- **False positive rate:** < 1% for default rule set (measured by
  user-reported issues)
- **Performance:** < 1 second on a project with 500 feature files
- **Test coverage:** > 95% for the linter engine and built-in rules
- **Documentation coverage:** 100% of rules documented with examples

### Ecosystem Metrics

- **behave-model compatibility:** 100% compatibility with the latest
  `behave-model` release within 30 days of its release
- **behave-format integration:** Documented workflow for using both tools
  together within v1.0
- **CI integration:** Official GitHub Actions action within v2.0
- **IDE support:** LSP implementation within v2.x

### Community Metrics

- **Issue response time:** < 48 hours for bug reports
- **PR review time:** < 7 days for community PRs
- **Release cadence:** Monthly minor releases, quarterly feature releases
- **Documentation quality:** < 5 documentation-related issues per quarter

---

## 18. Acceptance Criteria

The VISION.md document is accepted when:

1. **All 18 sections are present and complete.** Each section addresses its
   topic with sufficient depth and specificity for an open source product
   vision document.

2. **The document is implementation agnostic.** It describes *what* the
   product is and *why* it exists, not *how* it is implemented. No code,
   no API signatures, no class diagrams.

3. **Every major decision is justified.** Non-goals explain what is
   excluded and why. Philosophy choices explain why they matter.
   Competitive analysis explains what to adopt and what to avoid.

4. **The ecosystem relationships are clear.** The boundaries between
   `behave-lint`, `behave-model`, `behave-format`, and the report libraries
   are explicitly defined. The architecture diagram shows the data flow.

5. **The competitive analysis covers all five tools** (Ruff, ESLint,
   Clippy, SonarLint, golangci-lint) with success factors, inspirations,
   and anti-patterns for each.

6. **The roadmap is phased and realistic.** Each phase has a clear theme
   and scope. Future vision items (auto-fix, SARIF, IDE, LSP, AI, rule
   marketplace, custom rule SDK) are described without implementation
   detail.

7. **The document reads professionally.** It is suitable for presentation
   to stakeholders, inclusion in a project README, and use as a reference
   for contributors and users.

8. **The document is detailed.** It exceeds 4,000 words and provides
   sufficient context for a new contributor to understand the project's
   direction and make informed decisions.

9. **The personas are realistic and diverse.** They represent different
   roles, team sizes, and use cases within the Behave ecosystem.

10. **The risks are honest and mitigated.** They acknowledge real
    challenges (adoption, scope creep, ecosystem coupling, performance)
    and provide concrete mitigation strategies.

---

*This document is the product vision for behave-lint. It is a living
document that evolves as the project grows and the ecosystem matures.*
