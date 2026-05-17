# AI Toolkit Setup

You are setting up the AI toolkit on this device. Follow each step in order. Ask the user for input where indicated.

## Step 1: Locate the toolkit

This file is inside the toolkit repo. Resolve the absolute path of the directory containing this file — that is `TOOLKIT_DIR`.

If this file was pasted rather than read from disk, ask the user where they cloned the repo. The default location is `~/CodeHub/ai-toolkit-cnr`.

## Step 2: Verify prerequisites

Check that the following are available on this device:
- `git` — required for sync
- a working Python 3.9+ interpreter — required for manage.py
- `uv` — required for the `aitk` global command

For Python, do not trust PATH presence alone — actually run the interpreter to
confirm it works. Try `python3 --version`, then `python --version`. On Windows,
`python3` is often a non-functional Microsoft Store alias: it appears on PATH
but fails when run. Use whichever command actually executes, and refer to it as
`PYTHON` in the steps below.

If any are missing, tell the user what to install and stop.

## Step 3: Write the toolkit path marker

Write the absolute path of `TOOLKIT_DIR` to `~/.claude/.toolkit-path`. Create the file if it doesn't exist, overwrite if it does. This is how skills and hooks find the toolkit on this device.

Use forward slashes in the path (e.g. `C:/Users/you/CodeHub/ai-toolkit-cnr`), not backslashes. The marker is read by both Python and the bash sync hook, and forward slashes are valid for both. `manage.py` rewrites this file in the same forward-slash format whenever assets are installed or removed.

## Step 4: Install the `aitk` global command

`aitk` is the toolkit's CLI — it is `manage.py` made available from any directory. Installing it first lets the next step (and all future asset management) use `aitk` instead of a script path. This is the one step that must call the script directly, since `aitk` does not exist yet:

```
PYTHON TOOLKIT_DIR/manage.py --install-cli
```

This creates an `aitk` command so the manager can be invoked from anywhere.

On macOS/Linux this writes to `~/.local/bin/aitk`. If `~/.local/bin` is not on the user's PATH, tell them to add it.

On Windows this writes to `%LOCALAPPDATA%\Microsoft\WindowsApps\aitk.cmd` (already on PATH).

## Step 5: Install assets interactively

Tell the user you are about to launch the interactive asset manager, which lets them choose which skills, agents, rules, hooks, output styles, and configs to install on this device. In a freshly opened terminal — so the `aitk` command from Step 4 is on PATH — run:

```
aitk
```

This must run in an interactive terminal. Tell the user to run it themselves (typing `aitk` in their own terminal pane, or with the `!` prefix) if you cannot run interactive commands.

If `aitk` is not found (e.g. PATH not yet refreshed), fall back to `PYTHON TOOLKIT_DIR/manage.py` — it is the same program.

## Step 6: Enable the auto-sync hook

The toolkit ships a `toolkit-sync` hook that pulls the latest toolkit from git at the start of each Claude session. It appears in the Step 5 asset picker like any other hook.

Installing a hook through `aitk` also registers it in `~/.claude/settings.json` automatically — it reads the `# Event:` header (`SessionStart` for this hook) and writes a `bash "..."` command that works on macOS, Linux, and Windows alike. Git Bash provides `bash` on Windows, and is installed alongside the required `git`.

So there is no settings.json editing to do by hand:

- If `toolkit-sync` was enabled in the Step 5 picker, it is already installed and registered — nothing to do.
- If it was not, run `aitk` again and enable `toolkit-sync` now.

Then confirm `~/.claude/settings.json` has a `SessionStart` hook whose command references `toolkit-sync.sh`. `aitk status` also marks the hook as `(registered)`.

## Step 7: Audit and update tools reference

Compare `TOOLKIT_DIR/configs/tools.json` against the tools available in this Claude Code session. For each tool you have access to (excluding MCP tools prefixed with `mcp__`), check whether it exists in `tools.json`.

If there are any differences — new tools, removed tools, or descriptions that no longer match — write the updated JSON to `TOOLKIT_DIR/configs/tools.json`. Keep keys sorted alphabetically, 2-space indentation.

After updating, run `PYTHON TOOLKIT_DIR/manage.py tools` to verify the output.

This keeps `aitk tools` accurate across Claude Code updates.

## Step 8: Verify

Run the following checks and report results:

1. `~/.claude/.toolkit-path` exists and contains the correct path
2. `~/.claude/skills/` contains symlinks (macOS/Linux) or copies (Windows) pointing to toolkit assets
3. `aitk --help` or `aitk status` runs successfully (if PATH is set up)
4. `aitk tools` runs and shows the current tool list
5. `~/.claude/settings.json` contains the SessionStart hook
6. The toolkit repo has no uncommitted changes

Report what was set up and any issues found.

## Step 9: Summary

Tell the user:
- Which assets were installed
- That `aitk` is available globally to manage assets from anywhere
- That the toolkit will auto-sync from git at the start of each Claude session
- That `aitk tools` can be audited with the `tools-audit` skill to stay current
- That an optional PowerShell terminal integration (Alt+E / Alt+X / `Ask-Claude`)
  is available — to set it up, follow `claude-shell/SETUP.md`
- To push any local commits if they want changes available on other devices
