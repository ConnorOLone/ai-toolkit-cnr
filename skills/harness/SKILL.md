---
name: harness
description: Use when the user runs /harness at the end of a session. Reviews what went wrong, proposes one concrete harness improvement (rule / hook / skill update / CLAUDE.md line), and writes it on approval.
user-invocable: true
disable-model-invocation: true
allowed-tools: Agent Read Write Edit Glob Grep Bash
argument-hint: "[optional note on what frustrated you this session]"
---

You are the end-of-session harness improver. The user invoked `/harness` with:

$ARGUMENTS

The compounding harness (CLAUDE.md, hooks, skills, agents, rules) is the
strategic asset. This skill is how that asset compounds — by turning one
session's friction into a durable improvement.

## Process

### 1. Gather session signal

Look at:

- The session's `git log` since the start (or last `/harness` mark)
- Any `$ARGUMENTS` the user passed in
- The current state of CLAUDE.md, installed skills, and rules

Reference `prompts/postmortem.md` for the structured questions.

### 2. Identify ONE candidate artifact

A harness improvement is one of:

| Type | When to choose |
|---|---|
| **CLAUDE.md line** | A rule that the agent should always remember in this project, fits in ≤2 lines |
| **Rule file (`rules/`)** | A path-scoped rule (e.g. "in this directory, do X") |
| **Skill update** | An existing skill missed a step or got something wrong |
| **New skill** | A multi-step procedure that recurs — never for one-offs |
| **Hook** | Only when behavior MUST happen 100% deterministically (formatting, blocking destructive commands) |
| **Test / lint rule** | A class of mistake the agent kept making that a check would catch |

Pick **one**. Bundling several improvements is a sign you don't yet know
which is load-bearing.

### 3. Apply the Anthropic test

Before proposing it, ask: *"Would removing this line cause Claude to make
mistakes that it doesn't currently make?"*

If the answer is no, the artifact isn't worth adding. Tell the user so — not
every session yields an artifact, and that's normal.

### 4. Propose and confirm

Present the candidate to the user:

```
Proposed: <type> — <one-line description>
File: <exact path>
Content: <exact text or diff>
Reason: <what went wrong this session that this prevents next time>
```

Wait for user approval before writing. Connor mode applies — terse, justified.

### 5. Apply

On approval, write the change. For CLAUDE.md edits, use `Edit`. For new files,
use `Write`. Confirm by showing the diff.

If the user rejects or wants changes, iterate once. If still not right, drop
it — premature artifacts are worse than no artifact.

## Rules

- **One artifact per session.** No bundles.
- **Concrete > general.** "Add Y to CLAUDE.md" beats "improve docs". Quote the line.
- **Read-only by default.** Only apply on explicit approval.
- **No retrospective justification.** If the artifact doesn't pass the
  Anthropic test, skip it — don't reach for one because the user invoked the skill.
- **Connor mode**: terse, decisions justified.
