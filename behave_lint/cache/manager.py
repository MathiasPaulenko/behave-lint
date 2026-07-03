"""Cache manager for incremental linting.

Stores per-file diagnostic results keyed by content hash and
configuration signature. On subsequent runs, unchanged files
skip rule execution entirely and reuse cached diagnostics.

Cache format (JSON):
    {
        "version": 1,
        "entries": {
            "<sha256>": {
                "diagnostics": [...],
                "file_path": "...",
                "config_hash": "..."
            }
        }
    }

The cache key is the SHA-256 of the file content. The config
hash ensures that changing rules, severity overrides, or other
config options invalidates the cache.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from behave_lint.exceptions import CacheError
from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic

logger = logging.getLogger(__name__)

_CACHE_FORMAT_VERSION = 1


def _compute_file_hash(content: str) -> str:
    """Compute SHA-256 hash of file content.

    Args:
        content: File content as string.

    Returns:
        Hexadecimal hash string.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _compute_config_hash(config: Config) -> str:
    """Compute a hash of the configuration fields that affect diagnostics.

    Args:
        config: The resolved configuration.

    Returns:
        Hexadecimal hash string.
    """
    relevant = {
        "select": sorted(config.select),
        "ignore": sorted(config.ignore),
        "profile": config.profile,
        "group": sorted(config.group),
        "severity_overrides": {
            k: v.value for k, v in sorted(config.severity_overrides.items())
        },
        "rule_params": config.rule_params,
        "fail_on": config.fail_on.value,
    }
    raw = json.dumps(relevant, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class CacheEntry:
    """A single cache entry for a file.

    Attributes:
        file_hash: SHA-256 of the file content.
        config_hash: Hash of the relevant config fields.
        diagnostics: Cached diagnostics for this file.
        file_path: Path to the file (for reference).
    """

    file_hash: str
    config_hash: str
    diagnostics: list[Diagnostic]
    file_path: str


@dataclass
class CacheStats:
    """Statistics for a cache run.

    Attributes:
        hits: Number of cache hits.
        misses: Number of cache misses.
    """

    hits: int = 0
    misses: int = 0


class CacheManager:
    """Manages the incremental lint cache.

    Stores and retrieves per-file diagnostic results. The cache
    is persisted as a JSON file in the configured cache directory.

    Attributes:
        _cache_dir: Directory where the cache file is stored.
        _config_hash: Hash of the current configuration.
        _entries: In-memory cache entries (file_hash -> CacheEntry).
        _stats: Hit/miss statistics for the current run.
    """

    def __init__(self, cache_dir: str, config: Config) -> None:
        """Initialize the cache manager.

        Args:
            cache_dir: Directory path for the cache file.
            config: The resolved configuration.
        """
        self._cache_dir = Path(cache_dir)
        self._config_hash = _compute_config_hash(config)
        self._entries: dict[str, CacheEntry] = {}
        self._stats = CacheStats()
        self._load()

    @property
    def stats(self) -> CacheStats:
        """Return cache statistics for the current run.

        Returns:
            A CacheStats with hits and misses counts.
        """
        return self._stats

    @property
    def cache_file(self) -> Path:
        """Return the path to the cache file.

        Returns:
            Path to the JSON cache file.
        """
        return self._cache_dir / "lint_cache.json"

    def get(self, file_path: str, content: str) -> list[Diagnostic] | None:
        """Look up cached diagnostics for a file.

        Args:
            file_path: Path to the file (for reference).
            content: Current file content.

        Returns:
            Cached diagnostics if hit, None if miss.
        """
        file_hash = _compute_file_hash(content)
        entry = self._entries.get(file_hash)
        if entry is not None and entry.config_hash == self._config_hash:
            self._stats.hits += 1
            logger.debug("Cache hit for %s (hash=%s)", file_path, file_hash[:8])
            return list(entry.diagnostics)
        self._stats.misses += 1
        logger.debug("Cache miss for %s (hash=%s)", file_path, file_hash[:8])
        return None

    def put(
        self,
        file_path: str,
        content: str,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Store diagnostics for a file in the cache.

        Args:
            file_path: Path to the file (for reference).
            content: File content at the time of linting.
            diagnostics: Diagnostics produced for this file.
        """
        file_hash = _compute_file_hash(content)
        self._entries[file_hash] = CacheEntry(
            file_hash=file_hash,
            config_hash=self._config_hash,
            diagnostics=list(diagnostics),
            file_path=file_path,
        )

    def save(self) -> None:
        """Persist the cache to disk.

        Raises:
            CacheError: If the cache cannot be written.
        """
        try:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            data: dict[str, Any] = {
                "version": _CACHE_FORMAT_VERSION,
                "entries": {},
            }
            for file_hash, entry in self._entries.items():
                data["entries"][file_hash] = {
                    "file_path": entry.file_path,
                    "config_hash": entry.config_hash,
                    "diagnostics": [self._serialize_diag(d) for d in entry.diagnostics],
                }
            self.cache_file.write_text(
                json.dumps(data, indent=2, default=str),
                encoding="utf-8",
            )
        except OSError as exc:
            raise CacheError(f"Failed to write cache: {exc}") from exc

    def clear(self) -> None:
        """Clear all cache entries and remove the cache file."""
        self._entries.clear()
        self._stats = CacheStats()
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
        except OSError as exc:
            logger.warning("Failed to remove cache file: %s", exc)

    def _load(self) -> None:
        """Load the cache from disk if it exists."""
        if not self.cache_file.exists():
            return
        try:
            data = json.loads(self.cache_file.read_text(encoding="utf-8"))
            if data.get("version") != _CACHE_FORMAT_VERSION:
                logger.info("Cache version mismatch, starting fresh")
                return
            for file_hash, entry_data in data.get("entries", {}).items():
                diagnostics = [
                    self._deserialize_diag(d) for d in entry_data.get("diagnostics", [])
                ]
                self._entries[file_hash] = CacheEntry(
                    file_hash=file_hash,
                    config_hash=entry_data.get("config_hash", ""),
                    diagnostics=diagnostics,
                    file_path=entry_data.get("file_path", ""),
                )
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to load cache, starting fresh: %s", exc)
            self._entries.clear()

    @staticmethod
    def _serialize_diag(diag: Diagnostic) -> dict[str, Any]:
        """Serialize a Diagnostic to a JSON-compatible dict.

        Args:
            diag: The diagnostic to serialize.

        Returns:
            A dictionary representation of the diagnostic.
        """
        return {
            "rule_id": diag.rule_id,
            "severity": diag.severity.value,
            "message": diag.message,
            "file_path": diag.file_path,
            "line": diag.line,
            "category": diag.category.value,
            "column": diag.column,
            "end_line": diag.end_line,
            "end_column": diag.end_column,
            "suggestion": diag.suggestion,
            "doc_url": diag.doc_url,
        }

    @staticmethod
    def _deserialize_diag(data: dict[str, Any]) -> Diagnostic:
        """Deserialize a Diagnostic from a dict.

        Args:
            data: The dictionary representation.

        Returns:
            A reconstructed Diagnostic object.
        """
        from behave_lint.models.enums import Category, Severity

        return Diagnostic(
            rule_id=data["rule_id"],
            severity=Severity(data["severity"]),
            message=data["message"],
            file_path=data["file_path"],
            line=data["line"],
            category=Category(data["category"]),
            column=data.get("column"),
            end_line=data.get("end_line"),
            end_column=data.get("end_column"),
            suggestion=data.get("suggestion"),
            doc_url=data.get("doc_url"),
        )


__all__ = ["CacheEntry", "CacheManager", "CacheStats"]
