# Artifact Contracts

All phase artifacts are stored under `.adw/<task-slug>/` at the repository root.

## Table of Contents

1. [Directory layout](#1-directory-layout)
2. [0-state.md — Workflow state](#2-0-statemd--workflow-state)
3. [1-phase-plan.md — Idea output](#3-1-phase-planmd--idea-output)
4. [2-research.md — Research output](#4-2-researchmd--research-output)
5. [4-prd.md — PRD output](#5-4-prdmd--prd-output)
6. [5-plan.md — Plan + Refine output](#6-5-planmd--plan--refine-output)
7. [7-mrp.md — Merge-Readiness Pack](#7-7-mrpmd--merge-readiness-pack)
8. [7-crp.md — Consultation Request Pack](#8-7-crpmd--consultation-request-pack)
9. [8-qa-plan.md — QA Plan output](#9-8-qa-planmd--qa-plan-output)

---

## 1. Directory layout

```
.adw/
└── <task-slug>/
    ├── 0-state.md        ← always present; orchestrator reads/writes at every phase boundary
    ├── 1-phase-plan.md
    ├── 2-research.md
    ├── 4-prd.md          ← number 3 is reserved for prototype (no persisted artifact)
    ├── 5-plan.md         ← written by adw-plan, updated in-place by adw-refine
    ├── 7-mrp.md          ← or 7-crp.md (mutually exclusive)
    └── 8-qa-plan.md
```

The task slug is a short kebab-case label derived from the task title (e.g. `add-user-auth`,
`fix-login-redirect`). Generated once in Phase 1; used for all subsequent artifacts.

---

## 2. `0-state.md` — Workflow state

Written by the orchestrator at the start and end of every phase. Read first on resume.

```markdown
# Workflow State: <task-slug>

## Status
current-phase: <phase-number> — <phase-name>
phase-status: in-progress | complete

## Completed phases
- [x] 1 — Idea
- [ ] 2 — Research
- [ ] 4 — PRD
- [ ] 5 — Plan
- [ ] 6 — Refine
- [ ] 7 — Execution
- [ ] 8 — QA

## Notes
<context the agent should know when resuming: decisions made, blockers encountered, etc.>
```

Mid-phase interruption rule: if a phase artifact is incomplete on resume, restart that phase
from scratch. Partial artifacts are overwritten. Phases are idempotent — same inputs produce
same outputs.

---

## 3. `1-phase-plan.md` — Idea output

Produced by `adw-idea`. Consumed by the orchestrator and all phases.

Required sections:
- `## Task` — one-paragraph description of the task and its goal
- `## Task slug` — the kebab-case slug used for the `.adw/` directory
- `## Phase plan` — table listing each phase, its status (run / skip), and skip reason if applicable
- `## Context` — links to relevant files, tickets, or prior conversations

Skip rules: optional phases may be skipped with a documented reason. Mandatory phases
(1, 2, 4, 5, 6, 7, 8) cannot be skipped.

---

## 4. `2-research.md` — Research output

Produced by `adw-research`. Consumed by `adw-prd`, `adw-plan`, `adw-execution`.

Required sections:
- `## Task context` — restatement of what is being built and why
- `## Relevant code` — file paths, function names, patterns found in the codebase
- `## Constraints` — technical constraints, existing patterns that must be respected
- `## Risks` — potential pitfalls or areas of uncertainty
- `## Handoff notes` — summary for downstream phases

Scope: codebase and task context only. No external sources.

---

## 5. `4-prd.md` — PRD output

Produced by `adw-prd`. Consumed by `adw-plan`.

Required sections:
- `## Goal` — what success looks like; ties back to task in `1-phase-plan.md`
- `## End state` — concrete description of the system after the task is done
- `## Acceptance criteria` — specific, testable conditions (each must be falsifiable)
- `## Out of scope` — explicit list of what this task does not cover

---

## 6. `5-plan.md` — Plan + Refine output

Written by `adw-plan`, updated in-place by `adw-refine`.

Required sections:
- `## Tickets` — ordered list of implementation tickets; each ticket has:
  - ID (e.g. `T-01`)
  - Title
  - Description
  - Acceptance criteria (testable)
  - Blocking dependencies (list of ticket IDs this ticket depends on)
- `## Dependency graph` — textual or ASCII representation of blocking relationships
- `## Refinement notes` (added by `adw-refine`) — gap discovery findings, resolved ambiguities

Refinement adds `Acceptance criteria` to any ticket missing it and resolves dependency gaps.
Human sign-off is required before `adw-execution` begins.

---

## 7. `7-mrp.md` — Merge-Readiness Pack

Produced by `adw-execution` when all tickets complete successfully.

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

---

## 8. `7-crp.md` — Consultation Request Pack

Produced by `adw-execution` when execution is blocked.

```markdown
# Consultation Request: <task-slug>

## Blocker
<one paragraph describing exactly what the agent cannot proceed past>

## Decision needed
<the specific question or choice a human needs to resolve>

## Context
<relevant code, error output, or ticket reference>

## Options considered
<what the agent has already tried or ruled out>
```

After the human resolves the blocker, the orchestrator resumes from the blocked ticket.
`0-state.md` is updated to reflect the resolution.

---

## 9. `8-qa-plan.md` — QA Plan output

Produced by `adw-qa`. Consumed by the human reviewer.

Required sections:
- `## Verification checklist` — step-by-step human-in-the-loop checks, each actionable
- `## Automated tests` — list of test commands to run and expected outcomes
- `## Regression areas` — parts of the codebase most likely affected; warrant extra scrutiny
- `## Rollback plan` — steps to revert if issues are found post-merge
