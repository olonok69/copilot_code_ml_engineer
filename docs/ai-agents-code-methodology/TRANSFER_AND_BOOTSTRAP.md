# Transfer And Bootstrap Guide

This guide helps you move the methodology package to another machine and start configuration in a different repository.

## A) Package this folder on source machine

From repo root in PowerShell:

```powershell
$source = "data/changes/ai-agent-methodology"
$target = "data/changes/ai-agent-methodology-package.zip"
if (Test-Path $target) { Remove-Item $target -Force }
Compress-Archive -Path $source -DestinationPath $target -Force
Write-Host "Created: $target"
```

Send `data/changes/ai-agent-methodology-package.zip` to the other machine.

## B) Unpack on target machine

In the target repository root:

```powershell
$zip = "data/changes/ai-agent-methodology-package.zip"
Expand-Archive -Path $zip -DestinationPath "data/changes" -Force
```

Expected location after extract:

- `data/changes/ai-agent-methodology`

## C) Bootstrap in the target repo

### C1) Shared ledgers (tool-agnostic)

Rename and run:

```powershell
Rename-Item data/changes/ai-agent-methodology/scripts/bootstrap-new-repo.ps1.txt bootstrap-new-repo.ps1
pwsh data/changes/ai-agent-methodology/scripts/bootstrap-new-repo.ps1
```

This creates starter docs if missing:

1. `data/changes/STATUS.md`
2. `data/changes/FOLLOWUPS.md`
3. `data/changes/SHARP_EDGES.md`
4. `data/changes/_handover_template.md`
5. `data/changes/_qa_acceptance_template.md`
6. Working-agreement and orientation templates

Note: scripts are shipped as `.ps1.txt` specifically to reduce active-content blocking by mail scanners.

### C2) GitHub Copilot surface

```powershell
Rename-Item data/changes/ai-agent-methodology/scripts/bootstrap-copilot-repo.ps1.txt bootstrap-copilot-repo.ps1
pwsh data/changes/ai-agent-methodology/scripts/bootstrap-copilot-repo.ps1
# -Force overwrites existing files; -SkipCloudAgent skips copilot-setup-steps.yml
```

This creates if missing (never overwrites without `-Force`):

1. `AGENTS.md` and `.github/copilot-instructions.md`
2. `.github/instructions/*.instructions.md` — methodology gates, tool prevalence, Atlassian
3. `.github/skills/{kg,kg-refresh,methodology-plan,sanitise-diff,day,atlassian,evidence}/`
4. `.github/agents/refactor-scout.agent.md`
5. `.github/hooks/block-external-git.{json,sh,ps1}` + its offline test
6. `.mcp.json` (CLI + VS Code Copilot harness) and `.vscode/mcp.json` (VS Code Local harness)
7. `.github/workflows/copilot-setup-steps.yml` (cloud agent; must reach the default branch)
8. Appends `.codegraph/`, `IDENTITY.md` and `.github/copilot/settings.local.json` to `.gitignore`

Then: `bash .github/hooks/test-block-external-git.sh` → `codegraph init` → launch `copilot` from the repo
root and trust the folder → `/mcp`, `/skills`, `/instructions`. See `COPILOT_ADAPTATION.md` and
`copilot/README.md`. The script does not commit or push — the human reviews and commits.

## D) First-day setup checklist

1. Fill `STATUS.md` with current in-flight work.
2. Add 3-5 initial invariants in `SHARP_EDGES.md`.
3. Write the output-contract paragraph in `AGENTS.md`.
4. Define scoped test commands by subsystem.
5. Verify MCP tools respond (`/mcp`) and the hook test passes; test the hook against `/pr automerge`.
6. Run one issue fully with RED -> GREEN + contract verification.

## E) If knowledge graph is not available

Use this fallback process:

1. Maintain `STATUS.md` and per-ticket folders as your source of truth.
2. Search by contract fields, symptom terms, and key symbols.
3. Use git history overlap (files touched) to find related prior fixes.
4. Keep `SHARP_EDGES.md` short and current.

The `kg` skill documents this fallback explicitly.
