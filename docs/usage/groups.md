# Rule Groups

Rule groups provide a convenient way to select rules by **category** or
**tag** without listing each rule ID individually. Unlike profiles
(which set both `select` and `ignore`), groups are **additive** — they
add rule IDs to the `select` list and can be combined with each other
and with explicit `--select` rules.

## Usage

### CLI

```bash
# Select all correctness rules
behave-lint --group correctness features/

# Select multiple groups (comma-separated)
behave-lint --group correctness,style features/

# Combine with explicit rule selection
behave-lint --group correctness --select BS001 features/
```

### Configuration file (`pyproject.toml`)

```toml
[tool.behave-lint]
group = ["correctness", "style"]
```

### Environment variable

```bash
export BEHAVE_LINT_GROUP=correctness,style
```

## Precedence

Groups are resolved after profiles but before explicit `select`/`ignore`
overrides:

1. Built-in defaults
2. Profile (if specified)
3. Groups (if specified) — expanded to rule IDs and added to `select`
4. `pyproject.toml`
5. Environment variables
6. CLI overrides (highest)

Group-expanded rule IDs are **additive** — they are merged with any
explicitly selected rules, not replacing them.

## Built-in Groups

### Category-based groups

| Group | Prefix | Description |
|-------|--------|-------------|
| `correctness` | BC | Definitively wrong structures |
| `style` | BS | Stylistic conventions |
| `pedantic` | BP | Strict best practices (opt-in) |
| `step-definitions` | BD | Cross-reference with step defs |
| `consistency` | BK | Cross-file consistency |

### Tag-based groups

| Group | Tags matched | Description |
|-------|-------------|-------------|
| `naming` | `naming` | Naming conventions |
| `tags` | `tags` | Tag usage rules |
| `steps` | `steps` | Step content and phrasing |
| `background` | `background` | Background section rules |
| `description` | `description` | Feature/scenario descriptions |
| `documentation` | `documentation` | Documentation completeness |
| `formatting` | `formatting`, `whitespace`, `indentation`, `tabs` | Whitespace and formatting |
| `examples` | `examples` | Examples table rules |
| `scenarios` | `scenarios` | Scenario structure rules |
| `readability` | `readability` | Readability improvements |

## Combining Groups with Profiles

Groups and profiles can be used together. The profile sets the base
`select`/`ignore` lists, and groups add additional rules to `select`:

```bash
# Use recommended profile, but also enable pedantic rules
behave-lint --profile recommended --group pedantic features/
```

This is useful when you want most of a profile's recommendations but
also want to enable additional rule categories without listing every
rule ID.
