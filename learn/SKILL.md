---
name: learn
description: "Learn from mistakes by updating project guidelines. Use when a mistake was made that should be prevented in future sessions."
user-invocable: true
argument-hint: "[description of the mistake and correct behavior]"
---

# Learn from Mistakes

You made a mistake. Good - this is an opportunity to prevent it from happening again.

## Process

### Step 0: Track Progress

Before starting, create a task for each step below using TaskCreate. Chain sequential steps with addBlockedBy. As you work, update each task's status to `in_progress` when starting it and `completed` when done.

### 1. Analyze the Mistake

Identify:
- **What went wrong**: The specific action or omission
- **Why it happened**: The reasoning or assumption that led to the mistake
- **Correct behavior**: What should have been done instead

### 2. Formulate the Lesson

Create a concise entry:
- **Common Mistake**: Brief description of the anti-pattern (what NOT to do)
- **Correct Behavior**: Clear instruction of what TO do instead

The lesson should be:
- Actionable (tells you exactly what to do)
- Specific (not vague platitudes)
- Generalizable (applies beyond this one instance)

### 3. Find the Right Location

Check for project guidelines files (`AGENTS.md`, `CLAUDE.md`, or similar) and identify which section the lesson belongs in. If no suitable file exists, update auto memory instead.

### 4. Update Guidelines

Add a new row to the appropriate table:

```markdown
| <Common Mistake> | <Correct Behavior> |
```

### 5. Log the Mistake

Invoke `/log-mistake` with the mistake details from Step 1. This records the originating mistake in the structured log (`~/.claude/mistakes.jsonl`) so `/deep-reflect` and `/evolve-skill` can consume it.

### 6. Confirm the Update

Read back the updated section to verify the entry is clear and correctly formatted.

### Final Check

Run TaskList. If any task is not `completed`, go back and finish it now.

## Arguments

$ARGUMENTS
