# Rules Reference

`behave-lint` ships with **31 built-in rules** across 6 categories.

## Categories

| Prefix | Category | Default Severity | Rules |
|--------|----------|-----------------|-------|
| BC | [Correctness](correctness.md) | ERROR | 6 |
| BD | [Step Definitions](step-definitions.md) | WARNING | 5 |
| BK | [Consistency](consistency.md) | WARNING/INFO | 5 |
| BX | [Complexity](complexity.md) | WARNING | 5 |
| BS | [Style](style.md) | WARNING | 5 |
| BP | [Pedantic](pedantic.md) | INFO | 5 |

## Auto-fixable rules

| Rule | Fix | Safety |
|------|-----|--------|
| BC004 | Replace invalid tag characters with `_` | Safe |
| BD004 | Convert `{param}` → `<param>` | Safe |
| BD005 | Remove trailing punctuation | Safe |
| BS001 | Convert tags to `snake_case` | Safe |

See the [Auto-Fix guide](../usage/auto-fix.md) for details.

## Rule IDs

Rule IDs use a two-letter prefix followed by a three-digit number:

- **BC** — Correctness (definitively wrong structures)
- **BD** — Step Definitions (step pattern issues)
- **BK** — Consistency (cross-scenario consistency)
- **BX** — Complexity (overly complex features)
- **BS** — Style (style and convention)
- **BP** — Pedantic (strict best practices)
