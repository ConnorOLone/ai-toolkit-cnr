# AI Toolkit Setup

You are setting up the AI toolkit on this device. Follow each step in order. Ask the user for input where indicated.

## Step 1: Locate the toolkit

This file is inside the toolkit repo. Resolve the absolute path of the directory containing this file — that is `TOOLKIT_DIR`.

If this file was pasted rather than read from disk, ask the user where they cloned the repo. The default location is `~/CodeHub/ai-toolkit-cnr`.

## Step 2: Verify prerequisites

Check that the following are available on this device:
- `git` — required for sync
- `python3` — required for manage.py
- `uv` — required for the `aitk` global command

If any are missing, tell the user what to install and stop.

## Step 3: Write the toolkit path marker

Write the absolute path of `TOOLKIT_DIR` to `~/.claude/.toolkit-path`. Create the file if it doesn't exist, overwrite if it does. This is how skills and hooks find the toolkit on this device.

## Step 4: Install assets interactively

Tell the user you are about to launch the interactive asset manager, which lets them choose which skills, agents, rules, hooks, and configs to install on this device. Then run:

```
python3 TOOLKIT_DIR/manage.py
```

This must run in an interactive terminal. Tell the user to run it themselves with `!` prefix if you cannot run interactive commands.

## Step 5: Install the `aitk` global command

Run:

```
python3 TOOLKIT_DIR/manage.py --install-cli
```

This creates an `aitk` alias so the manager can be invoked from any directory.

On macOS/Linux this writes to `~/.local/bin/aitk`. If `~/.local/bin` is not on the user's PATH, tell them to add it.

On Windows this writes to `%LOCALAPPDATA%\Microsoft\WindowsApps\aitk.cmd`.

## Step 6: Register the auto-sync hook

Read the user's `~/.claude/settings.json`. Add a `SessionStart` hook that runs the toolkit sync script. Merge with any existing hooks — never replace.

The hook to add:

```json
{
  "SessionStart": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "TOOLKIT_DIR/hooks/toolkit-sync.sh",
          "timeout": 15,
          "statusMessage": "Syncing AI toolkit..."
        }
      ]
    }
  ]
}
```

Replace `TOOLKIT_DIR` with the actual absolute path resolved in Step 1.

If a SessionStart hook for toolkit-sync already exists, skip this step.

Validate that the resulting settings.json is valid JSON before writing.

## Step 7: Verify

Run the following checks and report results:

1. `~/.claude/.toolkit-path` exists and contains the correct path
2. `~/.claude/skills/` contains symlinks (macOS/Linux) or copies (Windows) pointing to toolkit assets
3. `aitk --help` or `aitk status` runs successfully (if PATH is set up)
4. `~/.claude/settings.json` contains the SessionStart hook
5. The toolkit repo has no uncommitted changes

Report what was set up and any issues found.

## Step 8: Summary

Tell the user:
- Which assets were installed
- That `aitk` is available globally to manage assets from anywhere
- That the toolkit will auto-sync from git at the start of each Claude session
- To push any local commits if they want changes available on other devices
