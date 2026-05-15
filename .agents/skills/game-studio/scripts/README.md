# Game Studio

An LLM agent skill and deterministic CLI for guiding a single game project through a structured, phase-gated development workflow from idea to implementation.

## What it is

The Game Studio is a workflow-first system. It does not generate a game autonomously. Instead it provides:

- A fixed eight-phase workflow with explicit human approval gates.
- Specialist role contracts (Creative/Product Lead, Producer, Game Designer, Engineering Lead, Art Director) invoked by an orchestrator, not running continuously.
- Repo-native Markdown artefacts as the single source of truth for every project decision.
- A deterministic CLI that handles all file operations — path resolution, project initialisation, artefact creation and validation, phase transitions, change logging, and diagnostics.

The skill (LLM layer) handles judgment: recommendation synthesis, role routing, trade-off analysis, implementation brief reasoning. The CLI handles everything deterministic.

## Phases

| # | Phase | Gate artefact |
|---|---|---|
| 01 | Idea Intake | `01-idea-brief.md` |
| 02 | Vision Definition | `02-vision-brief.md` |
| 03 | Concept Stress Test | `03-concept-stress-test.md` |
| 04 | Pre-Production Design | `04-design-package.md` |
| 05 | Prototype Planning *(optional)* | `05-prototype-plan.md` |
| 06 | Production Planning | `06-production-plan.md` |
| 07 | Change Control *(standing)* | — |
| 08 | Implementation Support | — |

A phase cannot advance until its gate artefact carries an `approved` or `approved-with-conditions` status, set by explicit human approval.

## Repository layout

```
docs/game-studio/
  system-reminder.md                   # Architecture and orchestrator spec
  implementation-plan.md               # Build sequencing
  phase-0-implementation-addendum.md   # Machine-facing contracts (normative)
  roles/                               # Specialist role contracts

.agents/skills/game-studio/
  SKILL.md
  references/
    roles.md
    workflow.md
    templates/                         # Source templates for artefact generation
  scripts/
    game-studio                        # Executable CLI entry point
    game_studio/
      src/                             # Command/runtime implementation
      tests/                           # Full CLI integration tests
```

## Project artefacts layout (target workspace)

Generated artefacts live in the **target workspace**, not this repository:

```
<workspace>/<docs-dir>/game-studio/projects/<project-slug>/
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
    IMP-001-<slice-name>.md
    IMP-002-<slice-name>.md
```

## Status vocabulary

All frontmatter `status` fields use these exact kebab-case values:

- `draft`
- `approved`
- `approved-with-conditions`
- `rework-required`
- `rejected`
- `parked`

Any other value is rejected by the validator.

## Installation

No package installation required. Python 3.10+ standard library only.

Make the entry point executable once:

```bash
chmod +x .agents/skills/game-studio/scripts/game-studio
```

Then run from the repository root:

```bash
python3 .agents/skills/game-studio/scripts/game-studio --help
```

Or add `.agents/skills/game-studio/scripts/` to your `PATH` to call it as `game-studio` from anywhere.

## Common flags

All commands require these three flags:

| Flag | Description |
|---|---|
| `--workspace <path>` | Root path of the target workspace |
| `--docs-dir <path>` | Docs directory relative to `--workspace` |
| `--project <slug>` | Project slug (folder name under `projects/`) |
| `--json` | Emit machine-readable JSON instead of human text |

## Commands

### `init`

Initialise a new project by creating all canonical artefacts from templates.

```bash
python3 .agents/skills/game-studio/scripts/game-studio \
  --workspace ~/my-game-repo \
  --docs-dir docs \
  --project dragon-heist \
  init
```

Use `--overwrite` to regenerate artefacts that already exist.

---

### `status`

Show the current phase, recommended next step, and blocking questions.

```bash
python3 .agents/skills/game-studio/scripts/game-studio \
  --workspace ~/my-game-repo \
  --docs-dir docs \
  --project dragon-heist \
  status
```

JSON output:

```bash
python3 .agents/skills/game-studio/scripts/game-studio \
  --workspace ~/my-game-repo \
  --docs-dir docs \
  --project dragon-heist \
  --json status
```

---

### `phase show`

Show the current phase, valid next phases, and whether the gate artefact is approved.

```bash
python3 .agents/skills/game-studio/scripts/game-studio \
  --workspace ~/my-game-repo \
  --docs-dir docs \
  --project dragon-heist \
  phase show
```

---

### `phase advance`

Advance to the next phase. The gate artefact for the current phase must have `approved` or `approved-with-conditions` status. The command fails with a clear error if the gate is not met or the transition is invalid.

```bash
python3 .agents/skills/game-studio/scripts/game-studio \
  --workspace ~/my-game-repo \
  --docs-dir docs \
  --project dragon-heist \
  phase advance --to 02-vision-definition
```

Valid phase values:

```
01-idea-intake
02-vision-definition
03-concept-stress-test
04-pre-production-design
05-prototype-planning
06-production-planning
07-change-control
08-implementation-support
```

---

### `artefact validate`

Validate the project folder: checks required files exist, all frontmatter statuses are valid, and the active phase is recognised.

```bash
python3 .agents/skills/game-studio/scripts/game-studio \
  --workspace ~/my-game-repo \
  --docs-dir docs \
  --project dragon-heist \
  artefact validate
```

Returns exit code `1` if any issues are found.

---

### `artefact create`

Create or refresh a single canonical artefact from its template.

```bash
python3 .agents/skills/game-studio/scripts/game-studio \
  --workspace ~/my-game-repo \
  --docs-dir docs \
  --project dragon-heist \
  artefact create --artefact 04-design-package.md
```

Use `--overwrite` to replace an existing artefact.

---

### `change request`

Append a new `CHG-XXX` entry to `07-change-decisions.md` with an auto-incrementing ID.

```bash
python3 .agents/skills/game-studio/scripts/game-studio \
  --workspace ~/my-game-repo \
  --docs-dir docs \
  --project dragon-heist \
  change request \
  --title "Add crafting mechanic" \
  --description "Player should be able to craft items at workbenches."
```

---

### `brief create`

Create the next `IMP-XXX-<slice>.md` file under `08-implementation-briefs/` from the implementation brief template. IDs are assigned sequentially.

```bash
python3 .agents/skills/game-studio/scripts/game-studio \
  --workspace ~/my-game-repo \
  --docs-dir docs \
  --project dragon-heist \
  brief create --slice-name "Core Loop Prototype"
```

---

### `doctor`

Run a full diagnostic pass: verifies the templates directory, project layout, artefact frontmatter, and phase consistency. Gate-not-met is reported as a warning (not a failure) on a fresh project.

```bash
python3 .agents/skills/game-studio/scripts/game-studio \
  --workspace ~/my-game-repo \
  --docs-dir docs \
  --project dragon-heist \
  doctor
```

## Typical session flow

```bash
# 1. Start a new project
python3 .agents/skills/game-studio/scripts/game-studio --workspace ~/my-game-repo --docs-dir docs --project dragon-heist init

# 2. Check state
python3 .agents/skills/game-studio/scripts/game-studio --workspace ~/my-game-repo --docs-dir docs --project dragon-heist status

# 3. Work with the orchestrator (LLM) to fill out 01-idea-brief.md
#    Once it's approved, update its frontmatter status to: approved

# 4. Advance to the next phase
python3 .agents/skills/game-studio/scripts/game-studio --workspace ~/my-game-repo --docs-dir docs --project dragon-heist phase advance --to 02-vision-definition

# 5. Continue through phases until production planning is approved

# 6. Create an implementation brief for the first slice
python3 .agents/skills/game-studio/scripts/game-studio --workspace ~/my-game-repo --docs-dir docs --project dragon-heist brief create --slice-name "Core Movement"

# 7. After implementation, record a change if scope shifts
python3 .agents/skills/game-studio/scripts/game-studio --workspace ~/my-game-repo --docs-dir docs --project dragon-heist change request --title "Remove dash ability" --description "Playtesting showed dash breaks level pacing."
```

## Running tests

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

All 16 tests should pass. No external dependencies required.

## Key design constraints

- The CLI never calls an LLM. All operations are deterministic.
- The skill (LLM layer) never writes directly to canonical artefacts without going through the CLI or explicit file tool use under orchestrator control.
- Generated project artefacts belong in the target workspace, not this repository.
- `phase advance` will always fail if the gate artefact is not approved. This is intentional and not bypassable via flags.
- Status values are strictly validated. Using prose forms like `approved with conditions` will cause `artefact validate` and `doctor` to fail.
