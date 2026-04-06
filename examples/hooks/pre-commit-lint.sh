#!/bin/bash
# Example hook script for PreToolUse on Bash(git commit)
# Runs linting before allowing a commit
#
# Add to settings.json:
# {
#   "hooks": {
#     "PreToolUse": [{
#       "matcher": "Bash",
#       "if": "Bash(git commit*)",
#       "hooks": [{ "type": "command", "command": "/path/to/pre-commit-lint.sh" }]
#     }]
#   }
# }

set -euo pipefail

# Read tool input from stdin
input=$(cat)

echo "Running lint check..." >&2

# Exit 0 to allow, exit 2 to block
exit 0
