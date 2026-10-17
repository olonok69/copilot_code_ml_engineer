# CodeGraph — local code intelligence (via MCP in GitHub Copilot)

A *local-first* tool that indexes your code with **tree-sitter** into a **SQLite graph** and exposes it to the
agent as an MCP server. The Claude Code volume installed it with `codegraph install --target=claude`; in Copilot
you register the server yourself — the shape depends on the surface (see [`../mcp/`](../mcp/)).

Repo: https://github.com/colbymchenry/codegraph · Docs: https://colbymchenry.github.io/codegraph/

## What it indexes (deterministic, from the AST — not summarised by an LLM)

- **Symbols:** functions, classes, methods, types, routes, components.
- **Edges:** calls, imports, inheritance, references, framework relations.
- **Files:** structure + full-text search.

Everything lives in `.codegraph/` (local SQLite). **No external services, no API keys.** Add `.codegraph/` to
`.gitignore`.

## CLI (same in every volume)

```bash
codegraph init        # create the .codegraph/ index and build it
codegraph sync        # incremental re-index
codegraph watch       # live re-index (unreliable on WSL /mnt)
codegraph explore "<symbol or question>"
codegraph serve --path <repo> --mcp
codegraph status
```

## Connecting it to Copilot

| Surface | Config |
|---|---|
| CLI + VS Code Copilot harness | `.mcp.json` / `~/.copilot/mcp-config.json`: `"codegraph": {"command": "codegraph", "args": ["serve", "--path", ".", "--mcp"], "tools": ["*"]}` — `tools` is **required** |
| VS Code Local harness | `.vscode/mcp.json` under `servers`, with `--path ${workspaceFolder}` |
| Cloud agent | Repo Settings → Copilot → MCP servers (`"tools": ["codegraph_explore"]`), and install the binary + build the index in `copilot-setup-steps.yml` |

⚠️ `${workspaceFolder}` is VS Code-only; `.mcp.json` expands env vars only. Whether `--path .` resolves against
the session cwd is UNVERIFIED — launch `copilot` from the repo root, or use an absolute path in the user config.
Workspace `.mcp.json` requires **folder trust**.

Checks: `/mcp` (CLI) lists the server; ask the agent to call `codegraph_explore`. Treat the source it prints as
**already read** — do not re-open that file.

The live repo root [`../../.mcp.json`](../../.mcp.json) wires it for this course.

## CodeGraph vs. Serena vs. text search

| Question | Tool |
|---|---|
| Survey: source + callers + blast radius + tested? | **CodeGraph** `codegraph_explore` |
| Precise check before a rename/delete | **Serena** `find_referencing_symbols` |
| Overview / body of a symbol | Serena, or the source `explore` already returned |
| Literal / string | text search |

In the methodology (stage 4): CodeGraph first, Serena before touching. See
[`../methodology/REAL_EXAMPLE.md`](../methodology/REAL_EXAMPLE.md).

## Blast radius

The ripple of touching a symbol: transitive callers + coverage flags. CodeGraph's blast is *flat* (it mixes
same-named symbols); the fine pre-rename verdict comes from Serena.
