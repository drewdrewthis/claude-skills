---
name: plan-feature
description: "Create a feature file with acceptance criteria before implementation. Use when no specs/features/*.feature file exists for the work."
context: fork
user-invocable: true
argument-hint: "[feature description or issue summary]"
---

Create a BDD feature file for: $ARGUMENTS

## First: Intent Check

Before writing anything, run the `/intent` protocol on the request. If the decision is anything other than "proceed," stop and talk to the user before writing the feature file.

## Read Any Spec Guidelines

Before writing any feature file, check for:
- `specs/README.md` or equivalent guidelines
- `docs/TESTING_PHILOSOPHY.md` or similar for test hierarchy

## Requirements Source

Work should be tied to a GitHub issue. If requirements are unclear:
- Ask for the GitHub issue number
- Use `gh issue view <number>` to fetch full context
- The issue description and acceptance criteria are the source of truth

## Build on Existing Patterns

Before specifying new functionality, search for existing patterns and systems in the codebase. Extend what exists rather than building from scratch.

## Output Location
Write to `specs/features/<feature-name>.feature` or the project's equivalent spec directory.

## What Makes a Good Feature File

### Feature Complete
- Captures ALL acceptance criteria from the issue
- Describes ALL user-visible behaviors
- No gaps - if it's not in the feature file, it's not in scope
- This file IS the specification of work to be done

### Non-Overlapping Test Coverage

Each scenario must be tagged with exactly ONE of:

| Tag | What It Tests | Mocking |
|-----|---------------|---------|
| `@e2e` | Happy paths, full system flow | None |
| `@integration` | Edge cases, error handling, module boundaries | External services only |
| `@unit` | Pure logic, branches, single function | Collaborators |

**Critical**: Don't duplicate coverage across levels. If E2E covers the happy path, integration tests edge cases, unit tests logic branches.

## Feature File Format

```gherkin
Feature: <Feature Name>
  As a <role>
  I want <goal>
  So that <benefit>

  # Happy path - full system
  @e2e
  Scenario: User successfully completes main flow
    Given <precondition>
    When <action>
    Then <expected result>

  # Edge cases and error handling
  @integration
  Scenario: Handles invalid input gracefully
    Given <precondition>
    When <invalid action>
    Then <error handling>

  # Pure logic branches
  @unit
  Scenario: Validates input format
    Given <input state>
    When <validation runs>
    Then <specific validation result>
```

## Guidelines

- One invariant per scenario (test one thing)
- Scenarios should be independent
- Focus on behavior, not implementation
- Ask for clarification if requirements are ambiguous

Return the file path when complete.
