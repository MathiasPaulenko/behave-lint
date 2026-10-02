"""Project model — aggregate view of all parsed feature files.

Used as the input model for cross-file rules (``RuleScope.CROSS_FILE``),
which analyze the whole project rather than a single feature file.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Project:
    """Aggregate of all parsed features in a lint run.

    Attributes:
        features: List of parsed feature models (behave-model Feature
            objects).
    """

    features: list[Any] = field(default_factory=list)


__all__ = ["Project"]
