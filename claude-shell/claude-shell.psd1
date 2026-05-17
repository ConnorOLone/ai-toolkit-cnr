@{
    RootModule        = 'claude-shell.psm1'
    ModuleVersion     = '1.0.0'
    GUID              = '5aec9d97-369c-467a-a778-f73f33405e1d'
    Author            = 'Connor O''Lone'
    Description       = 'Terminal-side Claude integration for PowerShell 7: Alt+E generates a command from natural language, Alt+X explains the current command, and Ask-Claude is a pipe-through filter. Backends: a direct Anthropic API call or the local claude CLI.'
    PowerShellVersion = '7.4'

    FunctionsToExport = @('Invoke-ClaudeAsk', 'Set-ClaudeShellConfig', 'Register-ClaudeShellKeyHandlers')
    CmdletsToExport   = @()
    VariablesToExport = @()
    AliasesToExport   = @('Ask-Claude')

    PrivateData = @{
        PSData = @{
            Tags = @('Claude', 'Anthropic', 'AI', 'PSReadLine', 'CLI')
        }
    }
}
