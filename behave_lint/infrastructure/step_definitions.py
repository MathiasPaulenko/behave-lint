"""Step definition loader — extracts step patterns from Python sources.

Walks a directory (or a single file) of behave step definition modules
and extracts the patterns registered via ``@given``, ``@when``,
``@then`` and ``@step`` decorators. Files are parsed with ``ast`` —
they are never imported or executed, so arbitrary step definition code
cannot run during linting.

Only literal string patterns are extracted; dynamically computed
patterns are skipped.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

from behave_lint.models.step_definition import StepDefinition

logger = logging.getLogger(__name__)

_DECORATOR_NAMES = frozenset({"given", "when", "then", "step"})


def _decorator_keyword(node: ast.expr) -> str | None:
    """Return the step keyword for a decorator node, or None.

    Accepts ``@given(...)``, ``@behave.given(...)`` and aliases such as
    ``@steps.given(...)`` — only the final attribute/name matters.
    """
    func = node.func if isinstance(node, ast.Call) else node
    if isinstance(func, ast.Name):
        name = func.id
    elif isinstance(func, ast.Attribute):
        name = func.attr
    else:
        return None
    name = name.lower()
    return name if name in _DECORATOR_NAMES else None


def _extract_from_node(node: ast.AST, file_path: str) -> list[StepDefinition]:
    """Extract step definitions from a function definition node."""
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return []

    defs: list[StepDefinition] = []
    for decorator in node.decorator_list:
        keyword = _decorator_keyword(decorator)
        if keyword is None or not isinstance(decorator, ast.Call):
            continue
        if not decorator.args:
            continue
        first = decorator.args[0]
        if not (isinstance(first, ast.Constant) and isinstance(first.value, str)):
            continue
        defs.append(
            StepDefinition(
                keyword=keyword,
                pattern=first.value,
                file_path=file_path,
                line=decorator.lineno,
            )
        )
    return defs


def load_step_definitions(path: str) -> list[StepDefinition]:
    """Load all step definitions under a file or directory.

    Args:
        path: Path to a ``.py`` file or a directory scanned recursively
            for ``*.py`` files.

    Returns:
        A list of extracted StepDefinition objects (possibly empty).
        Unparseable files are skipped with a warning.
    """
    root = Path(path)
    if root.is_file() and root.suffix == ".py":
        candidates = [root]
    elif root.is_dir():
        candidates = sorted(root.rglob("*.py"))
    else:
        logger.warning("Step definitions path not found: %s", path)
        return []

    defs: list[StepDefinition] = []
    for py_file in candidates:
        try:
            tree = ast.parse(
                py_file.read_text(encoding="utf-8"), filename=str(py_file)
            )
        except (OSError, SyntaxError) as exc:
            logger.warning("Cannot parse step definitions file %s: %s", py_file, exc)
            continue
        for node in ast.walk(tree):
            defs.extend(_extract_from_node(node, str(py_file)))
    return defs


__all__ = ["load_step_definitions"]
