"""Regression tests for bugs found in the v2.4.x audit.

Each test reproduces a confirmed defect that was previously not
covered: cross-file rules receiving no project model, cache path
misattribution, parse errors filtered by --select, ignored config
fields, and unsafe category prefix matching.
"""

from __future__ import annotations

from pathlib import Path

from behave_lint.cli.coordinator import _run_lint
from behave_lint.cli.exit_codes import determine_exit_code
from behave_lint.cli.parser import CLIArgs
from behave_lint.configuration.loader import load_config
from behave_lint.diagnostics.filters import (
    filter_disabled_rules,
    parse_disable_comments,
)
from behave_lint.engine.lint_engine import LintEngine
from behave_lint.models.config import Config
from behave_lint.models.diagnostic import Diagnostic
from behave_lint.models.enums import Category, Severity
from behave_lint.rules.builtin import register_builtins
from behave_lint.rules.registry import RuleRegistry

_FEATURE = "Feature: {name}\n\n  Scenario: S\n    Given a step\n"


def _engine(config: Config) -> LintEngine:
    registry = RuleRegistry()
    register_builtins(registry)
    return LintEngine(config, registry)


def test_cross_file_rule_detects_duplicate_features(tmp_path: Path) -> None:
    """BC005 must see the whole project, not a single feature."""
    for name in ("a.feature", "b.feature"):
        (tmp_path / name).write_text(_FEATURE.format(name="Dup"), encoding="utf-8")
    config = Config(select=("BC005",))
    result = _engine(config).lint([str(tmp_path)], use_cache=False)
    assert [d.rule_id for d in result.diagnostics] == ["BC005"]


def test_cache_remaps_file_path_for_identical_content(tmp_path: Path) -> None:
    """A second file with identical content must not inherit the
    first file's path in cached diagnostics."""
    content = "Feature: X\n\n  Scenario: S\n    Given a user.\n"
    (tmp_path / "first.feature").write_text(content, encoding="utf-8")
    (tmp_path / "second.feature").write_text(content, encoding="utf-8")
    config = Config(select=("BD005",), cache_dir=str(tmp_path / ".cache"))
    engine = _engine(config)
    engine.lint([str(tmp_path)])
    engine2 = _engine(config)
    result = engine2.lint([str(tmp_path)])
    paths = {d.file_path for d in result.diagnostics}
    assert any(p.endswith("second.feature") for p in paths)
    assert any(p.endswith("first.feature") for p in paths)


def test_parse_error_survives_select(tmp_path: Path) -> None:
    """B000 parse errors must not be filtered out by --select."""
    bad = tmp_path / "bad.feature"
    bad.write_text("not gherkin ::::\n", encoding="utf-8")
    config = Config(select=("BS001",))
    result = _engine(config).lint([str(bad)], use_cache=False)
    assert any(d.rule_id == "B000" for d in result.diagnostics)


def test_filter_disabled_rules_keeps_b000() -> None:
    diag = Diagnostic(
        rule_id="B000",
        severity=Severity.ERROR,
        message="parse failed",
        file_path="x.feature",
        line=1,
        category=Category.CORRECTNESS,
    )
    config = Config(select=("BS001",))
    assert filter_disabled_rules([diag], config) == [diag]


def test_inline_disable_supports_long_prefixes() -> None:
    """# behave-lint: off BSEC001 must only disable BSEC001, not all."""
    lines = ["# behave-lint: off BSEC001"]
    regions = parse_disable_comments(lines)
    assert len(regions) == 1
    assert regions[0].rule_ids == frozenset({"BSEC001"})


def test_config_exclude_is_honored(tmp_path: Path) -> None:
    """``exclude`` in configuration must skip matching files."""
    wip = tmp_path / "wip"
    wip.mkdir()
    (tmp_path / "a.feature").write_text(_FEATURE.format(name="A"), encoding="utf-8")
    (wip / "b.feature").write_text(_FEATURE.format(name="B"), encoding="utf-8")
    config = Config(exclude=(str(wip),))
    result = _engine(config).lint([str(tmp_path)], use_cache=False)
    assert result.summary.total_files == 1


def test_rule_params_from_config(tmp_path: Path) -> None:
    """``[tool.behave-lint.rules.BX001]`` params must reach the rule."""
    content = (
        "Feature: X\n\n  Scenario: S\n    Given one\n    When two\n    Then three\n"
    )
    (tmp_path / "x.feature").write_text(content, encoding="utf-8")
    config = Config(select=("BX001",), rule_params={"BX001": {"max_steps": 1}})
    result = _engine(config).lint([str(tmp_path)], use_cache=False)
    assert [d.rule_id for d in result.diagnostics] == ["BX001"]


def test_group_style_does_not_include_security() -> None:
    """The ``style`` group must not match BSEC rules via the ``BS`` prefix."""
    config = load_config(
        overrides={"group": ["style"]}, env={}, start_dir=Path("/nonexistent")
    )
    assert not any(r.startswith("BSEC") for r in config.select)
    assert all(r.startswith("BS") for r in config.select)


def test_group_complexity_exists() -> None:
    config = load_config(
        overrides={"group": ["complexity"]}, env={}, start_dir=Path("/nonexistent")
    )
    assert sorted(config.select) == [
        "BX001",
        "BX002",
        "BX003",
        "BX004",
        "BX005",
        "BX006",
    ]


def test_extends_merges_parent_config(tmp_path: Path) -> None:
    """``extends`` must load and merge a parent config file."""
    parent = tmp_path / "base.toml"
    parent.write_text(
        '[tool.behave-lint]\nselect = ["BC001", "BC002"]\n', encoding="utf-8"
    )
    child_dir = tmp_path / "child"
    child_dir.mkdir()
    child = child_dir / "pyproject.toml"
    child.write_text('[tool.behave-lint]\nextends = "../base.toml"\n', encoding="utf-8")
    config = load_config(config_path=str(child), env={})
    assert set(config.select) == {"BC001", "BC002"}


def test_extends_missing_file_raises(tmp_path: Path) -> None:
    child = tmp_path / "pyproject.toml"
    child.write_text('[tool.behave-lint]\nextends = "missing.toml"\n', encoding="utf-8")
    import pytest

    from behave_lint.exceptions import ConfigError

    with pytest.raises(ConfigError):
        load_config(config_path=str(child), env={})


def test_max_warnings_forces_failure() -> None:
    diag = Diagnostic(
        rule_id="BS001",
        severity=Severity.WARNING,
        message="w",
        file_path="x.feature",
        line=1,
        category=Category.STYLE,
    )
    assert determine_exit_code([diag], Severity.ERROR, max_warnings=0) == 1
    assert determine_exit_code([diag], Severity.ERROR, max_warnings=5) == 0


def test_config_output_used_when_no_flag(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    """``output`` in configuration must apply when --output is absent."""
    feature = tmp_path / "x.feature"
    feature.write_text(_FEATURE.format(name="X"), encoding="utf-8")
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.behave-lint]\noutput = "json"\nselect = ["BC001"]\n',
        encoding="utf-8",
    )
    args = CLIArgs(
        paths=[str(feature)],
        config=str(pyproject),
        no_cache=True,
    )
    _run_lint(args, [str(feature)])
    out = capsys.readouterr().out
    assert '"schemaVersion"' in out


def test_step_definitions_undefined_step(tmp_path: Path) -> None:
    """With step-definitions configured, BD001 flags unmatched steps."""
    steps_dir = tmp_path / "steps"
    steps_dir.mkdir()
    (steps_dir / "login.py").write_text(
        'from behave import given\n\n\n@given("a user")\ndef f(ctx):\n    pass\n',
        encoding="utf-8",
    )
    (tmp_path / "f.feature").write_text(
        "Feature: X\n\n  Scenario: S\n    Given a user\n    When something undefined\n",
        encoding="utf-8",
    )
    config = Config(select=("BD001",), step_definitions=str(steps_dir))
    result = _engine(config).lint([str(tmp_path)], use_cache=False)
    ids = [(d.rule_id, d.line) for d in result.diagnostics]
    assert ids == [("BD001", 5)]


def test_step_definitions_ambiguous(tmp_path: Path) -> None:
    """BD002 flags steps matching more than one definition."""
    steps_dir = tmp_path / "steps"
    steps_dir.mkdir()
    (steps_dir / "s.py").write_text(
        "from behave import given, step\n\n\n"
        '@given("a user")\ndef f1(ctx):\n    pass\n\n\n'
        '@step("a user")\ndef f2(ctx):\n    pass\n',
        encoding="utf-8",
    )
    (tmp_path / "f.feature").write_text(
        "Feature: X\n\n  Scenario: S\n    Given a user\n",
        encoding="utf-8",
    )
    config = Config(select=("BD002",), step_definitions=str(steps_dir))
    result = _engine(config).lint([str(tmp_path)], use_cache=False)
    assert [d.rule_id for d in result.diagnostics] == ["BD002"]


def test_config_fail_on_used_when_no_flag(tmp_path: Path) -> None:
    """``fail-on`` in configuration must drive the exit code."""
    feature = tmp_path / "x.feature"
    feature.write_text(
        "Feature: X\n\n  Scenario: S\n    Given a user.\n",
        encoding="utf-8",
    )
    pyproject = tmp_path / "pyproject.toml"
    # BD005 is a warning; fail_on=error means warnings must not fail.
    pyproject.write_text(
        '[tool.behave-lint]\nfail-on = "error"\nselect = ["BD005"]\n',
        encoding="utf-8",
    )
    args = CLIArgs(
        paths=[str(feature)],
        config=str(pyproject),
        no_cache=True,
        quiet=True,
    )
    exit_code = _run_lint(args, [str(feature)])
    assert exit_code == 0
