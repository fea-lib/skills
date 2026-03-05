# Plugin Index

This file is the authoritative registry of available plugins for the research skill.
Load it at Step 1 intake to present available integrations to the user.

Each entry lists the plugin file, a one-line user-facing description, and the prerequisites
the user needs to use it. The agent uses this list to build the dynamic activation question.

## Available Plugins

| Plugin | File | User-facing description | Prerequisites | Updating |
|--------|------|------------------------|---------------|---------|
| NotebookLM | `plugins/notebooklm.md` | Google NotebookLM — indexes all sources and answers cross-source questions via RAG; produces a briefing doc as a second output artifact | `pip install "notebooklm-py[browser]"` + `python3 -m playwright install chromium`; Google account | Say "update the notebooklm plugin" to sync with upstream CLI changes (see plugin Section 9) |

---

## How to add a new plugin

1. Create `references/plugins/<plugin-name>.md` following the 8-section plugin contract
   defined at the bottom of `SKILL.md`.
2. Add a row to the table above.
3. No changes to `SKILL.md` are needed — the generic activation question reads from this index.
