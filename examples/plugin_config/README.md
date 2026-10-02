# Plugin Config Example

A config-provider plugin that injects organization-wide defaults.

## Install and run

```bash
pip install ./examples/plugin_config
behave-lint features/
```

The plugin exposes a callable through the `behave_lint.config` entry
point group. The callable returns a dict of configuration overrides;
they sit below CLI flags but above `pyproject.toml` and profiles.
