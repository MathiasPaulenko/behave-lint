"""Public error hierarchy — alias for behave_lint.exceptions.

This module re-exports the exception hierarchy so that users and plugins
can import from behave_lint.errors without depending on internal module
paths. See API.md Section 11.
"""

from __future__ import annotations

from behave_lint.exceptions import (
    BehaveLintError,
    CacheError,
    ConfigError,
    FileDiscoveryError,
    InternalError,
    InvalidConfigValueError,
    NoFilesFoundError,
    ParseError,
    PluginError,
    PluginLoadError,
    PluginRegistrationError,
    ReporterError,
    RuleError,
    RuleExecutionError,
    RuleNotFoundError,
    UnknownConfigKeyError,
    UnknownRuleError,
)

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
