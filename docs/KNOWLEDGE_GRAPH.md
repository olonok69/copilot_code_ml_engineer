# Ticket knowledge graph — "CodeGraph, but for tickets and lessons"

> A real (sanitised) pattern built on a live project. Just as **CodeGraph** indexes the *code*, this graph
> indexes the **project's memory** — per-ticket writeups, "sharp edges", runbooks and memory notes — into a
> **navigable graph** the agent queries *before* touching anything. It is queried with the **`kg`** skill
> and rebuilt with **`kg-refresh`**. In the real installation everything lives under `data/` (gitignored):
> the nodes carry internal names, so the graph **never leaves the repo**.
>
> This is the ticket-graph case study within Session 2 of the GitHub Copilot volume. Pipeline, scripts and tests:
> [`knowledge-graph/`](./knowledge-graph/) (start with its [`README.md`](./knowledge-graph/README.md)).
> The bundled `knowledge-graph/output/` is an older sanitised snapshot (507 nodes · 672 edges · 35
> communities). The deck screenshot [`../presentation/kg_graph.png`](../presentation/kg_graph.png) is a
> newer topology-only render from ILS_2 (3,921 nodes · 8,508 links · 178 communities · 73 hyperedges).
> Labels and metadata are omitted; the current source graph contains internal identifiers and must not be
> copied into this course repository.

It complements CodeGraph rather than replacing it: **CodeGraph = the *what/how* of the code** (symbols,
calls, blast radius); **this graph = the *why* and the *what broke before*** (which tickets touch an area,
which danger zone surrounds it, how one ticket connects to another).

---

## 1. The problem it solves

In a repo with hundreds of per-ticket writeups (`data/changes/tkt-*/`), a "new" bug almost always has
**prior context that constrains the fix**: an invariant you must not break, a ticket that already fixed
something similar, a documented regression. Finding it by hand = remembering it exists and grepping. The
graph **makes it explicit**: one query returns the related tickets + the danger-zone cluster.

Real example: for a "letter-end" fix, `kg get_letter_end` instantly returned the whole danger zone (the 5–6
tickets sharing that code) — exactly what you would otherwise have to *remember* in order not to regress.

## 2. The corpus (what goes into the graph)

A **reproducible, diffable manifest** (`manifest.txt`) lists exactly which files go in, instead of a glob
that changes silently. Membership rules:

| Group | Rule |
|---|---|
| Primary per ticket | `data/changes/tkt-*/tkt-*.md` |
| Per-ticket fallback | for folders without `tkt-NNNN.md`, the largest `.md` (deterministic) |
| Extractor state | `data/changes/extractors/*/process.md` |
| Hubs | `STATUS.md`, `SHARP_EDGES.md`, `FOLLOWUPS.md`, `PLAYBOOK.md`, … |
| Orientation | the always-loaded orientation file(s), `CODE_NAVIGATION.md` |
| Ops | the `machine-sync` runbooks + the shared `s3-sync` record |
| Memory | the agent's memory notes (`*.md`) |

Hard exclusions: binaries (`.png`/`.json`/`.docx`), stale copies from a travel tarball (`payload/`),
handovers that only repeat the ticket. **Density without new knowledge = noise.**

Under Copilot the orientation file is `AGENTS.md` (+ `.github/copilot-instructions.md`), and the "memory"
group is whatever canonical notes you keep under `data/` — Copilot Memory (cloud, preview, 28-day expiry)
is not a file you can feed into a manifest.

## 3. The build pipeline (`kg-refresh`)

A deterministic wrapper around one semantic-extraction pass done by subagents:

```
kg_refresh.sh prepare   # build_manifest -> stage _corpus/ -> copy to a scratch OUTSIDE the repo
graphify <scratch>      # detect -> extraction by parallel subagents -> clustering -> HTML/JSON
kg_refresh.sh finalize  # copy artifacts to output/ + sync the in-place copy + leak-check
```

- **The gotcha that holds it all together:** `graphify` honours `.gitignore`, and **all of `data/` is
  gitignored** → running the detector in place finds **0 files**. Fix: stage the corpus in a **scratch
  outside the repo** (`~/.cache/…`), run there, copy the 3 artifacts back to `data/knowledge-graph/output/`.
- **Full rebuild** every time; ~5 parallel subagents (that's why `kg-refresh` is a skill, not a script: the
  semantic step is an agent step).
- **Leak-check** in `finalize`: aborts if any graph artifact landed outside `data/`.

Output: `output/graph.json` (NetworkX node-link, **typed edges** with `relation` + `confidence`),
`output/graph.html` (interactive), `output/GRAPH_REPORT.md` (god-nodes, surprising connections, questions).

### Running the semantic step under GitHub Copilot

The graphify extraction was built as a Claude Code skill that fans out to parallel subagents. Under Copilot
there are two honest options:

1. **Copilot CLI subagents** — the `task` tool, or `/fleet` for parallel subagents over a plan. Concurrency
   is plan-based (Free 2 … Enterprise 32) and the docs disagree on the maximum nesting depth (**6** in the
   reference table, **4** in the env-var table — verify on your build). Keep the fan-out one level deep.
2. **Keep that one step in Claude Code** and run everything else (the deterministic bookends, `kg` queries,
   the publisher guard) from Copilot.

Either way the bookends (`prepare` / `finalize`) and the publisher-only guard are scripts, not prose, so they
behave identically. Do **not** run `kg-refresh` on the cloud agent: the corpus is gitignored and the
publisher baton lives in the shared store.

## 4. The query surface (`kg`) — deterministic, no LLM

The engine already exists in `graphify`: `explain` (neighbours) and `path` (shortest path) read `graph.json`
**directly, without an LLM** — that *is* the CodeGraph analogue. The `kg` skill is a thin wrapper
(`kg_query.sh`) that pins the interpreter + graph path and normalises the token:

```bash
kg <ticket-or-topic>   # neighbours of a node     (graphify explain)  <- the most common use
kg <A> <B>             # shortest path A<->B      (graphify path)
kg find <substr>       # discover a node's exact name
```

Tokens match fuzzily: `TKT-1234`, `tkt-1234`, `get_letter_end`, `"letter end"` all resolve. If a topic does
not resolve, `find <substr>` gives the exact id to retry with. Under Copilot, `/kg <topic>` (CLI or VS Code)
or the agent picks the skill from its description at the orient stage.

> **"No LLM" is not "free" — it is a smaller, amortised cost.** The expensive inference (subagent
> extraction) is paid **once** in `kg-refresh`; each `explain`/`path`/`find` query is then a deterministic
> algorithm reading `graph.json` → **zero inference**. The only per-query cost is the agent reading a small
> output (like a `grep`): smaller and targeted, not zero. Building the graph is an **investment** — no
> inference per query, **deterministic, reproducible** results, expensive reasoning replaced by a cheap
> lookup.

## 5. Hooked into the workflow (the real goal)

A graph nobody queries is worth nothing. The **history-first** rule in the always-loaded instructions
(`AGENTS.md` / `.github/instructions/00-methodology-core.instructions.md`) says: **before designing a fix near
a known area, run `kg <ticket-or-topic>`** — *before* grepping `data/changes/`. One deterministic call puts
the reading list in front of you (related tickets + danger zone); then you read the ticket writeup and the
sharp-edges entry before writing. The graph points at *what to read*; it does not replace reading it.

Honesty about what it adds: the gain is **recall in dense zones** (letter-end, title cleanup, subsection
numbering) — there it saves a grep and catches the one relevant ticket you would have missed. In an
isolated area it adds little. `EXTRACTED` edges = reliable; `INFERRED` / `semantically_similar_to` = leads to
verify, not facts.

## 6. Travel between machines (main ⇄ laptop)

The graph is an **almost** derived artifact → **the built graph does not travel back**: whichever machine has
the current corpus rebuilds it. ⚠️ **With one exception that is NOT negotiable:** `community_labels.json`
(the hand-written community names) **is not a pure function of the corpus** — nothing regenerates it, and on a
real rebuild **under 1%** survived. If it was edited on the other machine, **it must travel back**, paired
with the graph it was written against. "Derived" is a property of the file, not of the folder. Two
subcommands close the loop (memory does not travel in the delta by default):

```bash
# Bare metal (new laptop): install tooling + pin the interpreter + verify kg
bash data/knowledge-graph/kg_refresh.sh bootstrap
# Before going back: memory is not in the delta -> park it under data/ so it travels
bash data/knowledge-graph/kg_refresh.sh snapshot-memory
# On the main machine, after landing the delta: merge memory back (with backup) and rebuild
bash data/knowledge-graph/kg_refresh.sh restore-memory  &&  kg-refresh
```

Full travel-kit detail: [`../examples/methodology/machine-sync.md`](../examples/methodology/machine-sync.md).
Copilot note: personal skills and instructions live in `~/.copilot/` (not `~/.claude/`), so that is the
folder a machine bring-up must carry.

## 7. Confidentiality

The nodes carry internal names → **internal only**; the whole tree lives under `data/` (gitignored) and is
**never committed**. A sanitised version (name → role) for sharing outside is a separate deliverable with
its own anonymisation pass — which is exactly the pass this course volume's copy went through.

---

## Map of the pieces

| Piece | What it is |
|---|---|
| `kg` (skill) | query: `explain` / `path` / `find` — deterministic |
| `kg-refresh` (skill) | rebuilds the graph (prepare → `graphify` → finalize) |
| `kg_query.sh` | wrapper over `graphify explain`/`path` + `find` in Python |
| `kg_refresh.sh` | deterministic bookends + `snapshot-memory` / `restore-memory` / `bootstrap` |
| `build_manifest.py` / `stage_corpus.py` | enumerate and stage the corpus |
| `data/knowledge-graph/output/` | `graph.json` + `graph.html` + `GRAPH_REPORT.md` |

> In one sentence: **the graph is the map; the agent's job after the pipeline is to be the guide.**
> Rebuildable, queryable in one call, hooked into the "history first" rule.
