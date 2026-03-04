# Skills

A collection of reusable AI agent skills — modular packages that extend agent capabilities with specialized knowledge, workflows, and bundled resources.

| Skill | Description |
|-------|-------------|
| [astro-starlight-charts](.agents/skills/astro-starlight-charts/SKILL.md) | Conventions, recipes, and anti-patterns for building static SVG chart components with Astro and D3. |

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
