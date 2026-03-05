# Skills

A collection of reusable AI agent skills — modular packages that extend agent capabilities with specialized knowledge, workflows, and bundled resources.

| Skill | Description |
|-------|-------------|
| [agentic-dev-workflow](.agents/skills/agentic-dev-workflow/SKILL.md) | Orchestrates a structured 8-phase agentic development lifecycle (Idea → Research → PRD → Plan → Refine → Execution → QA) with resumable state and artifact contracts. |
| [adw-idea](.agents/skills/adw-idea/SKILL.md) | Phase 1 of the agentic-dev-workflow: clarifies the task, derives the slug, and produces the phase plan artifact. |
| [adw-research](.agents/skills/adw-research/SKILL.md) | Phase 2 of the agentic-dev-workflow: explores the codebase and produces a research handoff artifact for downstream phases. |
| [adw-prototype](.agents/skills/adw-prototype/SKILL.md) | Phase 3 of the agentic-dev-workflow (optional): throwaway spike to resolve UI/UX or architectural uncertainty before writing the PRD. |
| [adw-prd](.agents/skills/adw-prd/SKILL.md) | Phase 4 of the agentic-dev-workflow: translates research into a PRD with testable acceptance criteria and an explicit out-of-scope list. |
| [adw-plan](.agents/skills/adw-plan/SKILL.md) | Phase 5 of the agentic-dev-workflow: decomposes the PRD into implementation tickets with explicit blocking dependencies. |
| [adw-refine](.agents/skills/adw-refine/SKILL.md) | Phase 6 of the agentic-dev-workflow: reviews tickets for gaps and missing acceptance criteria, then gates on human sign-off before execution. |
| [adw-execution](.agents/skills/adw-execution/SKILL.md) | Phase 7 of the agentic-dev-workflow: implements tickets in dependency order, producing a Merge-Readiness Pack or Consultation Request Pack. |
| [adw-qa](.agents/skills/adw-qa/SKILL.md) | Phase 8 of the agentic-dev-workflow: produces a human-in-the-loop verification checklist and rollback plan for the completed implementation. |
| [astro-starlight-charts](.agents/skills/astro-starlight-charts/SKILL.md) | Conventions, recipes, and anti-patterns for building static SVG chart components with Astro and D3. |
| [research](.agents/skills/research/SKILL.md) | Structured research support: finding and analysing resources, answering questions from evidence, and producing a documented research report. |

## Structure

```
.agents/skills/<skill-name>/   # One directory per skill
docs/                          # Guides, ADRs, and other human-facing docs
```

Each skill contains a `SKILL.md` (required) and optionally `scripts/`, `references/`, and `assets/`.

## Contributing

See `AGENTS.md` for conventions on creating and maintaining skills.

## Sources

Resources used to establish the conventions in `AGENTS.md`:

- [Building effective agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [skill-creator — anthropics/skills](https://skills.sh/anthropics/skills/skill-creator)

## Scripts

Install, update, and list skills using the `skill.sh` script via `curl`. Dependencies: `git`, `curl` — both standard on macOS and Linux.

### list

Lists all skills available in the repository.

```bash
curl -fsSL https://raw.githubusercontent.com/fea-lib/skills/main/scripts/skill.sh | bash -s list
```

### install

Copies the skill to `<path>/.agents/skills/<skill-name>` (defaults to `~/.agents/skills/<skill-name>`). You will be prompted to confirm the path before anything is written.

```bash
curl -fsSL https://raw.githubusercontent.com/fea-lib/skills/main/scripts/skill.sh | bash -s install <skill-name>
```

To install to a specific directory:

```bash
curl -fsSL https://raw.githubusercontent.com/fea-lib/skills/main/scripts/skill.sh | bash -s install <skill-name> --path /your/target/dir
```

### update

Looks for the installed skill in `./.agents/skills/` then `~/.agents/skills/`, and prompts if neither is found. If any local files differ from the remote version, you are warned and can abort before anything is overwritten.

```bash
curl -fsSL https://raw.githubusercontent.com/fea-lib/skills/main/scripts/skill.sh | bash -s update <skill-name>
```
