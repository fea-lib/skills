---
generated: 2026-03-05
status: decided
based_on: 1-research.md
---

# Design: Agentic Development Workflow Skill Library

This document records the design decisions made following the research phase
([`1-research.md`](1-research.md)). It is the authoritative reference for the
implementation phase.

## Table of Contents

1. [Goals](#1-goals)
2. [Skill Library Structure](#2-skill-library-structure)
3. [Phase Map](#3-phase-map)
4. [Key Design Decisions](#4-key-design-decisions)
5. [Skill Collision Prevention](#5-skill-collision-prevention)
6. [Artifact Contracts](#6-artifact-contracts)
7. [Testing Strategy](#7-testing-strategy)

---

## 1. Goals

- Produce a shareable, tool-agnostic agentic development workflow usable by small
  teams (2–10 people) with minimal setup friction.
- Encode the workflow as a library of composable agent skills following the
  `SKILL.md` + directory format established in this repository.
- Design philosophy: **lightweight + iterative** — enforce only the highest-leverage
  mandatory gates; keep optional phases optional; avoid governance overhead suited
  to enterprise contexts.

---

## 2. Skill Library Structure

```
.agents/skills/
├── agentic-dev-workflow/     # Orchestrator — the only loosely triggered skill
│   └── SKILL.md
├── adw-idea/                 # Phase 1
├── adw-research/             # Phase 2
├── adw-prototype/            # Phase 3 (optional)
├── adw-prd/                  # Phase 4
├── adw-plan/                 # Phase 5
├── adw-refine/               # Phase 6
├── adw-execution/            # Phase 7
└── adw-qa/                   # Phase 8
```

**9 skills total:** 8 phase skills + 1 orchestrator.

### Naming rationale

- `agentic-dev-workflow` — the orchestrator uses a full descriptive name; it is the
  single entry point a human would discover and trigger.
- `adw-*` prefix — all phase skills share a namespace prefix. This:
  - Prevents name collisions with third-party skills (e.g. a generic `research`
    skill in another library won't conflict with `adw-research`)
  - Signals to agents that these are sub-components of a system, not standalone tools
  - Makes the library self-documenting in any skill registry listing

---

## 3. Phase Map

| # | Skill | Phase | Status | Skip condition |
|---|---|---|---|---|
| 1 | `adw-idea` | Idea | **Mandatory** | — |
| 2 | `adw-research` | Codebase Research | **Mandatory** | — |
| 3 | `adw-prototype` | Prototype | Optional | No UI/UX work and no architectural uncertainty |
| 4 | `adw-prd` | PRD | **Mandatory** | — |
| 5 | `adw-plan` | Implementation Plan | **Mandatory** | — |
| 6 | `adw-refine` | Ticket Refinement | **Mandatory** | — |
| 7 | `adw-execution` | Execution Loop | **Mandatory** | — |
| 8 | `adw-qa` | QA Plan | **Mandatory** | — |

### Mandatory vs. optional rationale

The research identifies the two most commonly skipped and highest-impact phases as
codebase research (Phase 2) and QA (Phase 8) — both are mandatory here [1-research.md §3.1,
§8 point 3]. All other phases are mandatory because they form the minimum viable
pipeline for agent-safe execution. The prototype phase is the sole exception: most
day-to-day tasks have no UI/UX or architectural uncertainty component, making it the
exception rather than the rule.

### Phase flexibility

`adw-idea` produces a **phase plan artifact** as its primary output. This artifact
lists which phases will run for the specific task, with optional phases either included
(with rationale) or skipped (with a documented reason). The orchestrator follows the
phase plan — not a hardcoded sequence.

**Skip rule:** A skip reason must be documented in the phase plan. Silent skips are not
permitted. Per-phase human confirmation of every skip is not required — one decision,
one place, at the start of the workflow.

---

## 4. Key Design Decisions

### 4.1 Separate skills over a single monolithic skill

9 separate skills, not one skill with phase docs in `references/`.

- Progressive disclosure: only the active phase's skill loads into the context window.
  A monolithic skill would load all phase instructions regardless of which phase is
  running — wasted tokens.
- Independent reuse: individual phase skills can be invoked outside the full ADLC
  if useful (e.g. `adw-research` standalone for a codebase exploration task).
- Independent versioning: phase instructions can evolve without touching unrelated phases.
- Consistent with the research finding: "avoid monolithic kitchen-sink agents" applies
  to skills as much as to agents [1-research.md §3.2].

Shared artifact names and formats are defined once in the orchestrator's `references/`
directory and referenced by each phase skill to prevent consistency drift.

### 4.2 Orchestrator is the only loosely triggered skill

Only `agentic-dev-workflow` is triggered by natural human language. All `adw-*` phase
skills require the orchestrator to be active. Loose triggering on 8 skills creates a
high collision surface with other installed skills; gating phase skills behind an
orchestrator prerequisite makes them effectively unreachable without an active workflow
session.

### 4.3 adw-research is distinct from the general research skill

The repository already contains a general-purpose `research` skill. The two are
complementary, not conflicting:

| Dimension | `research` skill | `adw-research` phase skill |
|---|---|---|
| Trigger | Human request matching research phrases | Orchestrator instruction only |
| Scope | Any topic, any source type | Codebase and task context only — no external sources |
| Output | Standalone research report (file) | `research.md` handoff artifact for downstream phases |
| Audience | Human reader | Downstream agents (PRD, Plan, Execution) |
| Interaction | High — intake questions, approvals | Minimal — executes and produces artifact |

### 4.4 Ticket refinement is a dedicated phase

Ticket refinement is Phase 6 (`adw-refine`), a mandatory gate between Plan and
Execution. The research identifies mid-execution agent failures as most commonly
caused by ambiguous, underspecified, or dependency-hidden tickets [1-research.md §3.3].
Conflating refinement with decomposition (Phase 5) risks rushing it; a dedicated phase
makes the human sign-off gate explicit and non-skippable.

`adw-refine` covers:
- Gap discovery — what is missing or ambiguous in each ticket
- Acceptance criteria validation — every ticket must have a testable definition of done
- Dependency resolution — hidden blocking relationships surfaced and made explicit
- Human sign-off gate — mandatory human checkpoint before the execution loop starts

### 4.5 Execution loop control flow: hybrid

`adw-execution` uses static steps for the core loop with dynamic escalation paths.
The research documents a genuine conflict between deterministic and dynamic
orchestration [1-research.md §6, Conflict 1]. Static steps reduce ambiguity and
support auditability; dynamic escalation paths (CRP for blockers, MRP for completion)
handle cases where the agent cannot proceed without human input. This matches the
production pattern across most successful deployments.

### 4.6 Tool-agnostic

No tool-specific syntax. Skills work across Claude Code, Cursor, GitHub Copilot, and
any other agent that supports the `SKILL.md` format.

### 4.7 Observability out of scope for v1

The workflow is self-contained; teams can layer in tracing (Langfuse, Helicone, etc.)
independently without changes to the skill definitions. Revisit after the workflow has
been used on real tasks and specific observability gaps are identified.

---

## 5. Skill Collision Prevention

Three complementary mechanisms:

**1. Namespaced prefix**
All phase skills are prefixed `adw-`. The namespace is specific enough to avoid
accidental collision with common skill names in third-party libraries.

**2. Prerequisite gating in descriptions**
Every `adw-*` skill description states that it is triggered only when the
`agentic-dev-workflow` orchestrator is active and has explicitly entered the
corresponding phase. Example template:

> "Use only when the `agentic-dev-workflow` orchestrator skill is active and has
> explicitly entered Phase N — [Phase Name]."

**3. Narrow, workflow-specific trigger language**
Phase skill descriptions avoid generic verbs. They reference orchestrator state
explicitly, making accidental triggering from unrelated tasks effectively impossible.

---

## 6. Artifact Contracts

Phase artifacts are stored in a `.adw/` directory at the repo root, grouped by task:

```
.adw/
└── <task-slug>/
    ├── 0-state.md          ← always present; tracks current phase and completion status
    ├── 1-phase-plan.md
    ├── 2-research.md
    ├── 4-prd.md
    ├── 5-plan.md
    ├── 7-mrp.md  (or 7-crp.md)
    └── 8-qa-plan.md
```

Phase 3 (Prototype) produces no persisted artifact; its number is reserved in the
sequence so the file ordering always matches the phase map.

The task slug is a short kebab-case label derived from the task title in `adw-idea`
(e.g. `add-user-auth`, `fix-login-redirect`). It is generated once at Phase 1 and
used as the directory name for all subsequent phase artifacts in that task. Per-task
subdirectories allow multiple workflow instances to run in parallel without collision.

Teams may add `.adw/` to `.gitignore` or commit it for a full audit trail — the
workflow does not mandate either.

Artifact names and formats are defined in the orchestrator's `references/` directory.

| Phase | Produces | Consumed by |
|---|---|---|
| `adw-idea` | `1-phase-plan.md` — task scope + phase list with skip reasons | Orchestrator, all phases |
| `adw-research` | `2-research.md` — codebase findings, relevant patterns, constraints | `adw-prd`, `adw-plan`, `adw-execution` |
| `adw-prototype` | Throwaway spike (not persisted as a formal artifact) | `adw-prd` |
| `adw-prd` | `4-prd.md` — goal, end-state, acceptance logic, out-of-scope | `adw-plan` |
| `adw-plan` | `5-plan.md` — ticket list with blocking relationships | `adw-refine` |
| `adw-refine` | `5-plan.md` (updated) — refined tickets with acceptance criteria, resolved deps | `adw-execution` |
| `adw-execution` | `7-mrp.md` or `7-crp.md` — merge-readiness pack or consultation request | `adw-qa`, human reviewer |
| `adw-qa` | `8-qa-plan.md` — human-in-the-loop verification checklist | Human reviewer |

### Interruption and resume

The workflow can be stopped and resumed at any point. `0-state.md` is the single
source of truth for workflow state. The orchestrator writes it at the start and end
of every phase; on resume, it reads `0-state.md` first to determine where to continue.

**`0-state.md` format:**

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
<any context the agent should know when resuming, e.g. decisions made, blockers hit>
```

**Mid-phase interruption:** If the current phase artifact is incomplete when the
workflow is resumed, the phase restarts from scratch. Partial artifacts are
overwritten. This is safe because phases are designed to be short and idempotent —
re-running a phase against the same inputs produces the same output.

### MRP and CRP formats

Both are lightweight markdown checklists. The full SASE spec [1-research.md §3.3, S1]
is designed for compliance-critical enterprise environments; for a small team,
structured YAML with formal fields adds overhead without proportional benefit.

**`7-mrp.md` — Merge-Readiness Pack** (produced when execution completes successfully):

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

**`7-crp.md` — Consultation Request Pack** (produced when execution is blocked):

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

---

## 7. Testing Strategy

> **Status: Out of scope for v1.**
>
> The testing plan below is fully designed and ready to implement. It is deferred because
> Promptfoo requires a direct LLM API key (Anthropic or OpenAI) and no key is available
> in the current environment. The GitHub Copilot OAuth token managed by OpenCode cannot
> be used directly with Promptfoo without a local proxy. Tests will be added in a
> follow-up once a direct API key is available.

Skills are configuration artifacts — they cannot be unit-tested in isolation. What is
tested is the *effect*: load the skill as the agent's system prompt, run representative
inputs, and evaluate the outputs.

```
SKILL.md → agent context → outputs → evaluated
```

### 7.1 Scope

Six of the nine skills are in scope for automated testing. Three are explicitly excluded:

| Skill | Testable | Reason if excluded |
|---|---|---|
| `adw-idea` | Yes | — |
| `adw-research` | Yes | — |
| `adw-prototype` | **No** | Produces no persisted artifact |
| `adw-prd` | Yes | — |
| `adw-plan` | Yes | — |
| `adw-refine` | Yes | — |
| `adw-execution` | **No** | Operates on a real codebase; meaningful tests require a controlled codebase fixture — too expensive for v1 |
| `adw-qa` | Yes | — |
| `agentic-dev-workflow` | **No** | Full orchestration loop spans 8 phases; integration test cost is disproportionate for v1 |

### 7.2 Tooling

**Promptfoo** is the primary test runner. It is declarative (YAML, no code), tool-agnostic,
runs locally and in CI, and supports both deterministic assertions and LLM-as-judge scoring.
Each testable skill will include a `tests/promptfooconfig.yaml` bundled in its skill directory.

**Prerequisites:**
- Node.js ≥ 18
- `npx promptfoo@latest` (no permanent install required)
- A direct LLM API key: `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`

Note: GitHub Copilot's OAuth token (as managed by OpenCode) cannot be used directly —
it requires a token exchange step that is not supported natively by Promptfoo. A local
OpenAI-compatible proxy (e.g. `copilot-gpt4-service`) could bridge this gap but adds
operational overhead not warranted for v1.

### 7.3 Test structure per skill

Each skill's test suite uses two assertion layers:

**Layer 1 — Deterministic** (cheap, runs first): structural checks that the output artifact
meets its format contract — required sections present, slug format valid, no forbidden
patterns. These catch obvious regressions without any LLM API cost.

**Layer 2 — LLM-as-judge** (`llm-rubric` assertions): quality checks that require
semantic evaluation — acceptance criteria are testable, dependency relationships are
explicit, skip reasons are substantive rather than empty.

Test cases use synthetic but realistic inputs: pre-written fixture versions of upstream
artifacts (e.g. a fake `2-research.md` as input to `adw-prd`). This isolates each skill
from real codebase dependencies and keeps tests fast and repeatable.

Example config shape:

```yaml
# .agents/skills/adw-prd/tests/promptfooconfig.yaml
prompts:
  - file://../SKILL.md

providers:
  - anthropic:messages:claude-sonnet-4-20250514

tests:
  - description: "Produces all required sections"
    vars:
      input: |
        [fixture content of 2-research.md]
    assert:
      - type: contains
        value: "## Goal"
      - type: contains
        value: "## Acceptance Criteria"
      - type: contains
        value: "## Out of Scope"
      - type: llm-rubric
        value: "Acceptance criteria are specific and testable, not vague"
        threshold: 0.7
```

Run a skill's tests:
```bash
npx promptfoo@latest eval --config .agents/skills/adw-prd/tests/promptfooconfig.yaml
```

### 7.4 CI integration

Tests run on every PR that modifies a skill file via the `promptfoo/promptfoo-action@v2`
GitHub Action. Promptfoo's built-in caching prevents redundant LLM calls when inputs
haven't changed. LLM-as-judge pass threshold: **0.7** (calibrate against human judgements
before treating as a hard gate).

```yaml
- name: Run skill evals
  uses: promptfoo/promptfoo-action@v2
  with:
    config: .agents/skills/adw-prd/tests/promptfooconfig.yaml
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### 7.5 What automated tests cannot verify

- Whether the agent made the *right* execution or escalation decision (requires a real task)
- Whether a skill works correctly when multiple skills are loaded simultaneously
- End-to-end workflow correctness across all phases

These gaps are addressed by manual walkthrough on a real task before each major skill version release.

---

*Document generated: 2026-03-05*
