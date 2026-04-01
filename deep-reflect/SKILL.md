---
name: deep-reflect
description: "Deep audit of Claude session history. Analyzes JSONL logs for mistakes, failed patterns, token waste, and missed opportunities. Writes findings to memory."
argument-hint: "[7d] [--project my-project]"
user-invocable: true
context: fork
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Skill
---

# /deep-reflect — Deep Session Audit

Analyzes Claude conversation history (JSONL files) to identify mistakes, failed communication patterns, token waste, recurring bugs, and missed opportunities. Writes actionable findings to persistent memory.

## Arguments

- `/deep-reflect` — default: last 7 days, scoped by context (see below)
- `/deep-reflect 3d` — last 3 days
- `/deep-reflect 14d` — last 14 days
- `/deep-reflect --project <name>` — filter to project directory name (substring match on path)
- `/deep-reflect --all` — all projects

Parse `$ARGUMENTS` for time window and project filter.

### Scope detection

Determine which sessions to include:

1. If `--all` or `--project` is specified, use that filter
2. If the current working directory is a **shepherd/orchestrator** session (e.g. `~/.config/<project-name>`, or CLAUDE.md says "shepherd"/"orchestrator"), default to `--all` — the shepherd oversees all repos
3. Otherwise, find the Claude project directory for the current working directory by matching `~/.claude/projects/` entries against `$PWD`. Use that exact project directory prefix (not substring grep) to filter sessions. Include worktree subdirectories that share the same repo root.

## Instructions

### Step 0: Track Progress

Before starting, create a task for each phase below using TaskCreate. Chain sequential phases with addBlockedBy. As you work, update each task's status to `in_progress` when starting it and `completed` when done.

### Phase 1: Extract session digests

1. Find all JSONL session files matching the time window:
   ```bash
   find ~/.claude/projects -name "*.jsonl" -mtime -<DAYS> ! -path "*/subagents/*" ! -name "history.jsonl"
   ```
   Apply project filter: for `--all`, skip filtering. For `--project`, use `grep -i <project>`. For auto-detected scope, match the exact project directory prefix from the path.

2. Run the extraction script on all matching files:
   ```bash
   SCRIPT_DIR="$(find ~/.claude/skills/deep-reflect -name extract_session_digest.py)"
   mkdir -p /tmp/deep-reflect-digests
   rm -f /tmp/deep-reflect-digests/all.txt
   find ~/.claude/projects -name "*.jsonl" -mtime -<DAYS> ! -path "*/subagents/*" ! -name "history.jsonl" | <filter_command> | while read f; do
     python3 "$SCRIPT_DIR" "$f" >> /tmp/deep-reflect-digests/all.txt
   done
   ```

3. Generate aggregate stats:
   ```bash
   python3 -c "
   import re
   with open('/tmp/deep-reflect-digests/all.txt') as f:
       text = f.read()
   sessions = text.count('# Session:')
   corrections = len(re.findall(r'\[CORRECTION\]', text))
   frustrations = len(re.findall(r'\[FRUSTRATION\]', text))
   print(f'Sessions: {sessions}')
   print(f'Corrections: {corrections}')
   print(f'Frustrations: {frustrations}')
   "
   ```

### Phase 2: Analyze digests

Read the combined digest file. This is the core analysis step — do NOT delegate this to a subagent. Use your full reasoning to identify patterns across sessions.

Look for these categories:

1. **Recurring bugs** — Same issue appearing in 3+ sessions
2. **Wasted work** — Features built then discarded, wrong technology choices
3. **Communication failures** — User had to re-explain, Claude misunderstood intent
4. **Token waste** — Redundant reads, verbose responses, unnecessary agent spawns
5. **Missing skills** — Workflows that were done manually but should be a skill (repeated multi-step patterns, user said "turn this into a skill", or ad-hoc workflows that took >3 steps and will recur)
6. **Skill friction** — Skills that were invoked but had corrections, wasted steps, or required course corrections (track which skill and what went wrong)
7. **Skill/agent architecture mismatches** — Skills running inline that should fork (context bloat), or forked skills that needed conversation context (went off-topic). Refer to `~/.claude/ARCHITECTURE.md` for the decision checklist.
8. **Forgotten instructions** — Things in CLAUDE.md or memory that were violated
9. **What worked well** — Patterns to reinforce (important: don't only capture failures)

Also get the git log for the same period:
```bash
git log --since="<DAYS> days ago" --oneline --all
```

### Phase 3: Write findings

1. **Write the full report** to `~/.claude/projects/<current-project>/memory/deep_reflect_<DATE>.md` with type `project`.

   Structure:
   - Top-level numbers (sessions, corrections rate, frustration rate)
   - Numbered findings with: what happened, root cause, lesson
   - What worked well
   - Recommendations (immediate + longer-term)

2. **Create individual feedback memories** for the top 3-5 most impactful findings. Each should have:
   - The rule
   - **Why:** (what went wrong)
   - **How to apply:** (when this guidance kicks in)

3. **Update MEMORY.md** with links to all new files.

4. **Present highlights** to the user — don't just say "I wrote it to memory." Walk through the top findings with specific examples.

### Phase 3.5: Skill Evolution

After writing findings but before cleanup, process skill-related discoveries:

1. **Create missing skills** — For each "missing skill" finding from Phase 2, invoke `/create-skill` with the workflow description. Only create skills for patterns that appeared in 2+ sessions or that the user explicitly asked for.

2. **Evolve used skills** — For each "skill friction" finding from Phase 2, invoke `/evolve-skill <skill-name>` with the specific friction evidence (corrections, wasted steps, token waste). Pass the evidence as context so evolve-skill doesn't need to re-scan sessions.

3. **Report** — Include a "Skill Evolution" section in the highlights: which skills were created, which were evolved, and what changed.

### Phase 3.55: Tool Ecosystem Scan

For each "missing skill" or "process gap" finding, before building from scratch, search for existing open-source tools that already solve the problem:

1. **Search** — Use `/deep-research` (or web search if deep-research is unavailable) for each gap: "open source tool for [gap description] MCP Claude"
2. **Evaluate** — Does an existing tool solve ≥80% of the need? Is it MIT/Apache licensed? Is it maintained?
3. **Recommend** — For each gap, recommend: adopt existing tool, adapt it, or build from scratch
4. **Create spike issues** — If a promising tool is found, create a spike issue to evaluate it rather than building immediately

This prevents reinventing wheels. The best skill is one you don't have to write.

### Phase 3.6: Action Items

Always end the reflect with concrete action items. Don't ask the user if they want them — just present them and start executing.

For each finding, determine if there's a fixable action:

| Finding Type | Action |
|-------------|--------|
| Skill friction | Evolve the skill (Phase 3.5 already handles this) |
| Missing skill | Create it (Phase 3.5 already handles this) |
| Recurring bug | Create an issue or investigate root cause |
| Process gap | Update the relevant skill, agent, or CLAUDE.md |
| Behavioral pattern | Write a feedback memory (Phase 3 already handles this) |

Present the action items as a numbered list with status:
- Items already handled by Phase 3/3.5 → mark as **Done**
- Items that need further work → execute them now

Do not wait for user approval on action items. The whole point of reflect is to act on what was found.

### Phase 3.7: Update Rolling Log

Append one line to `~/.claude/skills/deep-reflect/reflect.log`:

```
YYYY-MM-DD | <project> | <sessions> sessions | <correction_rate>% corrections | <frustration_rate>% frustrations | <top finding summary>
```

This file is the trend history. Scan it at the start of Phase 2 to compare against previous runs — are correction rates improving or getting worse?

### Phase 4: Cleanup

```bash
rm -rf /tmp/deep-reflect-digests
```

### Final Check

Run TaskList. If any task is not `completed`, go back and finish it now.

## Important Notes

- The extraction script filters out task-notifications and `<local-command-stdout>` blocks from correction/frustration detection to reduce false positives
- Subagent JSONL files are excluded — they're noisy and the orchestrator session captures the important signals
- The analysis step requires judgment — write findings and memories directly, then present highlights
- Check for existing `deep_reflect_*.md` files to avoid duplicating previous findings
- If previous findings exist, focus on what's NEW or what's gotten WORSE since then

