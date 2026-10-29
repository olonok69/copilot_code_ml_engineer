# Package Manifest

Artifacts included in the portable methodology package (GitHub Copilot edition).

## Core docs

1. `README.md`
2. `TECHNICAL.md` (Spanish: `TECHNICAL_ES.md`)
3. `COPILOT_ADAPTATION.md`
4. `START_HERE.md`
5. `TRANSFER_AND_BOOTSTRAP.md`
6. `NEW_REPO_CONFIGURATION_PLAN.md`
7. `AGENT_SETUP_TOOLS.md`

## Visual flow

1. `flow.mmd` (Mermaid source)
2. `flow.png`

## Templates

1. `templates/ORIENTATION_TEMPLATE.md`
2. `templates/STATUS_TEMPLATE.md`
3. `templates/FOLLOWUPS_TEMPLATE.md`
4. `templates/SHARP_EDGES_TEMPLATE.md`
5. `templates/TEST_MAP_TEMPLATE.md`
6. `templates/ISSUE_NOTE_TEMPLATE.md`
7. `templates/HANDOVER_TEMPLATE.md`
8. `templates/QA_ACCEPTANCE_TEMPLATE.md`
9. `templates/COPILOT_WORKING_AGREEMENT_TEMPLATE.md`

## Copilot surface pack (`copilot/`)

1. `copilot/README.md`
2. `copilot/AGENTS.md.example`
3. `copilot/copilot-instructions.md.example`
4. `copilot/instructions/00-methodology-core.instructions.md`
5. `copilot/instructions/01-tool-prevalence.instructions.md`
6. `copilot/instructions/02-gates-and-handoff.instructions.md`
7. `copilot/instructions/atlassian.instructions.md`
8. `copilot/mcp.json.example` — CodeGraph, Serena, Context7 (`mcpServers`; Playwright is built into the CLI)
9. `copilot/.vscode/mcp.json.example` — VS Code Local harness (`servers`)
10. `copilot/hooks/block-external-git.json` + `.sh` + `.ps1` + `test-block-external-git.sh`
11. `copilot/agents/refactor-scout.agent.md` — read-only scout
12. `copilot/copilot-setup-steps.yml.example` — cloud-agent environment
13. `copilot/skills/{day,atlassian,evidence,preview,kg,kg-refresh,methodology-plan,sanitise-diff}/SKILL.md`

## Scripts

1. `scripts/bootstrap-new-repo.ps1.txt` — ledgers + shared templates
2. `scripts/bootstrap-copilot-repo.ps1.txt` — the Copilot surface (never overwrites without `-Force`)

## Not in this edition

The Cursor surface (`cursor/`, `CURSOR_ADAPTATION.md`), the Confluence publishing pack and `flow.svg` live in
the Cursor volume: [`cursor_code_ml_engineer`](https://github.com/olonok69/cursor_code_ml_engineer).

## Intended use

1. Copy the package to the target repo under `data/changes/ai-agent-methodology`.
2. Rename the two `scripts/*.ps1.txt` to `.ps1` and run them from the target repo root.
3. Fill the generated templates and start the first issue with the planning template in `COPILOT_ADAPTATION.md`.
