# Hooks

Shell scripts and configurations for Claude Code hooks (pre/post tool-call automations).

## Installation

Install a hook with `aitk` — it copies the script into `~/.claude/hooks/` **and**
registers it in `~/.claude/settings.json`, reading the event from the script's
`# Event:` / `# Matcher:` header. Uninstalling a hook removes the registration.
`aitk status` shows each installed hook's registration state.

To register a hook by hand instead, add the entry to `settings.json` yourself —
see `configs/` for examples.

## Conventions

- Scripts should be executable (`chmod +x`)
- Name scripts descriptively: `<event>-<purpose>.sh`
- Include an `# Event:` header line (and `# Matcher:` for tool events) — `aitk`
  reads these to register the hook automatically
