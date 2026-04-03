---
name: prove-it
description: "Prove implementation correctness by mapping every acceptance criterion to concrete evidence (passing tests, command output, code grep). Use after /review passes, before marking a PR ready. Also use standalone when you want proof that work is actually done — not just 'I think it works.'"
user-invocable: true
argument-hint: "[feature-file-path or issue-number]"
---

Verify that the implementation is correct by producing an evidence table mapping each acceptance criterion to concrete proof. No criterion passes on vibes.

## Step 0: Track Progress

Before starting, create a task for each step below using TaskCreate. Chain sequential steps with addBlockedBy. As you work, update each task's status to `in_progress` when starting it and `completed` when done.

## Step 1: Find Acceptance Criteria

Locate the source of truth, checking in order:

1. **Argument provided** — if a feature file path or issue number was given, use that
2. **Feature file** — glob `specs/features/**/*.feature` for files matching the current branch or issue
3. **GitHub issue** — extract from the issue body linked to the current branch (`gh issue view`)
4. **PR description** — fall back to the PR body if no feature file or issue

Extract each discrete criterion as a checklist item. For feature files, each `Scenario:` line is a criterion. For issues, look for checkbox lists, "What needs to happen" sections, or numbered requirements.

## Step 2: Gather Evidence

For each criterion, find ONE of these evidence types (in preference order):

| Evidence Type | How to Find | Proof Standard |
|---|---|---|
| **Test** | Grep test names matching the criterion. Run the specific test and confirm it passes. | Test name + pass output |
| **Build** | Run the project's build/test commands from CLAUDE.md | Green output |
| **Code** | Grep for structural criteria ("type X exists", "field Y renamed", "no Z in codebase") | File:line showing presence/absence |
| **Demo** | Run the binary with appropriate args, capture stdout | Command + output |
| **Screenshot** | For visual/TUI criteria, use `freeze` to capture terminal output as PNG | Image path |

Rules:
- **Read-only.** Don't modify code, create files, or change state. You're verifying, not fixing.
- **Run tests selectively.** Don't run the full suite for each criterion — run targeted tests. Only run the full suite once for the "all tests pass" criterion.
- **Prefer tests over grep.** A passing test is stronger evidence than "the code looks right."
- **Be honest.** If you can't find evidence, mark it unverified. Don't rationalize.

## Step 3: Produce Evidence Table

Output a markdown table:

```
## Verification Report

| # | Criterion | Evidence | Status |
|---|-----------|----------|--------|
| 1 | Standalone sessions render in TUI | test `build_task_table_rows_includes_standalone` passes | PASS |
| 2 | Enter key attaches to standalone | `JoinStandalone` variant in `TaskEnterAction` + test | PASS |
| 3 | Warning modal on inapplicable key | `guard_requires_worktree` sets warning + test | PASS |
| 4 | Init wizard offers shepherd setup | `suggest_shepherd_session_step` at shell.rs:439 | PASS |
| 5 | start_on_launch creates session | No test exercises tmux creation end-to-end | UNVERIFIED |

**Verdict: 4/5 verified, 1 unverified**
```

## Step 4: Verdict

- **ALL PASS** — every criterion has evidence. Report the table and confirm ready for completion.
- **UNVERIFIED items exist** — report the table. List each unverified item with what evidence *would* be needed. Do not block — flag and let the caller decide.
- **FAILURES** — a test that was supposed to pass fails, or code grep contradicts the criterion. This blocks. Report clearly what's wrong.

## Final Check

Run TaskList. If any task is not `completed`, go back and finish it now.

## Integration with /orchestrate

When called from orchestrate, this replaces the self-check step. Return the verdict so orchestrate can decide whether to proceed to PR completion or loop back to implementation.
