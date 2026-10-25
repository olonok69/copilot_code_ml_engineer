# GitHub Copilot — A course in three parts (deck + guides)

> **The GitHub Copilot volume** of a course series — same course, same method, different tool:
> [Claude Code](https://github.com/olonok69/claude_code_ml_engineer) ·
> [Cursor](https://github.com/olonok69/cursor_code_ml_engineer) ·
> **GitHub Copilot (this repo)** ·
> [Pi](../pi_code_ml_engineer).

Material for a **course/workshop** on **GitHub Copilot** as an *agent* (not autocomplete): one
presentation (`.pptx`) in **three parts**, two written guides, a live-demo runbook, and runnable examples.
Aimed at **developers**. English only. Every Copilot claim was checked against docs.github.com and
code.visualstudio.com on **17 October 2026**; where the docs are silent or contradict themselves, the
material says so.

- **Part 1 — GitHub Copilot.** Opens with a **surfaces map**: Copilot CLI (`copilot`, not the retired
  `gh copilot`), VS Code with its two harnesses (Copilot harness = the CLI's runtime; Local harness = classic
  agent mode, with prompt files, handoffs and a different hook schema), JetBrains, the **Copilot cloud agent**
  (formerly "coding agent") and Copilot code review — plus a feature × surface matrix. Then: install, auth,
  headless `copilot -p`, models, billing in **GitHub AI Credits** (premium requests ended 2026-06-01) ·
  memory and instructions (`AGENTS.md`, `.github/copilot-instructions.md`, `.instructions.md` `applyTo`) ·
  permissions, trust and sandbox · sessions · context window · prompt caching (honest: no user control) · MCP
  · skills and plugins · custom agents and subagents · hooks · automation.
- **Part 2 — The methodology (tool-agnostic):** the 11-stage workflow with gates · tool prevalence
  (CodeGraph, Serena, GSD and its substitutes) · the transfer — **from Claude Code to Copilot**, with a
  rewritten adaptation guide and a ready-to-copy `.github/` surface · machine sync and the shared engineering
  record over S3. The outbound gate is **five checks** (validate the instrument · contract via *wrapper* ·
  member list, not totals · deployed image · look at the output). "The human owns merge" is now
  **enforceable** (a committed `preToolUse` hook + cloud-agent limits) — and two new holes are named
  (`/pr automerge`, code-review approvals).
- **Part 3 — The ticket knowledge graph (graphify):** corpus with manifest, `kg-refresh` pipeline, zero-LLM
  `kg` query, and how both run under Copilot (CLI subagents / `/fleet`).

## Naming in this volume

The earlier volumes use Spanish file names with `_EN` English twins. This volume is **English only**, so
the files carry plain English names:

| This volume | Cursor / Claude Code volume |
|---|---|
| [`TECHNICAL_GUIDE.md`](./TECHNICAL_GUIDE.md) | `GUIA_TECNICA_EN.md` |
| [`SPEAKER_GUIDE.md`](./SPEAKER_GUIDE.md) | `GUIA_PRESENTACION_EN.md` |
| [`DEMO_RUNBOOK.md`](./DEMO_RUNBOOK.md) | `DEMO_RUNBOOK_EN.md` |
| [`examples/`](./examples/) | `ejemplos/` |
| [`presentation/`](./presentation/) | `presentacion/` |

Section numbering (§00–§16) matches across the guides, the deck and the sibling volumes; §00 (surfaces map)
is new in this volume.

## Contents

| File | What it is |
|---|---|
| [`SPEAKER_GUIDE.md`](./SPEAKER_GUIDE.md) | Speaker guide: narrative per slide + closing one-liners 🗣️ + links to the code. |
| [`TECHNICAL_GUIDE.md`](./TECHNICAL_GUIDE.md) | Copy-paste implementation reference, with the **Claude Code → Cursor → Copilot** equivalence table. |
| [`DEMO_RUNBOOK.md`](./DEMO_RUNBOOK.md) | Live-demo cheatsheet: preflight, command per slide, timings, common failures. |
| [`presentation/Copilot_Presentation.pptx`](./presentation/) | The deck (16:9), same visual system as the sibling decks. |
| [`presentation/build_pptx_copilot.py`](./presentation/build_pptx_copilot.py) | Deck generator (regenerable). |
| [`examples/`](./examples/) | Runnable artifacts by course section. |
| [`docs/`](./docs/) | Methodology pack (with the Copilot surface), knowledge-graph pipeline, sync runbooks, and the research notes behind Part 1. |
| [`AGENTS.md`](./AGENTS.md) · [`.github/`](./.github/) · [`.mcp.json`](./.mcp.json) | The live Copilot surface of this repo — open it with the CLI or VS Code and try it. |

## The live surface (this repo)

| Piece | Path | Try it |
|---|---|---|
| Always-on instructions | [`AGENTS.md`](./AGENTS.md), [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) | `copilot` → `/instructions` |
| Skills | [`.github/skills/`](./.github/skills/) `audit`, `audit-python`, `deploy-staging` | `/audit` on [`ex_npm/`](./ex_npm/) · `/audit-python` on [`ex_app/`](./ex_app/) · `/deploy-staging` on [`ex_staging/`](./ex_staging/) |
| Read-only agent | [`.github/agents/refactor-scout.agent.md`](./.github/agents/refactor-scout.agent.md) | `copilot --agent refactor-scout` |
| Git-block hook | [`.github/hooks/block-external-git.json`](./.github/hooks/block-external-git.json) | ask the agent to `git push` → denied · `bash .github/hooks/test-block-external-git.sh` |
| MCP | [`.mcp.json`](./.mcp.json) | `copilot mcp list` (requires folder trust) |

## Examples (by course section)

**Part 1:** [`examples/agents-md/`](./examples/agents-md/) (§02) ·
[`examples/context/`](./examples/context/) (§05) ·
[`examples/prompt-caching/`](./examples/prompt-caching/) (§06) ·
[`examples/mcp/`](./examples/mcp/) (§07) ·
[`examples/skills-plugins/`](./examples/skills-plugins/) (§08 — incl. `day`, `atlassian`, `evidence`, `preview`; tools in
[`examples/methodology/tools/`](./examples/methodology/tools/)) ·
[`examples/subagents/`](./examples/subagents/) (§09) ·
[`examples/hooks/`](./examples/hooks/) (§10) ·
[`examples/permissions/`](./examples/permissions/) (§03) ·
[`examples/automation/`](./examples/automation/) (§11 — Actions workflow with `copilot -p`, cloud-agent tasks API, SDK).

**Part 2:** [`examples/methodology/`](./examples/methodology/) (workflow, real example, tool prevalence,
machine sync, S3 scripts) · [`examples/codegraph/`](./examples/codegraph/) ·
[`examples/serena/`](./examples/serena/) · [`examples/gsd/`](./examples/gsd/) ·
[`docs/ai-agents-code-methodology/`](./docs/ai-agents-code-methodology/) — the portable starter kit:
[`COPILOT_ADAPTATION.md`](./docs/ai-agents-code-methodology/COPILOT_ADAPTATION.md) + the ready-to-copy surface
[`copilot/`](./docs/ai-agents-code-methodology/copilot/) · [`docs/synchro/`](./docs/synchro/).

**Part 3:** [`docs/knowledge-graph/`](./docs/knowledge-graph/) · [`docs/KNOWLEDGE_GRAPH.md`](./docs/KNOWLEDGE_GRAPH.md) ·
[`presentation/kg_graph.png`](./presentation/kg_graph.png) (sanitised capture of the real graph).

## Regenerating the deck and diagrams

```bash
uv run --with python-pptx --with pillow python presentation/build_pptx_copilot.py   # -> presentation/Copilot_Presentation.pptx
python examples/methodology/render_flow.py      # -> flow.png (11-stage workflow)
python examples/subagents/render_agents.py      # -> agents.png (subagent vs /fleet vs cloud agent)
```

## Tests you can run offline

```bash
bash .github/hooks/test-block-external-git.sh                         # the git-block hook (bash; PS=1 adds PowerShell)
cd examples/methodology/tools && uv run -q --with pytest --with boto3 python -m pytest -q
cd docs/knowledge-graph && uv run -q --with pytest python -m pytest -q
```

## Technology documentation

| Technology | Role | Documentation |
|---|---|---|
| **GitHub Copilot** | The tool (Part 1) | <https://docs.github.com/en/copilot> · CLI reference <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference> · hooks <https://docs.github.com/en/copilot/reference/hooks-reference> |
| **VS Code agents** | Copilot / Local harnesses | <https://code.visualstudio.com/docs/agents/concepts/agent-harnesses> |
| **MCP** | Connection standard (§07) | <https://modelcontextprotocol.io> |
| **CodeGraph** | Code graph (§13) | <https://colbymchenry.github.io/codegraph/> |
| **Serena** | LSP navigation (§13) | <https://github.com/oraios/serena> |
| **GSD** | Productised method — Claude Code only (§13) | <https://github.com/tomascortereal/claude-code-setup> |
| **Spec Kit** | Spec-driven templates (third-party coverage only) | <https://github.com/github/spec-kit> |
| **graphify** | Ticket knowledge graph (Part 3) | <https://graphify.net> |
| **Context7** | Up-to-date library docs | <https://context7.com> |

## Sources

Official docs <https://docs.github.com/en/copilot> and <https://code.visualstudio.com/docs> —
**verified 2026-10-17. Copilot moves fast; re-check before reuse.** Per-claim citations:
[`docs/research/COPILOT_FINDINGS_2026-10-17.md`](./docs/research/COPILOT_FINDINGS_2026-10-17.md); URL list in
[`TECHNICAL_GUIDE.md` § Sources](./TECHNICAL_GUIDE.md#sources).

> Examples derived from a real professional project are **sanitised** (no client names, ticket IDs, account
> IDs, people or secrets). The knowledge-graph material, sync runbooks, methodology examples and graph
> screenshot are taken from the already-sanitised Pi volume, with the same pseudonym mapping (tickets
> `TKT-1xx` / `CHG-1xx`, clients `ClientB`…`ClientV`), so the volumes stay consistent with each other. The
> Cursor volume's `confluence_pack/` (Confluence publishing pages) is **deliberately not included** here.
