# copilot_code — course / workshop repo

Lean always-on memory. Detail lives in the guides and `examples/`.

## What this repo is

Material for the **GitHub Copilot** course (3 parts): guides, PPTX, and runnable examples under `examples/`.
Not an application codebase — it demos the Copilot customization surface (skills, agents, hooks, MCP).

## Demo surface (this repo's `.github/` + `.mcp.json`)

Wired for live testing when you run `copilot` from **this** repo root (trust the folder when asked) or open
it in VS Code with the Copilot harness:

| Piece | Path | How to try |
|---|---|---|
| Skills | `.github/skills/audit`, `audit-python`, `deploy-staging` | `/audit ex_npm` · `/audit-python ex_app` · `/deploy-staging ex_staging` |
| Custom agent | `.github/agents/refactor-scout.agent.md` | `copilot --agent refactor-scout` or "use the refactor-scout agent on …" |
| Instructions | `.github/copilot-instructions.md`, `.github/instructions/lean-memory.instructions.md` | `/instructions` (CLI) lists them |
| Hook | `.github/hooks/block-external-git.json` (+ `.sh` / `.ps1`) | ask the agent to `git push` → denied |
| MCP | `.mcp.json` (context7 + codegraph) | `/mcp` — Playwright is built into the CLI, not configured here |

Canonical teaching copies live under `examples/*` (keep them in sync if you edit).

## Rules

- Human owns push / PR / merge / deploy (see `.github/copilot-instructions.md`).
- Show real command output; evidence over claims.

## Pointers

- Talk track: `SPEAKER_GUIDE.md` · live demos: `DEMO_RUNBOOK.md` · reference: `TECHNICAL_GUIDE.md`
- Methodology pack: `docs/ai-agents-code-methodology/`
- Copilot facts (dated): `docs/research/COPILOT_FINDINGS_2026-10-17.md`
