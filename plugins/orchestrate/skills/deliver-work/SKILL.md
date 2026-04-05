---
name: deliver-work
description: "Implementation and verification phase. Runs implement → sweep → review → prove-it → complete. Takes a validated feature file from /plan-work and delivers a green PR. Use when the plan is ready and you just need to build it."
user-invocable: true
argument-hint: "<feature file path or issue number>"
---

# Deliver Work

The building half of orchestration. Takes a validated plan and delivers a green PR.

## Input

`$ARGUMENTS` — a feature file path or issue number (assumes plan-work is done).

## Prerequisites

A validated feature file or clear issue with acceptance criteria. If no plan exists, run `/plan-work` first.

## Steps

### Step 0: Read Task List

Run TaskList to see the tasks orchestrate created. Update them as you progress — do not create new ones unless orchestrate missed something.

### 1. Implement
- Invoke `/code` with the feature file path and requirements
- Tell coder NOT to run typecheck/tests — orchestrator handles that
- After first commit: push + invoke `/write-pr` to create a draft PR
- Mark task completed when done

### 2. Sweep
- Invoke `/sweep auto` to check for similar patterns elsewhere
- For bug fixes: same anti-pattern in other files
- For features: consistency check
- Persist results to PR description
- If must-fix items: invoke `/code` to fix

### 3. Review (Required)
- Run project build and test commands
- Invoke `/review`
- Address all findings, loop until clean
- Push after each fix

### 4. Prove It
- Invoke `/prove-it` with the feature file path
- Map every acceptance criterion to evidence
- If gaps: fix and re-prove

### 5. Complete
- Invoke `/write-pr` to update the PR body with final state
- `gh pr ready` to mark for review
- `/drive-pr --once` to fix any CI issues
- Report summary with PR URL and evidence table

## Final Check

Run TaskList. If any task is not `completed`, go back and finish it now.

## PR Lifecycle
- First commit → push + `/write-pr` to create draft PR
- Push incrementally after each fix
- `/write-pr` again before marking ready (updates body with final state)
- Mark ready only after all verification passes
