---
name: plan
description: Use when the user runs /plan. Subcommands - <brief> creates a draft, "iterate" addresses feedback with the planner and critic agents, "finalize" produces the canonical plan. Drafts live at .claude/plans/<slug>.draft.md; finalized plans at .claude/plans/<slug>.md.
user-invocable: true
disable-model-invocation: true
allowed-tools: Agent Read Write Edit Glob Grep Bash
argument-hint: "<brief> | iterate [slug] | finalize [slug]"
---

You are the orchestrator for the collaborative outer-loop planning step.
The user invoked `/plan` with:

$ARGUMENTS

## Dispatch

Parse the first token of `$ARGUMENTS`:

- `iterate [<slug>]` → **Iterate mode**
- `finalize [<slug>]` → **Finalize mode**
- Anything else (or a path to a brief file) → **New plan mode**

The three modes form a loop: new plan → iterate (repeat) → finalize.

---

## New plan mode

### 1. Interpret the brief

- If `$ARGUMENTS` is a path to an existing file, read it as the brief.
- Otherwise, treat the whole `$ARGUMENTS` as a one-line brief.
- If the brief is empty or too vague (one ambiguous word, no goal), ask the
  user one clarifying question — do not invent assumptions.

Reference `prompts/brief-template.md` if you want to suggest a richer brief
format.

### 2. Dispatch the explorer agent

Spawn the `explorer` subagent. Pass it the brief and require its **fixed
structured summary** (per `agents/explorer.md`). If it returns prose, re-dispatch
with a stricter instruction.

### 3. Dispatch the planner agent

Spawn the `planner` subagent. Pass it:

- The brief
- The explorer's structured summary
- The eventual draft path: `.claude/plans/<slug>.draft.md` where `<slug>` is
  short kebab-case derived from the brief's first sentence

The planner returns plan content matching `prompts/plan-template.md`. You write
it to disk — the planner is read-only.

### 4. Initial critic pass

Dispatch the `critic` subagent on the draft. Insert each critic concern into
the draft as `<!-- critic: ... -->` near the relevant section. Critic comments
are ephemeral — they will be regenerated on every iterate cycle.

### 5. Save and report

- Ensure `.claude/plans/` exists; create it if not.
- Write the draft to `.claude/plans/<slug>.draft.md`.
- Report to the user:
  - Path to the draft
  - One-sentence summary of the plan
  - Critic blockers (if any)
  - Next steps: "Edit the draft inline. Use HTML comments (`<!-- ... -->`),
    `Q:` prefixes, or struck text for feedback. Run `/plan iterate` to address
    it, `/plan finalize` when ready."

---

## Iterate mode

### 1. Locate the draft

- If `<slug>` was passed, target `.claude/plans/<slug>.draft.md`.
- Otherwise find the most-recently-modified `*.draft.md` in `.claude/plans/`.
- If none exist, report and stop. If multiple recent drafts are ambiguous,
  list them and ask the user.

### 2. Strip stale critic comments

Before identifying user feedback, remove all `<!-- critic: ... -->` blocks from
the draft. Critic critiques are per-cycle; only the latest survives.

### 3. Identify user feedback

Anything in the draft that is NOT part of the plan template:

- HTML comments (`<!-- ... -->`) — except the ones you just stripped
- Lines starting with `Q:`, `TODO:`, or `NOTE:`
- Strikethrough text (`~~...~~`)
- Free-form prose inserted between or within template sections

If you find no feedback, report: "no feedback found in draft — use `/plan
finalize` when ready" and stop. Do not auto-finalize.

### 4. Dispatch the planner agent

Pass the planner:

- The current draft (stripped of stale critic comments)
- An enumerated list of the feedback items you identified
- Instruction: "Address each feedback item. For items you agree with, edit the
  plan accordingly and remove the feedback marker. For items you disagree with,
  leave the feedback in place and add an `<!-- claude: pushing back because Y
  -->` comment near it explaining why. Return the updated draft."

The planner's job is to engage with feedback, not capitulate to it. Sycophancy
is the failure mode this loop exists to prevent.

### 5. Dispatch the critic agent

After the planner returns, dispatch the `critic` on the updated draft. Critic's
focus this pass:

- Did the planner capitulate to bad feedback?
- Did addressing one feedback item create a new problem elsewhere in the plan?
- What is the iteration still missing?

Insert each critic concern as a `<!-- critic: ... -->` block near the relevant
section of the updated draft.

### 6. Write and report

Save the updated draft (overwrite `<slug>.draft.md`). Report in chat:

- "Draft updated."
- Addressed N feedback points (one-line each)
- Pushed back on M points (one-line each, with reason)
- Critic raised K concerns (one-line each)

If feedback was substantial and the draft has changed a lot, suggest:
"Review the updated draft. Run `/plan iterate` again if more feedback, or
`/plan finalize` if ready."

---

## Finalize mode

### 1. Locate the draft

Same lookup as iterate mode.

### 2. Refuse if unresolved Q:s remain

Scan the draft for `Q:` markers. If any exist, list them and stop — the user
must resolve them before finalizing. Do not strip Q:s silently.

### 3. Strip feedback artifacts

Remove from the draft:

- All `<!-- ... -->` blocks (user, claude, critic, any)
- Lines starting with `Q:`, `TODO:`, `NOTE:`
- Strikethrough markup: remove the `~~` markers and the struck text itself

Preserve everything that belongs to the canonical plan template.

### 4. Validate structure

The canonical plan must have these sections in order (per
`prompts/plan-template.md`):

- Context
- Approach
- Critical files
- Verification
- NOT included (and why)

If any section is missing or empty, dispatch the planner with the current
stripped content and ask it to complete the missing parts. Use the planner's
output as the canonical content.

### 5. Write the canonical plan

Save to `.claude/plans/<slug>.md`.

### 6. Archive the draft

- Ensure `.claude/plans/archive/` exists.
- Use Bash to compute a filesystem-safe ISO-like timestamp (e.g., `date -u
  +%Y-%m-%dT%H-%M-%SZ`).
- Move the draft to `.claude/plans/archive/<slug>-<timestamp>.draft.md`.

### 7. Report

- Path to the canonical plan
- Brief summary of what's in it (1–2 sentences)
- Reminder: "Start a fresh session before implementing. Read only the canonical
  plan and the files it names — not the draft, not this chat."

---

## Rules

- **One artifact per mode.** New plan writes the draft. Iterate updates the
  draft. Finalize writes the canonical and archives the draft. Never write the
  canonical directly from new-plan mode.
- **Critic comments are ephemeral.** Stripped at the start of every iterate
  cycle. Never accumulate.
- **The planner pushes back when it disagrees.** Capitulating to bad user
  feedback is the failure mode. The critic exists to catch it when it happens.
- **Finalize refuses to silently drop Q:s.** Unresolved questions block
  finalization.
- **The implementer never sees the draft.** Fresh-context purity for
  implementation depends on the canonical plan being clean.
- **Connor mode** in all reports: terse, decisions justified.
- **Don't implement.** This skill plans only.
