# claude-shell

A small, self-contained PowerShell module that puts Claude one keystroke away in
your terminal: **Alt+E** turns plain English into a PowerShell command, **Alt+X**
explains the command you're about to run, and **`Ask-Claude`** is a pipe-through
filter for everything else. It replaces the `aichat` CLI with ~250 auditable lines
of PowerShell that depend on nothing but PowerShell built-ins. It can call the
Anthropic API directly, or shell out to your existing `claude` CLI so there is no
per-token cost.

- **Requires:** PowerShell 7.4+ (Windows or macOS) and, for the key bindings, PSReadLine 2.4+.
- **Dependencies:** none beyond the above. No third-party modules, no compiled binaries.

---

**Fastest — Claude-guided:** open Claude Code in the repo and say
`follow claude-shell/SETUP.md`. It picks a backend, writes the config, and edits
your `$PROFILE` for you — on Windows or macOS.

**Manual:**

1. Clone the `ai-toolkit-cnr` repo (you have likely already done this).
2. Add the lines from [`examples/profile-snippet.ps1`](examples/profile-snippet.ps1)
   to your PowerShell `$PROFILE`, editing the repo path to match your machine.
   Open the profile in any editor — `notepad $PROFILE` on Windows, `nano $PROFILE`
   on macOS (create it first if needed: `New-Item -ItemType File $PROFILE -Force`).
   The snippet imports the module and calls `Register-ClaudeShellKeyHandlers`.
3. Open a new terminal (or run `. $PROFILE`).

To use the module without touching `$PROFILE`, just import the manifest directly:

```powershell
Import-Module ./claude-shell/claude-shell.psd1
```

`Import-Module` only defines functions — it does **not** bind keys or make any
network call. Key binding is an explicit, separate step (`Register-ClaudeShellKeyHandlers`).

---

## Configure

Pick **one** backend.

### Backend A — direct Anthropic API

Needs an API key. Provide it either way:

```powershell
# Option 1: environment variable (nothing written to disk by this module)
$env:ANTHROPIC_API_KEY = 'sk-ant-...'

# Option 2: the config file
Set-ClaudeShellConfig -ApiKey 'sk-ant-...'
```

### Backend B — the local `claude` CLI (no API cost)

Uses whatever authentication your `claude` CLI is already signed in with — e.g. a
Claude subscription — so it does not incur direct API charges. No API key needed.

```powershell
Set-ClaudeShellConfig -Backend ClaudeCli
```

**Latency:** each call cold-starts the `claude` process (a full Node runtime) —
measured at ~5-10s, and no flag removes it. That is fine for `Ask-Claude` in
scripts, but too slow for the Alt+E / Alt+X key bindings. If you want those to
feel instant, use Backend A — it is a single HTTPS request and returns in ~1s.

### Config file

`Set-ClaudeShellConfig` writes to `~/.claude-shell/config.json` — in your home
directory, **not** in this repo, so the repo stays committable.

| Setting            | Default                          | Notes                                            |
|--------------------|----------------------------------|--------------------------------------------------|
| `ApiKey`           | _(none)_                         | Required for `Api` backend. Falls back to `$env:ANTHROPIC_API_KEY`. |
| `Backend`          | `Api`                            | `Api` or `ClaudeCli`.                            |
| `Model`            | `claude-haiku-4-5-20251001`      | Used by both backends.                           |
| `MaxTokens`        | `1024`                           | `Api` backend only (the CLI manages its own).    |
| `ApiEndpoint`      | `https://api.anthropic.com/v1/messages` | `Api` backend only.                       |
| `AnthropicVersion` | `2023-06-01`                     | `Api` backend only.                              |

Each machine has its own config file, so a work machine can use `ClaudeCli` while
a personal machine uses `Api` — same module, no code changes.

---

## The three features

### Alt+E — natural language → PowerShell command

Type what you want, press **Alt+E**. The buffer shows an hourglass while it thinks,
then is replaced with a runnable command. You review it and press Enter yourself —
nothing runs automatically. On failure your original text is restored.

```
list files modified today        →   Get-ChildItem -Recurse -File | Where-Object { $_.LastWriteTime.Date -eq (Get-Date).Date }
```

### Alt+X — explain the current command

With a command in the buffer, press **Alt+X**. A one-or-two-sentence explanation is
printed above the prompt. The buffer is **not** modified — you're left exactly where
you were, free to run, edit, or clear it.

### `Ask-Claude` — pipe-through filter

Reads piped input and/or a prompt, writes the answer to stdout so it composes:

```powershell
Get-Content errors.log | Ask-Claude "summarise the errors and group by type"
git diff --staged | Ask-Claude "write a conventional commit message, output only the message"
Ask-Claude "regex for matching UK postcodes"
git diff --staged | Ask-Claude "commit message" | Set-Clipboard
"hello" | Ask-Claude "translate to french"
```

`Ask-Claude` is an alias of `Invoke-ClaudeAsk` (PowerShell reserves `Ask-` as an
unapproved verb; the alias gives the friendly name without an import warning).

> **macOS:** for Alt+E / Alt+X to register, your terminal must send Option as the
> Meta key. Terminal.app: Settings → Profiles → Keyboard → "Use Option as Meta
> key". iTerm2: Settings → Profiles → Keys → Left Option key → "Esc+".

---

## Security review

This section is written so a reviewer can sign off quickly. The module is ~250
lines of PowerShell in one file — reading it end to end is the fastest audit.

### What it does, in both backends

- Sends the text you act on (your buffer for Alt+E/Alt+X, or your piped input plus
  prompt for `Ask-Claude`) to Anthropic, and returns the reply.
- Reads its config from `~/.claude-shell/config.json`.

### What it never does

- No third-party dependencies — only PowerShell built-ins and `Invoke-RestMethod`.
- No background jobs, no scheduled tasks, no local HTTP servers, no long-running
  connections, no telemetry.
- No file I/O other than reading the config file (and writing it **only** when you
  explicitly run `Set-ClaudeShellConfig`).
- No global variables; module state is script-scoped and limited to constants.
- The API key is never logged and never written anywhere except your own config
  file. Errors report the exception message only — never the request or headers.

### Backend A — `Api`: what data leaves the machine

- **One** HTTPS `POST` per action to `https://api.anthropic.com/v1/messages`.
- Request body: the model name, a token cap, and your text. Header: your API key
  (`x-api-key`). Nothing else.
- Single request/response, 30-second timeout. No subprocess is ever spawned.
- This is the cleanest mode to audit: every byte that leaves the machine is in the
  ~25-line `Invoke-ClaudeApi` function.

### Backend B — `ClaudeCli`: what data leaves the machine

- claude-shell makes **no network call itself**. It runs the local `claude` CLI as
  a subprocess (`claude --print ...`) and `claude` performs the request under its
  own, already-approved authentication. Your text is passed to it via stdin.
- Each call is invoked with `--tools ""` (all tools disabled — it cannot read or
  write files or run commands), `--strict-mcp-config` (no MCP servers start), and
  `--no-session-persistence` (no transcript written to disk).
- **Caveat for reviewers:** this is **subprocess execution**, and because Anthropic's
  `--bare` mode forces API-key auth (which would defeat the no-cost goal), it is not
  used. Without `--bare`, `claude` loads your Claude Code configuration — including
  `CLAUDE.md` from the current directory and any **hooks** you have configured, which
  will run. In this mode the security question is really "do we trust the `claude`
  CLI that is already installed and approved on this machine" — claude-shell only
  adds a thin, tool-disabled wrapper around it.

**Recommendation:** use Backend A for the interactive Alt+E / Alt+X bindings — it is
both the fastest (~1s vs ~5-10s) and the cleanest to audit. Use Backend B only where
the `claude` CLI is already approved and an API key cannot be provisioned, accepting
the per-call latency.

---

## How to extend

Add your own key binding in `$PROFILE`, after `Register-ClaudeShellKeyHandlers`.
Use `Ask-Claude` for the Claude call and the `PSConsoleReadLine` API for the buffer.
The profile snippet ships with a worked example — **Alt+G**, which drafts a commit
message from the staged diff:

```powershell
Set-PSReadLineKeyHandler -Chord 'Alt+g' -BriefDescription 'ClaudeCommitMsg' -ScriptBlock {
    $diff = git diff --staged
    if (-not $diff) { return }
    $msg = $diff | Ask-Claude 'Write a Conventional Commits message for this staged diff. Output only the message.'
    if ($msg) {
        [Microsoft.PowerShell.PSConsoleReadLine]::RevertLine()
        [Microsoft.PowerShell.PSConsoleReadLine]::Insert("git commit -m `"$msg`"")
    }
}
```

To change what Alt+E / Alt+X ask for, edit the `$script:Prompts` hashtable near the
top of `claude-shell.psm1`.

---

## How to uninstall

1. Remove the claude-shell lines from your `$PROFILE`.
2. Delete the config directory if you want to remove your API key:

   ```powershell
   Remove-Item -Recurse "$HOME/.claude-shell"
   ```

3. Open a new terminal. The key bindings are gone; nothing else was installed.
