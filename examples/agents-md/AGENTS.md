# AGENTS.md — project orientation (GitHub Copilot)

> **Golden rule of this file:** it is loaded as session orientation by the Copilot CLI, VS Code, the cloud
> agent and code review. Keep it small. Only orientation + one-line pointers go here; the detail lives in
> files under `data/changes/` that are read **on demand**.
> Mandatory gates also live in `.github/instructions/*.instructions.md` (scoped with `applyTo`).

## What this project is

A document-extraction service (serverless function, Python 3.12). It turns PDFs into structured data and
validates them against a schema.

## Structure (repos in the workspace)

| Repo | Role | Permission |
|---|---|---|
| `sample-service` | **Owned** — where we work. | Edit / commit (push only if the human asks). |
| `frontend`, `backend`, `infra` | **Read-only context.** | Read freely. **Do not** edit unless explicitly asked; if a fix is needed there, propose it. |

> Do not commit/stage from the workspace root: always operate inside a specific repo.

## Commands

```bash
.venv/bin/pytest tests/ -q          # tests
.venv/bin/python -m parser <pdf>    # run the parser on one file
```

## Code navigation

Mandatory order (also in `.github/instructions/01-tool-prevalence.instructions.md`):

1. **CodeGraph** `codegraph_explore` first (survey + blast radius).
2. **Serena** `find_referencing_symbols` **always** before renaming/deleting.
3. Text search / file reads only for literals.

## Conventions

- Branches: `feat/tck-NNNN` (feature) · `fix/tck-NNNN` (bugfix).
- **Confidentiality:** never client names, ticket IDs or secrets in code/commits.
- **No agent self-attribution** in delivered artifacts.
- **Plan → agree → implement**; external actions = the human (unless explicitly asked).

## On-demand memory — pointers (do NOT copy the detail here)

- Live status per ticket → `data/changes/STATUS.md`
- Debugging lessons → `data/changes/PLAYBOOK.md`
- Invariants / locked decisions → `data/changes/SHARP_EDGES.md`
- Sanitisation policy → `data/changes/CONVENTIONS.md`
- Handover template → `data/changes/_HANDOVER_TEMPLATE.md`
- Copilot methodology pack → `data/changes/ai-agent-methodology/COPILOT_ADAPTATION.md`

<!-- Do NOT add a per-ticket ledger here: this file is always loaded; keep it small.
     Each record is written ONCE in its canonical ledger; only the pointer lives here. -->
