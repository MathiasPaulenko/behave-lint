# Changelog

All notable changes to behave-lint will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.6.0] - 2025-07-03

### Added

- Incremental cache — skip rule execution for unchanged files.
  SHA-256 content hashing + config hash for automatic invalidation.
- New `behave_lint.cache` module with `CacheManager`.
- `--no-cache` and `--clear-cache` CLI flags now functional.
- `cache_hits` and `cache_misses` populated in `LintSummary`.
- Documentation: `docs/usage/cache.md`.

## [1.5.1] - 2025-07-03

### Added

- Auto-fix metadata declared for BS001 (tag casing), BS006 (step keyword
  casing), BS007 (trailing whitespace), BS008 (tab indentation),
  BC004 (invalid tag syntax), BD004 (step parameter convention),
  BD005 (step trailing punctuation) — all SAFE.
- Auto-fix support for BS004 (background name) — UNSAFE, inserts
  `Background: Common setup` as a placeholder name.
- Tests for all newly declared auto-fix metadata and BS004 fix.

### Fixed

- Documentation workflow: duplicate `github-pages` artifact caused by
  both `build` and `deploy` jobs uploading. Now only `build` uploads.
- Added `workflow_dispatch` trigger to docs workflow for manual runs.

## [1.5.0] - 2025-07-03

### Added

- Rule groups — select rules by category or tag via `--group` CLI flag,
  `group` config key, or `BEHAVE_LINT_GROUP` env var.
- 5 category-based groups: `correctness`, `style`, `pedantic`,
  `step-definitions`, `consistency`.
- 10 tag-based groups: `naming`, `tags`, `steps`, `background`,
  `description`, `documentation`, `formatting`, `examples`,
  `scenarios`, `readability`.
- Groups are additive — they merge with explicit `--select` rules and
    can be combined with profiles.
- New `group` field in `Config` and `CLIArgs`.
- New `behave_lint.configuration.groups` module with group definitions
  and validation.
- Documentation: `docs/usage/groups.md`.

## [1.4.0] - 2025-07-03

### Added

- Auto-fix support for BS002 (keyword ordering) — reorders steps to
  Given-When-Then order (UNSAFE, requires `--unsafe-fixes`).
- Auto-fix support for BS003 (step phrasing) — replaces first-person
  "I" with "the user", handling common conjugations like "I am" →
  "the user is" and "I've" → "the user has" (SAFE, `--fix`).
- Auto-fix support for BS005 (feature description) — inserts a
  template description ("As a [role] / I want to [action] / So that
  [benefit]") after the Feature line (UNSAFE, requires
  `--unsafe-fixes`).
- Updated `auto_fix` metadata for BS002, BS003, and BS005 rules.

## [1.3.2] - 2025-07-03

### Fixed

- Fix `test_profile_shown_in_help` failing on CI by stripping ANSI codes
  and adding direct command parameter verification.

## [1.3.1] - 2025-07-03

### Fixed

- Fix `test_profile_shown_in_help` failing on CI due to ANSI color codes
  in Typer's Rich-rendered help output (use `color=False` in CliRunner).

## [1.3.0] - 2025-07-03

### Added

- **Profiles/Presets** — built-in rule profiles for common use cases:
  - `recommended` — all rules except pedantic (34 rules).
  - `strict` — all rules including pedantic (41 rules).
  - `minimal` — only correctness and step-definition rules (15 rules).
- New `--profile` CLI flag.
- New `profile` config key in `pyproject.toml`.
- New `BEHAVE_LINT_PROFILE` environment variable.
- New [Profiles guide](usage/profiles.md) in documentation.

## [1.2.1] - 2025-07-03

### Fixed

- Apply `ruff format` to new rule files (fixes CI format check).

## [1.2.0] - 2025-07-03

### Added

- **10 new built-in rules** (31 → 41 total):
  - BC007: `empty-scenario` — detects scenarios with no steps.
  - BC008: `unused-outline-placeholder` — detects unused Examples columns.
  - BC009: `undefined-outline-placeholder` — detects undefined `<param>` placeholders.
  - BC010: `duplicate-examples-name` — detects duplicate Examples names.
  - BS006: `step-keyword-casing` — enforces capitalized step keywords (auto-fixable).
  - BS007: `trailing-whitespace` — detects trailing whitespace (auto-fixable).
  - BS008: `tab-indentation` — detects tab indentation (auto-fixable).
  - BX006: `feature-file-too-long` — detects overly long feature files.
  - BP006: `missing-feature-description` — detects features without a description.
  - BP007: `scenario-without-assertion` — detects scenarios without a `Then` step.

## [1.1.0] - 2025-07-02

### Changed

- CLI migrated from `argparse` to `Typer` for a richer help experience
  with coloured output, progressive disclosure, and better error messages.
- `CLIArgs` dataclass retained for backward compatibility; `parse_args`
  and `create_parser` removed in favour of the Typer `app` object.
- `--json` and `--sarif` shortcut flags removed — use `--output json` and
  `--output sarif` instead.
- Exit code for invalid CLI flags now correctly returns `2` (config error)
  instead of `3` (internal error).

### Added

- `typer>=0.12` as a runtime dependency.
- `run_lint()` public function in `behave_lint.cli.coordinator` for
  programmatic invocation without going through `main()`.
- `FailOn` and `OutputFormat` `StrEnum` types exported from
  `behave_lint.cli.parser`.

### Removed

- `create_parser()` function from `behave_lint.cli.parser`.
- `parse_args()` function from `behave_lint.cli.parser`.
- `--json` shortcut flag (use `--output json`).
- `--sarif` shortcut flag (use `--output sarif`).

## [1.0.0] - 2025-07-02

### Added

- Repository bootstrap with complete project skeleton.
- `pyproject.toml` with PEP 621 metadata, hatchling build backend,
  and tooling configuration (Ruff, Mypy, Pytest, Coverage).
- Package skeleton with all subpackages per REPOSITORY_DESIGN.md.
- Test skeleton with all test types (unit, integration, golden,
  snapshot, performance, regression, architecture).
- GitHub workflows for CI, documentation, release, and security.
- MkDocs Material documentation site configuration.
- Pre-commit hooks (Ruff, Mypy, standard hooks).
- Contributing guide, code of conduct, security policy.
- Supported versions and roadmap documents.
- Core domain models: `Diagnostic`, `Severity`, `Category`, `Config`.
- Rule engine with `RuleExecutor`, `LintEngine`, `RuleRegistry`.
- CLI with `--select`, `--ignore`, `--fail-on`, `--output`, `--config`.
- 31 built-in rules across 6 categories (BC, BD, BK, BX, BS, BP).
- 5 output formats: console, JSON, SARIF, Markdown, GitHub Actions.
- Plugin system with entry-point discovery and isolation.
- Auto-fix infrastructure with `FixCoordinator` and conflict resolution.
- 4 safe auto-fixes: BC004, BD004, BD005, BS001.
- Full documentation: Getting Started, CLI Reference, Configuration,
  Auto-Fix guide, Rules catalog, Guides (CI/CD, pre-commit, custom
  rules, plugin development).
- Runnable example projects: basic-usage, auto-fix, ci-cd, custom-rules.
- Performance benchmark tests with fixture generation (10/100/1000 files).
- Nightly CI workflow for performance benchmarks.

### Changed

- Version bumped from 0.1.0 to 1.0.0.
- Development status classifier updated from Pre-Alpha to Beta.
- Documentation URL updated to GitHub Pages site.
- Authors updated to include project maintainer.

### Removed

- `behave-lint.toml` configuration file support (use `pyproject.toml`
  `[tool.behave-lint]` section instead).

## [0.1.0] - 2025-01-15

### Added

- Initial repository setup.
- Foundation milestone (M1) preparation.
