"""Smoke test — verify package imports and version string."""

from __future__ import annotations

import behave_lint


def test_package_imports() -> None:
    """The package can be imported without errors."""
    assert hasattr(behave_lint, "__version__")


def test_version_string() -> None:
    """The version string follows semver format."""
    version = behave_lint.__version__
    assert isinstance(version, str)
    parts = version.split(".")
    assert len(parts) >= 2


def test_public_api_exports() -> None:
    """Core public API objects are importable from behave_lint."""
    from behave_lint import (
        AutoFixCapability,
        Category,
        Config,
        Diagnostic,
        LintResult,
        LintSummary,
        RuleExample,
        RuleMetadata,
        Severity,
    )

    assert Severity is not None
    assert Category is not None
    assert Diagnostic is not None
    assert Config is not None
    assert LintResult is not None
    assert LintSummary is not None
    assert RuleMetadata is not None
    assert RuleExample is not None
    assert AutoFixCapability is not None


def test_errors_importable() -> None:
    """The errors module is importable with the full hierarchy."""
    from behave_lint.errors import (
        BehaveLintError,
        ConfigError,
        InternalError,
        NoFilesFoundError,
        PluginError,
    )

    assert issubclass(ConfigError, BehaveLintError)
    assert issubclass(InternalError, BehaveLintError)
    assert issubclass(NoFilesFoundError, BehaveLintError)
    assert issubclass(PluginError, BehaveLintError)
