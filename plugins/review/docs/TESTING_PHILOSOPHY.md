# Testing Philosophy

## Core Principles

### Test Behavior, Not Implementation

Focus on **what** the code does, not **how** it does it. Tests should validate user-visible outcomes and contracts, enabling refactoring without rewriting tests.

### No "Should" in Test Names

Use present tense, active voice. Describe expected behavior directly.

| Avoid | Prefer |
|-------|--------|
| `it("should sign up a user")` | `it("signs up a user")` |
| `it("should redirect guests")` | `it("redirects guest users")` |

### Nested Describe for Context

Use nested `describe` blocks to group tests by context/condition:

```
describe("getUserById()", () => {
  describe("when user exists", () => {
    it("returns the user", () => { ... });
  });

  describe("when user does not exist", () => {
    it("returns null", () => { ... });
  });
});
```

### Single Expectation Per Test

Isolating assertions makes failures immediately clear. When multiple behaviors need testing, create separate tests.

## Coverage is Mandatory

Every change ships with tests. No exceptions.

- **Bug fixes** must include a regression test that fails without the fix and passes with it.
- **New features** must have integration and/or unit tests covering acceptance criteria.
- **Refactors** must not reduce existing test coverage.

## Test Hierarchy

Each level has a distinct purpose. Avoid overlap.

| Level | Purpose | Mocking | Quantity |
|-------|---------|---------|----------|
| **E2E** | Catastrophic regression detection for stable core flows | None | Minimal |
| **Integration** | Edge cases, error handling, boundary crossing | External boundaries only | As many as needed |
| **Unit** | Pure logic, branches | Everything | As many as needed |

### Decision Tree

Apply in order. Stop at first match.

```
Is this a core happy path of a stable feature?
  -> E2E (only if not already covered)

Is this testing error handling or edge cases?
  -> Integration (mock boundaries)

Is this a complete user workflow?
  -> Integration

Is this pure logic in isolation?
  -> Unit

Is this a regression from production?
  -> Add at LOWEST sufficient level (unit > integration > e2e)
```

## Mocking Strategy

**Prefer stubs and environment simulation over mocks.**

Mocks test implementation details. When you refactor internals, mock-heavy tests break even though behavior is unchanged. Instead:

- Use stubs for external services
- Use real implementations where practical
- Mock only at external boundaries (APIs, databases, file systems)

## Test Data

**Create minimal, context-specific data.** Only generate data needed for the specific test. Comprehensive setup obscures what's actually being tested.

## Scenario Design

Each test should verify **one invariant**. When deciding whether to extend or create a new test:

- **Extend**: The new assertion is a natural consequence of the same behavior
- **New test**: The assertion tests a distinct invariant that could fail independently

## Regression Policy

When a bug is found:

1. Reproduce with a failing test
2. Add test at the lowest sufficient level
3. Fix and verify green

This keeps the suite lean while ensuring real failures never recur.

## What We Don't Test

- Type definitions
- Simple pass-throughs with no logic
- Third-party library internals
- Constants/config (unless dynamic)
