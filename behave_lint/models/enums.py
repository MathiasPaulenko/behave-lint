"""Domain enums — Severity, Category, AutoFixCapability, and taxonomy enums.

These enums are the foundational vocabulary of behave-lint. They are used
across all layers: configuration, rules, diagnostics, reporters, and CLI.

See API.md Section 4 and RULE_TAXONOMY.md Sections 3-5.
"""

from __future__ import annotations

from enum import Enum


class Severity(Enum):
    """Importance level of a diagnostic.

    Members:
        ERROR: Must be fixed; causes non-zero exit code.
        WARNING: Should be fixed; does not cause non-zero exit by default.
        INFO: Informational; never affects exit code.
        OFF: Rule is disabled; no diagnostics are produced.
    """

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    OFF = "off"

    @classmethod
    def from_string(cls, value: str) -> Severity:
        """Parse a string into a Severity member.

        Args:
            value: Case-insensitive severity string.

        Returns:
            The matching Severity member.

        Raises:
            ValueError: If the string does not match any member.
        """
        normalized = value.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        valid = ", ".join(m.value for m in cls)
        raise ValueError(f"Invalid severity '{value}'. Expected one of: {valid}.")


class Category(Enum):
    """Groups rules by concern (what kind of problem).

    Members:
        CORRECTNESS: Definitively wrong structures.
        STYLE: Stylistic conventions.
        COMPLEXITY: Overly complex specifications.
        CONSISTENCY: Cross-file consistency.
        PEDANTIC: Strict best practices (opt-in).
        STEP_DEFINITIONS: Cross-reference with step defs.
    """

    CORRECTNESS = "correctness"
    STYLE = "style"
    COMPLEXITY = "complexity"
    CONSISTENCY = "consistency"
    PEDANTIC = "pedantic"
    STEP_DEFINITIONS = "step_definitions"

    @property
    def code(self) -> str:
        """Single-letter category code used in rule IDs.

        Returns:
            The category code: C, S, X, K, P, or D.
        """
        return _CATEGORY_CODES[self]

    @property
    def default_severity(self) -> Severity:
        """Default severity for rules in this category.

        Returns:
            The default Severity for the category.
        """
        return _CATEGORY_DEFAULT_SEVERITY[self]

    @classmethod
    def from_string(cls, value: str) -> Category:
        """Parse a string into a Category member.

        Args:
            value: Case-insensitive category string.

        Returns:
            The matching Category member.

        Raises:
            ValueError: If the string does not match any member.
        """
        normalized = value.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        valid = ", ".join(m.value for m in cls)
        raise ValueError(f"Invalid category '{value}'. Expected one of: {valid}.")

    @classmethod
    def from_code(cls, code: str) -> Category:
        """Parse a single-letter code into a Category member.

        Args:
            code: Single uppercase letter (C, S, X, K, P, D).

        Returns:
            The matching Category member.

        Raises:
            ValueError: If the code does not match any member.
        """
        normalized = code.strip().upper()
        for member in cls:
            if member.code == normalized:
                return member
        valid = ", ".join(m.code for m in cls)
        raise ValueError(f"Invalid category code '{code}'. Expected one of: {valid}.")


class AutoFixCapability(Enum):
    """Declares a rule's auto-fix support.

    Members:
        NONE: Not fixable.
        SAFE: Fix does not change semantics.
        UNSAFE: Fix may change semantics.
    """

    NONE = "none"
    SAFE = "safe"
    UNSAFE = "unsafe"


class FixCost(Enum):
    """Estimated effort to fix a diagnostic.

    Members:
        TRIVIAL: Minimal effort (e.g., whitespace).
        LOW: Quick fix (e.g., rename).
        MEDIUM: Requires some thought (e.g., restructure scenario).
        HIGH: Significant effort (e.g., rewrite feature file).
    """

    TRIVIAL = "trivial"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PerformanceImpact(Enum):
    """Execution cost of a rule.

    Members:
        NEGLIGIBLE: Near-zero cost (simple checks).
        LOW: Fast (single-pass, no I/O).
        MEDIUM: Moderate (multi-pass or cross-file).
        HIGH: Expensive (may require step definition analysis).
    """

    NEGLIGIBLE = "negligible"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EducationalValue(Enum):
    """Pedagogical value of a rule's diagnostics.

    Members:
        NONE: No educational value.
        LOW: Minor learning opportunity.
        MEDIUM: Explains a common pitfall.
        HIGH: Teaches a fundamental BDD concept.
    """

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


_CATEGORY_CODES: dict[Category, str] = {
    Category.CORRECTNESS: "C",
    Category.STYLE: "S",
    Category.COMPLEXITY: "X",
    Category.CONSISTENCY: "K",
    Category.PEDANTIC: "P",
    Category.STEP_DEFINITIONS: "D",
}

_CATEGORY_DEFAULT_SEVERITY: dict[Category, Severity] = {
    Category.CORRECTNESS: Severity.ERROR,
    Category.STYLE: Severity.WARNING,
    Category.COMPLEXITY: Severity.WARNING,
    Category.CONSISTENCY: Severity.WARNING,
    Category.PEDANTIC: Severity.OFF,
    Category.STEP_DEFINITIONS: Severity.WARNING,
}


__all__ = [
    "AutoFixCapability",
    "Category",
    "EducationalValue",
    "FixCost",
    "PerformanceImpact",
    "Severity",
]
