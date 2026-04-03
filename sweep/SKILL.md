---
name: sweep
description: "Search for similar patterns, anti-patterns, or issues elsewhere in the codebase after a fix or feature. Use after implementing a fix to catch the same bug in other places, or proactively to audit for a known pattern."
user-invocable: true
argument-hint: "<pattern description or 'auto' to derive from recent changes>"
---

# Sweep

After fixing a bug or implementing a feature, search the codebase for similar patterns elsewhere. Prevents whack-a-mole fixes.

## Input

`$ARGUMENTS` — either:
- A description of the pattern to search for (e.g., "unchecked null returns from getUserById")
- `auto` — derive the pattern from the most recent commit or PR diff

## Step 0: Track Progress

Before starting, create a task for each step below using TaskCreate. Chain sequential steps with addBlockedBy. As you work, update each task's status to `in_progress` when starting it and `completed` when done.

## Step 1: Identify the pattern

If `auto`: read the recent diff (`git diff HEAD~1` or `gh pr diff`) and identify:
- The anti-pattern that was fixed (for bug fixes)
- The new pattern that was introduced (for features)
- The contract that changed (for refactors)

State the pattern clearly in one sentence before searching.

## Step 2: Search

Use targeted grep/glob to find similar occurrences. Be specific — don't grep for generic terms. Search for:
- Same function calls with same risky usage
- Same structural pattern (e.g., missing error handling on a specific API)
- Same anti-pattern in related modules

Limit scope to the current repo unless told otherwise.

## Step 3: Classify findings

For each occurrence found:

| Classification | Action |
|---------------|--------|
| **Same bug** — identical anti-pattern, will cause same issue | Flag as must-fix |
| **Similar risk** — same pattern but different context, may or may not be a problem | Flag for review |
| **False positive** — pattern matches but context makes it safe | Skip |

## Step 4: Report

Output a sweep report:

```
## Sweep: [pattern description]

**Source:** [commit/PR that triggered the sweep]

### Must-fix (N)
| File | Line | Description |
|------|------|-------------|
| path/to/file.ts | 42 | Same unchecked return |

### Review (N)
| File | Line | Description |
|------|------|-------------|
| path/to/other.ts | 88 | Similar pattern, different context |

### Clean
N files checked, no additional occurrences.
```

## Step 5: Persist

To prevent duplicate sweeps on the same pattern, append a summary to the PR description or post as a PR comment:

```
### Sweep: [pattern]
Checked N files. Found M must-fix, K review. [Details above / in comments]
```

This lets `/review` and `/pr-review` see that a sweep was already done and skip re-sweeping the same pattern.

## Final Check

Run TaskList. If any task is not `completed`, go back and finish it now.

## Composability

- `/orchestrate` calls `/sweep` between implement and review
- `/pr-review` checks if a sweep was done (look for "### Sweep:" in PR description/comments). If not, run one.
- `/review` can invoke `/sweep` if it finds a concerning pattern during code review
