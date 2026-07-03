"""Tests for incremental cache manager and integration."""

from __future__ import annotations

from pathlib import Path

import pytest

from behave_lint.cache.manager import CacheManager
from behave_lint.configuration.loader import load_config
from behave_lint.engine.lint_engine import LintEngine
from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.rules.builtin import register_builtins
from behave_lint.rules.registry import RuleRegistry

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def simple_feature(tmp_path: Path) -> Path:
    f = tmp_path / "test.feature"
    f.write_text(
        "Feature: Test\n\n"
        "  Scenario: A scenario\n"
        "    Given a step\n"
        "    When I do something\n"
        "    Then I see a result\n",
        encoding="utf-8",
    )
    return f


@pytest.fixture
def config() -> Config:
    return load_config()


@pytest.fixture
def cache_dir(tmp_path: Path) -> str:
    d = tmp_path / ".cache"
    d.mkdir()
    return str(d)


# ---------------------------------------------------------------------------
# CacheManager unit tests
# ---------------------------------------------------------------------------


class TestCacheManager:
    """Unit tests for CacheManager."""

    def test_miss_on_first_lookup(self, cache_dir: str, config: Config) -> None:
        mgr = CacheManager(cache_dir, config)
        result = mgr.get("test.feature", "content")
        assert result is None
        assert mgr.stats.misses == 1
        assert mgr.stats.hits == 0

    def test_hit_after_put(self, cache_dir: str, config: Config) -> None:
        mgr = CacheManager(cache_dir, config)
        diags = [
            Diagnostic(
                rule_id="BS001",
                severity=Severity.WARNING,
                message="Test",
                file_path="test.feature",
                line=1,
                category=Category.STYLE,
            )
        ]
        mgr.put("test.feature", "content", diags)
        result = mgr.get("test.feature", "content")
        assert result is not None
        assert len(result) == 1
        assert result[0].rule_id == "BS001"
        assert mgr.stats.hits == 1
        assert mgr.stats.misses == 0

    def test_miss_on_content_change(self, cache_dir: str, config: Config) -> None:
        mgr = CacheManager(cache_dir, config)
        mgr.put("test.feature", "old content", [])
        result = mgr.get("test.feature", "new content")
        assert result is None
        assert mgr.stats.misses == 1

    def test_miss_on_config_change(self, cache_dir: str, config: Config) -> None:
        mgr1 = CacheManager(cache_dir, config)
        mgr1.put("test.feature", "content", [])
        mgr1.save()

        config2 = load_config(overrides={"select": ["BS001"]})
        mgr2 = CacheManager(cache_dir, config2)
        result = mgr2.get("test.feature", "content")
        assert result is None
        assert mgr2.stats.misses == 1

    def test_persistence_across_instances(self, cache_dir: str, config: Config) -> None:
        mgr1 = CacheManager(cache_dir, config)
        diags = [
            Diagnostic(
                rule_id="BS001",
                severity=Severity.WARNING,
                message="Test",
                file_path="test.feature",
                line=1,
                category=Category.STYLE,
            )
        ]
        mgr1.put("test.feature", "content", diags)
        mgr1.save()

        mgr2 = CacheManager(cache_dir, config)
        result = mgr2.get("test.feature", "content")
        assert result is not None
        assert len(result) == 1
        assert result[0].rule_id == "BS001"
        assert mgr2.stats.hits == 1

    def test_clear_removes_cache(self, cache_dir: str, config: Config) -> None:
        mgr = CacheManager(cache_dir, config)
        mgr.put("test.feature", "content", [])
        mgr.save()
        assert mgr.cache_file.exists()

        mgr.clear()
        assert not mgr.cache_file.exists()
        assert len(mgr._entries) == 0

    def test_corrupted_cache_handled_gracefully(
        self, cache_dir: str, config: Config
    ) -> None:
        cache_file = Path(cache_dir) / "lint_cache.json"
        cache_file.write_text("{invalid json", encoding="utf-8")

        mgr = CacheManager(cache_dir, config)
        result = mgr.get("test.feature", "content")
        assert result is None

    def test_old_cache_version_ignored(self, cache_dir: str, config: Config) -> None:
        import json

        cache_file = Path(cache_dir) / "lint_cache.json"
        cache_file.write_text(
            json.dumps({"version": 0, "entries": {}}),
            encoding="utf-8",
        )
        mgr = CacheManager(cache_dir, config)
        assert len(mgr._entries) == 0


# ---------------------------------------------------------------------------
# LintEngine integration tests
# ---------------------------------------------------------------------------


class TestCacheIntegration:
    """Integration tests for cache with LintEngine."""

    def test_second_run_uses_cache(self, simple_feature: Path, tmp_path: Path) -> None:
        cache_dir = str(tmp_path / ".cache")
        config = load_config(overrides={"cache_dir": cache_dir})
        registry = RuleRegistry()
        register_builtins(registry)

        engine = LintEngine(config, registry)

        # First run — should be all misses
        result1 = engine.lint(
            [str(simple_feature)],
            use_cache=True,
        )
        assert result1.summary.cache_misses == 1
        assert result1.summary.cache_hits == 0

        # Second run — same content, should be all hits
        result2 = engine.lint(
            [str(simple_feature)],
            use_cache=True,
        )
        assert result2.summary.cache_hits == 1
        assert result2.summary.cache_misses == 0

        # Diagnostics should be identical
        assert len(result1.diagnostics) == len(result2.diagnostics)

    def test_no_cache_flag_skips_cache(
        self, simple_feature: Path, tmp_path: Path
    ) -> None:
        cache_dir = str(tmp_path / ".cache")
        config = load_config(overrides={"cache_dir": cache_dir})
        registry = RuleRegistry()
        register_builtins(registry)

        engine = LintEngine(config, registry)

        # Run with cache to populate
        engine.lint([str(simple_feature)], use_cache=True)

        # Run without cache — should not hit
        result = engine.lint([str(simple_feature)], use_cache=False)
        assert result.summary.cache_hits == 0
        assert result.summary.cache_misses == 0

    def test_clear_cache_flag(self, simple_feature: Path, tmp_path: Path) -> None:
        cache_dir = str(tmp_path / ".cache")
        config = load_config(overrides={"cache_dir": cache_dir})
        registry = RuleRegistry()
        register_builtins(registry)

        engine = LintEngine(config, registry)

        # First run — populate cache
        engine.lint([str(simple_feature)], use_cache=True)

        # Second run with clear_cache — should be miss
        result = engine.lint(
            [str(simple_feature)],
            use_cache=True,
            clear_cache=True,
        )
        assert result.summary.cache_misses == 1
        assert result.summary.cache_hits == 0

    def test_modified_file_is_miss(self, simple_feature: Path, tmp_path: Path) -> None:
        cache_dir = str(tmp_path / ".cache")
        config = load_config(overrides={"cache_dir": cache_dir})
        registry = RuleRegistry()
        register_builtins(registry)

        engine = LintEngine(config, registry)

        # First run
        engine.lint([str(simple_feature)], use_cache=True)

        # Modify file
        simple_feature.write_text(
            "Feature: Modified\n\n  Scenario: B scenario\n    Given another step\n",
            encoding="utf-8",
        )

        # Second run — should be miss
        result = engine.lint([str(simple_feature)], use_cache=True)
        assert result.summary.cache_misses == 1
        assert result.summary.cache_hits == 0
