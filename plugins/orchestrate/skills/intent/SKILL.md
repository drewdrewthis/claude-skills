---
name: intent
description: "Metacognitive checkpoint — analyze user intent before executing. Use standalone or let orchestrate/plan invoke it. Forces critical thinking about what the user actually wants."
user-invocable: true
argument-hint: "[user request or instruction to analyze]"
---

# Intent Analysis

Analyze the **trajectory of the entire conversation** — not just the most recent message.

Additional context, if provided: $ARGUMENTS

### Step 0: Track Progress

Before starting, create a task for each phase/step below using TaskCreate. Chain sequential phases with addBlockedBy. As you work, update each task's status to `in_progress` when starting it and `completed` when done.

## How to Read Intent

Intent lives in the arc of the conversation, not in individual messages. Before answering any questions below:

1. **Trace the thread.** What did the user start trying to accomplish? What has happened since? Where is the conversation heading?
2. **Look for the underlying drive.** The user's literal words are symptoms. What outcome are they actually steering toward? What would make them say "yes, that's exactly what I wanted"?
3. **Notice pivots and corrections.** If the user has redirected, pushed back, or expressed dissatisfaction — that's signal about what they *actually* care about, which may differ from the original ask.
4. **Distinguish the task from the goal.** The task is what was asked. The goal is why it matters. Always optimize for the goal.

This skill works as a **circuit breaker** at any point — not just at the start of work.

## The Questions

Answer each of these explicitly. Do not skip any. Do not treat this as a formality.

### 1. What is the user's trajectory?
- What arc has this conversation followed? Where did it start, and where is it heading?
- What is the **underlying goal** — the outcome they care about, not the literal words of the last message?
- What does "success" look like from their perspective?
- What corrections or pushback have they given? What do those reveal about their real priorities?

### 2. Am I solving the right problem?
- Apply the **5 Whys**: Why is the user asking this? Why does that matter? Keep going until you hit the root motivation.
- Is the current approach addressing a symptom or the actual problem?
- Is there a simpler path that achieves the same outcome?
- Are there assumptions baked into the current direction that should be questioned?
- Would a senior engineer look at the full conversation and say "yes, right trajectory" or "wait, you've drifted"?

### 3. What am I not being asked that I should flag?
- Risks, trade-offs, or second-order effects the user may not have considered
- Missing context that would change the approach
- Alternative approaches worth mentioning
- Things that could go wrong
- Ways the current trajectory could miss the actual goal

### 4. Should I push back?
- Is the current direction a good idea? Be honest.
- If not, what would you suggest instead?
- Is the scope right, or is it too big / too small for the actual goal?
- Am I about to do something the user will correct me on, based on the pattern of this conversation?

## Decision

After answering the questions above, take exactly ONE action:

| Action | When | What to do |
|--------|------|------------|
| **Proceed** | Intent is clear, approach is sound | State your understanding and continue |
| **Propose alternative** | Goal is clear but there's a better way | Present the alternative, ask the user |
| **Clarify** | Intent is ambiguous or missing critical context | Ask specific questions (not vague "can you elaborate?") |
| **Push back** | This is a bad idea | Explain why, constructively, and suggest a better direction |

### Final Check

Run TaskList. If any task is not `completed`, go back and finish it now.

## What "doing this right" looks like

- You genuinely considered an alternative, even if you concluded the original approach is correct
- You identified at least one risk or trade-off, even if it's minor
- Your restatement of intent adds something — it's not just parroting the request back
- If you're proceeding, you can articulate WHY this is the right approach, not just that it is

## What "doing this wrong" looks like

- Writing "the intent is clear, proceeding" without any actual reflection
- Restating the request verbatim and calling it "intent analysis"
- Identifying zero risks or trade-offs (there are always some)
- Never pushing back or proposing alternatives across many invocations (you're rubber-stamping)
