---
name: tmux-window-fork
description: "Spawn a sister Claude session in a new tmux window of the current tmux session, briefed with a delegated sub-thread. Use when the user says 'fork yourself into a tmux window', 'fork off to a window', 'spawn a sister', 'hand this off to a sister', '/tmux-window-fork', or when a side-investigation has grown large enough that staying on it blocks the caller's core duties. Distinct from the native /fork (conversation branch) — this creates a real long-lived tmux-hosted Claude process. The sister owns the forked thread; the caller returns to its normal workload."
user-invocable: true
argument-hint: "<name> [briefing...]"
allowed-tools:
  - Bash
  - Read
  - Write
  - TaskCreate
  - TaskUpdate
---

# Tmux-Window Fork

Hand off a sub-thread by spawning a sister Claude session in a new window of the current tmux session, so this session can return to its primary duty.

The defining constraint: **the sister is a real long-lived Claude process in a real tmux window**, not an Agent tool call and not a conversation branch. It survives this session exiting, can be switched to with `tmux select-window`, and can be messaged via `/delegate`. Agents are for delegated *research* that returns to this context. The native `/fork` is for branching *this* conversation. This skill is for delegated *workstreams* that should run in parallel on the same machine as independent Claude processes.

## When to reach for this

- A side investigation in this conversation has grown ≥3-4 turns of tool calls and is likely to keep going.
- Core-duty work (triage, replies to the user, PR driving) is being blocked while you chase the side thread.
- The user says any of: "fork yourself into a window", "fork off to a tmux window", "spawn a sister", "hand this off", "free yourself up".
- You catch yourself thinking "this doesn't belong in this session's main context" — fork first, apologize later.

If the task is truly tiny (one grep + one edit), don't fork — just do it. If it's truly large (weeks of implementation), it wants a worktree and `/launch`, not a tmux fork. Tmux fork is for the middle: a meaty thread that's not implementation work.

**Disambiguate from native `/fork`.** If the user says bare "fork", check context: branching this conversation (native `/fork`) or spawning a parallel Claude process (this skill)? If unclear, ask one short question.

## Step 0: Track progress

Create tasks for the phases below with TaskCreate. Mark each in_progress when starting and completed when done.

## Phase 1: Resolve the name

`$ARGUMENTS` is `<name> [briefing...]`. The first whitespace-delimited token is the tmux window name; everything after is the briefing text (optional — see Phase 2).

Rules:
- Slug the name: lowercase, alphanumeric + hyphens only, ≤30 chars. Reject empty.
- Prefix with `fork-` so it's clear in `tmux list-windows` this is a sister thread (not a worker, not the parent session itself). Example: `fork-api-investigation`.
- If a window with this name already exists in the current session → reject and suggest `/delegate` to the existing one instead.

If the user didn't supply a name, pick one from the briefing's topic and tell them what you chose.

## Phase 2: Compose the briefing

The briefing is the first message the sister reads on boot. Make it self-contained — the sister has none of this conversation's context.

Briefing must include:

1. **Identity** — "You are a sister Claude session forked from a parent session. Your parent handed you this thread because [one-sentence reason]."
2. **Goal** — what "done" looks like for this thread, in one or two sentences. Outcome, not steps.
3. **Context snapshot** — the minimum the sister needs to pick up: relevant issue numbers, PR numbers, file paths, findings already made. Pull from this conversation's scrollback — don't re-derive. Aim for a short bulleted list, not prose.
4. **Authority** — what the sister is allowed to do without asking. Sensible defaults: read-only + issue body edits + GitHub comments OK; no merges/closes/force-pushes/session kills without checking with the user.
5. **Report back** — where results go. Usually: "Post the final summary to this tmux window as a text message; don't message the user directly unless blocked."
6. **Exit condition** — when this sister is done, it should say so and stop. Don't leave it spinning.

Write the briefing to a file so the sister can re-read it:

```bash
BRIEF_DIR="$HOME/.cache/claude-forks"
mkdir -p "$BRIEF_DIR"
BRIEF_FILE="$BRIEF_DIR/<name>-$(date +%s).md"
# Write briefing content via the Write tool to $BRIEF_FILE
```

If the user passed the briefing inline via `$ARGUMENTS`, use that verbatim as Phase 2's body but still prepend the identity/authority/report-back scaffolding. If they didn't, **write the briefing yourself** from the conversation state and show it to them before spawning.

## Phase 3: Spawn the window

Get the current tmux session name:

```bash
CURRENT_SESSION=$(tmux display-message -p '#S')
```

If the command errors (not running inside tmux), stop and tell the user. Fork requires a tmux host.

Create a new window in that session, named with the slug. The window starts at `$HOME` by default — override with `-c <path>` if the sister needs a specific workspace:

```bash
tmux new-window -t "$CURRENT_SESSION" -n "<name>" -c "$HOME"
```

Launch Claude in the new window with the briefing piped via the initial prompt. The sister must run with `--dangerously-skip-permissions` (so it can operate autonomously) and `--rc` + `-n "<name>"` so it participates in Remote Control like any other session:

```bash
tmux send-keys -t "${CURRENT_SESSION}:<name>" \
  "claude --dangerously-skip-permissions --rc -n '<name>' \"\$(cat $BRIEF_FILE)\"" Enter
```

Both `--rc` and `-n` are undocumented in `claude --help` but valid — they enable Remote Control and set the display name. Do not drop them; the parent session (and `/delegate`) rely on both to message the sister later.

## Phase 4: Verify the sister booted

Sleep 3-5s, then capture the new window and confirm Claude is running (not stuck at the trust-folder prompt):

```bash
sleep 4
tmux capture-pane -t "${CURRENT_SESSION}:<name>" -p | tail -10
```

Expected signals: `⏵⏵ bypass permissions on`, the briefing rendering, a task list forming, `✻ Cerebrating…`. If you see `Yes, I trust this folder?` the sister didn't accept trust — send `1` + Enter. If you see a resume picker or shell prompt, something went wrong — abort and report.

## Phase 5: Report back to the caller

Tell the user, in one line:

> Forked to `<window-name>`. Briefing: `<brief-file>`. Switch with `tmux select-window -t ${CURRENT_SESSION}:<name>` or message it with `/delegate <window-name> <msg>`.

Then stop. **Do not narrate what the sister is doing** — it owns its own thread now. The whole point of forking is so this session can move on.

## Final Check

Run TaskList. If any task is not `completed`, finish it now. If the sister failed to boot, the fork task is NOT complete — leave it in_progress and tell the user.

## Anti-patterns

| Anti-pattern | Why wrong |
|--------------|-----------|
| Using the Agent tool instead of spawning a real session | Agents die when this conversation ends. Forks are long-lived sister processes. |
| Forking without a briefing, expecting the sister to "figure it out" | Sister has zero context. Briefing is non-negotiable. |
| Forking tiny tasks | A one-grep-one-edit task is faster inline. Fork overhead isn't free. |
| Starting the sister without `--rc` / `-n` | Breaks Remote Control and `/delegate`; sister becomes an island. |
| Polling the sister after forking | The point of forking is to be free. If you need to check in, use the monitor or let the sister ping you. |
| Forking issue implementation work | Use `/launch #N` — it gives a worktree, branch, and proper session name convention. Fork is for non-implementation threads. |
| Running the fork from inside a worker session | Forks belong to supervisor-class sessions. A worker forking itself creates hard-to-track sprawl. |
