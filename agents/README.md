# Agents

Custom subagent definitions for Claude Code.

## Structure

Each agent is a `.md` file with YAML frontmatter:

```yaml
---
name: my-agent
description: What this agent does
allowed-tools: Read Grep Glob
model: sonnet
---

System prompt instructions here...
```

## Installation

Run `./scripts/install.sh` to symlink all agents into `~/.claude/agents/`.

## Docs

https://code.claude.com/docs/en/skills.md (agents section)
