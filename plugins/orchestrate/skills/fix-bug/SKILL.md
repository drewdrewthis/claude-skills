---
name: fix-bug
description: "Bug fix flow: readiness check → investigate → failing test (TDD) → fix → verify → review → complete. Skips planning — fixes existing behavior, not new behavior."
user-invocable: true
argument-hint: "<issue number>"
---

# Fix Bug

Fix a bug with TDD: reproduce it, write a failing test, fix it, prove the fix.

## Shared Protocols

Before any step that touches code, rebase:
```bash
git fetch origin && git rebase origin/main
```

**PR lifecycle:** First commit → push + `/write-pr` to create draft PR. Push after each subsequent commit. `/write-pr` again before marking ready. `gh pr ready` only when done.

## Step 0: Intent + Context

1. Run `/intent` on the request. If not "proceed," stop and talk to the user.
2. Fetch the issue: `gh issue view <number> --json title,body,labels`
3. Run TaskList to see the tasks orchestrate created. Update them as you progress — do not create new ones unless orchestrate missed something.

## Step 1: Readiness Check

The issue must include **reproduction steps** — specific actions that trigger the bug.

**Ready**: Clear steps to reproduce, expected vs actual behavior described.
**Not ready**: No repro steps, vague symptoms. Comment asking for specifics and stop.

## Step 2: Investigate

- First check: does the issue body contain a `🤖 For Agents` section with root cause analysis and implementation plan? If yes, **use it as a starting point** — skip redundant investigation. But if something doesn't add up (stale line numbers, missing files, contradictions), run `/challenge` on the plan before proceeding.
- If no agent plan exists: delegate to `/code` (or Explore agent) to find the root cause
- Identify affected code paths and the specific defect

If the `🤖 For Agents` plan exists and passes validation, proceed directly — the human already approved the plan during issue creation. Only stop to ask the user if `/challenge` reveals significant problems or the code has diverged from what the plan describes.

## Step 3: Write Failing Regression Test (TDD)

- Delegate to `/code` to write a test that **reproduces the bug**
- The test MUST be run and MUST fail — proves it catches the bug
- Choose the right level:
  - Runtime crash → integration test (execute the crashing path)
  - Wrong output → unit test may suffice
  - UI issue → browser test
- If the test passes without a fix, the test is wrong — rewrite it

## Step 4: Fix

- Delegate to `/code` to apply the minimal fix
- Tell coder NOT to run typecheck or tests — orchestrator handles that

## Step 5: Verify

- Run the regression test — it MUST now pass
- Max 3 attempts, then escalate to user

## Step 6: Sweep

- Invoke `/sweep auto` to find the same anti-pattern elsewhere
- If must-fix items found → `/code` to fix

## Step 7: Review

Non-negotiable quality gate.

1. Run the project's build and test commands (check CLAUDE.md)
2. Invoke `/review` — runs principles, hygiene, security, test reviewers in parallel
3. Address ALL findings:
   - Must-fix → `/code` immediately
   - Consider → fix or document why not
4. After fixes, run `/review` AGAIN — loop until clean
5. Update affected ADRs or docs

## Step 8: Prove It

Invoke `/prove-it` with the issue number.

Map each criterion to concrete proof (passing test, command output, code grep). No criterion passes on vibes.

- ALL PASS → proceed
- UNVERIFIED → fix gap and re-run
- FAILURES → back to Fix (step 4)

## Step 9: Complete

1. Invoke `/write-pr` to update PR body with final state
2. `gh pr ready`
3. `/drive-pr --once` to fix any CI failures
4. Run TaskList — all tasks must be `completed`
5. Report summary (PR URL, evidence table)

## Boundaries

You delegate, you don't implement. `/code` writes code. `/review` checks quality. `/prove-it` produces evidence.
