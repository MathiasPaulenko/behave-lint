"""Tests for watch mode."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from behave_lint.cli.parser import CLIArgs
from behave_lint.cli.watch import WatchMode


@pytest.fixture
def cli_args() -> CLIArgs:
    return CLIArgs(
        paths=["features/"],
        output="console",
        fail_on="warning",
    )


@pytest.fixture
def feature_file(tmp_path: Path) -> Path:
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


class TestWatchMode:
    """Tests for WatchMode."""

    def test_init(self, cli_args: CLIArgs) -> None:
        watcher = WatchMode(cli_args, ["features/"])
        assert watcher.args is cli_args
        assert watcher.paths == ["features/"]
        assert watcher.debounce_seconds == 0.5

    def test_init_custom_debounce(self, cli_args: CLIArgs) -> None:
        watcher = WatchMode(cli_args, ["features/"], debounce_seconds=1.0)
        assert watcher.debounce_seconds == 1.0

    def test_on_change_ignores_non_feature_files(self, cli_args: CLIArgs) -> None:
        watcher = WatchMode(cli_args, ["features/"])
        with patch.object(watcher, "_lint_once") as mock_lint:
            watcher.on_change("features/test.txt")
            mock_lint.assert_not_called()

    def test_on_change_triggers_lint_for_feature_files(self, cli_args: CLIArgs) -> None:
        watcher = WatchMode(cli_args, ["features/"])
        with patch.object(watcher, "_lint_once") as mock_lint:
            watcher.on_change("features/test.feature")
            mock_lint.assert_called_once()

    def test_debounce_prevents_rapid_re_lint(self, cli_args: CLIArgs) -> None:
        watcher = WatchMode(cli_args, ["features/"], debounce_seconds=0.5)
        with patch("behave_lint.cli.watch._run_lint", return_value=0) as mock_run:
            watcher._lint_once()
            watcher._lint_once()
            assert mock_run.call_count == 1

    def test_debounce_allows_after_timeout(self, cli_args: CLIArgs) -> None:
        watcher = WatchMode(cli_args, ["features/"], debounce_seconds=0.05)
        with patch("behave_lint.cli.watch._run_lint", return_value=0) as mock_run:
            watcher._lint_once()
            time.sleep(0.1)
            watcher._lint_once()
            assert mock_run.call_count == 2

    def test_lint_once_calls_run_lint(
        self, cli_args: CLIArgs, feature_file: Path
    ) -> None:
        args = CLIArgs(paths=[str(feature_file)], output="console", fail_on="off")
        watcher = WatchMode(args, [str(feature_file)], debounce_seconds=0.0)
        with patch("behave_lint.cli.watch._run_lint", return_value=0) as mock_run:
            result = watcher._lint_once()
            assert result == 0
            mock_run.assert_called_once_with(args, [str(feature_file)])

    def test_on_change_with_feature_file_calls_lint(self, cli_args: CLIArgs) -> None:
        watcher = WatchMode(cli_args, ["features/"], debounce_seconds=0.0)
        with patch("behave_lint.cli.watch._run_lint", return_value=0) as mock_run:
            watcher.on_change("features/login.feature")
            assert mock_run.call_count == 1


class TestFeatureFileHandler:
    """Tests for _FeatureFileHandler."""

    def test_ignores_directory_events(self, cli_args: CLIArgs) -> None:
        watcher = WatchMode(cli_args, ["features/"])
        from behave_lint.cli.watch import _FeatureFileHandler

        handler = _FeatureFileHandler(watcher)
        event = MagicMock()
        event.is_directory = True
        event.src_path = "features/"
        handler.on_modified(event)
        handler.on_created(event)

    def test_ignores_non_feature_files(self, cli_args: CLIArgs) -> None:
        watcher = WatchMode(cli_args, ["features/"])
        from behave_lint.cli.watch import _FeatureFileHandler

        handler = _FeatureFileHandler(watcher)
        event = MagicMock()
        event.is_directory = False
        event.src_path = "features/readme.md"
        with patch.object(watcher, "on_change") as mock_change:
            handler.on_modified(event)
            mock_change.assert_called_once_with("features/readme.md")

    def test_handles_feature_file_creation(self, cli_args: CLIArgs) -> None:
        watcher = WatchMode(cli_args, ["features/"])
        from behave_lint.cli.watch import _FeatureFileHandler

        handler = _FeatureFileHandler(watcher)
        event = MagicMock()
        event.is_directory = False
        event.src_path = "features/new.feature"
        with patch.object(watcher, "on_change") as mock_change:
            handler.on_created(event)
            mock_change.assert_called_once_with("features/new.feature")


class TestWatchModeIntegration:
    """Integration tests for watch mode with the CLI."""

    def test_watch_flag_in_args(self) -> None:
        args = CLIArgs(paths=["features/"], watch=True)
        assert args.watch is True

    def test_watch_flag_default_false(self) -> None:
        args = CLIArgs(paths=["features/"])
        assert args.watch is False

    def test_watch_lints_initially(self, feature_file: Path) -> None:
        """Watch mode should lint once on startup."""
        args = CLIArgs(
            paths=[str(feature_file)],
            output="console",
            fail_on="off",
            watch=True,
        )
        watcher = WatchMode(args, [str(feature_file)], debounce_seconds=0.0)
        with (
            patch("behave_lint.cli.watch._run_lint", return_value=0) as mock_run,
            patch("watchdog.observers.Observer"),
            patch(
                "behave_lint.cli.watch.time.sleep",
                side_effect=KeyboardInterrupt,
            ),
        ):
            result = watcher.run()
            assert result == 0
            mock_run.assert_called_once()
