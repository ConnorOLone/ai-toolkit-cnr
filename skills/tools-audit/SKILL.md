---
name: tools-audit
description: Use when auditing or updating the toolkit's Claude Code tools reference to match the current session's available tools
user-invocable: true
argument-hint: "[--apply]"
---

# Tools Audit

Compare the tools reference file against the tools actually available in this Claude Code session and apply any updates.

## How to run

1. Read `~/.claude/.toolkit-path` to find the toolkit repo (`TOOLKIT_DIR`).
2. Read `TOOLKIT_DIR/configs/tools.json` — this is the current tools reference (a flat JSON object mapping tool names to descriptions).
3. Compare against the tools available in your current session. You know what tools you have — check your own tool list. Exclude MCP tools (prefixed with `mcp__`).
4. Report:
   - **Added** — tools available now but missing from `tools.json`
   - **Removed** — tools in `tools.json` that are no longer available
   - **Changed** — tools whose behavior has shifted enough that the description should be updated
5. If no differences found, report that the reference is up to date and stop.
6. If the user passed `--apply` or confirms the changes, write the updated JSON to `TOOLKIT_DIR/configs/tools.json`. Keep keys sorted alphabetically. Use 2-space indentation.
7. Run `python3 TOOLKIT_DIR/manage.py tools` to verify the output looks correct.

## Description style

- One line per tool, starting with a verb
- Concise — describe what it does, not how to use it
- Include parenthetical examples only where the name is ambiguous (e.g. Bash, Glob)
