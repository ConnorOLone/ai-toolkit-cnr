# claude-shell Setup

You are setting up the `claude-shell` PowerShell module on this device. It adds
Claude to the user's PowerShell terminal: **Alt+E** (generate a command from
natural language), **Alt+X** (explain the current command), and the `Ask-Claude`
pipe-through filter. Follow each step in order. Ask the user for input where
indicated. Works on Windows and macOS.

This module only applies inside **PowerShell 7 (`pwsh`)**. Every command below
runs in `pwsh`, and the file edited is the `pwsh` `$PROFILE`. If the user's
default shell is something else (zsh, cmd), the module loads whenever they start
`pwsh`.

## Step 1: Locate the module

This file lives in the `claude-shell/` directory of the ai-toolkit-cnr repo.
Resolve the absolute path of the directory containing this file — call it
`MODULE_DIR`. The manifest is `MODULE_DIR/claude-shell.psd1`. Use forward slashes
in the path; they work on both Windows and macOS.

## Step 2: Confirm PowerShell 7.4+

Run `pwsh -NoProfile -Command '$PSVersionTable.PSVersion'`. It must be 7.4 or newer.

If `pwsh` is missing, tell the user how to install it, then stop:
- macOS: `brew install --cask powershell`
- Windows: `winget install Microsoft.PowerShell` (or the Microsoft Store)

## Step 3: Choose a backend

Ask the user which backend to use:

- **Api** — a direct HTTPS call to the Anthropic API. Fast (~1s). Needs an API key.
- **ClaudeCli** — shells out to the local `claude` CLI. No API key needed, but each
  call cold-starts the CLI (~5-10s) — too slow to be pleasant for Alt+E / Alt+X.

Recommend **Api** for the interactive key bindings.

- If the user picks **Api**: ask for their Anthropic API key, or check whether one
  is already in the environment with
  `pwsh -NoProfile -Command '[bool]$env:ANTHROPIC_API_KEY'`.
- If the user picks **ClaudeCli**: confirm `claude` is on PATH with
  `pwsh -NoProfile -Command '[bool](Get-Command claude -CommandType Application -ErrorAction SilentlyContinue)'`.
  If it is not, tell the user to install/sign in to Claude Code first, then stop.

## Step 4: Write the configuration

In `pwsh`, import the module and save the chosen backend. Run ONE of the following,
substituting the real `MODULE_DIR` (and API key, if applicable):

```
# Api backend — omit -ApiKey if ANTHROPIC_API_KEY is already set in the environment:
pwsh -NoProfile -Command "Import-Module 'MODULE_DIR/claude-shell.psd1'; Set-ClaudeShellConfig -Backend Api -ApiKey 'sk-ant-...'"

# ClaudeCli backend:
pwsh -NoProfile -Command "Import-Module 'MODULE_DIR/claude-shell.psd1'; Set-ClaudeShellConfig -Backend ClaudeCli"
```

This writes `~/.claude-shell/config.json`. The API key, if any, is stored only
there — never in the repo.

## Step 5: Add the module to the PowerShell profile

Find the profile path with `pwsh -NoProfile -Command '$PROFILE'`. Create the file
and its parent directory if they do not exist.

This step must be **safe to re-run**. Read the existing `$PROFILE` first: if it
already contains `Register-ClaudeShellKeyHandlers`, skip the append and tell the
user it is already configured. Otherwise append these three lines, substituting
the real `MODULE_DIR`:

```
# claude-shell — terminal-side Claude integration
Import-Module 'MODULE_DIR/claude-shell.psd1'
Register-ClaudeShellKeyHandlers
```

## Step 6: Verify

Run:

```
pwsh -NoProfile -Command "Import-Module 'MODULE_DIR/claude-shell.psd1'; (Get-Command -Module claude-shell).Name"
```

Confirm it lists `Ask-Claude`, `Invoke-ClaudeAsk`, `Register-ClaudeShellKeyHandlers`,
and `Set-ClaudeShellConfig` with no errors.

## Step 7: Tell the user

- Open a **new** `pwsh` terminal — the profile only loads on a fresh session.
- Test Alt+E: type `list files modified today` and press **Alt+E**; it should
  become a PowerShell command. Test Alt+X: type any command and press **Alt+X**;
  an explanation prints above the prompt.
- **macOS only:** if Alt+E does nothing, the terminal is not sending Option as the
  Meta key. Terminal.app: Settings → Profiles → Keyboard → "Use Option as Meta
  key". iTerm2: Settings → Profiles → Keys → Left Option key → "Esc+".
- If they chose the `ClaudeCli` backend, remind them the ~5-10s per-call latency is
  expected, and that switching to `Api` later is just
  `Set-ClaudeShellConfig -Backend Api -ApiKey '...'`.
