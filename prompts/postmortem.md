---
name: postmortem
description: End-of-session reflection that feeds /harness
---

# Session postmortem

After shipping (or aborting) a piece of work, spend 2 minutes on this before
closing the session. The output is the input to `/harness`.

The goal: turn one session's friction into a durable harness improvement.

---

## What did the agent get wrong?

Concrete. "It assumed X was true and it wasn't." "It missed file Y." "It used
pattern Z when the repo uses W." If nothing went wrong, say so — that's also a
data point (and rare enough to be worth recording).

## What did I correct manually?

Edits / instructions / re-prompts you had to add. These are the loudest signal
for what's missing from CLAUDE.md / skills / rules.

## What took longer than expected?

If a step that should be fast was slow, why? Tool confusion, missing context,
re-exploration the harness should have prevented.

## Proposed artifact

The output `/harness` will run with. Pick *one* concrete change:

- New line in CLAUDE.md (quote it)
- New rule in `rules/` (give the path scope and content)
- New hook (event + matcher + behavior — only if it MUST happen 100% deterministically)
- Update to an existing skill (which skill, what change)
- New test or lint rule (which file, what it asserts)

If no single change beats "do nothing", say so — not every session yields an artifact.
