---
title: LLM Agent Game Studio Implementation Spec
status: approved
owner_role: human
contributors:
  - Studio Orchestrator
updated_at: 2026-05-15
---

# LLM Agent Game Studio Implementation Spec

## Purpose

Define the execution-ready specification for a workflow-centric, role-evaluated indie game studio assistant.

Machine-facing implementation details for the skill plus CLI build are further specified in `phase-0-implementation-addendum.md`. If this document conflicts with that addendum on runtime behavior, CLI contract, serialized status values, or project layout rules, the addendum wins.

This system must:

1. Help one active game project at a time move from idea to execution-ready slices.
2. Preserve human control over vision, approvals, and major trade-offs.
3. Use a single orchestrator as the control plane.
4. Use specialist role contracts as reusable skills, not always-on peer agents.
5. Persist canonical state and artefacts in the project repository as numbered Markdown files.

## Product Definition

The product is a `Studio Orchestrator` that:

1. Guides the user through a fixed, phase-gated workflow.
2. Invokes specialist roles when needed.
3. Produces and maintains numbered project artefacts.
4. Enforces approval gates.
5. Supports bounded implementation work only after an approved implementation brief exists.

## Non-Goals

V1 must not:

1. Behave like a fully autonomous game studio.
2. Use peer-to-peer role chatter as a first-class pattern.
3. Run long-lived autonomous background workflows.
4. Generate one giant master design document.
5. Continue beyond the approved active implementation slice.
6. Treat LLM output as truth when prototypes, tests, or human judgment can validate it.

## Core Architecture

### Control Plane

`Studio Orchestrator`

Responsibilities:

1. Track current phase and workflow state.
2. Determine the primary, consulted, and review roles for the active step.
3. Load relevant approved artefacts.
4. Collect role outputs using step-specific templates.
5. Enforce approval gates and pause conditions.
6. Merge approved content into canonical artefacts.
7. Maintain `00-current-state.md` and `00-risk-register.md`.

Non-responsibilities:

1. Does not own creative authorship.
2. Does not silently change approved vision or scope.
3. Does not behave as a substitute domain specialist.

### Specialist Roles

1. `Creative/Product Lead`
2. `Producer`
3. `Game Designer`
4. `Engineering Lead`
5. `Art Director`

### Canonical Memory

All canonical project state lives in the repository as Markdown artefacts.

Rules:

1. Approved artefacts are canonical memory.
2. Draft deep-dive notes are non-canonical until promoted by the orchestrator.
3. Open questions must either block progression or become accepted risks.
4. Accepted risks persist in `00-risk-register.md`.

## Interaction Model

### Primary Interface

The user interacts primarily with the `Studio Orchestrator`.

### Deep-Dive Interface

The user may temporarily deep-dive into a specialist role.

Deep-dive rules:

1. The specialist loads relevant approved artefacts.
2. The specialist answers from its role contract only.
3. The specialist may create a draft note.
4. The specialist may not promote drafts into canonical numbered artefacts.
5. Control returns to the orchestrator after the deep-dive.

### Operating Modes

1. `Collaborative Mode`
Purpose: discussion, critique, refinement, trade-off analysis.

2. `Execution Mode`
Purpose: bounded implementation work on an approved slice.

Default execution loop:

1. plan
2. propose
3. execute
4. report
5. await approval for next slice

## Workflow

### Phase Order

1. `01 Idea Intake`
2. `02 Vision Definition`
3. `03 Concept Stress Test`
4. `04 Pre-Production Design`
5. `05 Prototype Planning` when required
6. `06 Production Planning`
7. `07 Change Control` standing workflow
8. `08 Implementation Support`

### Required Gates

Approval is required at minimum for:

1. Vision approval.
2. Prototype plan approval when required.
3. Production plan approval.
4. Major scope changes.
5. Each implementation brief before execution.
6. Foundational technical choices.

### Phase Outcomes

Allowed outcomes:

1. `approved`
2. `approved-with-conditions`
3. `rework-required`
4. `rejected`
5. `parked`

`parked` means intentionally inactive and not allowed to advance.

## Repository Structure

The human provides the repository root and target documentation directory at startup.

For the skill source repository versus target workspace split, and for canonical generated project paths, follow `phase-0-implementation-addendum.md`.

Recommended structure:

Skill source repository:

```text
<skills-repo>/
  docs/
    game-studio/
      system-reminder.md
      implementation-plan.md
      phase-0-implementation-addendum.md
      roles/
        creative-product-lead.md
        producer.md
        game-designer.md
        engineering-lead.md
        art-director.md
        orchestrator.md
  .agents/
    skills/
      game-studio/
        SKILL.md
        references/
          roles.md
          workflow.md
          templates/
            00-current-state.md
            00-risk-register.md
            01-idea-brief.md
            02-vision-brief.md
            03-concept-stress-test.md
            04-design-package.md
            05-prototype-plan.md
            06-production-plan.md
            07-change-decisions.md
            08-implementation-brief.md
        scripts/
          game-studio
          game_studio/
            src/
            tests/
```

Target workspace:

```text
<target-repo>/<target-docs-dir>/game-studio/projects/<project-slug>/
  00-current-state.md
  00-risk-register.md
  01-idea-brief.md
  02-vision-brief.md
  03-concept-stress-test.md
  04-design-package.md
  05-prototype-plan.md
  06-production-plan.md
  07-change-decisions.md
  08-implementation-briefs/
    IMP-001-<slice>.md
```

Conventions:

1. One project folder per game.
2. Role contracts and templates are global and reusable inputs.
3. Numbered artefacts represent workflow order, not role ownership.
4. Generated project artefacts live in the target workspace, not the skill source repository.
5. Revisions happen in place.
6. `draft` and `approved` are document states, not separate files.

## Canonical State Files

### `00-current-state.md`

Must always answer:

1. Current phase.
2. Latest approved artefacts.
3. Blocking questions.
4. Accepted risks.
5. Next decision required from the user.
6. Recommended next workflow step.

### `00-risk-register.md`

Must track:

1. Risk ID.
2. Description.
3. Category.
4. Phase introduced.
5. Status.
6. Severity.
7. Confidence.
8. Mitigation.
9. Owner role.
10. Whether it blocks progression.

## Artefact Frontmatter Standard

Every canonical artefact must include at least:

```yaml
---
title: <document title>
status: draft | approved | approved-with-conditions | rework-required | rejected | parked
owner_role: <primary role>
contributors:
  - <role>
inputs:
  - <artefact path or source>
open_questions:
  - <question>
approved_by: <human or empty>
updated_at: <YYYY-MM-DD>
---
```

## Artefact Content Template

Each substantive artefact should contain these sections where applicable:

1. Purpose
2. Decision Summary
3. Assumptions
4. Inputs
5. Primary Recommendation
6. Alternatives
7. Trade-offs
8. Impact
9. Confidence
10. Role Contributions
11. Open Questions
12. Risks
13. Acceptance Criteria
14. Approval Status
15. Next Actions

### Recommendation Format

Every major recommendation must include:

1. `recommendation`
2. `reasoning`
3. `trade-offs`
4. `impact`
5. `confidence`
6. `next action`
7. `alternatives` with at least one and at most two serious alternatives

Confidence values:

1. `high`
2. `medium`
3. `low`

## Role Contracts

Each role contract must define:

1. `mission`
2. `owns`
3. `must_not_decide`
4. `required_inputs`
5. `output_template`
6. `review_criteria`
7. `escalation_conditions`

### 1. Creative/Product Lead

Mission:

Protect the game's vision, audience fit, differentiation, and core trade-offs.

Owns:

1. Vision.
2. Target audience.
3. Creative pillars.
4. Differentiation.
5. Major feature trade-offs.
6. Non-goals.

Must not decide:

1. Milestone sequencing.
2. Task scheduling.
3. Technical architecture without engineering input.

Required inputs:

1. Idea brief.
2. Vision-related approved artefacts.
3. Comparable references.
4. Constraints and goals.

Output template:

1. One-sentence verdict.
2. Vision and pillar alignment.
3. Player and product impact.
4. Trade-offs.
5. Recommended path.
6. Alternatives.
7. Open questions.

Review criteria:

1. Does it strengthen the game's identity?
2. Does it serve the target player?
3. Does it preserve the irreducible core?

Escalation conditions:

1. Pillar conflict.
2. Audience drift.
3. Major scope cut affecting core promise.

### 2. Producer

Mission:

Protect delivery clarity, scope discipline, sequencing, and change impact visibility.

Owns:

1. Scope control.
2. Milestone framing.
3. Dependency mapping.
4. Sequencing recommendations.
5. Change impact analysis.
6. Process risk surfacing.

Must not decide:

1. Vision.
2. Creative identity.
3. Product authorship.

Required inputs:

1. Approved design and vision artefacts.
2. Risk register.
3. Technical and art constraints.

Output template:

1. Scope summary.
2. Dependency map.
3. Delivery risks.
4. Recommended sequencing.
5. Alternatives.
6. Consequences of each.

Review criteria:

1. Is scope coherent and bounded?
2. Are dependencies explicit?
3. Are lock points clear?

Escalation conditions:

1. Unbounded scope.
2. Hidden dependencies.
3. Major slip or plan invalidation.

### 3. Game Designer

Mission:

Turn vision into a compelling, coherent, testable player experience.

Owns:

1. Core loop.
2. Mechanics.
3. Systems.
4. Progression.
5. Onboarding.
6. Pacing.
7. Playtest interpretation.

Must not decide:

1. Business or product direction alone.
2. Architecture alone.

Required inputs:

1. Approved vision brief.
2. Comparable references.
3. Constraints.
4. Prototype findings when available.

Output template:

1. Core loop summary.
2. Player experience goals.
3. Mechanics and systems summary.
4. Risks and dominant strategy concerns.
5. Prototype or playtest recommendations.
6. Alternatives.

Review criteria:

1. Is the loop clear and compelling?
2. Does the design support the pillars?
3. Are onboarding and pacing addressed?

Escalation conditions:

1. Weak or contradictory core loop.
2. Unsupported fantasy.
3. Unvalidated design risk.

### 4. Engineering Lead

Mission:

Protect feasibility, architecture quality, tooling leverage, testability, and technical risk visibility.

Owns:

1. Feasibility analysis.
2. Architecture recommendations.
3. Tooling recommendations.
4. Implementation strategy.
5. Test strategy.
6. Verification checklist.
7. Technical risk reporting.

Must not decide:

1. Product direction.
2. Final scope and creative trade-offs.

Required inputs:

1. Approved design artefacts.
2. Functional requirements.
3. Non-functional requirements.
4. Constraints.
5. Existing codebase context when relevant.

Output template:

1. Feasibility status: `green`, `amber`, or `red`.
2. Key technical issues.
3. Proposed solutions.
4. Alternatives.
5. Test strategy.
6. Verification checklist.

Review criteria:

1. Is the proposal feasible under stated constraints?
2. Are requirements and trade-offs explicit?
3. Is testability included?

Escalation conditions:

1. Red feasibility status.
2. Foundational architecture choice required.
3. Vision conflict caused by implementation constraints.

### 5. Art Director

Mission:

Protect visual identity, readability, style coherence, and art-production realism.

Owns:

1. Visual direction.
2. Readability.
3. Style rules.
4. Reference selection.
5. Art burden visibility.

May produce:

1. Supportive sample art.
2. Moodboards.
3. Prompt packs.
4. Style probes.
5. Composition notes.

Must not decide:

1. Product direction.
2. Technical architecture.
3. Delivery schedule.

Required inputs:

1. Vision artefacts.
2. Design package.
3. Constraints.
4. Target platform and camera context.

Output template:

1. Visual direction summary.
2. Readability rules.
3. Style references.
4. Production constraints.
5. Supportive art suggestions.
6. Alternatives.

Review criteria:

1. Is the style coherent and readable?
2. Can it scale to the intended content volume?
3. Does it support gameplay clarity?

Escalation conditions:

1. Style drift.
2. Readability risk.
3. Art burden incompatible with scope.

## Workflow Phase Specs

### 01 Idea Intake

Primary role: `Creative/Product Lead`

Consulted roles:

1. `Producer` when constraints are already visible.

Outputs:

1. `01-idea-brief.md`

Required contents:

1. Logline.
2. Genre and platform assumptions.
3. Target player hypothesis.
4. Core fantasy.
5. Initial references.
6. Known constraints.
7. Unknowns.

Acceptance criteria:

1. The idea can be explained in one paragraph.
2. The target player is named.
3. Major unknowns are explicit.

### 02 Vision Definition

Primary role: `Creative/Product Lead`

Consulted roles:

1. `Game Designer`
2. `Producer`

Outputs:

1. `02-vision-brief.md`

Required contents:

1. Vision paragraph.
2. Three to five pillars.
3. Non-goals.
4. Target audience.
5. Success criteria.
6. Core trade-off priorities.

Acceptance criteria:

1. Pillars are explicit and non-generic.
2. Non-goals exist.
3. Human approval is recorded.

### 03 Concept Stress Test

Primary role: `Producer`

Consulted roles:

1. `Creative/Product Lead`
2. `Game Designer`
3. `Engineering Lead`
4. `Art Director`

Outputs:

1. `03-concept-stress-test.md`

Required contents:

1. Core strengths.
2. Fatal risks.
3. Scope risks.
4. Technical risks.
5. Art burden risks.
6. Differentiation check.
7. Kill criteria.
8. Recommendation and alternatives.

Acceptance criteria:

1. Major risks are explicit.
2. A clear verdict exists.
3. The user can approve progression, request rework, reject, or park.

### 04 Pre-Production Design

Primary role: `Game Designer`

Consulted roles:

1. `Creative/Product Lead`
2. `Engineering Lead`
3. `Art Director`
4. `Producer`

Outputs:

1. `04-design-package.md`

Required contents:

1. Core loop.
2. Mechanics and systems outline.
3. Progression outline.
4. Onboarding outline.
5. Pacing outline.
6. Technical assumptions.
7. Art direction summary.

Acceptance criteria:

1. The loop is explicit.
2. Major systems are named.
3. Remaining risks are visible.
4. The package is compact and decision-grade.

### 05 Prototype Planning

Primary role: `Engineering Lead`

Consulted roles:

1. `Game Designer`
2. `Producer`
3. `Creative/Product Lead`

Outputs:

1. `05-prototype-plan.md`

Required contents:

1. Risks to validate.
2. Smallest meaningful prototypes.
3. Pass/fail criteria.
4. Dependencies.
5. Test strategy.
6. Recommendation and alternatives.

Acceptance criteria:

1. Every prototype maps to a specific risk.
2. Pass/fail conditions are explicit.
3. Human approval is recorded.

### 06 Production Planning

Primary role: `Producer`

Consulted roles:

1. `Engineering Lead`
2. `Game Designer`
3. `Creative/Product Lead`
4. `Art Director`

Outputs:

1. `06-production-plan.md`

Required contents:

1. Milestones.
2. Ordered slices.
3. Dependencies.
4. Definitions of done.
5. Major risks.
6. Recommended sequence.

Acceptance criteria:

1. Dependencies are explicit.
2. Slices are independently understandable.
3. The plan only starts after stress test or prototype gate conditions are satisfied.

### 07 Change Control

Primary role: `Producer`

Automatically consulted based on impact:

1. `Creative/Product Lead` for pillar, audience, differentiation, or major scope effects.
2. `Engineering Lead` for feasibility, architecture, performance, testing, or tooling effects.
3. `Art Director` for visual identity, readability, and content burden effects.
4. `Game Designer` for loop, system, pacing, and onboarding effects.

Outputs:

1. `07-change-decisions.md`

Required contents:

1. Requested change.
2. Impacted artefacts.
3. Recommendation.
4. Alternatives.
5. Trade-offs.
6. Approval status.

Acceptance criteria:

1. Change impact is explicit.
2. Required human decision is explicit.
3. Updated risks are captured.

### 08 Implementation Support

Primary role: `Engineering Lead`

Consulted roles vary by slice.

Outputs:

1. `08-implementation-briefs/IMP-xxx-*.md`

Required contents:

1. Slice goal.
2. Inputs and linked approved artefacts.
3. Acceptance criteria.
4. Expected tests.
5. Functional requirements.
6. Non-functional requirements.
7. Constraints.
8. Risks.
9. Recommendation and alternatives.

Acceptance criteria:

1. The slice is bounded.
2. It references approved upstream artefacts.
3. Testing expectations are explicit.
4. Human approval is recorded before execution.

## Routing Rules

The orchestrator routes primarily from active workflow step.

### Role Assignment Model

For each step define:

1. One `primary` role.
2. Zero or more `consulted` roles.
3. Zero or more `review` roles.

Default routing behavior:

1. Primary role drafts first.
2. Consulted and review roles react to the draft.
3. Orchestrator synthesizes into a final recommendation.

Parallel review is reserved for:

1. High-risk decisions.
2. Significant role disagreement.
3. High-uncertainty branches.

### Automatic Invocation Rules

Invoke `Creative/Product Lead` when the decision affects:

1. Pillars.
2. Audience.
3. Differentiation.
4. Major scope cuts.

Invoke `Producer` when the decision affects:

1. Sequencing.
2. Dependencies.
3. Effort.
4. Milestone shape.
5. Change impact.

Invoke `Engineering Lead` when the decision affects:

1. Feasibility.
2. Architecture.
3. Tooling.
4. Testing.
5. Performance.
6. Engine choice.
7. Technical risk.

Invoke `Art Director` when the decision affects:

1. Visual identity.
2. Readability.
3. Content burden.
4. Style consistency.

If a role is skipped in a low-risk case, the orchestrator must log the reason in the artefact.

## Pause and Escalation Rules

The orchestrator must pause when:

1. An action conflicts with approved vision or pillars.
2. A foundational technical choice requires commitment.
3. A role raises a blocking red-risk issue.
4. A required input artefact is missing.
5. An implementation request exceeds the approved slice.

Pause output must include:

1. Clear issue description.
2. Why this blocks progress.
3. Recommended resolution.
4. One or two alternatives.
5. Consequences of each alternative.
6. Exact decision needed from the user.

## Implementation Rules

### Preconditions for Code Writing

Code may only be written when:

1. An approved implementation brief exists.
2. Acceptance criteria are explicit.
3. Expected tests are explicit.
4. Relevant upstream artefacts are approved.

### Allowed Implementation Outputs

1. Code.
2. Tests.
3. Technical specs.
4. Engine setup plans.
5. Scene/system breakdowns.
6. Content schemas.
7. Tuning specs and tables.
8. UI flow definitions.

### Code Completion Standard

Generated code remains provisional until:

1. It matches the approved implementation brief.
2. Relevant tests pass.
3. Trade-offs are summarized.
4. Follow-up risks are recorded.

### Post-Execution Review Template

Every execution slice must end with:

1. What changed.
2. What passed.
3. What failed.
4. Remaining risks.
5. Whether the next slice is still valid.

## Evaluation and Review

### Default Review Rubric

Every major artefact should be evaluated against:

1. Vision alignment.
2. Player value.
3. Scope realism.
4. Technical feasibility.
5. Production clarity.
6. Unresolved risk quality.

### Acceptance Criteria Requirement

Every major artefact must include explicit acceptance criteria so the orchestrator can determine whether the phase is complete.

### Revision Tracking

Every revised artefact should record:

1. What changed.
2. Why it changed.
3. Which risks or questions it resolved.

## Minimum Deliverables to Build First

The initial implementation of the studio should produce these reusable assets first:

1. `roles/orchestrator.md`
2. `roles/creative-product-lead.md`
3. `roles/producer.md`
4. `roles/game-designer.md`
5. `roles/engineering-lead.md`
6. `roles/art-director.md`
7. Template for `00-current-state.md`
8. Template for `00-risk-register.md`
9. Templates for `01` through `08` artefacts
10. Routing matrix by workflow step
11. Pause and escalation policy
12. Execution brief and post-execution review templates

## Acceptance Criteria for the Studio Itself

The studio implementation is acceptable when it can:

1. Create a new project folder in a human-provided target documentation directory.
2. Maintain canonical state in numbered Markdown artefacts.
3. Correctly identify the active workflow phase.
4. Route to the correct primary and consulted roles for each phase.
5. Enforce approval gates without silent advancement.
6. Produce compact decision-grade pre-production artefacts.
7. Track risks and open questions across phases.
8. Create approved implementation briefs with explicit test expectations.
9. Pause cleanly on conflicts with approved vision, pillars, or constraints.
10. Keep the user in control while still being opinionated and useful.

## Recommended Build Order

1. Build orchestrator contract and state model.
2. Build artefact templates and numbering conventions.
3. Build role contracts.
4. Build routing matrix.
5. Build gate and pause logic.
6. Build implementation brief and execution review templates.
7. Pilot on one real project.

## Final Rule

When uncertain, prefer:

1. simpler workflow over richer orchestration
2. clearer artefacts over clever prompts
3. explicit pause over silent progress
4. bounded execution over autonomous chaining
5. human vision preservation over local agent optimization
