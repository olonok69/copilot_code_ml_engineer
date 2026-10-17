# AGENT SETUP — day-to-day tools (GitHub Copilot / Part 2)

> Runbook for setting up the five day-to-day tools in a repo worked with GitHub Copilot.
> Guides: [`../../TECHNICAL_GUIDE.md`](../../TECHNICAL_GUIDE.md) §7 + §13 ·
> [`COPILOT_ADAPTATION.md`](./COPILOT_ADAPTATION.md) · [`copilot/README.md`](./copilot/README.md).

## The 5 tools

| # | Tool | Kind | Smoke test |
|---|---|---|---|
| 1 | **CodeGraph** | MCP (`.mcp.json`) + CLI | `codegraph explore "<a known symbol>"` / MCP `codegraph_explore` |
| 2 | **Serena** | MCP (`uvx`) | `find_referencing_symbols` on a known method |
| 3 | **Playwright** | **Built into the Copilot CLI** (add to `.vscode/mcp.json` only for the VS Code Local harness) | Open `https://example.com`, report the title |
| 4 | **Context7** | MCP (http) | A library docs query (e.g. pytest fixtures) |
| 5 | **kg** | Skill + `kg_query.sh` | `bash data/knowledge-graph/kg_query.sh find letter` |

## Why they often look "not installed"

1. `copilot` was launched from a **parent** folder — workspace `.mcp.json` is looked up from cwd to git root,
   and AGENTS.md only at the git root and cwd. Launch from the repo root.
2. The folder is **not trusted** — repo hooks and workspace MCP are gated by folder trust (and skipped in
   `-p` mode unless `--trust-folder`).
3. A server entry is missing the required `tools` array (`"tools": ["*"]`).
4. `codegraph` was installed after the session started — restart the session so the binary is on PATH.
5. Serena needs a first cold start (`uvx` download).
6. Skills are in `~/.claude/skills/` — the Copilot CLI does not read that folder; copy to `~/.copilot/skills/`.
7. A skill's `name` differs from its folder name — VS Code silently drops it.

## Agent instructions (short)

When asked to configure the tools in a repo:

1. Install host CLIs if missing (`codegraph`, `uvx`, `node`, `bash`).
2. Ensure `.mcp.json` lists codegraph / serena / context7 with `tools`; **do not** add Playwright for the CLI.
3. Ensure skills `kg` / `kg-refresh` and the `.github/instructions/` gates exist (run the bootstrap if needed).
4. Ask the human to restart `copilot` from the repo root and trust the folder; check `/mcp` and `/skills`.
5. Run all five smoke tests; report a pass/fail table with evidence.

Do **not** port Claude `settings.local.json` (repo files cannot hold Copilot allow/deny lists). Do **not**
push/PR unless asked — the hook denies it anyway.

## Pack paths

- MCP: [`copilot/mcp.json.example`](./copilot/mcp.json.example) · [`copilot/.vscode/mcp.json.example`](./copilot/.vscode/mcp.json.example)
- Bootstrap: [`scripts/bootstrap-copilot-repo.ps1.txt`](./scripts/bootstrap-copilot-repo.ps1.txt)
- Examples: [`../../examples/mcp/`](../../examples/mcp/), [`../../examples/codegraph/`](../../examples/codegraph/), [`../../examples/serena/`](../../examples/serena/)
