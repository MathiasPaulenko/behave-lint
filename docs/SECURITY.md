# Security Policy

## Supported Versions

| Version | Supported | Status |
|---|---|---|
| 0.1.x | Yes | Pre-alpha |
| < 0.1 | No | Unreleased |

## Reporting a Vulnerability

If you discover a security vulnerability in behave-lint, please
report it responsibly:

1. **Do not** open a public GitHub issue.
2. Email **security@paulenko.dev** with a description of the
   vulnerability, steps to reproduce, and potential impact.
3. You will receive an acknowledgment within 48 hours.
4. We will investigate and provide a fix timeline within 7 days.

## Security Architecture

behave-lint is a **static analysis tool** — it reads files and
produces reports. It does not:

- Execute code
- Make network requests
- Import user-provided modules (except explicitly installed plugins)
- Use `eval` or `exec`
- Spawn subprocesses

Step definition analysis uses Python's `ast` module (read-only
parsing, no code execution). See ref/ARCHITECTURE.md Section 19 for
full details.

## Plugin Security

Plugins are Python packages installed via `pip install`. Users are
responsible for vetting plugins before installation. Plugin load
failures are isolated — a malicious or buggy plugin cannot crash the
core engine.
