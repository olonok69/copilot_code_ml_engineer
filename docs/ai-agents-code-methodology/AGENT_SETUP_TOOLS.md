# AGENT SETUP — day-to-day tools (GitHub Copilot / Session 2)

> Runbook for setting up the five day-to-day tools in a repo worked with GitHub Copilot.
> Guides: [`../../TECHNICAL_GUIDE.md`](../../TECHNICAL_GUIDE.md) §7 + §13 ·
> [`COPILOT_ADAPTATION.md`](./COPILOT_ADAPTATION.md) ·
> [`COPILOT_REPLICATION_CHECKLIST.md`](./COPILOT_REPLICATION_CHECKLIST.md) ·
> [`copilot/README.md`](./copilot/README.md).

## The 5 tools

| # | Tool | Kind | Smoke test |
|---|---|---|---|
| 1 | **CodeGraph** | MCP (`.mcp.json`) + CLI | `codegraph explore "<a known symbol>"` / MCP `codegraph_explore` |
| 2 | **Serena** | MCP (`uvx`) | `find_referencing_symbols` on a known method |
| 3 | **Playwright** | **Built into the Copilot CLI** (add to `.vscode/mcp.json` only for the VS Code Local harness) | Open `https://example.com`, report the title |
| 4 | **Context7** | MCP (http) | A library docs query (e.g. pytest fixtures) |
| 5 | **kg** | Skill + `kg_query.sh` | `bash data/knowledge-graph/kg_query.sh find letter` |

## Choose the WSL execution mode

The Copilot surface and the execution environment are separate choices. For a repo on the Windows
`D:` drive, use `/mnt/d/...` inside WSL.

- **CLI:** install Copilot CLI in the selected WSL distro and launch it from the repo root in that
  distro's terminal. Its `~/.copilot/skills/`, PATH, tools, and credentials are the WSL user's, not
  automatically the Windows user's.
- **VS Code Remote - WSL:** install the VS Code WSL extension on Windows, then open the repo from a WSL
  terminal with `code .` (or use **WSL: Connect to WSL**). Confirm the status bar names the distro and
  install Copilot extensions into WSL when prompted. Run shell/tool smoke tests in that remote window.
- **Do not use a Windows-local `\\wsl$` / `\\wsl.localhost` file path as a substitute** for Remote - WSL.
  A Windows-local window may use Windows extensions, PATH, and personal configuration. It is a distinct
  test environment.

See the [WSL replication checks](./COPILOT_REPLICATION_CHECKLIST.md#2-wsl-is-an-execution-environment-not-a-copilot-surface)
and Microsoft's [Developing in WSL](https://code.visualstudio.com/docs/remote/wsl) guide.

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
4. Ask the human to restart the intended Copilot surface in the target environment and trust the folder;
   for CLI, check `/mcp` and `/skills`; for VS Code, inspect the active Customizations and MCP view in
   the correct local or Remote - WSL window.
5. Run all five smoke tests; report a pass/fail table with evidence.

Do **not** port Claude `settings.local.json` (repo files cannot hold Copilot allow/deny lists). Do **not**
push/PR unless asked — the hook denies it anyway.

For a Claude Code → Copilot comparison, the five tool checks are only one layer. Use the
[replication checklist](./COPILOT_REPLICATION_CHECKLIST.md) to verify orientation, all eight methodology
skills, side-effect boundaries, and redacted evidence. It distinguishes discovery from behavior and marks
credentialed, client-data, shared-record, publisher-only, and paid checks as gated rather than silently
skipped.

## Pack paths

- MCP: [`copilot/mcp.json.example`](./copilot/mcp.json.example) · [`copilot/.vscode/mcp.json.example`](./copilot/.vscode/mcp.json.example)
- Bootstrap: [`scripts/bootstrap-copilot-repo.ps1.txt`](./scripts/bootstrap-copilot-repo.ps1.txt)
- Examples: [`../../examples/mcp/`](../../examples/mcp/), [`../../examples/codegraph/`](../../examples/codegraph/), [`../../examples/serena/`](../../examples/serena/)
