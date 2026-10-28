# GitHub Copilot — Technical implementation guide (course in two sessions)

> Versión en español: [`GUIA_TECNICA.md`](./GUIA_TECNICA.md).

> Copy-paste reference for building each piece. It complements
> [`SPEAKER_GUIDE.md`](./SPEAKER_GUIDE.md) (the narrative thread) with the **how**.
> Runnable artifacts are in [`examples/`](./examples/); [`docs/`](./docs/) is the methodology pack and
> reference material. Sibling volumes, same structure and section numbering:
> [Claude Code](https://github.com/olonok69/claude_code_ml_engineer) ·
> [Cursor](https://github.com/olonok69/cursor_code_ml_engineer) ·
> [Pi](../pi_code_ml_engineer).
>
> **Verification note:** every Copilot claim here comes from
> [`docs/research/COPILOT_FINDINGS_2026-10-17.md`](./docs/research/COPILOT_FINDINGS_2026-10-17.md), which
> cites a docs.github.com or code.visualstudio.com page for each fact, all fetched on **17 October 2026**.
> Where the docs are silent the guide says **UNVERIFIED** or **NOT DOCUMENTED**. Where the docs contradict
> themselves the guide says that too. Copilot moves fast — re-check before reuse.

## Table of contents

**Session 1 — GitHub Copilot**

0. [Surfaces map (read first)](#0-surfaces-map)
1. [Install, auth, headless, models, billing](#1-install-auth-headless-models-billing)
2. [Memory and instructions](#2-memory-and-instructions)
3. [Permissions, trust, sandbox](#3-permissions-trust-sandbox)
4. [Sessions](#4-sessions)
5. [Context window](#5-context-window)
6. [Prompt caching](#6-prompt-caching)
7. [MCP](#7-mcp)
8. [Skills and plugins](#8-skills-and-plugins)
9. [Custom agents and subagents](#9-custom-agents-and-subagents)
10. [Hooks](#10-hooks)
11. [Automation](#11-automation)

**Session 2 — The methodology + ticket graph**

12. [The workflow and the real example](#12-methodology)
13. [The tools: CodeGraph, Serena, GSD](#13-the-methods-tools)
14. [Transferring the methodology — from Claude Code to Copilot](#14-transferring-the-methodology)
15. [Machine sync (tarball + S3)](#15-machine-sync)

16. [Ticket knowledge graph](#16-ticket-knowledge-graph)
17. [Field test 2026-10-28: the methodology on Copilot, measured](#17-field-test-2026-10-28)

**Appendices**

- [A. Equivalence table: Claude Code → Cursor → Copilot](#a-equivalence-table-claude-code--cursor--copilot)
- [B. Gotchas that changed in 2025–2026](#b-gotchas-that-changed-in-20252026)
- [Sources](#sources)

---

# SESSION 1 — GitHub Copilot

## 0. Surfaces map

"Copilot" is not one product. Before configuring anything, decide **which surface** reads the file you
are about to write.

| Surface | What it is | Note |
|---|---|---|
| **Copilot CLI** (`copilot`) | Terminal agent, npm package `@github/copilot`. GA 2026-02-25 (public preview since Sep 2025). | ⚠️ **Not** the retired `gh copilot` extension (a 2024 GitHub CLI extension). |
| **VS Code — Copilot harness** | Same runtime as the CLI (Copilot SDK, runs in the "Agent Host"). | Shares `~/.copilot/*`, `.github/hooks` (CLI schema), `.mcp.json`, skills and agents with the CLI. |
| **VS Code — Local harness** | Classic VS Code agent mode, in the extension host. | Own `chat.*` settings, **own hook schema**, `.vscode/mcp.json`. **Prompt files and `handoffs` work only here.** |
| VS Code — Claude / Codex harnesses, Cloud target | Other engines selectable in the Session Target control. | Out of scope except "Cloud" = delegate to the cloud agent. |
| **JetBrains agent mode** | Agent mode + MCP supported. | Skills, custom agents, custom instructions and prompt files are **Preview**. |
| **Copilot cloud agent** | **Formerly "coding agent".** Takes an issue / prompt / API call / automation, works in an ephemeral GitHub Actions Linux sandbox, opens a **draft PR**. | All tools pre-approved; structurally cannot approve or merge. |
| **Copilot code review** | PR reviewer on github.com and in IDEs; can be automatic via rulesets. | Reads instructions and skills **from the PR head branch**. |
| Copilot on github.com, Copilot app | Chat, Agents page, Spaces; desktop app (`copilot app` / `/app`). | Mentioned for completeness. |

### Feature × surface matrix

| Feature | CLI | VS Code Copilot harness | VS Code Local harness | JetBrains | Cloud agent | Code review |
|---|---|---|---|---|---|---|
| `.github/copilot-instructions.md` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `.github/instructions/*.instructions.md` (`applyTo`) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AGENTS.md` | ✓ root + cwd only | ✓ | ✓ (nested: `chat.useNestedAgentsMdFiles`, off) | ✗ in Chat | ✓ nearest wins | ✓ |
| `CLAUDE.md` / `GEMINI.md` | ✓ | — | `chat.useClaudeMdFile` | — | ✓ | ✓ (+ `REVIEW.md`) |
| Prompt files `.github/prompts/*.prompt.md` | ✗ | ✗ | ✓ | ✓ (preview) | ✗ | ✗ |
| Skills | ✓ | ✓ | ✓ | Preview | ✓ | ✓ |
| Custom agents `.github/agents/*.agent.md` | ✓ | ✓ | ✓ (+ `handoffs`) | Preview | ✓ | — |
| Hooks | ✓ `.github/hooks` | ✓ CLI schema | ✓ **different schema** | — | ✓ `.github/hooks` only, Linux | **NOT DOCUMENTED** |
| MCP config | `.mcp.json`, `.github/mcp.json`, `~/.copilot/mcp-config.json` (`mcpServers`) | `.mcp.json` + user file (+ forwarded `.vscode/mcp.json`) | `.vscode/mcp.json` (`servers`) | `mcp.json` via UI (path NOT DOCUMENTED) | Repo Settings JSON | only `readOnlyHint: true` tools |
| Plan mode | `/plan`, `--plan`, Shift+Tab | Plan agent | Plan agent | — | — | — |

Sources: GH:reference/custom-instructions-support, GH:reference/copilot-feature-matrix,
VSC:agents/concepts/agent-harnesses, VSC:agent-customization/hooks, VSC:agent-customization/prompt-files.
(⚠️ The feature matrix page still lists VS Code only up to 1.108 — verify on your build.)

> **The single most important structural fact:** VS Code has **two Copilot engines**. A hook, a prompt
> file or an MCP server that works in one may silently not exist in the other. Always state the harness.

---

## 1. Install, auth, headless, models, billing

```bash
npm install -g @github/copilot                  # Node.js 22+; prerelease: @github/copilot@prerelease
brew install --cask copilot-cli                 # macOS/Linux
winget install GitHub.Copilot                   # Windows (PowerShell 6+ required)
curl -fsSL https://gh.io/copilot-install | bash # macOS/Linux script (PREFIX=, VERSION=)
copilot update                                  # or /update; auto-update on by default (COPILOT_AUTO_UPDATE=false)
```

**Auth.** `copilot login` (or `/login`) with `--host`, `--web-flow`, `--device-code` (default on remote
terminals and CI), `--with-token` (stdin). Environment tokens, in precedence order:
`COPILOT_GITHUB_TOKEN` > `GH_TOKEN` > `GITHUB_TOKEN`. A PAT must be a **fine-grained, user-owned** PAT
with the **"Copilot Requests"** account permission. In Actions with `GITHUB_TOKEN`: workflow permission
`copilot-requests: write`, and the org policy "Allow use of Copilot CLI billed to the organization" on.

**Headless.**
```bash
copilot -p "Explain ./complex.ts" -s                 # -p exits after completion; -s = only the answer
echo "Explain ./complex.ts" | copilot                # piped stdin works (ignored if -p is given)
copilot -p '...' -s --allow-tool='shell(git:*)' --deny-tool='shell(git push)' --no-ask-user --model=claude-sonnet-5.5
copilot -p '...' --output-format=json                # JSONL events
copilot -p '...' --share=./report.md                 # export the transcript
copilot -p "..." --trust-folder                      # trust repo hooks/MCP/plugins for this one -p run
copilot -p "..." --max-ai-credits=5                  # soft per-response spend cap
copilot --plan --mode autopilot -p "..."             # plan-then-autopilot
copilot -p "..." --fleet                             # parallel subagent orchestration
```

Subcommands: `copilot init` (writes `.github/copilot-instructions.md`), `copilot mcp list|get|add|enable|disable|remove`,
`copilot skill list|add [--project]|remove|enable|disable`, `copilot plugin …`, `copilot config [--repo|--local] KEY VALUE`,
`copilot instruction list`, `copilot help permissions|sandbox|config`.

Slash commands worth knowing: `/model`, `/context`, `/compact [focus]`, `/usage`, `/limits` · `/agent`,
`/subagents`, `/plan`, `/autopilot`, `/fleet`, `/delegate` (`&` prefix) · `/review`, `/security-review`,
`/rubber-duck` · `/skills`, `/mcp`, `/plugin`, `/instructions` · `/permissions`, `/sandbox` · `/resume`,
`/session`, `/rewind`, `/fork`, `/share`, `/chronicle` · `/remote`, `/pr [view|create|fix|auto|automerge]` ·
`/research`. ⚠️ **`/pr auto` and `/pr automerge` can merge PRs** — see §10 and §14.

**Models (CLI table, 2026-10-17).** Default `claude-sonnet-5.5`; also `gpt-5.4`, `claude-opus-5.5`,
`claude-haiku-5.5`, `claude-haiku-4.5`, `gpt-5.3-codex`, `gemini-3.7-flash`, `gemini-3.8-flash`, opt-in
`gpt-6.1-sol` / `gpt-6-astra` / `gpt-6-luna`, and `auto`. Select with `--model=`, `COPILOT_MODEL`,
`/model [--session|--global|--repo|--local]`, `settings.json` `"model"`, or repo `.github/copilot/settings.json`
`"model"` (trusted folders only); allowlist via `.github/allowed_models.txt`. Effort: `--effort=low|medium|high|xhigh|max`.
1M-token context: VS Code and CLI only, supported models, more credits (`--context long_context`).
BYOK: `providers.json` / `COPILOT_PROVIDERS_CONFIG`.

**Billing.** Since **2026-06-01**: GitHub **AI Credits** (1 credit = $0.01), priced per token for input,
output, cached input and cache write. Pro $10 → 1,500 credits; Pro+ $39 → 7,000; Max $100 → 20,000.
Free/Student: Auto model only. Business/Enterprise: pooled. Completions and next-edit suggestions are
not billed. Auto model selection: 10% discount on paid plans. ⚠️ **"Premium requests" and multipliers are
legacy** — they apply only to annual Pro/Pro+ plans that stayed on the old model. Any course slide that
says "300 premium requests" is out of date.

**Credits per token (checked 2026-10-26, "Models and pricing").** Prices are in dollars per 1M tokens,
so $1 per 1M tokens = 100 credits per 1M tokens. There is no fixed credits-per-token ratio: it depends
on the model and on the token type.

| Model (default tier), per 1M tokens | Input | Cached input | Cache write | Output |
|---|---|---|---|---|
| Claude Haiku 5.5 (≤100K input) | $0.10 = 10 cr | $0.01 = 1 cr | $0.125 = 12.5 cr | $0.50 = 50 cr |
| Claude Sonnet 5.5 (CLI default) | $2.00 = 200 cr | $0.10 = 10 cr | $2.50 = 250 cr | $10.00 = 1,000 cr |
| Claude Opus 5.5 | $4.00 = 400 cr | $0.20 = 20 cr | $5.00 = 500 cr | $20.00 = 2,000 cr |

Example (Sonnet 5.5): 50,000 input + 5,000 output tokens = 10 + 5 = 15 credits ($0.15); with 40,000 of the
input tokens served from cache, about 7.4 credits. Unused monthly credits do not carry over.

---

## 2. Memory and instructions

### What loads where

| File | CLI | VS Code | Cloud agent | Code review |
|---|---|---|---|---|
| `.github/copilot-instructions.md` | ✓ | ✓ | ✓ | ✓ (the **only** file VS Code / Visual Studio / Eclipse code review reads) |
| `.github/instructions/**/*.instructions.md` | ✓ | ✓ | ✓ | ✓ |
| `AGENTS.md` | root + cwd | ✓ | nearest wins | ✓ |
| `CLAUDE.md`, `GEMINI.md`, `.claude/rules/**/*.md` | ✓ | Local: `chat.useClaudeMdFile` | ✓ (`CLAUDE.md`) | ✓ + `REVIEW.md` |
| Personal | `~/.copilot/copilot-instructions.md`, `~/.copilot/instructions/**` | `~/.copilot/instructions` (Copilot harness) / profile (Local) | — | — |

**CLI loading rules.** All sources load **simultaneously and are merged**, each read in the git root
**and** in the cwd. ⚠️ A nested `<subdir>/AGENTS.md` is picked up **only if you launch `copilot` from that
subdir** — not "nearest in the tree" (that is the cloud agent's rule). ⚠️ `~/.claude/CLAUDE.md` is **not**
read by the CLI; personal instructions go in `~/.copilot/copilot-instructions.md`. Opt out with
`--no-custom-instructions`; toggle files with `/instructions`.

**`@path` imports** (eager, recursive, cycle and size guards) work in `AGENTS.md`, `CLAUDE.md` and
`.github/copilot-instructions.md` **in the CLI**. VS Code's docs say "use Markdown links"; whether VS Code
expands `@path` is **NOT DOCUMENTED** — prefer pointers.

**Path-specific instructions:**
```markdown
---
applyTo: "app/models/**/*.rb"     # comma-separated globs allowed: "**/*.ts,**/*.tsx"
excludeAgent: "code-review"       # or "cloud-agent" (optional)
---
Rules for models go here.
```
VS Code also accepts optional `name` and `description` (description enables on-demand loading). The CLI
also reads `.claude/rules/*.md` with `paths:` (or `applyTo:`) — Claude Code rules reuse as-is.

**VS Code (Local harness) settings:** `chat.useAgentsMdFile`, `chat.useNestedAgentsMdFiles` (off by
default), `chat.useClaudeMdFile`, `github.copilot.chat.codeGeneration.useInstructionFiles`,
`chat.useCustomizationsInParentRepositories`.

**Prompt files** (`.github/prompts/*.prompt.md`, frontmatter `description`, `name`, `argument-hint`,
`agent`, `model`, `tools`; invoked `/name`) run **only in the VS Code Local harness** (plus Visual Studio
and JetBrains per GitHub's docs). The CLI does not load them — use skills, or `.claude/commands/*.md`.

### Two-tier pattern (see [`examples/agents-md/`](./examples/agents-md/))
- **Tier 1** = root `AGENTS.md` (one voice shared with Cursor and Claude Code) + a small
  `.github/copilot-instructions.md` + scoped gates in `.github/instructions/<concern>.instructions.md`.
  Small, one-line pointers.
- **Tier 2** = `data/changes/` ledgers (`STATUS.md`, `PLAYBOOK.md`, `SHARP_EDGES.md`, `TEST_MAP.md`,
  `FOLLOWUPS.md`, `<ticket>/<ticket>.md`) read on demand. Use `@path` only for what must be eager.
- **Write-once rule:** each fact lives in one ledger; the always-loaded file carries the pointer.
- **Tier 0:** machine-local `IDENTITY.md` (gitignored). Load it via `~/.copilot/copilot-instructions.md`
  or a `sessionStart` hook returning `additionalContext` (CLI/cloud).
- **Per-folder rules:** because nested `AGENTS.md` behaves differently per surface, the portable pattern
  is `.instructions.md` with `applyTo: "subdir/**"`.

> **The index goes stale too.** Moving content out of the always-loaded file into an on-demand file does
> not refresh it. Real case: a 28-entry ticket→test list was moved to `TEST_MAP.md` and the check asserted
> "28 entries". It had 28 — and 28 was wrong: `tests/` held 80 files. Verify a moved list against the
> thing it describes, never against its own former self.

### Memory systems — three distinct ones, none canonical
- **Copilot Memory** (cloud, public preview): repo facts with code citations (validated against the
  branch) + user preferences; used by cloud agent, code review, CLI; **unused memories expire after 28
  days**. In the CLI, `--enable-memory` turns it on in `-p` mode.
- **VS Code memory tool** (local): `/memories/`, `/memories/repo/`, `/memories/session/`.
- **CLI session store + `/chronicle`** (`standup`, `improve` suggests edits to `copilot-instructions.md`,
  `skills create` drafts skills from usage).

Treat all three like Cursor Memories: a **complement**, never the source of truth. Canonical memory stays
in versioned ledgers.

---

## 3. Permissions, trust, sandbox

Which of these have a runnable example in the repo, and which do not (saved approvals, trusted folders,
CLI sandbox settings, managed settings, cloud-agent firewall): see the table in
[`SPEAKER_GUIDE.md` §03](./SPEAKER_GUIDE.md#03-permissions-trust-sandbox-slides-1112).

### CLI patterns: `Kind(argument)`

| Kind | Examples |
|---|---|
| `shell` | `shell(git:*)` (`:*` = command stem + space), `shell(git push)`, `shell(gh pr)` (git/gh match the first-level subcommand) |
| `write` / `read` | `write(src/*.ts)`, `read(.env)` |
| `url` | `url(github.com)` |
| `memory` | `memory` |
| MCP server | `MyMCP(tool)`, `MyMCP` |

```bash
copilot --allow-tool='shell(git:*)' --deny-tool='shell(git push)' --deny-tool='shell(gh pr)'
```
- **Deny always beats allow** — even with `--allow-all`/`--yolo` or saved approvals.
- `--deny-tool='write(PATH)'` is exact or trailing-segment matching ("no glob support yet").
- Also: `--available-tools` / `--excluded-tools` (hide tools), `--allow-url` / `--deny-url`,
  `--allow-all-paths`, `--allow-all-tools` (`COPILOT_ALLOW_ALL`), `/permissions assisted` (an LLM judge
  recommends).
- Prompt keys: `y`, `n`, `!` (allow similar for the session), `#` (deny similar). Saved approvals:
  `~/.copilot/permissions-config.json`; URLs: `allowedUrls` in `~/.copilot/settings.json`. **Flags are
  never persisted.**

⚠️ **No repo-level allow/deny lists.** `.github/copilot/settings.json` accepts only an allowlist of keys
(`companyAnnouncements`, `contextTier`, `deniedUrls`, `disableAllHooks`, `disabledMcpServers`,
`disabledSkills`, `effortLevel`, `enabledPlugins`, `extraKnownMarketplaces`, `hooks`,
`includeCoAuthoredBy`, `mergeStrategy`, `model`, `respectGitignore`) — everything else is **silently
ignored**. `permissions.deny/ask/allow` rules exist only as **enterprise-managed / MDM** settings.
**Consequence: a team-wide "never push" rule committed to the repo must be a hook (§10).**
`permissions.disableBypassPermissionsMode: "disable" | "allow-auto-only"` (user, managed or MDM) blocks
`--yolo` and the other allow-all flags.

**Trusted folders.** First launch asks; the list lives in `trustedFolders` in `~/.copilot/config.json`
(auto-managed state — user settings are in `settings.json`). Trust gates **repo hooks, workspace MCP
(`.mcp.json`, `.github/mcp.json`), repo plugin settings, repo `model`/`effortLevel`**. ⚠️ In **`-p` mode
these are skipped for untrusted folders** unless `--trust-folder`, `GITHUB_COPILOT_PROMPT_MODE_REPO_HOOKS=true`,
`GITHUB_COPILOT_PROMPT_MODE_WORKSPACE_MCP=true`, `GITHUB_COPILOT_PROMPT_MODE_EXTENSIONS=true` or
`COPILOT_ALLOW_ALL=true`. **A CI gate built on a repo hook does nothing without one of these.**

**Sandbox** (GA 2026-10-07: CLI, Copilot app, VS Code Agent Host). MXC engine (Seatbelt / Bubblewrap /
ProcessContainer). `/sandbox enable`, `--sandbox`, or `sandbox.enabled` in `~/.copilot/settings.json`.
Policy keys: `sandbox.userPolicy.network.allowedHosts|blockedHosts|allowLocalNetwork|proxy`,
`sandbox.userPolicy.filesystem.deniedPaths`, `sandbox.credentials.envVars{…injectHosts}` (secret masking),
`sandbox.auth.git`, `sandbox.auth.gh`. **Not repo-overridable.** Plan mode blocks project edits at the tool
layer ("safety net, not a guarantee").

### VS Code
`chat.permissions.default`: **Manual** (default), **Assisted**, **Allow all**. Settings:
`chat.tools.eligibleForAutoApproval`, `chat.tools.urls.autoApprove`, `chat.tools.terminal.autoApprove`
(`false` wins), `chat.tools.global.autoApprove`, `chat.agent.sandbox.enabled` (network allowed by default;
Linux/WSL2 needs `bubblewrap` + `socat`). ⚠️ A `false` terminal rule **only requires approval — it does not
block**. To block, the docs say: a `PreToolUse` hook returning `permissionDecision: "deny"`.

### Cloud agent
All tools pre-approved, no prompts; a hook `"ask"` is treated as `"deny"`. Firewall in the repository
**"Internet access"** settings (covers cloud agent + code review; not compatible with self-hosted runners).
Guardrails: only users with write access trigger it; it pushes **only to its own `copilot/` branch** (or
the PR branch when you `@copilot` an existing PR); it **cannot mark ready, approve or merge**; workflows
wait for a human "Approve and run workflows"; the requester cannot approve the PR. Protect Copilot and MCP
config with `CODEOWNERS` + "Require review from Code Owners". Examples:
[`examples/permissions/`](./examples/permissions/).

### The layers — compared with Claude Code and Cursor
1. **Flags / saved approvals** (CLI) or `chat.tools.*` (VS Code) — per user, per machine.
2. **Managed settings** — the only place for org-wide `permissions.deny`.
3. **Instructions** (`AGENTS.md`, `.instructions.md`) — judgment, not a veto.
4. **Hooks** — `preToolUse` deny by *content*; the only committable veto.
5. **Structural limits** — cloud agent cannot merge; `CODEOWNERS` on the config.

> Claude Code curates `permissions.allow/deny` in a committed `settings.json`; Cursor uses
> `permissions.json`; **Copilot has no committed allow/deny** — the same *policy* (the human owns
> everything external) is re-implemented with a hook + flags + structural limits.

---

## 4. Sessions

| Need | CLI | VS Code |
|---|---|---|
| Resume | `copilot --continue`, `--resume[=ID|name]`, `/resume`; every `-p` run prints a `--resume` hint | Sessions view |
| Name | `-n NAME`, `/rename` | — |
| Parallel | `/fork` (works while running), `/new worktree`, `-w`, Sessions sidebar | multi-chat, `/fork`, fork from checkpoint |
| Checkpoints | at **every compaction**: `/session checkpoints` (a *summary*, not a file snapshot) | checkpoints |
| Roll back | `/rewind` (alias `/undo`): conversation only, or conversation + files; git not required | restore checkpoint |
| Share | `/share`, `--share`, `--share-gist` (no gists for EMU/data-residency) | — |
| Remote | `/remote on`, `--remote` (GA 2026-05-18: steer from github.com, Mobile, VS Code) | — |
| Hand off to cloud | `/delegate` or `&` prefix → branch + draft PR | Session Target → Cloud |

Unlike Cursor (independent entry points), Copilot **does** hand sessions between surfaces: CLI → cloud via
`/delegate`, VS Code Session Target with history, and remote steering of a running CLI session.

---

## 5. Context window

Full reference: [`examples/context/`](./examples/context/).

```text
/context              # usage by System Prompt, Custom Instructions, System Tools, MCP Tools, Messages, Free Space, Buffer
/compact [focus]      # manual compaction; Esc cancels; compactions cannot be undone
```
- **Auto-compaction** starts in the background at **~80%** and pauses at ~95%. VS Code: disable with
  `github.copilot.chat.summarizeAgentConversationHistory.enabled`; the context-window control in the chat
  input shows the breakdown and AI credits.
- Tool output **> 20 KiB** is written to a temp file; the model gets the path + a preview
  (`COPILOT_LARGE_OUTPUT_THRESHOLD_BYTES`).
- **Deferred tool loading:** `toolSearch` setting; per-MCP-server `deferTools: "auto"|"never"`.
- MCP server instructions: only allowlisted servers' instructions load up front
  (`--allow-all-mcp-server-instructions` loads all).
- Subagents run in separate windows. ⚠️ Custom agents spawned as subagents get **no repo instructions**
  unless `include-custom-instructions: true`.
- VS Code references: `#codebase` runs a search (it does not dump the codebase), `#file:`, `#fetch`, `#tool:<name>`.
- Exact default window per model: **NOT DOCUMENTED** in one table.

**Lean-context levers:** small stable instructions; rarely-needed material in skills (loaded on demand);
fewer MCP servers (`disabledMcpServers`); subagents for noisy research; new session between unrelated
tasks. *If you can delete a line from `AGENTS.md` without the agent getting things wrong, delete it.*

---

## 6. Prompt caching

**The honest answer: there is no user-facing caching control in Copilot.** No `cache_control`, no TTL, no
env var — in CLI, VS Code or cloud agent (NOT DOCUMENTED anywhere). SDK-level controls: NOT DOCUMENTED.

But caching happens and **you pay for it**: the pricing tables bill **cached input** and **cache write**
per model (Anthropic and GPT-5.6+/GPT-6 families list cache-write costs).

What you *can* do:
- **Diagnose in VS Code with the Cache Explorer** (Agent Debug Logs → Summary → Cache Explorer): per-turn
  hit %, reused tokens, and the **first divergence** in the prompt signature (system / tools / messages).
  Diagnosis only — not control.
- **Keep the prefix stable**: choose model, effort, context size and tools *before* the first request;
  don't edit instruction or agent files mid-session; attach only relevant context; subagents for side
  research; `/compact` or a new session deliberately. **Forking preserves the prompt cache.**
- The CLI has no cache view; `/usage` shows per-model tokens and credits. OpenTelemetry export exists;
  whether it carries cache-token attributes is UNVERIFIED.

The mechanism itself (prefix caching, breakpoints, write/read multipliers) is shown with the Anthropic API
in [`examples/prompt-caching/`](./examples/prompt-caching/) — to understand *why* the stable-prefix advice
works, not because Copilot exposes it.

---

## 7. MCP

| Surface | File | Top key |
|---|---|---|
| CLI user | `~/.copilot/mcp-config.json` | `mcpServers` |
| CLI workspace | `.mcp.json` (any dir cwd → git root), `.github/mcp.json` — **requires folder trust** | `mcpServers` |
| CLI per session | `--additional-mcp-config='{json}'` or `@file` | — |
| VS Code Copilot harness | `.mcp.json` + `~/.copilot/mcp-config.json`; forwards eligible `.vscode/mcp.json` servers **except those using `${input:...}`** | `mcpServers` |
| VS Code Local harness | `.vscode/mcp.json` or profile `mcp.json` | **`servers`** (+ `inputs[]`, `sandbox{}`) |
| JetBrains | `mcp.json` via Chat → tools icon → "Add MCP Tools" (disk path NOT DOCUMENTED) | `servers` |
| Cloud agent + code review | Repo **Settings → Copilot → MCP servers** (JSON in the UI) or `mcp-servers:` in agent YAML | `mcpServers` |

```jsonc
// .mcp.json (CLI + VS Code Copilot harness). JSON proper has no comments — see examples/mcp/.
{ "mcpServers": {
    "codegraph": { "command": "codegraph", "args": ["serve", "--path", ".", "--mcp"], "tools": ["*"] },
    "serena":    { "command": "uvx", "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server"], "tools": ["*"] },
    "context7":  { "type": "http", "url": "https://mcp.context7.com/mcp", "tools": ["*"] }
} }
```
- **`tools` is required** in CLI and cloud configs. Other fields: `env` (`$VAR`, `${VAR:-default}`), `cwd`,
  `timeout`, `deferTools`; remote: `headers`, `oauthClientId`, `oauthScopes`, `oauthGrantType: client_credentials`.
- Tool names reach the model as `serverName-toolName`.
- **Built into the CLI:** `github-mcp-server` (read-heavy default subset), **`playwright`**, `fetch`, `time`.
  ⚠️ **Do not configure Playwright again.** Disable with `--disable-builtin-mcps` / `--disable-mcp-server NAME`.
- ⚠️ `${workspaceFolder}` is VS Code-only. Whether `--path .` resolves against the session cwd for workspace
  servers is UNVERIFIED — launch from the repo root, or use an absolute path in `~/.copilot/mcp-config.json`.
- **Cloud agent:** default servers GitHub (read-only) + Playwright (localhost). Tools only — no resources,
  prompts or OAuth remote servers. Secrets: Agents secrets/variables prefixed **`COPILOT_MCP_`**. Tools run
  without approval → allowlist read-only tools. Install binaries in `.github/workflows/copilot-setup-steps.yml`
  (single job named `copilot-setup-steps`, on the default branch). Context7 needs a firewall allow rule.
- **Code review uses an MCP tool only if `annotations.readOnlyHint: true`.**
- Migration: `jq '{mcpServers: .servers}' .vscode/mcp.json > .mcp.json`.

Examples: [`examples/mcp/`](./examples/mcp/) · live: [`.mcp.json`](./.mcp.json).

> **Config gives capability; instructions give judgment.** Installing Serena makes the tool exist; making
> the agent reach for it unprompted takes an instruction with a trigger map ("CodeGraph BEFORE reading
> whole files; `find_referencing_symbols` ALWAYS before a rename") —
> [`examples/methodology/tools.md`](./examples/methodology/tools.md).

---

## 8. Skills and plugins

| Surface | Project | Personal |
|---|---|---|
| CLI | `.github/skills/`, `.agents/skills/`, `.claude/skills/` | `~/.copilot/skills/`, `~/.agents/skills/` |
| VS Code | `.github/skills/`, `.claude/skills/`, `.agents/skills/` | `~/.copilot/skills/`, **`~/.claude/skills/`**, `~/.agents/skills/` |
| Cloud agent, code review | `.github/skills`, `.claude/skills`, `.agents/skills` | — |

⚠️ **The CLI does not read `~/.claude/skills/`** (VS Code does). Copy or symlink personal skills to
`~/.copilot/skills/`, or `copilot skill add <dir>` / `COPILOT_SKILLS_DIRS`.

**Frontmatter.** `name` (required) + `description` (required, ≤1024 chars); optional `argument-hint`,
`allowed-tools` (CLI/cloud), `user-invocable`, `disable-model-invocation`; `context: fork` (VS Code,
feature-flagged); `license` (cloud). ⚠️ **VS Code requires `name` to be lowercase-hyphen and equal to the
folder name, or the skill "silently fails to load"** — the portable rule is: folder name = `name`.
⚠️ Drop Claude-style `trigger:` keys (not a Copilot key; whether unknown keys are ignored is UNVERIFIED).
The exact grammar of `allowed-tools` entries is UNVERIFIED beyond `shell`.

**Invocation:** `/skill-name`, or automatically by `description`. Manage with `/skills list|info|add|remove|reload`,
`copilot skill …`, VS Code "Chat: Open Customizations", `gh skill` (GitHub CLI ≥ 2.90, preview).

```text
.github/skills/audit/SKILL.md            # live in this repo → /audit on ex_npm
.github/skills/audit-python/SKILL.md     # → /audit-python on ex_app
.github/skills/deploy-staging/SKILL.md   # → /deploy-staging on ex_staging
```
Methodology skills (`day`, `atlassian`, `evidence`, `preview`, `kg`, `kg-refresh`, `methodology-plan`,
`sanitise-diff`): [`docs/ai-agents-code-methodology/copilot/skills/`](./docs/ai-agents-code-methodology/copilot/skills/);
worked examples with their tools: [`examples/skills-plugins/`](./examples/skills-plugins/) +
[`examples/methodology/tools/`](./examples/methodology/tools/). `day`, `atlassian`, `evidence` and `preview` use local
credentials (`preview` also Docker) — **local surfaces only, not the cloud agent**.

⚠️ **The strongest reason for a skill is enforcement, not convenience.** "Pull at the start, push at the end"
sat in an operations doc for months without being followed; packaged as `day start` / `day end` it both
executes and leaves the record that makes a lapse visible. Copilot adds a real upgrade over Cursor here: a
CLI `sessionStart` **prompt hook** `{"type":"prompt","prompt":"/day start"}` (new interactive sessions only)
can *run* the routine instead of reminding you.

**Plugins.** Agent Plugins 1.0 (`plugin.json` with the agent-plugins.org schema) or legacy Copilot
`plugin.json`; the legacy loader also accepts `.claude-plugin/plugin.json`, and Claude Code marketplaces are
readable. `copilot plugin install NAME@MARKETPLACE | OWNER/REPO | URL | PATH`,
`copilot plugin marketplace add OWNER/REPO`; built-in marketplace **`awesome-copilot`**. Repo-declared:
`enabledPlugins` / `extraKnownMarketplaces` in `.github/copilot/settings.json`.

---

## 9. Custom agents and subagents

Full reference + diagram: [`examples/subagents/`](./examples/subagents/). Live:
[`.github/agents/refactor-scout.agent.md`](./.github/agents/refactor-scout.agent.md).

**Locations (CLI, priority order):** `~/.copilot/agents/` → `.github/agents/` (cwd → git root; deepest
wins) → `.claude/agents/` → `--add-dir` roots → plugins → org/enterprise (`/agents` in the org's `.github`
or `.github-private` repo). Extension `*.agent.md`. VS Code: `.github/agents/*.agent.md`, user folder,
`.claude/agents/*.md`.

```yaml
---
name: refactor-scout
description: Read-only blast-radius research before a rename or delete; returns a summary
tools: ["read", "search"]      # the read-only tools list IS the enforcement — prose is not
user-invocable: true
---
```
Frontmatter: `description` (required CLI/cloud), `name`, `tools` (aliases `execute/shell/Bash`, `read`,
`edit`, `search`, `agent`, `web`, `todo`, `server/*`, `server/tool`; `[]` = none), `model`,
`target: vscode|github-copilot`, `disable-model-invocation`, `user-invocable`, `mcp-servers` (cloud + CLI),
CLI-only `include-custom-instructions`, `hooks`, `sidekick:`; **VS Code Local only:** `handoffs[]`,
`agents[]`, `argument-hint`. Body max 30,000 chars (cloud).

**Built-in CLI subagents:** `code-review`, `explore`, `general-purpose`, `research`, `rubber-duck`,
`security-review`, `task`. Spawned through the `task` tool; background agents can be messaged
(`write_agent`). ⚠️ The docs list default models for built-ins (`claude-sonnet-4.6`, `gpt-5.4-mini`) that
**differ** from the CLI default-model table (`claude-sonnet-5.5`) — a documentation inconsistency.

**Limits:** concurrency by plan (Free 2, Pro 4, Max 8, Business 16, Enterprise 32). ⚠️ Max depth is **6** in
the reference table but **4** in the env-var table (`COPILOT_SUBAGENT_MAX_DEPTH`) — the docs contradict
themselves; verify on your build.

**Parallelism and teams.** `/fleet` / `--fleet` runs a plan with parallel subagents; **sidekick agents**
run in the background and post to the session inbox; `/tasks`; `/delegate` hands to the cloud agent. Copilot
is closer to Claude Code's Agent Teams than Cursor is (messaging via `write_agent`), but it is still not the
same lead/teammates/shared-inbox model.

| | Subagent (`task`) | `/fleet` | Cloud agent (`/delegate`) |
|---|---|---|---|
| Context | Isolated; returns summary | N isolated subagents on a plan | Full session in Actions sandbox |
| Communication | Result → parent (`write_agent` for background) | Orchestrated by the parent | Draft PR + comments |
| Cost | Low | Medium | High |
| Output | Text | Edits in your session | Branch `copilot/…` + draft PR |

---

## 10. Hooks

Everything in [`examples/hooks/`](./examples/hooks/); live in
[`.github/hooks/block-external-git.json`](./.github/hooks/block-external-git.json).

**Support:** CLI and cloud agent (one schema), VS Code (Preview, **two implementations**), code review:
NOT DOCUMENTED.

**Locations (CLI, all combined):** `/etc/github-copilot/policy.d/*.json` (root-owned) →
**`.github/hooks/*.json`** → `~/.copilot/hooks/*.json` → inline `hooks` in `.github/copilot/settings.json`,
`.github/copilot/settings.local.json`, **`.claude/settings.json`**, `.claude/settings.local.json` →
`~/.copilot/settings.json` → plugin `hooks.json` → agent frontmatter `hooks:`. The cloud agent reads only
`.github/hooks/*.json` (Linux; `powershell` entries ignored; CWD `/workspace`). Changes load at CLI start.

```json
{ "version": 1,
  "hooks": {
    "preToolUse": [
      { "type": "command", "matcher": "bash|powershell",
        "bash": "./.github/hooks/block-external-git.sh",
        "powershell": "./.github/hooks/block-external-git.ps1",
        "cwd": ".", "timeoutSec": 10 }
    ] } }
```

**Events:** `sessionStart`, `sessionEnd`, `userPromptSubmitted`, `userPromptTransformed`, **`preToolUse`**,
`postToolUse`, `postToolUseFailure`, `permissionRequest` (CLI), `agentStop`, `subagentStart`,
`subagentStop`, `preCompact`, `errorOccurred`, `notification` (CLI). Types: `command`, `http` (https for
`preToolUse`/`permissionRequest`), `prompt` (`sessionStart` only).

**`preToolUse` contract:**
- Input `{sessionId, timestamp, cwd, toolName, toolArgs}`. ⚠️ `toolArgs` is typed `unknown` but the docs'
  debug example passes a **JSON string** — handle both.
- Output: one JSON object `{"permissionDecision":"allow"|"deny"|"ask","permissionDecisionReason":"…"}`
  (reason required for deny; `modifiedArgs` optional).
- Exit codes: `0` parse stdout · **`2` = deny** · other non-zero = **fail-closed deny** for `preToolUse`.
- ⚠️ **Timeouts are fail-OPEN — every event, policy hooks included** (default 30 s). Keep blocking hooks fast.
- `agentStop` / `subagentStop`: `{"decision":"block","reason":"…"}` forces another turn (guard after 8) — a
  "verify before stop" gate.
- Kill switch: `disableAllHooks: true`.
- PascalCase aliases (`PreToolUse`) switch the payload to VS Code-style snake_case and Claude matcher
  semantics (`bash`/`powershell` → `Bash`, `view` → `Read`, `task` → `Agent`).

**VS Code Local harness — different schema.** Files: `.github/hooks/*.json`, `~/.copilot/hooks/*.json`,
`.claude/settings*.json` (only with `chat.useClaudeHooks`, off by default), agent frontmatter, plugins.
PascalCase events; input `{tool_name, tool_input, tool_use_id}`; output
`{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"…"}}`;
exit 2 = blocking error. Copilot-format files are parsed there but runtime payloads use the Local schema.

**The portable block recipe (this repo's hook):** one script reads both payload shapes
(`toolArgs.command` as string or object, or `tool_input.command`), filters to shell tools inside the
script (Local may ignore the matcher — UNVERIFIED), denies `git push`, `gh pr create|merge|ready`, `gh api …/merge`,
`gh release create`, `terraform apply`, `kubectl apply`, `helm upgrade|install`, `aws … deploy`, prints
both output shapes and **exits 2** — the one blocking signal documented in both schemas. On no match it
prints `{}` and exits 0 — deliberately **not** `"allow"`, which could auto-approve the tool.

```bash
bash .github/hooks/test-block-external-git.sh          # 16 offline cases incl. a known-answer canary
PS=1 bash .github/hooks/test-block-external-git.sh     # also the PowerShell twin
```

⚠️ Two gaps to close by policy, not by this hook: **`/pr create|auto|automerge`** are first-party CLI
commands; whether they pass through `preToolUse` is **UNVERIFIED** → name them human-only in instructions
and test the hook against them on your build. And **in `-p`/CI, repo hooks don't load in an untrusted folder**
→ `--trust-folder`. Belt and braces: `--deny-tool='shell(git push)' --deny-tool='shell(gh pr)'`.

---

## 11. Automation

See [`examples/automation/`](./examples/automation/).

**`copilot -p` in GitHub Actions:**
```yaml
permissions:
  contents: read
  copilot-requests: write          # GITHUB_TOKEN path; or COPILOT_GITHUB_TOKEN = fine-grained PAT
steps:
  - uses: actions/checkout@v4
  - run: npm install -g @github/copilot
  - run: |
      copilot -p "Review the diff against main and list risky changes" -s --no-ask-user \
        --trust-folder \
        --allow-tool='shell(git:*)' \
        --deny-tool='shell(git push)' --deny-tool='shell(gh pr)'
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
`COPILOT_TASK_WAIT_TIMEOUT_SECONDS` (default 600) bounds the wait for background tasks.

**GitHub recommends GitHub Agentic Workflows** (`github/gh-aw`) over raw `copilot` steps (guardrails,
default `GITHUB_TOKEN`).

**Cloud agent via REST (public preview, user-to-server tokens only):**
```bash
curl -X POST https://api.github.com/agents/repos/OWNER/REPO/tasks \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{"prompt":"Fix the flaky health test","base_ref":"main","create_pull_request":true}'
# list: GET /agents/repos/OWNER/REPO/tasks · GET /agents/tasks
```
Also: assign an issue to Copilot (REST/GraphQL); **Automations** (repo Agents → Automations pane;
schedule- or event-triggered; events from users without write access ignored by default); integrations
(Slack, Teams, Jira, Linear, Azure Boards, Raycast); CLI `/every`, `/after` (experimental).

**Copilot SDK:** `@github/copilot-sdk` (npm), `github-copilot-sdk` (pip, `from copilot import CopilotClient`),
Go, .NET, Java. Flow: `new CopilotClient()` → `createSession({model:"auto"})` → `sendAndWait({prompt})`;
programmatic hooks (`onPreToolUse`) return `permissionDecision`. SDK caching controls: NOT DOCUMENTED.

**Code review automation:** ruleset rule **"Automatically request Copilot code review"** ("Review new
pushes", "Review draft pull requests"); effort Lite or Balanced; reads `copilot-instructions.md`, path
instructions, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `REVIEW.md` and `.github/skills` **from the head
branch** — so a PR can change its own reviewer's instructions: protect them with CODEOWNERS. ⚠️ **Copilot
approvals** (preview, off by default) can count toward required approvals — **keep off** if the human owns
merge.

**ACP server:** `copilot --acp`.

---

# SESSION 2 — The methodology

## 12. Methodology

The deep material (11-stage workflow, real end-to-end example, tool prevalence) is in
[`examples/methodology/`](./examples/methodology/). Summary:

### The real workflow ([`WORKFLOW.md`](./examples/methodology/WORKFLOW.md))
Agent = disciplined collaborator; autonomy is earned per decision. 11 stages chained by **deterministic
gates**: orient (`kg` skill + history + status) → inbound triage against the **output contract** →
regression vs pre-existing → investigate with a **deterministic oracle** (before the paid LLM call) →
**plan mode** (`/plan`, enforced at the tool layer) + human agreement → implement: TDD RED→GREEN → verify
(unit + scoped + regression + contract via the *wrapper* AND inside the deployed image) → document →
**sanitise** (`sanitise-diff` skill on added lines) → handoff (the agent does **not** push/PR/merge/deploy —
`preToolUse` hook + instructions; the human does it) → review (Copilot code review, **approvals off**) +
persist (`kg-refresh` if applicable). Diagram: [`flow.png`](./examples/methodology/flow.png). Case study:
[`REAL_EXAMPLE.md`](./examples/methodology/REAL_EXAMPLE.md).

> **The outbound gate is FIVE checks** (not "the tests pass"):
> **(0) validate the measuring instrument** — any diagnostic that informs a ship decision first runs against
> a **known-answer case**, recorded next to the finding; never wrap the measurement in your own
> `try/except → return False`;
> **(1) reproduce at the real output stage** — the *wrapper* that rebuilds the contract, not an internal
> function; **(2) the output matches the contract on the member LIST, never on a total**; **(3) verify inside
> the deployed image**; **(4) look at the output** rendered, by eye, before the PR. Green tests are not proof
> of what ships. Identical in role to the Claude Code and Cursor gates — only which agent runs it changes.
>
> **Five ways a green gate proves nothing** (all five have bitten us): a **broken instrument** (a probe that
> swallows its own error and reports a uniform plausible "no"); **a total that matches** (one item wrongly
> added and one wrongly dropped cancel — assert on ids, measure deltas); **a gate that couldn't fail** (a
> detector firing on 0 of 190 corpus documents reads the same whether correct or broken — say so); **a canary
> that never applied the real perturbation** (synthetic test recovered 100%, the real change recovered <1%
> because it touched what the test never did); **a structural gate read as a semantic one** (every group
> matched, zero orphans — and 56% of the carried-over names were wrong; schedule the human read).
>
> **The output contract is a living document.** When a change alters what is emitted: **comply**, **revise**
> the rule in the same change, or **record** why it's out of scope. Silence is not an option. Cite rules by
> stable identifier, never by local path.
>
> **Where does the expected number come from?** "The other environment returns X" is evidence about that
> environment, never a specification.

### Tool prevalence ([`tools.md`](./examples/methodology/tools.md))
`AGENTS.md` and `.github/instructions/01-tool-prevalence.instructions.md` say **which tool, in what order**
(cheap → expensive, deterministic → probabilistic):
```
Orient       -> kg skill (ticket graph) · STATUS.md/ledgers · git · gh (read-only)   (no inference)
Navigate     -> CodeGraph codegraph_explore (MCP) — source + paths + blast radius, treat as ALREADY read
Refactor-chk -> Serena find_referencing_symbols (MCP) — MANDATORY before rename/delete
Diagnose     -> deterministic oracle (parser/validator/_diag_*.py)
Environment  -> cloud CLI, read-only
Contract     -> Playwright (built into the Copilot CLI) / browser dev tools against the output endpoint
Deployed     -> Docker: repro inside the runtime image
Only at the end -> the agent turn, to VERIFY the fix (not to diagnose)
```

### Method permissions (same policy, third mechanism)
Claude Code: committed allowlist. Cursor: `permissions.json` + rules + hooks. **Copilot: no committed
allow/deny** → (1) instructions for prevalence and "no push", (2) per-user CLI flags or VS Code
`chat.tools.*`, (3) **the `preToolUse` hook** as the committable veto, (4) cloud-agent structural limits,
(5) managed `permissions.deny` for org policy.

---

## 13. The method's tools

Setup + smoke tests: [`AGENT_SETUP_TOOLS.md`](./docs/ai-agents-code-methodology/AGENT_SETUP_TOOLS.md).

### CodeGraph ([`examples/codegraph/`](./examples/codegraph/))
Tree-sitter index → SQLite in `.codegraph/` (no API keys). Symbols + call paths + blast radius + test
coverage flags, in one round-trip.
```bash
codegraph init ; codegraph sync ; codegraph explore "<symbol|question>"
```
Register in `.mcp.json` with `"tools": ["*"]` (§7); for the cloud agent, install it in
`copilot-setup-steps.yml` and paste the server JSON into repo settings. It is the **first** navigation tool;
treat its output as already read. On WSL2 `/mnt`, the watcher can miss changes → `codegraph sync`.

### Serena ([`examples/serena/`](./examples/serena/))
LSP-backed semantic navigation. `find_referencing_symbols` is the precise check before renaming/deleting
(disambiguates same-named methods by class). Complements CodeGraph. The read-only
[`refactor-scout`](./.github/agents/refactor-scout.agent.md) agent packages CodeGraph → Serena → grep.

**Copilot does not inherit Serena from other agents.** In the 2026-10-28 field test it was missing only
because it had never been registered for Copilot. Adding it to the personal config fixed it:
```jsonc
// ~/.copilot/mcp-config.json (back it up first)
{ "mcpServers": {
    "serena": { "command": "uvx", "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server"], "tools": ["*"] }
} }
```
Measured after a restart, in VS Code Copilot: `initial_instructions`, `find_symbol` and
`find_referencing_symbols` worked; `safe_delete_symbol` refused to delete a referenced method and listed its
5 reference sites; `rename_symbol` reported 7 changes across the definition, one caller and tests in 3 files
(reverted with git). `replace_symbol_body` and the insert tools were not exercised.
- ⚠️ The first call per session can time out while the Python language server warms up (~1 min). Retry.
- ⚠️ Edits land on disk slightly after the tool returns: a `git diff` taken at once can be empty.
- Serena caches under the ignored `.serena/` and may report references inside ignored `data/` copies.
- Fallback order when Serena is unavailable: CodeGraph → Pylance usages → grep.

### GSD ([`examples/gsd/`](./examples/gsd/)) — Claude Code only
Phase-based cycle with versioned `.planning/` state and specialised subagents. **No Copilot port.**
Nearest Copilot pieces:
```
/plan, --plan, Shift+Tab           -> discuss gate -> plan (enforced at the tool layer)
--plan --mode autopilot            -> plan-then-execute, bounded by --max-autopilot-continues / --max-ai-credits
/fleet                             -> wave-parallel plan execution
.github/agents/{planner,executor,verifier}.agent.md -> the gsd-* roles
agentStop hook decision: block     -> "verify before stop" gate
VS Code handoffs (Local only)      -> plan -> implement buttons
Spec Kit (github/spec-kit)         -> spec-driven templates; third-party coverage only, version UNVERIFIED
data/changes/                      -> the state store (not .planning/)
```
> **Honesty:** this project does not run GSD; it uses the 11-stage workflow + `data/changes/`. GSD makes
> more sense in a multi-component greenfield.

---

## 14. Transferring the methodology

Material: [`docs/ai-agents-code-methodology/`](./docs/ai-agents-code-methodology/) —
[`COPILOT_ADAPTATION.md`](./docs/ai-agents-code-methodology/COPILOT_ADAPTATION.md) (rewritten for the
2026 surfaces) + ready-to-copy surface [`copilot/`](./docs/ai-agents-code-methodology/copilot/) +
[`templates/COPILOT_WORKING_AGREEMENT_TEMPLATE.md`](./docs/ai-agents-code-methodology/templates/COPILOT_WORKING_AGREEMENT_TEMPLATE.md).

**What travels unchanged:** plan → agreement → implement · verify against the consumer's contract · solve
the general class · durable trail · the human owns everything external.

**What changes — the surface:**
```
CLAUDE.md (+ hierarchy)          -> AGENTS.md + .github/copilot-instructions.md + .github/instructions/*.instructions.md
                                    (CLI also reads CLAUDE.md and .claude/rules — but NOT ~/.claude/CLAUDE.md)
~/.claude/skills/                -> .github/skills/ or ~/.copilot/skills/ (CLI does NOT read ~/.claude/skills)
settings.json permissions        -> no committed allow/deny: hook + --deny-tool + managed settings
Hooks (PreToolUse, exit 2)       -> .github/hooks/*.json preToolUse; exit 2 / permissionDecision deny
Plan mode                        -> /plan, --plan (enforced)
Subagents + Agent Teams          -> .github/agents/*.agent.md + built-ins + /fleet + sidekicks
claude -p                        -> copilot -p (+ --trust-folder in CI)
Auto-memory / claude-mem         -> Copilot Memory (cloud, 28-day expiry) / VS Code /memories / /chronicle — complements only
.mcp.json                        -> .mcp.json with "tools" required (+ .vscode/mcp.json "servers" for Local)
Agent SDK                        -> @github/copilot-sdk / github-copilot-sdk
```

**The rule that became enforceable — and the two new holes.** "No direct merge/deploy by the agent" used to
be policy only. Now: a committed `preToolUse` deny hook (works in CLI, cloud agent, VS Code Copilot harness),
`--deny-tool` flags (deny beats `--yolo`), `permissions.disableBypassPermissionsMode`, structural cloud-agent
limits (own `copilot/` branch, cannot approve or merge) and CODEOWNERS on `.github/hooks/**`,
`.github/agents/**`, `.github/skills/**`, `.mcp.json`, `AGENTS.md`. New holes to close: **CLI `/pr auto` and
`/pr automerge`** (hook coverage UNVERIFIED → human-only in instructions, test on your build), and
**Copilot code review approvals** (preview, off by default) → **keep off**.

**Bootstrap in a target repo:** see
[`TRANSFER_AND_BOOTSTRAP.md`](./docs/ai-agents-code-methodology/TRANSFER_AND_BOOTSTRAP.md) and
`scripts/bootstrap-new-repo.ps1.txt` + `scripts/bootstrap-copilot-repo.ps1.txt` (shipped as `.ps1.txt` to
dodge email active-content blocking).

**Fallback without a ticket knowledge graph** (80% of the value): newest-first `STATUS.md` + per-ticket
folders · lexical search by symptom/symbol/contract field · commit history (file overlap) · a short "danger
zones" section. Copilot Memory and `/chronicle` can help recall — never as the record.

**First-day checklist:** `STATUS.md` · 3–5 invariants in `SHARP_EDGES.md` · the output contract · scoped
test commands · install the hook and run its test · one complete issue RED→GREEN with contract verification.

---

## 15. Machine sync

Two mechanisms that don't compete: **(A)** tarball + USB for a full machine bring-up; **(B)** shared object
storage (S3) for the day-to-day engineering record.

### A. Full bring-up: tarball + USB (asymmetric)
Sanitised walkthrough: [`examples/methodology/machine-sync.md`](./examples/methodology/machine-sync.md);
runbooks in [`docs/synchro/`](./docs/synchro/). Adaptation:
```
Claude Code                          Copilot
Pointer in CLAUDE.md                 Pointer in AGENTS.md / an .instructions.md
Bundle ~/.claude (skills + memory)   Bundle ~/.copilot (skills, agents, hooks, mcp-config.json, settings.json);
                                     Copilot Memory is cloud-side and not a file — decide explicitly what travels
codegraph MCP in ~/.claude.json      Re-pin --path in ~/.copilot/mcp-config.json (absolute path on the laptop)
/kg-refresh Claude skill             kg-refresh skill in ~/.copilot/skills + the same kg_refresh.sh
```
⚠️ Do not tar `~/.copilot/config.json` blindly: it holds auth and `trustedFolders` state for *that* machine;
re-login and re-trust on the target. **Outbound = full copy; inbound = delta only** (`git fetch` + a small
tarball of the gitignored `data/`, landed by an agent following an `INSTRUCTIONS.md` written for it, with
backups first and STOP on doubt). The agent never pushes, merges or opens PRs during landing — the hook
enforces it.

### B. The shared record: `data/` over S3
Full runbook: [`docs/synchro/s3-sync/README.md`](./docs/synchro/s3-sync/README.md); scripts:
[`examples/methodology/s3-sync/`](./examples/methodology/s3-sync/).
```bash
./data-pull.sh            # preview  ->  ./data-pull.sh --go
./data-push.sh            # preview  ->  ./data-push.sh --go
./mount-data.sh           # live shared view, READ-ONLY
./validate.sh             # a machine isn't set up until this prints MACHINE READY
```

| Rule | Why |
|---|---|
| Scope grows in reviewed phases | Every widening is a security event: scan first, canary the scanner, then reconcile. |
| Write via sync, read via read-only mount | Object storage has no locking and no atomic rename. |
| Dry-run by default; `--delete` separate | An exact mirror from a stale view erases a teammate's push. |
| Deliberate deletion = a tool with a tombstone | `delete.sh` (publisher only) + `_deletions.jsonl`; a push that cannot read the list refuses. |
| Docs = source; the graph is derived — **per file, not per folder** | A hand-authored names overlay lives inside the generated tree; treat it as source. |
| Pairs move together | Stamp the overlay with a fingerprint of its graph; fail loudly on mismatch. |
| Coordinate without locks | One request file per contributor in a queue. |
| ⚠️ Recovery expires (30 days) | Pull before you edit, push what you changed, report losses within the month. |
| Shared ledgers are append-only | Rewriting one silently drops someone else's line. |
| ⚠️ Guard BOTH directions | A pull clobbers you; a push clobbers your colleague — refuse (exit 4), don't warn. |
| One writer per per-machine file | Otherwise the first symptom is a wrong conclusion about a person. |
| A guard that cries wolf teaches overrides | False-positive rate is a safety property. |

**The machine has a role.** `MACHINE_NAME` / `MACHINE_ROLE` in `config.env`, `identity.sh --write`
generates a machine-local `IDENTITY.md`, and the always-loaded instructions point at it. Under Copilot, load
it through `~/.copilot/copilot-instructions.md` (personal, machine-local) or a `sessionStart` hook.

**And the habit needs a mechanism.** `day start` / `day end` packaged as a role-aware skill
([`examples/skills-plugins/`](./examples/skills-plugins/)) — and under the Copilot CLI, optionally *forced*
by a `sessionStart` prompt hook. Every dangerous step is gated behind a question it answers first; where
the answer is ambiguous it stops and asks.

> ⚠️⚠️ **A safety guard can silently disable the instrument that proves the habit.** A pre-pull snapshot
> installed its own `trap … EXIT`; bash keeps one EXIT trap, so it replaced the one that wrote the activity
> log — dry runs kept logging, every real pull went unrecorded for two days. Ask what else claims the same
> single-slot resource; the real path and the rehearsal path are different code paths.

> ⚠️ **Measure an optimisation before you quote it.** Predicted "minutes to seconds"; measured 212 s → 123 s.

> **Field test 2026-10-28 (Copilot, real workday).** `day start` found that `LOCAL_DATA` in `config.env`
> pointed at a different checkout **before** any pull; after a local-only fix, `IDENTITY.md` was regenerated,
> the `changes` dry run found nothing to upload, and the pull ran with a pre-pull snapshot, moved
> upstream-deleted files aside and used no `--delete`. `day end` ran only as a dry-run publish preview plus
> the read-only activity ledger. That preview listed two `knowledge-graph/_corpus` files that would have
> uploaded despite the contributor rule: a real publish must exclude them, write the STATUS row first, and
> never use `--delete`. A local `canary_leadin_diff.json` overwritten by a re-run was restored from the bucket
> with a read-only `s3 cp`. See [§17](#17-field-test-2026-10-28).

---

# SESSION 2 CONTINUED — The ticket knowledge graph (graphify)

## 16. Ticket knowledge graph

**Technology: `graphify` — not CodeGraph.** CodeGraph indexes the *code*; this graph indexes the
**project's memory** — per-ticket write-ups, sharp edges, runbooks, memory notes. Pipeline:
[`docs/knowledge-graph/`](./docs/knowledge-graph/); narrative: [`docs/KNOWLEDGE_GRAPH.md`](./docs/KNOWLEDGE_GRAPH.md).

| Piece | What it is |
|---|---|
| `kg` skill | `explain` / `path` / `find` — deterministic, **no LLM** |
| `kg-refresh` skill | `prepare` → semantic extraction (agent step) → `finalize` |
| [`kg_query.sh`](./docs/knowledge-graph/kg_query.sh) | Wrapper over `graphify explain`/`path` on `output/graph.json` + `find` |
| [`kg_refresh.sh`](./docs/knowledge-graph/kg_refresh.sh) | Deterministic bookends: `prepare` / `finalize` / `bootstrap` / `snapshot-memory` / `restore-memory` |
| `build_manifest.py` / `stage_corpus.py` | Enumerate and stage the corpus with provenance-preserving names |
| `test_kg_*.py` | The bookends are tested — infrastructure, not a one-off |

> **Sanitisation note.** The interactive graph bundled under `docs/knowledge-graph/output/` is an older,
> sanitised snapshot (507 nodes · 672 edges · 35 communities). The deck screenshot
> [`presentation/kg_graph.png`](./presentation/kg_graph.png) is refreshed from the ILS_2 graph snapshot:
> 3,921 nodes · 8,508 links · 178 communities · 73 hyperedges (94.3% `EXTRACTED` links). It shows
> topology only; labels and metadata are omitted because the source graph contains internal identifiers.
> Do not copy the source graph output into this course repository.

```bash
kg_refresh.sh prepare        # manifest -> stage _corpus/ -> scratch OUTSIDE the repo
                              # semantic extraction (agent, parallel subagents) -> HTML/JSON/report
kg_refresh.sh finalize       # copy artifacts to output/ + leak check
kg explain <ticket|topic>    # neighbours — the most common use
kg path <A> <B>              # shortest path
kg find <substr>             # discover a node's exact name
```

**Under Copilot.** `kg` is deterministic shell — a direct port: `.github/skills/kg/SKILL.md` (or
`~/.copilot/skills/kg/`, since the CLI does not read `~/.claude/skills`). `kg-refresh` wraps graphify's
semantic step, which in Claude Code fans out to parallel subagents. Under the Copilot CLI the same fan-out
maps to built-in subagents via the `task` tool or `/fleet` (concurrency by plan: Pro 4, Max 8, Business 16);
VS Code Local uses `runSubagent`. Or keep running the semantic step from Claude Code — the bookends don't
care which agent ran in between. The **publisher-only guard stays in the script**, not in the prompt. Not a
cloud-agent task: the corpus lives in gitignored `data/`, which the cloud agent never sees.

**Gotcha that holds the pipeline together:** graphify honours `.gitignore` and all of `data/` is ignored →
the corpus is staged in a scratch outside the repo and artifacts are copied back. That's why `kg-refresh` is
a skill, not a script.

**Hook-in:** stage 1 (Orient) of `00-methodology-core.instructions.md`: run `kg explain <ticket|topic>`
before grepping `data/changes/`. `EXTRACTED` = reliable; `INFERRED` = a lead to verify. The real gain is
recall in dense zones.

> ⚠️ **Field note (2026-10-28).** `/kg count edges` in Copilot returned graph-size metadata (3,921 nodes /
> 8,508 edges), but `kg_query.sh` itself supports only `explain`, `path` and `find`. Calling the script with
> `count edges` is not a valid count test; do not present it as one. `kg_query.sh find <substr>` worked
> (22 matches). Do not refresh the graph from a contributor machine.

> ⚠️ **"Derived" is a property of the file, not of the folder.** Inside the generated tree lives a
> hand-authored file — the curated community names — that nothing regenerates; on a real rebuild **under 1%**
> survived. Classify per file: source / derived / authored-inside-derived (treat as source). Stamp the
> overlay with a fingerprint of its graph; a per-file sync cannot express atomicity.

> **Cost — honest.** "No LLM at query time" is not "free": the reasoning is paid once at build time; each
> `kg` query is a deterministic lookup whose only cost is the agent reading a short output. Paid once,
> collected on every use — from any of the four agents.

---

## 17. Field test 2026-10-28

The methodology and all its skills were run with **GitHub Copilot agent in VS Code** on a real
non-production workday, with some deliberate restrictions. Full reports:
[`COPILOT_METHODOLOGY_LIVE_VALIDATION_2026-10-28.md`](./docs/ai-agents-code-methodology/field-reports/COPILOT_METHODOLOGY_LIVE_VALIDATION_2026-10-28.md)
(skill by skill) and
[`COPILOT_SST-6880_METHOD_REPLAY_2026-10-28.md`](./docs/ai-agents-code-methodology/field-reports/COPILOT_SST-6880_METHOD_REPLAY_2026-10-28.md)
(one ticket replayed through the gates). These are **measured** results that replace the earlier
"parity is expected" claim. They are not a statement that anything was published, merged or pushed.

### Skill by skill

| Skill / tool | Result | What actually ran | Limits |
|---|---|---|---|
| `day` start | PASS, scoped | Identity + non-prod AWS checked; stale sync target fixed (local only, user-authorised); dry run clean; protected pull with snapshot, no `--delete` | `git fetch` blocked (no non-interactive GitHub credentials) |
| `day` end | MINIMAL | Dry-run publish preview + read-only activity ledger | No upload; preview flagged 2 `_corpus` files to exclude |
| `evidence` | PASS, live read-only | 2 dev runs: source, highlighted DOCX, raw Lambda result, scrubbed log; source hashes matched | Not the consumer `get-sl-upload-status` contract (needs an app session) |
| `preview` / viewer | PASS, captured outputs | Local frontend + mock APIs rendered the captured results; containers removed afterwards | Deliberately not the normal preview command, which re-extracts and can spend model calls |
| `atlassian` | PASS | 62-test mocked suite; 3 approved read-only GETs (2 Jira, 1 Confluence metadata) | No page bodies, comments, exports or writes |
| `kg` | PASS, bounded | `find` with 22 matches; `/kg count edges` returned metadata only | See the §16 note on `count` |
| `kg-refresh` | OUT OF SCOPE | — | Excluded by the user |
| `methodology-plan` | PARTIAL | Synthetic six-part plan; gates 1–5 replayed on the real ticket | Full template agreement not done |
| `sanitise-diff` | PASS | Disposable fixture, then the real fix diff (134 added lines) in a disposable repo | 1 internal ticket id in a test docstring (repo convention) |
| CodeGraph | PASS, bounded | One-symbol lookup: one file with callers and dependencies | Navigation, not test coverage |
| Serena | PASS, live | See [§13](#13-the-methods-tools) | First call slow; edits land late |
| Context7 | NOT EXERCISED | Connected according to the user | No tool exposed in the session |

### One ticket, replayed

On a backup clone, branch `replay/…-pre-fix` cut at the commit before the original fix:

| Gate | Result |
|---|---|
| Root cause | Same as the earlier agents: `is_potential_title` rejects a 13-word title (`TITLE_LEN_MAX` = 13), and `_underlined_lead_in_titles` stops at a non-underlined typed number run (`59.`), so `_is_acceptable_title` never rescues it. **Not blind**: the fix plan had been read earlier. |
| RED | 14 new tests: 5 fail on the target behaviour (assertions, not import errors), 9 guards pass |
| GREEN | One function, ~18 added lines + 2 regexes, no threshold/prompt/config change; 14/14 new + 17/17 existing = 31 pass |
| Blast radius | No-LLM lead-in diff over the local corpus, canary first: 8 files gain lead-ins, exactly 1 outcome-changing entry; counts equal the ticket's recorded sweep |
| Deployed image | Real LLM re-extract in the deployed image (branch mounted read-only, on a copy): 94 provisions, all 6 checks pass |
| Regression | Related subset: 235 passed, 1 skipped, 0 failed. Full suite: 1552 → 1566 passed (+14), same 3 failures, same 5 collection errors (broker 0.1.3 vs v0.1.5 in the host venv; those files did not run) |
| Sanitise | 0 names (11-entry list), secrets, account ids, e-mails or attribution; 1 internal ticket id |
| Close | Fix and tests reverted and archived (`fix.diff`, test as `.txt`); replay branch deleted; nothing committed or pushed |

Still owed in the real flow: the re-upload check on the deployed function after a merge, and a blind run on
an unseen ticket.

### Practical findings

- Cold imports of the extractor from `/mnt/d` take ~5 min (I/O bound; ~1.5–2 min once cached). A short tool
  timeout there is a tooling limit, not a defect.
- Local runs need dummy `SQS_LAMBDACLIENTSL` / `SQS_MATTERRPCSERVICE` values; no network is used.
- The extractor rewrites the DOCX it opens: always run on a copy, and check the original's mtime afterwards.
- When the host venv lacks a dependency version, run inside the deployed-image build with the branch mounted
  read-only, as the ticket's own second run did.
- Re-running a corpus diff overwrites the recorded output file: keep a byte copy first.
- Evidence folders contain customer documents. They stay local and ignored; never copy them into slides
  or commits.

---

## A. Equivalence table: Claude Code → Cursor → Copilot

| Concept | Claude Code | Cursor | GitHub Copilot (Oct 2026) |
|---|---|---|---|
| CLI / headless | `claude -p` | `agent -p --trust [--force]` | `copilot -p "…" -s [--allow-tool …] [--trust-folder]`; piped stdin OK |
| Cloud async agent | (web / remote) | Background/Cloud Agents | **Copilot cloud agent** (issue assign, `/delegate`, `&`, `POST /agents/repos/{o}/{r}/tasks`) |
| Always-loaded memory | `CLAUDE.md` | `AGENTS.md` + `.cursor/rules` `alwaysApply` | `AGENTS.md` and/or `.github/copilot-instructions.md` (CLI also `CLAUDE.md`/`GEMINI.md`) |
| Scoped rules | `.claude/rules` `paths:` | `.mdc` `globs` | `.github/instructions/*.instructions.md` `applyTo` (+ `excludeAgent`); CLI also `.claude/rules` |
| Eager import | `@path` | `@file` in `.mdc` | `@path` in AGENTS.md/CLAUDE.md/copilot-instructions.md (CLI) |
| Personal memory | `~/.claude/CLAUDE.md` | user rules | `~/.copilot/copilot-instructions.md`, `~/.copilot/instructions/` |
| Auto memory | `MEMORY.md` / claude-mem | Cursor Memories | Copilot Memory (cloud, preview) / VS Code `/memories` / `/chronicle` |
| Reusable prompts | slash commands / skills | skills | skills (all surfaces); prompt files (VS Code Local, VS, JetBrains) |
| Permissions | `settings.json` `permissions.allow/deny` | `permissions.json` | `--allow-tool/--deny-tool`; saved `permissions-config.json`; repo-level only via **managed** settings; VS Code `chat.tools.*` |
| Bypass mode | `--dangerously-skip-permissions` | `--yolo`/`--force` | `--yolo`/`--allow-all`; blockable via `permissions.disableBypassPermissionsMode` |
| Sandbox | sandbox settings | — | `/sandbox`, `--sandbox`, `sandbox.*` (GA 2026-10-07); VS Code `chat.agent.sandbox.enabled` |
| Trust | workspace trust | Workspace Trust / `--trust` | `trustedFolders`, `--trust-folder`, `--add-dir` |
| Sessions | `--resume`/`--continue` | chats, CLI sessions | `--resume`/`--continue`, `/fork`, `/rewind`, `/share`, `/remote`, `/delegate` |
| Context view / compaction | `/context`, `/compact` | context ring, `/summarize` | `/context`, `/compact [focus]`, auto at ~80% |
| Prompt caching control | API `cache_control` only | none | none; billed cached-input/cache-write; VS Code Cache Explorer (diagnose) |
| MCP config | `.mcp.json` | `.cursor/mcp.json` | `.mcp.json`/`.github/mcp.json` + `~/.copilot/mcp-config.json` (`tools` required); `.vscode/mcp.json` (`servers`); cloud: repo settings |
| Skills | `.claude/skills`, `~/.claude/skills` | `.cursor/skills` (+ `.claude/skills`) | `.github/skills`, `.claude/skills`, `.agents/skills`; `~/.copilot/skills` (VS Code also `~/.claude/skills`) |
| Plugins | `/plugin` | Marketplace UI | `copilot plugin install`; `awesome-copilot`; reads `.claude-plugin/` |
| Subagents | `.claude/agents/*.md` | `.cursor/agents/*.md` | `.github/agents/*.agent.md`, `~/.copilot/agents/` (CLI also `.claude/agents/`) + 7 built-ins |
| Parallel / teams | Agent Teams | Cloud Agents (no messaging) | `/fleet`, background subagents + `write_agent`, sidekicks, `/delegate` |
| Hooks | `settings.json` hooks | `.cursor/hooks.json` | `.github/hooks/*.json` `{version:1}` camelCase; also `.claude/settings.json`; VS Code Local schema differs |
| Block a command | PreToolUse exit 2 / deny | `permission:"deny"` / exit 2 | `preToolUse` `permissionDecision:"deny"` / **exit 2** (crash = fail-closed; timeout = fail-open) |
| CI | `claude -p` in Actions | Cursor SDK / Bugbot | `copilot -p` (`copilot-requests: write`), Agentic Workflows, Automations |
| SDK | Agent SDK | `@cursor/sdk` | `@github/copilot-sdk` (+ Python/Go/.NET/Java) |
| PR review bot | — | Bugbot | Copilot code review (rulesets; `REVIEW.md`; approvals preview — keep off) |
| Plan mode | plan mode | Plan mode | `/plan`, `--plan`, Shift+Tab (enforced) |
| GSD | GSD plugin | n/a | n/a: plan mode + `/fleet` + custom agents (+ Spec Kit) |

## B. Gotchas that changed in 2025–2026

1. **Coding agent → cloud agent** (docs URLs now `/cloud-agent/`).
2. **Premium requests → AI Credits** (2026-06-01).
3. **Copilot CLI GA 2026-02-25** — not the retired `gh copilot`.
4. CLI user settings moved to `~/.copilot/settings.json`; `config.json` is internal state; hooks are no
   longer read from it.
5. VS Code harness split; `chat.agentSkillsLocations` / `chat.instructionsFilesLocations` are deprecated
   and not read by the Copilot harness.
6. VS Code drops skills whose `name` ≠ folder; the CLI ignores `~/.claude/skills`.
7. `AGENTS.md` nesting differs per surface.
8. No committed allow/deny in the CLI → hooks.
9. `-p` skips repo hooks / workspace MCP in untrusted folders.
10. MCP `tools` required; `.vscode/mcp.json` uses `servers`; `${input:}` not forwarded; cloud agent: no OAuth
    remote, resources or prompts.
11. Playwright, GitHub, fetch, time are built into the CLI.
12. Hook timeouts fail open.
13. `/pr auto` / `/pr automerge` exist; code review can approve (preview).
14. Code review reads config from the PR head branch.
15. Docs contradictions: subagent depth 6 vs 4; built-in default models vs the default-model table.
16. Sandbox on Linux/WSL2 needs `bubblewrap` + `socat`; VS Code sandbox allows network by default.
17. Copilot Memory expires unused entries after 28 days.
18. Content exclusions apply in the CLI and Copilot app (GA 2026-09-02, Business/Enterprise).

---

## Sources

**Verified 2026-10-17 — Copilot moves fast, re-check before reuse.** Full per-claim citations:
[`docs/research/COPILOT_FINDINGS_2026-10-17.md`](./docs/research/COPILOT_FINDINGS_2026-10-17.md).

- Copilot CLI command reference — <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference>
- Install / authenticate / configure the CLI — <https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli>
- Allowing tools — <https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/allowing-tools>
- Custom instructions support — <https://docs.github.com/en/copilot/reference/custom-instructions-support>
- Repository instructions — <https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions>
- Hooks reference — <https://docs.github.com/en/copilot/reference/hooks-reference>
- Custom agents configuration — <https://docs.github.com/en/copilot/reference/custom-agents-configuration>
- About agent skills — <https://docs.github.com/en/copilot/concepts/agents/about-agent-skills>
- Context management (CLI) — <https://docs.github.com/en/copilot/concepts/agents/copilot-cli/context-management>
- Cloud agent risks and mitigations — <https://docs.github.com/en/copilot/concepts/agents/cloud-agent/risks-and-mitigations>
- Cloud agent environment (`copilot-setup-steps.yml`) — <https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/customize-the-agent-environment>
- Cloud agent via the API — <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-via-the-api>
- MCP for cloud agent — <https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/configure-mcp-servers>
- Code review configuration — <https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/configure-code-review>
- Copilot CLI in Actions — <https://docs.github.com/en/copilot/how-tos/copilot-cli/automate-copilot-cli/automate-with-actions>
- Billing (AI Credits) — <https://docs.github.com/en/copilot/concepts/billing-and-usage/individuals/billing> · models and pricing <https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing>
- Copilot Memory — <https://docs.github.com/en/copilot/concepts/agents/copilot-memory>
- VS Code agent harnesses — <https://code.visualstudio.com/docs/agents/concepts/agent-harnesses>
- VS Code hooks — <https://code.visualstudio.com/docs/agent-customization/hooks> · reference <https://code.visualstudio.com/docs/agents/reference/hooks-reference>
- VS Code MCP configuration — <https://code.visualstudio.com/docs/agents/reference/mcp-configuration>
- VS Code agent skills — <https://code.visualstudio.com/docs/agent-customization/agent-skills>
- VS Code Cache Explorer — <https://code.visualstudio.com/docs/agents/agent-troubleshooting/cache-explorer>
- Changelog: CLI GA — <https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/> · sandbox GA — <https://github.blog/changelog/2026-10-07-local-sandboxing-for-github-copilot-now-generally-available/> · agent skills — <https://github.blog/changelog/2025-12-18-github-copilot-now-supports-agent-skills/>
- Tools: CodeGraph <https://colbymchenry.github.io/codegraph/> · Serena <https://github.com/oraios/serena> · graphify <https://graphify.net> · Context7 <https://context7.com> · MCP <https://modelcontextprotocol.io> · GSD <https://github.com/tomascortereal/claude-code-setup> · Spec Kit <https://github.com/github/spec-kit> (third-party coverage only)
