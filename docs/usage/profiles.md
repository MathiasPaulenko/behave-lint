# Profiles

Profiles are predefined rule sets that make it easy to configure
`behave-lint` for common use cases without listing individual rule IDs.

## Built-in profiles

| Profile | Description | Rules enabled |
|---------|-------------|---------------|
| `recommended` | All rules except pedantic (BP). Good default for most projects. | 43 rules (BC, BD, BK, BX, BS, BSEC, BI18N, BACC) |
| `strict` | All rules including pedantic. Maximum enforcement. | 50 rules (all) |
| `minimal` | Only correctness and step-definition rules. Catches real bugs only. | 15 rules (BC, BD) |

## Usage

### CLI

```bash
# Use the recommended profile
behave-lint features/ --profile recommended

# Use the strict profile (all rules)
behave-lint features/ --profile strict

# Use the minimal profile (correctness + step definitions only)
behave-lint features/ --profile minimal
```

### Configuration file

In `pyproject.toml`:

```toml
[tool.behave-lint]
profile = "recommended"
```

### Environment variable

```bash
export BEHAVE_LINT_PROFILE=strict
behave-lint features/
```

## Precedence

Profiles are resolved early in the configuration pipeline, after
built-in defaults but before `pyproject.toml` and CLI overrides.

This means:

- `--select` and `--ignore` from CLI or config **override** the
  profile's `select`/`ignore` lists.
- A profile specified in `pyproject.toml` is overridden by
  `--profile` on the CLI.

```text
Defaults → Profile → pyproject.toml → Environment → CLI overrides
```

## Combining with `--select` and `--ignore`

You can combine a profile with explicit `--select` or `--ignore`:

```bash
# Use recommended profile but also enable BP001
behave-lint features/ --profile recommended --select BP001

# Use strict profile but disable BX001
behave-lint features/ --profile strict --ignore BX001
```

When `--select` is specified, it replaces the profile's select list.
When `--ignore` is specified, it replaces the profile's ignore list.

## Default behavior

If no profile is specified, `behave-lint` enables all non-experimental,
non-deprecated rules by default (equivalent to `recommended` without
the pedantic exclusions).
