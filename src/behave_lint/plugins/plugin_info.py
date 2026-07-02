"""Plugin metadata — dataclass for discovered plugin information.

Each discovered plugin (via entry points) is represented by a PluginInfo
object that holds its metadata before loading.

See COMPONENT_DESIGN.md C09 and API.md Section 9.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PluginType(Enum):
    """Type of plugin entry point.

    Members:
        RULES: Rule plugin (behave_lint.rules entry point group).
        REPORTERS: Reporter plugin (behave_lint.reporters entry point group).
        CONFIG: Configuration extension plugin (behave_lint.config entry point group).
    """

    RULES = "rules"
    REPORTERS = "reporters"
    CONFIG = "config"


@dataclass(frozen=True, slots=True)
class PluginInfo:
    """Metadata for a discovered plugin.

    Attributes:
        name: Entry point name (unique within a group).
        type: Plugin type (rules, reporters, config).
        module: Module path to import (e.g., "acme_lint_rules").
        attr: Attribute name to load from the module (e.g., "register_rules").
        group: Full entry point group name.
        loaded: Whether the plugin module has been imported.
        error: Error message if loading or registration failed, or None.
    """

    name: str
    type: PluginType
    module: str
    attr: str
    group: str
    loaded: bool = False
    error: str | None = None


__all__ = ["PluginInfo", "PluginType"]
