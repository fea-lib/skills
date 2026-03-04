# Agent Instructions: AI Agent Skills Repository

This repository stores reusable AI agent skills. When helping with skill creation or maintenance,
follow the conventions and workflows described here.

---

## Repository Layout

```
.
├── AGENTS.md                  # This file
├── .agents/
│   └── skills/                # All skills live here (one directory per skill)
│       └── <skill-name>/
│           ├── SKILL.md       # Required: frontmatter + instructions
│           ├── scripts/       # Optional: executable code
│           ├── references/    # Optional: documentation loaded as needed
│           └── assets/        # Optional: files used in skill output
└── docs/                      # Non-skill reference documents (guides, ADRs, notes)
```

**Key rules:**
- Every skill goes under `.agents/skills/<skill-name>/` — never elsewhere.
- General documentation (guides, notes, architecture decisions, etc.) goes under `docs/` — never inside a skill directory.
- Skill directories contain only what an agent needs to execute the skill, plus any human-readable documentation about that specific skill (e.g. a `README.md`). General repository docs — guides, ADRs, notes not tied to a specific skill — go in `docs/`.

---

## What a Skill Is

A skill is a self-contained package that gives an AI agent specialized knowledge, workflows,
and/or reusable resources for a specific domain. Skills are loaded on demand — only when the
agent determines a task matches the skill's description.

Skills are **not** general documentation. They exist to reduce repeated effort and improve
consistency across many future invocations of the same type of task.

---

## Skill File: `SKILL.md`

Every skill requires exactly one `SKILL.md` with:

### Frontmatter (YAML)

```yaml
---
name: skill-name
description: >
  What this skill does and when to use it. Include specific trigger phrases and contexts.
  All "when to use" information belongs here — not in the body.
---
```

Only `name` and `description` are required. Do not add other frontmatter fields unless there
is a concrete need (e.g., `compatibility` for environment requirements).

**Writing a good description:**
- Describe both *what* the skill does and *when* to trigger it.
- Be specific about trigger contexts — err toward being a little "pushy" to avoid undertriggering.
- Do not put "When to Use" sections in the body — those are never read until after triggering.

### Body (Markdown)

- Keep under 500 lines. Split into `references/` files if approaching this limit.
- Use imperative/infinitive form for instructions.
- Explain *why* things matter — don't just list rules. Smart agents respond better to reasoning than rigid MUSTs.
- Reference any bundled resource files clearly, with guidance on when to read them.

---

## Bundled Resources

### `scripts/`
Executable code (Python, Bash, etc.) for tasks that are:
- Repeatedly rewritten from scratch across invocations
- Fragile or error-prone and require deterministic execution

Scripts eliminate a class of compounding errors: a small mistake early in a multi-step task
can cascade. Deterministic code removes that risk entirely. A strong signal that code belongs
here: the same helper appears independently across multiple task transcripts.

Scripts must be tested before including them in a skill.

### `references/`
Documentation loaded into context only when needed. Use for:
- Database or API schemas
- Domain knowledge, business logic, company policies
- Detailed workflow guides that would bloat `SKILL.md`

For files longer than ~100 lines, include a table of contents at the top.
Reference these files from `SKILL.md` with clear guidance on when to read them.

### `assets/`
Files used in skill *output* (not read into context). Use for:
- Templates (HTML, DOCX, PPTX, etc.)
- Boilerplate code starters
- Brand assets, fonts, icons

---

## Design Principles

### Context efficiency
The context window is shared. Every token costs something. Only include content that agents
could not reasonably derive on their own. Prefer examples over verbose explanations.

### Agent-computer interface (ACI)
Skill instructions are an interface — they deserve the same engineering attention as any
well-designed API or tool definition. Apply the same standard you would to writing a clear
docstring for a capable junior developer: explain parameters, state edge cases, clarify
boundaries with adjacent tools or steps. Ask yourself: *is it immediately obvious how to use
this, or does it require careful thought?* If the latter, the agent will also struggle.

This means:
- Name things so their purpose is self-evident
- Explain *why* a step matters, not just *what* to do — agents with reasoning context generalise
  better than agents following opaque rules
- State input format requirements and edge cases explicitly; don't assume the agent will infer them
- Avoid all-caps imperatives (ALWAYS, NEVER) as a substitute for motivation — if a constraint
  needs that emphasis, it probably needs a one-sentence explanation more

### Progressive disclosure
Skills load in three levels:
1. **Metadata** (name + description) — always present, ~100 words
2. **SKILL.md body** — loaded when the skill triggers
3. **Bundled resources** — loaded only when Claude determines they are needed

Keep `SKILL.md` lean. Move detailed content to `references/` files and point to them clearly.

### Degree of freedom
Match instruction specificity to the task's fragility:
- High freedom (prose): use when many approaches are valid
- Medium freedom (pseudocode/parameterized scripts): use when a preferred pattern exists
- Low freedom (specific scripts, precise steps): use when consistency or correctness is critical

### Simplicity discipline
Add structure only when it demonstrably improves outcomes. A skill that works well with a
short `SKILL.md` and no bundled resources is better than one padded with content that doesn't
change agent behaviour. The same principle applies internally: if a `references/` file would
never be needed, don't create it.

### Minimal context footprint
When creating or updating skill documents, prefer brevity over completeness. Omit anything an
agent can reasonably infer. Use bullet points over paragraphs, examples over explanations, and
`references/` files over inline content. The goal is the smallest document that produces correct
agent behaviour — not the most thorough one.

### Task parallelisation
When implementing a skill or working on tasks within this repository, identify independent
work units and execute them concurrently. For example: scaffold directory structure, read
existing files, and fetch external references can all happen in the same round-trip. Parallelism
reduces latency and keeps context lean by not accumulating unnecessary intermediate results.

### No auxiliary docs in skill directories
Skills should contain only what an agent needs to do the job. Do not create files like
`INSTALLATION_GUIDE.md`, `QUICK_REFERENCE.md`, `CHANGELOG.md`, or other meta documentation
that isn't directly useful for executing the skill. A `README.md` is acceptable if it
provides human-readable context about the skill itself. General repository docs go in `docs/`.

---

## Creating a New Skill

1. **Understand the use case** — gather concrete examples of how the skill will be used and
   what a user would say to trigger it.

2. **Plan reusable contents** — for each example, identify what scripts, references, or assets
   would help future invocations avoid repeating the same work.

3. **Initialize the skill** — create the directory under `.agents/skills/<skill-name>/` and
   scaffold its structure. Use the `init_skill.py` script from the `skill-creator` skill if available:
   ```bash
   python scripts/init_skill.py <skill-name> --path .agents/skills
   ```

4. **Implement resources** — write scripts, reference docs, and assets. Test any scripts.
   Remove unused example directories from the template.

5. **Write `SKILL.md`** — fill in frontmatter (`name`, `description`) and the body following
   the guidelines above. Remove any TODO placeholders from the scaffold.

6. **Update `README.md`** — add a row to the skills table at the top of `README.md` with the
   skill name (linked to its `SKILL.md`) and a one-sentence description taken from the frontmatter.

7. **Package** — use `package_skill.py` if distributing:
   ```bash
   python scripts/package_skill.py .agents/skills/<skill-name>
   ```

8. **Iterate** — test on real tasks and improve based on observed gaps. Watch transcripts,
   not just outputs: if agents independently write the same helper code across invocations,
   that code belongs in `scripts/`.

---

## Improving an Existing Skill

- Read the current `SKILL.md` and any referenced files before making changes.
- Prefer editing existing files over creating new ones.
- If adding new reference material, create a file in `references/` and link to it from
  `SKILL.md` with a note on when to read it.
- After changes, re-test on representative tasks to verify the improvement.

---

## Non-Skill Documentation

Any document that is not a direct part of a skill (guides, architecture notes, process docs,
ADRs, meeting notes, etc.) goes under `docs/` in the repository root — not inside any skill
directory.

Example:
```
docs/
├── skill-design-guide.md
├── conventions.md
└── adr/
    └── 001-skill-storage-layout.md
```
