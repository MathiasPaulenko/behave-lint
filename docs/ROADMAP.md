# Roadmap

This document summarizes the implementation roadmap.

## Current Status

**Stable** — v1.1.0 released. 41 built-in rules, auto-fix, plugins,
reporters, Typer-based CLI, and full documentation. Available on PyPI.

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

- v1.2+: Profiles, groups, additional rules, cookiecutter template.
- v2.0+: LSP server, IDE extensions, watch mode, new categories.
- v3.0+: AI rule suggestions, rule marketplace, cloud rules.
- v4.0+: Industry packs, compliance packs.
- v5.0+: Certification packs, cross-runner support, AI rule engine.
