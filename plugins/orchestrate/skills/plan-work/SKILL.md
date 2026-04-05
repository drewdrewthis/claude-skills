---
name: plan-work
description: "Research and planning phase for features. Runs intent → plan → challenge → readiness gate. Produces a validated feature file ready for /deliver-work. Use before implementation when the problem needs thinking, not just coding."
user-invocable: true
argument-hint: "<issue number or requirements>"
---

# Plan Work

The thinking half of orchestration. Produces a validated, challenged feature file ready for implementation.

## Input

`$ARGUMENTS` — an issue number or requirements description.

## Steps

### Step 0: Track Progress

Before starting, create a task for each step below using TaskCreate. Chain sequential steps with addBlockedBy. As you work, update each task's status to `in_progress` when starting it and `completed` when done.

### 1. Intent Analysis
Run `/intent` on the request. Decide: proceed, propose alternative, clarify, or push back.

### 2. Source of Work
Fetch the GitHub issue if available: `gh issue view <number> --json title,body`

### 3. Plan
- Check if a feature file exists in `specs/` or equivalent
- If not, invoke `/plan-feature` to create one
- Read the feature file to understand acceptance criteria

### 4. Challenge
- Invoke `/challenge` with the feature file
- Look for: hidden assumptions, failure modes, scope creep, missing edge cases
- If significant issues: update the feature file, re-challenge
- If clean: proceed

### 5. Test Review
- Invoke `/test-review` on the feature file
- Validates pyramid placement (`@e2e`, `@integration`, `@unit` tags)
- Fix any violations

### 6. Readiness Gate
Evaluate — don't ask for approval:

**Ready** (proceed): clear acceptance criteria, bounded scope, no unresolved questions.
**Not ready** (stop): vague requirements, missing edge cases, needs discussion.

If not ready: document what's missing on the issue and stop.
If ready: the feature file is the deliverable. Pass it to `/deliver-work` or `/orchestrate`.

## Final Check

Run TaskList. If any task is not `completed`, go back and finish it now.

## Output

A validated feature file path, ready for implementation.
