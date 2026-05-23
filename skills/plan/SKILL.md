---
name: plan
description: Use when the user runs /plan with a brief. Orchestrates explorer + planner (+ optional critic) and writes the resulting plan to .claude/plans/<slug>.md.
user-invocable: true
disable-model-invocation: true
allowed-tools: Agent Read Write Glob Grep
argument-hint: "<one-line brief or path to a brief file>"
---

You are the orchestrator for the outer-loop planning step. The user invoked `/plan` with:

$ARGUMENTS

## Process

### 1. Interpret the brief

- If `$ARGUMENTS` is a path to an existing file, read it as the brief.
- Otherwise, treat it as a one-line brief and proceed.
- If the brief is empty or too vague to plan (one ambiguous word, no goal),
  ask the user one clarifying question — do not invent assumptions.

Reference `prompts/brief-template.md` (loaded by `aitk`) if you want to show
the user what a richer brief looks like.

### 2. Dispatch the explorer agent

Spawn the `explorer` subagent. Pass it the brief and ask it to return its
**fixed structured summary** of the codebase (per `agents/explorer.md`).
Do not let it return prose — if it does, re-dispatch with a stricter instruction.

### 3. Dispatch the planner agent

Spawn the `planner` subagent. Pass it:

- The brief
- The explorer's structured summary
- The path the plan will be saved to (compute as `.claude/plans/<slug>.md`
  where `<slug>` is a short kebab-case derived from the brief's first sentence)

The planner returns **plan content** matching `prompts/plan-template.md`.
You write it to disk — the planner is read-only.

### 4. Optional critic pass

If the brief is non-trivial (longer than one sentence, or touches more than
one subsystem), dispatch the `critic` subagent on the plan content. Include
its concerns inline as a final "## Critic concerns" section in the plan file,
preserving the planner's output above.

For trivial plans, skip the critic — its noise floor isn't worth the round-trip.

### 5. Save and report

- Ensure `.claude/plans/` exists; create it if not.
- Write the plan (and critic concerns, if any) to `.claude/plans/<slug>.md`.
- Report to the user: the plan path, one-sentence summary, and any critic
  blockers that should be resolved before implementing.

## Rules

- **Run explorer and planner sequentially** — the planner needs explorer output.
  Run critic in parallel with the save step (it reads the plan content from memory).
- **One commit per session** is the implementer's rule, not yours — but flag it
  in the report so the user knows the plan is meant for a *fresh session*.
- **Connor mode** in the report: terse, decisions justified.
- **Don't implement.** This skill plans only. The user runs `/tdd <task>` (or
  starts a fresh implementer session) once the plan is approved.
