# Output Styles

Custom output styles for Claude Code — Markdown files that modify the system
prompt to change Claude's role, tone, or default response format.

Installed to `~/.claude/output-styles/`. Select one with `/config` →
**Output style**, or set the `outputStyle` key in `settings.json`.

## Format — `output-styles/<name>.md`

```yaml
---
name: Display Name               # optional — defaults to the file name
description: Shown in /config    # optional
keep-coding-instructions: false  # keep Claude's built-in coding instructions
---

Instructions appended to the system prompt...
```

## Conventions

- One `.md` file per style; the file name is the style name unless `name` is set
- Set `keep-coding-instructions: true` if Claude should still write code the
  same way — leave it `false`/unset for non-coding assistants
- Create one with `aitk new output-style <name>`, install it with `aitk`

## Docs

- https://code.claude.com/docs/en/output-styles.md
