---
name: handoff
description: Instructions for the implementer session that picks up an approved plan
---

# Plan-to-implementer handoff

Read this first in a **fresh Claude Code session** when starting implementation
of an approved plan. The point of the fresh session is to discard the exploration
context that produced the plan — the plan is now the source of truth.

---

## Rules

1. **Read only what the plan references.** Don't re-explore the codebase from
   scratch. The plan named the critical files for a reason.

2. **If the plan is wrong or incomplete, stop and flag.** Don't improvise around
   a gap. Surfacing the gap is more valuable than working around it.

3. **One commit per session.** Red test commit, then green-implementation commit
   is fine. Avoid drive-by changes outside the plan's scope — log them in a
   "Follow-ups" comment for `/harness` instead of committing.

4. **TDD when the task is testable.** Failing test first, prove it fails, commit.
   Implement until green. Run lint/typecheck before the final commit.

5. **Verify against the plan's Verification section before declaring done.**
   If a verification step can't be run, say so explicitly rather than skipping it.

---

## What to read

- The plan file (passed by path).
- The files the plan's "Critical files" section names.
- Nothing else, unless answering a specific question the implementation raises.
