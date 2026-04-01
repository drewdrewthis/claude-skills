---
name: quorum
description: "Debate a design question with N agents arguing different positions, then synthesize a recommendation. Use when there are multiple valid approaches, the user says 'debate this', 'quorum', or wants perspectives stress-tested before deciding."
user-invocable: true
argument-hint: "<question to debate>"
---

# Quorum

N agents argue different sides of a question. You synthesize the best answer.

## Input

`$ARGUMENTS` — the question or decision to debate. If it includes explicit options, use those. Otherwise, identify the viable approaches yourself.

## Step 0: Track Progress

Before starting, create a task for each step below using TaskCreate. Chain sequential steps with addBlockedBy. As you work, update each task's status to `in_progress` when starting it and `completed` when done.

## Step 1: Frame the debate

Analyze the question and identify **all viable positions** — not just two. Most questions have 2-4 strong positions. Don't force binary framing on a question that has three or more legitimate angles.

State each position clearly:
- **Position A**: [approach/argument]
- **Position B**: [approach/argument]
- **Position C**: [approach/argument] (if applicable)
- ...

## Step 2: Gather ecosystem context

Before launching agents, gather relevant context they'll need to argue well. Agents debating in a vacuum produce generic arguments. Give them:
- Existing skills, tools, or systems related to the question (list names and one-line descriptions)
- Current pain points or recent failures that motivated the question
- Constraints (team size, technical debt, adoption patterns)

Include this as a "Context" section at the top of each agent's prompt.

## Step 3: Launch agents in parallel

Launch **one Agent per position** in a **single message** so they all run concurrently. Each agent gets:

1. The ecosystem context from Step 2
2. The full question context
3. Their assigned position to argue FOR
4. A summary of ALL other positions they're arguing against
5. Instructions to make the strongest possible case, anticipate counterarguments, and identify risks of the other approaches

Use `subagent_type: devils-advocate` for all. Use `model: sonnet` unless the question requires deep architectural reasoning (then `opus`).

**Agent prompt template:**
```
You are arguing FOR Position [X]: [position].
The question is: [question].
The other positions are:
- Position [Y]: [summary]
- Position [Z]: [summary]
...

Ecosystem context:
[relevant skills, tools, systems, constraints, recent failures]

Make the strongest possible case for your position:
1. Why this approach is better than each alternative
2. Concrete benefits and examples
3. Risks/weaknesses of each opposing approach
4. How your position interacts with the existing ecosystem (does it complement, replace, or restructure what exists?)
5. Acknowledge your own weaknesses honestly
6. Under what conditions would you concede to another position?
```

## Step 4: Synthesize

After all agents return, write a synthesis:

```
## Quorum Result

**Question:** [the question]

**Positions debated:** [N positions]

**Recommendation:** [which approach wins and why]

**Key reasoning:**
- [2-3 bullet points on why this approach is better for this context]

**From the dissent:**
- [strongest points from losing positions worth noting or incorporating]

**Conditions where other approaches win:**
- [Position X wins if...]
- [Position Y wins if...]
```

The synthesis should be opinionated — pick a winner. "It depends" is not a recommendation. State the conditions under which you'd change your mind. If two positions are genuinely complementary (not competing), say so and recommend the combination.

## Step 5: Deliver

Present the synthesis inline.

### Final Check

Run TaskList. If any task is not `completed`, go back and finish it now.

<!-- evolved: 2026-03-30 — added ecosystem context step (agents argued in vacuum without knowing existing skills); expanded agent prompt to include ecosystem interaction; changed from hardcoded 2 agents to N agents -->

