---
name: research
description: >
  Structured research support: finding and analysing resources, answering questions from
  evidence, covering angles the user may have missed, and producing a documented research
  report. Use when the user asks to "research X", "find information about Y", "investigate Z",
  "do a literature review", "compare options", "analyse sources on", or any task that involves
  gathering, evaluating, and synthesising information from multiple sources. Also triggers on
  requests like "what do we know about X", "help me understand Y", or "find resources on Z".
  Supports web pages, local files, academic papers, code repositories, and video content.
---

# Research

A structured workflow for finding, evaluating, and synthesising information — with proactive
gap analysis and a documented output report.

## Workflow

Execute these steps in order. Steps 1 and 5 involve user interaction; do not skip them.

### Step 1 — Intake & framing

Before searching for anything, probe the user's framing to surface assumptions and gaps.
Ask only the questions that are genuinely unclear; don't ask about things already stated.

Core intake questions (adapt as needed):

```
1. What is the specific question or decision this research is meant to inform?
2. Are there particular source types you trust or distrust for this topic?
   (e.g. "academic only", "no Wikipedia", "include grey literature")
3. Any time range constraints? (e.g. "post-2022 only")
4. Any geographic or domain scope constraints?
5. How will you use the output? (Quick orientation / decision support / formal report / other)
6. Are there specific angles, viewpoints, or stakeholders you already know you want covered?
7. [Dynamic — see below]
```

**Question 7 — Plugin activation (generic):**

Before asking Q7, load `references/plugins/INDEX.md` to get the current plugin list.
Build Q7 from the index entries, listing each plugin with its user-facing description and
prerequisites. Example rendering (adapt to actual index contents):

```
7. Would you like to activate any integrations for this session?

   Available:
   • NotebookLM — Google NotebookLM: indexes all sources and answers cross-source
     questions via RAG; produces a second briefing-doc output artifact.
     Requires: notebooklm-py>=0.6 installed; Google account.

   Reply with the name(s) of any you'd like to use, or "none" to skip.
```

If the index has no entries (empty table), omit Q7 entirely.

**After the user answers Q7:**
For each plugin the user activated, load its file from `references/plugins/` and run its
Section 1 (Setup & Availability Check) before proceeding. If setup fails and the user
chooses not to fix it, mark that plugin as unavailable and continue with the standard workflow.
Plugins that pass setup are active for the entire session.

After intake, confirm your understanding:
> "I'll research [restate question], focusing on [scope], using [source types].
> [If any plugins active: I'll use [plugin names] — [one-line summary of each plugin's role].]
> I'll flag gaps and missed angles at the end. Ready to start?"

---

### Step 2 — Source discovery

Identify relevant sources. Read `references/source-types.md` to guide tool selection and
discovery strategy per resource type (web, local files, arXiv, code repos, video).

Aim for breadth first: 4–8 diverse primary sources before going deep on any one.

**If NotebookLM is enabled:** Follow `references/plugins/notebooklm.md` Section 2 instead.
The NLM research agent (`source add-research --mode deep`) is the primary discovery mechanism.
Use WebFetch-based discovery only as a fallback if fewer than 4 sources are returned.

---

### Step 3 — Primary source analysis

Fetch and analyse each primary source. For each source:

1. Extract the key claims, data, and evidence relevant to the research question.
2. Apply the quality rubric (see `references/quality-rubric.md`) and assign a quality annotation.
3. Note any secondary leads the source points to (citations, linked resources, related repos).

Do not follow secondary leads yet — collect them for Step 5.

**If NotebookLM is enabled:** Follow `references/plugins/notebooklm.md` Section 3 instead.
Use `notebooklm source guide <id>` to get NLM's AI summary and keywords per source as a
substitute for direct WebFetch reads. Apply the quality rubric as normal based on that output.
Also run `notebooklm generate mind-map` after all sources are loaded to get a concept overview.

---

### Step 4 — Synthesis

Combine findings across primary sources:

- Group by theme or sub-question.
- Surface agreements, contradictions, and patterns.
- Note claims that are single-sourced (unverified) vs corroborated.
- Do not silently choose one side of a conflict — document it.

**If NotebookLM is enabled:** Follow `references/plugins/notebooklm.md` Section 4 instead.
Issue the core synthesis queries via `notebooklm ask`, generate a data table for structured
comparisons, and produce the NotebookLM briefing doc (Artifact A). Use the RAG responses
with their inline citations as the primary evidence base for this section.

---

### Step 5 — Secondary source check-in

Present the secondary leads identified in Step 3 and ask the user for approval before fetching:

```
I've identified these secondary sources worth following:

1. [Title / URL] — [why it's relevant, e.g. "cited by three primary sources on X"]
2. [Title / URL] — [why it's relevant]
3. ...

Shall I fetch and analyse these? Approve all, select a subset, or skip.
```

Wait for the user's response. Then fetch approved sources and integrate findings into the synthesis.

**If NotebookLM is enabled:** After user approval, add each approved URL via
`notebooklm source add <url>` before fetching. Follow `references/plugins/notebooklm.md`
Section 5 to re-query the expanded notebook.

---

### Step 6 — Gap retrospective

After synthesis, evaluate the research against this checklist and flag every gap found:

- **Opposing view** — Is there a credible counter-argument or minority position?
- **Recency** — Are the most recent developments (last 6–12 months) represented?
- **Practitioner vs theoretical** — Is both academic/theoretical and real-world/practitioner perspective present?
- **Geographic / cultural variation** — Does the finding generalise, or is it region/culture-specific?
- **Adjacent domains** — Are there insights from neighbouring fields that apply here?
- **Negative results** — What has been tried and failed? Is that documented?
- **Stakeholder perspectives** — Are all relevant stakeholders (users, operators, critics) represented?

Write "none identified" only if genuinely true after checking all seven.

**If NotebookLM is enabled:** Before running the checklist, issue the seven gap-framing queries
via `notebooklm ask` (see `references/plugins/notebooklm.md` Section 6). Use the answers as
evidence when evaluating each checklist item. Then save the full session history to the
notebook: `notebooklm history --save`.

---

### Step 7 — Report output

Produce the research report using the template in `references/report-template.md`.

**If NotebookLM is enabled:** Two outputs are produced (see `references/plugins/notebooklm.md`
Section 7):
- **Artifact A** — NotebookLM briefing doc (already downloaded in Step 4; present it now
  if not already offered to the user)
- **Artifact B** — The agent's structured report using our template, populated with the NLM
  synthesis findings. The NLM briefing doc is listed as a source in Section 4 (Source
  Inventory) with type "NotebookLM output".

**Standard mode:** produce one report using the template.

After completing the report(s), offer to save to file(s):

```
The report is ready. Would you like me to save it to a file?
If yes, I'll write it to `research-report-<topic-slug>.md` in the current directory,
or you can specify a different path.
```

If the user provides a path, write to that path exactly. If they confirm the default, use
`research-report-<topic-slug>.md` where `<topic-slug>` is a short kebab-case label derived
from the research question.

---

## References

| File | Load when |
|------|-----------|
| `references/source-types.md` | At Step 2, before discovering or fetching sources — covers all resource types (web, local, arXiv, repos, video) including skill-aware YouTube handling |
| `references/quality-rubric.md` | At Step 3, when annotating sources |
| `references/report-template.md` | At Step 7, when producing the output report |
| `references/plugins/INDEX.md` | At Step 1 intake, **before asking Q7** — lists all available plugins with user-facing descriptions and prerequisites; used to build the dynamic activation question |
| `references/plugins/notebooklm.md` | At Step 1, **only if the user activates NotebookLM**. Keep loaded for the entire session. Contains the full co-analyst workflow: setup, source discovery, RAG synthesis, gap queries, and dual-output instructions. |

## Plugin contract

Each plugin in `references/plugins/` follows this contract so future plugins (Confluence,
Obsidian, etc.) are consistent:

1. **Section 1 — Setup & Availability Check**: How to verify the tool is installed and
   authenticated. Must include graceful fallback instructions for when the tool is unavailable.
2. **Sections 2–6**: One section per research workflow step (2 = discovery, 3 = analysis,
   4 = synthesis, 5 = secondary sources, 6 = gap retrospective). Each section describes what
   the plugin does for that step and what the agent falls back to if the plugin fails.
3. **Section 7 — Final Output**: What additional artifacts the plugin produces and how they
   relate to the agent's structured report.
4. **Section 8 — Fallback Rules**: A table of common failure modes and recovery actions.
   The session must always complete even if the plugin fails entirely.
