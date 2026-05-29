---
title: 'PRD: Agentic Research Assistant'
---

## Problem Statement

High-quality research requires more than finding a few relevant links. A useful research process must frame the question, define evidence standards, discover diverse sources, evaluate credibility, synthesize across claims, expose conflicts, identify blind spots, and preserve provenance so the work can be reviewed later.

Current AI-assisted research workflows are useful but fragile. They often produce fluent reports without enough visibility into how sources were selected, which claims are weak, whether counterevidence was considered, or where the agent made judgment calls. They also tend to be either too interactive, forcing the user to babysit every step, or too autonomous, silently making scope and quality decisions that should be explicit.

The user needs an OpenCode-native research assistant that can run serious research with bounded autonomy: ask for the right brief up front, work in parallel where possible, pause only when a real decision is needed, produce auditable artifacts, and support a true AFK mode when the user wants uninterrupted execution with deferred decisions captured for final review.

## Solution

Build an OpenCode-native agentic research assistant centered on durable research runs. Each research run starts from a structured brief, is represented internally as a dependency graph, uses parallel workers for independent discovery and analysis tasks, and writes all artifacts to a local run folder.

The assistant is invoked with a `/research` command. It supports two checkpoint modes:

1. **Default mode** pauses for meaningful human decisions: material scope expansion, expensive or slow tools, low-confidence evidence, source conflicts that affect the answer, consequential actions, and final sign-off.
2. **AFK mode** is activated with `--afk`. After the initial brief, the assistant does not stop for mid-run research-quality decisions. It may use configured allowlisted tools, continues working around blocked branches, and records unresolved choices in a deferred-decisions artifact for final review.

Research thoroughness is controlled separately with `--depth quick|standard|deep`, so checkpoint policy and research depth do not become tangled.

The assistant produces decision-support-grade Markdown reports: good enough to inform personal or engineering decisions after human spot-checking, but not presented as guaranteed factual truth or formal regulated-domain evidence.

## User Stories

1. As a user, I want to start a research run with `/research <question>`, so that I can begin structured research without manually setting up files or templates.
2. As a user, I want to pass `--depth quick|standard|deep`, so that I can trade off speed, source breadth, recursion depth, and evaluator strictness.
3. As a user, I want to pass `--afk`, so that the assistant can complete the research without stopping for mid-run decisions.
4. As a user, I want default mode to pause only for meaningful decisions, so that I am not interrupted for routine source selection or summarization.
5. As a user, I want `--afk` mode to record deferred decisions instead of interrupting me, so that I can review judgment calls after the run completes.
6. As a user, I want the assistant to ask clarifying questions when the initial brief is incomplete, so that ambiguous research does not start from a poor framing.
7. As a user, I want the assistant to require at least a research question and intended use, so that it can judge whether the final report answers the actual need.
8. As a user, I want to specify scope constraints, source preferences, recency constraints, evidence thresholds, source types, and tool allowlist overrides, so that the run matches the decision I need to make.
9. As a user, I want default source and tool preferences to be configurable, so that trusted read/search tools do not need to be re-approved every run.
10. As a user, I want per-run tool allowlist overrides, so that I can permit or prohibit specific tools for a specific research task.
11. As a user, I want the assistant to support web pages, local files, code repositories, documentation sites, PDFs/papers, and video transcripts where tooling supports them, so that one workflow covers most text-based research needs.
12. As a user, I want social media and private app integrations to be out of scope unless provided as local or exported sources, so that v1 remains focused and reliable.
13. As a user, I want the assistant to represent each run as a dependency graph, so that independent branches can continue while blocked branches wait for approval or are deferred.
14. As a user, I want the assistant to perform source discovery recursively within depth limits, so that it can follow important leads without drifting indefinitely.
15. As a user, I want quick runs to be lightweight, so that I can get an orientation without waiting for deep research.
16. As a user, I want standard runs to include one secondary-source pass and full quality gates, so that the result is useful for normal decision support.
17. As a user, I want deep runs to search more broadly and recurse further, so that complex topics receive broader coverage and stricter evaluation.
18. As a user, I want the assistant to run independent source discovery branches in parallel, so that research completes faster without sacrificing coverage.
19. As a user, I want the assistant to analyze sources in parallel, so that source-level notes can be produced efficiently.
20. As a user, I want the assistant to use parallel evaluator or blindspot passes where useful, so that missing perspectives and weak claims are more likely to be caught.
21. As a user, I want one orchestrator to remain the source of truth for run state, so that parallel workers do not create conflicting versions of the research.
22. As a user, I want every run to produce a durable run folder, so that the work can be audited, resumed, or extended later.
23. As a user, I want each run folder to include the brief, state, source inventory, notes, evaluation, final report, and run log, so that I can inspect both the answer and the process.
24. As a user, I want AFK runs to include a deferred-decisions artifact, so that I can see what would have required a checkpoint in default mode.
25. As a user, I want the assistant to store artifacts locally and write only inside the run folder during execution, so that research runs are predictable and local-first.
26. As a user, I want the assistant to redact secrets from artifacts, so that sensitive tokens or credentials are not accidentally persisted.
27. As a user, I want the assistant to prefer primary, official, standards-based, expert, and well-corroborated sources, so that reports are grounded in higher-quality evidence.
28. As a user, I want the assistant to evaluate each source with a consistent rubric, so that source quality is not judged ad hoc.
29. As a user, I want source inventories to include source type, date, quality, contribution, and limitations, so that I can judge whether the source set is trustworthy.
30. As a user, I want important claims to have claim-level evidence records, so that key conclusions can be traced to specific source support.
31. As a user, I want important claims labeled as corroborated, single-sourced, contradicted, unresolved, or interpretive, so that confidence is explicit.
32. As a user, I want the assistant to cite factual claims in the final report, so that I can spot-check important assertions.
33. As a user, I want the assistant to surface conflicts instead of smoothing them over, so that I can see where evidence disagrees.
34. As a user, I want the assistant to run a blindspot analysis, so that opposing views, recency gaps, missing stakeholders, geographic bias, adjacent domains, and negative results are considered.
35. As a user, I want the assistant to check whether the final report answers the original brief, so that a polished but off-target report is treated as a failure.
36. As a user, I want quality gates to run before finalization, so that missing citations, narrow source diversity, unresolved conflicts, or ignored brief requirements are caught.
37. As a user, I want a final Markdown report with an executive summary, methodology, findings, sources, conflicts, gaps, and next steps, so that the output is useful and auditable.
38. As a user, I want an optional compact summary, so that I can quickly understand the result before reading the full report.
39. As a user, I want run state to be resumable, so that interrupted research does not need to start over.
40. As a user, I want prior run folders to be usable as sources manually, so that I can build on previous research without introducing a complex cross-run cache in v1.
41. As a user, I want external publishing or copying of final reports to require explicit instruction, so that research execution itself stays contained.
42. As a user, I want no autonomous irreversible actions in v1, so that research cannot unexpectedly modify external systems.
43. As a user, I want the assistant to finish with explicit gaps when budgets are exhausted, so that it does not loop indefinitely pretending certainty.
44. As a user, I want the assistant to distinguish checkpoint mode from depth, so that I can run deep research AFK or quick research interactively.
45. As a user, I want the system to be implementation-ready but not over-specified at code level, so that implementation tickets can be created without locking in brittle internals too early.

## Implementation Decisions

### Runtime and Product Boundary

- The assistant is OpenCode-native in v1.
- No standalone UI, daemon, web app, or mobile app is required.
- The design should remain portable at the architectural level, but implementation targets OpenCode workflows and local Markdown artifacts.
- The primary user is a single power user running local research sessions.
- Multi-user collaboration and shared team review workflows are out of scope for v1.

### Command Contract

The v1 invocation contract is:

```text
/research <question> [--depth quick|standard|deep] [--afk] [--sources web,local,repos,docs,papers,video] [--allow-tool <name>] [--disallow-tool <name>] [--out <run-slug>]
```

- `<question>` is required.
- If intended use is missing, the assistant asks for it before execution starts.
- `--depth` defaults to `standard`.
- `--afk` switches checkpoint policy to pure AFK mode.
- `--sources` narrows source classes for the run.
- `--allow-tool` and `--disallow-tool` override persistent defaults for the run.
- `--out` sets the run slug; otherwise the assistant derives a slug from the question.

### Initial Brief

Before execution starts, the assistant captures or infers:

- Research question.
- Decision or use the research will inform.
- Scope constraints and exclusions.
- Source preferences or source distrust.
- Time range and recency constraints.
- Desired output format.
- Depth: quick, standard, or deep.
- Checkpoint mode: default or AFK.
- Tool allowlist overrides.
- Evidence threshold or confidence requirement.

Question and intended use are mandatory. Missing non-critical fields may use defaults, but defaults must be recorded in the brief.

### Checkpoint Modes

Default mode pauses for:

- Material scope expansion.
- High-cost, paid, unusually slow, or unusually broad tool use.
- Source conflicts that materially affect the answer.
- Low-confidence synthesis on important claims.
- Consequential actions.
- Final decision-grade sign-off.

AFK mode:

- Is activated by `--afk`.
- Does not pause for mid-run research-quality decisions after the initial brief.
- May use configured allowlisted tools.
- Continues independent DAG branches when one branch is blocked.
- Records unresolved choices, blocked branches, skipped approvals, and material assumptions in `deferred-decisions.md`.
- Still produces a final report and final review point.

### Depth Budgets

Depth controls research breadth, recursion, evaluator strictness, and rough runtime expectations.

| Depth | Target behavior |
|---|---|
| `quick` | 3-5 sources, no recursive secondary pass, light evaluator pass, suitable for orientation. |
| `standard` | 6-12 sources, one secondary-source pass, full quality gates, suitable for ordinary decision support. |
| `deep` | 12-30 sources, multi-branch recursion, stricter evaluation, broader blindspot search, suitable for complex or higher-stakes decisions. |

Depth budgets are defaults, not guarantees. If a run cannot satisfy quality gates within budget, it finishes with explicit gaps rather than looping indefinitely.

### Stopping Conditions

The assistant stops when:

- The selected depth budget is reached or saturation is detected.
- The brief's subquestions are answered as far as available evidence allows.
- Quality gates pass, or failures are explicitly documented.
- Remaining gaps, unresolved conflicts, and deferred decisions are recorded.

The assistant must not continue indefinitely in search of perfect confidence.

### Run Graph and Parallel Execution

- Each research run is represented as a dependency graph.
- Nodes may represent subquestions, search tasks, source analyses, secondary leads, checkpoint decisions, synthesis sections, evaluator passes, or report generation.
- Node status is persisted so a run can be paused and resumed.
- Independent nodes may run in parallel.
- Blocked nodes do not block unrelated branches.
- One orchestrator owns the canonical run state.
- Parallel workers are used for independent retrieval, per-source analysis, multi-perspective blindspot checks, and evaluator passes.
- Logical agent roles may collapse into a single model/runtime when separate workers do not add value.

### Supported Source Types

V1 explicitly supports:

- Web pages.
- Local files.
- Code repositories.
- Documentation sites via Context7 or equivalent documentation tooling.
- PDFs and papers when available through configured tools.
- Video transcripts when available through configured tools.

Out of scope unless supplied as local/exported sources:

- Social media platforms.
- Private note apps.
- Chat platforms.
- Ticketing systems.
- Cloud drives.
- Databases.

### Tool Registry and Allowlist

- The assistant maintains persistent default tool allowances.
- A run may add or remove allowed tools through command flags or brief fields.
- AFK mode may use configured allowlisted tools without interrupting the user.
- Tool metadata should identify whether a tool is read-only, writes externally, may incur cost, may be slow, or may expose private data.
- Tools that are disallowed or unavailable produce blocked or skipped branch notes, not silent omissions.

### Run Artifacts

Each run writes to a local run folder. The default location is a research-run folder under the docs research area, using a slug derived from the question or `--out`.

Every run folder contains:

- `brief.md` — normalized brief, defaults, flags, assumptions, source scope, and tool policy.
- `state.json` — machine-readable run graph, node statuses, dependencies, checkpoint state, and artifact references.
- `source-inventory.md` — sources consulted, source type, date, quality rating, contribution, and limitations.
- `notes/` — source-level notes and extracted evidence.
- `evaluation.md` — quality gate results, evaluator findings, and unresolved quality issues.
- `final-report.md` — final user-facing report.
- `run-log.md` — human-readable timeline of major steps, tool use summaries, checkpoints, and completion status.
- `deferred-decisions.md` — only required for AFK runs; records choices that would have triggered checkpoints in default mode.

Research execution writes only to the run folder. Copying or publishing a final report elsewhere requires explicit user instruction.

### Evidence Model

- The system records source-level notes for every analyzed source.
- Important findings and recommendations receive claim-level evidence records.
- Claim-level evidence records include source IDs, direct quotes or precise paraphrases, quality rating, support status, and confidence label.
- Confidence labels include: corroborated, single-sourced, contradicted, unresolved, and interpretive.
- A full sentence-level claim graph is out of scope for v1.

### Quality Gates

Before finalization, the assistant evaluates:

- Whether the final report answers the original brief.
- Source diversity against the selected depth and source scope.
- Citation coverage for key claims.
- Recency where the topic requires current information.
- Material conflicts and unresolved contradictions.
- Blindspots: opposing views, recency gaps, practitioner vs. theoretical balance, geographic or cultural variation, adjacent domains, negative results, and stakeholder perspectives.
- Evaluator score or evaluator failure note.

Quality gate failure does not necessarily prevent report generation, but failures must be visible in `evaluation.md` and reflected in the final report's confidence and gaps.

### Final Report Structure

The final report uses the existing research-report structure:

- Executive Summary.
- Research Question and Scope.
- Methodology.
- Key Findings.
- Source Inventory.
- Conflicts and Open Questions.
- Blindspot / Gap Analysis.
- Recommendations and Next Steps.

AFK reports also include a Deferred Decisions section or link to the deferred-decisions artifact.

### Core Modules

**1. Research Brief**

Parses command flags and conversational answers into a normalized brief. Applies defaults and records assumptions.

**2. Run Graph / State Store**

Maintains the dependency graph, node status, checkpoint status, artifact references, and resumability contract.

**3. Source Discovery**

Generates subqueries, selects source classes, runs searches, follows secondary leads within depth limits, and creates source-analysis nodes.

**4. Source Analyzer**

Extracts claims, evidence, source metadata, quality notes, limitations, and secondary leads from each source.

**5. Evidence Store**

Stores source-level notes and key-claim evidence records. Supports confidence labeling and citation lookup.

**6. Synthesis Engine**

Groups findings by theme or subquestion, separates evidence from interpretation, identifies conflicts, and drafts report sections.

**7. Evaluator**

Runs quality gates, checks brief coverage, flags unsupported claims, reviews source diversity, and performs blindspot analysis.

**8. Checkpoint Manager**

Applies mode-specific checkpoint policy. In default mode, it pauses for required decisions. In AFK mode, it records deferred decisions and continues other branches.

**9. Report Generator**

Produces final Markdown reports, compact summaries, source inventories, evaluation summaries, and AFK deferred-decision summaries.

**10. Tool Registry**

Tracks tool capabilities, risk level, cost/latency expectations, source classes, privacy implications, and allowlist state.

### Logical Agent Roles

The PRD defines logical roles, not mandatory separate processes:

- Planner.
- Retriever.
- Source Analyst.
- Synthesizer.
- Critic.
- Reporter.

Implementations may collapse roles into one runtime or model when simpler. Parallel workers should be used only where independent work units justify the coordination overhead.

### Privacy and Security

- The system is local-first.
- Run artifacts are stored locally.
- Research execution writes only inside the run folder.
- Secrets must be redacted from artifacts.
- Private/local content should not be sent to external tools unless the selected model/tool requires it and the brief or tool policy allows it.
- No autonomous irreversible external actions are allowed in v1.

### Resume Behavior

- Runs can be resumed from `state.json`.
- Completed nodes are not repeated unless explicitly invalidated.
- Blocked nodes retain their reason and dependencies.
- AFK deferred decisions can be reviewed after completion and used to launch a follow-up run.
- Cross-run source caching and a persistent knowledge base are out of scope for v1.

## Testing Decisions

Tests should verify externally observable behavior through stable module interfaces. They should avoid asserting incidental implementation details or exact model wording. External search, fetch, and documentation tools should be mocked at the boundary.

Modules to test:

- **Research Brief** — parses command flags, applies defaults, requires question and intended use, records assumptions, handles allow/disallow tool overrides.
- **Run Graph / State Store** — creates dependency nodes, tracks status transitions, blocks only dependent branches, resumes from persisted state, and preserves completed work.
- **Tool Registry** — applies default allowlists, per-run overrides, source-class filtering, and AFK tool policy.
- **Source Analyzer** — normalizes source metadata, extracts source-level notes, records quality ratings, and emits secondary leads.
- **Evidence Store** — stores key-claim evidence records, links claims to source IDs, and preserves confidence labels.
- **Checkpoint Manager** — pauses in default mode for required events and records deferred decisions in AFK mode without stopping the run.
- **Evaluator / Quality Gates** — detects missing brief coverage, insufficient source diversity, missing citations on key claims, unresolved conflicts, recency gaps, and blindspot omissions.
- **Report Generator** — produces the required Markdown sections, includes source inventory and evaluation results, and adds AFK deferred-decision content when applicable.

Acceptance demo:

1. Run `/research "best practices for a known topic" --depth standard`.
2. Run `/research "best practices for a known topic" --depth standard --afk`.
3. Verify both runs create complete run folders.
4. Verify both runs persist graph state and source inventory.
5. Verify default mode creates checkpoints for material decisions.
6. Verify AFK mode does not stop mid-run and records deferred decisions instead.
7. Verify both final reports use the required template.
8. Verify quality gates include whether the brief was answered.
9. Verify no files outside the run folder are written during execution.

## Out of Scope

- Standalone web UI, desktop UI, mobile app, or daemon.
- Multi-user collaboration, team review workflows, permissions, or shared workspaces.
- External publishing integrations such as GitHub issues, Confluence, Notion, or ticketing systems.
- Persistent cross-run knowledge base or vector memory.
- Cross-run source cache with invalidation logic.
- Formal systematic-review workflows for regulated domains.
- Domain-specific legal, medical, financial, or compliance guarantees.
- Guaranteed factual correctness.
- Autonomous irreversible external actions.
- Full sentence-level claim graph for every factual statement.
- Social media and private SaaS connectors unless sources are provided as local/exported files.
- PDF, HTML, slide, or briefing-doc export beyond Markdown and compact summary.

## Further Notes

- The core product value is not maximum autonomy. It is reliable research method at scale: explicit framing, diverse retrieval, source-quality scoring, grounded synthesis, conflict handling, gap analysis, durable logs, and well-placed checkpoints.
- `--afk` should not mean lower-quality research. It means fewer interruptions. The cost is that unresolved judgment calls move to final review instead of being resolved mid-run.
- Depth and checkpoint policy must remain separate. A deep AFK run and a quick default-mode run are both valid.
- Parallelism should follow the DAG. Do not create separate agents simply because the design has logical roles.
- The assistant should prefer finishing with explicit gaps over fabricating confidence or expanding the run indefinitely.
