## Problem Statement

The `multi-model-research` skill, while functional, suffers from several operational fragilities that impede a smooth automated research workflow:
1.  **Command Parsing Errors:** Sub-agent commands are emitted as raw bash strings. If these strings contain special characters or if the shell's argument parsing is ambiguous, the command fails.
2.  **Research Timeouts:** The default timeout for `opencode run` (120s) is often insufficient for the `research` skill, which performs multiple web fetches and deep analysis.
3.  **Inaccessible PDF Content:** The `research` skill's primary fetching tool (`webfetch`) often returns binary data for PDFs, which the models cannot parse. This results in the research being grounded only in HTML summaries rather than primary source documents.
4.  **Brittle Error Handling:** When a sub-agent command fails (e.g., due to timeout or parsing), the orchestrator lacks an automated way to suggest a fix or retry with adjusted parameters.
5.  **Environment Stability:** Potential environment issues (like AVX warnings) are not proactively checked, leading to mysterious failures.

## Solution

Revise the `multi-model-research` orchestrator (`run.py`) and its associated prompt templates to improve robustness, observability, and content accessibility. This involves standardizing command emission, increasing default timeouts, enabling a fallback mechanism for PDF reading, and adding environment health checks.

## User Stories

1. As a research orchestrator, I want to use the `--` separator in all emitted `opencode run` commands, so that my instructions are never misparsed as CLI flags.
2. As a research orchestrator, I want to increase the default timeout for sub-agent research tasks to 600 seconds, so that complex source gathering doesn't get cut short.
3. As a researcher, I want my sub-agents to have a "Download-then-Read" strategy for PDFs, so that I can access the full text of primary documents even when `webfetch` returns binary data.
4. As a researcher, I want the `research` skill to proactively use the `Read` tool on local PDF binaries when `webfetch` provides a URL, so that content is accessible.
5. As an orchestrator, I want to verify that all output files exist and contain valid score blocks before proceeding to the next round, so that I don't attempt to score missing data.
6. As a research orchestrator, I want a `doctor` command to check for AVX support and required dependencies (like `playwright`), so that I can warn the user about potential environment issues early.
7. As a researcher, I want to be able to override the global timeout during `init`, so that I can adjust for particularly slow or fast networks.
8. As a sub-agent, I want clear instructions in my prompt on how to handle binary downloads, so that I don't get stuck with unreadable content.

## Implementation Decisions

### Orchestrator (`run.py`)
- **CLI Robustness:** Modify `emit_subagent_cmd` to insert `--` before the positional prompt message.
- **Timeout Management:**
    - Add a `--timeout` argument to the `init` command (default 600000ms).
    - Persist this timeout in `_state.json`.
    - Apply this timeout to all emitted bash commands.
- **Score Verification:**
    - Update `cmd_score_round` to check for file existence.
    - If a file is missing, print a `RERUN_REQUIRED` message with the specific command to run.
- **Environment Checks:**
    - Add a `cmd_doctor` function.
    - Implement checks for `bun` version, AVX support (via `sysctl` or `/proc/cpuinfo`), and `playwright` installation.

### Prompt Templates (`references/prompts.md`)
- **PDF Handling Strategy:** Update the "Step-A — Produce (Round 1: Research)" template to include a instruction for handling binary PDFs: "If a primary source is a PDF and webfetch returns binary data, download the file locally and use the Read tool to extract the text."

### Research Skill Interaction
- No direct changes to the `research` skill itself are proposed here, but the *usage* of it by `multi-model-research` sub-agents will be modified via the prompt update to bridge the `webfetch`/`Read` gap.

## Testing Decisions

- **Command Generation Test:** Verify that `emit_subagent_cmd` produces a string containing both `--` and the correct timeout value.
- **State Persistence Test:** Verify that a custom timeout passed to `init` is correctly saved in `_state.json`.
- **Score Extraction Robustness:** Test `extract_scores` with malformed, empty, and valid JSON blocks.
- **Doctor Command Verification:** Run `run.py doctor` on the current environment and verify it detects the known AVX limitation.

## Out of Scope

- Fixing the `webfetch` tool's binary handling globally (this remains a local workaround for the research skill).
- Modifying the core `opencode` CLI or its model providers.
- Adding new research plugins (like Confluence or Obsidian) as part of this fix.

## Further Notes

- The AVX warning is a known issue on some hardware/OS configurations. The `doctor` command should specifically warn about this if detected.
- The "Download-then-Read" strategy assumes the sub-agent's environment has write access to the workspace, which was confirmed in this session.

---

# Plan: Multi-Model Research Robustness Hardening

> Source PRD: `.prd/01-multi-model-research-robustness.md`

## Architectural decisions

Durable decisions that apply across all phases:

- **Command surface**: The orchestrator remains a subcommand CLI (`list-defaults`, `list-models`, `config`, `init`, `score-round`, `finalize`, `deliver`) with a new `doctor` health-check command.
- **Workflow shape**: Execution stays stage-based (`init` -> round produce/compare -> `score-round` -> `finalize` -> `deliver`) with state persisted between commands.
- **State schema**: `_state.json` remains the source of run state and will include configurable timeout and round-scoring metadata.
- **Key models**: `topic`, `models`, `tokens`, round artifacts (`rN-produce`, `rN-compare`), score matrix, winner metadata, and output destinations.
- **Prompt boundary**: Sub-agent behavior is controlled through `references/prompts.md` templates with placeholder substitution before each run.
- **Tooling boundary**: PDF accessibility is handled as an orchestration strategy (prompt and run behavior), not by changing external `webfetch` internals.

---

## Phase 1: Safe Command Envelope + Configurable Timeout Baseline

**User stories**: 1, 2, 7

### What to build

Establish a stable command contract for all emitted sub-agent invocations and make timeout an explicit run configuration that can be set at initialization, persisted in run state, and applied consistently to emitted commands.

### Acceptance criteria

- [ ] Every emitted `opencode run` command includes a positional separator that prevents prompt text from being parsed as CLI flags.
- [ ] `init` accepts a global timeout value with a default of 600000ms.
- [ ] The selected timeout is persisted to run state and reused by all emitted sub-agent commands.

---

## Phase 2: Round Integrity Guardrails

**User stories**: 5

### What to build

Harden round progression so scoring only proceeds when expected artifacts exist and contain machine-readable score data, with actionable rerun instructions when prerequisites are missing or malformed.

### Acceptance criteria

- [ ] Round scoring validates expected compare outputs before computing winners.
- [ ] Missing or invalid comparator outputs produce clear rerun guidance tied to the specific missing artifact.
- [ ] Pipeline state is not advanced for a round until valid score inputs are available.

---

## Phase 3: PDF-Accessible Research Strategy in Round-1 Produce

**User stories**: 3, 8

### What to build

Update the Round-1 research prompt contract so sub-agents follow a deterministic fallback for binary PDF sources: download locally and read via local tools, preserving grounding in primary documents.

### Acceptance criteria

- [ ] Round-1 produce prompt explicitly instructs a download-then-read fallback for binary PDF responses.
- [ ] Prompt wording clarifies expected behavior without exposing model identity or orchestration internals.
- [ ] Research outputs can include findings grounded in PDF primary sources when direct fetch content is unreadable.

---

## Phase 4: Research Skill Usage Hardening for Local Binary Reads

**User stories**: 4

### What to build

Tighten orchestration-level instructions so sub-agents reliably use local file reading for downloaded binaries in research workflows, without requiring direct modification of the separate `research` skill implementation.

### Acceptance criteria

- [ ] Orchestration prompts make local binary read behavior explicit and unambiguous.
- [ ] The fallback path is framed as default behavior whenever URL fetch returns binary content.
- [ ] No direct source changes are required in the standalone `research` skill to activate this behavior.

---

## Phase 5: Environment Doctor + Early Risk Signaling

**User stories**: 6

### What to build

Add a preflight health-check command that validates runtime prerequisites and surfaces actionable warnings (including AVX-related risks) before users begin a research run.

### Acceptance criteria

- [ ] A `doctor` command exists and runs independently of active research runs.
- [ ] Doctor reports include runtime/tooling checks for core dependencies and browser automation requirements.
- [ ] Doctor output explicitly flags AVX-related risks with actionable warning text.

---

## Phase 6: Robustness Regression Harness

**User stories**: 1, 2, 5, 6, 7

### What to build

Codify regression checks for command generation, timeout persistence, score extraction robustness, and doctor diagnostics so reliability improvements remain stable over future edits.

### Acceptance criteria

- [ ] Tests or scripted checks verify command emission includes safe argument separation and configured timeout.
- [ ] Tests or scripted checks verify timeout persistence in run state from `init` inputs.
- [ ] Score extraction and round scoring checks cover malformed, empty, and valid score blocks.
- [ ] Doctor verification confirms known AVX limitation is detected and reported on affected environments.

---

## Implementation Tickets

### Ticket 1: Safe command envelope and timeout baseline

- **Phase**: 1
- **User stories**: 1, 2, 7
- **Depends on**: none
- **Scope**: Add `--` separator in emitted sub-agent commands; add `--timeout` to `init` (default `600000` ms); persist timeout in `_state.json`; apply timeout to all emitted `opencode run` commands.
- **Definition of done**:
  - [ ] Emitted commands include positional argument separator.
  - [ ] Timeout can be overridden at init and defaults correctly.
  - [ ] Persisted timeout is reused in all subsequent command emission paths.

### Ticket 2: Round integrity guardrails

- **Phase**: 2
- **User stories**: 5
- **Depends on**: Ticket 1
- **Scope**: Validate expected compare files exist and contain valid score blocks before winner computation; emit actionable rerun instructions when prerequisites fail.
- **Definition of done**:
  - [ ] Missing compare artifacts are detected before scoring.
  - [ ] Malformed or absent score blocks are reported with explicit rerun guidance.
  - [ ] Round state does not advance on invalid inputs.

### Ticket 3: Round-1 PDF fallback prompt contract

- **Phase**: 3
- **User stories**: 3, 8
- **Depends on**: none
- **Scope**: Update Round-1 research prompt template to instruct download-then-read behavior for binary PDF fetch results.
- **Definition of done**:
  - [ ] Prompt text includes deterministic binary PDF fallback instructions.
  - [ ] Instructions preserve anonymity requirements and prompt fidelity requirements.
  - [ ] Output quality criteria still align with existing research deliverable expectations.

### Ticket 4: Orchestration-level local binary read hardening

- **Phase**: 4
- **User stories**: 4
- **Depends on**: Ticket 3
- **Scope**: Ensure orchestration instructions consistently direct sub-agents to local `Read`-based extraction for downloaded binaries without modifying the separate `research` skill.
- **Definition of done**:
  - [ ] Prompt guidance unambiguously indicates local read fallback when URL fetch is binary.
  - [ ] Behavior is achievable through orchestration/prompt updates only.
  - [ ] No direct edits are required in the standalone `research` skill package.

### Ticket 5: Add doctor command and environment diagnostics

- **Phase**: 5
- **User stories**: 6
- **Depends on**: Ticket 1
- **Scope**: Introduce `doctor` command to check runtime and dependency prerequisites (including AVX risk and browser automation dependency state) and print actionable warnings.
- **Definition of done**:
  - [ ] CLI exposes `doctor` subcommand with clear output.
  - [ ] Checks cover runtime, AVX support signal, and Playwright dependency signal.
  - [ ] Warning text clearly indicates risk and recommended remediation.

### Ticket 6: Regression coverage for robustness features

- **Phase**: 6
- **User stories**: 1, 2, 5, 6, 7
- **Depends on**: Tickets 1, 2, 5
- **Scope**: Add tests or scripted verification for command generation, timeout persistence, score parsing/scoring resilience, and doctor behavior.
- **Definition of done**:
  - [ ] Command generation checks validate separator and timeout emission.
  - [ ] State persistence checks validate timeout round-trip in `_state.json`.
  - [ ] Score extraction/scoring checks cover malformed, empty, and valid score blocks.
  - [ ] Doctor checks verify AVX warning behavior in known-limited environment.

### Optional sub-tasks (for splitting in tracker)

- **T1.1**: Add `--timeout` init parsing and default value handling.
- **T1.2**: Persist timeout in state and thread through command emission helpers.
- **T1.3**: Add command separator handling in all emitted `opencode run` invocations.
- **T2.1**: Expected compare file set validation per round.
- **T2.2**: Score block validation and rerun message templating.
- **T3.1**: Update Round-1 produce prompt with PDF binary fallback text.
- **T4.1**: Align orchestration instructions with `Read`-based local extraction behavior.
- **T5.1**: Implement `doctor` command wiring and diagnostics output formatting.
- **T5.2**: Add checks for runtime, AVX indicators, and Playwright presence.
- **T6.1**: Add regression checks for command generation and timeout persistence.
- **T6.2**: Add malformed/empty/valid score block tests.
- **T6.3**: Add doctor verification path for AVX warning behavior.
