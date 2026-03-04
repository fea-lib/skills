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

Install, update, and list skills using the `skill.sh` script via `curl`:

```bash
# List all available skills
curl -fsSL https://raw.githubusercontent.com/fea-lib/skills/main/scripts/skill.sh | bash -s list

# Install a skill (defaults to ~/.agents/skills/<skill-name>)
curl -fsSL https://raw.githubusercontent.com/fea-lib/skills/main/scripts/skill.sh | bash -s install <skill-name>

# Install to a specific directory (/your/target/dir/<skill-name>)
curl -fsSL https://raw.githubusercontent.com/fea-lib/skills/main/scripts/skill.sh | bash -s install <skill-name> --path /your/target/dir

# Update an installed skill
curl -fsSL https://raw.githubusercontent.com/fea-lib/skills/main/scripts/skill.sh | bash -s update <skill-name>
```

**Install** copies the skill to the target directory. You will be prompted to confirm the path before anything is written.

**Update** looks for the installed skill in `./.agents/skills/` then `~/.agents/skills/`, and prompts if neither is found. If any local files differ from the remote version, you are warned and can abort before anything is overwritten.

**Dependencies:** `git`, `curl` — both standard on macOS and Linux.
