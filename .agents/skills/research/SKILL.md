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
```

After intake, confirm your understanding:
> "I'll research [restate question], focusing on [scope], using [source types]. I'll flag gaps
> and missed angles at the end. Ready to start?"

---

### Step 2 — Source discovery

Identify relevant sources. Read `references/source-types.md` to guide tool selection and
discovery strategy per resource type (web, local files, arXiv, code repos, video).

Aim for breadth first: 4–8 diverse primary sources before going deep on any one.

---

### Step 3 — Primary source analysis

Fetch and analyse each primary source. For each source:

1. Extract the key claims, data, and evidence relevant to the research question.
2. Apply the quality rubric (see `references/quality-rubric.md`) and assign a quality annotation.
3. Note any secondary leads the source points to (citations, linked resources, related repos).

Do not follow secondary leads yet — collect them for Step 5.

---

### Step 4 — Synthesis

Combine findings across primary sources:

- Group by theme or sub-question.
- Surface agreements, contradictions, and patterns.
- Note claims that are single-sourced (unverified) vs corroborated.
- Do not silently choose one side of a conflict — document it.

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

---

### Step 7 — Report output

Produce the research report using the template in `references/report-template.md`.

After completing the report, offer to save it to a file:

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
