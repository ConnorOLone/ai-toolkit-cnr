# ai-toolkit-cnr

Personal collection of AI-related tools, configurations, and automations for Claude Code and other AI workflows.

## Structure

```
skills/          — Claude Code skills (directory-based with SKILL.md + frontmatter)
agents/          — Custom subagent definitions
rules/           — Path-specific instruction rules
hooks/           — Claude Code hooks (shell scripts triggered by events)
output-styles/   — Custom output styles (system-prompt .md files)
scripts/         — Standalone utility scripts
prompts/         — Reusable prompt templates and system prompts
mcp/             — MCP server configurations and custom servers
configs/         — Shared configuration files (settings.json fragments, keybindings, etc.)
claude-shell/    — PowerShell module for terminal-side Claude (sourced from $PROFILE)
examples/        — Reference templates (not symlinked — copy to create new assets)
```

## Usage

Each directory contains its own README with conventions and docs links.

## Workflow tools

User-invocable slash commands that codify the two-loop development workflow.
Once installed via `aitk`, run them in any project:

| Trigger | Use when |
|---|---|
| `/plan <brief>` | You have an idea but not yet a plan. Dispatches `explorer` + `planner` (+ optional `critic`) and writes the plan to `.claude/plans/<slug>.md`. |
| `/tdd <task>` | You have an approved plan and want to ship a single task. Red test → green implementation → one commit. |
| `/review [ref]` | Implementation is done. Fresh-context review by `code-reviewer` + `security-reviewer` in parallel. |
| `/harness` | End of session. Reviews friction, proposes one concrete harness improvement (rule / hook / skill update / CLAUDE.md line). |
| `agent-workflow` skill | Parallel work across multiple agents — see `skills/agent-workflow/` and `agentctl`. |

## Setup

### Claude-guided setup (recommended)

Clone the repo, open Claude Code, and say:

```
follow setup.md
```

Claude will handle everything: install assets, set up the `aitk` CLI, register hooks, and verify the setup. Works on macOS and Windows.

### Interactive manager

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
