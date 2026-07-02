"""File discovery — finds .feature files in specified paths.

Walks directories and collects .feature files, applying exclude patterns.
Handles both individual files and directory trees.

See COMPONENT_DESIGN.md C10 and ARCHITECTURE.md Section 11.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path


def discover_files(
    paths: list[str],
    *,
    exclude: list[str] | None = None,
) -> list[str]:
    """Find .feature files in the specified paths.

    Args:
        paths: List of file or directory paths to search.
        exclude: Glob patterns to exclude (e.g., ["**/vendor/**"]).

    Returns:
        Sorted list of .feature file paths (as strings).
    """
    exclude_patterns = exclude or []
    result: set[str] = set()

    for raw_path in paths:
        path = Path(raw_path)

        if not path.exists():
            continue

        if path.is_file():
            if _is_feature_file(path) and not _is_excluded(path, exclude_patterns):
                result.add(str(path))
        elif path.is_dir():
            for found in path.rglob("*.feature"):
                if not _is_excluded(found, exclude_patterns):
                    result.add(str(found))

    return sorted(result)


def _is_feature_file(path: Path) -> bool:
    """Check if a path is a .feature file.

    Args:
        path: Path to check.

    Returns:
        True if the file has a .feature extension.
    """
    return path.suffix == ".feature"


def _is_excluded(path: Path, patterns: list[str]) -> bool:
    """Check if a path matches any exclude pattern.

    Args:
        path: Path to check.
        patterns: Glob patterns to match against.

    Returns:
        True if the path matches any pattern.
    """
    if not patterns:
        return False

    path_str = str(path).replace("\\", "/")
    for pattern in patterns:
        normalized = pattern.replace("\\", "/")
        if fnmatch.fnmatch(path_str, normalized):
            return True
        if fnmatch.fnmatch(path.name, normalized):
            return True
    return False


__all__ = ["discover_files"]
