# Roadmap

This document summarizes the implementation roadmap.

## Current Status

**Stable** — v2.4.0 released. 50 built-in rules across 9 categories
(correctness, style, complexity, consistency, pedantic, step definitions,
security, i18n, accessibility), auto-fix (14 rules), profiles, groups,
incremental cache, cookiecutter plugin template, watch mode, plugins,
reporters, Typer-based CLI, LSP server with diagnostics, quick fixes,
workspace config, and incremental sync. Available on PyPI.

## Milestones

| Milestone | Name | Status | Target Release |
|---|---|---|---|
| M1 | Foundation | Complete | 0.1.0-alpha |
| M2 | Core Engine | Complete | 0.1.0-alpha |
| M3 | Diagnostics | Complete | 0.2.0-alpha |
| M4 | CLI | Complete | 0.2.0-alpha |
| M5 | Configuration | Complete | 0.3.0-alpha |
| M6 | Rules SDK | Complete | 0.3.0-alpha |
| M7 | Built-in Rules | Complete | 0.5.0-beta |
| M8 | Reporters | Complete | 0.6.0-beta |
| M9 | Plugins | Complete | 0.7.0-beta |
| M10 | Auto-Fix | Complete | 0.8.0-beta |
| M11 | Documentation | Complete | 0.9.0-beta |
| M12 | v1.0 | Complete | 1.0.0 |
| M13 | CLI Typer Migration | Complete | 1.1.0 |
| M14 | Rule Groups | Complete | 1.5.0 |
| M15 | Incremental Cache | Complete | 1.6.0 |
| M16 | Cookiecutter Plugin Template | Complete | 1.7.0 |
| M17 | Pedantic Auto-Fixes | Complete | 1.8.0 |
| M18 | Watch Mode | Complete | 1.9.0 |
| M19 | LSP Server | Complete | 2.0.0 |
| M20 | LSP Quick Fixes & Workspace Config | Complete | 2.1.0–2.3.0 |
| M21 | New Rule Categories (Security, I18N, Accessibility) | Complete | 2.4.0 |

## Critical Path

```text
M1 → M2 → M6 → M7 → M10 → M12
```

## Release Timeline

- **Alpha (0.1–0.4):** Internal validation, architecture testing.
- **Beta (0.5–0.9):** Public releases, community feedback.
- **RC (0.99.x):** Feature-frozen, bug fixes only.
- **Stable (1.0.0):** First production release.
- **v1.1.0:** CLI migrated to Typer, documentation updated.

## Future (Post-v1.1)

- v1.2+: Profiles, groups, additional rules.
- v1.5+: More auto-fixes, incremental cache.
- v1.7+: Cookiecutter plugin template.
- v2.0+: LSP server, IDE extensions, watch mode, new categories.
  - v2.0.0: LSP server with real-time diagnostics.
  - v2.1.0: LSP codeAction quick fixes.
  - v2.2.0: LSP workspace configuration.
  - v2.3.0: LSP incremental document sync.
  - v2.4.0: Security, I18N, Accessibility rule categories (9 new rules).
- v3.0+: AI rule suggestions, rule marketplace, cloud rules.
- v4.0+: Industry packs, compliance packs.
- v5.0+: Certification packs, cross-runner support, AI rule engine.
