"""Regression tests for defects found during the production-quality audit.

Each test pins a previously broken behavior: a crash, a silent failure,
or an incorrect semantic that must not come back.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any

import pytest

from behave_lint.cache.manager import CacheManager
from behave_lint.cli.coordinator import run_lint
from behave_lint.cli.parser import CLIArgs
from behave_lint.diagnostics.filters import (
    EnableRegion,
    filter_excluded_files,
    filter_inline_disables,
    parse_disable_comments,
)
from behave_lint.diagnostics.validation import validate_diagnostics
from behave_lint.engine.lint_engine import LintEngine
from behave_lint.infrastructure.file_discovery import discover_files
from behave_lint.infrastructure.project_loader import load_features
from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.models.lint_result import LintResult, LintSummary
from behave_lint.models.rule_metadata import RuleMetadata
from behave_lint.rules.base import Rule
from behave_lint.rules.registry import RuleRegistry
from behave_lint.rules.scope import RuleScope


def _write_feature(path: Path, content: str = "Feature: F\n") -> str:
    path.write_text(content, encoding="utf-8")
    return str(path)


def _make_metadata(rule_id: str = "BC001") -> RuleMetadata:
    return RuleMetadata(
        rule_id=rule_id,
        name="test-rule",
        title="Test Rule",
        description="A test rule.",
        category=Category.CORRECTNESS,
        default_severity=Severity.WARNING,
        motivation="For testing.",
        since="0.1.0",
    )


class TestNonUtf8FeatureFile:
    """A non-UTF-8 .feature file must not crash the whole run."""

    def test_invalid_utf8_produces_parse_diagnostic(self, tmp_path: Path) -> None:
        bad = tmp_path / "latin1.feature"
        bad.write_bytes(b"Feature: caf\xe9\n  Scenario: s\n    Given x\n")
        good = tmp_path / "good.feature"
        _write_feature(good)

        registry = RuleRegistry()
        engine = LintEngine(Config(), registry)
        result = engine.lint([str(tmp_path)])

        # No crash; both files were counted; the bad one got B000.
        assert result.summary.total_files == 2
        assert any(
            d.rule_id == "B000" and d.file_path == str(bad) for d in result.diagnostics
        )

    def test_load_features_reports_real_error(self, tmp_path: Path) -> None:
        bad = tmp_path / "latin1.feature"
        bad.write_bytes(b"\xff\xfe not gherkin \x80")
        result = load_features([str(bad)])
        assert len(result.errors) == 1
        _path, message = result.errors[0]
        assert message != "Failed to parse feature file"
        assert message  # non-empty real message


class TestDiscoveryResilience:
    """Discovery must skip invalid/unreadable paths without crashing."""

    def test_invalid_path_skipped(self) -> None:
        assert discover_files(["nonexistent-dir-xyz"]) == []

    def test_path_with_null_byte_does_not_crash(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            assert discover_files(["a\x00b"]) == []

    def test_mixed_valid_and_invalid_paths(self, tmp_path: Path) -> None:
        _write_feature(tmp_path / "ok.feature")
        found = discover_files(["a\x00b", str(tmp_path)])
        assert len(found) == 1


class TestExecutorStamping:
    """Malformed rule output is dropped, not fatal — for both scopes."""

    def _executor(self) -> tuple[Any, RuleRegistry]:
        from behave_lint.rules.executor import RuleExecutor

        registry = RuleRegistry()
        return RuleExecutor(registry, Config()), registry

    def test_cross_file_invalid_output_does_not_crash(self) -> None:
        executor, registry = self._executor()
        metadata = _make_metadata("BK001")

        class Bad(Rule):
            def check(self, feature: Any, config: Config) -> list[Any]:
                return ["not-a-diagnostic", 42]

        Bad.metadata = metadata
        Bad.scope = RuleScope.CROSS_FILE
        registry.register(Bad)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            diags, _fixes = executor.execute([], project=object())
        assert diags == []

    def test_valid_diags_survive_a_bad_sibling(self, tmp_path: Path) -> None:
        executor, registry = self._executor()
        metadata = _make_metadata("BC001")
        good = Diagnostic(
            rule_id="X",
            severity=Severity.WARNING,
            message="ok",
            file_path=str(tmp_path / "f.feature"),
            line=1,
            category=Category.CORRECTNESS,
        )
        bad = Diagnostic(
            rule_id="X",
            severity=Severity.WARNING,
            message="ok",
            file_path=str(tmp_path / "f.feature"),
            line=1,
            category=Category.CORRECTNESS,
        )
        # Forge an invalid diagnostic past the dataclass checks.
        object.__setattr__(bad, "line", 0)

        class Mixed(Rule):
            def check(self, feature: Any, config: Config) -> list[Any]:
                return [good, bad]

        Mixed.metadata = metadata
        registry.register(Mixed)

        feature = tmp_path / "f.feature"
        _write_feature(feature)
        from behave_lint.infrastructure.project_loader import load_single

        model = load_single(str(feature))
        assert model is not None
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            diags, _ = executor.execute([model])
        assert len(diags) == 1
        assert diags[0].rule_id == "BC001"

    def test_explicit_per_diagnostic_severity_preserved(self, tmp_path: Path) -> None:
        executor, registry = self._executor()
        metadata = _make_metadata("BC001")

        class SeverityRule(Rule):
            def check(self, feature: Any, config: Config) -> list[Any]:
                return [
                    self.diagnostic("explicit error", severity=Severity.ERROR),
                ]

        SeverityRule.metadata = metadata
        registry.register(SeverityRule)

        feature = tmp_path / "f.feature"
        _write_feature(feature)
        from behave_lint.infrastructure.project_loader import load_single

        model = load_single(str(feature))
        assert model is not None
        diags, _ = executor.execute([model])
        assert diags[0].severity is Severity.ERROR

    def test_severity_override_still_wins(self, tmp_path: Path) -> None:
        executor, registry = self._executor()
        metadata = _make_metadata("BC001")

        class SeverityRule(Rule):
            def check(self, feature: Any, config: Config) -> list[Any]:
                return [
                    self.diagnostic("explicit error", severity=Severity.ERROR),
                ]

        SeverityRule.metadata = metadata
        registry.register(SeverityRule)
        executor._config = Config(severity_overrides={"BC001": Severity.INFO})

        feature = tmp_path / "f.feature"
        _write_feature(feature)
        from behave_lint.infrastructure.project_loader import load_single

        model = load_single(str(feature))
        assert model is not None
        diags, _ = executor.execute([model])
        assert diags[0].severity is Severity.INFO

    def test_zero_max_workers_does_not_crash(self, tmp_path: Path) -> None:
        executor, registry = self._executor()
        metadata = _make_metadata("BC001")

        class Ok(Rule):
            def check(self, feature: Any, config: Config) -> list[Any]:
                return []

        Ok.metadata = metadata
        registry.register(Ok)

        feature = tmp_path / "f.feature"
        _write_feature(feature)
        from behave_lint.infrastructure.project_loader import load_single

        model = load_single(str(feature))
        assert model is not None
        diags, _ = executor.execute([model], max_workers=0)
        assert diags == []


class TestCacheResilience:
    """Corrupted cache files must not crash or poison the run."""

    def _diag(self, tmp_path: Path) -> Diagnostic:
        return Diagnostic(
            rule_id="BC001",
            severity=Severity.WARNING,
            message="m",
            file_path=str(tmp_path / "f.feature"),
            line=1,
            category=Category.CORRECTNESS,
        )

    def test_non_object_json_starts_fresh(self, tmp_path: Path) -> None:
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        (cache_dir / "lint_cache.json").write_text("[1, 2, 3]")
        mgr = CacheManager(str(cache_dir), Config())
        assert mgr.get("x", "content") is None

    def test_malformed_entry_skipped_others_kept(self, tmp_path: Path) -> None:
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        data = {
            "version": 1,
            "entries": {
                "good": {
                    "config_hash": "x",
                    "file_path": "a.feature",
                    "diagnostics": [
                        {
                            "rule_id": "BC001",
                            "severity": "warning",
                            "message": "m",
                            "file_path": "a.feature",
                            "line": 1,
                            "category": "correctness",
                        }
                    ],
                },
                "bad-severity": {
                    "config_hash": "x",
                    "file_path": "b.feature",
                    "diagnostics": [
                        {
                            "rule_id": "BC001",
                            "severity": "critical",
                            "message": "m",
                            "file_path": "b.feature",
                            "line": 1,
                            "category": "correctness",
                        }
                    ],
                },
                "not-an-object": 42,
            },
        }
        (cache_dir / "lint_cache.json").write_text(json.dumps(data))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mgr = CacheManager(str(cache_dir), Config())
        assert "good" in mgr._entries
        assert "bad-severity" not in mgr._entries
        assert "not-an-object" not in mgr._entries

    def test_roundtrip_still_works(self, tmp_path: Path) -> None:
        cache_dir = tmp_path / "cache"
        mgr = CacheManager(str(cache_dir), Config())
        mgr.put("f.feature", "content", [self._diag(tmp_path)])
        mgr.save()
        assert not (cache_dir / "lint_cache.tmp").exists()
        mgr2 = CacheManager(str(cache_dir), Config())
        hit = mgr2.get("f.feature", "content")
        assert hit is not None and len(hit) == 1


class TestInlineDisableSemantics:
    """`on RULE` inside a global `off` re-enables only that rule."""

    def test_on_rule_inside_global_off(self) -> None:
        lines = [
            "# behave-lint: off",
            "Feature: F",
            "# behave-lint: on BC001",
            "  Scenario: s",
        ]
        regions = parse_disable_comments(lines)
        disables = [r for r in regions if not isinstance(r, EnableRegion)]
        enables = [r for r in regions if isinstance(r, EnableRegion)]

        # Global off stays open through EOF.
        assert any(r.is_disabled("BS001", 4) for r in disables), (
            "other rules must stay disabled"
        )
        # BC001 is re-enabled from line 3.
        assert any(r.reenables("BC001", 4) for r in enables)

    def test_filter_respects_partial_reenable(self, tmp_path: Path) -> None:
        path = str(tmp_path / "f.feature")
        diags = [
            Diagnostic(
                rule_id="BC001",
                severity=Severity.WARNING,
                message="m",
                file_path=path,
                line=4,
                category=Category.CORRECTNESS,
            ),
            Diagnostic(
                rule_id="BS001",
                severity=Severity.WARNING,
                message="m",
                file_path=path,
                line=4,
                category=Category.STYLE,
            ),
        ]
        lines = [
            "# behave-lint: off",
            "Feature: F",
            "# behave-lint: on BC001",
            "  Scenario: s",
        ]
        filtered = filter_inline_disables(diags, {path: lines})
        assert [d.rule_id for d in filtered] == ["BC001"]

    def test_docstring_directives_ignored(self, tmp_path: Path) -> None:
        lines = [
            "Feature: F",
            "  Scenario: s",
            "    Given step",
            '    """',
            "    # behave-lint: off",
            '    """',
            "    Then other",
        ]
        regions = parse_disable_comments(lines)
        assert regions == []

    def test_on_specific_closes_only_that_rule(self) -> None:
        lines = [
            "# behave-lint: off BC001,BS001",
            "Feature: F",
            "# behave-lint: on BC001",
            "  Scenario: s",
        ]
        regions = parse_disable_comments(lines)
        # BS001 must remain disabled through EOF; BC001 region closed.
        bs_still_off = any(r.is_disabled("BS001", 4) for r in regions)
        assert bs_still_off


class TestExcludedFilesFilter:
    def test_prefix_exclusion_matches_discovery(self) -> None:
        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.WARNING,
            message="m",
            file_path="features/wip/x.feature",
            line=1,
            category=Category.CORRECTNESS,
        )
        assert filter_excluded_files([diag], ["features/wip"]) == []

    def test_glob_still_works(self) -> None:
        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.WARNING,
            message="m",
            file_path="features/wip/x.feature",
            line=1,
            category=Category.CORRECTNESS,
        )
        assert filter_excluded_files([diag], ["**/wip/**"]) == []


class TestModelIntegrity:
    def test_lint_result_properties_follow_diagnostics(self) -> None:
        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.ERROR,
            message="m",
            file_path="f.feature",
            line=1,
            category=Category.CORRECTNESS,
        )
        result = LintResult(diagnostics=[diag], summary=LintSummary())
        assert result.has_errors is True
        assert result.has_diagnostics is True

    def test_end_column_before_column_rejected(self) -> None:
        with pytest.raises(ValueError, match="end_column"):
            Diagnostic(
                rule_id="BC001",
                severity=Severity.WARNING,
                message="m",
                file_path="f.feature",
                line=1,
                category=Category.CORRECTNESS,
                column=10,
                end_line=1,
                end_column=5,
            )

    def test_validate_diagnostics_drops_non_diagnostic(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            assert validate_diagnostics(["not a diag", 42]) == []


class TestUnknownRuleIds:
    """Unknown rule IDs in config must fail fast with exit code 2."""

    def test_select_unknown_rule_exits_2(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _write_feature(tmp_path / "f.feature")
        args = CLIArgs(paths=[str(tmp_path)], select=["TYP999"])
        code = run_lint(args)
        assert code == 2
        err = capsys.readouterr().err
        assert "Unknown rule" in err

    def test_close_match_suggests_rule(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _write_feature(tmp_path / "f.feature")
        args = CLIArgs(paths=[str(tmp_path)], select=["bc001"])
        code = run_lint(args)
        assert code == 2
        assert "did you mean" in capsys.readouterr().err

    def test_parse_error_rule_id_is_valid(self, tmp_path: Path) -> None:
        _write_feature(tmp_path / "f.feature")
        args = CLIArgs(paths=[str(tmp_path)], select=["B000"])
        assert run_lint(args) != 2


class TestReporterManager:
    def test_multi_file_format_single_output_errors(self, tmp_path: Path) -> None:
        from behave_lint.reporters.manager import ReporterManager

        mgr = ReporterManager()
        result = LintResult()
        with pytest.raises(ValueError, match="single"):
            mgr.render(
                result,
                ["json", "sarif"],
                str(tmp_path / "out.txt"),
            )


class TestWatchMode:
    def test_uppercase_extension_triggers(self) -> None:
        from behave_lint.cli.watch import WatchMode

        calls: list[int] = []
        mode = WatchMode(CLIArgs(), ["x"])
        mode._lint_once = lambda: calls.append(1) or 0  # type: ignore[method-assign]
        mode.on_change("dir/FILE.FEATURE")
        mode.on_change("dir/other.txt")
        assert len(calls) == 1


class TestStepDefinitionRegexCache:
    def test_pattern_to_regex_is_cached(self) -> None:
        from behave_lint.models.step_definition import pattern_to_regex

        assert pattern_to_regex("a {x} b") is pattern_to_regex("a {x} b")


class TestSarifUris:
    def test_windows_path_uses_forward_slashes(self) -> None:
        from behave_lint.reporters.sarif import SARIFReporter

        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.WARNING,
            message="m",
            file_path="features\\sub\\f.feature",
            line=1,
            category=Category.CORRECTNESS,
        )
        results = SARIFReporter._build_results(LintResult(diagnostics=[diag]))
        uri = results[0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]  # type: ignore[index]
        assert uri == "features/sub/f.feature"


class TestKeywordOrderingFix:
    """BS002 fixes must preserve multi-line step content (docstrings, tables)."""

    def test_docstring_travels_with_its_step(self, tmp_path: Path) -> None:
        from behave_lint.infrastructure.project_loader import load_single
        from behave_lint.rules.builtin.style import KeywordOrderingRule

        content = (
            "Feature: F\n"
            "  Scenario: s\n"
            "    When act\n"
            '      """\n'
            "      doc content here\n"
            '      """\n'
            "    Given a\n"
            "    Then done\n"
        )
        path = _write_feature(tmp_path / "f.feature", content)
        model = load_single(path)
        rule = KeywordOrderingRule()
        config = Config()
        diagnostics = rule.check(model, config)
        fixes = rule.get_fixes(model, config, diagnostics)

        assert len(fixes) == 1
        fix = fixes[0]
        assert "doc content here" in fix.new_text
        # No content lost: the reordered text covers the same lines.
        assert fix.new_text.count("\n") == fix.old_text.count("\n")
        assert fix.new_text.index("Given a") < fix.new_text.index("When act")

    def test_fix_skipped_when_last_step_has_docstring(self, tmp_path: Path) -> None:
        from behave_lint.infrastructure.project_loader import load_single
        from behave_lint.rules.builtin.style import KeywordOrderingRule

        content = (
            "Feature: F\n"
            "  Scenario: s\n"
            "    Then early\n"
            "    Given late\n"
            '      """\n'
            "      trailing doc\n"
            '      """\n'
        )
        path = _write_feature(tmp_path / "f.feature", content)
        model = load_single(path)
        rule = KeywordOrderingRule()
        config = Config()
        diagnostics = rule.check(model, config)
        fixes = rule.get_fixes(model, config, diagnostics)

        assert fixes == []


class TestTagFixTokenBoundary:
    """Tag fixes must replace whole tokens, not substrings of other tags."""

    def test_tag_casing_fix_preserves_sibling_tag(self, tmp_path: Path) -> None:
        from behave_lint.infrastructure.project_loader import load_single
        from behave_lint.rules.builtin.style import TagCasingRule

        path = _write_feature(tmp_path / "f.feature", "@Smoke @Smoker\nFeature: F\n")
        model = load_single(path)
        rule = TagCasingRule()
        config = Config()
        diagnostics = rule.check(model, config)
        fixes = rule.get_fixes(model, config, diagnostics)

        new_texts = {f.new_text for f in fixes}
        assert "@smoke @Smoker\n" in new_texts
        assert "@Smoke @smoker\n" in new_texts


class TestLineRulesSkipDocstrings:
    """Line-oriented rules must not treat docstring content as Gherkin."""

    _DOCSTRING_FEATURE = (
        "Feature: F\n"
        "  Scenario: s\n"
        "    Given x\n"
        '      """\n'
        "      given inside doc   \n"
        "\t      more content\n"
        '      """\n'
        "    Then ok\n"
    )

    def test_keyword_casing_ignores_docstring(self, tmp_path: Path) -> None:
        from behave_lint.infrastructure.project_loader import load_single
        from behave_lint.rules.builtin.style import StepKeywordCasingRule

        path = _write_feature(tmp_path / "f.feature", self._DOCSTRING_FEATURE)
        model = load_single(path)
        assert StepKeywordCasingRule().check(model, Config()) == []

    def test_trailing_whitespace_ignores_docstring(self, tmp_path: Path) -> None:
        from behave_lint.infrastructure.project_loader import load_single
        from behave_lint.rules.builtin.style import TrailingWhitespaceRule

        path = _write_feature(tmp_path / "f.feature", self._DOCSTRING_FEATURE)
        model = load_single(path)
        assert TrailingWhitespaceRule().check(model, Config()) == []

    def test_tab_indentation_ignores_docstring(self, tmp_path: Path) -> None:
        from behave_lint.infrastructure.project_loader import load_single
        from behave_lint.rules.builtin.style import TabIndentationRule

        path = _write_feature(tmp_path / "f.feature", self._DOCSTRING_FEATURE)
        model = load_single(path)
        assert TabIndentationRule().check(model, Config()) == []


class TestEuroDatePattern:
    def test_euro_sign_detected(self) -> None:
        from behave_lint.rules.builtin.i18n import _LOCALE_SPECIFIC_PATTERN

        assert _LOCALE_SPECIFIC_PATTERN.search("the price is €99")
        assert _LOCALE_SPECIFIC_PATTERN.search("cost €100 today")


class TestStepDefinitionLoaderResilience:
    def test_invalid_encoding_file_skipped(self, tmp_path: Path) -> None:
        from behave_lint.infrastructure.step_definitions import (
            load_step_definitions,
        )

        bad = tmp_path / "bad.py"
        bad.write_bytes(b"\xff\xfe invalid \x80")
        good = tmp_path / "good.py"
        good.write_text("@given('a user')\ndef f(ctx):\n    pass\n")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            defs = load_step_definitions(str(tmp_path))
        assert len(defs) == 1

    def test_null_byte_file_skipped(self, tmp_path: Path) -> None:
        from behave_lint.infrastructure.step_definitions import (
            load_step_definitions,
        )

        bad = tmp_path / "nul.py"
        bad.write_bytes(b"x = 1\x00\n")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            assert load_step_definitions(str(bad)) == []


class TestConsoleAnsiPadding:
    def test_message_column_stable_with_color(self) -> None:
        import re

        from behave_lint.reporters.console import ConsoleReporter

        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.WARNING,
            message="hello",
            file_path="f.feature",
            line=1,
            category=Category.CORRECTNESS,
        )
        colored = ConsoleReporter(use_color=True)._format_diagnostic(diag)
        plain = ConsoleReporter(use_color=False)._format_diagnostic(diag)

        ansi_stripped = re.sub(r"\x1b\[[0-9;]*m", "", colored)
        assert ansi_stripped == plain
        assert plain.index("hello") == 64


class TestEnvGroupBeatsToml:
    """BEHAVE_LINT_GROUP must override a TOML `group` (documented precedence)."""

    def test_env_group_replaces_toml_group(self, tmp_path: Path) -> None:
        from behave_lint.configuration.loader import load_config

        toml = tmp_path / "pyproject.toml"
        toml.write_text('[tool.behave-lint]\ngroup = ["style"]\n', encoding="utf-8")

        config = load_config(
            config_path=str(toml), env={"BEHAVE_LINT_GROUP": "security"}
        )
        assert config.group == ["security"]


class TestExtendsMissingSection:
    """extends -> pyproject.toml without [tool.behave-lint] is a clear error."""

    def test_clear_error(self, tmp_path: Path) -> None:
        from behave_lint.configuration.loader import load_config
        from behave_lint.exceptions import ConfigError

        parent_dir = tmp_path / "parent"
        parent_dir.mkdir()
        parent = parent_dir / "pyproject.toml"
        parent.write_text('[project]\nname = "x"\n', encoding="utf-8")
        child = tmp_path / "pyproject.toml"
        child.write_text(
            '[tool.behave-lint]\nextends = "parent/pyproject.toml"\n',
            encoding="utf-8",
        )

        with pytest.raises(ConfigError, match="behave-lint"):
            load_config(config_path=str(child))

    def test_parent_with_other_tool_table_errors(self, tmp_path: Path) -> None:
        from behave_lint.configuration.loader import load_config
        from behave_lint.exceptions import ConfigError

        parent = tmp_path / "shared.toml"
        parent.write_text("[tool.ruff]\nline-length = 88\n", encoding="utf-8")
        child = tmp_path / "pyproject.toml"
        child.write_text(
            '[tool.behave-lint]\nextends = "shared.toml"\n', encoding="utf-8"
        )

        with pytest.raises(ConfigError, match="behave-lint"):
            load_config(config_path=str(child))


class TestStringListElementValidation:
    """Non-string elements in list config keys raise a config error."""

    def test_paths_non_string_element(self, tmp_path: Path) -> None:
        from behave_lint.configuration.loader import load_config
        from behave_lint.exceptions import InvalidConfigValueError

        toml = tmp_path / "pyproject.toml"
        toml.write_text("[tool.behave-lint]\npaths = [1, 2]\n", encoding="utf-8")

        with pytest.raises(InvalidConfigValueError):
            load_config(config_path=str(toml), env={})

    def test_select_non_string_element(self, tmp_path: Path) -> None:
        from behave_lint.configuration.loader import load_config
        from behave_lint.exceptions import InvalidConfigValueError

        toml = tmp_path / "pyproject.toml"
        toml.write_text('[tool.behave-lint]\nselect = ["BC001", 5]\n', encoding="utf-8")

        with pytest.raises(InvalidConfigValueError):
            load_config(config_path=str(toml), env={})


class TestFindConfigFileInvalidPath:
    """An explicit config path with invalid chars raises ConfigError."""

    def test_null_byte_path(self) -> None:
        from behave_lint.configuration.discovery import find_config_file
        from behave_lint.exceptions import ConfigError

        with pytest.raises(ConfigError):
            find_config_file(explicit_path="bad\x00config.toml")


class TestAutofixEolPreservation:
    """Fix application must preserve the file's original EOL style."""

    def _make_edit(self, path: Path, old: str, new: str, line: int) -> Any:
        from behave_lint.autofix.models import FixEdit
        from behave_lint.models.enums import AutoFixCapability

        return FixEdit(
            file_path=str(path),
            start_line=line,
            end_line=line,
            old_text=old,
            new_text=new,
            safety=AutoFixCapability.SAFE,
            rule_id="BS007",
            diagnostic_line=line,
        )

    def test_crlf_preserved(self, tmp_path: Path) -> None:
        from behave_lint.autofix.coordinator import FixCoordinator

        path = tmp_path / "f.feature"
        path.write_bytes(b"Feature: F\r\n  Scenario: S\r\n")
        edit = self._make_edit(path, "Feature: F\n", "Feature: G\n", 1)

        result = FixCoordinator().apply_edits([edit])
        assert result.applied_count == 1
        data = path.read_bytes()
        assert data == b"Feature: G\r\n  Scenario: S\r\n"

    def test_lf_untouched(self, tmp_path: Path) -> None:
        from behave_lint.autofix.coordinator import FixCoordinator

        path = tmp_path / "f.feature"
        path.write_bytes(b"Feature: F\n  Scenario: S\n")
        edit = self._make_edit(path, "Feature: F\n", "Feature: G\n", 1)

        result = FixCoordinator().apply_edits([edit])
        assert result.applied_count == 1
        assert path.read_bytes() == b"Feature: G\n  Scenario: S\n"

    def test_no_stray_tmp_file(self, tmp_path: Path) -> None:
        from behave_lint.autofix.coordinator import FixCoordinator

        path = tmp_path / "f.feature"
        path.write_bytes(b"Feature: F\n")
        edit = self._make_edit(path, "Feature: F\n", "Feature: G\n", 1)

        FixCoordinator().apply_edits([edit])
        leftovers = [p for p in tmp_path.iterdir() if p.name != "f.feature"]
        assert leftovers == []


class TestMarkdownPipeEscaping:
    """Pipes in file paths must not break the Markdown table."""

    def test_pipe_in_path_escaped(self, tmp_path: Path) -> None:
        from behave_lint.reporters.markdown import MarkdownReporter

        diag = Diagnostic(
            rule_id="BC001",
            severity=Severity.WARNING,
            message="m",
            file_path="we|ird.feature",
            line=1,
            category=Category.CORRECTNESS,
        )
        summary = LintSummary(total_files=1)
        result = LintResult(diagnostics=[diag], summary=summary)

        out = tmp_path / "r.md"
        MarkdownReporter().render(result, output_file=str(out))
        assert "we\\|ird.feature" in out.read_text(encoding="utf-8")
