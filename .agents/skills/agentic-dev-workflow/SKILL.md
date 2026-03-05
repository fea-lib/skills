---
name: agentic-dev-workflow
description: >
  Orchestrates a structured 8-phase agentic development workflow (ADLC) for software tasks.
  Phases: Idea → Research → (Prototype) → PRD → Plan → Refine → Execution → QA.
  Load this skill when a user asks to start a new feature, bug fix, or refactor using an
  agentic workflow, or says anything like "let's work on X using the workflow", "start an
  agentic dev workflow", "run the ADW on this", or "let's plan and implement X properly".
  This is the only entry point for the adw-* phase skills — do not trigger those directly.
---

# Agentic Development Workflow

Orchestrates a structured, resumable development lifecycle. Each phase has a dedicated
`adw-*` skill that loads only when that phase is active — keeping the context window lean.

Artifact formats: see `references/artifact-contracts.md`.

## Phase map

| # | Skill | Status | Skip condition |
|---|---|---|---|
| 1 | `adw-idea` | Mandatory | — |
| 2 | `adw-research` | Mandatory | — |
| 3 | `adw-prototype` | Optional | No UI/UX work and no architectural uncertainty |
| 4 | `adw-prd` | Mandatory | — |
| 5 | `adw-plan` | Mandatory | — |
| 6 | `adw-refine` | Mandatory | — |
| 7 | `adw-execution` | Mandatory | — |
| 8 | `adw-qa` | Mandatory | — |

## Starting a new workflow

1. Load `adw-idea` and execute Phase 1. It produces `1-phase-plan.md` which determines
   which optional phases run and documents any skip reasons.
2. Create `.adw/<task-slug>/0-state.md` to initialise workflow state (format in
   `references/artifact-contracts.md` §2).
3. Proceed phase by phase in sequence, loading the corresponding `adw-*` skill for each.
4. Update `0-state.md` at the start and end of every phase.

## Resuming an interrupted workflow

1. Read `.adw/<task-slug>/0-state.md` to determine the current phase and status.
2. If `phase-status: in-progress`, restart that phase from scratch (overwrite partial artifact).
3. If `phase-status: complete`, load the skill for the next phase in the plan.

## Phase transitions

- After each phase completes, confirm the produced artifact is present in `.adw/<task-slug>/`.
- Update `0-state.md` before entering the next phase.
- Mandatory human checkpoints: after Phase 6 (Refine) before entering Phase 7 (Execution).
  Do not start execution without explicit human sign-off on `5-plan.md`.

## Artifact reference

Read `references/artifact-contracts.md` for:
- Directory layout and file naming
- Required sections for each artifact
- `0-state.md`, MRP, and CRP formats
- Mid-phase interruption and resume rules
