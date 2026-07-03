# Installation

## Requirements

- Python 3.11 or higher
- pip or [uv](https://docs.astral.sh/uv/)

## Install with pip

```bash
pip install behave-lint
```

## Install with uv

```bash
uv add behave-lint
```

## Optional: watch mode

Watch mode requires the `watchdog` package. Install it as an optional
dependency:

```bash
pip install behave-lint[watch]
```

Or with uv:

```bash
uv add 'behave-lint[watch]'
```

## Verify installation

```bash
behave-lint --version
```

## Next steps

- [Quick Start](quick-start.md) — lint your first feature files
- [CLI Reference](../usage/cli-reference.md) — all command-line options
- [Configuration](../usage/configuration.md) — customize rule behavior
