# Context window — the resource that governs everything (GitHub Copilot)

The context window is still **the most important resource**: instructions, MCP, subagents and skills
exist so you do not waste it. Parallel to the **Context** section of the Claude Code and Cursor volumes.
Facts verified 2026-10-17 ([`../../docs/research/COPILOT_FINDINGS_2026-10-17.md`](../../docs/research/COPILOT_FINDINGS_2026-10-17.md) §5).

## 1. Anatomy: what fills the context

Run `/context` in the Copilot CLI. It breaks usage down into: **System Prompt · Custom Instructions ·
System Tools · MCP Tools · Messages · Free Space · Buffer**. In VS Code the context-window control in the
chat input shows the token count, a breakdown and AI credits.

| Block | You control it? |
|---|---|
| System prompt | No — hidden, always first |
| Custom instructions (`AGENTS.md`, `copilot-instructions.md`, `.instructions.md`, `CLAUDE.md`…) | **Yes** — hence the two-tier pattern ([`../agents-md/`](../agents-md/)) |
| System tools + MCP tools | **Yes** — fewer servers, `disabledMcpServers`, deferred tool loading (`toolSearch`, per-server `deferTools`) |
| Messages (turns, file reads, tool output) | Partly — targeted reads, subagents for noise |

## 2. Controls

### Copilot CLI

```text
/context              # token usage by block
/compact [focus]      # compact now, optionally steering what to keep (Esc cancels; cannot be undone)
/session checkpoints  # a summary checkpoint is created at every compaction (not a file snapshot)
/rewind               # roll back conversation only, or conversation + files
/new, /fork           # fresh session / branch the session
```

- **Auto-compaction** starts in the background at about **80%** and pauses at about **95%**.
- Tool output **larger than 20 KiB is saved to a temp file**; the model gets the path and a preview.
  Override with `COPILOT_LARGE_OUTPUT_THRESHOLD_BYTES`.
- MCP server *instructions*: only allowlisted servers' load up front (`--allow-all-mcp-server-instructions` loads all).
- **Subagents** run in separate context windows; custom agents spawned as subagents get **no** repo
  instructions unless `include-custom-instructions: true`.
- Context size is model-dependent; a 1M-token tier exists in VS Code and CLI on supported models (costs
  more credits). An exact default window per model is NOT DOCUMENTED in one table.

### VS Code

- Context-window control in the chat input (breakdown + credits); `/compact [focus]`; auto-compaction can
  be disabled with `github.copilot.chat.summarizeAgentConversationHistory.enabled`.
- References: `#codebase` runs a **search** (it does not dump the codebase), `#file:`, `#fetch`, `#tool:<name>`.

## 3. Lean-context levers (both surfaces)

1. **Small, stable instructions** — if you can delete a line without the agent getting things wrong, delete it.
2. **Pointers, not copies** — detail in `data/changes/` on demand ([`AGENTS.pointers-example.md`](./AGENTS.pointers-example.md)).
3. **Rarely-needed procedures → skills** (loaded on demand by `description`), not always-on instructions.
4. **MCP in moderation** — fewer servers = fewer tool schemas ([`../mcp/`](../mcp/)).
5. **Subagents for noisy research** — only the summary returns ([`../subagents/`](../subagents/)). In VS Code,
   skills can also run with `context: fork` (feature-flagged).
6. **Targeted reads** — CodeGraph first ([`../codegraph/`](../codegraph/)): one call with signal beats ten whole files.
7. **New session between unrelated tasks** — and compact deliberately, not at random.

**Link to Part 2:** the CodeGraph → Serena → text-search prevalence is a context-management policy.
