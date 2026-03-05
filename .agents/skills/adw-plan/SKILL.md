---
name: adw-plan
description: >
  Phase 5 of the agentic-dev-workflow: Implementation Plan. Decomposes the PRD into an
  ordered list of implementation tickets with explicit blocking dependencies. Produces
  5-plan.md (later updated in-place by adw-refine). Use only when the
  agentic-dev-workflow orchestrator skill is active and has explicitly entered Phase 5 — Plan.
---

# Phase 5 — Implementation Plan

Produce the initial `5-plan.md`. This document is the work breakdown structure. It is
updated in-place during Phase 6 (Refine), then consumed by execution.

## Inputs

- `4-prd.md` — goal, end state, acceptance criteria, out of scope
- `2-research.md` — relevant code, constraints, risks

## Steps

1. **Read the inputs** listed above.

2. **Decompose into tickets.** Each ticket should:
   - Be completable in a single focused coding session
   - Have a single clear responsibility
   - Map to one or more acceptance criteria from `4-prd.md`

3. **Write `5-plan.md`** in `.adw/<task-slug>/`:

   ```markdown
   # Implementation Plan: <task-slug>

   ## Tickets

   ### T-01: <title>
   **Description:** <what to implement>
   **Acceptance criteria:** <testable condition(s) specific to this ticket>
   **Blocks:** none | T-02, T-03, ...
   **Blocked by:** none | T-01, ...

   ### T-02: <title>
   ...

   ## Dependency graph
   T-01 → T-03
   T-02 → T-03
   (or "No blocking dependencies" if all tickets are independent)
   ```

4. **Check completeness.** Every acceptance criterion in `4-prd.md` must be covered by
   at least one ticket. Add a ticket for any uncovered criterion.

5. **Update `0-state.md`**: `current-phase: 5 — Plan`, `phase-status: complete`,
   check Phase 5 in Completed phases.

## Guidance on ticket granularity

- Too coarse: "Implement authentication" (spans multiple files, multiple concerns)
- Too fine: "Add import statement to auth.ts" (not meaningful standalone work)
- Right: "Add JWT validation middleware", "Wire middleware to protected routes"

Hidden dependencies are the most common cause of execution failures. If ticket B touches
code that ticket A modifies, make that dependency explicit now.
