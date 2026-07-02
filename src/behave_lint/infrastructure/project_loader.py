"""Project loader — parses .feature files via behave-model.

Loads feature files into behave-model's Feature objects, handling parse
errors gracefully. Each file is loaded independently — a parse failure in
one file does not prevent loading others.

See COMPONENT_DESIGN.md C11 and ARCHITECTURE.md Section 5.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from behave_model import BehaveModelError, load_feature

logger = logging.getLogger(__name__)


@dataclass
class LoadResult:
    """Result of loading feature files.

    Attributes:
        features: Successfully parsed feature models.
        errors: List of (file_path, error_message) for failed loads.
    """

    features: list[Any] = field(default_factory=list)
    errors: list[tuple[str, str]] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Whether any file failed to load.

        Returns:
            True if there are load errors.
        """
        return len(self.errors) > 0


def load_features(
    file_paths: list[str],
    *,
    language: str | None = None,
) -> LoadResult:
    """Load multiple feature files, isolating parse failures.

    Args:
        file_paths: List of .feature file paths to load.
        language: Optional Gherkin language (e.g., "es").

    Returns:
        A LoadResult with parsed features and any errors.
    """
    features: list[Any] = []
    errors: list[tuple[str, str]] = []

    for file_path in file_paths:
        feature = load_single(file_path, language=language)
        if feature is not None:
            features.append(feature)
        else:
            errors.append((file_path, "Failed to parse feature file"))

    return LoadResult(features=features, errors=errors)


def load_single(
    file_path: str,
    *,
    language: str | None = None,
) -> Any | None:
    """Load a single feature file.

    Args:
        file_path: Path to the .feature file.
        language: Optional Gherkin language.

    Returns:
        A Feature model, or None if parsing failed.
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        logger.warning("Feature file not found: %s", file_path)
        return None

    try:
        return load_feature(str(path), language=language)
    except BehaveModelError as exc:
        logger.warning("Parse error in '%s': %s", file_path, exc)
        return None
    except Exception as exc:
        logger.warning("Unexpected error loading '%s': %s", file_path, exc)
        return None


def get_file_path_from_feature(feature: Any) -> str:
    """Extract the file path from a feature model.

    Args:
        feature: A behave-model Feature object.

    Returns:
        The file path string, or empty string if not available.
    """
    location = getattr(feature, "location", None)
    if location is not None:
        filename = getattr(location, "filename", None)
        if filename is not None:
            return str(filename)
    return ""


def get_line_from_feature(feature: Any) -> int:
    """Extract the starting line from a feature model.

    Args:
        feature: A behave-model Feature object.

    Returns:
        The line number, or 1 if not available.
    """
    location = getattr(feature, "location", None)
    if location is not None:
        line = getattr(location, "line", None)
        if line is not None:
            return int(line)
    return 1


__all__ = [
    "LoadResult",
    "get_file_path_from_feature",
    "get_line_from_feature",
    "load_features",
    "load_single",
]
