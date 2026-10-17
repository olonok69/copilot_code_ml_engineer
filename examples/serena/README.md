# Serena — semantic code navigation (MCP in GitHub Copilot)

[Serena](https://github.com/oraios/serena) gives the agent symbolic understanding via LSP. Same tool as in
Claude Code and Cursor; only **how the server is registered** changes.

## Registering it

CLI / VS Code Copilot harness (`.mcp.json` or `~/.copilot/mcp-config.json`):

```json
"serena": {
  "command": "uvx",
  "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server"],
  "tools": ["*"]
}
```

VS Code Local harness: the same server under `servers` in `.vscode/mcp.json`
([`../mcp/.vscode/mcp.json.example`](../mcp/.vscode/mcp.json.example)). CLI one-liner:
`copilot mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server`.
Cloud agent: repo MCP settings with a read-only `tools` allowlist + `uvx` installed in `copilot-setup-steps.yml`
([`../mcp/cloud-agent-mcp.json.example`](../mcp/cloud-agent-mcp.json.example)).

## Tools that matter

| Tool | What it does | When |
|---|---|---|
| `find_symbol` | Locate a symbol (`body=true` → its body) | One method in a 5k-line file |
| `get_symbols_overview` | File skeleton | First look |
| `find_referencing_symbols` | References disambiguated by class | **Mandatory before renaming/deleting** |
| `search_for_pattern` | Pattern with symbolic context | Literal + containing symbol |
| `activate_project` | Switch indexed project | Multi-repo |

The model sees them as `serena-find_symbol` etc. (`serverName-toolName`).

## Prevalence (same as in Claude Code)

1. CodeGraph `codegraph_explore` first.
2. Serena `find_referencing_symbols` before rename/delete.
3. Text search only for literals.

Scout agent: [`../subagents/.github/agents/refactor-scout.agent.md`](../subagents/.github/agents/refactor-scout.agent.md)
(add `"serena/find_referencing_symbols"` to its `tools` to let it call Serena).

## Permissions

Claude Code used a `mcp__serena__…` allowlist; Copilot CLI uses `--allow-tool='serena(find_symbol)'` /
`--allow-tool='serena'` per session (deny beats allow), and the methodology instructions say *when* to reach for
it. There is no repo-committable allowlist — see [`../permissions/`](../permissions/).
