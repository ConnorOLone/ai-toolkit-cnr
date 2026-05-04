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

## Setup

### Interactive manager (recommended)

```sh
python3 manage.py              # first run — from the repo
python3 manage.py --install-cli  # install the 'aitk' global command
aitk                           # run from anywhere after install
```

Cross-platform interactive CLI. Shows all available assets (skills, agents, rules, hooks, configs), their install status, and lets you toggle them on/off. Works on macOS and Windows. Requires [uv](https://docs.astral.sh/uv/) for the global `aitk` command.

### Batch install (all assets)

**macOS:**
```sh
./scripts/install.sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy Bypass -File scripts\install.ps1
```

Installs everything. macOS uses symlinks; Windows uses copies (re-run after updating).

## Docs

- [Skills](https://code.claude.com/docs/en/skills.md)
- [Hooks](https://code.claude.com/docs/en/hooks.md)
- [Settings](https://code.claude.com/docs/en/settings.md)
- [MCP](https://code.claude.com/docs/en/mcp.md)
