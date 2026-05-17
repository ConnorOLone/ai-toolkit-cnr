# claude-shell — add these lines to your PowerShell 7 $PROFILE (Windows or macOS).
#
# Edit your profile:   notepad $PROFILE   (Windows)  /  nano $PROFILE   (macOS)
# Create it if needed: New-Item -ItemType File -Path $PROFILE -Force
# Apply changes:       start a new terminal, or run  . $PROFILE
#
# Tip: instead of editing by hand, open Claude Code in the repo and say
#      "follow claude-shell/SETUP.md" — it does all of this for you.

# 1. Point this at wherever you cloned the ai-toolkit-cnr repo. Forward slashes
#    work on every OS. Adjust the path to match this machine.
$ClaudeShellRepo = "$HOME/codehub/ai-toolkit-cnr"

# 2. Import the module and register the Alt+E / Alt+X key bindings.
Import-Module (Join-Path $ClaudeShellRepo 'claude-shell/claude-shell.psd1')
Register-ClaudeShellKeyHandlers

# 3. (Optional) An extra binding — Alt+G drafts a commit message from the staged diff.
#    This is the pattern for adding your own bindings; see the README "How to extend".
Set-PSReadLineKeyHandler -Chord 'Alt+g' -BriefDescription 'ClaudeCommitMsg' `
    -LongDescription 'Insert a git commit command with a message generated from the staged diff' -ScriptBlock {
    $diff = git diff --staged
    if (-not $diff) {
        [Microsoft.PowerShell.PSConsoleReadLine]::Insert('# nothing staged')
        return
    }
    $msg = $diff | Ask-Claude 'Write a Conventional Commits message for this staged diff. Output only the message, single line.'
    if ($msg) {
        [Microsoft.PowerShell.PSConsoleReadLine]::RevertLine()
        [Microsoft.PowerShell.PSConsoleReadLine]::Insert("git commit -m `"$msg`"")
    }
}
