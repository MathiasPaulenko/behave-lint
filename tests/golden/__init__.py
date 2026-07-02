"""Golden tests — output stability against curated .feature fixtures.

Each golden test runs the linter on a fixed input and compares the
diagnostic output to a stored golden file. Golden files are reviewed
and committed — changes indicate intentional behavior shifts.
"""

from __future__ import annotations
