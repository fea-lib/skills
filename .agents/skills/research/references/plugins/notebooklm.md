# NotebookLM Plugin

This file is loaded **only** when the user opts in to NotebookLM at the start of a research
session. It provides step-by-step instructions for using NotebookLM as a co-analyst alongside
Claude throughout the research workflow.

NotebookLM's role: ingest and index all sources, run its own research agent for discovery,
answer cross-source RAG queries with citations, and generate structured analysis artifacts.
Claude's role: frame the research, orchestrate the workflow, apply quality rubrics, run the
gap retrospective, and produce the final structured report.

---

## Table of Contents

1. [Setup & Availability Check](#1-setup--availability-check) — used at Step 1
2. [Source Discovery](#2-source-discovery) — used at Step 2
3. [Per-Source Analysis](#3-per-source-analysis) — used at Step 3
4. [Synthesis via RAG](#4-synthesis-via-rag) — used at Step 4
5. [Secondary Sources](#5-secondary-sources) — used at Step 5
6. [Gap Retrospective Queries](#6-gap-retrospective-queries) — used at Step 6
7. [Final Output](#7-final-output) — used at Step 7
8. [Fallback Rules](#8-fallback-rules) — referenced throughout

---

## 1. Setup & Availability Check

Run these checks **immediately** after the user activates the plugin, before proceeding with intake.

### 1.1 Pipeline CLI and auth checks

Run both checks in parallel (they are independent):

```bash
notebooklm --version
notebooklm auth check
```

Evaluate the combined results:

**If `--version` fails (command not found):**

```
NotebookLM CLI is not installed. To use the NotebookLM plugin, run:

  pip install "notebooklm-py[browser]>=0.6"
  playwright install chromium

Then authenticate:

  notebooklm login

Would you like to continue this research session without NotebookLM instead?
```

Wait for the user's response. If they want to skip: proceed with the standard workflow.
If they want to install: pause and let them set it up, then re-run both checks.

**If `--version` passes but `auth check` fails:**

```
NotebookLM authentication is not valid. Please run:

  notebooklm login

This will open a browser window — log in to your Google account, then press Enter.
Let me know when done and I'll continue.
```

Wait for the user to confirm, then re-run `notebooklm auth check` to verify before proceeding.

**If both pass:** proceed directly to Section 1.2.

### 1.2 Create notebook for this session

Once checks pass, create a notebook named after the research topic (use the topic slug from
the intake question, or a short descriptive title if intake hasn't started yet):

```bash
notebooklm create "<Research Topic Title>"
```

Capture the notebook ID from the output. Then set it as active:

```bash
notebooklm use <notebook_id>
```

Confirm to the user:
```
NotebookLM notebook "<title>" created. All sources will be indexed there throughout
this session. I'll use it for discovery, analysis, and synthesis.
```

---

## 2. Source Discovery

NotebookLM's research agent is the **primary** discovery mechanism when this plugin is active.

### 2.1 Run the research agent

Start a deep web research run (non-blocking, suitable for agent workflows):

```bash
notebooklm source add-research "<research question>" --mode deep --no-wait
```

Use the user's research question from Step 1 intake as the query. Notify the user that
discovery is running and may take up to 10 minutes:

```
NotebookLM research agent is running in deep mode. This can take up to 10 minutes.
I'll poll for progress and keep you updated.
```

Poll for status every 60 seconds and report each update:

```bash
notebooklm research status
```

After each poll, output a brief progress line (use the status field from the command output):

```
[~Xs elapsed] Research agent: <status> — <sources_found> sources found so far.
```

Once the status indicates completion, import all sources:

```bash
notebooklm research wait --import-all --timeout 60
```

Using a short `--timeout 60` here is safe because we already waited for completion via
polling — this call is just for the final import, not open-ended waiting.

### 2.2 Check source count

```bash
notebooklm source list
```

If fewer than 4 sources were imported, supplement with Claude's native WebFetch-based
discovery (see `references/source-types.md`, Section 6) and add each found URL:

```bash
notebooklm source add "<url>"
```

### 2.3 Add any user-provided sources

If the user specified particular URLs, files, or YouTube videos at intake, add them now:

```bash
notebooklm source add "<url-or-filepath>"   # auto-detects type
```

Supported: URLs, YouTube links, PDFs, text files, Markdown, DOCX, audio, video, images.

---

## 3. Per-Source Analysis

### 3.1 Get AI summaries per source

For each source in the notebook, retrieve NotebookLM's AI-generated summary and keywords
instead of fetching the full page with WebFetch:

```bash
notebooklm source guide <source_id>
```

Output: summary text + keyword list. Use this as the basis for quality annotation.
Apply the quality rubric from `references/quality-rubric.md` as normal — the `source guide`
output provides enough signal to assess credibility, bias, and recency indicators.

### 3.2 Generate a concept map

Immediately after all sources are loaded, generate a mind map to get a cross-source concept
overview. This is synchronous — no `--wait` needed:

```bash
notebooklm generate mind-map
notebooklm download mind-map ./mindmap-<topic-slug>.json
```

Read the downloaded JSON (structure: `{"name": "...", "children": [...]}`) and use it to
orient the synthesis in Step 4. Summarise the top-level concepts to the user before proceeding.

---

## 4. Synthesis via RAG

Use `notebooklm ask` to perform cross-source synthesis. These queries replace (or heavily
augment) what Claude would otherwise derive by reading each source individually.

### 4.1 Core synthesis queries

Issue these queries in sequence. Each response includes inline citations `[1]`, `[2]` etc.
that map to specific sources — capture these for the source inventory.

```bash
notebooklm ask "What are the main themes and key claims across all sources?"
notebooklm ask "What do sources agree on? Where do they contradict or diverge?"
notebooklm ask "What is the strongest evidence for the central claims?"
notebooklm ask "Which sources are most authoritative or frequently cited by others?"
notebooklm ask "What practical or real-world applications do the sources describe?"
```

Save each answer as a note for later reference:

```bash
notebooklm ask "<question>" --save-as-note --note-title "<short label>"
```

### 4.2 Topic-specific follow-up queries

Based on the research question and concept map from Step 3, issue 2–3 additional targeted
queries relevant to the specific topic. Examples:

- `"What are the limitations or open problems identified across sources?"`
- `"How has [key concept] evolved over the time range covered by the sources?"`
- `"What do sources say about [specific angle from intake]?"`

### 4.3 Structured comparison table

If the research involves comparing options, approaches, tools, or entities:

```bash
notebooklm generate data-table "<natural language description of what to compare>" --wait
notebooklm download data-table ./comparison-<topic-slug>.csv
```

Read the CSV and include relevant columns in Section 3 (Key Findings) of the final report.

### 4.4 Generate NotebookLM briefing doc (Artifact A)

```bash
notebooklm generate report --format briefing-doc --wait
notebooklm download report ./notebooklm-briefing-<topic-slug>.md
```

This is **Artifact A** — one of two final deliverables. Offer it to the user immediately
after download. Continue to Step 5 regardless (Claude's structured report is still produced).

---

## 5. Secondary Sources

After the user approves secondary leads (Step 5 of the main workflow):

```bash
notebooklm source add "<approved_url>"   # repeat for each approved source
```

Once added, wait briefly for indexing (usually < 30 seconds), then re-run the most relevant
synthesis queries from Section 4.1 against the expanded source set:

```bash
notebooklm ask "Given all sources including the newly added ones, does the picture change?"
notebooklm ask "What do the new sources add or contradict?"
```

---

## 6. Gap Retrospective Queries

Before running the 7-point gap checklist (Step 6 of the main workflow), issue these targeted
queries to NotebookLM. Use the answers as evidence when evaluating each checklist item.

```bash
notebooklm ask "Is there a credible opposing view or minority position not well represented in these sources?"
notebooklm ask "What recent developments from the last 12 months might be missing from these sources?"
notebooklm ask "Are there practitioner or real-world perspectives underrepresented compared to theoretical ones?"
notebooklm ask "Do these sources represent a particular geographic or cultural perspective? What is missing?"
notebooklm ask "What adjacent fields or disciplines might have relevant insights not covered here?"
notebooklm ask "What approaches have been tried and failed, according to these sources?"
notebooklm ask "Are there important stakeholder groups whose perspectives are absent from these sources?"
```

After the retrospective, persist the full session conversation to the notebook:

```bash
notebooklm history --save --note-title "Research Session - <date> - <topic-slug>"
```

---

## 7. Final Output

Two deliverables are produced when NotebookLM is active:

### Artifact A — NotebookLM Briefing Doc

Already downloaded in Section 4.4 as `./notebooklm-briefing-<topic-slug>.md`.

This is NotebookLM's own synthesis of the indexed sources. Present it to the user and offer
to save it if not already done.

### Artifact B — Claude's Structured Report

Produce the full report using `references/report-template.md` as normal. Populate it using:

- Section 2 (Methodology): note that NotebookLM was used; list the notebook ID; note that
  `source add-research` drove discovery and `ask` queries drove synthesis.
- Section 3 (Key Findings): draw from the `ask` responses captured in Steps 4 and 5.
  The NLM briefing doc (Artifact A) is a valid input here — treat it as source `[S-NLM]`
  in the source inventory.
- Section 4 (Source Inventory): include every source from `notebooklm source list`, with
  quality annotations from Section 3.1. Add the NLM briefing doc as a separate entry
  (Type: "NotebookLM output", Quality: note it is a synthesis, not a primary source).
- Sections 5–7: gap analysis, conflicts, and next steps as normal.

After producing Artifact B, offer to save both files:

```
Both outputs are ready:
- Artifact A: NotebookLM briefing doc → notebooklm-briefing-<slug>.md
- Artifact B: Structured research report → research-report-<slug>.md

Would you like me to save Artifact B to a file? I can also save it to a custom path.
```

---

## 8. Fallback Rules

Apply these whenever a `notebooklm` command fails mid-session (error, auth expiry, timeout,
rate limit):

1. **Log the failure** — note which step and command failed.
2. **Continue natively** — fall back to Claude's standard capability for that step
   (WebFetch for discovery, direct reading for analysis, Claude synthesis for Step 4).
3. **Record in report** — add a note to Section 2 (Methodology) stating which steps ran
   natively due to NotebookLM errors.
4. **Do not abort** — the research session always completes. NotebookLM is an enhancement,
   not a dependency.

Common failure modes and recovery:

| Failure | Recovery |
|---------|----------|
| `auth check` fails mid-session | Run `notebooklm auth check` again; if still failing, offer user option to re-run `notebooklm login` or continue natively |
| `source add-research` times out | Check `notebooklm research status`; if still running, wait; if failed, run `source add` for manually discovered URLs |
| `ask` returns empty or error | Retry once; if still failing, Claude synthesises from `source guide` outputs and direct source reads |
| `generate report` fails | Skip Artifact A; Artifact B (Claude's report) is unaffected |
| Rate limit on any command | Wait 30–60 seconds and retry; if persistent, continue with native Claude for remainder of session |
