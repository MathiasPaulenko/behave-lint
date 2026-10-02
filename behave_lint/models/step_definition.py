"""Step definition model — a step pattern extracted from Python sources.

Represents one ``@given``/``@when``/``@then``/``@step`` decorator found
in a step definition file. Step definitions are loaded read-only via
``ast`` parsing; the Python modules are never imported or executed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_STEP_KEYWORDS = ("given", "when", "then", "step")

_PARAM_PATTERN = re.compile(r"\{[^{}]+\}")


def pattern_to_regex(pattern: str) -> re.Pattern[str]:
    """Convert a behave step pattern into a compiled regex.

    Behave supports two pattern styles:

    - ``parse``-style placeholders: ``I have {count} cukes`` — each
      ``{name}`` or ``{name:type}`` placeholder matches any text.
    - Raw regexes (``@step("^...$")`` or patterns containing
      ``(?P<name>...)`` groups) are used as-is.

    Args:
        pattern: The step definition pattern.

    Returns:
        A compiled regular expression anchored to the full text.
    """
    if pattern.startswith("^") or "(?P<" in pattern or "(?<" in pattern:
        try:
            return re.compile(pattern)
        except re.error:
            return re.compile(r"$.^")  # never matches

    regex = ""
    pos = 0
    for match in _PARAM_PATTERN.finditer(pattern):
        regex += re.escape(pattern[pos : match.start()])
        inner = match.group()[1:-1]
        # {name:type} — integer placeholders match digits only
        _, _, param_type = inner.partition(":")
        regex += r"\d+" if param_type == "d" else r".+?"
        pos = match.end()
    regex += re.escape(pattern[pos:])
    try:
        return re.compile(f"^{regex}$")
    except re.error:
        return re.compile(r"$.^")


@dataclass(frozen=True, slots=True)
class StepDefinition:
    """A step pattern extracted from a Python step definition file.

    Attributes:
        keyword: Decorator keyword — ``given``, ``when``, ``then`` or
            ``step`` (matches any keyword).
        pattern: The step pattern text (parse-style or regex).
        file_path: Path of the Python file where it was defined.
        line: 1-based line number of the decorated function.
    """

    keyword: str
    pattern: str
    file_path: str
    line: int

    def matches_keyword(self, keyword: str) -> bool:
        """Check whether this definition applies to a step keyword.

        Args:
            keyword: Effective step keyword (``given``, ``when``,
                ``then`` — ``and``/``but`` are resolved by the caller).

        Returns:
            True if the definition can match a step with that keyword.
        """
        return self.keyword == "step" or self.keyword == keyword

    def matches(self, text: str) -> bool:
        """Check whether a step text matches this definition's pattern.

        Args:
            text: The step text (without the leading keyword).

        Returns:
            True if the pattern matches the whole step text.
        """
        return pattern_to_regex(self.pattern).match(text) is not None


__all__ = ["StepDefinition", "pattern_to_regex"]
