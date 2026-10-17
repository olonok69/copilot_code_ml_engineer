---
name: kg-refresh
argument-hint: '[request "why"]'
description: >-
  Rebuild or refresh the ticket knowledge graph (graphify corpus) after new
  writeups land. Use when closing a ticket loop, after adding STATUS/PLAYBOOK
  lessons, or when the user asks to refresh /kg. Publisher machine only for
  rebuild; contributors file a refresh request instead.
---

# kg-refresh — rebuild ticket knowledge graph

## Role gate (read first)

1. Read machine-local `IDENTITY.md` (via `AGENTS.md`).
2. If role is **contributor** (or baton is not held here):
   - Do **not** rebuild or publish `knowledge-graph/`.
   - File a request instead, then push:

```bash
bash data/knowledge-graph/kg_refresh.sh request "why a refresh is due"
# from s3-sync: ./data-push.sh --go
# Expect SKIPPED knowledge-graph/ except refresh_queue/ — that is success.
```

3. If role is **publisher** and you hold the baton: continue below.

## When to use (publisher)

- Stage **11 Persist** after durable docs changed.
- User asks to refresh the ticket graph / `/kg-refresh` **on the publisher**.
- Budget re-labelling: only ~37–48% of ~102 hand-authored community names survive a
  rebuild even with stable ids — refresh is a naming cost, not free.

## Procedure (publisher)

1. `publisher.sh status` — confirm this machine holds the baton.
2. `kg_refresh.sh queue` — read pending contributor requests.
3. Locate project scripts (commonly `data/knowledge-graph/kg_refresh.sh`).
4. Follow the project’s documented pipeline. Typical shape:

```text
kg_refresh.sh prepare   # stage corpus outside gitignored paths if required
# run graphify extract on the staged corpus (may need an agent step)
kg_refresh.sh finalize  # copy artifacts + leak-check
```

5. Health-check labels (`kg_labels.py check`) — fingerprint pair must match.
6. `kg_refresh.sh queue --clear` then **push** — `--clear` must **delete consumed
   keys in the bucket**, not only archive locally (otherwise the next pull resurrects
   the queue everywhere).
7. Smoke-test with the `kg` skill on a known ticket id.
8. Report what changed and any naming work still owed.

## Gotchas

- Some graphify setups respect `.gitignore` and see **0 files** inside gitignored
  `data/` — use the project scratch/staging flow.
- `refresh_queue/` lives under `knowledge-graph/` but is the contributor mailbox;
  baton gating must **exempt** it on contributor push.
- Never run contributor `--delete` to clear the queue.

## If graphify is not installed / not publisher

Do not fail the methodology. Ensure instead:

1. `data/changes/STATUS.md` updated.
2. Per-ticket writeup complete.
3. `SHARP_EDGES.md` / `PLAYBOOK.md` updated if a reusable lesson exists.
4. Contributor: refresh **request** filed + pushed if a rebuild is warranted.

Tell the user the graph rebuild was skipped and the STATUS fallback remains authoritative.

---

## Invocation per surface (GitHub Copilot)

CLI on the **publisher** machine. Not for the cloud agent (the corpus is gitignored and the publisher baton lives in the shared store).

- **Copilot CLI:** type `/kg-refresh` or let the agent pick it from the `description`. Manage with `/skills` or `copilot skill list|add|remove`.
- **VS Code (Copilot or Local harness):** `/kg-refresh` in chat; manage in **Chat: Open Customizations**.
- **Copilot cloud agent / code review:** automatic selection only (by `description`).
- ⚠️ The Copilot CLI does **not** read `~/.claude/skills/` (VS Code does). A personal copy goes in `~/.copilot/skills/kg-refresh/` (or `~/.agents/skills/`), or register the folder with `copilot skill add <dir>` / `COPILOT_SKILLS_DIRS`. Project copy: `.github/skills/kg-refresh/SKILL.md`.
- Frontmatter is Copilot-valid: `name` equals the folder name (lowercase-hyphen — VS Code silently drops a mismatch), `description` ≤ 1024 characters, no `trigger:` key.

The semantic-extraction step (graphify) needs parallel subagents. Under Copilot use CLI subagents — the `task` tool or `/fleet` — or keep running that one step from Claude Code. Subagent depth/concurrency limits differ by plan and the docs disagree on max depth (6 vs 4): keep the fan-out shallow. The publisher-only guard lives in `kg_refresh.sh` and `publisher.sh`, not in this prose.
