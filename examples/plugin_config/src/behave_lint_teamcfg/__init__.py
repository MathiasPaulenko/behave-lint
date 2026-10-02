"""Example config-provider plugin: injects team-wide defaults."""

from __future__ import annotations


def team_defaults() -> dict[str, object]:
    """Return configuration overrides applied before CLI flags."""
    return {
        "profile": "recommended",
        "exclude": ["features/vendor/"],
    }


__all__ = ["team_defaults"]
