"""Shared type definitions used across behave-lint.

This module contains type aliases and protocols that are used by multiple
components. Domain enums (Severity, Category) and data models (Diagnostic,
Config) belong in behave_lint.models.
"""

from __future__ import annotations

from typing import TypeAlias

from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.rule_metadata import RuleMetadata

DiagnosticList: TypeAlias = list[Diagnostic]
RuleMap: TypeAlias = dict[str, RuleMetadata]
RuleID: TypeAlias = str
FilePath: TypeAlias = str

__all__ = [
    "DiagnosticList",
    "FilePath",
    "RuleID",
    "RuleMap",
]
