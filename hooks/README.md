# Hooks

Shell scripts and configurations for Claude Code hooks (pre/post tool-call automations).

## Installation

Add hook entries to your Claude Code `settings.json`. See `configs/` for examples.

## Conventions

- Scripts should be executable (`chmod +x`)
- Name scripts descriptively: `<event>-<purpose>.sh`
- Include a comment header describing trigger conditions
