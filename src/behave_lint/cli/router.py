"""Command router — routes CLI commands to the appropriate handler.

Commands:
    lint (default) — Lint feature files.
    --list-rules   — List all available rules.
    --explain      — Show documentation for a rule.
    --version      — Print version and exit.

See API.md Section 10 and SPECIFICATION.md Section 10.
"""

from __future__ import annotations

from typing import Protocol

from behave_lint.cli.parser import CLIArgs
from behave_lint.models.rule_metadata import RuleMetadata


class SupportsRuleRegistry(Protocol):
    """Protocol for a registry that can list and look up rules."""

    def get_all(self) -> list[tuple[type, RuleMetadata, str]]: ...

    def get(self, rule_id: str) -> tuple[type, RuleMetadata, str] | None: ...


def route_command(
    args: CLIArgs,
    registry: SupportsRuleRegistry,
) -> int:
    """Route the CLI command based on parsed arguments.

    Args:
        args: Parsed CLI arguments.
        registry: Rule registry for listing/explaining rules.

    Returns:
        Exit code (0 for success, 2 for unknown rule).
    """
    # --list-rules takes priority
    if args.list_rules:
        _print_rules_list(registry, args)
        return 0

    # --explain takes priority
    if args.explain is not None:
        return _print_rule_explanation(registry, args.explain)

    # Default: lint command (handled by coordinator)
    return -1  # sentinel: caller should proceed with lint


def _print_rules_list(
    registry: SupportsRuleRegistry,
    args: CLIArgs,
) -> None:
    """Print the list of available rules.

    Args:
        registry: Rule registry with registered rules.
        args: Parsed CLI arguments (for filtering).
    """
    rules = registry.get_all()
    if not rules:
        print("No rules registered.")
        return

    print(f"{'Rule ID':<10} {'Name':<30} {'Category':<15} {'Severity':<10}")
    print("-" * 70)
    for _rule_class, metadata, _source in sorted(rules, key=lambda r: r[1].rule_id):
        print(
            f"{metadata.rule_id:<10} "
            f"{metadata.name:<30} "
            f"{metadata.category.value:<15} "
            f"{metadata.default_severity.value:<10}"
        )


def _print_rule_explanation(
    registry: SupportsRuleRegistry,
    rule_id: str,
) -> int:
    """Print detailed documentation for a rule.

    Args:
        registry: Rule registry for rule lookup.
        rule_id: The rule ID to explain.

    Returns:
        0 if rule found, 2 if unknown rule ID.
    """
    result = registry.get(rule_id)
    if result is None:
        print(f"Unknown rule ID: '{rule_id}'")
        return 2

    _rule_class, metadata, _source = result

    print(f"Rule: {metadata.rule_id} — {metadata.name}")
    print(f"Title: {metadata.title}")
    print()
    print(f"Description: {metadata.description}")
    print()
    print(f"Category: {metadata.category.value}")
    print(f"Default Severity: {metadata.default_severity.value}")
    print(f"Since: {metadata.since}")
    print()
    print(f"Motivation: {metadata.motivation}")

    if metadata.tags:
        print(f"\nTags: {', '.join(metadata.tags)}")

    if metadata.aliases:
        print(f"\nAliases: {', '.join(metadata.aliases)}")

    if metadata.doc_url:
        print(f"\nDocumentation: {metadata.doc_url}")

    if metadata.experimental:
        print("\nStatus: Experimental")

    if metadata.deprecated:
        print("\nStatus: Deprecated")
        if metadata.replaced_by:
            print(f"Replaced by: {metadata.replaced_by}")

    if metadata.examples:
        print("\nExamples:")
        for i, example in enumerate(metadata.examples, 1):
            print(f"\n  Example {i}: {example.description}")
            print(f"  Before:\n{example.before}")
            print(f"  After:\n{example.after}")

    return 0


__all__ = ["route_command"]
