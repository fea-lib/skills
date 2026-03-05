---
name: adw-qa
description: >
  Phase 8 of the agentic-dev-workflow: QA Plan. Produces a human-in-the-loop verification
  checklist, automated test commands, regression areas, and rollback plan for the completed
  implementation. Produces 8-qa-plan.md. Use only when the agentic-dev-workflow orchestrator
  skill is active and has explicitly entered Phase 8 — QA, and 7-mrp.md is present.
---

# Phase 8 — QA Plan

Produce `8-qa-plan.md`. This artifact is the handoff to the human reviewer — a structured
checklist for verifying the implementation is correct and safe to merge.

## Inputs

- `7-mrp.md` — completed tickets, test results, audit trail
- `4-prd.md` — acceptance criteria to verify
- `2-research.md` — regression areas identified during research

## Steps

1. **Read the inputs** listed above.

2. **Write `8-qa-plan.md`** in `.adw/<task-slug>/`:

   ```markdown
   # QA Plan: <task-slug>

   ## Verification checklist
   - [ ] <actionable check tied to AC-01>
   - [ ] <actionable check tied to AC-02>
   - [ ] <additional check for edge case or regression>
   - ...

   ## Automated tests
   | Command | Expected outcome |
   |---|---|
   | `<test command>` | All tests pass |
   | `<lint command>` | No errors |

   ## Regression areas
   <specific parts of the codebase most likely affected by this change>

   ## Rollback plan
   1. <step to revert the change if issues are found post-merge>
   2. ...
   ```

3. **Update `0-state.md`**: `current-phase: 8 — QA`, `phase-status: complete`, check
   Phase 8 in Completed phases. Add a note that the workflow is complete.

4. **Announce completion.** Inform the human that the workflow is complete and
   `8-qa-plan.md` is ready for review alongside `7-mrp.md`.

## Quality bar

`8-qa-plan.md` is complete when:
- Every acceptance criterion from `4-prd.md` maps to at least one verification check
- Each check is actionable (a human can execute it without further interpretation)
- Regression areas are named specifically (not "everything")
- The rollback plan is specific enough to follow under pressure
