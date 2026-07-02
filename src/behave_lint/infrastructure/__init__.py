"""File discovery, project loader, cache manager.

Infrastructure layer — components C10, C11, C12.

See COMPONENT_DESIGN.md Section 8 and ARCHITECTURE.md Section 5.
"""

from __future__ import annotations

from behave_lint.infrastructure.file_discovery import discover_files
from behave_lint.infrastructure.project_loader import (
    LoadResult,
    get_file_path_from_feature,
    get_line_from_feature,
    load_features,
    load_single,
)

__all__ = [
    "LoadResult",
    "discover_files",
    "get_file_path_from_feature",
    "get_line_from_feature",
    "load_features",
    "load_single",
]
