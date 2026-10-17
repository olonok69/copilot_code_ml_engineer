# MCP — Model Context Protocol (GitHub Copilot)

**MCP** connects Copilot to external tools and data (CodeGraph, Serena, Context7, your own tooling…).
Copilot has **four different config shapes** depending on the surface — the most common porting mistake.
Facts: findings §7 ([`../../docs/research/COPILOT_FINDINGS_2026-10-17.md`](../../docs/research/COPILOT_FINDINGS_2026-10-17.md)).

## Where config lives

| Surface | File / place | Top key | Notes |
|---|---|---|---|
| CLI — user | `~/.copilot/mcp-config.json` | `mcpServers` | `copilot mcp add NAME -- cmd args` · `copilot mcp add --transport http NAME URL` |
| CLI — workspace | `.mcp.json` (any dir cwd→git root) and `.github/mcp.json` | `mcpServers` | **Requires folder trust.** Priority: `--additional-mcp-config` > plugins > workspace > user |
| CLI — per session | `--additional-mcp-config='{json}'` or `@file` | | |
| VS Code — Copilot harness | reads `.mcp.json` + `~/.copilot/mcp-config.json`; forwards eligible `.vscode/mcp.json` servers **except those using `${input:...}`** | `mcpServers` | |
| VS Code — Local harness | `.vscode/mcp.json` or user-profile `mcp.json` | **`servers`** (+ `inputs[]`, `sandbox{}`) | `${workspaceFolder}`, `${input:id}`, `envFile` |
| JetBrains | `mcp.json` opened from Copilot Chat → tools icon → "Add MCP Tools" | `servers` | on-disk path NOT DOCUMENTED |
| Cloud agent + code review | Repo **Settings → Copilot → MCP servers** (JSON pasted in the UI, not a file); also `mcp-servers:` in a custom agent | `mcpServers` | see below |

Files here:

| File | For |
|---|---|
| [`mcp.json.example`](./mcp.json.example) | `.mcp.json` / `~/.copilot/mcp-config.json` (CLI + VS Code Copilot harness) |
| [`.vscode/mcp.json.example`](./.vscode/mcp.json.example) | VS Code Local harness (`servers`, `${workspaceFolder}`) |
| [`cloud-agent-mcp.json.example`](./cloud-agent-mcp.json.example) | Paste into repo Settings → Copilot → MCP servers (cloud agent) |

The live repo root [`../../.mcp.json`](../../.mcp.json) wires context7 + codegraph for this course.

## CLI server fields

- **Local (stdio):** `command`, `args`, **`tools` (required**, e.g. `["*"]`), `env` (`$VAR`, `${VAR}`,
  `${VAR:-default}`), `cwd`, `timeout` (ms, default 30000), `type: local|stdio`, `deferTools`, `disableToolCache`.
- **Remote:** `type: http|sse`, `url`, `tools`, `headers`, `oauthClientId`, `oauthScopes`,
  `oauthGrantType: client_credentials`, `oidc`.
- The model sees tools as `serverName-toolName` (sanitised, max 64 chars).
- ⚠️ `${workspaceFolder}` is VS Code-only. `.mcp.json` expands env vars only. Whether `--path .` resolves
  against the session cwd is UNVERIFIED — launch `copilot` from the repo root, or use an absolute path in
  `~/.copilot/mcp-config.json`.

## Built-in CLI servers — don't configure them twice

`github-mcp-server` (read-heavy default subset; widen with `--add-github-mcp-toolset`,
`--add-github-mcp-tool`, `--enable-all-github-mcp-tools`), **`playwright`**, `fetch`, `time`. Disable with
`--disable-builtin-mcps` or `--disable-mcp-server NAME`. ⚠️ **Playwright is already built in** — that is why
it is absent from `mcp.json.example` and present only in the VS Code Local file.

## Cloud agent

- Default servers: GitHub (read-only, repo-scoped token) and Playwright (localhost only).
- Only **tools** are used — no resources, no prompts, **no OAuth remote servers**.
- Secrets must be **Agents** secrets/variables prefixed **`COPILOT_MCP_`**, referenced as `$COPILOT_MCP_X`
  or `${COPILOT_MCP_X}` (agent YAML also accepts `${{ secrets.X }}`).
- Copilot calls the configured tools **autonomously, without approval** → allowlist **read-only** tools
  (the example lists tool names instead of `"*"`).
- Binaries (`codegraph`, `uvx`) are installed by `.github/workflows/copilot-setup-steps.yml` — a single job
  named `copilot-setup-steps`, on the default branch. Template:
  [`../../docs/ai-agents-code-methodology/copilot/copilot-setup-steps.yml.example`](../../docs/ai-agents-code-methodology/copilot/copilot-setup-steps.yml.example).
- Remote hosts (e.g. `mcp.context7.com`) need a firewall allowlist entry (repo "Internet access" settings).

## Code review

Copilot code review uses an MCP tool **only if it has `annotations.readOnlyHint: true`**, and only when
"Allow Copilot to use MCP tools when reviewing pull requests" is on.

## Migrating a VS Code config to the CLI

```bash
jq '{mcpServers: .servers}' .vscode/mcp.json > .mcp.json   # then add "tools": ["*"] per server
```

## Good practice

- **Secrets via env**, never hardcoded in versioned JSON.
- **Permissions:** MCP tools are allowed/denied in the CLI with `--allow-tool='serena(find_symbol)'` /
  `--deny-tool='MyMCP'` (see [`../permissions/`](../permissions/)); a repo cannot commit an allowlist.
- **Few servers** — every server adds tool schemas to context ([`../context/`](../context/)).
- **Org policy:** an enterprise MCP allowlist (fingerprints of command+args+URL, fail-closed) can block
  servers you configure.
- Config gives *capability*; instructions give *judgement* ("CodeGraph BEFORE reading whole files").

Daily servers (methodology): `codegraph` ([`../codegraph/`](../codegraph/)) · `serena` ([`../serena/`](../serena/)) · `context7` · Playwright (built in).
Ready-to-copy pack: [`../../docs/ai-agents-code-methodology/copilot/mcp.json.example`](../../docs/ai-agents-code-methodology/copilot/mcp.json.example).
