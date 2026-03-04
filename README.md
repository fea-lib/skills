# Skills

A collection of reusable AI agent skills — modular packages that extend agent capabilities with specialized knowledge, workflows, and bundled resources.

## Structure

```
.agents/skills/<skill-name>/   # One directory per skill
docs/                          # Guides, ADRs, and other human-facing docs
```

Each skill contains a `SKILL.md` (required) and optionally `scripts/`, `references/`, and `assets/`.

## Skills

| Skill | Description |
|-------|-------------|
| [astro-starlight-charts](.agents/skills/astro-starlight-charts/SKILL.md) | Conventions, recipes, and anti-patterns for building static SVG chart components with Astro and D3. |

## Contributing

See `AGENTS.md` for conventions on creating and maintaining skills.

## Sources

Resources used to establish the conventions in `AGENTS.md`:

- [Building effective agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [skill-creator — anthropics/skills](https://skills.sh/anthropics/skills/skill-creator)
