# {{ cookiecutter.project_name }}

A [behave-lint](https://github.com/MathiasPaulenko/behave-lint) plugin that adds the **{{ cookiecutter.rule_id }}** rule: {{ cookiecutter.rule_title }}.

## Installation

```bash
pip install {{ cookiecutter.project_name }}
```

## Usage

Once installed, the rule is automatically discovered by behave-lint:

```bash
# Run with all rules (including this plugin)
behave-lint features/

# Run only this plugin's rule
behave-lint --select {{ cookiecutter.rule_id }} features/

# Explain the rule
behave-lint --explain {{ cookiecutter.rule_id }}
```

## Rule: {{ cookiecutter.rule_id }}

| Field | Value |
|-------|-------|
| **ID** | {{ cookiecutter.rule_id }} |
| **Name** | {{ cookiecutter.rule_name }} |
| **Category** | {{ cookiecutter.category }} |
| **Severity** | {{ cookiecutter.severity }} |
{% if cookiecutter.include_auto_fix == "yes" %}
| **Auto-fix** | Yes (SAFE) |
{% else %}
| **Auto-fix** | No |
{% endif %}

{{ cookiecutter.rule_description }}

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check && ruff format
```

## License

{{ cookiecutter.license }}
