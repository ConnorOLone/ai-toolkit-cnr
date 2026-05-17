# claude-shell.psm1 — terminal-side Claude integration for PowerShell 7.4+
# Three features (Alt+E translate, Alt+X explain, Ask-Claude filter) over two
# backends: a direct HTTPS POST to api.anthropic.com, or the local `claude` CLI.
# No globals, no background jobs, no servers. See README.md for the audit summary.

Set-StrictMode -Version Latest

$script:ConfigPath = Join-Path $env:USERPROFILE '.claude-shell\config.json'

# Defaults — overridden by config.json, which is written only by Set-ClaudeShellConfig.
$script:Defaults = @{
    Model            = 'claude-haiku-4-5-20251001'
    MaxTokens        = 1024
    ApiEndpoint      = 'https://api.anthropic.com/v1/messages'
    AnthropicVersion = '2023-06-01'
    Backend          = 'Api'
}

# System prompts for the three features — kept here so they are easy to review and tweak.
$script:Prompts = @{
    Translate = 'You translate natural language into a single PowerShell command for Windows. Output ONLY the command, no explanation, no markdown, no backticks. The command must be a single line. Prefer modern PowerShell 7 syntax.'
    Explain   = 'You explain shell commands. Given a command, reply with a plain-English explanation of what it does in 1-2 sentences. No markdown, no code blocks, no preamble.'
    Ask       = 'You are a concise assistant running inside a terminal pipeline. Answer directly. Output only what was asked, with no preamble or sign-off.'
}

# === Configuration ===========================================================

# Reads config.json (if present), layers it over the defaults, and falls back to
# the ANTHROPIC_API_KEY environment variable for the key. Returns a hashtable.
function Get-ClaudeShellConfig {
    $config = $script:Defaults.Clone()
    if (Test-Path $script:ConfigPath) {
        try {
            $file = Get-Content -Raw -Path $script:ConfigPath -ErrorAction Stop | ConvertFrom-Json -AsHashtable
            foreach ($key in @($file.Keys)) {
                if ($null -ne $file[$key] -and '' -ne $file[$key]) { $config[$key] = $file[$key] }
            }
        } catch {
            Write-Error "claude-shell: config at $script:ConfigPath is not valid JSON ($($_.Exception.Message)). Using defaults."
        }
    }
    if (-not $config.ContainsKey('ApiKey') -and $env:ANTHROPIC_API_KEY) {
        $config['ApiKey'] = $env:ANTHROPIC_API_KEY
    }
    return $config
}

# Writes selected settings to config.json (in the user's profile dir, not the repo).
# Only the parameters you pass are changed; everything else in the file is preserved.
function Set-ClaudeShellConfig {
    [CmdletBinding()]
    param(
        [string]$ApiKey,
        [string]$Model,
        [int]$MaxTokens,
        [string]$ApiEndpoint,
        [string]$AnthropicVersion,
        [ValidateSet('Api', 'ClaudeCli')]
        [string]$Backend
    )
    $dir = Split-Path -Parent $script:ConfigPath
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }

    $existing = @{}
    if (Test-Path $script:ConfigPath) {
        try { $existing = Get-Content -Raw $script:ConfigPath | ConvertFrom-Json -AsHashtable } catch { $existing = @{} }
    }
    foreach ($p in $PSBoundParameters.GetEnumerator()) { $existing[$p.Key] = $p.Value }

    $existing | ConvertTo-Json | Set-Content -Path $script:ConfigPath -Encoding UTF8
    Write-Host "claude-shell: saved $($PSBoundParameters.Count) setting(s) to $script:ConfigPath" -ForegroundColor Green
}

# === Backends ================================================================

# Removes a leading ```lang fence and trailing ``` fence if the model added them
# despite being told not to.
function Remove-CodeFence {
    param([string]$Text)
    if ([string]::IsNullOrWhiteSpace($Text)) { return $Text }
    $t = $Text.Trim()
    if ($t.StartsWith('```')) {
        $t = $t -replace '^```[^\r\n]*\r?\n?', ''
        $t = $t -replace '\r?\n?```\s*$', ''
    }
    return $t.Trim()
}

# Backend 1: a direct HTTPS request to the Anthropic Messages API.
function Invoke-ClaudeApi {
    param([hashtable]$Config, [string]$SystemPrompt, [string]$UserContent)

    if (-not $Config.ContainsKey('ApiKey') -or -not $Config['ApiKey']) {
        Write-Error 'claude-shell: no API key. Run Set-ClaudeShellConfig -ApiKey <key>, or set $env:ANTHROPIC_API_KEY.'
        return $null
    }
    $body = @{
        model      = $Config.Model
        max_tokens = $Config.MaxTokens
        messages   = @(@{ role = 'user'; content = $UserContent })
    }
    if ($SystemPrompt) { $body['system'] = $SystemPrompt }
    $headers = @{
        'x-api-key'         = $Config.ApiKey
        'anthropic-version' = $Config.AnthropicVersion
        'content-type'      = 'application/json'
    }
    try {
        $response = Invoke-RestMethod -Method Post -Uri $Config.ApiEndpoint -Headers $headers `
            -Body ($body | ConvertTo-Json -Depth 6) -TimeoutSec 30 -ErrorAction Stop
        return $response.content[0].text
    } catch {
        Write-Error "claude-shell: API request failed — $($_.Exception.Message)"
        return $null
    }
}

# Backend 2: shell out to the local `claude` CLI. Uses whatever auth Claude Code
# is configured with (e.g. a Claude subscription), so it incurs no direct API cost.
# Tools are disabled and MCP is suppressed so each call is a plain one-shot prompt.
function Invoke-ClaudeCli {
    param([hashtable]$Config, [string]$SystemPrompt, [string]$UserContent)

    if (-not (Get-Command claude -CommandType Application -ErrorAction SilentlyContinue)) {
        Write-Error 'claude-shell: Backend is ClaudeCli but `claude` was not found on PATH.'
        return $null
    }
    $cliArgs = @(
        '--print', '--model', $Config.Model,
        '--output-format', 'text',
        '--tools', '',              # disable all tools — this is a text-only prompt
        '--strict-mcp-config',      # ignore any configured MCP servers
        '--no-session-persistence'  # do not write a session transcript to disk
    )
    if ($SystemPrompt) { $cliArgs += @('--system-prompt', $SystemPrompt) }
    try {
        $output = $UserContent | & claude @cliArgs 2>&1
        $errs = @($output | Where-Object { $_ -is [System.Management.Automation.ErrorRecord] })
        $text = @($output | Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] })
        if ($LASTEXITCODE -ne 0) {
            Write-Error "claude-shell: the claude CLI exited with code $LASTEXITCODE — $($errs -join '; ')"
            return $null
        }
        return ($text -join "`n")
    } catch {
        Write-Error "claude-shell: failed to run the claude CLI — $($_.Exception.Message)"
        return $null
    }
}

# The single entry point used by all three features: pick the backend from
# config, call it, strip any stray code fences. Returns $null on failure.
function Invoke-Claude {
    param([string]$SystemPrompt, [string]$UserContent)

    $config = Get-ClaudeShellConfig
    $raw = switch ($config.Backend) {
        'ClaudeCli' { Invoke-ClaudeCli -Config $config -SystemPrompt $SystemPrompt -UserContent $UserContent }
        default     { Invoke-ClaudeApi -Config $config -SystemPrompt $SystemPrompt -UserContent $UserContent }
    }
    if ($null -eq $raw) { return $null }
    return (Remove-CodeFence -Text $raw)
}

# === Public: Ask-Claude ======================================================

# Pipe-through filter. Reads piped stdin and/or a -Prompt, sends both to Claude,
# writes the answer to stdout so it composes with the rest of the pipeline.
function Invoke-ClaudeAsk {
    [CmdletBinding()]
    [OutputType([string])]
    param(
        [Parameter(Position = 0)]
        [string]$Prompt,

        [Parameter(ValueFromPipeline)]
        [string]$InputObject
    )
    begin { $piped = [System.Collections.Generic.List[string]]::new() }
    process { if ($null -ne $InputObject) { $piped.Add($InputObject) } }
    end {
        $stdin = ($piped -join "`n").Trim()
        if (-not $Prompt -and -not $stdin) {
            Write-Error 'Ask-Claude: supply a prompt, pipe input, or both.'
            return
        }
        $content = if ($stdin) { "$Prompt`n`n$stdin".Trim() } else { $Prompt }
        $answer = Invoke-Claude -SystemPrompt $script:Prompts.Ask -UserContent $content
        if ($answer) { Write-Output $answer }
    }
}
Set-Alias -Name Ask-Claude -Value Invoke-ClaudeAsk

# === Public: PSReadLine key handlers =========================================

# Registers Alt+E and Alt+X. Call this from $PROFILE (see examples/profile-snippet.ps1).
# The handler script blocks are defined here, in module scope, so they can reach the
# module-private Invoke-Claude and $script:Prompts. That is why binding lives here and
# not in the profile — and why Import-Module itself stays free of any PSReadLine calls.
function Register-ClaudeShellKeyHandlers {
    [CmdletBinding()]
    param()
    if (-not (Get-Command Set-PSReadLineKeyHandler -ErrorAction SilentlyContinue)) {
        Write-Error 'claude-shell: PSReadLine is required for the Alt+E / Alt+X key bindings.'
        return
    }

    # Alt+E — replace the buffer: natural language in, a PowerShell command out.
    Set-PSReadLineKeyHandler -Chord 'Alt+e' -BriefDescription 'ClaudeTranslate' `
        -LongDescription 'Translate the current buffer into a PowerShell command' -ScriptBlock {
        $line = $null; $cursor = $null
        [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$line, [ref]$cursor)
        if ([string]::IsNullOrWhiteSpace($line)) { return }

        $original = $line
        # Show a static hourglass in the buffer while the (blocking) request runs.
        [Microsoft.PowerShell.PSConsoleReadLine]::Replace(0, $line.Length, "$([char]0x231B)")
        $command = Invoke-Claude -SystemPrompt $script:Prompts.Translate -UserContent $original

        # The buffer now holds just the 1-char hourglass; swap in the result, or
        # restore the original input if the request failed.
        $replacement = if ($command) { $command } else { $original }
        [Microsoft.PowerShell.PSConsoleReadLine]::Replace(0, 1, $replacement)
    }

    # Alt+X — explain the current buffer without changing or running it.
    Set-PSReadLineKeyHandler -Chord 'Alt+x' -BriefDescription 'ClaudeExplain' `
        -LongDescription 'Explain the current command without running it' -ScriptBlock {
        $line = $null; $cursor = $null
        [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$line, [ref]$cursor)
        if ([string]::IsNullOrWhiteSpace($line)) { return }

        Write-Host ''
        Write-Host "  $([char]0x231B)" -NoNewline -ForegroundColor DarkGray
        $explanation = Invoke-Claude -SystemPrompt $script:Prompts.Explain -UserContent $line
        Write-Host ("`r" + (' ' * 8) + "`r") -NoNewline   # clear the hourglass
        if ($explanation) {
            Write-Host "  $explanation" -ForegroundColor Cyan
        } else {
            Write-Host '  (claude-shell: no explanation returned)' -ForegroundColor DarkGray
        }
        # Redraw the prompt with the original buffer intact, ready to run.
        [Microsoft.PowerShell.PSConsoleReadLine]::InvokePrompt()
    }
}

Export-ModuleMember -Function Invoke-ClaudeAsk, Set-ClaudeShellConfig, Register-ClaudeShellKeyHandlers `
    -Alias Ask-Claude
