# Prompt caching — the honest answer for GitHub Copilot

Every turn resends context to the model. **Prompt caching** lets a stable prefix be processed once and
re-read cheaply. The runnable demo [`cache_demo.py`](./cache_demo.py) talks to the **Anthropic API**, not
to Copilot — it teaches the mechanism. Facts: findings §6
([`../../docs/research/COPILOT_FINDINGS_2026-10-17.md`](../../docs/research/COPILOT_FINDINGS_2026-10-17.md)).

## 1. What Copilot gives you: no control

- **No user-facing caching control** in the CLI, VS Code or the cloud agent: no `cache_control`, no TTL
  setting, no env var. NOT DOCUMENTED anywhere. Programmatic (SDK) caching controls: NOT DOCUMENTED.
- **Caching does happen, and you pay for it.** Since 2026-06-01 billing is in GitHub AI Credits, priced per
  token for input, output, **cached input** and **cache write** (per-model tables). Anthropic models and
  the GPT-5.6+/GPT-6 families list cache-write costs.
- **VS Code: diagnosis, not control — the Cache Explorer** (Agent Debug Logs → Summary → Cache Explorer):
  per-turn cache hit %, reused tokens, and the **"first divergence"** in the prompt signature
  (system / tools / messages).
- **CLI: no cache view.** `/usage` shows per-model tokens and credits. OpenTelemetry export exists; whether
  it carries cache-token attributes is UNVERIFIED.

## 2. What you CAN do — keep the prefix stable

The VS Code docs' own advice (applies to every surface):

1. Choose model, effort, context size and tools **before** the first request.
2. **Don't edit instruction or agent files mid-session** (`AGENTS.md`, `.instructions.md`, `.agent.md`).
3. Attach only relevant context.
4. Use **subagents** for side research.
5. `/compact` or start a new session **deliberately**, not randomly.
6. **Forking preserves the prompt cache** (`/fork`).

**Portable moral:** a lean, stable tier 1 ([`../agents-md/`](../agents-md/)) = fewer fixed tokens, better
behaviour, and a cache-friendly prefix — the same rule as `CLAUDE.md` in Claude Code.

## 3. The mechanism (Anthropic API) — what the demo shows

The API caches a **contiguous prefix** up to a *cache breakpoint* (`cache_control`), with a TTL.

| | Cache write | Cache read |
|---|---|---|
| 5 min TTL (default) | 1.25× input | **0.1×** input |
| 1 h TTL | 2× input | **0.1×** input |

Hierarchy: `[Tools] → [System] → [Messages]`; a change invalidates that level and every later one.
Two identical calls: the second must show `cache_read_input_tokens > 0`.

| | Claude Code | Cursor | Copilot |
|---|---|---|---|
| Exposes `cache_control`? | No | No | No |
| What you control | size/stability of `CLAUDE.md` + MCP tools | rules + `AGENTS.md` + MCP tools | instructions + agents + MCP tools; model/effort/tools fixed up front |
| Diagnose | — | — | VS Code **Cache Explorer** |

API docs: [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching).

## Running the demo

```bash
pip install anthropic python-dotenv   # dotenv optional
# ANTHROPIC_API_KEY in the environment or in .env
python cache_demo.py                  # CACHE_DEMO_MODEL=<model id> to override the model
```

Expected: call 1 writes the cache (`cache_creation > 0`); call 2 reads it (`cache_read > 0`).
