"""Integration test: end-to-end pipeline with real .feature files.

Tests the full pipeline: CLI args → config → file discovery → load →
rule execution → diagnostic collection → reporter output → exit code.
"""

from __future__ import annotations

import json
from pathlib import Path

from behave_lint.cli.coordinator import main


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_lint_clean_feature(self, tmp_path: Path, capsys: object) -> None:
        feature = tmp_path / "clean.feature"
        feature.write_text(
            "Feature: Clean Feature\n"
            "  A clean feature for testing.\n\n"
            "  Scenario: A scenario\n"
            "    Given a step\n"
            "    Then another step\n",
            encoding="utf-8",
        )
        exit_code = main([str(feature)])
        assert exit_code == 0

    def test_lint_invalid_feature(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.feature"
        bad.write_text("This is not valid Gherkin\n", encoding="utf-8")
        exit_code = main([str(bad)])
        # Parse errors are ERROR severity, fail_on defaults to WARNING
        assert exit_code == 1

    def test_lint_directory(self, tmp_path: Path) -> None:
        (tmp_path / "a.feature").write_text(
            "Feature: A\n  Description for A.\n\n  Scenario: S\n    Given step\n",
            encoding="utf-8",
        )
        (tmp_path / "b.feature").write_text(
            "Feature: B\n  Description for B.\n\n  Scenario: S\n    Given step\n",
            encoding="utf-8",
        )
        exit_code = main([str(tmp_path)])
        assert exit_code == 0

    def test_lint_no_paths(self, capsys: object) -> None:
        exit_code = main([])
        assert exit_code == 0

    def test_lint_json_output(self, tmp_path: Path) -> None:
        feature = tmp_path / "test.feature"
        feature.write_text(
            "Feature: Test\n  A test feature.\n\n  Scenario: S\n    Given step\n",
            encoding="utf-8",
        )
        output_file = tmp_path / "output.json"
        exit_code = main(
            [
                "--output",
                "json",
                "--output-file",
                str(output_file),
                str(feature),
            ]
        )
        assert exit_code == 0
        assert output_file.exists()
        data = json.loads(output_file.read_text(encoding="utf-8"))
        assert "diagnostics" in data
        assert "summary" in data

    def test_lint_fail_on_error(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.feature"
        bad.write_text("Not valid Gherkin\n", encoding="utf-8")
        exit_code = main(["--fail-on", "error", str(bad)])
        # Parse error is ERROR severity, fail_on=error → exit 1
        assert exit_code == 1

    def test_lint_fail_on_off(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.feature"
        bad.write_text("Not valid Gherkin\n", encoding="utf-8")
        exit_code = main(["--fail-on", "off", str(bad)])
        # fail_on=off → always exit 0
        assert exit_code == 0

    def test_lint_mixed_files(self, tmp_path: Path) -> None:
        good = tmp_path / "good.feature"
        good.write_text(
            "Feature: Good\n  A good feature.\n\n  Scenario: S\n    Given step\n",
            encoding="utf-8",
        )
        bad = tmp_path / "bad.feature"
        bad.write_text("Not valid Gherkin\n", encoding="utf-8")
        exit_code = main([str(tmp_path)])
        assert exit_code == 1

    def test_lint_quiet_mode(self, tmp_path: Path, capsys: object) -> None:
        feature = tmp_path / "test.feature"
        feature.write_text(
            "Feature: Test\n  A test feature.\n\n  Scenario: S\n    Given step\n",
            encoding="utf-8",
        )
        exit_code = main(["--quiet", str(feature)])
        assert exit_code == 0
        captured = capsys.readouterr()  # type: ignore[attr-defined]
        assert captured.out == ""

    def test_version(self) -> None:
        try:
            main(["--version"])
        except SystemExit as exc:
            assert exc.code == 0
