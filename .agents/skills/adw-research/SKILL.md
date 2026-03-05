---
name: adw-research
description: >
  Phase 2 of the agentic-dev-workflow: Codebase Research. Explores the repository to
  understand existing patterns, constraints, and risks relevant to the task. Produces
  2-research.md for downstream phases (PRD, Plan, Execution). Scope is codebase and
  task context only — no external sources. Use only when the agentic-dev-workflow
  orchestrator skill is active and has explicitly entered Phase 2 — Research.
---

# Phase 2 — Codebase Research

Produce `2-research.md`. This artifact is the shared knowledge base for PRD, Plan, and
Execution. Investing in it reduces ambiguity in every downstream phase.

Scope: **codebase and task context only**. Do not fetch external documentation or sources —
that is the role of the general `research` skill, which has different scope and audience.

## Steps

1. **Read `1-phase-plan.md`** to understand the task and its context links.

2. **Explore the codebase.** Focus on areas directly relevant to the task:
   - Locate files, modules, and functions that will be modified or touched by the change
   - Identify the patterns and conventions already in use (naming, file structure, error
     handling, testing approach)
   - Find any existing tests covering the affected areas
   - Surface hard constraints (framework versions, API contracts, legacy code that cannot change)

3. **Identify risks.** Areas of uncertainty, complexity, or fragility that could cause the
   implementation to go wrong or take longer than expected.

4. **Write `2-research.md`** in `.adw/<task-slug>/`:

   ```markdown
   # Research: <task-slug>

   ## Task context
   <one paragraph restating what is being built and why, from 1-phase-plan.md>

   ## Relevant code
   <file paths, function names, class names, patterns found — be specific>

   ## Constraints
   <technical constraints, existing patterns that must be respected, things that cannot change>

   ## Risks
   <potential pitfalls, areas of uncertainty, complexity hotspots>

   ## Handoff notes
   <summary for the PRD and Plan phases: what they need to know from this research>
   ```

5. **Update `0-state.md`**: `current-phase: 2 — Research`, `phase-status: complete`,
   check Phase 2 in Completed phases.

## Quality bar

`2-research.md` is complete when:
- Relevant files are listed with specific paths (not "somewhere in the codebase")
- At least one constraint and one risk are documented (if there are genuinely none, say so
  explicitly — do not leave the sections empty)
- Handoff notes are concise enough that `adw-prd` can start without asking follow-up questions
