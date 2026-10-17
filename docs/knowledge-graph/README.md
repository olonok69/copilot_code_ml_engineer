# `knowledge-graph/` — the ticket knowledge graph pipeline (Part 3)

The real, tested pipeline behind the `kg` / `kg-refresh` skills, copied from a production installation and
sanitised. Narrative: [`../KNOWLEDGE_GRAPH.md`](../KNOWLEDGE_GRAPH.md). Skills:
[`kg`](../ai-agents-code-methodology/copilot/skills/kg/SKILL.md) ·
[`kg-refresh`](../ai-agents-code-methodology/copilot/skills/kg-refresh/SKILL.md).

## What is here

| File | Role |
|---|---|
| [`kg_query.sh`](./kg_query.sh) | Deterministic query surface: `explain` / `path` (via graphify) + `find` (pure Python). No LLM. |
| [`kg_refresh.sh`](./kg_refresh.sh) | Deterministic bookends around the semantic step: `prepare` / `finalize` / `bootstrap` / `snapshot-memory` / `restore-memory` |
| [`build_manifest.py`](./build_manifest.py) · [`stage_corpus.py`](./stage_corpus.py) | Enumerate and stage the corpus with provenance-preserving flat names |
| `test_kg_*.py` | Offline tests for the bookends and the query surface |
| [`design.md`](./design.md) · [`plan.md`](./plan.md) · [`phase2-*`](./phase2-refresh-design.md) · [`_findings.md`](./_findings.md) · [`TRAVEL_SYNC.md`](./TRAVEL_SYNC.md) | Historical design/plan/findings — written for the original Claude Code installation; kept for the reasoning |
| [`output/`](./output/) · `graphify-out/` · [`manifest.txt`](./manifest.txt) | The **real** output and corpus manifest, in sanitised form (see below) |

## The real output, sanitised

The real graph (**507 nodes · 672 edges · 35 communities**, 92% `EXTRACTED` edges) was built from internal
ticket write-ups. It ships here in **sanitised** form — the same copy as the sibling Pi volume, with the same
pseudonym mapping: tickets `TKT-1xx` / `CHG-1xx`, clients and funds `ClientB`…`ClientV`, paths rewritten to a
generic workspace. [`output/graph.html`](./output/graph.html) is the interactive view;
[`output/GRAPH_REPORT.md`](./output/GRAPH_REPORT.md) the audit report;
[`../../presentation/kg_graph.png`](../../presentation/kg_graph.png) the screenshot used in the deck.

```bash
bash docs/knowledge-graph/kg_query.sh find letter        # discover node names
bash docs/knowledge-graph/kg_query.sh TKT-104            # neighbours (needs the graphify package)
bash docs/knowledge-graph/kg_query.sh TKT-104 TKT-101    # shortest path (needs graphify)
```

## How `kg` and `kg-refresh` run under GitHub Copilot

- **`kg`** — a direct port: the skill calls `kg_query.sh`; invoke `/kg <topic>` in the CLI or VS Code, or let
  the agent pick it from its description at the orient stage. Zero inference per query.
- **`kg-refresh`** — publisher machine only. `prepare` and `finalize` are plain scripts. The semantic
  extraction in the middle needs parallel subagents: use the Copilot CLI's `task` tool or `/fleet`, or keep
  that single step in Claude Code. Subagent concurrency is plan-based and the docs disagree on max depth
  (6 vs 4) — keep the fan-out one level deep. Never run it on the cloud agent (gitignored corpus, publisher
  baton in the shared store).

## Tests

```bash
cd docs/knowledge-graph && uv run -q --with pytest python -m pytest -q
```

Measured 2026-10-17 in this repo: **16 passed, 1 failed**. The failure is
`test_prepare_stages_corpus_into_scratch`, which needs the real ~90-file corpus under `data/changes/`
(asserts > 50 staged files) — not shipped here, so it cannot pass in the course repo. The `explain`/`path`
tests run only when the `graphify` package is importable (they skip otherwise).

One portability fix was made while porting: `kg_refresh.sh` aborted at start-up (exit 2, no message) on any
machine without a matching `~/.claude/projects/*/memory` folder, because a failing `ls` inside a command
substitution trips `set -euo pipefail`. It now falls back cleanly (`|| true`). Set `KG_MEMORY_DIR` to point
`snapshot-memory` / `restore-memory` at your canonical notes folder.
