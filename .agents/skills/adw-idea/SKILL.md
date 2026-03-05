---
name: adw-idea
description: >
  Phase 1 of the agentic-dev-workflow: Idea. Clarifies the task, derives the task slug,
  and produces 1-phase-plan.md — the artifact that governs which phases run. Also
  initialises 0-state.md. Use only when the agentic-dev-workflow orchestrator skill is
  active and has explicitly entered Phase 1 — Idea.
---

# Phase 1 — Idea

Produce `1-phase-plan.md` and initialise `0-state.md`. This artifact drives every
subsequent phase; getting it right is the highest-leverage investment in the workflow.

## Steps

1. **Understand the task.** If the request is ambiguous, ask the minimum questions needed
   to determine scope and goal. Aim for one clarifying exchange, not a long interview.

2. **Derive the task slug.** Short kebab-case label from the task title:
   `add-user-auth`, `fix-login-redirect`, `refactor-payment-service`.

3. **Decide the phase plan.** Apply skip conditions:
   - Phase 3 (Prototype) may be skipped if there is no UI/UX work and no architectural
     uncertainty. Document the reason explicitly — silent skips are not permitted.
   - All other phases are mandatory; do not skip them.

4. **Write `1-phase-plan.md`** in `.adw/<task-slug>/`:

   ```markdown
   # Phase Plan: <task-slug>

   ## Task
   <one-paragraph description of the task and its goal>

   ## Task slug
   <task-slug>

   ## Phase plan
   | # | Phase | Status | Reason if skipped |
   |---|---|---|---|
   | 1 | Idea | complete | — |
   | 2 | Research | run | — |
   | 3 | Prototype | skip / run | <reason if skip> |
   | 4 | PRD | run | — |
   | 5 | Plan | run | — |
   | 6 | Refine | run | — |
   | 7 | Execution | run | — |
   | 8 | QA | run | — |

   ## Context
   <links to relevant files, tickets, prior conversations, or "none">
   ```

5. **Create `.adw/<task-slug>/0-state.md`** (format in
   `agentic-dev-workflow/references/artifact-contracts.md` §2) with:
   - `current-phase: 1 — Idea`
   - `phase-status: complete`
   - Phase 1 checked in Completed phases

6. **Hand off to orchestrator.** State the task slug and confirm Phase 1 is complete.

## Quality bar

`1-phase-plan.md` is complete when:
- The task description is specific enough that a developer who has never seen the
  conversation could understand what to build
- Every skipped phase has a documented reason
- The task slug is valid kebab-case (lowercase, hyphens only, no spaces)
