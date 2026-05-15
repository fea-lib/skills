# Workflow Reference

Detailed phase rules, gate requirements, artefact contracts, and escalation rules.
Load when the orchestrator needs to know the exact requirements for a phase or gate.

## Phase order

```
01-idea-intake
02-vision-definition
03-concept-stress-test
04-pre-production-design
05-prototype-planning  (optional — may skip from 04 to 06)
06-production-planning
07-change-control      (standing — always available, not sequential)
08-implementation-support
```

## Gate rules

A phase cannot advance until its gate artefact has `approved` or `approved-with-conditions`
status, set by explicit human confirmation.

| Leaving phase | Gate artefact | Hard gate? |
|---|---|---|
| 01-idea-intake | `01-idea-brief.md` | Yes |
| 02-vision-definition | `02-vision-brief.md` | Yes |
| 03-concept-stress-test | `03-concept-stress-test.md` | Yes |
| 04-pre-production-design | `04-design-package.md` | Yes |
| 05-prototype-planning | `05-prototype-plan.md` | Yes |
| 06-production-planning | `06-production-plan.md` | Yes |
| 08-implementation-support | Approved `IMP-XXX` brief before each slice | Yes |

To advance: `python3 .agents/skills/game-studio/scripts/game-studio ... phase advance --to <next-phase>`

The CLI will fail with a clear error if the gate is not met.

## Phase behaviour

### 01 Idea Intake

Primary: creative-product-lead

Goal: capture the game idea with enough clarity to evaluate whether it is worth pursuing.

Output: `01-idea-brief.md`

Required contents:
- One-sentence pitch.
- Genre and target platform.
- Intended player and player goal.
- Core loop hypothesis.
- What makes it different.
- Initial constraints (team, budget, timeline if known).

Gate condition: human approves the brief as worth pursuing.

### 02 Vision Definition

Primary: creative-product-lead. Consulted: game-designer, producer.

Goal: lock the creative pillars, target player, and non-goals so all downstream decisions
have a reference point.

Output: `02-vision-brief.md`

Required contents:
- Creative pillars (3–5 non-negotiable design principles).
- Target player profile.
- Core experience promise.
- Explicit non-goals.
- Comparable references and how this differs.

Gate condition: human approves the vision. Approved pillars are locked — changes require a
`change request` entry and human approval.

### 03 Concept Stress Test

Primary: producer. Consulted: all roles.

Goal: surface the riskiest assumptions before committing to pre-production. Kill weak concepts early.

Output: `03-concept-stress-test.md`

Required contents:
- Assumptions being tested.
- Risk assessment per role (feasibility, design, delivery, art).
- Kill/proceed recommendation with reasoning.
- Open questions that must be answered before proceeding.
- Risks added to `00-risk-register.md`.

Gate condition: human makes explicit proceed / kill / park decision.

### 04 Pre-Production Design

Primary: game-designer. Consulted: creative-product-lead, engineering-lead, art-director, producer.

Goal: produce a compact, decision-grade design package — not a full GDD.

Output: `04-design-package.md`

Required contents:
- Core loop description.
- Key mechanics with brief spec.
- System interactions.
- Player progression outline.
- Content scope estimate.
- Open design questions.

Gate condition: human approves the design package.

### 05 Prototype Planning (optional)

Primary: engineering-lead. Consulted: game-designer, producer, creative-product-lead.

Skip condition: no UI/UX uncertainty, no architectural uncertainty, and all critical risks
have accepted mitigations. Skip reason must be logged in `00-current-state.md`.

Goal: identify what to prototype to reduce the highest-risk unknowns before full production.

Output: `05-prototype-plan.md`

Required contents:
- Prototype goal (what question it answers).
- Risk-first ordering — hardest thing first.
- Timebox and acceptance criteria for each prototype.
- What success looks like.

Gate condition: human approves the prototype plan.

### 06 Production Planning

Primary: producer. Consulted: all roles.

Goal: convert the approved concept into a sequenced, dependency-explicit implementation plan.

Output: `06-production-plan.md`

Required contents:
- Milestones with definitions of done.
- Slice backlog ordered by dependency.
- Explicit dependency map.
- Risk register updated.

Gate condition: human approves the production plan.

### 07 Change Control (standing)

Primary: producer. Consulted: auto-selected by impact area.

Available at any phase. Every change that affects approved artefacts, scope, pillars, or
implementation briefs must go through here.

Output: append a `CHG-XXX` entry to `07-change-decisions.md`.

Use: `python3 .agents/skills/game-studio/scripts/game-studio ... change request --title "..." --description "..."`

Required contents per entry:
- Requested change.
- Impacted artefacts.
- Role assessments.
- Recommendation.
- Decision (to be filled by human).

### 08 Implementation Support

Primary: engineering-lead. Consulted: varies by slice.

Goal: bounded implementation of one approved slice at a time.

Gate: an approved `IMP-XXX` brief must exist before any code is written.

Create a brief: `python3 .agents/skills/game-studio/scripts/game-studio ... brief create --slice-name "..."`

Required brief contents:
- Slice goal.
- Upstream artefact references.
- Functional and non-functional requirements.
- Constraints and out-of-scope list.
- Test strategy (unit, integration, manual, regression).
- Acceptance criteria.

Execution loop:
1. Plan.
2. Propose.
3. Execute.
4. Report.
5. Complete post-execution review section in the brief.
6. Await human approval before next slice.

## Artefact frontmatter standard

```yaml
---
title: <document title>
status: draft | approved | approved-with-conditions | rework-required | rejected | parked
owner_role: <primary role>
contributors:
  - <role>
inputs:
  - <artefact path>
open_questions:
  - <question>
approved_by: <human or empty>
updated_at: <YYYY-MM-DD>
---
```

## `00-current-state.md` contract

Must always answer:

1. Current phase.
2. Latest approved artefacts with statuses.
3. Blocking questions.
4. Accepted risks (IDs only — detail lives in `00-risk-register.md`).
5. Next decision required from the human.
6. Recommended next step.

Update this file after every meaningful action.

## `00-risk-register.md` contract

Every open question that cannot block a phase must be recorded as an accepted risk.

Required fields per entry: Risk ID, description, category, phase introduced, status,
severity, confidence, mitigation, owner role, blocks-progression flag.

## Escalation rules

Pause immediately when:

1. An action conflicts with approved vision or pillars.
2. A foundational technical choice requires human commitment.
3. A role raises a critical-severity risk with no mitigation.
4. A required input artefact is missing.
5. An implementation request exceeds the approved slice scope.

Pause output must include:
1. Clear issue description.
2. Why this blocks progress.
3. Recommended resolution.
4. Alternatives with consequences.
5. The exact decision needed from the human.

Do not proceed until the human resolves the conflict.
