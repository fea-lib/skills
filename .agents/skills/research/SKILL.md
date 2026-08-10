---
name: research
description: >
  Run durable, auditable research workflows with bounded autonomy and resumable
  state. Use when the user asks for `/research ...`, asks for structured
  decision-support research with citations and quality gates, requests AFK
  research mode (`--afk`), or wants checkpointed depth-controlled research
  (`--depth quick|standard|deep`) with local run artifacts, including `/research --help`.
---

# Agentic Research Assistant

Run research as a resumable workflow, not an ad hoc chat. The objective is
decision-support quality with explicit provenance, visible uncertainty, and
bounded autonomy.

Read these references before execution:
- `references/run-folder-contract.md`
- `references/quality-gates.md`
- `references/templates.md`

## Command Contract

Treat this as the v1 command surface:

```text
/research <question> [--depth quick|standard|deep] [--afk] [--sources web,local,repos,docs,papers,video] [--allow-tool <name>] [--disallow-tool <name>] [--out <run-slug>] [--help]

/research prompt-builder [<rough prompt text>]
```

- Require `<question>`.
- Require intended use before execution starts.
- Default `--depth` to `standard`.
- Use `--afk` only for checkpoint policy; do not reduce research quality goals.
- Treat `--allow-tool` and `--disallow-tool` as run-local overrides.

### `--help` behavior

When invoked with `/research --help`, do not start a run. Return:
- A short summary of what `/research` does in no more than 2 sentences.
- Full usage and option list.

Use this exact option inventory in help output:

```text
Usage:
  /research <question> [--depth quick|standard|deep] [--afk] [--sources web,local,repos,docs,papers,video] [--allow-tool <name>] [--disallow-tool <name>] [--out <run-slug>] [--help]

  /research prompt-builder [<rough prompt text>]

Options (research):
  --depth <quick|standard|deep>   Research budget and strictness (default: standard)
  --afk                           Disable mid-run checkpoints; defer decisions to final review
  --sources <list>                Comma-separated source classes: web,local,repos,docs,papers,video
  --allow-tool <name>             Add tool to allowlist for this run (repeatable)
  --disallow-tool <name>          Remove tool from allowlist for this run (repeatable)
  --out <run-slug>                Override output run folder slug
  --help                          Show summary, usage, and options without executing
```

## Research Prompt Builder

Use `/research prompt-builder [<rough prompt text>]` to enter an interactive
wizard that helps craft a high-quality research brief. The wizard produces a
saved `brief.md` and a copy-paste `/research` command string.

If invoked with no text, show a brief usage note then start the empty wizard.

### Interaction flow

1. **Parse** — Extract known fields from the rough prompt (if any).
2. **Wizard loop** — Ask one question at a time for each missing field. The
   user can say "done" at any point to exit early. Collect these fields:
   - Research question (required)
   - Intended use / decision this informs (required)
   - Depth: `quick|standard|deep` (required)
   - AFK vs checkpoint mode
   - Source preferences: `web,local,repos,docs,papers,video`
   - Source distrusts / exclusions (free-text; show examples: vendor marketing,
     social media, personal blogs, AI-generated content)
   - Recency requirements
   - Scope constraints (in scope / out of scope)
   - Evidence threshold (4-level picker: gut check / standard / high
     confidence / decision-grade, with free-text override)
3. **Quality check pass** — Run the assembled brief through the heuristic
   checklist below. For each fail or warn, show the issue and a concrete
   rewrite suggestion. The user can accept the suggestion, override, or go
   back to the relevant wizard question. Loop until all checks are resolved
   or explicitly accepted-as-is.
4. **Summary** — Display the full brief and the generated `/research` command.
   Ask "Looks good?" — confirm or cancel.
5. **Save** — Write `brief.md` to
    Follow project conventions on where to store research artifacts; fall
    back to `<workspace-root>/docs/research/<slug>/`.
    Derive slug from the research question; offer an override option during
    the wizard.
6. **Handoff** — Print the copy-paste `/research` command, then ask "Run now?"
   If yes, proceed to the standard research execution workflow (step 1 of the
   Operating Model below). If no, exit.

### Quality heuristic checklist

Run each check against the assembled brief. For each failure, present the
issue and a concrete rewrite suggestion:

| Check | What it catches | Suggestion pattern |
|---|---|---|
| **Vagueness** | Question lacks a specific angle, comparison, or constraint | Push for actionable framing: "What specifically about X? A comparison between approaches? A performance question?" |
| **Missing intended use** | No decision context; research will drift | Prompt: "What will you do with this information? What decision does it inform?" |
| **Breadth/depth mismatch** | `--depth quick` with 6+ source types or a very broad scope | Warn and recommend adjusting depth or narrowing scope |
| **Leading / bias** | Question assumes a conclusion ("Why is X better than Y?") | Suggest neutral reframe: "What are the tradeoffs between X and Y?" |
| **Unstated assumptions** | Question implies a commitment the user hasn't validated | Surface: "Does this assume X is the right approach? Are alternatives in scope?" |
| **Empty confidence threshold** | No evidence threshold set | Prompt with the 4-level picker: "What would be good enough to act on?" |
| **Source blind spot** | Contradictory source policy (e.g., distrusts vendors but needs product comparisons) | Flag the contradiction and ask for resolution |



## Operating Model

### 1) Intake and brief normalisation

Collect and write `brief.md` first. Require:
- Research question
- Intended use / decision this informs

Capture if available, else default and record assumptions:
- Scope constraints and exclusions
- Source preferences and distrusts
- Recency requirements
- Source types in scope
- Depth and checkpoint mode
- Tool allowlist policy and overrides
- Evidence threshold / confidence requirement

Use the template in `references/templates.md`.

### 2) Run folder setup

Create a run folder and write only inside it during execution.

Default location:
- Follow project conventions for research artifact storage; fall back to
  `<workspace-root>/docs/research/<run-slug>/`

Run slug precedence:
1. `--out`
2. Derived slug from question

Initialize:
- `state.json`
- `run-log.md`
- `notes/`

Use `references/run-folder-contract.md` for required files.

### 3) Graph-driven execution

Model the run as a dependency graph with persisted node state.

Allowed node types include:
- Subquestion planning
- Discovery/retrieval
- Source analysis
- Secondary-lead follow-up
- Checkpoint decisions
- Synthesis sections
- Evaluator/quality-gate passes
- Report generation

Parallelise independent nodes. Do not block unrelated branches when one branch is
blocked or waiting.

### 4) Depth budgets

Treat depth as budget defaults, not guarantees:

| Depth | Defaults |
|---|---|
| `quick` | 3-5 sources, no secondary recursion pass, light evaluator pass |
| `standard` | 6-12 sources, one secondary-source pass, full quality gates |
| `deep` | 12-30 sources, broader multi-branch recursion, stricter evaluator pass |

If quality gates cannot be fully satisfied within budget, stop and document gaps.
Do not loop indefinitely.

### 5) Checkpoint policy

Default mode: pause for meaningful decisions:
- Material scope expansion
- High-cost / unusually slow / unusually broad tool use
- Material source conflicts affecting conclusions
- Low-confidence synthesis on important claims
- Consequential actions
- Final decision-grade sign-off

AFK mode (`--afk`):
- Do not pause for mid-run research-quality decisions after intake
- Continue independent branches when one branch is blocked
- Record unresolved decisions, skipped approvals, blocked branches, and material
  assumptions in `deferred-decisions.md`
- Still produce final report and final review handoff

### 6) Evidence and provenance

Record source-level notes for each analyzed source in `notes/`.

For important claims, keep claim-level records including:
- Source IDs
- Quote or precise paraphrase
- Quality rating
- Support status
- Confidence label

Confidence labels:
- `corroborated`
- `single-sourced`
- `contradicted`
- `unresolved`
- `interpretive`

### 7) Quality gates and finalization

Run gates from `references/quality-gates.md` before finalizing.

Gate failures do not block report generation by default, but must be explicit in:
- `evaluation.md`
- `final-report.md` (confidence and gap signaling)

Generate:
- `source-inventory.md`
- `evaluation.md`
- `final-report.md`
- Optional compact summary

In AFK mode, include a deferred-decision section or link.

### 8) Resume behavior

Resume from `state.json`:
- Do not repeat completed nodes unless explicitly invalidated
- Preserve blocked reasons and dependencies
- Continue from pending/blocked frontier

## Source and Tool Scope

In scope for v1 (when tools are available):
- Web pages
- Local files
- Code repositories
- Documentation sources
- PDFs/papers
- Video transcripts

Out of scope unless user supplies local/exported artifacts:
- Social media
- Private SaaS apps and chats
- Ticketing systems
- Cloud drives
- Databases

Use tool allowlists and per-run overrides from the brief. When a disallowed or
unavailable tool blocks work, record it as blocked/skipped with impact.

## Safety and Privacy

- Store artifacts locally in the run folder only.
- Redact secrets from persisted artifacts.
- Do not perform autonomous irreversible external actions.
- Do not publish or copy outputs elsewhere without explicit instruction.

## Completion Criteria

A run is complete when:
- Budget is exhausted or saturation is reached
- Subquestions are answered as far as evidence allows
- Quality gates pass, or failures are clearly documented
- Remaining conflicts, gaps, and deferred decisions are explicit
