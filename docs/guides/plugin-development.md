# Plugin Development

Plugins extend `behave-lint` with custom rules, reporters, or
configuration providers.

## Plugin types

| Type | Entry point group | Description |
|------|-------------------|-------------|
| Rules | `behave_lint.rules` | Custom lint rules |
| Reporters | `behave_lint.reporters` | Custom output formats |
| Config | `behave_lint.config_sources` | Configuration providers |

## Creating a plugin

### 1. Set up your package

```toml
[project]
name = "behave-lint-my-plugin"
version = "0.1.0"
requires-python = ">=3.11"

[project.entry-points."behave_lint.rules"]
my-rule = "my_plugin.rules:MyCustomRule"
```

### 2. Implement your rule

See the [Custom Rules](custom-rules.md) guide for the full rule
implementation example.

### 3. Implement a custom reporter

```python
from behave_lint.models.lint_result import LintResult
from behave_lint.reporters.base import Reporter
from typing import ClassVar


class MyReporter(Reporter):
    """Custom reporter that outputs diagnostics as CSV."""

    name: ClassVar[str] = "csv"
    supports_file_output: ClassVar[bool] = True
    supports_stdout: ClassVar[bool] = True

    def render(self, result: LintResult, output_file: str | None = None) -> None:
        lines = ["rule_id,severity,file,line,message"]
        for d in result.diagnostics:
            lines.append(
                f"{d.rule_id},{d.severity},"
                f"{d.file_path},{d.line},{d.message}"
            )
        content = "\n".join(lines)
        self._write_output(content, output_file)
```

Register it:

```toml
[project.entry-points."behave_lint.reporters"]
csv = "my_plugin.reporters:MyReporter"
```

### 4. Install and test

```bash
pip install -e .
behave-lint features/ --output csv
```

## Plugin isolation

Plugins are loaded in isolated mode — a failure in one plugin does not
crash the linter. Errors are reported as warnings.

## Discovery

`behave-lint` discovers plugins via Python entry points. Ensure your
plugin package is installed in the same environment as `behave-lint`.
