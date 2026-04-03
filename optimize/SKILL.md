---
name: optimize
description: "Audit agent config and conversation for token waste: duplication, bloat, unnecessary context loading. Produces actionable fixes."
user-invocable: true
argument-hint: "[scope: 'config' | 'session' | 'all']"
---

# Token Optimization Audit

Audit for token waste and produce actionable fixes. Scope: $ARGUMENTS (default: all).

### Step 0: Track Progress

Before starting, create a task for each phase/step below using TaskCreate. Chain sequential phases with addBlockedBy. As you work, update each task's status to `in_progress` when starting it and `completed` when done.

## 1. Config Layer Audit (scope: config | all)

Check for duplication and bloat across the agent configuration files.

### Understand the two scopes:
- **Global** (`~/.claude/`): Personal config on this machine only. Not shared. Can be freely modified.
- **Project** (`.claude/` in repo): Checked into git, shared with the whole team. Changes here affect everyone.

When the same skill/agent exists in both scopes, the project version is the **canonical shared** version. The global version is a **personal fallback** for repos that don't define their own. Never recommend deleting project versions in favor of global — project is the source of truth for the team.

### Scan these locations:
- `~/.claude/CLAUDE.md` (global instructions — personal)
- Project `CLAUDE.md` and `AGENTS.md` (shared with team)
- `~/.claude/agents/*.md` (global agent definitions — personal)
- `.claude/agents/*.md` (project agent definitions — shared)
- `~/.claude/skills/*/SKILL.md` (global skills — personal)
- `.claude/skills/*/SKILL.md` (project skills — shared)

### Look for:
- **Inlined instructions** that could be references to docs (e.g., coding standards repeated in agent prompts instead of "Read `docs/CODING_STANDARDS.md`")
- **Bloated agent prompts** — instructions over ~50 lines that could be split into "always loaded" essentials vs "read on demand" references
- **Overlapping skills within the same scope** — two skills that do nearly the same thing (one should be deleted or merged)
- **Dead config** — agents/skills referenced nowhere within their scope, empty directories that shadow other scopes
- **Cross-scope duplication** — global config that restates what project config already provides (global can defer to project, not the other way around)
- **Stale global overrides** — global versions identical to project versions (the global copy is redundant since the project version will be used)

### Output format:
```
## Config Issues

### Bloat (inline → reference)
- **[file] (scope)**: lines N-M could reference `path/to/doc` instead

### Dead Config
- **[file] (scope)**: why it's dead (no invocation path, empty directory, etc.)

### Cross-Scope Waste
- **global [file]**: identical to project version, global copy is redundant
- **global [file]**: restates what project AGENTS.md already covers

### Recommendations
1. Specific action to take (specify which scope to modify)
2. Specific action to take
```

## 2. Session Audit (scope: session | all)

Review the current conversation for token inefficiency patterns.

### Look for:
- **Large tool results that could have been filtered** — e.g., reading an entire file when only a few lines were needed, API responses ingested wholesale instead of written to temp file and grepped
- **Repeated searches** — same or overlapping Grep/Glob calls that could have been one query
- **Agent sprawl** — agents spawned for tasks that could have been a direct tool call, or multiple agents doing overlapping work
- **Unnecessary context loading** — files read that were never used in the response
- **Verbose output** — responses that could be shorter without losing information

### Output format:
```
## Session Issues

### Wasteful Patterns
- **[pattern]**: what happened, what would be more efficient

### Estimated Token Savings
- Pattern 1: ~Xk tokens saved per occurrence
- Pattern 2: ~Xk tokens saved per occurrence

### Recommendations
1. Specific strategy for future sessions
```

## 3. Summary

End with a prioritized action list:
```
## Action Items (by token savings, highest first)
1. [action] — est. savings: Xk tokens/session
2. [action] — est. savings: Xk tokens/session
```

### Final Check

Run TaskList. If any task is not `completed`, go back and finish it now.

## Rules

- Be concrete. "Reduce bloat" is not actionable. "Delete lines 45-80 of coder.md, replace with `Read docs/CODING_STANDARDS.md`" is.
- Don't propose changes that sacrifice agent quality for token savings. The goal is eliminating waste, not cutting corners.
- If session logs are available (`.jsonl` files), scan them for patterns. Use targeted Grep, don't read entire logs.
- Write findings to a temp file if the audit itself would produce too much output.
