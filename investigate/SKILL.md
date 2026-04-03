---
name: investigate
description: "Systematic investigation of a production bug or performance issue. Traces symptoms to root cause through code analysis, hypothesis testing, and empirical validation."
user-invocable: true
argument-hint: "[error message, symptom, or issue number]"
---

Investigate the problem described below. Follow the structured investigation protocol — do not jump to fixes.

$ARGUMENTS

## Pre-flight

Before starting, verify you have enough to work with:
- A specific error message, symptom, or issue number
- An affected endpoint, feature, or user journey
- A reproducing input or example (or evidence that reproduction is environment-dependent)

If any are missing, ask for them before proceeding.

## Problem Classification

Classify the problem to select the right investigation depth and strategy categories:

| Class | Signal | Phase 4 depth |
|-------|--------|---------------|
| **Performance / resource exhaustion** | OOM, timeout, slow query, high latency | Full exhaustive enumeration |
| **Logic error / wrong output** | Wrong calculation, missing data, incorrect state | Trace code path, may short-circuit at Phase 2 |
| **Reliability / intermittent failure** | Flaky, race condition, works-then-doesn't | Focus on concurrency, state, timing |
| **Data integrity** | Missing records, inconsistent state, corruption | Focus on write paths, migrations, replication |

**Scope calibration:** For P0 production outages, run full Phase 4 exhaustive enumeration. For P2+ minor regressions, enumerate 3-5 candidates and pick the winner.

## Investigation Protocol

### Step 0: Track Progress

Before starting, create a task for each phase below using TaskCreate. Chain sequential phases with addBlockedBy. As you work, update each task's status to `in_progress` when starting it and `completed` when done.

### Phase 1: Reproduce and Scope

1. **Capture the symptoms exactly.** What error? What endpoint? What input? What environment?
2. **Identify what works vs what doesn't.** Find a passing case and a failing case with the same setup. The difference between them is the clue.
3. **Narrow the blast radius.** Is this one customer, one query, one feature, or systemic?

If reproduction fails in dev, identify the conditions that differ from production (data volume, index state, concurrent load) and proceed to Phase 2 with production evidence — code reading + log analysis.

### Phase 2: Trace the Code Path

1. **Find the entry point.** Which API endpoint, tRPC procedure, or function handles this request?
2. **Trace the full call chain.** Entry point -> service -> query builder -> database. Don't skip layers.
3. **Generate the actual query/payload.** If the issue involves a database query, construct the exact query the code produces for the failing input. Run the query builder locally if possible.
4. **Identify which layer fails.** Is it the query construction, the database execution, the response parsing, or the frontend rendering?

**Early exit:** If you find an unambiguous defect with high confidence (e.g., assignment instead of comparison, missing null check, wrong column name), document it with evidence and skip to Phase 7. Record that Phase 4 was not exhausted and why.

### Phase 3: Form and Validate Hypotheses

1. **Generate MULTIPLE hypotheses** — at least 3. Don't stop at the first plausible explanation. The first guess is often wrong, especially for subtle bugs.
2. **Rank by likelihood.** Consider: does this hypothesis match the actual user experience? A race condition requiring sub-second timing is low-probability if users report the bug on normal save-reload cycles. Rank accordingly.
3. **State each hypothesis explicitly** before testing it. "I believe X is happening because Y."
4. **Sanity-check against user behavior.** Would a real user actually trigger this code path? If the hypothesis requires unusual timing, edge-case input, or specific sequences that users wouldn't normally do, it's probably not the root cause — even if the code path exists.
5. **Design a test that would disprove your hypothesis.** If you can't disprove it, it's not a hypothesis — it's a guess.
6. **Test empirically.** Run queries, check logs, probe limits. Don't reason about what "should" happen — verify what does.
7. **For state/persistence bugs: trace the full round-trip.** Follow the data from user input → in-memory state → serialization → storage → deserialization → display. The break is at one of these boundaries — find which one by checking the value at each step.
8. **Record what you ruled out.** Failed hypotheses are valuable — they prevent the implementer from going in circles.

### Phase 4: Exhaustive Strategy Enumeration

Before committing to any fix, enumerate ALL possible strategies — even unlikely ones. Select categories based on the problem class:

**Performance / resource exhaustion:**
- Query-level (rewrite, hints, settings, batching, sampling)
- Schema/storage (new columns, projections, materialized views, indexes, partitioning)
- Infrastructure (memory limits, instance sizing, caching)
- Application-level (pre-aggregation, caching, different data source)
- Compression/encoding (codecs, granularity, block sizes)

**Logic error / wrong output:**
- Code path (wrong branch, missing condition, off-by-one)
- Data (wrong column, missing join, stale cache)
- Type/coercion (implicit conversion, null handling, timezone)
- Configuration (feature flag, env var, default value)

**Reliability / intermittent:**
- Concurrency (race condition, lock contention, connection pool)
- State (stale cache, eventual consistency, retry without idempotency)
- Resources (memory pressure, connection exhaustion, disk space)
- External dependencies (timeout, rate limit, network partition)

### Phase 5: Test Each Strategy

For each strategy:
1. Can it be tested on dev/staging right now?
2. If yes — test it. Record the result with numbers (memory usage, latency, row counts).
3. If no — document why and what would be needed to test it.
4. Classify: works / doesn't work / works but heavy / needs more investigation

Before creating any schema object (table, projection, materialized view, index) for testing, name it with a `_investigate_` prefix. Drop all `_investigate_*` objects unconditionally at the end.

### Phase 6: Find the Simplest Fix

The best fix is often not the most obvious one. Check:
- **Does the data already exist somewhere else?** A different table, a pre-computed column, a materialized view.
- **Is the code doing unnecessary work?** Joining a table it doesn't need, reading columns it doesn't use.
- **Can the problem be avoided entirely?** Different query path, different data source, different algorithm.

A one-line change that uses existing data beats a schema migration every time.

### Phase 7: Write Up Findings

Structure the output as an **Investigation section** for a GitHub issue:

1. **Symptoms** — what's broken, exact errors
2. **Root cause** — what's actually happening, with evidence
3. **Strategies tested** — table of all approaches with results and numbers
4. **Findings** — what the implementer should know, including what was ruled out
5. **Caveats** — what the implementer should validate independently

If `$ARGUMENTS` contains a GitHub issue number, post findings as a comment on that issue. Otherwise, output to the conversation for the user to direct.

**Do not prescribe a specific fix.** Present findings and evidence. The implementer owns the solution. If one strategy is clearly superior, present the evidence — the implementer will reach the same conclusion.

## Final Check

Run TaskList. If any task is not `completed`, go back and finish it now.

## Rules

- **Never jump to a fix before Phase 4** (unless Phase 2 early-exit applies).
- **Test empirically, don't theorize.** "It should work" is not evidence.
- **Record numbers.** "It's faster" means nothing. "10 MB vs 600 MB" means everything.
- **Check if the data already exists.** Before building new infrastructure, search for existing columns, tables, materialized views, or pre-computed values.
- **Clean up after yourself.** Drop any test objects you created during investigation.
- **Inconclusive is a valid outcome.** If you can't determine root cause, say so. Document what was narrowed down and what data from production would be needed to continue.
