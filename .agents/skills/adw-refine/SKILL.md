---
name: adw-refine
description: >
  Phase 6 of the agentic-dev-workflow: Ticket Refinement. Reviews every ticket in
  5-plan.md for gaps, missing acceptance criteria, and hidden dependencies. Updates
  5-plan.md in place. Requires explicit human sign-off before execution begins. Use only
  when the agentic-dev-workflow orchestrator skill is active and has explicitly entered
  Phase 6 — Refine.
---

# Phase 6 — Ticket Refinement

Update `5-plan.md` with refinement findings, then obtain human sign-off. This is the
mandatory gate before execution. Rushing it is the most common cause of mid-execution
agent failures caused by ambiguous, underspecified, or dependency-hidden tickets.

## What refinement does

- **Gap discovery** — find what is missing or ambiguous in each ticket description
- **Acceptance criteria validation** — every ticket must have a testable definition of done
- **Dependency resolution** — surface hidden blocking relationships not caught in planning

## Steps

1. **Read `5-plan.md`** in full.

2. **Review each ticket** against three questions:
   - Is the description specific enough that an agent could implement it without asking questions?
   - Does it have at least one testable acceptance criterion?
   - Are all its dependencies on other tickets explicit?

3. **Update `5-plan.md`** in-place:
   - Add or improve acceptance criteria on any ticket missing them
   - Add missing blocking relationships to the dependency graph
   - Clarify ambiguous descriptions
   - Add a `## Refinement notes` section at the bottom:

     ```markdown
     ## Refinement notes
     - T-01: Added acceptance criterion for error case
     - T-03: Added dependency on T-02 (both modify the same config file)
     - T-05: Clarified that "update" means HTTP PATCH, not PUT
     ```

4. **Request human sign-off.** Present the updated `5-plan.md` and explicitly ask:
   _"The plan has been refined. Please review and confirm it is ready for execution."_
   Do not proceed to Phase 7 until the human explicitly approves.

5. **Update `0-state.md`**: `current-phase: 6 — Refine`, `phase-status: complete`,
   check Phase 6 in Completed phases. Add a note: "Human sign-off received."

## Quality bar

Refinement is complete when:
- Every ticket has at least one testable acceptance criterion
- No ticket description contains "as needed", "etc.", or "and other things"
- All inter-ticket dependencies are explicit in the dependency graph
- Human has explicitly confirmed the plan
