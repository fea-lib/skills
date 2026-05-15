---
title: Game Studio — Implementation Plan
status: approved
owner_role: human
updated_at: 2026-05-15
---

# Game Studio — Implementation Plan

## Purpose

Define the ordered build plan for the LLM Agent Game Studio. Each phase produces a testable, usable increment. Later phases build on earlier ones without requiring rework.

Machine-facing implementation contracts for the skill plus CLI build are locked in `phase-0-implementation-addendum.md`. This plan defines build sequencing and expected capabilities; the addendum defines the exact CLI, runtime, persistence, and validation shape.

## Pre-conditions

Before any build work starts, the human must confirm:

1. Repository root path.
2. Target documentation directory path.
3. Whether the studio will live as an OpenCode skill, a standalone agent system, or both.
4. Preferred LLM provider and model for the orchestrator.
5. Preferred LLM provider and model for specialist roles (can be same as orchestrator in v1).

The implementation may proceed only after the contracts in `phase-0-implementation-addendum.md` are treated as locked.

---

## Phase 1 — Studio Shell

**Goal:** The system can track one active project, know what phase it is in, and present the current state to the user.

**Deliverables:**

1. Orchestrator system prompt based on `roles/orchestrator.md`.
2. Startup sequence that reads repo root, docs dir, and project slug from the user.
3. `00-current-state.md` reader — parses and summarises state from the template.
4. `00-risk-register.md` reader — parses and surfaces blocking risks.
5. Phase state machine — maps phase names to numeric IDs and valid transitions.
6. Phase outcome vocabulary enforced: `approved`, `approved-with-conditions`, `rework-required`, `rejected`, `parked`.
7. Response format enforcer: every response ends with recommendation, alternatives, consequences, next action.

**Acceptance Criteria:**

- [ ] Given a project folder with a `00-current-state.md`, the orchestrator correctly identifies the active phase.
- [ ] The orchestrator surfaces the next recommended action on session start.
- [ ] The orchestrator refuses to advance a phase without explicit human approval.
- [ ] Phase transitions are logged in the state file.

**Key Decisions Required:**

1. Is the orchestrator a single long system prompt, or a composable set of instructions?
2. How is project context loaded — file reads at startup, or injected on demand?

---

## Phase 2 — Artefact System

**Goal:** The system can create, read, update, and promote numbered Markdown artefacts. It maintains a single source of truth in the repo.

**Deliverables:**

1. Artefact creation flow — instantiates numbered templates under `projects/<slug>/`.
2. Artefact reader — loads relevant artefacts for the current phase automatically.
3. Frontmatter parser — reads and updates `status`, `approved_by`, `updated_at`.
4. Draft-to-canonical promotion flow — only the orchestrator can promote drafts.
5. Revision tracking — appended comment or changelog entry on every update.
6. `00-current-state.md` writer — keeps the state file current after each major action.
7. `00-risk-register.md` writer — adds and updates risk entries.

**Acceptance Criteria:**

- [ ] A new project can be initialised with the correct folder structure and starter files.
- [ ] The orchestrator can read any numbered artefact and extract key fields.
- [ ] Frontmatter status is updated when a phase is approved or rejected.
- [ ] Draft notes cannot be treated as canonical without promotion.
- [ ] `00-current-state.md` reflects the true state after every interaction.

**Key Decisions Required:**

1. Does the system use file tools directly (read/write) or a thin wrapper?
2. Is frontmatter parsed with a YAML library or via LLM extraction?

---

## Phase 3 — Role Contracts

**Goal:** Each specialist role is implemented as a reusable skill or prompt contract. The orchestrator can invoke any role correctly for the current workflow step.

**Deliverables:**

1. System prompts derived from each role contract file:
   - `creative-product-lead.md`
   - `producer.md`
   - `game-designer.md`
   - `engineering-lead.md`
   - `art-director.md`
2. Per-role output templates enforced in prompts.
3. Routing matrix — table mapping each workflow step to primary, consulted, and review roles.
4. Role invocation logic — orchestrator selects roles from the routing matrix, not free-form.
5. Role skip logging — when a role is skipped, the reason is appended to the active artefact.
6. Deep-dive mode — temporary scoped session using a specialist role, returning control to orchestrator.

**Routing Matrix:**

| Phase | Primary | Consulted | Review |
|---|---|---|---|
| 01 Idea Intake | creative-product-lead | producer (if constraints known) | — |
| 02 Vision Definition | creative-product-lead | game-designer, producer | — |
| 03 Concept Stress Test | producer | creative-product-lead, game-designer, engineering-lead, art-director | — |
| 04 Pre-Production Design | game-designer | creative-product-lead, engineering-lead, art-director, producer | — |
| 05 Prototype Planning | engineering-lead | game-designer, producer, creative-product-lead | — |
| 06 Production Planning | producer | engineering-lead, game-designer, creative-product-lead, art-director | — |
| 07 Change Control | producer | auto-selected by impact area | — |
| 08 Implementation Support | engineering-lead | varies by slice | — |

**Acceptance Criteria:**

- [ ] Each role produces output conforming to its output template.
- [ ] The orchestrator correctly selects the primary role for each workflow step.
- [ ] Consulted roles respond to a primary draft, not independently.
- [ ] Deep-dive sessions load the correct artefacts and return control cleanly.
- [ ] Role outputs reference the artefacts they were given as inputs.

**Key Decisions Required:**

1. Are roles separate agent instances or separate system prompts in the same context?
2. Is role invocation sequential (primary → consulted → review) or via separate API calls?

---

## Phase 4 — Collaborative UX

**Goal:** The studio feels coherent, opinionated, and easy to navigate. The user can drive the workflow conversationally.

**Deliverables:**

1. Session start behaviour — loads state, presents dashboard, recommends next step.
2. Small-batch clarification — when inputs are missing, asks the fewest possible questions before proceeding.
3. Exploratory note handling — ad hoc requests are flagged as `exploratory` and stored outside canonical numbering until promoted.
4. Proactive next-step suggestion — after each major interaction, the orchestrator recommends the next valid step.
5. Jump-ahead warning — if the user skips a phase, the orchestrator warns about missing prerequisites but does not block.
6. Consistent response format — recommendation, alternatives, consequences, next action on every substantive response.
7. Challenge mode — in collaborative mode, weak ideas are challenged before being extended.

**Acceptance Criteria:**

- [ ] Session start surfaces current phase, blocking questions, and recommended next step without requiring user prompting.
- [ ] The system asks at most 3 clarifying questions before proceeding with a partial context.
- [ ] Exploratory notes are clearly marked and cannot enter the artefact system without explicit promotion.
- [ ] Every substantive response ends with a recommendation and at least one alternative.
- [ ] The orchestrator challenges clearly weak design ideas rather than silently extending them.

---

## Phase 5 — Gates and Change Control

**Goal:** Approval gates are enforced. Conflicts with approved vision or scope pause the system cleanly. Change requests are tracked.

**Deliverables:**

1. Approval gate enforcement — phase cannot advance without recorded human approval.
2. Pause and escalation logic — detects conflicts and halts with structured output.
3. Conflict detection — checks incoming requests against approved pillars, vision, and scope.
4. `07-change-decisions.md` writer — creates and appends CHG-XXX entries.
5. Change impact analysis flow — automatically invokes relevant roles based on impact area.
6. Accepted risk flow — open questions can be explicitly accepted and recorded in the risk register.
7. Condition tracking — `approved-with-conditions` entries are tracked until conditions are cleared.

**Pause Output Standard:**

Every pause must include:
1. Clear issue description.
2. Why this blocks progress.
3. Recommended resolution.
4. One or two alternatives with consequences.
5. Exact decision needed from the human.

**Acceptance Criteria:**

- [ ] A request that conflicts with an approved pillar triggers a pause with the standard output.
- [ ] Phase advancement without human approval is impossible.
- [ ] Every change decision is recorded in `07-change-decisions.md` with impacted artefacts listed.
- [ ] `approved-with-conditions` decisions surface their conditions on the next session start.
- [ ] Accepted risks appear in `00-risk-register.md`.

---

## Phase 6 — Bounded Implementation Support

**Goal:** The system can safely support approved development work one slice at a time without overreaching.

**Deliverables:**

1. Implementation brief creation flow — generates `08-implementation-briefs/IMP-XXX-*.md` in the target project from the `templates/08-implementation-brief.md` source template.
2. Execution mode — switches to bounded implementation behaviour when a brief is approved.
3. Pre-execution checklist — verifies brief approval, acceptance criteria, and test expectations exist.
4. Code generation within brief — produces code matching the brief, no more.
5. Test generation — produces tests matching the test strategy in the brief.
6. Non-code deliverable support — schemas, tuning specs, UI flows, engine setup plans.
7. Post-execution review writer — fills out the post-execution section of the brief.
8. Inter-slice gate — requires human review of the post-execution review before the next slice begins.
9. Scope boundary enforcement — refuses to generate code outside the approved brief.

**Technical Proposal Standard:**

Every technical proposal must state:
1. Which functional and non-functional requirements it addresses.
2. The constraints it operates within.
3. Trade-offs.
4. At least one alternative.

**Acceptance Criteria:**

- [ ] Code generation only starts after a brief with approval status `approved` exists.
- [ ] Generated code stays within the brief's defined scope.
- [ ] A conflict between the implementation request and approved vision triggers a pause.
- [ ] The post-execution review is completed before the next slice is approved.
- [ ] Non-code deliverables (schemas, specs, flows) are produced in the same bounded manner.

---

## Phase 7 — Pilot Project

**Goal:** Run the full workflow end-to-end on one real game idea. Validate that the system produces useful output at every phase.

**Pilot Checklist:**

- [ ] Idea Intake: produce a clear idea brief.
- [ ] Vision Definition: produce and approve a vision brief with real pillars.
- [ ] Concept Stress Test: surface at least two genuine risks.
- [ ] Pre-Production Design: produce a compact design package with a clear core loop.
- [ ] Prototype Planning: identify at least one risk-first prototype.
- [ ] Production Planning: produce a sequenced slice backlog.
- [ ] Change Control: make one change request and record it cleanly.
- [ ] Implementation Support: execute one approved implementation brief.

**Evaluation Questions:**

1. Did the workflow produce genuine clarity at each gate?
2. Did role lenses add specific value beyond generic LLM output?
3. Were the gates useful or just friction?
4. Were artefacts compact and decision-grade?
5. Did the system stay in its lane during implementation?
6. Did it challenge weak ideas effectively?

---

## Phase 8 — Post-Pilot Refinement

Only after the pilot, consider:

1. QA as a first-class role.
2. Richer playtest synthesis workflow.
3. External tool integrations (issue tracker, Notion, etc.).
4. More advanced implementation orchestration.
5. Automated evaluation harnesses.
6. Sample art and prompt pipeline.

---

## Build Order Summary

| Phase | What it enables |
|---|---|
| 1 — Studio Shell | Project state tracking and session flow |
| 2 — Artefact System | Canonical memory and document lifecycle |
| 3 — Role Contracts | Specialist expertise at each workflow step |
| 4 — Collaborative UX | Coherent, opinionated studio feel |
| 5 — Gates and Change Control | Vision preservation and drift prevention |
| 6 — Bounded Implementation | Safe development execution support |
| 7 — Pilot | Real-world validation |
| 8 — Refinement | Post-pilot improvements only |

## Non-Negotiable v1 Scope

Keep:
- Orchestrator.
- Five role contracts.
- Numbered artefacts.
- Current-state and risk-register.
- Phase gates.
- Change control.
- Bounded implementation briefs.

Defer if needed:
- Advanced art support.
- Multi-role parallel review.
- Autonomous asset production.
- Long-form debate workflows.
- Live-ops or post-launch structures.
