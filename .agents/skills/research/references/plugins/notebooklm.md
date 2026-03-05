# NotebookLM Plugin

> **CLI reference:** Full command docs, output schemas, and exit codes at
> <https://github.com/teng-lin/notebooklm-py/blob/main/src/notebooklm/data/SKILL.md>.
> This plugin covers only the research workflow integration.

NotebookLM's role: ingest and index all sources, run its own research agent for discovery,
answer cross-source RAG queries with citations, and generate structured analysis artifacts.
Claude's role: frame the research, orchestrate the workflow, apply quality rubrics, run the
gap retrospective, and produce the final structured report.

## Table of Contents

**Research workflow** (Sections 1–7 — run in order)
1. [Setup & Availability Check](#1-setup--availability-check)
2. [Source Discovery](#2-source-discovery)
3. [Per-Source Analysis](#3-per-source-analysis)
4. [Synthesis via RAG](#4-synthesis-via-rag)
5. [Secondary Sources](#5-secondary-sources)
6. [Gap Retrospective Queries](#6-gap-retrospective-queries)
7. [Final Output](#7-final-output)

**Post-session** (on request)
8. [Deliverables](#8-deliverables) — podcasts, videos, slide decks, infographics, quizzes, flashcards
9. [Fallback Rules](#9-fallback-rules)
10. [Update Check](#10-update-check) — never run automatically

---

## 1. Setup & Availability Check

### 1.1 Locate CLI and verify auth

The binary may not be on `$PATH`. Try in order until one succeeds:

```bash
notebooklm status
/Library/Frameworks/Python.framework/Versions/3.12/bin/notebooklm status
~/.local/bin/notebooklm status
```

Use whichever path works for all subsequent commands this session.

**CLI missing** — install and proceed to login:
```bash
pip install "notebooklm-py[browser]"
python3 -m playwright install chromium
```

**Check auth** — `status` does not confirm auth; always use:
```bash
notebooklm auth check
```
All four checks passing (Storage ✓, JSON ✓, Cookies ✓, SID ✓) = valid. If any fail, run the login flow.

**Login flow** — the command opens a browser and waits for Enter; automate with `expect`:
```bash
expect -c '
spawn notebooklm login
expect "Press ENTER when logged in"
sleep 120
send "\r"
expect eof
'
```
Tell the user: *"A browser window has opened. Log in to your Google account, wait for the NotebookLM homepage — I'll confirm automatically in 2 minutes."*

After `expect` completes, re-run `notebooklm auth check`. If it still fails, retry with `sleep 180` or ask the user to run `notebooklm login` manually in their own terminal.

**Non-Chrome browser** — Playwright always opens Chromium (not the system browser). Two options:
1. **(Recommended)** Log in inside the Chromium window that opens — it's a fresh session.
2. **Cookie export** (if they prefer not to re-auth in Chrome):
   ```bash
   pip3 install browser-cookie3
   python3 -c "
   import browser_cookie3, json, os
   # Set cookie_file to the browser's Cookies DB, e.g. Arc:
   cookie_file = os.path.expanduser('~/Library/Application Support/Arc/User Data/Default/Cookies')
   cj = browser_cookie3.chrome(cookie_file=cookie_file, domain_name='.google.com')
   cookies = [{'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path,
               'expires': c.expires, 'httpOnly': False, 'secure': c.secure, 'sameSite': 'Lax'}
              for c in cj]
   state = {'cookies': cookies, 'origins': []}
   os.makedirs(os.path.expanduser('~/.notebooklm'), exist_ok=True)
   with open(os.path.expanduser('~/.notebooklm/storage_state.json'), 'w') as f: json.dump(state, f)
   print(f'Wrote {len(cookies)} cookies')
   "
   ```
   Note: Arc and some Chromium-based browsers use custom keychain entries that `browser_cookie3`
   cannot decrypt — Option 1 is the reliable fallback in that case.

### 1.2 Select or create notebook

```bash
notebooklm list --json
```

Compare the 5 most recent notebooks to the research topic. If any look relevant, present them with a "Create new" option at the end and wait for the user's choice. If none match, confirm creating a new one.

```bash
notebooklm create "<Research Topic Title>"
notebooklm use <notebook_id>
```

---

## 2. Source Discovery

### 2.1 Run the research agent (non-blocking)

```bash
notebooklm source add-research "<research question>" --mode deep --no-wait
```

Spawn a background agent to wait and import:
```
notebooklm research wait -n <notebook_id> --import-all --timeout 1800
```
Notify the user the agent is running (up to 30 min). Continue when the background agent reports back.

### 2.2 Check source count and add user-provided sources

```bash
notebooklm source list
```

If fewer than 4 sources, supplement with WebFetch-based discovery (`references/source-types.md` §6) and add each URL:
```bash
notebooklm source add "<url>"
```

Add any user-specified URLs/files/videos from intake (auto-detects type):
```bash
notebooklm source add "<url-or-filepath>"
```

---

## 3. Per-Source Analysis

### 3.1 AI summaries per source

```bash
notebooklm source guide <source_id>
```

Use the summary + keywords as the basis for quality annotation (apply `references/quality-rubric.md` as normal).

### 3.2 Concept map

```bash
notebooklm generate mind-map
notebooklm download mind-map ./mindmap-<topic-slug>.json
```

Read the JSON (`{"name": "...", "children": [...]}`) and summarise top-level concepts to the user before proceeding to synthesis.

---

## 4. Synthesis via RAG

### 4.1 Core queries (save each as a note)

```bash
notebooklm ask "What are the main themes and key claims across all sources?" --save-as-note --note-title "themes"
notebooklm ask "What do sources agree on? Where do they contradict or diverge?" --save-as-note --note-title "agreements-conflicts"
notebooklm ask "What is the strongest evidence for the central claims?" --save-as-note --note-title "evidence"
notebooklm ask "Which sources are most authoritative or frequently cited by others?" --save-as-note --note-title "authority"
notebooklm ask "What practical or real-world applications do the sources describe?" --save-as-note --note-title "applications"
```

Each response includes inline citations `[1]`, `[2]` — capture these for the source inventory.

### 4.2 Topic-specific follow-ups

Issue 2–3 additional queries based on the research question and concept map, e.g.:
- `"What are the limitations or open problems identified across sources?"`
- `"How has [key concept] evolved over the time range covered by the sources?"`

### 4.3 Comparison table (if comparing options/tools)

```bash
notebooklm generate data-table "<what to compare>" --wait
notebooklm download data-table ./comparison-<topic-slug>.csv
```

### 4.4 Generate briefing doc (Artifact A)

```bash
notebooklm generate report --format briefing-doc --wait
notebooklm download report ./notebooklm-briefing-<topic-slug>.md
```

Offer Artifact A to the user immediately. Continue to Step 5 regardless.

---

## 5. Secondary Sources

Add each approved URL, then re-query:
```bash
notebooklm source add "<approved_url>"
notebooklm ask "Given all sources including the newly added ones, does the picture change?"
notebooklm ask "What do the new sources add or contradict?"
```

---

## 6. Gap Retrospective Queries

```bash
notebooklm ask "Is there a credible opposing view or minority position not well represented in these sources?"
notebooklm ask "What recent developments from the last 12 months might be missing from these sources?"
notebooklm ask "Are there practitioner or real-world perspectives underrepresented compared to theoretical ones?"
notebooklm ask "Do these sources represent a particular geographic or cultural perspective? What is missing?"
notebooklm ask "What adjacent fields or disciplines might have relevant insights not covered here?"
notebooklm ask "What approaches have been tried and failed, according to these sources?"
notebooklm ask "Are there important stakeholder groups whose perspectives are absent from these sources?"
```

Use the answers as evidence when evaluating the 7-point gap checklist in the main workflow. Then save session history:
```bash
notebooklm history --save --note-title "Research Session - <date> - <topic-slug>"
```

---

## 7. Final Output

Two deliverables:

**Artifact A** — Already downloaded in §4.4. Present to user if not already done.

**Artifact B** — Claude's structured report (`references/report-template.md`):
- **Frontmatter:** Add YAML frontmatter at the top of the report file with session metadata instead of a plain text footer:
  ```yaml
  ---
  generated: YYYY-MM-DD
  research_depth: "primary + approved secondary (N additional sources)"
  notebooklm_notebook: https://notebooklm.google.com/notebook/<notebook-id>
  artifact_briefing_doc: notebooklm-briefing.md
  ---
  ```
- **§2 Methodology:** note NotebookLM was used; reference the notebook via its URL (same as frontmatter); note discovery via `source add-research` and synthesis via `ask`.
- **§3 Artefacts** _(insert between §2 Methodology and §3 Key Findings, shifting subsequent sections by one)_: list all NLM-generated deliverables produced in §8. Link each by its NLM artifact URL rather than a local file path — this avoids committing binary files (`.mp4`, `.pdf`, `.png`) to git. To get the artifact URL:
  ```bash
  notebooklm artifact list   # find the artifact ID
  # URL pattern: https://notebooklm.google.com/notebook/<notebook-id>?artifactId=<artifact-id>
  ```
  Example table:
  ```markdown
  | Artefact | Description |
  |----------|-------------|
  | [Briefing doc](notebooklm-briefing.md) | NLM-generated briefing doc; source [S-NLM] |
  | [Video title](https://notebooklm.google.com/notebook/<id>?artifactId=<id>) | Short explainer (~5 min) |
  | [Slide deck title](https://notebooklm.google.com/notebook/<id>?artifactId=<id>) | Presentation |
  | [Infographic title](https://notebooklm.google.com/notebook/<id>?artifactId=<id>) | Visual summary |
  ```
  Omit this section if no deliverables were generated in §8.
- **§4 Key Findings** _(was §3)_: draw from `ask` responses. Treat Artifact A as source `[S-NLM]`.
- **§5 Source Inventory** _(was §4)_: every source from `notebooklm source list` with quality annotations. Add NLM briefing doc as Type: "NotebookLM output".
- **§6–8** _(were §5–7)_: gap analysis, conflicts, next steps as normal.

Replace the plain text footer with a single line pointing to the frontmatter:
```
*Report generated: YYYY-MM-DD — see frontmatter for full metadata.*
```

Offer to save both files when done.

---

## 8. Deliverables

Offer after Step 7, or on explicit user request at any point:

| Type | Generate command | Ext | Key flags |
|---|---|---|---|
| Podcast | `generate audio "<prompt>"` | `.mp3` | `--format deep-dive/brief/critique/debate`; `--length short/long` |
| Video | `generate video "<prompt>"` | `.mp4` | `--format explainer/brief`; `--style classic/whiteboard/kawaii/…` |
| Slide deck | `generate slide-deck` | `.pdf`/`.pptx` | `--format detailed/presenter`; `--length short`; pptx needs `--format pptx` |
| Infographic | `generate infographic` | `.png` | `--orientation landscape/portrait/square`; `--detail concise/standard/detailed` |
| Quiz | `generate quiz` | `.json`/`.md` | `--difficulty easy/medium/hard`; `--quantity fewer/standard/more`; md needs `--format markdown` |
| Flashcards | `generate flashcards` | `.json`/`.md` | same flags as quiz |

Pattern: `generate <type> [flags] --wait`, then `download <type> ./<topic-slug>-<type>.<ext>`.

Use the research topic as the prompt for podcast/video unless the user specifies one.

**If generation fails** (rate limit / timeout / `GENERATION_FAILED`): skip that type, offer the rest, then offer retry in 5–10 min or the NotebookLM web UI.

---

## 9. Fallback Rules

On any `notebooklm` command failure: fall back to Claude's native capability for that step, record it in §2 (Methodology), and continue. The session always completes.

| Failure | Recovery |
|---------|----------|
| `auth check` fails mid-session | Retry; if still failing, offer `notebooklm login` or continue natively |
| `source add-research` times out | Check `notebooklm research status`; if failed, add URLs manually via `source add` |
| `ask` returns empty or error | Retry once; if still failing, synthesise from `source guide` outputs |
| `generate report` fails | Skip Artifact A; Artifact B is unaffected |
| Rate limit | Wait 30–60 s and retry; if persistent, continue natively for the remainder |

---

## 10. Update Check

Run only when the user explicitly requests it (e.g. "update the notebooklm plugin"). Never run automatically.

1. **Confirm** — ask *"It looks like you want to check the NotebookLM plugin for upstream updates. Is that right?"* Abort if no.

2. **Fetch in parallel:**
   - Upstream SKILL.md: `https://raw.githubusercontent.com/teng-lin/notebooklm-py/refs/heads/main/src/notebooklm/data/SKILL.md`
   - Upstream README: `https://raw.githubusercontent.com/teng-lin/notebooklm-py/refs/heads/main/README.md`
   - Re-read this file as the baseline.

3. **CLI version check:**
   ```bash
   notebooklm --version
   pip index versions notebooklm-py 2>/dev/null | head -1
   ```
   If a newer version exists, ask before upgrading: `pip install --upgrade "notebooklm-py[browser]"`.

4. **Scope filter** — compare upstream only against commands and flags this plugin already references. Ignore language settings, bulk import, sharing, and anything else this plugin has never covered.

5. **Change report** — list each relevant diff (section, current text, upstream text, one-line impact). Ask: apply all / select / skip.

6. **Apply with preview** — for each approved change, show old → new text and confirm before writing to `notebooklm.md`. Summarise what changed when done.
