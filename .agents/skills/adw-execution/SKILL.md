---
name: adw-execution
description: >
  Phase 7 of the agentic-dev-workflow: Execution Loop. Implements tickets from the
  refined 5-plan.md in dependency order. Produces 7-mrp.md (Merge-Readiness Pack) on
  success or 7-crp.md (Consultation Request Pack) on a blocker. Use only when the
  agentic-dev-workflow orchestrator skill is active and has explicitly entered Phase 7 —
  Execution, and human sign-off on 5-plan.md has been confirmed.
---

# Phase 7 — Execution Loop

Work through tickets in `5-plan.md` in dependency order. Produce `7-mrp.md` when all
tickets are complete, or `7-crp.md` if execution is blocked.

## Inputs

- `5-plan.md` — refined tickets with acceptance criteria and dependency graph
- `2-research.md` — codebase patterns and constraints to follow
- `4-prd.md` — acceptance criteria to verify at completion

## Core loop

For each ticket (blocked-by tickets must complete first):

1. **Implement** the ticket. Follow the patterns and conventions from `2-research.md`.
2. **Verify** its acceptance criteria pass.
3. **Mark complete** in `5-plan.md` by adding `**Status: complete**` to the ticket.
4. **Update `0-state.md` Notes** with the completed ticket ID.

Repeat until all tickets are complete or a blocker is hit.

## Blocker handling (CRP path)

If execution cannot continue — an ambiguous requirement, an unexpected constraint, a
decision beyond the agent's authority — stop immediately and produce `7-crp.md`:

```markdown
# Consultation Request: <task-slug>

## Blocker
<one paragraph: exactly what the agent cannot proceed past>

## Decision needed
<the specific question or choice a human needs to resolve>

## Context
<relevant code, error output, or ticket reference>

## Options considered
<what the agent has already tried or ruled out>
```

Update `0-state.md`: `phase-status: in-progress` (not complete). Add the blocker to Notes.

After the human resolves the blocker: update Notes with the resolution, delete `7-crp.md`,
and resume from the blocked ticket.

## Completion (MRP path)

When all tickets are marked complete, verify the end state from `4-prd.md`. Then write
`7-mrp.md`:

```markdown
# Merge-Readiness Pack: <task-slug>

## Checklist
- [ ] All tickets in 5-plan.md marked complete
- [ ] Tests pass (paste command + result)
- [ ] Lint clean
- [ ] No regressions in related areas
- [ ] Acceptance criteria from each ticket met (reference ticket IDs)

## Audit trail
<brief narrative of what was done and any notable decisions made during execution>
```

Update `0-state.md`: `current-phase: 7 — Execution`, `phase-status: complete`, check
Phase 7 in Completed phases.

## Constraints

- Respect the dependency graph. Do not implement a ticket before its `blocked-by` tickets
  are complete.
- Follow existing codebase patterns from `2-research.md`. Do not introduce new patterns
  without documenting the reason in the MRP audit trail.
- If a ticket's acceptance criteria are ambiguous, raise a CRP rather than guessing.
