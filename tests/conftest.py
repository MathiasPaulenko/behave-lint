"""Root pytest configuration.

Shared fixtures and configuration available to all test modules.
"""

from __future__ import annotations

import pytest


@pytest.fixture()
def tmp_project(tmp_path: str) -> str:
    """Provide a temporary directory simulating a project root."""
    return tmp_path
