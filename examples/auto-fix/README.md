# Auto-Fix Example

Demonstrates `behave-lint --fix` on feature files with fixable violations.

## Structure

```
examples/auto-fix/
├── README.md
└── features/
    ├── before/          # Files with violations
    │   └── demo.feature
    └── after/           # Same files after --fix
        └── demo.feature
```

## Run

```bash
# See what violations exist (without fixing)
behave-lint examples/auto-fix/features/before/

# Apply safe fixes
behave-lint examples/auto-fix/features/before/ --fix

# Compare with the expected result
diff examples/auto-fix/features/before/demo.feature \
     examples/auto-fix/features/after/demo.feature
```

## What this demonstrates

- **BS001** (tag-casing): `@SmokeTest` → `@smoke_test`
- **BC004** (invalid-tag-syntax): `@smoke-test` → `@smoke_test`
- **BD005** (step-trailing-punctuation): `Given a user.` → `Given a user`
- **BD004** (step-parameter-convention): `{value}` → `<value>`
