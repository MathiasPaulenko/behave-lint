"""Rule base class — the SDK contract for all lint rules.

Subclass ``Rule``, implement ``check()``, and provide metadata via
class attributes. The ``self.diagnostic()`` helper constructs a
``Diagnostic`` with the rule's ID, category, and severity pre-filled.

See API.md Section 7 and RULE_ENGINE.md Section 2.
"""

from __future__ import annotations

from typing import Any, ClassVar

from behave_lint.autofix.models import FixEdit
from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.rule_metadata import RuleMetadata
from behave_lint.rules.diagnostic_factory import DiagnosticFactory, HasLocation
from behave_lint.rules.scope import RuleScope


class Rule:
    """Base class for all lint rules.

    Subclasses must:
    - Set the ``metadata`` class attribute to a ``RuleMetadata`` object.
    - Implement the ``check()`` method.

    Subclasses may:
    - Set ``scope`` to ``RuleScope.CROSS_FILE`` for cross-file rules.
    - Set ``default_params`` to a dict of configurable parameters.

    Attributes:
        metadata: Rule metadata (must be set by subclass).
        scope: Execution scope (default: SINGLE_FILE).
        default_params: Default parameter values for this rule.
    """

    metadata: RuleMetadata
    scope: RuleScope = RuleScope.SINGLE_FILE
    default_params: ClassVar[dict[str, Any]] = {}

    def __init__(self) -> None:
        """Initialize the rule instance.

        The constructor may set up internal state (caches, compiled
        patterns) but must not perform I/O or access the project model.
        """
        self._diagnostic_factory: DiagnosticFactory | None = None

    def check(self, feature: Any, config: Config) -> list[Diagnostic]:
        """Analyze the feature and return diagnostics.

        For single-file rules, ``feature`` is a single feature model.
        For cross-file rules, ``feature`` is the full project model.

        Args:
            feature: The parsed feature (or project for cross-file rules).
            config: The resolved configuration object.

        Returns:
            A list of diagnostics (possibly empty).

        Raises:
            NotImplementedError: If the subclass does not implement this.
        """
        raise NotImplementedError(
            f"Rule {self.__class__.__name__} must implement check()"
        )

    def get_fixes(
        self, feature: Any, config: Config, diagnostics: list[Diagnostic]
    ) -> list[FixEdit]:
        """Return fix edits for the given diagnostics.

        Override this method to provide auto-fix support. The default
        implementation returns no fixes.

        Args:
            feature: The parsed feature model.
            config: The resolved configuration object.
            diagnostics: Diagnostics produced by this rule's check().

        Returns:
            A list of FixEdit objects to apply.
        """
        return []

    def diagnostic(
        self,
        message: str,
        node: HasLocation | None = None,
        *,
        line: int | None = None,
        column: int | None = None,
        file_path: str | None = None,
        end_line: int | None = None,
        end_column: int | None = None,
        suggestion: str | None = None,
        doc_url: str | None = None,
        severity: Severity | None = None,
    ) -> Diagnostic:
        """Create a diagnostic with this rule's metadata pre-filled.

        This is a convenience method that delegates to the internal
        DiagnosticFactory. The rule's ID, category, and default severity
        are automatically stamped on the diagnostic.

        Args:
            message: What is wrong (factual statement).
            node: A behave-model element with file_path and line.
            line: Explicit line number (overrides node).
            column: Explicit column number (overrides node).
            file_path: Explicit file path (overrides node).
            end_line: End line of the diagnostic range.
            end_column: End column of the diagnostic range.
            suggestion: How to fix it (actionable guidance).
            doc_url: URL to rule documentation.
            severity: Override severity (defaults to rule's default).

        Returns:
            A Diagnostic with rule metadata pre-filled.
        """
        if self._diagnostic_factory is not None:
            factory = self._diagnostic_factory
            if severity is not None:
                factory = DiagnosticFactory(
                    rule_id=factory.rule_id,
                    category=factory.category,
                    severity=severity,
                    file_path=factory.file_path,
                )
            return factory.create(
                message=message,
                node=node,
                line=line,
                column=column,
                file_path=file_path,
                end_line=end_line,
                end_column=end_column,
                suggestion=suggestion,
                doc_url=doc_url,
            )

        # Fallback: create diagnostic directly from metadata
        resolved_line = line
        if resolved_line is None and node is not None:
            resolved_line = getattr(node, "line", None)
            if resolved_line is None:
                loc = getattr(node, "location", None)
                if loc is not None:
                    resolved_line = getattr(loc, "line", None)
        if not resolved_line:
            resolved_line = 1

        resolved_path = file_path
        if not resolved_path and node is not None:
            resolved_path = getattr(node, "file_path", None)
        if not resolved_path and node is not None:
            loc = getattr(node, "location", None)
            if loc is not None:
                resolved_path = getattr(loc, "filename", None)
        if not resolved_path:
            resolved_path = ""

        return Diagnostic(
            rule_id=self.metadata.rule_id,
            severity=severity or self.metadata.default_severity,
            message=message,
            file_path=resolved_path,
            line=resolved_line,
            category=self.metadata.category,
            column=column,
            end_line=end_line,
            end_column=end_column,
            suggestion=suggestion,
            doc_url=doc_url or self.metadata.doc_url,
        )

    def _set_diagnostic_factory(self, factory: DiagnosticFactory) -> None:
        """Set the diagnostic factory for this rule instance.

        Called by the rule executor before execution.

        Args:
            factory: The diagnostic factory to use.
        """
        self._diagnostic_factory = factory

    @property
    def rule_id(self) -> str:
        """The rule's ID (from metadata)."""
        return self.metadata.rule_id

    @property
    def category(self) -> Category:
        """The rule's category (from metadata)."""
        return self.metadata.category

    @property
    def default_severity(self) -> Severity:
        """The rule's default severity (from metadata)."""
        return self.metadata.default_severity


__all__ = ["Rule"]
