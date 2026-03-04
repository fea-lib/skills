# Source Types: Handling Guide

How to discover, fetch, and extract value from each resource type. Read the relevant section(s) before working with a new source type in a session.

---

## Table of Contents

1. [Web Pages & URLs](#1-web-pages--urls)
2. [Local Files](#2-local-files)
3. [Academic Papers & arXiv](#3-academic-papers--arxiv)
4. [Code Repositories](#4-code-repositories)
5. [YouTube & Video Content](#5-youtube--video-content)
6. [General Source Discovery](#6-general-source-discovery)

---

## 1. Web Pages & URLs

**Tool:** WebFetch (markdown format preferred for content extraction)

**Fetch strategy:**
- Fetch the primary URL first. If it redirects to a different host, follow the redirect immediately with a new WebFetch call.
- For long pages, skim headings and summary sections first; fetch subsections if needed.
- For paywalled content, try to find an open-access version (author's site, preprint, DOI resolver).

**Quality signals to extract:**
- Author name and credentials (byline, about page)
- Publication/organisation name and reputation
- Publication date (look for `<time>`, `datePublished` metadata, or footer)
- Last-updated date (distinct from publish date — important for fast-moving topics)
- Editorial standards (is this a peer-reviewed outlet, a personal blog, a PR piece?)
- External links cited (does it reference primary sources, or is it self-referential?)

**Red flags:**
- No author, no date, no external citations
- Domain is a content farm or SEO-optimised affiliate site
- Claims are extraordinary without primary source links
- Heavy promotional framing

---

## 2. Local Files

**Tools:** Read (for text/markdown/code), Glob (to discover files by pattern)

**Strategy by file type:**

| File type | Approach |
|-----------|----------|
| `.md`, `.txt`, `.rst` | Read directly. Note creation/modification date from filesystem if relevant. |
| `.pdf` | Read directly — the Read tool handles PDFs and returns them as attachments. Extract key sections; don't load the entire file into context if it is very long — read in chunks. |
| `.json`, `.yaml`, `.csv` | Read and interpret structure. For large data files, read a representative sample. |
| Source code files | Treat as structured evidence — see Section 4 (Code Repositories). |
| `.docx`, `.pptx` | If a dedicated skill (e.g. `docx`) is available, use it. Otherwise, attempt Read and extract what is accessible. |

**Quality signals:**
- For internal documents: who authored it and when? Is it a draft or final?
- For data files: what is the provenance? Is there a README or metadata file alongside?
- For code: is it tested, documented, actively maintained?

---

## 3. Academic Papers & arXiv

**Tools:** WebFetch (for arXiv abstract and PDF pages), Read (if PDF is local)

**arXiv URL patterns:**
- Abstract page: `https://arxiv.org/abs/<id>` — fetch this first (title, authors, abstract, submission date)
- PDF: `https://arxiv.org/pdf/<id>` — fetch only if the abstract is insufficient
- HTML version (better for extraction): `https://arxiv.org/html/<id>` — preferred over PDF when available

**Strategy:**
1. Fetch the abstract page first. Extract: title, authors, affiliation, submission date, abstract, subject category.
2. Check whether it has been published in a peer-reviewed venue (look for "Submitted to" or journal reference in the metadata).
3. If the abstract is insufficient, fetch the HTML or PDF version and focus on: Introduction, Conclusion, and any figures/tables directly relevant to the research question.
4. Note the citation count if accessible (e.g. via Google Scholar or Semantic Scholar URLs).

**Quality signals:**
- Peer-reviewed publication vs preprint-only
- Author affiliation (academic institution, industry lab, independent)
- Submission date and whether it has been updated (v1 vs v3 etc.)
- Citation count (a rough proxy for community uptake — high citation ≠ correct, but low citation on an old paper is a signal)
- Replication studies or critiques citing this paper

**For non-arXiv academic sources:**
- DOI links: try `https://doi.org/<doi>` — often resolves to publisher page or open-access PDF
- PubMed: `https://pubmed.ncbi.nlm.nih.gov/<id>/` for biomedical literature
- Semantic Scholar: `https://api.semanticscholar.org/graph/v1/paper/search?query=<title>` for metadata

---

## 4. Code Repositories

**Tools:** WebFetch (for GitHub/GitLab web views), Read/Glob (for local repos)

**Treat repositories as structured, layered sources.** Read in this order — stop when you have enough:

1. **README** — purpose, architecture overview, status, usage
2. **CHANGELOG or releases** — trajectory and recency of active development
3. **Open issues and PRs** — known problems, community health, contested design decisions
4. **Tests** — what behaviour is actually guaranteed vs aspirational
5. **Core source files** — for technical detail when README is insufficient

**GitHub URL patterns (WebFetch):**
- Repo root: `https://github.com/<org>/<repo>`
- Raw file: `https://raw.githubusercontent.com/<org>/<repo>/main/<path>`
- Issues: `https://github.com/<org>/<repo>/issues`
- Releases: `https://github.com/<org>/<repo>/releases`

**Quality signals:**
- Stars, forks, contributor count (community adoption)
- Last commit date (is it actively maintained?)
- Open vs closed issue ratio
- Presence of tests and CI
- Licence (relevant if the research is about reuse or adoption)

---

## 5. YouTube & Video Content

**Skill-aware strategy — check at runtime:**

1. Check whether a `youtube-summarizer` skill (or equivalent video/transcript skill) is available in the active skill list.
   - If yes: use it. It will handle transcript extraction and summarisation with optimised tooling.
   - If no: proceed with the fallback below.

**Fallback (no dedicated skill):**
- Fetch the YouTube page with WebFetch: `https://www.youtube.com/watch?v=<id>`
- Extract: title, channel, upload date, description (often contains timestamps and key points)
- Try fetching the auto-generated transcript via: `https://www.youtube.com/api/timedtext?v=<id>&lang=en`
- If transcript is unavailable, use the description + any linked resources (slides, papers, blog posts in the description) as proxies for content.

**Quality signals:**
- Channel authority (official org, known expert, general content creator)
- Upload date
- View count and engagement (rough proxy — not a quality signal on its own)
- Whether the content is a primary presentation (conference talk, tutorial) or secondary commentary

---

## 6. General Source Discovery

When the user has not provided specific sources, use these strategies to find them:

**For current events / recent developments:**
- WebFetch on news aggregators or official sources directly
- Search-style queries via WebFetch on sites like `site:arxiv.org <topic>` or `site:github.com <topic>`

**For technical topics:**
- Official documentation sites first
- arXiv for cutting-edge research
- GitHub for implementations and adoption evidence

**For business / market research:**
- Company official sites, annual reports, press releases
- Industry analyst reports (Gartner, Forrester — note: often paywalled)
- Crunchbase, LinkedIn for company/people data

**For breadth on an unknown topic:**
- Start with a high-quality overview source (Wikipedia is acceptable as an orientation source, not a primary citation)
- Follow its references to primary sources
- Cross-check across at least 3 independent sources before treating a claim as established

**If the NotebookLM plugin is active:**
Use `notebooklm source add-research "<query>" --mode deep` as the primary discovery mechanism
(see `references/plugins/notebooklm.md`, Section 2). The WebFetch-based strategies in this
section serve as a fallback if the NLM research agent returns fewer than 4 sources, or if
NotebookLM is unavailable for this session.

**Secondary source approval:**
After primary sources are analysed, compile a list of promising secondary leads and present them to the user before fetching:

```
I've identified these secondary sources worth following:
1. [Title / URL] — reason it's relevant
2. [Title / URL] — reason it's relevant

Shall I fetch and analyse these? You can approve all, select a subset, or skip.
```

Wait for the user's response before proceeding.
