---
name: toolkit
description: Use when the user wants to save, create, list, edit, or remove skills, agents, rules, hooks, scripts, prompts, or configs in their central AI toolkit. Also use when the user says "save this to the toolkit", "add this skill", or wants to manage AI tooling across devices.
user-invocable: true
allowed-tools: Read Write Edit Glob Grep Bash
argument-hint: "[action] [asset-type] [name] — e.g. 'add skill my-new-skill' or 'list agents'"
---

You are managing the user's central AI toolkit repository. This toolkit stores reusable Claude Code assets (skills, agents, rules, hooks, scripts, prompts, configs) that can be synced across devices and accounts.

## Finding the Toolkit

Read `~/.claude/.toolkit-path` — it contains the absolute path to the toolkit repo on this device. This file is written automatically by `manage.py` or the install scripts.

If the file doesn't exist, ask the user to run `python3 manage.py` from their toolkit repo first.

## Toolkit Structure

```
skills/<name>/SKILL.md    — Claude Code skills (directory-based)
agents/<name>.md          — Custom subagent definitions
rules/<name>.md           — Path-specific instruction rules
hooks/<name>.sh           — Shell scripts for hook events
scripts/<name>.py|sh      — Standalone utility scripts
prompts/<name>.md         — Reusable prompt templates
configs/<name>.json|md    — Settings fragments, CLAUDE.md templates
```

## Asset Formats

### Skills — `skills/<name>/SKILL.md`

```yaml
---
name: skill-name
description: Use when [triggering conditions]
user-invocable: true|false
disable-model-invocation: true|false
allowed-tools: Read Write Edit Glob Grep Bash
argument-hint: "[description of expected arguments]"
---

Skill instructions here...
```

- Directory-based: each skill gets `skills/<name>/SKILL.md`
- Name uses lowercase letters, numbers, hyphens only
- Description starts with "Use when..." — describes triggering conditions, not what the skill does
- Supporting files can live alongside SKILL.md in the same directory

### Agents — `agents/<name>.md`

```yaml
---
name: agent-name
description: What this agent does
allowed-tools: Read Grep Glob
model: sonnet
---

System prompt instructions here...
```

- Single `.md` file per agent
- Skip `README.md` (reserved for docs)

### Rules — `rules/<name>.md`

```yaml
---
paths:
  - "src/**/*.ts"
  - "tests/**/*.test.ts"
---

Instructions that apply only when matching files are in context...
```

- Single `.md` file per rule
- `paths:` frontmatter is optional — rules without it are always loaded
- Skip `README.md`

### Hooks — `hooks/<name>.sh`

```bash
#!/bin/bash
# Description of what this hook does
# Event: PreToolUse|PostToolUse|etc.
# Matcher: ToolName(pattern)
set -euo pipefail
input=$(cat)
# Exit 0 to allow, exit 2 to block
exit 0
```

- Must be executable (`chmod +x`)
- Include a comment header with event and matcher info
- The user must still register hooks in their settings.json

### Scripts — `scripts/<name>.py|sh`

- Standalone utilities, no special format required
- Shell scripts should be executable

### Prompts — `prompts/<name>.md`

- Markdown files with reusable prompt templates
- No required frontmatter

### Configs — `configs/<name>.json|md`

- Settings fragments, keybinding overrides, CLAUDE.md templates
- Use `.example` suffix for configs with placeholders

## Commands

Parse `$ARGUMENTS` for the action. Supported operations:

### `list [type]`
List available assets. If type is omitted, list all. Show name and description.

### `add <type> <name>`
Create a new asset. Ask the user for the content or generate it based on context. Follow the format templates above exactly.

### `edit <type> <name>`
Read and modify an existing asset.

### `remove <type> <name>`
Delete an asset. Confirm with the user before deleting.

### `show <type> <name>`
Display the full content of an asset.

### `sync`
Run `manage.py` instructions — remind the user to run `python3 manage.py` from the toolkit root to sync assets to this device.

### No arguments
If `$ARGUMENTS` is empty, list all assets with their install status and ask what the user wants to do.

## Important Rules

- Never put assets in `examples/` — that directory is for reference templates only
- Never commit secrets or API keys — use env var references
- Skip `README.md` files when listing assets (they're documentation, not assets)
- After creating or modifying an asset, remind the user to run `python3 manage.py` to sync changes to `~/.claude/`
- When creating skills, ensure the description follows CSO best practices: starts with "Use when...", describes triggering conditions only, written in third person
