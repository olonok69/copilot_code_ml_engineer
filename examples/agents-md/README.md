# AGENTS.md + instructions — the "two-tier context" pattern in GitHub Copilot

In Claude Code the always-loaded file is `CLAUDE.md`. In Copilot the role is covered by:

1. **`AGENTS.md`** at the repo root (short orientation, pointers) — read by the CLI, VS Code, the cloud
   agent and code review on github.com. Prefer it as the one shared voice with Cursor and Claude Code.
2. **`.github/copilot-instructions.md`** — optional, small. Read by every surface, and the **only** file
   code review in VS Code / Visual Studio / Eclipse reads.
3. **`.github/instructions/*.instructions.md`** with `applyTo` globs — scoped gates (the counterpart of
   Cursor `.mdc` `globs` / Claude `.claude/rules` `paths:`). Optional `excludeAgent: "code-review"` or
   `"cloud-agent"`; VS Code adds `name` / `description`.

The typical mistake is the same in every tool: putting the whole history into the always-loaded tier until
every turn pays a huge tax.

## Files in this folder

| File | Tier | What it shows |
|---|---|---|
| [`AGENTS.md`](./AGENTS.md) | 1 | Orientation + repo map + one-line pointers |
| [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) | 1 | The few non-negotiables every surface (incl. IDE code review) must see |
| [`.github/instructions/tests.instructions.md`](./.github/instructions/tests.instructions.md) | scoped | `applyTo` + `excludeAgent` frontmatter |
| [`.claude/rules/no-print-debugging.md`](./.claude/rules/no-print-debugging.md) | scoped | The CLI also reads `.claude/rules/**/*.md` with `paths:` — Claude Code rules reuse as-is |

Full methodology pack: [`../../docs/ai-agents-code-methodology/copilot/`](../../docs/ai-agents-code-methodology/copilot/).

## Loading rules per surface (verified 2026-10-17)

| Surface | What it loads |
|---|---|
| **Copilot CLI** | All sources merged: `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`, `.github/instructions/**`, `.claude/rules/**`, `.github/copilot-instructions.md` — each **at the git root and at the cwd only** — plus `~/.copilot/copilot-instructions.md`, `~/.copilot/instructions/**`. ⚠️ A nested `subdir/AGENTS.md` is read only if you launch `copilot` from that subdir. ⚠️ `~/.claude/CLAUDE.md` is **not** read. |
| **Cloud agent / github.com** | "The **nearest** `AGENTS.md` in the directory tree takes precedence" + `copilot-instructions.md` + path instructions + `CLAUDE.md`/`GEMINI.md`. |
| **Code review (github.com)** | Same family, plus `REVIEW.md` — read from the PR's **head** branch (protect with CODEOWNERS). |
| **VS Code Local harness** | `chat.useAgentsMdFile`; nested AGENTS.md only with `chat.useNestedAgentsMdFiles` (off by default); `CLAUDE.md` with `chat.useClaudeMdFile`. |
| **JetBrains Chat** | `copilot-instructions.md` + path instructions; AGENTS.md ✗ in Chat. |

**Safe pattern for per-folder rules:** an `.instructions.md` with `applyTo: "subdir/**"` — it works the same
everywhere, unlike nested `AGENTS.md`.

### `@path` imports — CLI only

The CLI expands `@path` imports eagerly (recursive, with cycle and size guards) inside `AGENTS.md`,
`CLAUDE.md` and `.github/copilot-instructions.md`. VS Code docs instead say "use Markdown links"; whether
VS Code expands `@path` is NOT DOCUMENTED. Eager = paid every turn → use pointers by default
(see [`../context/AGENTS.pointers-example.md`](../context/AGENTS.pointers-example.md)).

## Tier 2 — on demand (all the detail)

Files under `data/changes/` the agent reads **only when the ticket calls for it**:

| File | Contents |
|---|---|
| `STATUS.md` | Live ledger: status per ticket (branch/commit/PR/test count). |
| `PLAYBOOK.md` | Codified debugging lessons. |
| `SHARP_EDGES.md` | "Do not touch" invariants with the ticket that set them. |
| `CONVENTIONS.md` | Confidentiality / sanitisation policy. |
| `<TICKET>/<TICKET>.md` | Per-ticket ledgers, each self-contained. |

### The write-once discipline

> Each record is written in **exactly one** canonical ledger. `AGENTS.md` / instructions carry a
> **pointer**, never a copy. In the original Claude Code project the trim was **~73%** with no loss of
> information — the same goal applies here.

## What differs from Claude Code and Cursor

| Claude Code | Cursor | Copilot |
|---|---|---|
| `CLAUDE.md` (+ `~/.claude/CLAUDE.md`) | `AGENTS.md` + `.cursor/rules` | `AGENTS.md` and/or `.github/copilot-instructions.md` (CLI also reads `CLAUDE.md`) |
| `.claude/rules` `paths:` | `.mdc` `globs` | `.github/instructions/*.instructions.md` `applyTo` (CLI also `.claude/rules`) |
| `@path` eager import | `@file` in `.mdc` | `@path` in the CLI only |
| `~/.claude/CLAUDE.md` | user rules | `~/.copilot/copilot-instructions.md`, `~/.copilot/instructions/` |
| auto-memory `MEMORY.md` | Cursor Memories | Copilot Memory (cloud, preview, 28-day expiry) — a complement, never the source of truth |

See also [`../context/`](../context/).
