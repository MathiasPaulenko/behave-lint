# behave-lint — AI Implementation Strategy

> This document defines the implementation strategy for the behave-lint project.
>
> Every AI assistant participating in the development of this repository MUST follow this strategy.
>
> This document is considered the implementation constitution of the project.

---

# Project Vision

The goal of behave-lint is **not** to create another linter.

The goal is to create the reference quality platform for the Behave ecosystem, comparable to tools such as:

- Ruff
- ESLint
- Roslyn
- Clippy
- SonarLint

The project must prioritize:

- Maintainability
- Extensibility
- Performance
- Determinism
- Excellent developer experience
- High-quality documentation
- Clean Architecture
- Long-term evolution

---

# Development Philosophy

The project SHALL NOT be implemented in a single step.

The project SHALL be developed incrementally using a Pull Request-oriented workflow.

Each implementation phase must:

- produce a coherent feature
- be independently reviewable
- include tests
- include documentation
- preserve backward compatibility
- avoid architectural changes unless explicitly requested

Every implementation phase must leave the repository in a working state.

---

# Implementation Model

Development is divided into two major stages.

---

# Stage A — Framework

This stage builds the behave-lint platform.

It focuses on infrastructure.

It does NOT focus on the individual lint rules.

The framework is implemented using ten implementation phases.

---

## PR-01 Foundation

Goal:

Create the production-ready project foundation.

Deliverables:

- package structure
- pyproject
- tooling
- CI
- documentation
- quality tools
- development environment

---

## PR-02 Core Domain

Goal:

Implement the domain model.

Deliverables:

- common models
- dataclasses
- enums
- metadata
- exceptions
- shared types
- interfaces
- contracts

---

## PR-03 Configuration System

Goal:

Implement the configuration engine.

Deliverables:

- configuration loader
- validation
- profiles
- overrides
- discovery
- precedence

---

## PR-04 Diagnostic Engine

Goal:

Implement diagnostics.

Deliverables:

- diagnostics
- severities
- categories
- serialization
- formatting
- reporting model

---

## PR-05 Rule Engine

Goal:

Implement the execution engine.

Deliverables:

- registry
- execution context
- visitors
- scheduling
- execution pipeline
- rule loading

---

## PR-06 CLI

Goal:

Implement the complete command line interface.

Deliverables:

- commands
- help
- progress
- UX
- output selection
- configuration integration

---

## PR-07 Reporters

Goal:

Implement reporting.

Deliverables:

- JSON
- Console
- Markdown
- SARIF
- Reporter API

---

## PR-08 Plugin System

Goal:

Implement extensibility.

Deliverables:

- plugin discovery
- entry points
- registration
- validation
- plugin lifecycle

---

## PR-09 Auto Fix Engine

Goal:

Implement automatic fixes.

Deliverables:

- fix planning
- conflict detection
- preview mode
- rollback
- safe fixes

---

## PR-10 Integration & Quality

Goal:

Prepare version 1.0.

Deliverables:

- integration tests
- benchmarks
- documentation review
- release preparation
- performance validation

---

# Stage B — Built-in Rules

Rules are NOT implemented individually.

Rules MUST be implemented by category.

This significantly improves consistency and maintainability.

Recommended implementation order:

- Project Rules
- Feature Rules
- Background Rules
- Scenario Rules
- Scenario Outline Rules
- Step Rules
- Tags Rules
- Examples Rules
- Tables Rules
- Documentation Rules
- Best Practices Rules
- Performance Rules
- Security Rules

Each implementation phase should produce an entire category of rules.

Never implement isolated rules unless explicitly requested.

---

# Repository Organization

The repository should evolve around these main modules.

- configuration
- diagnostics
- rules
- plugins
- reporters
- cli
- engine
- models
- services
- utils

Each module should remain cohesive and loosely coupled.

---

# AI Development Workflow

Every implementation prompt must follow the same structure.

1. Role
2. Context
3. Project Documents
4. Objective
5. Scope
6. Out of Scope
7. Files to Create
8. Files to Modify
9. Acceptance Criteria
10. Coding Standards
11. Testing Requirements
12. Documentation Requirements
13. Definition of Done
14. Review Checklist

No implementation prompt should omit any of these sections.

---

# Engineering Principles

Always follow:

- SOLID
- DRY
- KISS
- Composition over inheritance
- Explicit is better than implicit
- Strong typing
- High cohesion
- Low coupling

Prefer:

- dataclasses
- pathlib
- typing
- Protocol
- Enum
- immutable objects whenever possible

Avoid unnecessary abstractions.

---

# Quality Requirements

Every implementation phase must include:

- unit tests
- integration tests when applicable
- type hints
- documentation updates
- changelog updates (if applicable)

No feature is complete without tests.

---

# AI Collaboration Strategy

Recommended workflow:

### Architect

Use a reasoning-focused model (for example GLM-5.2 High).

Responsibilities:

- review architecture
- validate implementation
- identify design issues
- verify consistency

### Implementer

Use a coding-focused model (for example Kimi K2.7).

Responsibilities:

- generate production code
- generate tests
- update documentation
- implement requested features

---

# Goal

At every moment the repository should look like a mature open source project.

Every Pull Request should be potentially releasable.

The codebase should remain consistent, maintainable and easy to evolve over many years.

This implementation strategy is mandatory for every future implementation prompt.
