---
name: adw-prototype
description: >
  Phase 3 of the agentic-dev-workflow: Prototype (optional). Creates a throwaway spike
  to reduce UI/UX or architectural uncertainty before committing to a PRD. Produces no
  persisted artifact; findings are noted in 0-state.md. Use only when the
  agentic-dev-workflow orchestrator skill is active and has explicitly entered Phase 3 —
  Prototype, as specified in 1-phase-plan.md.
---

# Phase 3 — Prototype (Optional)

This phase exists to reduce uncertainty before writing a PRD. It is a throwaway spike —
code written here is not production code and is not committed. Its purpose is to answer
a specific question.

## When this phase runs

Only if `1-phase-plan.md` lists Phase 3 as "run". Two conditions justify running it:
- There is UI/UX work where the right interaction pattern is unknown
- There is architectural uncertainty where multiple approaches are plausible and the
  right choice affects downstream decisions

If neither condition applies, the phase was already skipped in Phase 1.

## Steps

1. **State the prototype question.** Before writing any code, write one sentence:
   _"This prototype answers: [specific question]."_
   If you cannot write that sentence clearly, clarify scope with the human first.

2. **Build the spike.** Keep it minimal — the goal is evidence, not quality:
   - Use the simplest possible implementation that answers the question
   - Do not add error handling, tests, or polish
   - If the question cannot be answered in a short exploration, raise a CRP rather than
     continuing to explore indefinitely

3. **Document findings** in a brief message to the human:
   - What the spike revealed
   - Which approach the PRD should adopt and why
   - Any constraints or patterns discovered that `adw-prd` must know

4. **Discard the spike code.** Do not commit it. This phase produces no persisted file
   artifact — only the findings message.

5. **Update `0-state.md`**: `current-phase: 3 — Prototype`, `phase-status: complete`.
   Add prototype findings to the Notes section so `adw-prd` can access them without a
   separate file.
