---
name: tdd
description: Use when the user runs /tdd with a task. Runs the red→green→commit cycle, dispatches test-runner for execution, enforces one-commit-per-session and lint/typecheck gate.
user-invocable: true
disable-model-invocation: true
allowed-tools: Agent Read Write Edit Bash Glob Grep
argument-hint: "<task description, ideally a single task from an approved plan>"
---

You are the inner-loop driver. The user invoked `/tdd` with:

$ARGUMENTS

## Process

### 1. Confirm scope

The task should be **a single deliverable that fits in one commit** — or two
commits (failing-test, then passing-implementation). If the task is larger
than that, stop and tell the user — suggest they `/plan` first to break it
down. Don't proceed with multi-feature TDD in one session.

### 2. Write the failing test

- Locate the appropriate test file (or create one matching the project's
  existing test conventions — check sibling tests first).
- Write a test that captures the task's behavior. The test must currently fail.
- Run the test via the `test-runner` subagent to **prove it fails**. Do not
  proceed if it passes — that means the test isn't testing what you think.

### 3. Commit the failing test (optional but preferred)

If the project's convention allows red-test commits, commit the failing test
with a `test:` prefix. If not (e.g. CI rejects red commits), keep it staged
and combine with step 5's commit.

### 4. Implement until green

- Edit code until the test passes.
- Dispatch `test-runner` for each verification run — do not run tests in the
  main loop unless you have a specific reason (the dispatch keeps test logs
  out of this context).
- Stop as soon as the test passes. Don't refactor opportunistically.

### 5. Lint and typecheck gate

Before committing, run the project's lint and typecheck. Infer the commands
from the project:

| Marker | Lint / typecheck |
|---|---|
| `package.json` with `lint`/`typecheck` scripts | `npm run lint && npm run typecheck` |
| `pyproject.toml` with `ruff` / `mypy` | `ruff check . && mypy .` |
| `Cargo.toml` | `cargo clippy -- -D warnings && cargo check` |
| `go.mod` | `go vet ./...` |

If lint/typecheck fails, fix the new code only (don't touch unrelated issues).
If you can't fix it cleanly in scope, stop and report — don't disable the rule.

### 6. Commit

Single descriptive commit. Imperative-mood subject ≤ 70 chars, body explains
the why if non-obvious. Co-author trailer per repo convention.

### 7. Report

- One-line summary of what shipped
- Commands the user can run to verify (the test name, lint, typecheck)
- Anything you noticed but didn't act on — feeds `/harness` later

## Rules

- **One commit per session** (or two if red+green split). No drive-by changes.
  If you notice unrelated issues, log them for `/harness`, don't fix them.
- **Test-runner is read-only.** If a test needs fixing, you (the orchestrator)
  edit it — never the test-runner.
- **Never disable tests or rules to make things pass.** Disabling is a code
  smell that requires user approval.
- **Connor mode**: terse, decisions justified.
