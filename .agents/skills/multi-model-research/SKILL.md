---
name: multi-model-research
description: >
  Run the same research task across multiple models in parallel, compare their
  outputs anonymously, and synthesise one final report. Use when the user asks
  for multi-model research, wants multiple models to cross-check each other, or
  wants a result less shaped by one model's blind spots.
---

# Multi-Model Research

Variants are anonymised to other models via tokenised filenames. A model may still
recognise its own prior output, but does not know which other model produced the
remaining variants.

## How to run

**1. Get default models** (if `--models` not supplied by user):

```bash
opencode models | python scripts/run.py list-defaults
```

`list-defaults` checks `config.yaml` first. If configured models are found, those are used.
If not, it falls back to auto-selecting the highest-ranked Claude and GPT models.

If fewer than 2 models are returned, ask the user to select models manually before continuing.

## Configuration (--config flag)

When the user invokes the skill with `--config`, run the configuration flow instead of a research task:

**1. Fetch all available models:**

```bash
opencode models | python scripts/run.py list-models
```

This prints a JSON array of all available model IDs.

**2. Present the list as a multi-select to the user.** Let them pick the models they want to use as defaults. No minimum enforced here — if fewer than 2 are selected, `init` will fail with an existing error message.

**3. Persist the selection:**

```bash
python scripts/run.py config --set "<model-a>,<model-b>,..."
```

Confirm to the user how many models were saved and to which file.

To inspect the current config at any time:

```bash
python scripts/run.py config --show
```

The config is stored in `config.yaml` inside the skill directory. Delete or edit it manually to reset or adjust. When no `config.yaml` exists, the skill auto-selects models as before.

**2. Initialise the run** (emits Round 1 subagent commands):

```bash
python scripts/run.py init \
  --topic "<topic>" \
  --out-dir "<path>" \
  --models "<model-a>,<model-b>" \
  [--depth N] [--criteria <path>] [--audit-model <model>] [--output-file <path>] [--debug]
```

`--out-dir` default: derive a kebab-case slug from the topic → `./research/<slug>/`

**3. Execute each phase** as the script emits commands, then call back:

```bash
python scripts/run.py score-round --out-dir "<path>" --round N
python scripts/run.py finalize   --out-dir "<path>"
python scripts/run.py deliver    --out-dir "<path>"
```

If `score-round` prints `RERUN_REQUIRED: <filename>`, rerun that subagent once with
the same inputs. If the rerun also fails, remove that comparator's file and call
`score-round` again — the script will exclude it and log the exclusion. If all
comparators fail, halt and report to the user.

## Failure handling

If the script exits with an error, report it verbatim to the user. Do not retry
autonomously — ask whether to resume or abort.

## References

| File | Purpose |
|------|---------|
| `references/criteria.md` | Default scoring criteria — edit to customise weights or add criteria |
| `references/prompts.md` | Phase prompt templates — edit to tune wording |
| `references/score-extraction.md` | Score block format (for debugging malformed blocks) |
