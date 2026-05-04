# install.ps1 — Copy AI toolkit assets into Claude Code config directories (Windows)
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\install.ps1
#
# What it does:
#   - Copies skills/<name>/  → ~/.claude/skills/<name>/
#   - Copies agents/*.md     → ~/.claude/agents/*.md
#   - Copies rules/*.md      → ~/.claude/rules/*.md
#   - Copies configs/CLAUDE.md → ~/.claude/CLAUDE.md (user-level context)
#
# Does NOT copy examples/ — those are reference-only.
# Safe to re-run — overwrites existing files.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoDir = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not $RepoDir) {
    $RepoDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
}
$ClaudeDir = Join-Path $env:USERPROFILE ".claude"

Write-Host "AI Toolkit Installer (Windows)"
Write-Host "Repo:   $RepoDir"
Write-Host "Target: $ClaudeDir"
Write-Host ""

# --- Skills ---

$SkillsSource = Join-Path $RepoDir "skills"
if (Test-Path $SkillsSource) {
    $SkillsDest = Join-Path $ClaudeDir "skills"
    New-Item -ItemType Directory -Path $SkillsDest -Force | Out-Null
    $count = 0
    foreach ($skillDir in Get-ChildItem -Path $SkillsSource -Directory) {
        $skillMd = Join-Path $skillDir.FullName "SKILL.md"
        if (-not (Test-Path $skillMd)) {
            Write-Host "  skipped: $($skillDir.Name) (no SKILL.md)"
            continue
        }
        $dest = Join-Path $SkillsDest $skillDir.Name
        if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
        Copy-Item -Recurse -Force $skillDir.FullName $dest
        Write-Host "  copied skill: $($skillDir.Name)"
        $count++
    }
    Write-Host "Skills: $count copied"
} else {
    Write-Host "Skills: skipped (no skills/ directory)"
}

Write-Host ""

# --- Agents ---

$AgentsSource = Join-Path $RepoDir "agents"
if (Test-Path $AgentsSource) {
    $AgentsDest = Join-Path $ClaudeDir "agents"
    New-Item -ItemType Directory -Path $AgentsDest -Force | Out-Null
    $count = 0
    foreach ($agent in Get-ChildItem -Path $AgentsSource -Filter "*.md" -File) {
        if ($agent.Name -eq "README.md") { continue }
        Copy-Item -Force $agent.FullName (Join-Path $AgentsDest $agent.Name)
        Write-Host "  copied agent: $($agent.Name)"
        $count++
    }
    Write-Host "Agents: $count copied"
} else {
    Write-Host "Agents: skipped (no agents/ directory)"
}

Write-Host ""

# --- Rules ---

$RulesSource = Join-Path $RepoDir "rules"
if (Test-Path $RulesSource) {
    $RulesDest = Join-Path $ClaudeDir "rules"
    New-Item -ItemType Directory -Path $RulesDest -Force | Out-Null
    $count = 0
    foreach ($rule in Get-ChildItem -Path $RulesSource -Filter "*.md" -File) {
        if ($rule.Name -eq "README.md") { continue }
        Copy-Item -Force $rule.FullName (Join-Path $RulesDest $rule.Name)
        Write-Host "  copied rule: $($rule.Name)"
        $count++
    }
    Write-Host "Rules: $count copied"
} else {
    Write-Host "Rules: skipped (no rules/ directory)"
}

Write-Host ""

# --- User-level CLAUDE.md ---

$ClaudeMd = Join-Path $RepoDir "configs" "CLAUDE.md"
if (Test-Path $ClaudeMd) {
    Copy-Item -Force $ClaudeMd (Join-Path $ClaudeDir "CLAUDE.md")
    Write-Host "CLAUDE.md: copied to $ClaudeDir\CLAUDE.md"
} else {
    Write-Host "CLAUDE.md: skipped (no configs/CLAUDE.md found)"
}

# --- Toolkit path marker ---

Set-Content -Path (Join-Path $ClaudeDir ".toolkit-path") -Value $RepoDir -Encoding UTF8
Write-Host "Toolkit path: saved to $ClaudeDir\.toolkit-path"

Write-Host ""
Write-Host "Done."
Write-Host ""
Write-Host "Note: Windows uses copies, not symlinks. Re-run this script after updating the toolkit."
