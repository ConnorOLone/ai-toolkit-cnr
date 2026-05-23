---
name: brief-template
description: One-page brief the human authors before invoking /plan
---

# Brief

Outer-loop step 1. Frame the work in writing *before* asking the agent to plan.
The act of writing the brief is the value — it forces the constraints into the open.

Keep it under one page.

---

## Goal

One sentence. What changes when this is done. User-observable if possible.

## Constraints

What the solution must respect. Existing files, APIs, performance budgets,
permission boundaries, deadlines. Bullet list. Omit the section if none.

## Success criteria

How we'll know it worked. Prefer testable / observable criteria over feelings.
Example: "Running X command produces Y output", not "feels faster".

## Out of scope

Things the agent might assume but shouldn't do. Explicitly excluded.
This section is the cheapest way to prevent scope drift.

---

## Tips

- If you can't write the goal in one sentence, the brief isn't ready.
- Constraints you can't articulate are constraints the agent will violate.
- "Out of scope" is more useful than you'd think — fill it in.
