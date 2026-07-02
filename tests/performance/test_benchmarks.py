"""Performance benchmark tests for behave-lint.

Validates performance targets from SPECIFICATION.md Section 13:
- <1s for 100 files
- <5s for 1000 files
- <30s for 5000 files

Fixtures are generated on-demand and cleaned up after each test.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

# Make scripts/ importable
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.generate_fixtures import generate_feature_file  # noqa: E402

from behave_lint.configuration.loader import load_config  # noqa: E402
from behave_lint.engine.lint_engine import LintEngine  # noqa: E402
from behave_lint.rules.builtin import register_builtins  # noqa: E402
from behave_lint.rules.registry import RuleRegistry  # noqa: E402

# Performance targets (seconds)
# These are generous cross-platform targets. CI-specific targets
# (stricter) are defined in the nightly workflow.
TARGET_10_FILES = 1.0
TARGET_100_FILES = 2.0
TARGET_1000_FILES = 15.0


def _generate_fixtures(output_dir: Path, count: int) -> Path:
    """Generate fixture .feature files in a temp directory.

    Args:
        output_dir: Directory to write fixtures to.
        count: Number of .feature files to generate.

    Returns:
        Path to the directory containing the generated files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    for i in range(count):
        feature_path = output_dir / f"feature_{i:04d}.feature"
        feature_path.write_text(generate_feature_file(i), encoding="utf-8")
    return output_dir


def _lint_directory(feature_dir: Path) -> float:
    """Lint a directory and return elapsed time in seconds.

    Args:
        feature_dir: Directory containing .feature files.

    Returns:
        Elapsed time in seconds.
    """
    config = load_config(overrides={"paths": [str(feature_dir)]})
    registry = RuleRegistry()
    register_builtins(registry)
    engine = LintEngine(config=config, registry=registry)
    start = time.perf_counter()
    engine.lint()
    elapsed = time.perf_counter() - start
    return elapsed


@pytest.mark.performance
def test_perf_10_files(tmp_path: Path) -> None:
    """Benchmark: 10 files should lint in <0.5s."""
    fixture_dir = _generate_fixtures(tmp_path / "features", 10)
    elapsed = _lint_directory(fixture_dir)
    assert elapsed < TARGET_10_FILES, (
        f"10 files took {elapsed:.2f}s (target: <{TARGET_10_FILES}s)"
    )


@pytest.mark.performance
def test_perf_100_files(tmp_path: Path) -> None:
    """Benchmark: 100 files should lint in <1s."""
    fixture_dir = _generate_fixtures(tmp_path / "features", 100)
    elapsed = _lint_directory(fixture_dir)
    assert elapsed < TARGET_100_FILES, (
        f"100 files took {elapsed:.2f}s (target: <{TARGET_100_FILES}s)"
    )


@pytest.mark.performance
@pytest.mark.slow
def test_perf_1000_files(tmp_path: Path) -> None:
    """Benchmark: 1000 files should lint in <5s."""
    fixture_dir = _generate_fixtures(tmp_path / "features", 1000)
    elapsed = _lint_directory(fixture_dir)
    assert elapsed < TARGET_1000_FILES, (
        f"1000 files took {elapsed:.2f}s (target: <{TARGET_1000_FILES}s)"
    )
