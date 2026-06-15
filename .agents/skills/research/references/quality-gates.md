# Quality Gates

Run these checks before finalization. A failed gate should not be hidden.

## Required Checks

1. **Brief fidelity**
   - Does the report answer the question and intended use from `brief.md`?

2. **Source diversity vs depth and scope**
   - Does source breadth match `quick|standard|deep` and selected source classes?

3. **Citation coverage for key claims**
   - Are important factual claims backed by explicit source references?

4. **Recency adequacy**
   - For time-sensitive topics, are stale-source risks called out?

5. **Conflict visibility**
   - Are material contradictions surfaced and labeled unresolved when needed?

6. **Blindspot coverage**
   - Opposing views
   - Recency gaps
   - Practitioner vs theoretical balance
   - Geographic/cultural variation
   - Adjacent domains
   - Negative results
   - Stakeholder perspectives

7. **Evaluator verdict**
   - Record overall evaluator score, or explicit evaluator-failure note.

## Failure Policy

- Do not fabricate confidence to satisfy gates.
- If budget or tool constraints prevent closure, finalize with explicit gaps.
- Mirror gate failures in both `evaluation.md` and `final-report.md`.

## Suggested `evaluation.md` Layout

```markdown
---
title: Evaluation - <run-slug>
---

# Evaluation

## Gate Results
- Brief fidelity: pass|warn|fail
- Source diversity: pass|warn|fail
- Citation coverage: pass|warn|fail
- Recency adequacy: pass|warn|fail
- Conflict visibility: pass|warn|fail
- Blindspot coverage: pass|warn|fail
- Evaluator verdict: pass|warn|fail

## Notes
- <Concise rationale per non-pass gate>

## Unresolved Issues
- <Explicit list>
```
