#!/bin/bash
# Auto-sync the AI toolkit at Claude Code session start.
# Event: SessionStart
#
# Runs at the start of each Claude Code session (or manually).
# Reads the toolkit path from ~/.claude/.toolkit-path, does a
# non-destructive git pull if there are upstream changes, and
# re-runs manage.py to update installed assets.
#
# Silent on success, only prints when it actually syncs.

set -euo pipefail

TOOLKIT_PATH_FILE="$HOME/.claude/.toolkit-path"

[ -f "$TOOLKIT_PATH_FILE" ] || exit 0

TOOLKIT_DIR="$(cat "$TOOLKIT_PATH_FILE")"
[ -d "$TOOLKIT_DIR/.git" ] || exit 0

cd "$TOOLKIT_DIR"

# Don't sync if there are local uncommitted changes — user is editing
if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
    exit 0
fi

# Fetch quietly, check if behind
git fetch --quiet origin 2>/dev/null || exit 0

LOCAL=$(git rev-parse HEAD 2>/dev/null)
REMOTE=$(git rev-parse @{u} 2>/dev/null) || exit 0

if [ "$LOCAL" = "$REMOTE" ]; then
    exit 0
fi

# Only fast-forward — never force or merge
if git merge-base --is-ancestor "$LOCAL" "$REMOTE" 2>/dev/null; then
    git pull --ff-only --quiet origin 2>/dev/null || exit 0
    echo "[aitk] Toolkit synced — $(git log --oneline "$LOCAL".."$REMOTE" | wc -l | tr -d ' ') new commit(s)" >&2
fi

exit 0
