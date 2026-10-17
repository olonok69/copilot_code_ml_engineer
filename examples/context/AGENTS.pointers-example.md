# AGENTS.md — pointers (lazy) vs eager loading

> Example fragment of a tier-1 `AGENTS.md`. Compare it with the full pattern in
> [`../agents-md/AGENTS.md`](../agents-md/AGENTS.md).
>
> ⚠️ The Copilot **CLI** supports `@path` imports in `AGENTS.md` / `CLAUDE.md` /
> `.github/copilot-instructions.md` — they are **EAGER** (pulled in at start, recursively). VS Code docs
> recommend Markdown links instead; `@path` expansion there is NOT DOCUMENTED. So the portable pattern is:
> - **Pointer** (`data/changes/STATUS.md`…) = **LAZY**: the agent reads it when needed.
> - **Anti-pattern:** pasting STATUS/SHARP_EDGES/PLAYBOOK into AGENTS.md, or `@`-importing them → you pay
>   for it on **every** turn.

## Project

Billing API. Monorepo: `api/` (FastAPI) + `web/` (React).
Repo overview: read `README.md` when you need it (do not embed it here).
npm scripts: read `package.json` on demand.

## Commands

- Tests: `.venv/bin/pytest tests/ -q` (never bare `pytest`: use the venv)
- Lint: `npm run lint --workspace=web`

## Rules

- Before renaming/deleting a shared symbol: `codegraph_explore` + Serena
  `find_referencing_symbols` (the why lives in `data/changes/CONVENTIONS.md`).
- Live status per ticket: `data/changes/STATUS.md` (read when orienting, do not copy here).
- Always-on gates: `.github/instructions/` (methodology).

<!--
  - Everything is a one-line pointer: the agent reads on demand.
  - ANTI-PATTERN: do NOT paste big ledgers into AGENTS.md or @-import them.
  - Result: a small, stable tier 1 (which also keeps the prompt prefix cache-friendly).
-->
