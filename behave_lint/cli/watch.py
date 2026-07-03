"""Watch mode — re-lint on file changes.

Uses watchdog to observe .feature files and re-runs the linter
automatically when changes are detected. Designed for development
workflows where immediate feedback is valuable.

Usage:
    behave-lint features/ --watch
    behave-lint features/ --watch --output github
"""

from __future__ import annotations

import time
from pathlib import Path

from behave_lint.cli.coordinator import _run_lint
from behave_lint.cli.parser import CLIArgs

try:
    from watchdog.events import FileSystemEventHandler
except ImportError:
    FileSystemEventHandler = object  # type: ignore[misc,assignment]


class WatchMode:
    """Watch .feature files and re-lint on changes.

    Attributes:
        args: CLI arguments to pass to each lint run.
        paths: Paths to watch.
        debounce_seconds: Minimum time between lint runs.
    """

    def __init__(
        self,
        args: CLIArgs,
        paths: list[str],
        *,
        debounce_seconds: float = 0.5,
    ) -> None:
        """Initialize watch mode.

        Args:
            args: CLI arguments for each lint run.
            paths: Paths to watch and lint.
            debounce_seconds: Minimum time between lint runs.
        """
        self.args = args
        self.paths = paths
        self.debounce_seconds = debounce_seconds
        self._last_run: float = 0.0

    def run(self) -> int:
        """Start watching and linting.

        Runs an initial lint, then watches for changes. Blocks
        until interrupted with Ctrl+C.

        Returns:
            Exit code from the initial lint run.
        """
        try:
            from watchdog.observers import Observer
        except ImportError:
            print(
                "Watch mode requires 'watchdog'. Install with:\n"
                "  pip install behave-lint[watch]",
            )
            return 2

        print(
            f"Watching {', '.join(self.paths)} for changes...\nPress Ctrl+C to stop.\n",
        )

        exit_code = self._lint_once()

        handler = _FeatureFileHandler(self)
        observer = Observer()
        for path in self.paths:
            p = Path(path)
            watch_path = str(p if p.is_dir() else p.parent)
            observer.schedule(handler, watch_path, recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping watch mode...")
            observer.stop()
        observer.join()

        return exit_code

    def _lint_once(self) -> int:
        """Run a single lint pass.

        Returns:
            Exit code from the lint run.
        """
        now = time.monotonic()
        if now - self._last_run < self.debounce_seconds:
            return 0
        self._last_run = now

        print(f"\n--- Linting at {time.strftime('%H:%M:%S')} ---")
        return _run_lint(self.args, self.paths)

    def on_change(self, file_path: str) -> None:
        """Called when a .feature file changes.

        Args:
            file_path: Path to the changed file.
        """
        if not file_path.endswith(".feature"):
            return
        print(f"  Change detected: {file_path}")
        self._lint_once()


class _FeatureFileHandler(FileSystemEventHandler):
    """File system event handler for .feature files."""

    def __init__(self, watch_mode: WatchMode) -> None:
        """Initialize the handler.

        Args:
            watch_mode: The watch mode instance to notify.
        """
        self.watch_mode = watch_mode

    def on_modified(self, event: object) -> None:
        """Handle file modification events.

        Args:
            event: File system event.
        """
        if getattr(event, "is_directory", False):
            return
        src_path = getattr(event, "src_path", "")
        if src_path:
            self.watch_mode.on_change(str(src_path))

    def on_created(self, event: object) -> None:
        """Handle file creation events.

        Args:
            event: File system event.
        """
        if getattr(event, "is_directory", False):
            return
        src_path = getattr(event, "src_path", "")
        if src_path:
            self.watch_mode.on_change(str(src_path))


__all__ = ["WatchMode"]
