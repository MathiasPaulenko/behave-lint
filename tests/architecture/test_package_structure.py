"""Architecture test — verify package structure and import boundaries.

These tests verify that the behave_lint package follows the layered
architecture rules defined in ARCHITECTURE.md Section 5.
"""

from __future__ import annotations

import importlib
import pathlib

import pytest

# Subpackages that must exist per REPOSITORY_DESIGN.md
EXPECTED_SUBPACKAGES = [
    "behave_lint.cli",
    "behave_lint.engine",
    "behave_lint.rules",
    "behave_lint.diagnostics",
    "behave_lint.configuration",
    "behave_lint.reporters",
    "behave_lint.infrastructure",
    "behave_lint.plugins",
    "behave_lint.models",
    "behave_lint.metadata",
    "behave_lint.statistics",
    "behave_lint.autofix",
    "behave_lint.services",
    "behave_lint.errors",
    "behave_lint.config",
]


@pytest.mark.architecture
@pytest.mark.parametrize("subpackage", EXPECTED_SUBPACKAGES)
def test_subpackage_importable(subpackage: str) -> None:
    """Each expected subpackage can be imported."""
    importlib.import_module(subpackage)


@pytest.mark.architecture
def test_version_attribute() -> None:
    """The package exposes a __version__ attribute."""
    import behave_lint

    assert isinstance(behave_lint.__version__, str)


@pytest.mark.architecture
def test_py_typed_marker() -> None:
    """The py.typed marker file exists for PEP 561 compliance."""
    import behave_lint

    pkg_dir = pathlib.Path(behave_lint.__file__).parent
    assert (pkg_dir / "py.typed").exists()


# Public API exports per API.md Section 4
PUBLIC_API_NAMES = [
    "Severity",
    "Category",
    "Diagnostic",
    "Config",
    "LintResult",
    "LintSummary",
    "RuleMetadata",
    "RuleExample",
    "AutoFixCapability",
    "load_config",
]


@pytest.mark.architecture
@pytest.mark.parametrize("name", PUBLIC_API_NAMES)
def test_public_api_export(name: str) -> None:
    """Each public API name is importable from behave_lint."""
    import behave_lint

    assert hasattr(behave_lint, name), f"behave_lint.{name} is not exported"


@pytest.mark.architecture
def test_errors_module_importable() -> None:
    """The behave_lint.errors module is importable and exports BehaveLintError."""
    from behave_lint import errors

    assert hasattr(errors, "BehaveLintError")
    assert hasattr(errors, "ConfigError")
    assert hasattr(errors, "InternalError")
    assert hasattr(errors, "NoFilesFoundError")
    assert hasattr(errors, "PluginError")
