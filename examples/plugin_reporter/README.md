# Plugin Reporter Example

A custom reporter plugin that adds a `csv` output format.

## Install and run

```bash
pip install ./examples/plugin_reporter
behave-lint features/ --output csv
```

The plugin exposes a `Reporter` subclass through the
`behave_lint.reporters` entry point group. The entry point name
(`csv`) becomes the format name used with `--output`.
