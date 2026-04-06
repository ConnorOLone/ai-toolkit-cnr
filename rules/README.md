# Rules

Path-specific instruction files for Claude Code (`.claude/rules/`).

Rules are like CLAUDE.md fragments that only load when working on matching files.

## Structure

Each rule is a `.md` file with optional `paths:` frontmatter:

```yaml
---
paths:
  - "src/**/*.ts"
  - "tests/**/*.test.ts"
---

Instructions that apply only when these files are in context...
```

Rules without `paths:` frontmatter are always loaded.

## Installation

Run `./scripts/install.sh` to symlink all rules into `~/.claude/rules/`.

## Docs

https://code.claude.com/docs/en/skills.md
