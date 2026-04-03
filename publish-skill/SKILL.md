---
name: publish-skill
description: "PII-scrub and publish a skill from ~/.claude/skills/ to the public <your-org>/claude-skills repo. Use when a skill is ready to share publicly."
user-invocable: true
argument-hint: "<skill-name> [--dry-run]"
---

# Publish Skill

Scrub and publish a local skill to the public skills repo.

Target repo: `<your-org>/claude-skills`
Skill name: $ARGUMENTS

## Phase 1: Resolve Target

1. Parse skill name from arguments. If `--dry-run` is present, report what would happen but don't push.
2. Read the skill from `~/.claude/skills/<name>/SKILL.md`
3. If the skill has an `agent:` field in frontmatter, note it — the agent definition will also need publishing.
4. Check if `~/claude-skills/` exists (local clone). If not, clone `<your-org>/claude-skills` there.

## Phase 2: PII Scrub

Scan the SKILL.md content for PII and project-specific references. **Flag and fix** any of:

- Personal home directory paths (e.g., `/Users/<name>/`, `/home/<name>/`, `~/.config/<project>/`)
- GitHub usernames in non-generic context (references to specific org repos that aren't the skills repo itself)
- Internal hostnames, IP addresses, or API endpoints
- Slack channel names or webhook URLs
- References to specific people by name
- Org-specific repo names (e.g. `acme/my-app`) — replace with generic placeholders
- Bot tokens or channel IDs
- Any absolute paths that leak machine-specific info

**Replacements:**
- `/Users/<name>/` → `~/` or `/home/user/`
- Specific org/repo refs → `acme/my-project` or similar generic
- Internal URLs → `https://example.com`

Show the user a diff of all changes before proceeding.

## Phase 3: Publish Agent (if coupled)

If the skill references an `agent:` definition:

1. Read the agent from `~/.claude/agents/<agent-name>.md`
2. Apply the same PII scrub
3. Note: this skill + agent pair should be published as a **plugin**, not a standalone skill
4. Create the plugin structure:
   ```
   ~/claude-skills/plugins/<skill-name>/
   ├── skills/<skill-name>/SKILL.md
   └── agents/<agent-name>.md
   ```
5. Update `~/claude-skills/.claude-plugin/marketplace.json` to include the new plugin

## Phase 4: Publish Standalone Skill

If the skill has no agent dependency:

1. Copy the scrubbed SKILL.md to `~/claude-skills/<skill-name>/SKILL.md`
2. If the skill directory contains other files (templates, scripts), copy those too after scrubbing

## Phase 5: Commit and Push

1. `cd ~/claude-skills`
2. `git add <skill-name>/` (or `plugins/<skill-name>/` for coupled skills)
3. Commit with message: `publish: <skill-name>`
4. If `--dry-run`, show what would be committed and stop
5. Push to origin

## Phase 6: Report

- Confirm what was published
- Show the install command: `npx skills add <your-org>/claude-skills/<skill-name>`
- For plugins: show the marketplace install path
- Flag any PII that was scrubbed so the user can verify the replacements
