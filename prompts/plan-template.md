---
name: plan-template
description: Strict format for plans produced by the planner agent and /plan skill
---

# Plan template

The planner agent emits plans in this format. The human authors plans in this format too.
One schema for both keeps `/plan`, `/tdd`, and `/review` interoperable.

Sections in order. Headings are literal — keep them.

---

## Context

Why this change. The problem or need; what prompted it; the intended outcome.
2–5 sentences. No restatement of the request.

## Approach

One recommended approach. Not a menu. Terse.
For each non-obvious choice, one line of justification (`X — because Y, not Z`).
If multiple subsystems are involved, sub-headings per subsystem.

## Critical files

Build these first; everything else follows from them. Ordered list of file paths,
each with one line on why it's critical (defines a contract / unlocks the rest /
single highest-leverage change). 3–8 entries.

```
1. path/to/file.ext — why it's first
2. path/to/file.ext — why it follows
...
```

## Verification

How to confirm the change actually works end-to-end. Concrete steps, not assertions.
Prefer commands the user can run, observable behaviors, or specific tests.

## NOT included (and why)

Things that would be reasonable additions but are deliberately deferred or rejected.
Each entry: one-line scope + one-line reason. This section is load-bearing —
it prevents scope creep and documents the road not taken for future revisits.

---

## Conventions

- No "alternatives considered" section unless the user explicitly asks. The recommended approach is the plan.
- No estimates unless asked.
- Connor mode: terse, decisions justified, redundancy flagged.
- If something can't be decided without input, surface it as a question to the user before writing the plan, not as a TODO in the plan.
