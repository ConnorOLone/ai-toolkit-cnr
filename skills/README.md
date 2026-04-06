# Skills

Custom Claude Code skills using the recommended directory-based structure.

## Structure

Each skill is a directory containing a `SKILL.md` with YAML frontmatter:

```
skills/
  my-skill/
    SKILL.md          # Required — skill instructions + frontmatter
    templates/        # Optional — supporting files referenced via ${CLAUDE_SKILL_DIR}
```

Keep skill directories clean — no examples or scratch files. Use `examples/skills/` for reference templates.

## Frontmatter Reference

```yaml
---
name: my-skill
description: What this skill does
user-invocable: true              # Show in /menu (default: true)
disable-model-invocation: false   # Prevent Claude auto-invoking (default: false)
allowed-tools: Read Grep Edit     # Tools available to the skill
argument-hint: "[issue-number]"   # Autocomplete hint for arguments
model: sonnet                     # Override model
effort: high                      # Effort level: low/medium/high/max
context: fork                     # Run in isolated subagent
agent: Explore                    # Subagent type
paths: "src/**"                   # Only activate for matching paths
---
```

| Setting | User can invoke | Claude can invoke |
|:--------|:----------------|:------------------|
| (default) | Yes | Yes |
| `disable-model-invocation: true` | Yes | No |
| `user-invocable: false` | No | Yes |

## Installation

Run `./scripts/install.sh` to symlink all skills into `~/.claude/skills/`.

## Docs

https://code.claude.com/docs/en/skills.md
