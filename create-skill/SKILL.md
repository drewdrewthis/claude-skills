---
name: create-skill
description: "Create a new Claude Code skill with correct structure, progressive disclosure, and token-efficient design. Use when the user wants to turn a workflow into a skill, says 'make this a skill', or asks to create/write a skill. Also triggered by /deep-reflect when it identifies a missing skill."
user-invocable: true
argument-hint: "[skill name or description of what the skill should do]"
---

# Create Skill

Turn a workflow, pattern, or capability into a well-structured skill.

Context from conversation or arguments: $ARGUMENTS

## Step 0: Track Progress

Before starting, create a task for each phase below using TaskCreate. Chain sequential phases with addBlockedBy. As you work, update each task's status to `in_progress` when starting it and `completed` when done.

## Phase 1: Capture Intent

Before writing anything, answer these questions. Extract answers from conversation history first — don't re-ask what's already been demonstrated.

1. **What does this skill do?** One sentence. If you can't say it in one sentence, the skill is too broad — split it.
2. **When should it trigger?** The specific user phrases, contexts, or situations.
3. **What's the output?** Files, messages, state changes, delegated work.
4. **Does it need tools/agents?** Which tools, which agent types, any MCP servers.
5. **Fork or inline?** Does it need isolation (`context: fork`) or run in conversation? Read `~/.claude/ARCHITECTURE.md` for the decision checklist on when to use skills vs agents and inline vs fork.

## Phase 1.5: Landscape Check

Before writing from scratch, check if this already exists:

1. **Local skills** — scan `~/.claude/skills/` and `.claude/skills/` for overlapping functionality. Could an existing skill be extended instead?
2. **Official library** — check [anthropics/skills](https://github.com/anthropics/skills) for Anthropic's maintained skills, templates, and the `/skill-creator` reference implementation.
3. **Community registry** — search [skills.sh](https://skills.sh) (Vercel's open registry, 100+ skills across 40+ agents). Run `npx skills find <keyword>` or search the web. Uses the same SKILL.md format.
4. **Prior art** — quick web search for `"claude code skill" <topic>` or `"AGENTS.md" <topic>`. Check the [agentskills.io](https://agentskills.io/) spec for format conventions.

**If a match exists:**
- Evaluate fit. If it's close enough, install/adapt it instead of writing from scratch. Tell the user what you found.
- If it's partial, use it as a starting point — cite the source in an `<!-- adapted from: ... -->` comment.

**If no match:** Proceed to Phase 2.

## Phase 2: Write the Skill

### Directory Structure

```
~/.claude/skills/<skill-name>/
├── SKILL.md              # Required — the skill itself
├── references/           # Optional — docs loaded on demand
│   └── detailed-guide.md
└── scripts/              # Optional — deterministic/repetitive tasks
    └── helper.py
```

### SKILL.md Anatomy

```yaml
---
name: <slug>                    # kebab-case identifier
description: "<what + when>"    # This is the PRIMARY trigger — be specific and slightly pushy
user-invocable: true            # false only for skills invoked exclusively by other skills
argument-hint: "[args]"         # Optional — show expected arguments
# Optional fields:
context: fork                   # Only if skill needs isolation (reviews, parallel work)
agent: <agent-type>             # Only if delegating to a specific agent
allowed-tools: [Tool1, Tool2]  # Only if restricting tool access
---
```

### Body Guidelines

| Principle | Rule |
|-----------|------|
| **Length** | Under 100 lines for simple skills, under 300 for complex. If approaching 500, split into SKILL.md + references/ |
| **Style** | Imperative voice. Explain *why*, not just *what*. No heavy-handed MUSTs — explain reasoning instead |
| **Structure** | Phases or numbered steps. Each phase has a clear purpose. Skills with 4+ phases must include Step 0 (create tasks) and a Final Check — see `~/.claude/ARCHITECTURE.md` "Task Tracking Pattern" |
| **Arguments** | Use `$ARGUMENTS` placeholder for pass-through |
| **Token budget** | Every line should earn its place. Cut instructions the model would follow anyway. Don't repeat what's in CLAUDE.md |
| **Examples** | Include 1-2 examples for non-obvious output formats. Skip for obvious ones |
| **References** | Large docs (>50 lines) go in `references/` with a pointer from SKILL.md |

### Description Field — Critical

The description is the primary trigger mechanism. It must include:
- **What** the skill does (the capability)
- **When** to use it (specific trigger phrases and contexts)
- Keep it under ~50 words but be specific enough to trigger reliably

Err on the side of "pushy" — Claude undertriggers skills. Better to trigger and not be needed than to miss a relevant invocation.

### Progressive Disclosure

Three levels, loaded incrementally:
1. **Metadata** (name + description) — always in context (~50 words)
2. **SKILL.md body** — loaded when skill triggers (target <200 lines)
3. **Bundled resources** — loaded on demand (unlimited size)

Keep the body lean. Move reference material to `references/`. Move deterministic logic to `scripts/`.

## Phase 3: Validate

Before presenting to the user:

1. **Read it fresh** — does it make sense without conversation context?
2. **Check for bloat** — delete any line the model would follow without being told
3. **Check for gaps** — would a fresh Claude session know what to do with this?
4. **Description test** — given 3 realistic user prompts, would this description trigger?
5. **Token check** — is the SKILL.md under 200 lines? If not, what can move to references?

Present the skill to the user. Walk through the key design decisions.

## Phase 4: Placement

Skills go in `~/.claude/skills/<name>/SKILL.md` for global skills, or `.claude/skills/<name>/SKILL.md` for project-specific skills. Ask the user which scope if unclear.

## Final Check

Run TaskList. If any task is not `completed`, go back and finish it now.

## Anti-patterns

- **Kitchen-sink skills** — doing 5 things instead of 1. Split them.
- **Verbose instructions** — telling the model things it already knows. Trust its intelligence.
- **Missing trigger context** — a description that says "do X" but not "when to do X."
- **Hardcoded paths** — use relative paths or `$ARGUMENTS`, not absolute paths.
- **Duplicating CLAUDE.md** — if it's already in global instructions, don't repeat it.
