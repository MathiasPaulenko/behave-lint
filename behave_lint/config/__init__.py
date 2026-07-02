"""Public configuration API — alias for behave_lint.configuration.

See API.md Section 6 and CONFIGURATION_SYSTEM.md.
"""

from __future__ import annotations

from behave_lint.configuration.loader import load_config
from behave_lint.models.config import Config

__all__ = [
    "Config",
    "load_config",
]
