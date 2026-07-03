"""Tests for the cookiecutter plugin template.

Verifies that the template generates a valid, importable plugin project
with correct structure, entry points, and rule registration.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

cookiecutter = pytest.importorskip("cookiecutter.main")

TEMPLATE_DIR = Path(__file__).resolve().parents[4] / "templates" / "cookiecutter-plugin"


def _generate_project(tmp_path: Path, **overrides: object) -> Path:
    """Generate a plugin project from the template.

    Args:
        tmp_path: Temporary directory for the generated project.
        **overrides: Cookiecutter context overrides.

    Returns:
        Path to the generated project root.
    """
    from cookiecutter.main import cookiecutter

    context = {
        "project_name": "test-plugin",
        "plugin_name": "test_plugin",
        "class_name": "TestPlugin",
        "rule_id": "XT001",
        "rule_name": "test-rule",
        "rule_title": "Test rule",
        "rule_description": "A test rule.",
        "category": "style",
        "severity": "warning",
        "author_name": "Test Author",
        "author_email": "test@example.com",
        "version": "0.1.0",
        "license": "MIT",
        "include_auto_fix": "no",
    }
    context.update(overrides)

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    project_path = cookiecutter(
        str(TEMPLATE_DIR),
        no_input=True,
        extra_context=context,
        output_dir=str(output_dir),
    )
    return Path(project_path)


class TestTemplateStructure:
    """Verify the generated project has correct file structure."""

    def test_generates_expected_files(self, tmp_path: Path) -> None:
        project = _generate_project(tmp_path)
        assert (project / "pyproject.toml").exists()
        assert (project / "README.md").exists()
        assert (project / "LICENSE").exists()
        assert (project / ".gitignore").exists()
        assert (project / "test_plugin" / "__init__.py").exists()
        assert (project / "test_plugin" / "rules.py").exists()
        assert (project / "tests" / "__init__.py").exists()
        assert (project / "tests" / "test_rule.py").exists()

    def test_pyproject_has_entry_point(self, tmp_path: Path) -> None:
        project = _generate_project(tmp_path)
        content = (project / "pyproject.toml").read_text(encoding="utf-8")
        assert "behave_lint.rules" in content
        assert "test_plugin.rules:register_rules" in content

    def test_readme_has_rule_id(self, tmp_path: Path) -> None:
        project = _generate_project(tmp_path)
        content = (project / "README.md").read_text(encoding="utf-8")
        assert "XT001" in content

    def test_rules_py_has_metadata(self, tmp_path: Path) -> None:
        project = _generate_project(tmp_path)
        content = (project / "test_plugin" / "rules.py").read_text(encoding="utf-8")
        assert 'rule_id="XT001"' in content
        assert 'name="test-rule"' in content
        assert "register_rules" in content
        assert "TestPluginRule" in content


class TestTemplateWithAutoFix:
    """Verify the template with auto-fix enabled."""

    def test_auto_fix_included(self, tmp_path: Path) -> None:
        project = _generate_project(tmp_path, include_auto_fix="yes")
        content = (project / "test_plugin" / "rules.py").read_text(encoding="utf-8")
        assert "AutoFixCapability" in content
        assert "get_fixes" in content

    def test_auto_fix_excluded_by_default(self, tmp_path: Path) -> None:
        project = _generate_project(tmp_path)
        content = (project / "test_plugin" / "rules.py").read_text(encoding="utf-8")
        assert "AutoFixCapability" not in content
        assert "get_fixes" not in content


class TestTemplateImportable:
    """Verify the generated plugin is importable and registers correctly."""

    def test_register_rules_returns_rule_class(self, tmp_path: Path) -> None:
        project = _generate_project(tmp_path)
        sys.path.insert(0, str(project))

        try:
            mod = importlib.import_module("test_plugin.rules")
            rule_classes = mod.register_rules()
            assert len(rule_classes) == 1
            assert hasattr(rule_classes[0], "metadata")
            assert rule_classes[0].metadata.rule_id == "XT001"
        finally:
            sys.path.remove(str(project))
            for mod_name in list(sys.modules):
                if mod_name.startswith("test_plugin"):
                    del sys.modules[mod_name]
