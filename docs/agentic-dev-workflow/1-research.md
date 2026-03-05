---
generated: 2026-03-05
research_depth: "primary + approved secondary (6 additional sources)"
notebooklm_notebook: https://notebooklm.google.com/notebook/d6aebae5-247f-49f1-a2ec-f18b7b53ff5b
artifact_briefing_doc: notebooklm-briefing.md
---

# Research Report: Effective and Shareable Agentic Development Workflows

## Table of Contents

1. [Research Question & Scope](#1-research-question--scope)
2. [Methodology](#2-methodology)
3. [Artefacts](#3-artefacts)
4. [Key Findings](#4-key-findings)
5. [Source Inventory](#5-source-inventory)
6. [Conflicts & Open Questions](#6-conflicts--open-questions)
7. [Blindspot / Gap Analysis](#7-blindspot--gap-analysis)
8. [Recommended Next Steps](#8-recommended-next-steps)

---

## 1. Research Question & Scope

```
Research question: What makes an agentic development workflow effective and
  efficient? How can such a workflow be structured, documented, and made
  shareable and consistent across a team? What is the proper format for a
  shareable workflow that can be plugged into existing agentic systems
  (via skills, templates, or similar)?

Scope constraints:
  - Time range: 2025–2026 only
  - Source types: practitioner videos/talks, blog posts/articles, official
    docs/frameworks, academic papers, GitHub repositories
  - Domain: software engineering workflows, not general AI/ML research

Out of scope:
  - Pre-2025 literature (foundational papers referenced only if cited by
    in-scope sources)
  - General enterprise AI strategy without workflow-specific implications
  - Non-software agentic applications (robotics, autonomous vehicles, etc.)
```

---

## 2. Methodology

- **Resource types consulted:** YouTube video, arXiv papers, practitioner blog posts, official framework docs (Azure, OpenAI, LangGraph, CrewAI, GitHub), Reddit practitioner threads, industry analyst reports (Anthropic, Deloitte, IBM), GitHub repositories
- **Search strategy:** NLM deep research agent queried ~43 web sources; direct arXiv URL fetching for key papers; five RAG synthesis queries against the full corpus; seven gap-retrospective queries; two topic-specific queries on shareability formats and real-world evidence
- **Depth:** Primary sources + approved secondary leads (6 additional sources approved mid-session)
- **Secondary sources approved by user:** Yes — SkillFortify paper (arXiv:2603.00195), GitHub Agentic Workflows docs, Reddit practitioner thread, ACP Agent Registry, Agent Skills Directory (skills.sh), OpenAI Routines & Handoffs doc
- **Tools used:** NotebookLM RAG (notebook ID [`d6aebae5-247f-49f1-a2ec-f18b7b53ff5b`](https://notebooklm.google.com/notebook/d6aebae5-247f-49f1-a2ec-f18b7b53ff5b)), WebFetch, Read, Bash (NLM CLI), five saved synthesis notes + session history note
- **NotebookLM briefing doc (Artifact A):** `notebooklm-briefing.md` [S-NLM]

---

## 3. Artefacts

Generated from the NotebookLM notebook as part of this research session.

| File | Description |
|------|-------------|
| [`notebooklm-briefing.md`](sources/notebooklm-briefing.md) | NLM-generated briefing doc; used as source `[S-NLM]` throughout this report |
| [`infographic.png`](sources/infographic.png) | Visual summary: Enterprise Agentic AI 2026 Overview |
| [`slide-deck.pdf`](sources/slide-deck.pdf) | Presentation: The Agentic Enterprise Playbook |
| [Effective Agentic Workflows](https://notebooklm.google.com/notebook/d6aebae5-247f-49f1-a2ec-f18b7b53ff5b?artifactId=07e7f166-e294-4810-a59e-c4cdbd7b50d9) | Short explainer: Effective Agentic Workflows (~5 min) |

---

## 4. Key Findings

### 3.1 The Paradigm Shift: SE 3.0 and the ADLC

Software engineering is entering a third era: **SE 3.0** — Agentic Software Engineering [S1, S2]. The progression:

- **SE 1.0:** Human-written code
- **SE 2.0:** AI-assisted development (Copilot-style autocomplete)
- **SE 3.0:** Agents execute tasks; humans act as "Agent Coaches" who specify intent, define constraints, and curate context [S1, S4, S-NLM]

The traditional SDLC is being replaced by the **Agentic Development Lifecycle (ADLC)**, which requires *continuous context propagation* across phases so that agents do not lose architectural rationale during handoffs [S1, S8]. The most concretely documented version is the **7-phase AI-driven development workflow** [S3]:

1. **Idea** — Define the core feature, bug fix, or refactor
2. **Research** — Explore the repo or external APIs; cache findings in `research.md`
3. **Prototype** — Use throwaway routes to iterate on UI/UX and architecture
4. **PRD** — Formally describe end-state and acceptance logic
5. **Implementation Plan (Kanban)** — Break the PRD into tickets with blocking relationships
6. **Execution Loop** — Run a coding agent (AFK loop) to execute tickets
7. **QA Plan** — Agent produces a plan for human-in-the-loop verification

This 7-phase model is corroborated in structure (if not exactly in naming) by the SASE paper [S1], EPAM's ADLC article [S8], and HMH Engineering's roadmap [S9].

### 3.2 Architecture: Specialization Over Monoliths

All practitioner and academic sources converge on one structural principle: **avoid monolithic "kitchen-sink" agents** [S1, S4, S10, S-NLM].

Giving a single agent too many tools forces the LLM to spend context reasoning about tool selection, increasing hallucination risk. The four canonical multi-agent topologies are [S10, S11, S12]:

| Topology | Best for | Trade-off |
|---|---|---|
| **Sequential pipeline** | Predictable, high-quality processes | Slowest; no parallelism |
| **Parallel/concurrent** | Independent subtasks needing fast turnaround | Aggregation complexity |
| **Orchestrator-worker** | Complex goals with decomposable sub-tasks | Manager agent is a bottleneck |
| **Swarm/decentralised** | Open-ended exploration and debate | Least predictable; hardest to audit |

Complementary to this: tasks that don't require language reasoning (GitHub commits, DB writes, API calls) should use **direct deterministic function calls**, not LLM-mediated tool calls [S1, S4]. This reduces token burn and eliminates ambiguous parameter formatting.

### 3.3 Workflow Documentation: The Four Artifact Types

Effective agentic workflows require four categories of documented artifact [S1, S4, S5, S13, S-NLM]:

**1. Specification artifacts (pre-execution)**
- **BriefingScript / PRP (Product Requirement Prompt):** A machine-readable work order with goal, architectural context, potential pitfalls, and a testable "Definition of Done" [S1, S4]. Replaces vague tickets.
- **LoopScript:** A declarative playbook defining task decomposition, Standard Operating Procedures, parallelisation rules, and mandatory review checkpoints [S1].

**2. Knowledge artifacts (persistent)**
- **Agent Skills (`SKILL.md`):** Version-controlled directory containing YAML frontmatter (metadata) + Markdown instructions + supplementary scripts/references/assets. Loaded on demand via *progressive disclosure* (brief summary first, full doc only when triggered) [S5, S13, S14].
- **Meta-prompt files (`AGENTS.md`, `CLAUDE.md`, `.clinerules`):** Repo-root files that codify project norms, coding style, and architectural principles. Agents read these before beginning tasks [S5, S13].
- **MentorScript:** Captures human reviewer corrections as durable norms so agents don't repeat mistakes [S1].

**3. Evidence artifacts (post-execution)**
- **Merge-Readiness Pack (MRP):** A bundled proof of completion: functional correctness, test verification, hygiene checks (linting, DRY), and full audit trail. Submitted by the agent for human review [S1].
- **Consultation Request Pack (CRP):** A formal escalation artifact when an agent hits a blocker — documents the specific uncertainty and routes it to the appropriate human specialist [S1].

**4. Observability artifacts (continuous)**
- **Execution traces:** Every tool call, intermediate reasoning step, and chain-of-thought — captured for debugging, rollback, and LLM-as-a-Judge evaluation [S4, S15].
- **Versioned prompts:** Prompts stored as immutable YAML/JSON artifacts in Git, deployed via CI/CD, with rollback capability [S13, S16].

### 3.4 The Canonical Shareable Format: Agent Skills

The most widely corroborated format for sharing workflows across teams and tools is the **Agent Skill** [S5, S13, S14, S17, S18]:

```
.agents/skills/<skill-name>/
├── SKILL.md          # YAML frontmatter + Markdown instructions (required)
├── scripts/          # Deterministic helper code
├── references/       # Domain docs loaded on demand
└── assets/           # Templates, boilerplate, brand assets
```

The `SKILL.md` frontmatter structure:
```yaml
---
name: skill-name
description: >
  What this skill does and when to trigger it. Includes specific phrases
  and contexts that signal the agent to load this skill.
---
```

**Why this format works:**
- **Progressive disclosure** conserves token budget: agents receive ~100-token summaries initially; full instructions load only on match [S5, S13]
- **Cross-platform portability:** Works across Claude Code, GitHub Copilot, Cursor, and Microsoft Semantic Kernel [S13, S17]
- **Version control native:** Directory structure is Git-friendly; skills evolve like code [S13]
- **Composable:** Skills can reference other skills or shared `references/` files [S5]

Standard storage locations: `.github/skills/`, `.claude/skills/`, `.agents/skills/` [S13, S5].

### 3.5 Team-Scale Sharing: Three Tiers

Sharing mechanisms exist at three scales [S13, S19, S20, S-NLM]:

**Tier 1 — Repository level (small teams, low friction):**
`AGENTS.md` / `CLAUDE.md` at repo root. Read by all agents before starting tasks. Contains project-specific rules, architectural principles, and coding standards. Simple text file, no tooling required.

**Tier 2 — Organisation level (medium teams):**
Internal skill library in a shared Git repo (e.g., `github.com/org/agent-skills`). Skills versioned independently; agents pull from the library. Prompt registries (Langfuse, Maxim AI, PromptLayer, Humanloop) for prompt versioning with A/B testing and rollback [S16, S21].

**Tier 3 — Enterprise / cross-org (large teams):**
AI Agent Registries that function as an authoritative system of record. Each registered "Agent Card" declares: unique identity, business owner, tool allow-list, required evidence outputs, lifecycle state [S19, S20, S22].

Three registry architectures exist (Conflicting evidence: see Section 5):
- **Centralised:** MCP Registry — `mcp.json` files, GitHub OAuth, single metaregistry [S19]
- **Decentralised:** A2A Agent Cards — `/.well-known/agent.json`, self-hosted JSON [S20]
- **Federated/cryptographic:** NANDA Index — W3C Verifiable Credentials, cryptographically signed AgentFacts [S22]

### 3.6 Economics: The Unreliability Tax

Multi-turn agentic loops introduce **quadratic token cost growth**: a 10-cycle loop can cost 50× more than a single pass, because each turn re-sends the full context history [S23, S24, S-NLM].

Mitigations:
- **Routing:** Classify task complexity; route cheap tasks to fast/small models; reserve frontier models for reasoning [S4, S24]
- **Prompt caching:** Reuse processed system instructions; can cut input costs by up to 90% [S23, S-NLM]
- **Persistent memory:** Vector stores for successful plans reduce re-planning overhead [S4, S23]
- **Turn limits:** Hard circuit breakers to halt runaway loops [S1, S4]

Real-world signal: 95% of enterprise AI pilots fail [S25]; the "AI slop" crisis (low-quality auto-generated code creating a denial-of-service on maintainer attention) is an emerging production risk [S26].

### 3.7 Security: Skills as a Supply Chain Attack Vector

Skills represent a new software supply chain risk. SkillFortify [S27] (Feb 2026) found:
- **26.1% of published agent skills** contain at least one exploitable vulnerability
- The **ClawHavoc campaign** (Jan–Feb 2026) infiltrated 1,200+ malicious skills into public marketplaces
- Attack vectors: prompt injection, arbitrary code execution, data exfiltration via tool misuse

Implications for workflow design:
- Vet third-party skills before adding to internal libraries
- Apply RBAC to skill execution (agents should not self-grant new tool permissions)
- Implement capability-based sandboxing (SASE's formal model) for production environments [S1, S27]

### 3.8 Real-World Validation

Production deployments confirm the workflow patterns described above work at scale [S28, S-NLM]:

| Organisation | Outcome |
|---|---|
| Rakuten | 12.5M-line codebase; complex feature implemented in 7 hours at 99.9% numerical accuracy |
| CRED | 2× execution speed; developers shifted to strategic work |
| Klarna | LangGraph customer support agent handles ⅔ of all inquiries; equivalent to 853 FTEs; $60M saved |
| Replit | Agent task success rate 80% → 96% across thousands of daily sessions (Mastra framework) |
| Augment Code | 4–8 month onboarding estimate completed in 2 weeks |
| Anthropic Legal | Contract review turnaround 2–3 days → 24 hours |

Common pattern across all successful deployments: **process redesign ("agent-native"), not "paving the cow path"** [S28, S-NLM]. Simply bolting agents onto legacy human processes consistently fails.

---

## 5. Source Inventory

| ID | Source | Type | Date | Quality | Notes |
|----|--------|------|------|---------|-------|
| S1 | [arXiv:2509.06216] Agentic Software Engineering: Foundational Pillars and a Research Roadmap (Queen's U / Huawei / Concordia / NAIST) | Academic | 2025-09 | **High** — peer-reviewed, multi-institution, extensively cited | Introduced SASE framework: BriefingScript, LoopScript, MentorScript, MRP, CRP, ACE, AEE |
| S2 | Software Engineering 3.0: Intent-Driven Paradigm — Emergent Mind | Web | 2025 | **Medium** — practitioner blog, corroborated by S1 | Frames SE 1.0/2.0/3.0 taxonomy |
| S3 | The 7 Phases of AI-Driven Development — Matt Pocock (YouTube) | Video | 2025 | **Medium-High** — experienced practitioner, widely shared | Primary seed source; 7-phase workflow |
| S4 | Top AI Agentic Workflow Patterns Enterprises Should Use in 2026 — Dextra Labs | Web | 2026 | **Medium** — practitioner guide, no peer review, corroborated | Canonical patterns; KISS principle; direct function calls |
| S5 | Agent Skills Directory — skills.sh | Web | 2026 | **Medium** — marketplace listing, limited methodology | Format reference for skill directory structure |
| S6 | Formal Analysis and Supply Chain Security for Agentic AI Skills — arXiv:2603.00195 (SkillFortify) | Academic | 2026-02 | **Medium-High** — formal methods, independent authors, recency unverified | 26.1% vulnerability rate; ClawHavoc campaign |
| S7 | Automate Repository Tasks with GitHub Agentic Workflows — GitHub Docs | Web | 2026 | **High** — official vendor documentation | GitHub's YAML+Markdown workflow format; permissions model |
| S8 | Introducing Agentic Development Lifecycle (ADLC) — EPAM | Web | 2025 | **Medium** — consulting firm, no peer review | ADLC phases; context propagation |
| S9 | A Roadmap for the Future of Agentic Software Development — HMH Engineering | Web | 2025 | **Medium** — practitioner blog, small shop | Corroborates 7-phase structure independently |
| S10 | AI Agent Orchestration Patterns — Azure Architecture Center | Web | 2025 | **High** — official Microsoft docs, well-maintained | Sequential, parallel, orchestrator-worker patterns |
| S11 | Building Agentic Workflows with LangGraph and Granite — IBM | Web | 2025 | **Medium-High** — official IBM docs | LangGraph state management; cyclic graphs |
| S12 | Multi-Agent Architectures — Swarms | Web | 2025 | **Medium** — framework docs | Swarm/decentralised topology |
| S13 | How to Write and Implement Agent Skills — DigitalOcean | Web | 2025 | **Medium** — editorial quality, corroborated | Skill directory format; YAML frontmatter; progressive disclosure |
| S14 | Agent Skills — Microsoft Learn / Semantic Kernel | Web | 2025 | **High** — official Microsoft docs | Cross-platform skills portability |
| S15 | Different Evals for Agentic AI: Methods, Metrics & Best Practices — testRigor | Web | 2025 | **Medium** — vendor blog, methodology not specified | LLM-as-a-Judge; task success rate; hallucination rate KPIs |
| S16 | Best Prompt Management Tools for Teams (2025) — Fast.io | Web | 2025 | **Medium** — vendor review, possible bias | Langfuse, Maxim AI, PromptLayer comparison |
| S17 | Give Your Agents Domain Expertise with Agent Skills — Microsoft / Semantic Kernel | Web | 2025 | **High** — official Microsoft docs | Cross-platform portability confirmed |
| S18 | Why Agent Skills Matter for Your Organization — (vendor article) | Web | 2025 | **Medium** — vendor marketing, some corroboration | Business case for skills libraries |
| S19 | Enterprise AI Agent Registry: The Missing System of Record — (industry blog) | Web | 2025 | **Medium** — practitioner-level, no peer review | Registry as system of record pattern |
| S20 | Orchestrating Agents: Routines and Handoffs — OpenAI for Developers | Web | 2025 | **High** — official OpenAI docs | A2A handoff protocol; agent cards |
| S21 | Top 5 Prompt Versioning Tools in 2025 — (industry blog) | Web | 2025 | **Medium** — no author, comparison format | Prompt registry platforms: Git integration |
| S22 | Evolution of AI Agent Registry Solutions: Centralized, Enterprise, and Distributed — arXiv | Academic | 2025 | **Medium-High** — arXiv preprint, not peer-reviewed at time of sourcing | NANDA Index; AgentFacts; W3C VCs |
| S23 | The Hidden Economics of AI Agents: Managing Token Costs and Latency Trade-offs | Web | 2025 | **Medium** — practitioner blog, corroborated | Quadratic cost growth; prompt caching |
| S24 | Agentic AI Cost Management: Stopping Margin Erosion — (industry article) | Web | 2026 | **Medium** — vendor, some corroboration | Routing; thinking budget |
| S25 | Agentic AI Market Outlook 2025–2026 — Statistics on Adoption, ROI, and Growth | Web | 2025 | **Low-Medium** — aggregated statistics, sources not all primary | 95% pilot failure rate; adoption metrics |
| S26 | GitHub's Points to a More Global, AI-Challenged Open Source Ecosystem in 2026 — InfoQ | Web | 2026 | **Medium-High** — InfoQ editorial quality | "AI slop" crisis; maintainer bottleneck |
| S27 | [arXiv:2603.00195] SkillFortify: Formal Analysis and Supply Chain Security for Agentic AI Skills | Academic | 2026-02 | **Medium-High** — formal methods; recency requires verification | 26.1% vulnerability; ClawHavoc; SAT-based dependency verification |
| S28 | 2026 Agentic Coding Trends Report — Anthropic (PDF) | Report | 2026 | **High** — first-party vendor data, case studies with named orgs | Rakuten, CRED, Augment Code case studies |
| S29 | How do you standardize AI agent development for a whole engineering team? — Reddit | Web | 2025 | **Medium** — unverified practitioners, diverse perspectives | Thin reference architecture; avoid LangChain; observability-first |
| S30 | The Agentic Software Development Life Cycle (A-SDLC) — (industry blog) | Web | 2025 | **Medium** — practitioner, corroborated | ADLC phase model comparison |
| S31 | LangGraph vs CrewAI — ZenML Blog | Web | 2025 | **Medium** — vendor-adjacent, technically sound | Framework trade-off analysis |
| S32 | The Agentic Reality Check: Preparing for a Silicon-Based Workforce — Deloitte | Web | 2025 | **High** — major consultancy, primary research | HR for agents; Moderna org restructure |
| S33 | ACP Agent Registry Is Live — JetBrains IDE | Web | 2026 | **Medium-High** — official JetBrains blog | ACP registry; IDE-integrated agent discovery |
| S34 | Agentic AI Evaluation Metrics — (industry article) | Web | 2025 | **Medium** — no peer review, corroborated | Task Success Rate; Tool Selection Accuracy KPIs |
| S35 | How Agentic AI Reimagines User Journeys — UXmatters | Web | 2025 | **Medium** — UX-focused, adjacent domain | Human-in-the-loop checkpoint design |
| S36 | Toward Agentic Software Engineering Beyond Code — arXiv | Academic | 2025 | **Medium** — arXiv preprint | Vision, values, vocabulary framing |
| S37 | Agentic AI in Software Development: Accelerating Modern Delivery | Web | 2025 | **Medium** — consulting-adjacent, corroborated | SE lifecycle phases |
| S38 | Top Use Cases of Agentic AI in 2026 Across Industries — TechAhead | Web | 2026 | **Medium** — vendor blog | Enterprise case studies cross-industry |
| S39 | From SDLC to Agentic SDLC — (blog) | Web | 2025 | **Medium** — practitioner, no peer review | SDLC → ADLC transition |
| S40 | Version Control Best Practices for AI Code — Ranger | Web | 2025 | **Medium** — practitioner guide | Prompt versioning; Git integration |
| S41 | Choose a Design Pattern for Your Agentic AI System — Google Cloud Architecture Center | Web | 2025 | **High** — official Google docs | Pattern taxonomy; trade-offs |
| S-NLM | NotebookLM Briefing Doc: The Future of Agentic AI — Artifact A (local file) | Local file | 2026-03 | **High** — synthesised from 43 sources, cross-referenced | All themes, case studies, quotes; base synthesis doc |

*Notes: Three sources returned errors (two Medium articles, one Towards Data Science article) and two sources were found to be off-topic (arXiv papers on physics/ML unrelated to agentic workflows). These are excluded from the analysis.*

---

## 6. Conflicts & Open Questions

**Conflict 1 — Orchestration philosophy: deterministic vs. dynamic**
[S1] (SASE) and [S10] (Azure) argue control flow should be explicit and hardcoded in `LoopScript`-style declarative files for predictability and safety. [S4] (Dextra Labs) and practitioner sources favour "magentic" dynamic orchestration where an LLM-powered manager autonomously formulates plans and adapts on the fly. Neither source is clearly more authoritative for all contexts: deterministic approaches excel for compliance-critical workflows; dynamic approaches excel for open-ended exploration. The practical resolution used by most production deployments is **hybrid**: static orchestration for core pipelines, dynamic routing for triage and classification sub-tasks.

**Conflict 2 — Framework choice: heavy vs. lightweight**
[S11, S31] advocate LangGraph for enterprise production (stable APIs, stateful branching, time-travel debugging) and CrewAI for rapid role-based prototyping. [S29] (Reddit practitioners) explicitly warn against LangChain/LangGraph abstractions as "brittle" and argue for simple API wrappers and custom JSON state. Both positions have merit at different scales; the community appears to be converging toward "start lightweight, introduce frameworks only when observability and stateful branching become necessary."

**Conflict 3 — Registry architecture: centralised vs. decentralised vs. federated**
[S19] (MCP) favours centralised metaregistry for governance simplicity. [S20] (A2A/OpenAI) favours decentralised self-hosted agent cards. [S22] (NANDA) proposes federated cryptographic AgentFacts. These are not mutually exclusive technically, but they imply very different trust models and governance overhead. No clear winner has emerged as of Q1 2026.

**Conflict 4 — Development philosophy: formal engineering vs. "start messy"**
[S1, S6] (SASE, SkillFortify) argue for mathematical guarantees, upfront BriefingScripts, and capability-based sandboxing. [S29] and some practitioner sources suggest over-planning is detrimental and advocate shipping quickly then iterating. [S6] explicitly criticises the "start messy" approach as a security liability for autonomous agents. This is a genuine unresolved tension; the appropriate position depends on deployment risk level.

**Unresolved — Skills marketplace security at scale**
[S6] documents ClawHavoc (1,200+ malicious skills) but provides limited guidance on detection tooling or secure supply chain practices beyond general sandboxing recommendations. This is an active research gap.

**Unresolved — Longitudinal ROI evidence**
Most case studies ([S28, S-NLM]) are from 2025–2026 pilots. Long-term ROI data (beyond 12 months) does not yet exist in the literature.

---

## 7. Blindspot / Gap Analysis

- [x] **Opposing view** — Well represented: 95% pilot failure rate, "AI slop" crisis, quadratic cost growth, supply chain attacks, maintainer burnout all documented. [S25, S26, S6, S23]

- [x] **Recency** — Covered: sources span Jan 2025–Mar 2026. SkillFortify (Feb 2026) and ACP registry (2026) represent the most recent developments. Minor gap: skills.sh marketplace evolution post-launch and ACP registry adoption metrics not yet available.

- [~] **Practitioner vs. theoretical** — Partially covered: academic/enterprise perspective well-represented (SASE, Deloitte, Anthropic, Azure, Google, IBM). Small-team practitioner perspective is underrepresented; Reddit thread [S29] is the primary source. **Gap: independent developer and small open-source team workflows are not well-documented in the literature.**

- [ ] **Geographic / cultural variation** — Not covered. All sources are US/Western European. **Gap: how agentic workflow practices differ in Global South contexts (India, Brazil, Southeast Asia) where significant engineering talent operates is entirely absent.** This matters because skills library design assumptions (tooling costs, connectivity, LLM API access) may not hold universally.

- [x] **Adjacent domains** — Several identified: platform engineering (skills-as-infrastructure), Agile/RE methods (user stories as BriefingScript precursors), cognitive science (human-in-the-loop checkpoints), knowledge management (MentorScript), FinOps (token cost management), HR (silicon workforce framing). Most are noted in the literature but not deeply explored.

- [x] **Negative results** — Documented: LangChain brittleness warnings, 95% pilot failure, "paving the cow path" anti-pattern, monolithic agent failures, over-engineering anti-pattern all present [S29, S25, S28, S4].

- [ ] **Stakeholder perspectives** — Partially covered. **Gap: junior developers (who will execute within these workflows) are not represented as research subjects.** Open-source maintainers who must review AI-generated PRs are mentioned [S26] but not interviewed. End users of software built by agents are entirely absent.

---

## 8. Recommended Next Steps

1. **Design your skill library structure now.** The evidence strongly converges on `SKILL.md` + directory as the correct atomic unit for shareable workflows. Use the structure from [S5, S13]: `.agents/skills/<skill-name>/SKILL.md` with YAML frontmatter (`name`, `description`) and Markdown instructions. Start with 2–3 skills that codify the highest-frequency repeated tasks your team faces.

2. **Add an `AGENTS.md` to every repository immediately.** This is the zero-friction starting point for team-wide consistency. Document: architectural principles agents must not violate, coding style decisions, tool allow-list, how to escalate. Agents read this before starting; teams update it like a living document.

3. **Adopt the 7-phase workflow as your team ADLC baseline [S3].** Start with a lightweight version: enforce a `research.md` caching step (Phase 2) and a `QA plan` step (Phase 7). These two phases are most commonly skipped and most correlated with poor output quality.

4. **Implement observability before you scale.** Reddit practitioners [S29] and multiple enterprise sources agree: "start with tracing, not features." Langfuse or Helicone as your first infrastructure investment gives you execution traces, cost visibility, and LLM-as-a-Judge eval capability from day one.

5. **Read the full SASE paper [S1] before committing to a governance model.** The BriefingScript → LoopScript → MRP → CRP artifact chain is the most formally specified end-to-end workflow in the literature. Even if you don't adopt it wholesale, its vocabulary and the reasoning behind each artifact will sharpen your own design decisions.

6. **Do not adopt a skills marketplace dependency without vetting it against SkillFortify [S6].** Before pulling third-party skills (from skills.sh or similar), review them for prompt injection vectors and over-broad tool permissions. The 26.1% vulnerability rate is not theoretical.

7. **Run a follow-up research pass on small-team practitioner workflows (2025–2026).** This session's gap analysis identified this as the most significant blind spot. Search specifically for indie developers, OSS maintainers, and teams under 10 people describing their agentic workflow practices — the enterprise-heavy literature may not translate directly to your context.

8. **Revisit registry architecture decisions in Q3 2026.** The MCP / A2A / NANDA landscape is actively evolving and no clear standard has emerged. Avoid committing to a single registry format for cross-org sharing before there is clearer convergence.

---

*Report generated: 2026-03-05 — see frontmatter for full metadata.*
