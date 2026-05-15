---
title: Game Studio - Phase 0 Implementation Addendum
status: approved
owner_role: human
updated_at: 2026-05-15
---

# Game Studio - Phase 0 Implementation Addendum

## Purpose

This document closes the remaining implementation gaps required to build the Game Studio as a skill plus CLI without architectural guesswork.

This addendum is normative for implementation. If it conflicts with older wording in `system-reminder.md` or `implementation-plan.md`, this addendum wins for machine-facing behavior.

## Product Form

The v1 deliverable has three parts:

1. A skill that encodes orchestrator behavior, phase rules, role routing, approval gates, and response standards.
2. A CLI that performs deterministic local operations such as project initialization, artefact creation, validation, and state inspection.
3. Repo-native Markdown artefacts generated into a target workspace and treated as the canonical project memory.

The v1 deliverable is not a standalone hosted application.

## Source Repo Versus Target Workspace

The implementation must distinguish between:

1. The skill source repository, where the skill, CLI, prompts, templates, and tests live.
2. The target workspace, where a game project's canonical artefacts are created and maintained.

Generated project artefacts must not be stored inside the skill source repository unless the human explicitly points the CLI at that repository as the target workspace.

## Canonical Layout

### Skill Source Repository

Recommended layout:

```text
<skills-repo>/
  docs/
    game-studio/
      system-reminder.md
      implementation-plan.md
      phase-0-implementation-addendum.md
      roles/
  .agents/
    skills/
      game-studio/
        SKILL.md
        references/
          roles.md
          workflow.md
          templates/
        scripts/
          game-studio
          game_studio/
            src/
            tests/
```

### Target Workspace

Canonical project artefacts must live at:

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

1. One active project per CLI invocation.
2. Role contracts and templates are global inputs, not project state.
3. Canonical artefacts always live under the target workspace project path.
4. Revisions happen in place unless an artefact is explicitly append-only.

## Canonical Status Vocabulary

All machine-facing status values must use kebab-case only:

1. `draft`
2. `approved`
3. `approved-with-conditions`
4. `rework-required`
5. `rejected`
6. `parked`

Rules:

1. Frontmatter, CLI JSON output, validators, and state transition logic must use these exact values.
2. Human-readable CLI text may render friendly labels, but serialized values must remain unchanged.
3. Any document or template using `approved with conditions` or `rework required` in machine-facing fields must be treated as invalid until normalized.

## Implementation Brief Contract

The implementation brief file shape is fixed as follows:

1. The reusable template remains `.agents/skills/game-studio/references/templates/08-implementation-brief.md` inside the skill source repository.
2. Generated canonical implementation briefs live under `08-implementation-briefs/` in the target project.
3. Generated file names must use `IMP-XXX-<slice>.md` where `XXX` is a zero-padded numeric sequence.

Example:

```text
.agents/skills/game-studio/references/templates/08-implementation-brief.md
<target-docs-dir>/game-studio/projects/<project-slug>/08-implementation-briefs/IMP-001-core-loop-prototype.md
```

## CLI Contract

The CLI is the deterministic operating surface for the studio.

### Commands

The minimum v1 command surface is:

```text
game-studio init
game-studio status
game-studio phase show
game-studio phase advance
game-studio artefact create
game-studio artefact validate
game-studio change request
game-studio brief create
game-studio doctor
```

### Command Semantics

1. `game-studio init`
Creates the target project folder and seeds required artefacts from templates.

2. `game-studio status`
Reads the active project and prints current phase, blockers, approved artefacts, accepted risks, and recommended next step.

3. `game-studio phase show`
Prints the active phase, allowed next transitions, and unmet gate conditions.

4. `game-studio phase advance`
Attempts a phase transition only if gate conditions are met. Must fail if explicit approval is missing.

5. `game-studio artefact create`
Creates or refreshes a canonical artefact from the correct template for the requested phase or type.

6. `game-studio artefact validate`
Validates folder layout, required artefacts, frontmatter, status vocabulary, and phase-state consistency.

7. `game-studio change request`
Appends a structured change decision entry and updates affected project state files.

8. `game-studio brief create`
Creates the next `IMP-XXX-<slice>.md` file from the implementation brief template.

9. `game-studio doctor`
Runs a broader diagnostic pass across config, filesystem assumptions, required files, and project consistency.

### Common Flags

All relevant commands should support:

1. `--workspace <path>`
2. `--docs-dir <path>`
3. `--project <slug>`
4. `--json`
5. `--non-interactive`
6. `--yes`
7. `--model <provider/model>`
8. `--role-model <provider/model>`
9. `--timeout-ms <n>`

Rules:

1. Default output is human-readable.
2. `--json` must emit machine-readable structured output only.
3. `--non-interactive` must fail instead of prompting for missing required input.
4. Commands must return non-zero exit codes on validation failures, state transition failures, and provider/runtime failures.

## Runtime Architecture

### Responsibility Split

The CLI handles deterministic operations:

1. Path resolution.
2. Template instantiation.
3. Frontmatter parsing and writing.
4. Validation.
5. Phase transition eligibility checks.
6. Structured file updates.

The skill and orchestrator handle judgment operations:

1. Role routing.
2. Recommendation synthesis.
3. Trade-off analysis.
4. Change impact reasoning.
5. Implementation brief reasoning.

### Role Invocation Model

The v1 runtime must use separate sequential role calls.

Rules:

1. One primary role produces the first draft.
2. Consulted roles react to that draft and the cited artefacts.
3. The orchestrator consolidates outputs and writes or updates the canonical artefact.
4. No peer-to-peer role chatter in v1.
5. No long-running shared multi-role context in v1.
6. Deep-dive sessions are temporary scoped sessions that return control to the orchestrator.

## Tooling Contract

### Mandatory Capabilities

The implementation must support deterministic access to:

1. File reads.
2. File writes or edits.
3. Glob or file discovery.
4. Content search.

### Optional Capabilities

Optional for v1:

1. Shell execution for tests and diagnostics.
2. Specialist subagents for deeper analysis.

Rule:

If a deterministic operation can be executed directly, it must not be delegated to free-form LLM reasoning.

## Persistence Rules

1. Project root must always be explicit via flag, config, or interactive prompt.
2. The skill source repository is read-only reference input during normal project operation.
3. Canonical project state lives only in the target workspace.
4. Temporary exploratory notes are non-canonical until explicitly promoted.
5. The orchestrator is the only authority that may promote a draft into canonical project state.

## Provider and Model Execution Policy

The v1 policy prioritizes predictability over clever fallback behavior.

Rules:

1. Configure one orchestrator model.
2. Configure one role model, defaulting to the orchestrator model when omitted.
3. Do not implement automatic provider fallback in v1.
4. Retry at most 2 times on transient provider or network errors.
5. Default timeout is 60000 ms per role call unless overridden.
6. Load only phase-relevant artefacts by default.
7. Prefer summary-first context loading before full artefacts when feasible.
8. On provider failure, do not advance phase or write misleading approval state.
9. Partial draft content may be persisted only if explicitly marked non-canonical.

## Validation and Test Plan

Implementation does not begin without automated validation coverage for the CLI and state model.

### Required Test Layers

1. Unit tests for path resolution.
2. Unit tests for frontmatter parsing.
3. Unit tests for status normalization and validation.
4. Unit tests for phase transition validation.
5. Fixture tests for valid project layout.
6. Fixture tests for missing required files.
7. Fixture tests for invalid status values.
8. Fixture tests for invalid phase transitions.
9. Smoke tests for `init`, `status`, `artefact validate`, and `brief create`.
10. Golden tests for JSON output shape.
11. One end-to-end fixture covering project init, state inspection, artefact validation, and creation of one implementation brief.

### Minimum Acceptance Automation

The CLI is not ready for use until automated tests prove:

1. A project can be initialized from templates.
2. An invalid status value is rejected.
3. A phase cannot advance without required approval.
4. A valid implementation brief can be created at the correct path.
5. `--json` responses are stable and parseable.

## Build Start Gate

The implementation may start once the following are treated as locked:

1. CLI command surface.
2. Runtime responsibility split.
3. Canonical status vocabulary.
4. Implementation brief path rules.
5. Provider failure policy.
6. CLI validation and smoke-test plan.

## Immediate Build Recommendation

Start with these implementation slices in order:

1. Filesystem and config resolution.
2. Template instantiation and project init.
3. Frontmatter parser and status validator.
4. State reader for `00-current-state.md` and `00-risk-register.md`.
5. `status`, `phase show`, and `artefact validate` commands.
6. `brief create` command and `IMP-XXX` sequencing.
7. Skill wiring and orchestrator prompt packaging.
