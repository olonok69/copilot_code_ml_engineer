# block-external-git.ps1 — GitHub Copilot preToolUse guard (PowerShell twin of block-external-git.sh).
# Same contract: exit 2 + a deny decision on stdout for push / PR / merge / release / deploy commands;
# exit 0 + "{}" otherwise (never "allow": that could auto-approve the tool).
# Handles both payload shapes: {toolName, toolArgs (string|object)} and {tool_name, tool_input}.
# ⚠️ Timeouts are fail-OPEN; crashes are fail-CLOSED for preToolUse. Keep it fast, never throw.
# ⚠️ The cloud agent runs Linux and ignores the "powershell" entry — the .sh twin is what runs there.
$ErrorActionPreference = "SilentlyContinue"

$raw = [Console]::In.ReadToEnd()
$payload = $null
try { $payload = $raw | ConvertFrom-Json } catch { $payload = $null }

$tool = ""
$cmd = ""
if ($null -ne $payload) {
    if ($payload.PSObject.Properties.Name -contains "toolName") { $tool = [string]$payload.toolName }
    elseif ($payload.PSObject.Properties.Name -contains "tool_name") { $tool = [string]$payload.tool_name }

    $toolArgs = $null
    if ($payload.PSObject.Properties.Name -contains "toolArgs") { $toolArgs = $payload.toolArgs }
    elseif ($payload.PSObject.Properties.Name -contains "tool_input") { $toolArgs = $payload.tool_input }

    if ($toolArgs -is [string]) {
        try { $toolArgs = $toolArgs | ConvertFrom-Json } catch { $toolArgs = [pscustomobject]@{ command = $toolArgs } }
    }
    if ($null -ne $toolArgs) {
        foreach ($k in @("command", "cmd", "script")) {
            if ($toolArgs.PSObject.Properties.Name -contains $k -and $toolArgs.$k) { $cmd = [string]$toolArgs.$k; break }
        }
    }
} else {
    $cmd = $raw   # unparseable payload: scan the raw text (fail-safe)
}

if ($tool -and ($tool -notmatch '(?i)bash|powershell|shell|terminal|exec|command')) {
    Write-Output '{}'
    exit 0
}

$patterns = @(
    '(?i)(^|[;&|(`\s])git(\s+-\S+(\s+[^-\s]\S*)?)*\s+push(\s|$)',
    '(?i)gh\s+pr\s+(create|merge|ready)',
    '(?i)gh\s+api\s.*(/merges|/pulls/\d+/merge)',
    '(?i)gh\s+release\s+create',
    '(?i)terraform\s+apply',
    '(?i)kubectl\s+apply',
    '(?i)helm\s+(upgrade|install)',
    '(?i)aws\s.*\sdeploy'
)

foreach ($p in $patterns) {
    if ($cmd -match $p) {
        $reason = "Methodology handoff gate: outward-facing command blocked (push / PR / merge / release / deploy). The human owns these. Prepare the branch and a handover note instead."
        $out = [ordered]@{
            permissionDecision       = "deny"
            permissionDecisionReason = $reason
            hookSpecificOutput       = [ordered]@{
                hookEventName            = "PreToolUse"
                permissionDecision       = "deny"
                permissionDecisionReason = $reason
            }
        } | ConvertTo-Json -Compress -Depth 4
        Write-Output $out
        [Console]::Error.WriteLine("block-external-git: denied: $cmd")
        exit 2
    }
}

Write-Output '{}'
exit 0
