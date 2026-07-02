# Changelog

All notable changes to behave-lint will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
