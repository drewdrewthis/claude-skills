---
name: log-mistake
description: "Log a mistake to the structured mistake log. Use when the user corrects you, when you catch your own mistake, or when /learn codifies a new rule."
user-invocable: true
argument-hint: "[description of what went wrong]"
---

# Log Mistake

Append a structured entry to `~/.claude/mistakes.jsonl`. This is the single source of truth for corrections — consumed by `/deep-reflect`, `/evolve-skill`, `/learn`, and `/retro`.

## When This Runs

- **User correction** — the user says "no", "wrong", "not that", "stop", corrects your approach, or redirects you
- **Self-catch** — you realize you made a mistake before the user points it out
- **From /learn** — after codifying a rule, `/learn` invokes this to record the originating mistake
- **Manually** — user invokes `/log-mistake <description>`

## Process

### 1. Classify the Mistake

From the conversation context and `$ARGUMENTS`, determine:

| Field | How to determine |
|-------|-----------------|
| **category** | One of: `wrong-action`, `wrong-assumption`, `forgot-instruction`, `wasted-work`, `wrong-tool`, `wrong-model`, `style-violation`, `other` |
| **description** | What went wrong — one sentence, specific |
| **correction** | What should have happened — one sentence |
| **skill** | Which skill was active, if any (e.g., `manage-sessions`, `drive-pr`). Empty string if none. |
| **severity** | `low` (style/minor), `medium` (wasted work, wrong approach), `high` (destructive action, violated explicit instruction) |
| **trigger** | `human` (user corrected) or `self` (caught own mistake) |

### 2. Append to Log

```bash
echo '{"ts":"<ISO-8601-UTC>","project":"<project-name>","session":"<session-id-if-available>","category":"<category>","trigger":"<trigger>","description":"<description>","correction":"<correction>","skill":"<skill>","severity":"<severity>"}' >> ~/.claude/mistakes.jsonl
```

Use `date -u +%Y-%m-%dT%H:%M:%SZ` for the timestamp. For project, use the repo/project name from the current working directory. For session, use `$CLAUDE_SESSION_ID` if available, otherwise omit.

### 3. Check for Pattern

After logging, quickly scan the last 20 entries in `~/.claude/mistakes.jsonl` for the same `category` + similar `description`. If 3+ entries share the same pattern:

- Note: "This is a recurring pattern — consider running `/learn` to codify a rule if one doesn't already exist."
- Do NOT auto-invoke `/learn` — it requires judgment about where to put the rule.

### 4. Resume

Continue with whatever you were doing before the correction. This skill should take <10 seconds and not derail the conversation.

## Anti-patterns

- **Over-logging** — don't log clarifications ("what did you mean?") as mistakes. A correction changes direction; a clarification adds detail.
- **Vague entries** — "made a mistake" is useless. Be specific: "sent /drive-pr to session that was still in planning phase."
- **Blocking the conversation** — log and move on. Don't turn a quick correction into a retrospective.
