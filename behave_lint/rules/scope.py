"""Rule scope enum — distinguishes single-file from cross-file rules.

See RULE_ENGINE.md Section 6 and API.md Section 7.
"""

from __future__ import annotations

from enum import Enum


class RuleScope(Enum):
    """Execution scope of a rule.

    Members:
        SINGLE_FILE: Rule analyzes one feature file at a time.
            Parallelized across (rule, file) pairs.
        CROSS_FILE: Rule analyzes the entire project at once.
            Executed sequentially after all single-file rules.
    """

    SINGLE_FILE = "single_file"
    CROSS_FILE = "cross_file"


__all__ = ["RuleScope"]
