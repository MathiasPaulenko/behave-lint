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

**14 rules** provide auto-fixes (8 safe, 6 unsafe):

| Rule | Fix | Safety |
|------|-----|--------|
| BC004 | Replace invalid tag characters with `_` | Safe |
| BD004 | Convert `{param}` → `<param>` | Safe |
| BD005 | Remove trailing punctuation | Safe |
| BS001 | Convert tags to `snake_case` | Safe |
| BS003 | Normalize step phrasing | Safe |
| BS006 | Capitalize step keywords | Safe |
| BS007 | Remove trailing whitespace | Safe |
| BS008 | Convert tabs to spaces | Safe |
| BS002 | Reorder steps to Given-When-Then | Unsafe |
| BS004 | Rename custom Background names | Unsafe |
| BS005 | Insert Feature description template | Unsafe |
| BP001 | Insert `@smoke` tag on untagged scenarios | Unsafe |
| BP005 | Append `Valid values` to unnamed Examples | Unsafe |
| BP006 | Insert As a / I want / So that description | Unsafe |

Safe fixes run with `--fix`; unsafe fixes also require
`--unsafe-fixes`. See the [Auto-Fix guide](../usage/auto-fix.md) for
details.

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
