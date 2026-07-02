"""Plugin Manager — entry point discovery, loading, registration, isolation.

Infrastructure layer — component C09.

See COMPONENT_DESIGN.md Section 8 and PLUGIN_SYSTEM.md.
"""

from __future__ import annotations

from behave_lint.plugins.manager import PluginManager
from behave_lint.plugins.plugin_info import PluginInfo, PluginType

__all__ = [
    "PluginInfo",
    "PluginManager",
    "PluginType",
]
