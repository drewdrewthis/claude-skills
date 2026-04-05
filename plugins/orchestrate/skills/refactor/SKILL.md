---
name: refactor
description: "Refactor flow: triage complexity → gather criteria → baseline → implement → verify → review → complete. Simple refactors skip challenge/prove-it. Criteria come from the issue body."
user-invocable: true
argument-hint: "<issue number>"
---

# Refactor

Restructure code without changing external behavior. Criteria come from the GitHub issue, not a feature file.

## Shared Protocols

Before any step that touches code, rebase:
```bash
git fetch origin && git rebase origin/main
```

**PR lifecycle:** First commit → push + `/write-pr` to create draft PR. Push after each subsequent commit. `/write-pr` again before marking ready. `gh pr ready` only when done.

## Step 0: Intent + Complexity Triage

1. Run `/intent` on the request. If not "proceed," stop and talk to the user.
2. Fetch the issue: `gh issue view <number> --json title,body,labels`
3. If the issue body contains a `🤖 For Agents` section (inside `<details>` tags), use it as a starting point for affected files, execution order, and implementation plan — skip redundant investigation. But if something doesn't add up, run `/challenge` on the plan before proceeding.

If the plan passes validation, proceed directly — the human already approved it during issue creation. Only stop to ask the user if `/challenge` reveals significant problems or the code has diverged.
4. Run TaskList to see the tasks orchestrate created. Update them as you progress — do not create new ones unless orchestrate missed something.
5. If criteria are vague or missing, comment on the issue asking for specifics and stop.
5. **Classify complexity** — scan the issue scope and affected files:
   - **Simple:** ≤5 files, no public API changes, mechanical restructuring (rename, extract, move, inline). Pipeline: baseline → implement → verify → review → complete.
   - **Complex:** >5 files, public API changes, new abstractions, or cross-module restructuring. Pipeline: baseline → challenge → implement → verify → sweep → review → prove-it → complete.

## Step 1: Baseline

- Run the project's existing test suite and record the result
- This is the behavioral safety net — all existing tests must continue to pass after the refactor
- If tests are already failing, stop and flag to the user

## Step 2: Challenge (complex only)

Skip for simple refactors — the baseline tests are the safety net.

- Invoke `/challenge` with the issue description and criteria
- Focus on: will this break consumers? Are layer boundaries clear? Is scope bounded?
- If issues found: update the issue body and re-challenge

## Step 3: Implement

- Invoke `/code` with the issue URL and explicit criteria
- Tell coder: "This is a refactor — no behavioral changes. Existing tests must keep passing. Do NOT run typecheck/tests."
- Update criterion tasks as each is completed

## Step 4: Verify Behavioral Preservation

- Run the full test suite again
- Compare with baseline — same tests must pass
- New tests are fine. Fewer failures are fine. **New failures are not.**
- If regressions → `/code` to fix (max 3 attempts, then escalate)

## Step 5: Sweep (complex only)

Skip for simple refactors — mechanical restructuring rarely establishes new patterns.

- Invoke `/sweep auto` to apply the new pattern consistently
- If the refactor established a pattern (e.g., service/repo extraction), check if other modules need the same treatment
- Persist results to PR description

## Step 6: Review

Non-negotiable quality gate.

1. Run the project's build and test commands (check CLAUDE.md)
2. Invoke `/review` — runs principles, hygiene, security, test reviewers in parallel
3. Address ALL findings:
   - Must-fix → `/code` immediately
   - Consider → fix or document why not
4. After fixes, run `/review` AGAIN — loop until clean
5. Update affected ADRs or docs

## Step 7: Prove It (complex only)

Skip for simple refactors — passing tests from Step 4 are sufficient proof.

Invoke `/prove-it` with the issue number.

Map each acceptance criterion to concrete proof (code grep showing new structure, passing test suite, command output). No criterion passes on vibes.

- ALL PASS → proceed
- UNVERIFIED → fix gap and re-run
- FAILURES → back to Implement (step 3)

## Step 8: Complete

1. Invoke `/write-pr` to update PR body with final state
2. `gh pr ready`
3. `/drive-pr --once` to fix any CI failures
4. Run TaskList — all tasks must be `completed`
5. Report summary (PR URL, evidence table)

## Boundaries

You delegate, you don't implement. `/code` writes code. `/review` checks quality. `/challenge` stress-tests proposals. `/prove-it` produces evidence.
