# CLAUDE.md

This repository stores AI-related tools: skills, hooks, scripts, prompts, MCP servers, and configs.

## Project layout

- `skills/` — Claude Code skills (directory-based, each with `SKILL.md` + frontmatter)
- `agents/` — Custom subagent definitions (`.md` files with frontmatter)
- `rules/` — Path-specific instruction rules (`.md` files with `paths:` frontmatter)
- `hooks/` — Shell scripts for Claude Code hook events
- `output-styles/` — Custom output styles (`.md` files with frontmatter)
- `scripts/` — Standalone utility scripts
- `prompts/` — Reusable prompt templates
- `mcp/` — MCP server source code
- `configs/` — Settings fragments, keybindings, MCP configs
- `claude-shell/` — PowerShell module for terminal-side Claude, sourced from `$PROFILE` (not a Claude Code asset; not installed by `aitk`)
- `examples/` — Reference templates (not symlinked — copy from here to create new assets)

## Conventions

- No secrets in version control — use `.env` or env var references
- Each directory has its own README with usage instructions
- Skills use the directory-based format: `skills/<name>/SKILL.md` with YAML frontmatter
- Keep skill/agent/rule directories clean — examples go in `examples/` only
- Hook scripts must be executable and carry an `# Event:` header — `aitk`
  registers/unregisters them in `~/.claude/settings.json` on install/uninstall

## Official Documentation

Always refer to these for the latest Claude Code best practices:

- Skills: https://code.claude.com/docs/en/skills.md
- Hooks: https://code.claude.com/docs/en/hooks.md
- Settings: https://code.claude.com/docs/en/settings.md
- MCP: https://code.claude.com/docs/en/mcp.md
- Claude Code overview: https://code.claude.com/docs/en/overview.md
