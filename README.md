# ai-toolkit-cnr

Personal collection of AI-related tools, configurations, and automations for Claude Code and other AI workflows.

## Structure

```
skills/          — Claude Code skills (directory-based with SKILL.md + frontmatter)
agents/          — Custom subagent definitions
rules/           — Path-specific instruction rules
hooks/           — Claude Code hooks (shell scripts triggered by events)
scripts/         — Standalone utility scripts
prompts/         — Reusable prompt templates and system prompts
mcp/             — MCP server configurations and custom servers
configs/         — Shared configuration files (settings.json fragments, keybindings, etc.)
examples/        — Reference templates (not symlinked — copy to create new assets)
```

## Usage

Each directory contains its own README with conventions and docs links.

## Setup (macOS)

```sh
./scripts/install.sh
```

Symlinks skills, agents, and rules into `~/.claude/`. Examples are never symlinked.

On Windows, pull and copy manually.

## Docs

- [Skills](https://code.claude.com/docs/en/skills.md)
- [Hooks](https://code.claude.com/docs/en/hooks.md)
- [Settings](https://code.claude.com/docs/en/settings.md)
- [MCP](https://code.claude.com/docs/en/mcp.md)
