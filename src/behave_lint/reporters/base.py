"""Reporter base class — interface for custom output formats.

All reporters inherit from this class and implement the render() method
to transform a LintResult into formatted output.

See API.md Section 8 and COMPONENT_DESIGN.md C08.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

from behave_lint.models.lint_result import LintResult


class Reporter(ABC):
    """Base class for all output reporters.

    Subclasses must set the ``name`` class attribute and implement
    :meth:`render`.

    Class Attributes:
        name: Unique format name (e.g., "console", "json").
        supports_file_output: Whether this reporter can write to a file.
        supports_stdout: Whether this reporter can write to stdout.
        supports_streaming: Whether this reporter supports streaming
            for large outputs.
    """

    name: ClassVar[str] = ""
    supports_file_output: ClassVar[bool] = True
    supports_stdout: ClassVar[bool] = True
    supports_streaming: ClassVar[bool] = False

    @abstractmethod
    def render(self, result: LintResult, output_file: str | None = None) -> None:
        """Render the lint result to output.

        Args:
            result: The lint result containing diagnostics and summary.
            output_file: Path to write output to. If None, write to
                stdout.
        """
        ...

    @staticmethod
    def _write_output(content: str, output_file: str | None) -> None:
        """Write content to a file or stdout.

        Args:
            content: The formatted content to write.
            output_file: Path to write to. If None, writes to stdout.
        """
        if output_file:
            Path(output_file).write_text(content, encoding="utf-8")
        else:
            print(content)


__all__ = ["Reporter"]
