# Research Report Template

Use this structure for every research output. Adapt section depth to the complexity of the task — a quick factual lookup needs less detail than a competitive landscape or literature review. Omit sections that genuinely do not apply, but always include the source inventory and gap analysis.

---

## Table of Contents

1. [Research Question & Scope](#1-research-question--scope)
2. [Methodology](#2-methodology)
3. [Key Findings](#3-key-findings)
4. [Source Inventory](#4-source-inventory)
5. [Conflicts & Open Questions](#5-conflicts--open-questions)
6. [Blindspot / Gap Analysis](#6-blindspot--gap-analysis)
7. [Recommended Next Steps](#7-recommended-next-steps)

---

## 1. Research Question & Scope

State the research question exactly as understood after the intake conversation. Include any explicit constraints (time range, geography, domain, depth level) agreed with the user.

```
Research question: [verbatim or close paraphrase of what was asked]
Scope constraints: [e.g. "English-language sources only", "post-2020", "focus on OSS implementations"]
Out of scope: [anything explicitly excluded or deprioritised]
```

---

## 2. Methodology

Briefly describe how the research was conducted. This helps the user reproduce or extend the work.

- **Resource types consulted:** (web, local files, arXiv, code repos, video, etc.)
- **Search strategy:** key queries used, databases or indexes searched
- **Depth:** primary sources only / followed secondary leads / stopped at tertiary
- **Secondary sources approved by user:** yes/no, list if yes
- **Tools used:** (WebFetch, Read, arXiv URL pattern, youtube-summarizer skill, etc.)

---

## 3. Key Findings

Present the substantive answers and insights. Group by theme or sub-question. Each claim should reference at least one source from the source inventory using inline notation `[S1]`, `[S2]`, etc.

### [Theme or sub-question 1]

[Finding with inline reference, e.g. "The primary driver of X is Y [S3], though some practitioners dispute this [S7]."]

### [Theme or sub-question 2]

...

> For conflicting evidence, surface the conflict here with a note rather than silently choosing one side. Use "Conflicting evidence: see Section 5."

---

## 4. Source Inventory

List every source consulted, whether or not it contributed to the findings. Include quality annotations (see `references/quality-rubric.md` for the rubric).

| ID | Source | Type | Date | Quality | Notes |
|----|--------|------|------|---------|-------|
| S1 | [Title or URL] | Web / Paper / File / Repo / Video | YYYY-MM or "undated" | High / Medium / Low — _reason_ | Short note on what it contributed |
| S2 | ... | | | | |

> "Type" values: Web, Academic, Local file, Code repo, Video, Other
> Quality annotation format: `High — peer-reviewed, recent, corroborated` or `Low — undated blog, no author, uncorroborated`

---

## 5. Conflicts & Open Questions

List evidence that contradicts other findings, claims that could not be corroborated, and questions the research raised but did not resolve.

- **Conflict:** [S2] claims X; [S5] claims the opposite. Neither source is clearly more authoritative.
- **Unresolved:** Could not find primary data on Y — only secondary accounts exist.
- **Requires expertise:** Z requires domain expertise to evaluate correctly.

---

## 6. Blindspot / Gap Analysis

Document angles that were not covered, either because they were out of scope or because the research did not surface them. This section is mandatory — write "none identified" only if genuinely true after running the retrospective checklist.

Retrospective checklist (evaluate each):

- [ ] **Opposing view** — Is there a credible counter-argument or minority position?
- [ ] **Recency** — Are the most recent developments (last 6–12 months) represented?
- [ ] **Practitioner vs theoretical** — Is both academic/theoretical and real-world/practitioner perspective present?
- [ ] **Geographic / cultural variation** — Does the finding generalise, or is it region/culture-specific?
- [ ] **Adjacent domains** — Are there insights from neighbouring fields that apply here?
- [ ] **Negative results** — What approaches have been tried and failed? Is that documented?
- [ ] **Stakeholder perspectives** — Are all relevant stakeholders (users, operators, critics) represented?

For each gap identified, write one line: what is missing and why it matters.

---

## 7. Recommended Next Steps

Concrete, actionable suggestions for what the user should do with this research or where to go deeper.

1. [Specific action, e.g. "Read the full paper at S4 — the abstract-level summary in Section 3 may understate its relevance to your use case."]
2. [e.g. "Consult a domain expert on the conflict identified in Section 5 before making a decision on Z."]
3. [e.g. "Run a follow-up research pass on Y, which this session flagged as unresolved."]

---

*Report generated: [date]*
*Research session depth: primary + approved secondary / primary only*
