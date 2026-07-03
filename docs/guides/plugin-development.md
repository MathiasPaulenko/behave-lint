# Plugin Development

Plugins extend `behave-lint` with custom rules, reporters, or
configuration providers.

## Plugin types

| Type | Entry point group | Description |
|------|-------------------|-------------|
| Rules | `behave_lint.rules` | Custom lint rules |
| Reporters | `behave_lint.reporters` | Custom output formats |
| Config | `behave_lint.config_sources` | Configuration providers |

## Quick start with the cookiecutter template

The fastest way to create a plugin is using the cookiecutter template
included in this repository:

```bash
# Install cookiecutter
pip install cookiecutter

# Generate a plugin from the template
cookiecutter https://github.com/MathiasPaulenko/behave-lint --directory templates/cookiecutter-plugin
```

You'll be prompted for:

| Field | Description | Example |
|-------|-------------|---------|
| `project_name` | PyPI package name | `behave-lint-acme-rules` |
| `plugin_name` | Python module name | `acme_rules` |
| `class_name` | PascalCase rule class name | `AcmeRules` |
| `rule_id` | Unique rule ID | `XA001` |
| `rule_name` | Kebab-case rule name | `acme-check` |
| `rule_title` | Human-readable title | `Acme compliance check` |
| `category` | Rule category | `style`, `correctness`, etc. |
| `severity` | Default severity | `warning`, `error`, `info` |
| `include_auto_fix` | Include auto-fix skeleton | `yes` or `no` |

The generated project includes:

- `pyproject.toml` with entry points configured
- Rule skeleton with `RuleMetadata`, `check()`, and optional `get_fixes()`
- Test suite with fixtures
- README with usage examples
- MIT LICENSE
- `.gitignore`

## Creating a plugin manually

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
