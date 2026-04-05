---
name: orchestrate
description: "Classify work as bug/feature/refactor, run planning, create tasks from every acceptance criterion, then hand off to implementation. The task list is the contract."
user-invocable: true
argument-hint: "[issue number or requirements]"
---

# Orchestrate

You are the **orchestrator**. You classify, plan, build the task list, and hand off to implementation. The task list is the contract — every acceptance criterion becomes a tracked task.

## Step 1: Get Context

If you have an issue number, fetch it:
```bash
gh issue view <number> --json title,body,labels
```

If the issue body contains a `🤖 For Agents` section (inside `<details>` tags), that section has the root cause analysis, implementation plan, and task list. Use it as a starting point — skip redundant investigation. But if something doesn't add up (stale references, contradictions), run `/challenge` on the plan before proceeding.

If the `🤖 For Agents` plan exists and passes validation, proceed directly to Step 4 — the human already approved the plan during issue creation. Only stop to ask the user if `/challenge` reveals significant problems.

If no issue, use the user's description.

## Step 2: Classify

Check labels, title keywords, and issue body:

| Signal | Classification |
|--------|---------------|
| Label: `bug`. Title contains: fix, bug, broken, crash, error | **Bug** |
| Label: `refactor`. Title contains: refactor, extract, restructure, reorganize, consolidate, migrate, split, decouple | **Refactor** |
| Everything else (new behavior, new UI, new API, new endpoint) | **Feature** |

If ambiguous: new user-facing behavior = feature. Moving existing code without behavior change = refactor. Broken existing behavior = bug.

## Step 3: Plan

Each classification has a different planning step:

| Classification | Planning |
|----------------|----------|
| **Bug** | Read issue for repro steps and expected behavior. No feature file. |
| **Feature** | Invoke `/plan-work $ARGUMENTS`. Read the resulting feature file. |
| **Refactor** | Read issue body for structural acceptance criteria. No feature file. |

## Step 4: Build Task List

This is the critical step. Read the output of planning and create one TaskCreate per acceptance criterion:

**For Features** — read the feature file. Every `Scenario:` line becomes a task. Example:
- Task: "User successfully creates organization" (from `@e2e Scenario: User successfully creates organization`)
- Task: "Returns 400 for missing name" (from `@unit Scenario: Returns 400 for missing name`)

**For Bugs** — create tasks from the issue:
- Task: "Regression test reproduces the bug" (from repro steps)
- Task: "Fix applied, regression test passes"
- One task per expected-behavior assertion if multiple

**For Refactors** — create tasks from the issue's acceptance criteria:
- Task: "Business logic extracted to service layer" (from AC)
- Task: "Router only handles HTTP concerns" (from AC)
- Task: "Existing tests pass without modification" (always implicit)

Then add **phase tasks** chained after the criterion tasks:
- Implement (blocked by all criterion tasks being defined, not completed)
- Review (blocked by Implement)
- Prove It (blocked by Review)
- Complete (blocked by Prove It)

## Step 5: Hand Off to Implementation

| Classification | Action |
|----------------|--------|
| **Bug** | Invoke `/fix-bug $ARGUMENTS` |
| **Feature** | Invoke `/deliver-work` with the feature file path |
| **Refactor** | Invoke `/refactor $ARGUMENTS` |

The implementation skill reads the task list and updates criterion tasks as it completes each one. `/prove-it` at the end verifies every criterion task has evidence.

## Step 6: Final Verification

After implementation returns, run TaskList. If any task is not `completed`, something was missed — go back to the implementation skill with the specific incomplete tasks.
