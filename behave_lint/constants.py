"""Project-wide constants.

All module-level constants that are shared across components live here.
Constants that are specific to a single component should remain in that
component's module.
"""

from __future__ import annotations

# Exit codes
EXIT_CODE_SUCCESS: int = 0
EXIT_CODE_USER_ERROR: int = 1
EXIT_CODE_CONFIG_ERROR: int = 2
EXIT_CODE_INTERNAL_ERROR: int = 3

# Cache
DEFAULT_CACHE_DIR_NAME: str = ".behave-lint-cache"

# Rule ID prefix
BUILTIN_RULE_PREFIX: str = "B"
PARSE_ERROR_RULE_ID: str = "B000"

# Environment variable prefix
ENV_PREFIX: str = "BEHAVE_LINT_"

# Trace environment variable
TRACE_ENV_VAR: str = "BEHAVE_LINT_TRACE"
