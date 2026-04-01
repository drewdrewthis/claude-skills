---
name: drive-pr
description: "Drive a PR to mergeable state — fix CI failures and address review comments. Loops until green."
user-invocable: true
argument-hint: "[--once]"
---

# Drive PR

Drive the current branch's PR to mergeable state by fixing CI failures and addressing review comments. Loops until both are green.

## Flow

```
┌─► Check for unresolved review comments (FIRST)
│         │
│    none ▼ found
│    ┌────┴────┐
│    │         │
│    │    Triage, fix, reply, push
│    │         │
│    └────┬────┘
│         │
│    Wait for CI
│         │
│    pass ▼ fail
│    ┌────┴────┐
│    │         │
│    │    Read logs, diagnose, fix, push
│    │    (max 3 consecutive failures)
│    │         │
│    └────┬────┘
│         │
│    --once? ──yes──► Exit
│         │
│        no
│         ▼
└── Loop back to check comments
```

## Steps

### Step 0: Track Progress

Before starting, create a task for each step below using TaskCreate. Chain sequential steps with addBlockedBy. As you work, update each task's status to `in_progress` when starting it and `completed` when done.

### 1. Find the PR

```bash
gh pr view --json number,title,headRefName,url --jq '{number, title, headRefName, url}'
```

If no PR exists for the current branch, tell the user and exit.

### 2. Check for review comments (FIRST)

Address review comments BEFORE waiting for CI. Comments are actionable immediately — don't waste time watching CI while there are fixable issues.

Fetch unresolved review threads via GraphQL (REST does not expose thread resolution state):

```bash
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      pullRequest(number: NUMBER) {
        reviewThreads(first: 100) {
          nodes {
            id
            path
            line
            isResolved
            isOutdated
            comments(first: 10) {
              nodes {
                body
                author { login }
              }
            }
          }
        }
      }
    }
  }
'
```

Replace `OWNER`, `REPO`, and `NUMBER` with actual values from step 1. Use inline string substitution — do NOT use `-f`/`-F` variable parameters.

Filter for threads where `isResolved == false` and `isOutdated == false`.

**If there are unresolved threads:** triage and address them (step 3), then push. Continue to step 4 (CI).

**If no unresolved threads:** proceed directly to step 4 (CI).

### 3. Triage and address review comments

Classify each comment into one of three categories:

**Fix now** = the code is broken or wrong:
- Security vulnerabilities
- Logic errors / bugs
- Missing error handling that causes crashes
- Incorrect behavior vs documented intent

**Out of scope (YAGNI)** = the code works but could do more:
- "Add support for X" when X isn't used yet
- "Handle edge case Y" when Y doesn't exist in production
- Consistency improvements for features not yet built

**Won't fix** = not actionable:
- False positives from automated reviewers
- Style preferences that don't improve correctness

**Key question**: Is the reviewer pointing out something *broken*, or suggesting something *additional*? Only fix what's broken.

#### When to ask the user

**Always ask** when:
- A reviewer's comment is ambiguous (could be a bug or enhancement)
- Multiple valid approaches exist to fix an issue
- The fix would require significant architectural changes
- You're unsure if something is truly out of scope

#### Responding to comments

**Fix bugs in code we wrote.** If a reviewer points out broken behavior in code this PR introduces, fix it now.

**Don't add features that don't exist yet.** If a reviewer suggests "you should also handle X" but X isn't a current requirement, that's YAGNI. Respond with: "X isn't implemented/used yet. Will add when we build that feature."

**Never defer bugs to "future PR"** — that's avoiding work. But deferring unrequested features is correct.

When replying to threads:
- If fixed: briefly explain the fix
- If out of scope: explain what would need to exist first
- If won't fix: provide technical reasoning

After addressing comments:
1. Commit and push changes
2. Reply to each thread explaining the resolution
3. Resolve addressed threads via `gh api graphql` mutation

### 4. Wait for CI

**Normal mode:** Run this and let it block — it costs zero tokens while waiting:

```bash
gh pr checks --watch --fail-fast 2>&1
```

**`--once` mode** (when `$ARGUMENTS` contains `--once`): Take a non-blocking snapshot instead:

```bash
gh pr checks --json name,state,bucket,link 2>&1
```

Parse the JSON output and inspect each check's `bucket` field:
- All checks have `bucket == "pass"` → proceed to step 6
- Any check has `bucket == "fail"` → handle as CI failure (step 5)
- Some checks have `bucket == "pending"` but none failed → proceed to step 6 (do not treat pending as failure)

Then proceed through steps 5-6 once and exit without looping.

### 5. Handle CI failure

**After CI completes (both modes)**, cross-check with `gh run list` to catch failures masked by check-name deduplication:

```bash
gh run list --branch <branch> --limit 20 --json name,status,conclusion,databaseId
```

If any run has `conclusion == "failure"`, treat it as a CI failure even if `gh pr checks` showed green. `gh pr checks` deduplicates by check name and can show a passing run from an earlier commit while hiding a failing run from the current one.

**Normal mode — If CI passes (exit 0) and no failed runs in cross-check:** proceed to step 6.

**Normal mode — If CI fails (exit non-zero) or cross-check finds failures:**

1. Get the failed check names from the output (or from the `gh run list` cross-check)
2. Fetch the logs for each failed run:
   ```bash
   gh run view <run-id> --log-failed 2>&1 | tail -200
   ```
3. Diagnose the root cause from the logs
4. Fix the issue — edit files, run tests locally to verify
5. Commit and push:
   ```bash
   git add -A && git commit -m "fix: address CI failure - <brief description>"
   git push origin HEAD
   ```
6. Go back to step 2 (check comments again, then CI)

**Max 3 consecutive CI fix attempts.** If CI still fails after 3 pushes, report the situation to the user and stop. The counter resets whenever CI passes.

### 6. Report

Print a summary:
- PR URL
- CI status (green)
- Review status
- What was fixed (if anything)

If in `--once` mode, exit here. Otherwise, loop back to step 2 to keep watching.

### Final Check

Run TaskList. If any task is not `completed`, go back and finish it now.

<!-- evolved: 2026-03-31 — Add gh run list cross-check after gh pr checks to catch failures masked by check-name deduplication -->
