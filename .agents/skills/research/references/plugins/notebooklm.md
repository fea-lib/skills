# NotebookLM Plugin

> **CLI reference:** The authoritative command reference for `notebooklm-py` is maintained by
> the tool's author at
> <https://github.com/teng-lin/notebooklm-py/blob/main/src/notebooklm/data/SKILL.md>.
> This plugin is scoped to integrating NotebookLM into the research workflow steps only.
> Consult that file for full command documentation, output schemas, exit codes, and
> troubleshooting guidance.

This file is loaded **only** when the user opts in to NotebookLM at the start of a research
session. It provides step-by-step instructions for using NotebookLM as a co-analyst alongside
Claude throughout the research workflow.

NotebookLM's role: ingest and index all sources, run its own research agent for discovery,
answer cross-source RAG queries with citations, and generate structured analysis artifacts.
Claude's role: frame the research, orchestrate the workflow, apply quality rubrics, run the
gap retrospective, and produce the final structured report.

---

## Table of Contents

**Research workflow** (Sections 1–7 — run in order during a session)

1. [Setup & Availability Check](#1-setup--availability-check) — used at Step 1; includes notebook reuse check
2. [Source Discovery](#2-source-discovery) — used at Step 2
3. [Per-Source Analysis](#3-per-source-analysis) — used at Step 3
4. [Synthesis via RAG](#4-synthesis-via-rag) — used at Step 4
5. [Secondary Sources](#5-secondary-sources) — used at Step 5
6. [Gap Retrospective Queries](#6-gap-retrospective-queries) — used at Step 6
7. [Final Output](#7-final-output) — used at Step 7

**After the session** (Sections 8–9 — run after Step 7 or on explicit user request)

8. [Deliverables](#8-deliverables) — generate podcasts, videos, slide decks, infographics, quizzes, and flashcards
9. [Fallback Rules](#9-fallback-rules) — referenced throughout if any command fails

**Maintenance** (Section 10 — out-of-band, never run automatically)

10. [Update Check](#10-update-check) — sync plugin and CLI with upstream changes

---

## 1. Setup & Availability Check

Run these checks **immediately** after the user activates the plugin, before proceeding with intake.

### 1.1 Pipeline CLI and auth checks

Run the status check:

```bash
notebooklm status
```

Evaluate the result:

**If the command is not found (CLI missing):**

```
NotebookLM CLI is not installed. To use the NotebookLM plugin, run:

  pip install "notebooklm-py[browser]"
  playwright install chromium

Then authenticate:

  notebooklm login

Would you like to continue this research session without NotebookLM instead?
```

Wait for the user's response. If they want to skip: proceed with the standard workflow.
If they want to install: pause and let them set it up, then re-run `notebooklm status`.

**If the command is found but shows unauthenticated or an auth error:**

Run the diagnostic to get more detail:

```bash
notebooklm auth check
```

Then tell the user:

```
NotebookLM authentication is not valid. Please run:

  notebooklm login

This will open a browser window — log in to your Google account, then press Enter.
Let me know when done and I'll continue.
```

Wait for the user to confirm, then re-run `notebooklm status` to verify before proceeding.

**If `notebooklm status` shows "Authenticated as: email@...":** proceed directly to Section 1.2.

### 1.2 Select or create notebook for this session

Once checks pass, fetch the user's existing notebooks before creating a new one:

```bash
notebooklm list --json
```

Parse the returned list. Take the **5 most recent** notebooks (by `created_at`). Compare
each notebook's title to the current research topic — use natural language understanding
to judge similarity (keyword overlap, shared concepts). Identify any that plausibly relate
to the topic.

**If one or more look relevant**, present them to the user:

```
You have existing notebooks that may match this topic:

  1. "<Title A>"  (created <date>)
  2. "<Title B>"  (created <date>)
  N. Create a new notebook for "<Research Topic Title>"

Would you like to continue in an existing notebook, or start fresh?
Enter a number:
```

Always include "Create a new notebook" as the last numbered option.

**If none look relevant**, tell the user briefly and offer to proceed:

```
No existing notebooks appear to match this topic. I'll create a new one:
"<Research Topic Title>"

Shall I go ahead? (yes / no — or name an existing notebook if you'd prefer one)
```

**Wait for the user's response before proceeding.**

- If the user picks an existing notebook: run `notebooklm use <notebook_id>` and confirm
  which notebook is now active. Skip the `create` step entirely.
- If the user confirms a new notebook (or says yes to the no-match prompt): create it:

```bash
notebooklm create "<Research Topic Title>"
notebooklm use <notebook_id>
```

Confirm to the user which notebook is active and whether it was reused or newly created.

---

## 2. Source Discovery

NotebookLM's research agent is the **primary** discovery mechanism when this plugin is active.

### 2.1 Run the research agent

Start a deep web research run (non-blocking):

```bash
notebooklm source add-research "<research question>" --mode deep --no-wait
```

Use the user's research question from Step 1 intake as the query. Then spawn a background
agent to wait for completion and import the sources, so the main session remains responsive:

```
Spawn background agent:
  "Wait for NotebookLM deep research to complete in notebook <notebook_id>, then import
   all sources. Run:
     notebooklm research wait -n <notebook_id> --import-all --timeout 1800
   Report how many sources were imported, or report a timeout if it exceeds 30 minutes."
```

Notify the user:

```
NotebookLM research agent is running in deep mode (up to 30 minutes).
A background agent is waiting and will import sources automatically when done.
```

When the background agent reports back, continue to Section 2.2.

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

## 8. Deliverables

This section runs **after Step 7** (Final Output) once both Artifact A and Artifact B have
been delivered. It can also be triggered at any point during or after a session if the user
explicitly asks for a deliverable (e.g. "generate a podcast", "make a slide deck").

### 8.1 Proactive offer after Step 7

Immediately after presenting both artifacts in Section 7, offer the deliverables menu:

```
NotebookLM can also generate the following from the research sources in this notebook:

  a) Podcast        — audio deep dive (.mp3), ~10–20 min to generate
  b) Video          — video explainer (.mp4), ~15–45 min to generate
  c) Slide deck     — presentation (.pdf or .pptx), ~5–15 min to generate
  d) Infographic    — visual summary (.png), ~5–15 min to generate
  e) Quiz           — multiple-choice quiz (.json or .md), ~5–15 min to generate
  f) Flashcards     — study cards (.json or .md), ~5–15 min to generate

Which would you like? (Enter one or more letters, or "skip")
```

Wait for the user's response. If they say skip / none / no: acknowledge and close the session
as normal. If they select one or more: run the corresponding subsections below, then offer
to save all outputs before closing.

Note: Audio, video, quiz, flashcard, infographic, and slide deck generation are subject to
Google rate limiting and may occasionally fail. See Section 8.7 for fallback guidance.

### 8.2 Generating a deliverable

All deliverables follow the same pattern: `generate <type> [options] --wait`, then
`download <type> ./<topic-slug>-<type>.<ext>`. Tell the user the downloaded filename when done.

| Type | Generate command | Download ext | Key flags |
|---|---|---|---|
| Podcast | `generate audio "<prompt>"` | `.mp3` | `--format deep-dive`(default)`/brief/critique/debate`; `--length short/long` |
| Video | `generate video "<prompt>"` | `.mp4` | `--format explainer`(default)`/brief`; `--style classic/whiteboard/kawaii/anime/watercolor/retro-print/heritage/paper-craft` |
| Slide deck | `generate slide-deck` | `.pdf` or `.pptx` | `--format detailed`(default)`/presenter`; `--length short`; ask user pdf vs pptx before download — pptx requires `--format pptx` |
| Infographic | `generate infographic` | `.png` | `--orientation landscape`(default)`/portrait/square`; `--detail concise/standard`(default)`/detailed` |
| Quiz | `generate quiz` | `.json` or `.md` | `--difficulty easy/medium`(default)`/hard`; `--quantity fewer/standard`(default)`/more`; ask user json vs markdown before download — markdown requires `--format markdown` |
| Flashcards | `generate flashcards` | `.json` or `.md` | same flags as quiz |

For podcast and video, use the research topic as the `<prompt>` if the user doesn't specify one.

### 8.3 Fallback rules for deliverables

If any `generate` command fails (rate limit, timeout, or `GENERATION_FAILED`):

1. **Log the failure** — note which deliverable type failed.
2. **Do not abort** — offer the remaining deliverables the user requested; skip only the failed one.
3. **Report and offer options:** retry in 5–10 minutes, try in the NotebookLM web UI instead, or skip.
4. **If retrying**: wait at least 5 minutes, then re-run the same `generate` command once.
   If it fails again, offer the web UI or skip options.
5. **Never block the session** — if the user chooses to skip, confirm and move on.

---

## 9. Fallback Rules

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

---

## 10. Update Check

This section is invoked **out-of-band** — it is not part of the research workflow. Run it only
when the user triggers an update check; never run it automatically during a research session.

### 10.1 Trigger detection

Recognise any phrasing that plausibly means the user wants to sync this plugin with the
upstream `notebooklm-py` CLI or its published skill (e.g. "update the notebooklm plugin",
"check for notebooklm updates"). The match is intentionally loose — use natural language
understanding, not a keyword list. When in doubt, confirm (Section 10.2).

### 10.2 Confirmation step

Before doing anything, ask:

```
It looks like you want to check the NotebookLM plugin for upstream updates.
Is that right? (yes / no)
```

If the user says **no**: apologise briefly and return to whatever the user was doing before.
If the user says **yes**: proceed to Section 10.3.

### 10.3 Fetch upstream sources

Fetch all three of these in parallel:

1. **Upstream SKILL.md** — commands, patterns, autonomy rules, error handling, timing:
   `https://raw.githubusercontent.com/teng-lin/notebooklm-py/refs/heads/main/src/notebooklm/data/SKILL.md`

2. **Upstream README** — install instructions, prerequisites, auth setup:
   `https://raw.githubusercontent.com/teng-lin/notebooklm-py/refs/heads/main/README.md`

3. **This plugin file** — re-read `references/plugins/notebooklm.md` to understand what the
   plugin currently says. This is the baseline for the comparison.

### 10.4 CLI version check

Run these two commands (the second fetches the latest published version from PyPI):

```bash
notebooklm --version
pip index versions notebooklm-py 2>/dev/null | head -1
```

The first gives the installed version. The second lists available versions — the first entry
is the latest release.

Compare the two:

- **If already on the latest version:** note this in the update summary; no action needed for
  the CLI.
- **If a newer version is available:** report it and ask for confirmation before upgrading:

```
The installed notebooklm-py is <installed_version>.
A newer version is available: <latest_version>.

Would you like to upgrade?
  pip install --upgrade "notebooklm-py[browser]"

(yes / no)
```

If the user says **yes**: run the upgrade command, then re-run `notebooklm --version` to
confirm the new version is active. Report the result.

If the user says **no**: note the skipped upgrade in the final summary and continue.

If `notebooklm` is not installed (command not found): skip this step and note it in the
summary — CLI installation is covered by Section 1.1, not the update flow.

### 10.5 Scope filter

This plugin covers a narrow slice of the upstream CLI — only what is needed to integrate
NotebookLM into the research workflow. Compare upstream content **only** against what this
plugin already references. Do not import workflows this plugin has never covered.

To apply the filter: re-read each section of `notebooklm.md` and identify every
`notebooklm` command, flag, timeout value, pattern, or prerequisite it mentions. Those are
the in-scope items. Check each one against the upstream content.

**In scope** (if this plugin references them):
- Install commands and prerequisites (Section 1.1)
- Auth / setup check commands (`notebooklm status`, `notebooklm auth check`)
- Notebook create / use commands (Section 1.2)
- Research agent commands and flags (`source add-research`, `research wait`, timeouts)
- Source management commands (`source add`, `source list`, `source guide`)
- RAG query commands (`notebooklm ask`) and options used in the plugin
- Report generation commands and options used in the plugin (`generate report`, `download report`)
- Mind-map generation and download (Section 3.2)
- History save commands (Section 6)
- Any subagent pattern recommendations or parallel-safety flags affecting the above
- Audio / video / podcast workflows (Section 8)
- Quiz, flashcard, infographic, slide deck workflows (Section 8)

**Out of scope** (ignore upstream changes to these unless the plugin already references them):
- Language settings
- Bulk import patterns
- Features Beyond the Web UI table
- Sharing commands
- Anything in the upstream skill not touched by this plugin

### 10.6 Change report

Present each relevant difference as a numbered item showing: the section affected, the
current text, the upstream text, and a one-sentence impact statement. If no relevant changes
are found, say so. Close by asking: apply all / select which / skip.

### 10.7 Apply with preview

For each change the user approves (either all via option a, or a subset via option b):

1. Show the **exact proposed edit** — the old text and the replacement text, clearly delimited.
2. Ask: "Apply this change? (yes / no)"
3. If yes: write the edit to `notebooklm.md`.
4. If no: skip this change and move to the next.

After all approved changes are applied, summarise:

```
Done. Update complete.

CLI:    <installed_version> → <new_version>  (or: already up to date / skipped)
Plugin: N change(s) applied to notebooklm.md:
        - [brief description of each applied change]
        (or: no changes / skipped)
```

If the user skipped all changes: confirm nothing was modified.
