# Tool prevalence — what Copilot uses and when

**Instructions** (`.github/instructions/*.instructions.md`) and `AGENTS.md` do not only say *what* to do; they say **which tool**
and in what order. That turns "I have MCP installed" into "the agent pulls the right tool."

## The golden rule: graph navigation before reading files

> **"For 'what is this / who depends / what do I touch', a `codegraph_explore` **first** — source + call
> paths + blast radius + test-coverage flags in one call (treat the source it returns as ALREADY
> read; do not re-open it). Serena `find_referencing_symbols` for the **precise** check before renaming or
> deleting a helper (disambiguates by class). grep/Read only for literals."** — instruction in
> `.github/instructions/01-tool-prevalence.instructions.md`.

> **Two graphs, two domains.** CodeGraph indexes the *code*; the **`kg`** skill (graphify) indexes
> *project memory* (tickets, sharp edges). Detail: [`../../docs/KNOWLEDGE_GRAPH.md`](../../docs/KNOWLEDGE_GRAPH.md).

## Prevalence table

| I need… | Preferred tool | Why / rule |
|---|---|---|
| Survey: what is / who depends / blast / tested? | **CodeGraph** `codegraph_explore` | 1 query; treat as ALREADY read |
| Precise check before rename/delete | **Serena** `find_referencing_symbols` | Mandatory; disambiguates by class |
| Body / overview of a large file | Serena `find_symbol` / `get_symbols_overview` | Or the source from `explore` |
| Output contract | **Playwright** (built into the CLI) / F12 | What the consumer sees |
| Deployed runtime | **Docker** (same image) | Green tests ≠ what was shipped |
| Cheap root cause | **Oracle** (`_diag_*.py` / parser) | No model call to diagnose |
| Cloud logs / config | **AWS CLI** (read-only) | First-class debugging |
| Library docs | **Context7** | Vs training cutoff |
| git / PRs | `gh`, `git` | status-first |
| Tickets / lessons in the area | **Skill `kg`** (or STATUS fallback) | history-first before grep |
| Live ticket status / a wiki page | **Skill `atlassian`** ([`tools/atlassian/`](./tools/atlassian/)) | GET only, enforced in code; tickets and Confluence are written by the person (Confluence: plan → diff → OK per page) |
| Evidence of a failed run | **Skill `evidence`** ([`tools/README.md`](./tools/README.md)) | The log line is the index; S3 version chosen by time window, not the current one; read-only |
| Independent parallel work | **Subagents** (built-in `explore`, `/fleet`, custom `.agent.md`) | Without cluttering the main thread |

## Install and smoke

Runbook to configure the 5 tools (CodeGraph, Serena, Playwright, Context7, kg) and try them:
[`../../docs/ai-agents-code-methodology/AGENT_SETUP_TOOLS.md`](../../docs/ai-agents-code-methodology/AGENT_SETUP_TOOLS.md)

## The order (cheap → expensive)

1. Orientation: `STATUS.md` + `git`/`gh` + skill **`kg`**
2. Navigation: CodeGraph → Serena
3. Diagnosis: deterministic oracle
4. Environment: AWS CLI
5. Contract: Playwright
6. Outbound: wrapper + Docker
7. Only at the end: model call to verify the fix

## Skills vs oracles

| | **Skills / MCP** | **Oracles** (`_diag`, parser) |
|---|---|---|
| What it is | Registered capability (auto-select by `description`) | Code the agent writes and runs in Shell |
| Where (Copilot) | `.github/skills/` · `~/.copilot/skills/` · MCP | `data/changes/<ticket>/` (gitignored) or `src/`/`tests/` |
| Examples | `kg`, `sanitise-diff`, Serena, CodeGraph, Playwright | `_diag_pdf.py` |

In Claude Code `/kg` lived in `~/.claude/skills/`. In Copilot: project skill (`.github/skills/`) or user
(`~/.copilot/skills/`) — the CLI does **not** read `~/.claude/skills/`.

## Permissions (different from Claude)

Claude Code: hand-curated allowlist in `settings.local.json` (`mcp__serena__…`, etc.).

Copilot:

1. **Instructions** — prevalence and "no push, ever" (`AGENTS.md`, `copilot-instructions.md`).
2. **Per-run flags** — `--allow-tool='serena'`, `--deny-tool='shell(git push)'` (deny beats allow; never persisted).
3. **Hooks** — `preToolUse` deny for push/PR/merge/deploy ([`../hooks/`](../hooks/)) — the only repo-committable veto,
   because `.github/copilot/settings.json` cannot hold allow/deny lists.

Do not copy Claude's allow JSON; re-implement the *policy* with instructions + flags + hooks
([`../permissions/`](../permissions/)).
