# AI Agent Methodology Pack - Start Here

Use this folder as a portable starter kit for a different repository and machine. This copy is the
**GitHub Copilot** edition (course volume 3). The Cursor edition lives in the Cursor volume
([`cursor_code_ml_engineer`](../../../cursor_code_ml_engineer/)), and the original Claude Code setup in the Claude
Code volume ([`claude_code_ml_engineer`](../../../claude_code_ml_engineer/)); a Pi edition is in
[`pi_code_ml_engineer`](../../../pi_code_ml_engineer/).

## Goal

Set up a reliable AI-agent workflow with GitHub Copilot with:

1. Clear guardrails — enforced by a hook, not only written down.
2. Reproducible triage and verification.
3. Lightweight but durable documentation.
4. Optional MCP tool layer (CodeGraph, Serena, Context7; Playwright is built into the Copilot CLI) and the
   ticket graph (`kg`).

## Read in order

1. `README.md` — the methodology (tool-agnostic).
2. `TECHNICAL.md` — the mechanics.
3. `COPILOT_ADAPTATION.md` — surfaces, file mapping, hooks, the two new holes to close.
4. `copilot/README.md` — the copy-ready files and where each goes.
5. `TRANSFER_AND_BOOTSTRAP.md` — moving the pack and installing it.

## Fast path (30–60 minutes)

1. Copy this whole folder into the target repository under `data/changes/ai-agent-methodology`.
2. Rename and run the two bootstrap scripts from the target repo root:

```powershell
Rename-Item data/changes/ai-agent-methodology/scripts/bootstrap-new-repo.ps1.txt bootstrap-new-repo.ps1
pwsh data/changes/ai-agent-methodology/scripts/bootstrap-new-repo.ps1

Rename-Item data/changes/ai-agent-methodology/scripts/bootstrap-copilot-repo.ps1.txt bootstrap-copilot-repo.ps1
pwsh data/changes/ai-agent-methodology/scripts/bootstrap-copilot-repo.ps1
```

3. `bash .github/hooks/test-block-external-git.sh` → 0 failures; `codegraph init`.
4. Launch `copilot` from the repo root, **trust the folder**, check `/mcp`, `/skills`, `/instructions`.
5. Fill `data/changes/` templates + the output-contract paragraph in `AGENTS.md` + the working agreement.
6. Start the first issue in **plan mode** (`/plan`) using the planning template in `COPILOT_ADAPTATION.md`.

## What this pack gives you

1. Methodology overview and technical mechanics.
2. The Copilot adaptation and its copy-ready surface (`copilot/`).
3. Transfer and initialization instructions + bootstrap scripts.
4. Ready-to-fill templates for status, sharp edges, handover, QA and the Copilot working agreement.

## Non-negotiable rules

1. Plan -> agree -> implement.
2. Verify at output contract level.
3. Keep fixes generic (class-level, not one example only).
4. Keep a durable change trail.
5. Human owns external actions (push, PR, merge, deploy, external comms) — `/pr automerge` included.
