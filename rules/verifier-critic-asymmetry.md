# Verifier-critic asymmetry

Never let the same context that wrote code grade that code.

When reviewing, verifying, or evaluating work you (or another agent) just produced:

1. **Use `/review`** for code review — it dispatches `code-reviewer` and
   `security-reviewer` subagents in a fresh context.
2. **Dispatch `critic`** for plan/decision review before committing to an approach.
3. **Dispatch `test-runner`** to execute tests — never grade your own test runs.

## Read-only invariant

Reviewer-class agents (`code-reviewer`, `security-reviewer`, `critic`,
`test-runner`, `explorer`, `planner`) **must not** list `Edit` or `Write` in
their `allowed-tools` frontmatter. This is structural, not a request — if a
reviewer can edit, its review is no longer independent.

When adding a new reviewer-style agent, check this before merging:

```sh
rg -l 'Edit|Write' agents/*.md
```

Should return zero matches for any agent intended for review/verification roles.

## Why

Models exhibit *structural sycophancy* — same context that produced an output
biases toward justifying it. SycEval (mid-2026) measured a 36% false-pass rate
when the producing context also graded. Fresh context drops that to near-baseline.

The cost of a second agent invocation is trivial relative to the cost of a
false-positive review reaching production.
