# CopperRiver Skills

Curated skill library for [CopperRiver](https://github.com/copperriver) and compatible agents (Claude Code, Codex, Hermes).

## Structure

```
skills/
├── official/        # Skills built and maintained by CopperRiver
├── community/       # Community-contributed skills
└── claude-packs/    # Adapted from Claude Code skill packs
```

## Skill Format

Each skill is either a standalone `.md` file or a folder with `SKILL.md`:

```
my-skill/
├── SKILL.md          # Required
├── scripts/          # Optional
├── references/       # Optional
└── assets/           # Optional
```

### SKILL.md Frontmatter

```yaml
---
name: my-skill            # lowercase, hyphens, max 64 chars
description: What + when  # max 1024 chars
version: 1.0.0
category: browser|coding|media|integration|system
source: copperriver       # provenance tracking
---
```

Follows the [Agent Skills](https://agentskills.io) open standard.

## Compat

Skills work across:
- CopperRiver
- Claude Code
- OpenAI Codex
- Nous Research Hermes

## License

MIT unless otherwise noted in skill folder.
