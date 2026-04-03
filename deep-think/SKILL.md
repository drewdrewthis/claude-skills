---
name: deep-think
description: "Structured design exploration for open-ended technical questions. Combines codebase analysis, external research, strategy generation, and adversarial debate to produce a decision-ready report saved to docs/research/. Use when facing 'how should we...', 'what's the best way to...', 'deep think about', or any design question with multiple valid approaches."
user-invocable: true
argument-hint: "<design question or topic>"
---

# Deep Think

Structured design thinking for open-ended technical questions. The upstream thinking that leads to `/plan-feature`, `/challenge`, or an ADR.

## Input

`$ARGUMENTS` — the design question.

## Step 0: Track Progress

Before starting, create a task for each phase below using TaskCreate. Chain sequential phases with addBlockedBy. As you work, update each task's status to `in_progress` when starting it and `completed` when done.

## Phase 1: Frame the Question

Write a **Problem Frame** before researching anything:

```
QUESTION: [restate precisely]
CONSTRAINTS: [what can't change]
DECISION TYPE: [reversible/irreversible, blast radius]
SUCCESS CRITERIA: [what would a good answer look like?]
```

If too vague to frame, ask the user to narrow it.

## Phase 2: Codebase Analysis

Launch an **Explore agent** — what exists today, what constraints does the architecture impose, what's partially built that could be leveraged? Output specific file paths, structs, and evidence — not speculation.

## Phase 3: External Research

Launch a **deep-research agent** (or targeted web searches) to survey the landscape:

- **Prior art:** How do competitors/similar tools solve this?
- **Ecosystem:** What libraries, crates, frameworks exist?
- **Best practices:** What do practitioners recommend?
- **Anti-patterns:** What's been tried and failed?

Every claim needs a source URL.

## Phase 4: Generate Strategies

Generate **3-5 concrete strategies** based on Phase 2-3. For each:

| Field | Content |
|-------|---------|
| **Name** | Short descriptive label |
| **Description** | 2-3 sentences, concrete |
| **Requires** | Codebase changes, new deps, data model changes |
| **Strengths** | What it does well |
| **Weaknesses** | Where it falls short |
| **Effort** | T-shirt size (S/M/L) + complexity driver |
| **Risk** | What could go wrong, blast radius |

Include at least one "simplest thing" and one "do it properly" strategy.

## Phase 5: Adversarial Debate

Launch **/quorum** with the top 3 strategies. Give agents the full context from Phases 1-4.

**Skip if** one strategy is clearly dominant after Phase 4. Note why.

## Phase 6: Synthesize and Record

1. Write the exploration document using the template in `references/output-template.md` to `docs/research/NNN-<slug>.md`
2. Present a concise summary: question, strategy comparison table, recommendation, and next step (ADR? `/plan-feature`? more research?)

## Final Check

Run TaskList. If any task is not `completed`, go back and finish it now.

## Anti-patterns

- **Researching without framing** — "research everything about X" wastes tokens. Frame first.
- **Strategies without research** — armchair strategies are generic. Phase 3 grounds them.
- **Skipping the debate** — your first ranking is often wrong. The quorum catches blind spots.
- **Analysis paralysis** — if Phase 4 produces a clear winner, skip quorum and say so. Process serves the decision.
