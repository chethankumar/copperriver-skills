# CopperRiver Skills

Curated skill library for [CopperRiver](https://github.com/chethankumar/copperriver) and compatible agents (Claude Code, Codex, Hermes).

## Structure

```
skills/
├── official/        # Skills built and maintained by CopperRiver
├── community/       # Community-contributed skills
└── claude-packs/    # Adapted from Claude Code skill packs
```

## Skill Format (Standard)

Every skill follows the [Agent Skills](https://agentskills.io) open standard:

```
skill-name/
├── SKILL.md          # Required — metadata + instructions
├── scripts/          # Optional — executable code
├── references/       # Optional — documentation loaded on demand
└── assets/           # Optional — templates, resources
```

### SKILL.md Frontmatter

```yaml
---
name: skill-name          # lowercase, hyphens, max 64 chars, MUST match dir name
description: What + when  # max 1024 chars
version: 1.0.0
category: browser | coding | media | integration | system
source: copperriver       # provenance: copperriver | community | claude-code
---
```

### Categories

| Category | Description |
|----------|-------------|
| `browser` | Browser tab automation, web interaction |
| `coding` | Code quality, generation, development |
| `media` | Document/PDF/video creation and editing |
| `integration` | Third-party services (Slack, X, MCP) |
| `system` | OS-level automation, search, monitoring |

## Compatibility

Skills work across:
- **CopperRiver** — native
- **Claude Code** — drop into `.claude/skills/`
- **OpenAI Codex** — drop into skills dir, supports `.claude-plugin/` manifest
- **Nous Research Hermes** — drop into `skills/`

The standard frontmatter (`name` + `description`) is the cross-tool compatible core. Unknown fields are ignored gracefully.

## Available Skills

### Official (8)
| Name | Category | Description |
|------|----------|-------------|
| browser-control | browser | Control CopperRiver browser tabs via CDP |
| coding | coding | Guidelines to reduce common LLM coding mistakes |
| computer-use | system | Universal macOS desktop automation |
| computer-use-quick-ref | system | Quick reference for desktop automation |
| deliberation | system | Multi-model deliberation for high-stakes tasks |
| hyperframes | media | Animated video compositions using HTML+CSS+GSAP |
| mcp | integration | Access any MCP server's tools from bash |

### Claude Code Packs (8)
| Name | Category | Description |
|------|----------|-------------|
| docx | media | Document creation and editing |
| pdf | media | PDF manipulation toolkit |
| pptx | media | Presentation creation and editing |
| xlsx | media | Spreadsheet creation and editing |
| skill-creator | coding | Guide for creating effective skills |
| redesign-skill | coding | Upgrade websites to premium quality |
| website-gen | coding | Generate production-quality HTML websites |
| full-output | coding | Overrides default truncation |

### Community (1)
| Name | Category | Description |
|------|----------|-------------|
| design-taste-frontend | coding | Senior UI/UX engineering guidelines |

## Contributing

1. Fork this repo
2. Create your skill under `skills/community/your-skill/SKILL.md`
3. Add it to `.copperriver/marketplace.json`
4. Submit a PR

## License

MIT unless otherwise noted in skill folder.
