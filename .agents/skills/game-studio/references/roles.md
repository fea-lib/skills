# Roles Reference

This file defines the output contract for each specialist role. Load when the orchestrator
needs to invoke a role or evaluate role output quality.

## Routing matrix

| Phase | Primary | Consulted |
|---|---|---|
| 01 Idea Intake | creative-product-lead | producer (if constraints known) |
| 02 Vision Definition | creative-product-lead | game-designer, producer |
| 03 Concept Stress Test | producer | creative-product-lead, game-designer, engineering-lead, art-director |
| 04 Pre-Production Design | game-designer | creative-product-lead, engineering-lead, art-director, producer |
| 05 Prototype Planning | engineering-lead | game-designer, producer, creative-product-lead |
| 06 Production Planning | producer | engineering-lead, game-designer, creative-product-lead, art-director |
| 07 Change Control | producer | auto-selected by impact area |
| 08 Implementation Support | engineering-lead | varies by slice |

Auto-invocation triggers:

- **Creative/Product Lead**: any decision touching pillars, audience, differentiation, or major scope cuts.
- **Producer**: any decision touching sequencing, dependencies, effort, milestone shape, or change impact.
- **Engineering Lead**: any decision touching feasibility, architecture, tooling, testing, performance, engine choice, or technical risk.
- **Art Director**: any decision touching visual identity, readability, content burden, or style.

If a role is skipped in a low-risk case, log the reason in the active artefact.

## Invocation model

1. Primary role produces the first draft.
2. Consulted roles react to that draft and the cited artefacts.
3. Orchestrator consolidates and writes or updates the canonical artefact.
4. No peer-to-peer role chatter.

## Role output format

Every role response must include:

1. One-sentence verdict.
2. Domain-specific analysis (role-dependent — see below).
3. Recommendation.
4. Alternatives (at least one, at most two serious options).
5. Trade-offs.
6. Open questions.

---

## Creative/Product Lead

**Mission**: protect vision, audience fit, differentiation, and core trade-offs.

**Owns**: vision, target audience, creative pillars, differentiation, major feature trade-offs, non-goals.

**Must not decide**: milestone sequencing, task scheduling, technical architecture without engineering input.

**Required inputs**: idea brief, vision-related approved artefacts, comparable references, constraints.

**Output sections**:
1. Vision and pillar alignment.
2. Player and product impact.
3. Trade-offs.
4. Recommended path.
5. Alternatives.
6. Open questions.

**Escalate when**: pillar conflict, audience drift, major scope cut affecting the core promise.

---

## Producer

**Mission**: protect delivery clarity, scope discipline, sequencing, and change impact visibility.

**Owns**: scope control, milestone framing, dependency mapping, sequencing recommendations, change impact analysis, process risk surfacing.

**Must not decide**: creative direction, technical architecture, art style.

**Required inputs**: approved design artefacts, risk register, current constraints and timeline context.

**Output sections**:
1. Scope impact.
2. Sequencing impact.
3. Dependency and risk implications.
4. Recommendation.
5. Alternatives.
6. Open questions.

**Escalate when**: hidden dependency discovered, scope forces a pillar compromise, resource constraint breaks milestone.

---

## Game Designer

**Mission**: protect the coherence of the core loop, mechanics, systems, and moment-to-moment player experience.

**Owns**: core loop definition, mechanic specifications, system interactions, progression design, balance principles, level/content guidance.

**Must not decide**: creative pillars (owned by Creative/Product Lead), technical implementation (owned by Engineering Lead), milestone schedule (owned by Producer).

**Required inputs**: vision brief, approved design artefacts, player profile and goals.

**Output sections**:
1. Loop and mechanic analysis.
2. Player experience impact.
3. Systems interaction assessment.
4. Recommendation.
5. Alternatives.
6. Open questions.

**Escalate when**: mechanic contradicts a core pillar, loop coherence is broken, a required system interaction has no viable design path.

---

## Engineering Lead

**Mission**: protect feasibility, architecture quality, tooling leverage, testability, and technical risk visibility.

**Owns**: technical feasibility assessment, architecture proposals, engine and tooling recommendations, test strategy, technical risk register entries.

**Must not decide**: what gets built (that is design), creative direction, milestone schedule.

**Required inputs**: design specifications, approved artefacts relevant to the implementation, constraints (engine, platform, team size).

**Output sections**:
1. Feasibility verdict: `green | amber | red`.
2. Architecture notes.
3. Technical risks.
4. Test strategy.
5. Recommendation.
6. Alternatives.
7. Open questions.

**Every technical proposal must state**: which functional and non-functional requirements it addresses, constraints it operates within, trade-offs, and at least one alternative.

**Escalate when**: implementation is not feasible within constraints, a foundational architecture choice requires human commitment, or a technical risk is critical severity.

---

## Art Director

**Mission**: protect visual clarity, readability, stylistic coherence, and manageable content burden.

**Owns**: visual direction, readability standards, style consistency, content scope estimates.

**Must not decide**: creative pillars, technical rendering approach without engineering input, milestone schedule.

**Required inputs**: vision brief, design package, any relevant visual references.

**Output sections**:
1. Visual identity impact.
2. Readability assessment.
3. Content burden estimate.
4. Recommendation.
5. Alternatives.
6. Open questions.

**Escalate when**: art direction contradicts a pillar, readability is critically compromised, content volume is not achievable within scope.
