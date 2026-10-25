# Examples — adapted for GitHub Copilot

Same structure as the `ejemplos/` folders of the sibling volumes —
[Claude Code](https://github.com/olonok69/claude_code_ml_engineer/tree/master/ejemplos), [Cursor](https://github.com/olonok69/cursor_code_ml_engineer/tree/main/ejemplos) — and the
`examples/` folder of the [Pi volume](../../pi_code_ml_engineer/examples/), rewritten for **GitHub Copilot**
(this volume uses English folder names: `examples/`, `methodology/`). The methodology and the tool roles
(CodeGraph, Serena, Playwright, graphify) stay; the *surface* changes (instructions, skills, MCP, hooks, CLI).

Every Copilot claim here comes from the dated research notes
[`../docs/research/COPILOT_FINDINGS_2026-10-17.md`](../docs/research/COPILOT_FINDINGS_2026-10-17.md); where they say
UNVERIFIED, so do the examples. Full adaptation guide:
[`../docs/ai-agents-code-methodology/COPILOT_ADAPTATION.md`](../docs/ai-agents-code-methodology/COPILOT_ADAPTATION.md).

## Index (mapped to Session 1 of the course)

| Folder | Claude Code topic | Copilot equivalent |
|---|---|---|
| [`agents-md/`](./agents-md/) | Two-tier `CLAUDE.md` | `AGENTS.md` + `.github/copilot-instructions.md` + `.github/instructions/*.instructions.md` (`applyTo`) |
| [`context/`](./context/) | `/context`, `/compact` | `/context`, `/compact [focus]`, auto-compaction ~80%, >20 KiB output to a temp file |
| [`prompt-caching/`](./prompt-caching/) | Caching in Claude Code | Anthropic API demo + the honest answer: no control; VS Code Cache Explorer diagnoses |
| [`mcp/`](./mcp/) | `.mcp.json` + `claude mcp add` | `.mcp.json` (`mcpServers`, `tools` required) · `.vscode/mcp.json` (`servers`) · cloud-agent repo settings |
| [`skills-plugins/`](./skills-plugins/) | Slash commands + skills + plugins | `.github/skills/` (`day`, `atlassian`, `evidence`, `preview`, `audit`…) · prompt files (VS Code Local) · `copilot plugin` |
| [`subagents/`](./subagents/) | Task + Agent Teams | built-ins (`explore`, `task`…), `.github/agents/*.agent.md`, `/fleet`, `/delegate` to the cloud agent |
| [`hooks/`](./hooks/) | Hooks (`exit 2`) | `.github/hooks/*.json` (`preToolUse` deny / exit 2; timeout = fail-open) |
| [`permissions/`](./permissions/) | `settings.local.json` allowlist | `--allow-tool` / `--deny-tool` (deny wins), trusted folders, sandbox, VS Code `chat.tools.*` |
| [`automation/`](./automation/) | `claude -p` + Agent SDK | `copilot -p` in Actions, cloud-agent tasks API, Automations, code review rulesets, Copilot SDK |
| [`codegraph/`](./codegraph/) · [`serena/`](./serena/) | MCP in Claude | Same servers via Copilot MCP config |
| [`gsd/`](./gsd/) | GSD plugin | **No port** — plan mode + `/fleet` + role agents (+ Spec Kit, third-party-confirmed) |
| [`methodology/`](./methodology/) | 11-stage flow | Same flow + Copilot surface; real read-only tools with offline tests in [`methodology/tools/`](./methodology/tools/); shared-record scripts in [`methodology/s3-sync/`](./methodology/s3-sync/) |

## What is NOT there (or differs) — read before copying blindly

| Claude Code capability | In Copilot |
|---|---|
| `~/.claude/CLAUDE.md` | **Not read** by the CLI → `~/.copilot/copilot-instructions.md` |
| `~/.claude/skills/` | **Not read** by the CLI (VS Code does) → `~/.copilot/skills/` or `copilot skill add` |
| `settings.json` `permissions.allow/deny` in the repo | **No repo-level allow/deny** → hooks; org-wide via managed settings |
| `@path` imports | CLI only (`AGENTS.md`, `CLAUDE.md`, `copilot-instructions.md`); VS Code: NOT DOCUMENTED |
| Prompt caching control | None anywhere; billed cached-input / cache-write |
| Agent Teams | No 1:1 port → `/fleet`, background subagents + `write_agent`, sidekick agents, `/delegate` |
| GSD | Claude Code only |
| Auto-memory `MEMORY.md` | Copilot Memory (cloud, preview, 28-day expiry) / VS Code `/memories` / CLI `/chronicle` — complements, never the source of truth |
| One hook schema | **Two**: CLI/cloud/VS Code Copilot harness vs VS Code Local harness |

What travels almost unchanged: MCP servers (CodeGraph/Serena/Context7; Playwright is built into the CLI), the
11-stage discipline, the `data/changes/` ledgers, `_diag_*.py` oracles, Playwright for the contract, Docker for
the outbound check. The CLI even reads `CLAUDE.md`, `.claude/rules/`, `.claude/agents/`, `.claude/skills/`
(project) and hooks in `.claude/settings.json`.

## Live surface in this repo

Root [`../.github/`](../.github/) (skills `audit`, `audit-python`, `deploy-staging`; agent `refactor-scout`; hook
`block-external-git`; instructions) + [`../.mcp.json`](../.mcp.json) + [`../AGENTS.md`](../AGENTS.md).
Demo targets: [`../ex_npm/`](../ex_npm/) · [`../ex_app/`](../ex_app/) · [`../ex_staging/`](../ex_staging/).
