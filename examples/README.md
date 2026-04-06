# Examples

Reference examples for skills, agents, rules, hooks, and configs.

These are **not symlinked** — they exist purely as templates to copy from when creating new assets. This keeps symlinked directories clean.

## Structure

```
examples/
  skills/
    hello-world/SKILL.md       — Minimal user-invocable skill
  agents/
    reviewer.md                — Minimal custom agent definition
  rules/
    code-style.md              — Path-specific rule example
  hooks/
    pre-commit-lint.sh         — Hook script example
  configs/
    settings.example.json      — Settings with permissions + hooks
```
