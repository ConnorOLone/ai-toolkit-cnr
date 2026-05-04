#!/bin/bash
# install.sh — Symlink AI toolkit assets into Claude Code config directories (macOS only)
#
# Usage: ./scripts/install.sh
#
# What it does:
#   - Symlinks skills/<name>/  → ~/.claude/skills/<name>/
#   - Symlinks agents/*.md     → ~/.claude/agents/*.md
#   - Symlinks rules/*.md      → ~/.claude/rules/*.md
#   - Makes hooks/*.sh executable (referenced by path in settings.json)
#   - Symlinks configs/CLAUDE.md → ~/.claude/CLAUDE.md (user-level context)
#
# Does NOT symlink examples/ — those are reference-only.
# Safe to re-run — uses ln -sf(n) to overwrite existing symlinks.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE_DIR="$HOME/.claude"

# --- Preflight ---

if [[ "$(uname)" != "Darwin" ]]; then
  echo "This script is designed for macOS. On Windows, copy files manually."
  exit 1
fi

echo "AI Toolkit Installer (macOS)"
echo "Repo:   $REPO_DIR"
echo "Target: $CLAUDE_DIR"
echo ""

# --- Skills → ~/.claude/skills/ ---

if [ -d "$REPO_DIR/skills" ]; then
  mkdir -p "$CLAUDE_DIR/skills"
  count=0
  for skill_dir in "$REPO_DIR/skills"/*/; do
    [ -d "$skill_dir" ] || continue
    name="$(basename "$skill_dir")"
    if [ ! -f "$skill_dir/SKILL.md" ]; then
      echo "  skipped: $name (no SKILL.md)"
      continue
    fi
    ln -sfn "$skill_dir" "$CLAUDE_DIR/skills/$name"
    echo "  linked skill: $name"
    count=$((count + 1))
  done
  echo "Skills: $count linked"
else
  echo "Skills: skipped (no skills/ directory)"
fi

echo ""

# --- Agents → ~/.claude/agents/ ---

if [ -d "$REPO_DIR/agents" ]; then
  mkdir -p "$CLAUDE_DIR/agents"
  count=0
  for agent in "$REPO_DIR/agents"/*.md; do
    [ -f "$agent" ] || continue
    name="$(basename "$agent")"
    [ "$name" = "README.md" ] && continue
    ln -sf "$agent" "$CLAUDE_DIR/agents/$name"
    echo "  linked agent: $name"
    count=$((count + 1))
  done
  echo "Agents: $count linked"
else
  echo "Agents: skipped (no agents/ directory)"
fi

echo ""

# --- Rules → ~/.claude/rules/ ---

if [ -d "$REPO_DIR/rules" ]; then
  mkdir -p "$CLAUDE_DIR/rules"
  count=0
  for rule in "$REPO_DIR/rules"/*.md; do
    [ -f "$rule" ] || continue
    name="$(basename "$rule")"
    [ "$name" = "README.md" ] && continue
    ln -sf "$rule" "$CLAUDE_DIR/rules/$name"
    echo "  linked rule: $name"
    count=$((count + 1))
  done
  echo "Rules: $count linked"
else
  echo "Rules: skipped (no rules/ directory)"
fi

echo ""

# --- Hooks — make executable ---

if [ -d "$REPO_DIR/hooks" ]; then
  count=0
  for hook in "$REPO_DIR/hooks"/*.sh; do
    [ -f "$hook" ] || continue
    chmod +x "$hook"
    echo "  executable: $(basename "$hook")"
    count=$((count + 1))
  done
  echo "Hooks: $count made executable"
  echo "  (add hook paths to your settings.json — see examples/configs/)"
else
  echo "Hooks: skipped (no hooks/ directory)"
fi

echo ""

# --- User-level CLAUDE.md ---

if [ -f "$REPO_DIR/configs/CLAUDE.md" ]; then
  ln -sf "$REPO_DIR/configs/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
  echo "CLAUDE.md: linked to $CLAUDE_DIR/CLAUDE.md"
else
  echo "CLAUDE.md: skipped (no configs/CLAUDE.md found)"
fi

# --- Toolkit path marker ---

echo "$REPO_DIR" > "$CLAUDE_DIR/.toolkit-path"
echo "Toolkit path: saved to $CLAUDE_DIR/.toolkit-path"

echo ""
echo "Done."
