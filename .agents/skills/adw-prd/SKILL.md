---
name: adw-prd
description: >
  Phase 4 of the agentic-dev-workflow: PRD. Translates research findings into a precise
  end-state definition with testable acceptance criteria. Produces 4-prd.md. Use only
  when the agentic-dev-workflow orchestrator skill is active and has explicitly entered
  Phase 4 — PRD.
---

# Phase 4 — PRD

Produce `4-prd.md`. This document defines what "done" looks like. A good PRD prevents
scope creep during planning and gives the execution phase a clear target.

## Inputs

- `1-phase-plan.md` — task description and context
- `2-research.md` — codebase findings, constraints, risks
- `0-state.md` Notes — prototype findings if Phase 3 ran

## Steps

1. **Read the inputs** listed above. The PRD reflects everything learned in research
   and (if applicable) the prototype. Do not re-research the codebase here.

2. **Write `4-prd.md`** in `.adw/<task-slug>/`:

   ```markdown
   # PRD: <task-slug>

   ## Goal
   <what success looks like; one paragraph tied directly to the task from 1-phase-plan.md>

   ## End state
   <concrete description of the system after the task is done; what a developer would
   observe when standing in front of the finished product>

   ## Acceptance criteria
   - AC-01: <specific, testable condition>
   - AC-02: <specific, testable condition>
   - ...

   ## Out of scope
   - <explicit list of things this task does not cover>
   ```

3. **Validate acceptance criteria.** Each criterion must be:
   - Falsifiable — a test or check could fail it
   - Specific — no "should work correctly" or "should be fast"
   - Tied to observable behaviour, not implementation details

4. **Update `0-state.md`**: `current-phase: 4 — PRD`, `phase-status: complete`,
   check Phase 4 in Completed phases.

## Quality bar

`4-prd.md` is complete when:
- Every acceptance criterion is falsifiable
- Out of scope names at least one thing (forces conscious scoping decisions)
- The end state is concrete enough that a developer can tell when they have reached it
