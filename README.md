# claude-skills

Skills and plugins for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Install

**As a plugin** (recommended — gets you the multi-agent skills like `/review` and `/quorum`):

```bash
claude plugin add drewdrewthis/claude-skills
```

**Individual skills** (copy a single skill into your global skills directory):

```bash
cp -r <skill-name> ~/.claude/skills/
```

## Skills

### Standalone

| Skill | Description |
|-------|-------------|
| `/create-skill` | Turn a workflow into a well-structured Claude Code skill |
| `/evolve-skill` | Improve a skill based on how it just performed — patches friction, corrections, and missed steps |
| `/deep-reflect` | Audit Claude session history (JSONL logs) for mistakes, failed patterns, and token waste |
| `/retro` | Weekly engineering retrospective with commit analysis, quality metrics, and trend tracking |
| `/implement` | Start implementation of a GitHub issue (`/implement #123`) |
| `/drive-pr` | Drive a PR to mergeable state — fix CI failures, address review comments, loop until green |
| `/write-pr` | Create a PR with a filled-in template |

### Plugins

Plugins bundle skills with dedicated agents and reference docs. Install them via `claude plugin add`.

#### review (v2.0)

Parallel code review with 4 specialized agents running concurrently, followed by persona-driven perspectives.

**Agents:**
- **principles-reviewer** — SRP, design, readability, simplicity, extensibility
- **hygiene-reviewer** — reuse, patterns, idioms, dead code, bloat
- **test-reviewer** — test pyramid placement, coverage, naming
- **security-reviewer** — PII, secrets, data exposure

**Bundled docs:** `CODING_STANDARDS.md`, `TESTING_PHILOSOPHY.md`

```
/review              # review current diff
/review src/auth/    # focus on specific files
```

#### quorum (v1.0)

Debate a design question with N agents arguing different positions, then synthesize a recommendation. Includes a devil's advocate agent.

```
/quorum "Should we use Redis or Postgres for our job queue?"
/quorum "Monorepo vs polyrepo for our microservices"
```

## Structure

```
claude-skills/
├── .claude-plugin/
│   └── marketplace.json       # plugin registry
├── create-skill/SKILL.md
├── deep-reflect/
│   ├── SKILL.md
│   └── scripts/               # session analysis helpers
├── drive-pr/SKILL.md
├── evolve-skill/SKILL.md
├── implement/SKILL.md
├── retro/SKILL.md
├── write-pr/
│   ├── SKILL.md
│   └── docs/PR_TEMPLATE.md
└── plugins/
    ├── review/
    │   ├── .claude-plugin/plugin.json
    │   ├── agents/            # 4 reviewer agents
    │   ├── docs/              # coding standards, testing philosophy
    │   └── skills/review/SKILL.md
    └── quorum/
        ├── .claude-plugin/plugin.json
        ├── agents/            # devil's advocate
        └── skills/quorum/SKILL.md
```

## Writing your own skills

Use `/create-skill` to scaffold a new skill, or see any `SKILL.md` in this repo for the format. After using a skill, run `/evolve-skill <name>` to tighten it based on what actually happened.

## License

MIT
