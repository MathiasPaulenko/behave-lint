# Rules Reference

`behave-lint` ships with **50 built-in rules** across 9 categories.

## Categories

| Prefix | Category | Default Severity | Rules |
|--------|----------|-----------------|-------|
| BC | [Correctness](correctness.md) | ERROR | 10 |
| BD | [Step Definitions](step-definitions.md) | WARNING | 5 |
| BK | [Consistency](consistency.md) | WARNING/INFO | 5 |
| BX | [Complexity](complexity.md) | WARNING | 6 |
| BS | [Style](style.md) | WARNING | 8 |
| BP | [Pedantic](pedantic.md) | INFO | 7 |
| BSEC | [Security](security.md) | ERROR/WARNING | 3 |
| BI18N | [I18N](i18n.md) | WARNING/INFO | 3 |
| BACC | [Accessibility](accessibility.md) | WARNING | 3 |

## Auto-fixable rules

| Rule | Fix | Safety |
|------|-----|--------|
| BC004 | Replace invalid tag characters with `_` | Safe |
| BD004 | Convert `{param}` → `<param>` | Safe |
| BD005 | Remove trailing punctuation | Safe |
| BS001 | Convert tags to `snake_case` | Safe |
| BS006 | Capitalize step keywords | Safe |
| BS007 | Remove trailing whitespace | Safe |
| BS008 | Convert tabs to spaces | Safe |

See the [Auto-Fix guide](../usage/auto-fix.md) for details.

## Rule IDs

Rule IDs use a prefix followed by a three-digit number:

- **BC** — Correctness (definitively wrong structures)
- **BD** — Step Definitions (step pattern issues)
- **BK** — Consistency (cross-scenario consistency)
- **BX** — Complexity (overly complex features)
- **BS** — Style (style and convention)
- **BP** — Pedantic (strict best practices)
- **BSEC** — Security (sensitive data and credentials)
- **BI18N** — I18N (internationalization issues)
- **BACC** — Accessibility (inclusive design and accessibility)
