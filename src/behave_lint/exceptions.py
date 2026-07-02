"""Exception hierarchy for behave-lint.

All custom exceptions inherit from BehaveLintError. See API.md Section 11
and ARCHITECTURE.md Section 14 for the error handling design.

Hierarchy::

    BehaveLintError (base)
    ├── ConfigError
    │   ├── InvalidConfigValueError
    │   ├── UnknownConfigKeyError
    │   └── UnknownRuleError
    ├── NoFilesFoundError
    ├── InternalError
    ├── RuleError
    │   ├── RuleNotFoundError
    │   └── RuleExecutionError
    ├── ParseError
    ├── FileDiscoveryError
    ├── CacheError
    ├── ReporterError
    └── PluginError
        ├── PluginLoadError
        └── PluginRegistrationError
"""

from __future__ import annotations


class BehaveLintError(Exception):
    """Base exception for all behave-lint errors."""


class ConfigError(BehaveLintError):
    """Raised when configuration is invalid or cannot be loaded."""


class InvalidConfigValueError(ConfigError):
    """Raised when a config value is invalid (e.g., severity 'critical').

    Attributes:
        key: The configuration key.
        value: The invalid value.
        expected: Description of valid values.
    """

    def __init__(self, key: str, value: str, expected: str) -> None:
        self.key = key
        self.value = value
        self.expected = expected
        super().__init__(
            f"Invalid value '{value}' for key '{key}'. Expected: {expected}."
        )


class UnknownConfigKeyError(ConfigError):
    """Raised when an unknown key is found in pyproject.toml.

    Forward-compatible — produces a warning, not a fatal error.

    Attributes:
        key: The unknown configuration key.
    """

    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(f"Unknown configuration key '{key}'.")


class UnknownRuleError(ConfigError):
    """Raised when a rule ID in select/ignore is not registered.

    Attributes:
        rule_id: The unknown rule ID.
        suggestion: Fuzzy-match suggestion, or None.
    """

    def __init__(self, rule_id: str, suggestion: str | None = None) -> None:
        self.rule_id = rule_id
        self.suggestion = suggestion
        msg = f"Unknown rule ID '{rule_id}'."
        if suggestion:
            msg += f" Did you mean '{suggestion}'?"
        super().__init__(msg)


class NoFilesFoundError(BehaveLintError):
    """Raised when no .feature files are found in the specified paths.

    Attributes:
        paths: The paths that were searched.
    """

    def __init__(self, paths: list[str]) -> None:
        self.paths = paths
        super().__init__(f"No .feature files found in: {', '.join(paths)}")


class InternalError(BehaveLintError):
    """Raised on unexpected internal failures. Indicates a bug.

    Attributes:
        operation: What operation was being performed.
        version: Tool version at time of error.
    """

    def __init__(self, operation: str, version: str) -> None:
        self.operation = operation
        self.version = version
        super().__init__(
            f"Internal error during: {operation}. "
            f"behave-lint v{version}. "
            "Please report this at https://github.com/MathiasPaulenko/behave-lint/issues."
        )


class RuleError(BehaveLintError):
    """Base exception for rule-related errors."""


class RuleNotFoundError(RuleError):
    """Raised when a referenced rule ID does not exist.

    Attributes:
        rule_id: The missing rule ID.
    """

    def __init__(self, rule_id: str) -> None:
        self.rule_id = rule_id
        super().__init__(f"Rule not found: '{rule_id}'.")


class RuleExecutionError(RuleError):
    """Raised when a rule fails during execution.

    Attributes:
        rule_id: The rule that failed.
    """

    def __init__(self, rule_id: str, detail: str) -> None:
        self.rule_id = rule_id
        super().__init__(f"Rule '{rule_id}' failed: {detail}")


class ParseError(BehaveLintError):
    """Raised when a .feature file cannot be parsed.

    Attributes:
        file_path: Path to the file that failed to parse.
        line: Line number where parsing failed, if known.
    """

    def __init__(self, file_path: str, line: int | None = None) -> None:
        self.file_path = file_path
        self.line = line
        location = f" at line {line}" if line is not None else ""
        super().__init__(f"Parse error in '{file_path}'{location}.")


class FileDiscoveryError(BehaveLintError):
    """Raised when file discovery encounters an unrecoverable error."""


class CacheError(BehaveLintError):
    """Raised when the cache is corrupted or inaccessible."""


class ReporterError(BehaveLintError):
    """Raised when a reporter fails to produce output."""


class PluginError(BehaveLintError):
    """Raised when a plugin fails to load or register."""


class PluginLoadError(PluginError):
    """Raised when a plugin module cannot be imported.

    Attributes:
        plugin_name: The name of the plugin that failed to load.
    """

    def __init__(self, plugin_name: str, detail: str) -> None:
        self.plugin_name = plugin_name
        super().__init__(f"Failed to load plugin '{plugin_name}': {detail}")


class PluginRegistrationError(PluginError):
    """Raised when a plugin's registration function fails.

    Attributes:
        plugin_name: The name of the plugin that failed to register.
    """

    def __init__(self, plugin_name: str, detail: str) -> None:
        self.plugin_name = plugin_name
        super().__init__(f"Plugin '{plugin_name}' registration failed: {detail}")


__all__ = [
    "BehaveLintError",
    "CacheError",
    "ConfigError",
    "FileDiscoveryError",
    "InternalError",
    "InvalidConfigValueError",
    "NoFilesFoundError",
    "ParseError",
    "PluginError",
    "PluginLoadError",
    "PluginRegistrationError",
    "ReporterError",
    "RuleError",
    "RuleExecutionError",
    "RuleNotFoundError",
    "UnknownConfigKeyError",
    "UnknownRuleError",
]
