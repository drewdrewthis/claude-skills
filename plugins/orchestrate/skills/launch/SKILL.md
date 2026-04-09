---
name: launch
description: "Create a worktree for a GitHub issue and launch a Claude session to implement it. One command: worktree + session."
argument-hint: "#3"
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
---

# Launch

Create a local worktree for a GitHub issue and launch an autonomous Claude session in it to implement the work.

## Arguments

`$ARGUMENTS` is one or more issue numbers (with or without `#`). Example: `/launch #3` or `/launch 3 5 7`

## Steps

### Step 0: Track Progress

Before starting, create a task for each issue being launched using TaskCreate. As you work, update each task's status to `in_progress` when starting it and `completed` when done.

### 1. Parse issue numbers

Extract all numeric issue IDs from `$ARGUMENTS`. Strip `#` prefixes.

### 2. For each issue

#### 2a. Fetch issue info

```bash
gh issue view <N> --json title,body,number
```

#### 2b. Derive branch and directory names

1. Generate slug: lowercase title, replace non-alphanumeric with hyphens, collapse consecutive hyphens, trim, max 40 chars at word boundary
2. Branch: `issue<N>/<slug>`
3. Directory: `.worktrees/issue<N>-<slug>`

#### 2c. Ensure `.worktrees/` is in `.gitignore`

Check and add if missing.

#### 2d. Create worktree

```bash
git fetch origin
```

Check if branch exists on remote:
```bash
git ls-remote --heads origin <BRANCH>
```

- **Exists**: `git worktree add "<DIR>" "<BRANCH>"`, then rebase onto origin/main:
  ```bash
  cd "<DIR>" && git rebase origin/main && cd -
  ```
- **New**: `git worktree add -b "<BRANCH>" "<DIR>" origin/main`

If the worktree directory already exists, rebase it onto origin/main and report it.

#### 2e. Copy .env files

If the main checkout has `.env` files, copy them to the worktree:
```bash
find . -maxdepth 2 -name ".env*" -not -path "./.worktrees/*" | while read f; do
  cp "$f" "<DIR>/$f" 2>/dev/null
done
```

#### 2f. Launch Claude session

Launch an interactive Claude session in the worktree's tmux session. To avoid shell quoting issues with `tmux send-keys`, use a two-step approach:

1. Write a launcher script. Use `claude --dangerously-skip-permissions` for unattended sessions. Send `/rename` as the initial prompt, then send `/orchestrate` as a separate message after Claude starts:
```bash
cat > /tmp/claude-launch-issue<N>.sh << 'LAUNCHER'
cd <WORKTREE_DIR>
claude --dangerously-skip-permissions "/rename #<N> <SLUG>"
LAUNCHER
chmod +x /tmp/claude-launch-issue<N>.sh
```

2. Find or create the tmux session and run the script:
```bash
REPO_NAME=$(basename -s .git "$(git remote get-url origin)")
TMUX_SESSION=$(tmux list-sessions -F '#{session_name}' | grep -i "${REPO_NAME}_issue<N>" | head -1)

if [ -z "$TMUX_SESSION" ]; then
  TMUX_SESSION="${REPO_NAME}_issue<N>"
  tmux new-session -d -s "$TMUX_SESSION" -c "<WORKTREE_DIR>"
fi

tmux send-keys -t "$TMUX_SESSION" "bash /tmp/claude-launch-issue<N>.sh" Enter
```

3. After Claude starts, send `/orchestrate` as a separate message:
```bash
sleep 10
tmux send-keys -t "$TMUX_SESSION" "/orchestrate #<N>" Enter
sleep 3
# Verify the message was received
tmux capture-pane -t "$TMUX_SESSION" -p | tail -5
```

**Important:**
- **No nested launches.** If the current tmux session name contains `_issue` (meaning you're inside a worktree session), do NOT launch. Tell the user to launch from the orchestrator or main session instead. Nested launches produce mangled session names.
- Do NOT use `-p` (print) mode — it exits after one turn and can't handle multi-step implementation
- Do NOT use `< file` redirect — stdin closes and Claude exits after one response
- Use a launcher script to avoid quote nesting issues with `tmux send-keys`
- `--dangerously-skip-permissions` allows the session to run without interactive approval prompts — use only for trusted, automated workflows
- The positional prompt argument (`claude --dangerously-skip-permissions "prompt"`) starts an interactive session with that as the first message
- When resuming a session (e.g. after exit/restart), use `claude --continue` instead of starting fresh
- Include `/rename #<N> <slug>` as the first instruction so sessions are identifiable in `tmux list-sessions` and conversation history

#### 2g. Report

Output for each issue:
- Issue number and title
- Branch name
- Worktree absolute path
- Confirmation that Claude session was launched

### 3. Summary

After all issues are processed, print a summary table:

```
| Issue | Branch | Worktree | Status |
|-------|--------|----------|--------|
| #3    | issue3/implement-integration-... | /abs/path/.worktrees/... | Claude session launched |
```

### Final Check

Run TaskList. If any task is not `completed`, go back and finish it now.

## Notes

- Each Claude session runs independently in its own worktree
- Sessions read their own CLAUDE.md and have full context
- Use `tmux list-sessions` or check worktree directories to monitor progress
- If a worktree already exists, just launch the Claude session in it
