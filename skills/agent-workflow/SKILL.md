---
name: agent-workflow
description: Use this when working in an agentic parallel-branch workflow. Prefer agentctl commands for syncing with main and reading PR feedback. Avoid raw git/gh when agentctl provides an equivalent.
---

When invoked, follow these rules:

1) Normalize to repo root before running repo-relative commands:
   cd "$(git rev-parse --show-toplevel)"

2) Prefer these commands over ad-hoc git/gh:

- Sync current branch with main (preferred: rebase):
  AGENTCTL_MODE=agent agentctl sync

- Read PR comments (avoid manual copy/paste):
  AGENTCTL_MODE=agent agentctl pr comments
  AGENTCTL_MODE=agent agentctl pr comments --json

- Diagnose setup quickly:
  AGENTCTL_MODE=agent agentctl doctor

3) Do NOT attempt topology-changing actions in agent mode:
- Do not run: agentctl init / agentctl rm / agentctl clean
- If denied, stop and ask the user.

4) If a command fails due to working directory assumptions, re-check:
- pwd
- git rev-parse --show-toplevel
Then retry from repo root.
