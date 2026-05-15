---
title: Production Plan
status: draft
owner_role: producer
contributors:
  - engineering-lead
  - game-designer
  - creative-product-lead
  - art-director
inputs:
  - 02-vision-brief.md
  - 04-design-package.md
  - 05-prototype-plan.md
  - 00-risk-register.md
open_questions: []
approved_by:
updated_at: <YYYY-MM-DD>
---

# 06 — Production Plan

## Purpose

Convert the approved concept into a sequenced, dependency-explicit plan for building the game. Only starts after either the stress test passes with acceptable risk or prototype goals are met.

## Gate Check

<!-- Confirm the pre-conditions for production planning. -->

- [ ] Concept stress test outcome: `approved` or `approved-with-conditions`.
- [ ] Prototype plan outcome (if required): `approved`.
- [ ] All critical-severity risks are either resolved or have accepted mitigations.

## Milestones

<!-- Ordered sequence of major delivery points. Each milestone is a playable or demonstrable state. -->

| Milestone | Description | Deliverables | Definition of Done |
|---|---|---|---|
| M1 | | | |
| M2 | | | |
| M3 | | | |

## Slice Backlog

<!-- Implementation slices ordered by dependency. Each slice will become one or more IMP-XXX briefs. -->
<!-- Slices should be independently understandable and deliverable. -->

| Slice ID | Name | Milestone | Dependencies | Effort | Primary Role |
|---|---|---|---|---|---|
| S-001 | | | | | |
| S-002 | | | | | |

## Dependency Map

<!-- Explicit dependencies between slices. Undeclared dependencies are a leading cause of ordering failures. -->

```
S-001 → S-002 → S-004
S-003 (parallel with S-002)
```

## Definitions of Done

<!-- What does "done" mean for this project? Apply to every slice. -->

A slice is done when:

1. It matches the approved implementation brief.
2. Relevant tests pass.
3. Trade-offs and follow-up risks are recorded.
4. Engineering Lead has signed off on testability.
5. Human has approved before the next slice begins.

## Recommended Sequence

<!-- Walk-through of the recommended build order and why. -->

## Major Risks

<!-- Top risks for the production phase. Full entries in 00-risk-register.md. -->

| Risk ID | Description | Mitigation |
|---|---|---|
| | | |

## Alternatives

### Alternative A
Description:
Trade-offs:

## Open Questions

1.

## Acceptance Criteria

- [ ] Gate check is satisfied.
- [ ] Milestones are named and described.
- [ ] Slices are listed with dependencies.
- [ ] Definitions of done are explicit.
- [ ] Human approval recorded.

## Approval Status

Status: `draft`
Approved by:
Notes:
