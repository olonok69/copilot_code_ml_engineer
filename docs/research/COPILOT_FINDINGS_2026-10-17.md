> **Provenance.** Raw research notes behind Part 1 of this course, copied verbatim except for local paths and
> machine-specific names (sanitised). Verified **2026-10-17** — Copilot moves fast, re-check before reuse.
> The raw fetched pages are not redistributed; every claim cites its docs page (`GH:` / `VSC:` prefixes below).

# GitHub Copilot — research findings for "GitHub Copilot — a course in three parts"

Research date: **2026-10-17**. Every docs.github.com page below was fetched on 2026-10-17 through the docs
Markdown API (`https://docs.github.com/api/article/body?pathname=<path>`). I did not use rendered HTML.
VS Code pages were fetched the same day from `microsoft/vscode-docs@main`. Those carry `DateApproved: 10/14/2026` or
`10/16/2026`. Their public URLs are `https://code.visualstudio.com/docs/<same path>` (checked: HTTP 200).
URL shorthand used below:
- `GH:` = `https://docs.github.com/en/copilot/`
- `VSC:` = `https://code.visualstudio.com/docs/`

Wording rule: "NOT DOCUMENTED / UNVERIFIED" means I could not find it in the current docs. Nothing has been made up.

---

## 0. Big picture: what changed and what the surfaces are (read first)

**Product names changed.**
- "Copilot coding agent" is now **"Copilot cloud agent"**. The docs, URLs (`.../cloud-agent/...`) and hooks reference all use the new name.
- **Billing moved from premium requests to GitHub AI Credits on 2026-06-01.**
  - Source: GH:reference/copilot-billing/request-based-billing-legacy/what-changed-with-billing

**Surfaces covered in this course.**

| Surface | What it is | Primary docs |
|---|---|---|
| **Copilot CLI** (`copilot`) | Terminal agent. npm package `@github/copilot`. GA 2026-02-25 (public preview since Sep 2025). | GH:how-tos/copilot-cli · GH:reference/copilot-cli-reference/cli-command-reference · changelog https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/ |
| **VS Code agent** | Has **agent harnesses**: **Copilot** (shared Copilot SDK runtime, same engine as the CLI, runs in "Agent Host"), **Local** (classic VS Code agent mode in the extension host), **Claude**, **Codex**, plus a **Cloud** target. | VSC:agents/concepts/agent-harnesses |
| **JetBrains agent mode** | Agent mode and MCP are supported. Skills, custom agents, custom instructions and prompt files are **Preview**. | GH:reference/copilot-feature-matrix |
| **Copilot cloud agent** | Cloud agent (formerly coding agent). You give it an issue, prompt, API call or automation. It works in an ephemeral GitHub Actions Linux sandbox and opens a draft PR. | GH:concepts/agents/cloud-agent/risks-and-mitigations · GH:how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-on-github |
| **Copilot code review** | PR reviewer on github.com and in IDEs. Can be automatic through rulesets. | GH:how-tos/use-copilot-agents/use-code-review |
| **Copilot on github.com** | Chat, the Agents page `github.com/copilot/agents`, Spaces. | same |
| (also) **GitHub Copilot app** | Desktop app. `copilot app` / `/app` | GH:get-started/quickstart-copilot-app |

> ⚠️ **The most important structural fact for the course: VS Code has two different Copilot engines.**
> - The **Copilot harness** uses the same runtime as the CLI. It shares `~/.copilot/*`, `.github/hooks` (CLI schema), `.mcp.json`, skills and agents.
> - The **Local harness** has its own settings (`chat.*`), its own hook schema, prompt files and handoffs.
> - Prompt files and `handoffs` work **only in Local**.
>
> Sources: VSC:agent-customization/hooks, VSC:agent-customization/prompt-files, VSC:agents/reference/custom-agent-file-reference.

---

## 1. Install / auth / CLI usage / models / billing

### Install
Source: GH:how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli

```bash
npm install -g @github/copilot                  # Node.js 22+; prerelease: @github/copilot@prerelease
brew install --cask copilot-cli                 # macOS/Linux
winget install GitHub.Copilot                   # Windows (PowerShell 6+ required)
curl -fsSL https://gh.io/copilot-install | bash # macOS/Linux script; PREFIX=, VERSION= env vars
copilot update                                  # or /update; auto-update on by default (COPILOT_AUTO_UPDATE=false)
```

### Auth
Sources: GH:reference/copilot-cli-reference/cli-command-reference (§copilot login), and the install page.

- **Interactive:** `copilot login` or `/login`. Flags:
  - `--host https://example.ghe.com`
  - `--web-flow`
  - `--device-code` (the default on remote terminals and in CI)
  - `--with-token` (reads the token from stdin)
- **Environment tokens, in precedence order:** `COPILOT_GITHUB_TOKEN` > `GH_TOKEN` > `GITHUB_TOKEN`.
- **PAT:** must be a *fine-grained, user-owned* PAT with the **"Copilot Requests"** account permission.
- **Actions with `GITHUB_TOKEN`:** set workflow permission `copilot-requests: write`. The org policy "Allow use of Copilot CLI billed to the organization" must also be on.
  - Source: GH:how-tos/copilot-cli/use-copilot-cli-in-actions

### Headless / non-interactive
Sources: GH:how-tos/copilot-cli/automate-copilot-cli/run-cli-programmatically, plus the command reference.

```bash
copilot -p "Explain ./complex.ts" -s                     # -p/--prompt exits after completion; -s/--silent = only the answer
echo "Explain ./complex.ts" | copilot                    # piped stdin also works (ignored if -p given)
copilot -p '...' -s --allow-tool='shell(git:*)' --deny-tool='shell(git push)' --no-ask-user --model=claude-sonnet-5.5
copilot -p '...' --output-format=json                    # JSONL events
copilot -p '...' --share=./report.md | --share-gist      # export transcript
copilot -i "prompt"                                      # interactive + auto-run first prompt
copilot --autopilot --yolo --max-autopilot-continues 10 -p "..."   # local autonomous run
copilot --plan --mode autopilot -p "..."                 # plan-then-autopilot (env COPILOT_PLAN_THEN_AUTOPILOT=1)
copilot -p "..." --fleet                                 # parallel subagent orchestration
copilot --resume=SESSION-ID | --continue | -n NAME       # sessions (§4)
copilot -w [NAME]  /  -C DIR  /  --add-dir=PATH          # worktree, chdir, extra trusted dirs
copilot -p "..." --trust-folder                          # trust repo hooks/MCP/plugins for this one -p run only
copilot -p "..." --max-ai-credits=5                      # soft per-response spend cap
```

**Key CLI subcommands:**

| Command | Purpose |
|---|---|
| `copilot init` | Writes `.github/copilot-instructions.md` |
| `copilot mcp list\|get\|add\|enable\|disable\|remove` | Manage MCP servers |
| `copilot skill list\|add [--project]\|remove\|enable\|disable` | Manage skills |
| `copilot plugin …` | Manage plugins |
| `copilot config [--repo\|--local] KEY VALUE` | Read or change settings |
| `copilot instruction list` | List instruction sources |
| `copilot help permissions\|sandbox\|config\|…` | Built-in help topics |
| `copilot workflow run` | Run an extension-registered workflow |

**Useful slash commands** (full table in the command reference):
- **Model and context:** `/model`, `/context`, `/compact [focus]`, `/usage`, `/limits`
- **Agents and planning:** `/agent`, `/subagents`, `/plan`, `/autopilot` (alias `/goal`), `/fleet`, `/delegate` (`&` prefix = delegate)
- **Review:** `/review`, `/security-review`, `/rubber-duck`
- **Customization:** `/skills`, `/mcp`, `/plugin`, `/instructions`, `/env`
- **Permissions:** `/permissions [default|assisted|allow-all|show|reset]` (`/allow-all` and `/yolo` are aliases), `/sandbox`
- **Sessions:** `/resume`, `/session [checkpoints|…]`, `/rewind` (alias `/undo`), `/fork`, `/share`, `/chronicle`
- **Remote and PRs:** `/remote`, `/pr [view|create|fix|auto|automerge]`
- **Research:** `/research`
- **Experimental only:** `/every`, `/after`

### Models
Sources: GH:reference/copilot-cli-reference/cli-command-reference#supported-models and GH:reference/ai-models/supported-models

CLI table as of 2026-10-17:

| Model | Note |
|---|---|
| `claude-sonnet-5.5` | Default |
| `gpt-5.4` | |
| `gpt-6.1-sol`, `gpt-6-astra`, `gpt-6-luna` | Opt-in |
| `claude-opus-5.5` | |
| `claude-haiku-5.5`, `claude-haiku-4.5` | |
| `gpt-5.3-codex` | |
| `gemini-3.7-flash`, `gemini-3.8-flash` | |
| `auto` | Copilot picks the model |

- **Selection:**
  - `--model=` or `COPILOT_MODEL`
  - `/model [--session|--global|--repo|--local] [MODEL|auto TIER]` (tiers: `efficiency|balance|intelligence`)
  - `settings.json` `"model"`
  - repo `.github/copilot/settings.json` `"model"` (applies only in a trusted folder)
  - repo allowlist `.github/allowed_models.txt`
  - Effort: `--effort=low|medium|high|xhigh|max`
  - Long context: `--context long_context`
- **1M-token context window:** available only in **VS Code and CLI**, on supported models. It costs more credits.
- **Auto model selection:** paid plans get a 10% discount when using Auto.
  - Source: GH:concepts/billing-and-usage/individuals/billing
- **BYOK:** `providers.json` / `COPILOT_PROVIDERS_CONFIG` (CLI).

### Billing basics
Sources: GH:concepts/billing-and-usage/individuals/billing and GH:reference/copilot-billing/models-and-pricing

- **Since 2026-06-01:** usage-based billing in **GitHub AI Credits**. 1 credit = $0.01. Cost = per-token price × input, output, cached-input and cache-write tokens.
- **Monthly allowances:**

  | Plan | Price | Credits (base + flex) |
  |---|---|---|
  | Pro | $10 | 1,500 (1,000 + 500) |
  | Pro+ | $39 | 7,000 (3,900 + 3,100) |
  | Max | $100 | 20,000 (10,000 + 10,000) |

- **Free / Student:** Auto model selection only.
- **Business / Enterprise:** pooled per-user allowances.
- **Not billed:** code completions and next-edit suggestions.
- **"Premium requests" and multipliers are LEGACY.** They now apply only to annual Pro/Pro+ plans that stayed on the old model.

---

## 2. Memory / instructions

### File types and surface support
Source: GH:reference/custom-instructions-support

| File | CLI | VS Code (Copilot/Local) | Cloud agent | Code review (github.com) | JetBrains Chat |
|---|---|---|---|---|---|
| `.github/copilot-instructions.md` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `.github/instructions/**/*.instructions.md` (`applyTo`) | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AGENTS.md` | ✓ | ✓ | ✓ | ✓ | ✗ (Chat); ✓ via cloud agent |
| `CLAUDE.md` / `GEMINI.md` | ✓ | Claude harness / Local (`chat.useClaudeMdFile`) | ✓ | ✓ (+ `REVIEW.md`) | — |
| Personal | `~/.copilot/copilot-instructions.md`, `~/.copilot/instructions/**/*.instructions.md` | `~/.copilot/instructions` (Copilot harness) / profile (Local) | — | — | ✓ |
| Organization instructions | — | ✓ (`github.copilot.chat.organizationInstructions.enabled`) | ✓ | ✓ | — |

### CLI loading rules
Source: GH:reference/copilot-cli-reference/cli-command-reference#custom-instructions-locations

- All sources load **simultaneously and are merged**:
  - `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`, `.github/instructions/**/*.instructions.md`, `.claude/rules/**/*.md` and `.github/copilot-instructions.md`. Each is read **in the Git root and in the cwd**.
  - Plus `$HOME/.copilot/copilot-instructions.md`, `$HOME/.copilot/instructions/**/*.instructions.md` and `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`.
- ⚠️ **The CLI reads AGENTS.md only at the git root and the cwd.** It does not read "nearest in the tree" files. A nested `<subdir>/AGENTS.md` is picked up only if you launch `copilot` from that subdir.
  - By contrast, repo instructions for github.com and the cloud agent say: "the **nearest** `AGENTS.md` file in the directory tree will take precedence".
  - Source: GH:how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions
- ⚠️ `~/.claude/CLAUDE.md` is **not** in the CLI list. Personal instructions must go in `~/.copilot/copilot-instructions.md`.
- **`@path` imports (eager, recursive, with cycle and size guards)** work in `AGENTS.md`, `CLAUDE.md` and `.github/copilot-instructions.md` (CLI).
  - Source: same page, §Custom instructions imports.
  - VS Code docs instead say "use Markdown links" in instruction files (VSC:agent-customization/custom-instructions). Whether VS Code expands `@path` is NOT DOCUMENTED.
- **`.claude/rules/*.md`** take `paths:` (or `applyTo:`). They are delivered when a matching file is read or edited.
- **Opt-outs:** `--no-custom-instructions`; `/instructions` toggles files.

### Path-specific instructions format
Source: GH:how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions

```markdown
---
applyTo: "app/models/**/*.rb"        # comma-separated globs allowed: "**/*.ts,**/*.tsx"
excludeAgent: "code-review"          # or "cloud-agent" (optional)
---
```

VS Code adds optional `name` and `description`. `description` allows on-demand loading by task relevance.
- Source: VSC:agent-customization/custom-instructions

### VS Code (Local harness) settings
Source: VSC:agent-customization/custom-instructions

| Setting | Effect |
|---|---|
| `chat.useAgentsMdFile` | Enables AGENTS.md |
| `chat.useNestedAgentsMdFiles` | Nested AGENTS.md. **Off by default.** |
| `chat.useClaudeMdFile` | Reads root `CLAUDE.md`, `.claude/CLAUDE.md`, `~/.claude/CLAUDE.md`, `CLAUDE.local.md` |
| `github.copilot.chat.codeGeneration.useInstructionFiles` | Enables `.github/copilot-instructions.md` |
| `chat.useCustomizationsInParentRepositories` | Monorepo parent discovery |

- Older settings-based codegen instructions are deprecated since VS Code 1.102.
- Commit-message, PR-description and review-selection instruction settings remain.

### Prompt files (`.github/prompts/*.prompt.md`)
Sources: VSC:agent-customization/prompt-files, GH:how-tos/copilot-in-your-ide/customize-copilot/configure-custom-instructions/add-repository-instructions-in-your-ide

- Frontmatter: `description`, `name`, `argument-hint`, `agent` (`ask|agent|plan|<custom>`), `model`, `tools`. Invoked as `/name`.
- ⚠️ **They run ONLY in the VS Code *Local* harness.** VS Code docs tell you to convert them to skills for other harnesses.
- GitHub docs: prompt files are "only available in VS Code, Visual Studio, and JetBrains IDEs" (public preview).
- **The CLI does not load prompt files.** The CLI equivalent is skills, or `.claude/commands/*.md` "commands" (alternative skill format: `description`, `argument-hint`, `allowed-tools`, `disable-model-invocation`).
  - Source: GH:reference/copilot-cli-reference/cli-command-reference#commands-alternative-skill-format

### Copilot Memory (cloud, public preview)
Source: GH:concepts/agents/copilot-memory

- **Stores:**
  - Repository-level facts, with code citations. Validated against the current branch before use.
  - User-level preferences.
- **Used by:** cloud agent, code review (repo facts only), CLI, and agentic autofix.
- **Expiry:** unused memories auto-delete after **28 days**.
- **Defaults:** on for individual plans. Admin-enabled for Business/Enterprise.
- **CLI specifics:**
  - Tool kind `memory`.
  - `--enable-memory` turns memory on in `-p` mode (off there by default).
  - Only the root agent can `store_memory` / `vote_memory`.
  - Source: CLI command reference.
- **Manage it:** GH:how-tos/use-copilot-agents/copilot-memory/manage-for-yourself

### VS Code memory tool (local, different system)
Source: VSC:agents/run/memory

- Local files under `/memories/` (user, first 200 lines auto-loaded), `/memories/repo/` (workspace) and `/memories/session/`.
- The Plan agent writes `plan.md` to session memory.

### Session history ("chronicle")
Source: GH:how-tos/copilot-cli/use-copilot-cli/chronicle

- CLI sessions are stored locally in `~/.copilot/session-store.db` and `session-state/`. By default they are synced to the GitHub account (setting `remote`).
- `/chronicle standup|tips|improve|reindex|skills create|skills review|skills status`:
  - `improve` suggests edits to `copilot-instructions.md`.
  - `skills create` drafts skills from observed usage.

---

## 3. Permissions / approvals / trust / sandboxing

### CLI
Sources: GH:how-tos/copilot-cli/use-copilot-cli/allowing-tools, GH:how-tos/copilot-cli/set-up-copilot-cli/configure-copilot-cli, command reference §Tool permission patterns, GH:reference/copilot-cli-reference/cli-config-dir-reference

**Pattern syntax:** `Kind(argument)`.

| Kind | Examples |
|---|---|
| `shell` | `shell(git:*)` (`:*` = command stem + space), `shell(git push)` |
| `write` | `write(src/*.ts)` |
| `read` | `read(.env)` |
| `url` | `url(github.com)` |
| `memory` | `memory` |
| `SERVER-NAME` | `MyMCP(tool)`, `MyMCP` |

- For `git` and `gh`, match on the first-level subcommand: `shell(gh pr)`.
- **Deny always beats allow**, even with `--allow-all` or saved approvals.
- `--deny-tool='write(PATH)'` uses exact or trailing-segment matching ("no glob support yet").

**Flags:**
- `--allow-tool`, `--deny-tool`
- `--available-tools` / `--excluded-tools` (hide tools from the model entirely)
- `--allow-url`, `--deny-url`, `--allow-all-urls`
- `--allow-all-paths`, `--disallow-temp-dir`
- `--allow-all-tools` (env `COPILOT_ALLOW_ALL`), `--allow-all` (alias `--yolo`)
- `/permissions assisted`: an LLM judge recommends whether to approve.

**Prompt responses:**
- Keys: `y`, `n`, `!` (allow similar for the session), `#` (deny similar for the session).
- Dialog options: "Once", "This location" (saved to disk) or "Always".

**Persistence:**
- `~/.copilot/permissions-config.json` holds per-location `tool_approvals[]`. Kinds: `commands`, `read`, `write`, `mcp`, `memory`, …
- URL approvals go to `allowedUrls` in `~/.copilot/settings.json`.
- **CLI flags are never persisted.**

**Trusted folders:**
- You are prompted on first launch: trust for this session, or for future sessions.
- The list is stored as `trustedFolders` in `~/.copilot/config.json`. That file is auto-managed state; user settings now live in `settings.json`.
- **What trust gates:** repo hooks, workspace MCP (`.mcp.json`, `.github/mcp.json`), repo plugin settings, and repo `model`/`effortLevel`.
- **In `-p` mode** these are skipped for untrusted folders unless you use one of:
  - `--trust-folder`
  - `GITHUB_COPILOT_PROMPT_MODE_REPO_HOOKS=true`
  - `GITHUB_COPILOT_PROMPT_MODE_WORKSPACE_MCP=true`
  - `GITHUB_COPILOT_PROMPT_MODE_EXTENSIONS=true`
  - `COPILOT_ALLOW_ALL=true` (exactly `true`)

**⚠️ No repo-level persistent allow/deny lists.**
- `.github/copilot/settings.json` supports only an allowlist of keys: `companyAnnouncements`, `contextTier`, `deniedUrls`, `disableAllHooks`, `disabledMcpServers`, `disabledSkills`, `effortLevel`, `enabledPlugins`, `extraKnownMarketplaces`, `hooks`, `includeCoAuthoredBy`, `mergeStrategy`, `model` and `respectGitignore`. All other keys are silently ignored.
- `permissions.deny/ask/allow` rules (families: `Shell(...)`, `Bash(...)`, `PowerShell(...)`, `Read(...)`, `Edit(...)`, `Write(...)`, `Domain(...)`) exist **only as enterprise-managed or MDM settings**.
- **Consequence:** a team-wide "never push" rule in the repo must be a **hook** (§10).
- `permissions.disableBypassPermissionsMode: "disable"|"allow-auto-only"` blocks `--yolo` and the other allow-all flags. It can be set in user, managed or MDM settings.

**Sandbox:**
- GA 2026-10-07 across CLI, Copilot app and VS Code Agent Host sessions.
  - Source: https://github.blog/changelog/2026-10-07-local-sandboxing-for-github-copilot-now-generally-available/
- Engine: MXC (Microsoft eXecution Container): Seatbelt on macOS, Bubblewrap on Linux, ProcessContainer on Windows.
- Turn on with `/sandbox enable`, `--sandbox`, or `sandbox.enabled` in `~/.copilot/settings.json`.
- Policy keys: `sandbox.userPolicy.network.allowedHosts|blockedHosts|allowLocalNetwork|proxy`, `sandbox.userPolicy.filesystem.deniedPaths`, `sandbox.credentials.envVars{…injectHosts}` (masks secrets: the process sees placeholders and the proxy injects the real values only toward listed hosts), `sandbox.auth.git`, `sandbox.auth.gh`.
- **Not repo-overridable.**
- Plan mode blocks project-file edits at the tool layer ("safety net, not a guarantee").
- Command-safety analysis and an env-var denylist apply (`LD_*`, `GIT_CONFIG_*`, `PATH`, `GIT_SSH_COMMAND` …).

### VS Code
Sources: VSC:agents/run/approvals, VSC:agents/run/agent-sandboxing

- **Permission levels** (`chat.permissions.default`): **Manual** (default), **Assisted** (`chat.assistedPermissions.enabled`; not in Local), **Allow all**. Autopilot is a *mode* in the Copilot harness and a permission level in Local.
- **Settings:**

  | Setting | Purpose |
  |---|---|
  | `chat.tools.eligibleForAutoApproval` | Set a tool to `false` to always require approval |
  | `chat.tools.urls.autoApprove` | URL rules, with `approveRequest` / `approveResponse` |
  | `chat.tools.terminal.autoApprove` | Command or `/regex/` → `true`/`false`; `false` wins; `matchCommandLine` option |
  | `chat.tools.global.autoApprove` | Auto-approve everywhere |
  | `chat.agent.sandbox.enabled` | Sandbox. Network is allowed by default (`chat.agent.sandbox.network.allowNetwork` = true). Linux/WSL2 needs `bubblewrap` and `socat`. |

- Session-scoped allow-all: `/yolo` or `/autoApprove`.
- ⚠️ A `false` terminal rule only *requires approval*. It **does not block**. To block, the docs say to use a `PreToolUse` hook that returns `permissionDecision: "deny"`.
- **Workspace Trust** gates workspace hook files.

### Cloud agent
Sources: GH:concepts/agents/cloud-agent/risks-and-mitigations, GH:how-tos/copilot-on-github/customize-copilot/customize-the-firewall, GH:reference/hooks-reference

- **All tools are pre-approved.** No prompts. A hook `"ask"` is treated as `"deny"`.
- **Firewall:** under the repository "Internet access" settings tab. Covers the cloud agent and code review. Default: GitHub and Copilot hosts plus a "recommended allowlist" for dependency downloads. Not compatible with self-hosted runners.
- **Built-in guardrails:**
  - Only users with write access can trigger it.
  - It pushes **only to its own `copilot/` branch**, or to the PR branch when you `@copilot` an existing PR.
  - Its credentials can do "simple push operations" only. It "cannot directly run `git push`".
  - It **cannot mark ready, approve or merge**.
  - Actions workflows wait for **"Approve and run workflows"** by a human.
  - The requester cannot approve the PR.
  - Commits are signed and co-authored.
  - Hidden characters and HTML comments are stripped from prompts.
- **Recommended:** protect Copilot and MCP config files with `CODEOWNERS` + "Require review from Code Owners".
  - Source: GH:tutorials/cloud-agent/build-guardrails

---

## 4. Sessions

### CLI
Sources: GH:how-tos/copilot-cli/use-copilot-cli/work-with-multiple-sessions, GH:how-tos/copilot-cli/use-copilot-cli/chronicle, command reference

| Need | How |
|---|---|
| Resume | `copilot --continue` (most recent in cwd), `copilot --resume[=ID\|prefix\|name]`, `--session-id UUID`, `/resume`, `/continue`. Every `-p` run prints a `copilot --resume=SESSION-ID` hint. |
| Name | `-n NAME`, `/rename` |
| Multiple sessions | Sessions sidebar (← key), Sessions tab, `/fork` (works while running), `/new worktree`, `/worktree`, `/move` |
| Checkpoints | A checkpoint is created at **every compaction**: `/session checkpoints [n]`. ⚠️ This is a *summary* checkpoint, not a file snapshot. |
| Roll back | `/rewind` (alias `/undo`): "Conversation only" or "Conversation + files". Per-turn file tracking across edit tools, shell and subagents. **Git not required.** GH:how-tos/copilot-cli/use-copilot-cli/roll-back-changes |
| Share | `/share` (GitHub link), `/share file\|html\|gist`, `--share`, `--share-gist`. Gists are not available to EMU or data-residency accounts. |
| Remote steering | `/remote on`, `--remote`. Steer from github.com, Mobile or VS Code. GA 2026-05-18 (https://github.blog/changelog/2026-05-18-remote-control-for-copilot-cli-sessions-now-generally-available-on-mobile-web-and-vs-code/). `--connect=ID` |
| Crash restore | `COPILOT_ENABLE_INTERRUPTED_SESSION_RESTORE=1` (opt-in) |
| Hand off to cloud | `/delegate` or a `&` prompt prefix. Creates a branch and a draft PR. GH:how-tos/copilot-cli/use-copilot-cli/delegate-tasks-to-cca |

### VS Code
Source: VSC:agents/run/sessions/manage-sessions

- Checkpoints, fork from a checkpoint, `/fork`, multi-chat sessions, archive/done.
- The **Session Target** control picks the harness or Cloud. Handoff between them carries history (VSC:agents/concepts/sessions).

---

## 5. Context window

### CLI
Source: GH:concepts/agents/copilot-cli/context-management

- `/context`: token usage by System Prompt, Custom Instructions, System Tools, MCP Tools, Messages, Free Space and Buffer.
- **Auto-compaction** starts in the background at about **80%** and pauses at about 95%. `/compact [focus]` runs it manually; Esc cancels. Compactions cannot be undone.
- Tool output **>20 KiB is saved to a temp file**; the model gets the path and a preview. Override with `COPILOT_LARGE_OUTPUT_THRESHOLD_BYTES`.
- **Tool search (deferred tool loading):** `toolSearch` setting; per-MCP-server `deferTools: "auto"|"never"`.
- **MCP server instructions:** only allowlisted servers' instructions load up front. `--allow-all-mcp-server-instructions` loads all.
- Subagents run in separate context windows.
- Custom agents spawned as subagents get **no** repo instructions unless `include-custom-instructions: true`.
- **Context sizes** are model-dependent. The 1M tier is optional (VS Code and CLI only), and per-model token limits are in the pricing tables. ⚠️ An exact default window per model is NOT DOCUMENTED in a single table (UNVERIFIED).

### VS Code
Sources: VSC:agents/concepts/context, VSC:agents/run/sessions/manage-sessions, VSC:chat/copilot-chat-context

- The context-window control in the chat input shows token count, breakdown and AI credits.
- Auto-compaction can be disabled with `github.copilot.chat.summarizeAgentConversationHistory.enabled`. Manual: `/compact [focus]`.
- **References:**
  - `#codebase` runs a search; it does not dump the codebase into context.
  - `#file:` (also used inside skills, agents and prompts).
  - `#fetch` (`#web/fetch`), `#tool:<name>`.

**Lean-context levers (both):**
- Small, stable instructions; rarely-needed material moved into skills (loaded on demand).
- Fewer MCP servers, or `disabledMcpServers`.
- Subagents for noisy research. Skill `context: fork` (VS Code feature flag; needs `github.copilot.chat.skillTool.enabled`).
- New session between unrelated tasks.

---

## 6. Prompt caching (honest answer)

- **No user-facing caching control.** No `cache_control`, no TTL setting and no env var exist in CLI, VS Code or cloud agent. NOT DOCUMENTED anywhere.
- **Caching does happen, and you pay for it.** The pricing tables price **cached input** and **cache write** per model. Anthropic models and the GPT-5.6+/GPT-6 families list cache-write costs.
  - Source: GH:reference/copilot-billing/models-and-pricing
- **VS Code offers diagnosis, not control: the Cache Explorer.** Open it from the Agent Debug Logs → Summary → Cache Explorer. It shows per-turn cache hit %, reused tokens, and the "first divergence" in the prompt signature (system / tools / messages).
  - The docs' advice is to keep the request prefix stable:
    - Choose model, effort, context size and tools *before* the first request.
    - Don't edit instruction or agent files mid-session.
    - Attach only relevant context.
    - Use subagents for side research.
    - `/compact` or a new session deliberately.
    - **Forking preserves the prompt cache.**
  - Sources: VSC:agents/agent-troubleshooting/cache-explorer, VSC:agents/run/sessions/manage-sessions
- **The CLI has no cache view.** `/usage` shows per-model tokens and credits. OpenTelemetry export exists (command reference §OpenTelemetry). Whether OTel carries cache-token attributes: UNVERIFIED.
- **Programmatic (SDK)** caching controls: NOT DOCUMENTED (`@github/copilot-sdk`).

---

## 7. MCP

### Configuration files per surface

| Surface | File / place | Top key | Notes |
|---|---|---|---|
| CLI user | `~/.copilot/mcp-config.json` (`$COPILOT_HOME`) | `mcpServers` | `copilot mcp add NAME -- cmd args` / `--transport http NAME URL` |
| CLI workspace | `.mcp.json` (any dir cwd→git root) and `.github/mcp.json` | `mcpServers` | **Requires folder trust.** Priority: `--additional-mcp-config` > plugins > workspace > user |
| CLI per-session | `--additional-mcp-config='{json}'` or `@file` | | |
| VS Code Copilot harness | Reads `.mcp.json` (workspace root) + `~/.copilot/mcp-config.json`. Forwards eligible `.vscode/mcp.json` servers, **except those using `${input:...}`**. | `mcpServers` | VSC:agents/reference/mcp-configuration |
| VS Code Local harness | `.vscode/mcp.json` or user profile `mcp.json` | **`servers`** + `inputs[]` + `sandbox{}` | `${workspaceFolder}`, `${input:id}`, `envFile`, `sandboxEnabled` (macOS/Linux) |
| JetBrains | `mcp.json` opened from Copilot Chat → tools icon → "Add MCP Tools". Also an MCP Registry UI. | `servers` | ⚠️ File path on disk NOT DOCUMENTED. GH:how-tos/copilot-in-your-ide/customize-copilot/extend-copilot-with-tools-and-context/extend-copilot-chat-with-mcp |
| Cloud agent + code review | Repo **Settings → Copilot → MCP servers** (JSON pasted into the UI, not a file). Also `mcp-servers:` in custom-agent YAML. | `mcpServers` | GH:how-tos/copilot-on-github/customize-copilot/configure-mcp-servers |

**CLI server fields:**
- **Local:** `command`, `args`, `tools` (**required**, e.g. `["*"]`), `env` (`$VAR`, `${VAR}`, `${VAR:-default}`), `cwd`, `timeout` (ms, default 30000), `type: local|stdio`, `deferTools`, `disableToolCache`.
- **Remote:** `type: http|sse`, `url`, `tools`, `headers`, `oauthClientId`, `oauthScopes`, `oauthGrantType: client_credentials` (headless OAuth), `oidc`.
- **Tool name format seen by the model:** `serverName-toolName` (sanitized, max 64 characters).

**Built-in CLI servers:**
- `github-mcp-server`. Its default subset is read-heavy: `get_file_contents`, `search_code`, issues, PRs, commits, workflow runs, plus `label_write`. Widen with `--add-github-mcp-toolset`, `--add-github-mcp-tool` or `--enable-all-github-mcp-tools`.
- **`playwright`**, `fetch`, `time`.
- Disable with `--disable-builtin-mcps` or `--disable-mcp-server NAME`.
- ⚠️ **Playwright is already built in. Do not configure it twice.**

**Cloud agent MCP:**
- Default servers: GitHub (read-only, repo-scoped token) and Playwright (localhost only).
- **Only tools are used; no resources or prompts. No OAuth remote servers.**
- Secrets must be Agents secrets or variables prefixed **`COPILOT_MCP_`**. Reference them as `$COPILOT_MCP_X` or `${COPILOT_MCP_X}`. Agent YAML also accepts `${{ secrets.X }}`.
- Copilot uses the configured tools autonomously, without approval. Allowlist read-only tools.
- Install binaries such as `codegraph` or `uvx` through `.github/workflows/copilot-setup-steps.yml`. It needs a single job named `copilot-setup-steps`, and the file must be on the default branch.
  - Source: GH:how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/customize-the-agent-environment
- **Code review uses an MCP tool only if `annotations.readOnlyHint: true` is set.** Toggle: "Allow Copilot to use MCP tools when reviewing pull requests".

**Org policy:**
- The enterprise MCP allowlist uses fingerprints (command + args + URL) and is **fail-closed**. A private MCP registry is available.
- Sources: GH:how-tos/administer-copilot/manage-mcp-usage/configure-enterprise-allowlist, CLI reference §Enterprise MCP allowlist

**Migration:** `jq '{mcpServers: .servers}' .vscode/mcp.json > .mcp.json` (CLI reference).

---

## 8. Agent Skills, plugins, marketplace

### Locations

| Surface | Project | Personal |
|---|---|---|
| CLI | `.github/skills/`, `.agents/skills/`, `.claude/skills/`, parent `.github/skills/` (monorepo) | `~/.copilot/skills/`, `~/.agents/skills/` |
| VS Code | `.github/skills/`, `.claude/skills/`, `.agents/skills/` | `~/.copilot/skills/`, **`~/.claude/skills/`**, `~/.agents/skills/` |
| Cloud agent and code review | `.github/skills`, `.claude/skills`, `.agents/skills` | — |

- CLI extras: plugin dirs, `COPILOT_SKILLS_DIRS`, `skillDirectories` setting, `--add-dir`, built-in skills, and org/enterprise remote skills.
- **Surfaces:** cloud agent, code review, CLI, Copilot app, VS Code agent mode, JetBrains (Preview).
- Sources: GH:reference/copilot-cli-reference/cli-command-reference#skill-locations, VSC:agent-customization/agent-skills, GH:concepts/agents/about-agent-skills, GH:how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills
- ⚠️ **The CLI does NOT read `~/.claude/skills/`.** The user's existing personal skills (`evidence`, `atlassian`, `day`, `kg`, `kg-refresh`) must be copied or symlinked to `~/.copilot/skills/` or `~/.agents/skills/`, or registered with `copilot skill add <dir>` / `COPILOT_SKILLS_DIRS`.

### Frontmatter

| Key | CLI | VS Code | Cloud agent docs |
|---|---|---|---|
| `name` (required) | Letters, digits, `- _ . :` and space; max 64 | **lowercase, digits and hyphens only; must match the directory name**; max 64; otherwise "silently fail to load" | lowercase, hyphens |
| `description` (required) | Max 1024 | Max 1024 | ✓ |
| `argument-hint` | ✓ | ✓ | — |
| `allowed-tools` | ✓ (string or array; `"*"`) | not listed | ✓ (example `allowed-tools: shell`) |
| `user-invocable` | ✓ (default true) | ✓ | — |
| `disable-model-invocation` | ✓ (default false) | ✓ | — |
| `context: fork` | — | ✓ (feature-flagged) | — |
| `license` | — | — | ✓ |

**Notes on porting the user's skills:**
- ⚠️ `trigger: /day` (and `/kg`, `/kg-refresh`) in the author's `~/.claude/skills/*` frontmatter is **not a Copilot key**. Whether unknown keys are ignored is NOT DOCUMENTED / UNVERIFIED. Recommendation: remove it. Copilot invokes skills as `/<name>` automatically.
- The two Cursor-pack skills (`day`, `atlassian`) use only `name` + `description` with YAML `>-` folded descriptions. That is compatible.
- ⚠️ The exact grammar of `allowed-tools` entries (for example whether `shell(python3:*)` is accepted) is UNVERIFIED. The docs only show `shell`, and warn against pre-approving `shell`/`bash` for untrusted skills.

**Invocation:**
- `/skill-name` (users).
- Automatic, based on `description` (agent). VS Code also offers embeddings-based dynamic retrieval (`dynamicRetrieval.skills` setting in CLI).
- Management: CLI `/skills list|info|add [--project]|remove|reload`, `copilot skill …`; VS Code Agent Customizations editor (**Chat: Open Customizations**); `gh skill` (GitHub CLI ≥ 2.90, preview).
- The files in the skill directory are made available to the agent. Reference them with relative Markdown links or `#file:./x`.

### Plugins and marketplace
Sources: GH:concepts/agents/about-plugins, GH:how-tos/copilot-cli/customize-copilot/plugins-creating, GH:reference/copilot-cli-reference/cli-plugin-reference

- **Formats:**
  - **Agent Plugins 1.0:** `plugin.json` with `"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"`. Uses `skills/`, `mcp.json`, and `com.github.copilot/{agents,commands,rules,hooks/hooks.json,lsp.json}`.
  - **Legacy Copilot:** `plugin.json` with component paths `agents`, `skills`, `hooks`, `mcpServers`.
  - The legacy loader also accepts `.claude-plugin/plugin.json`.
- **Marketplaces:**
  - `marketplace.json` lives in `.github/plugin/`, `.plugin/`, root, or `.claude-plugin/`. Claude Code marketplaces are readable.
  - Built-in non-removable marketplace: **`awesome-copilot`**. `github/copilot-plugins` is no longer default.
- **Commands:**
  ```bash
  copilot plugin install NAME@MARKETPLACE | OWNER/REPO | URL | PATH
  copilot plugin marketplace add OWNER/REPO
  ```
  Interactive equivalent: `/plugin …`.
- **Repo-declared plugins:** `enabledPlugins` / `extraKnownMarketplaces` in `.github/copilot/settings.json`. The cloud agent also reads these.
- **VS Code:** agent plugins (VSC:agent-customization/agent-plugins) and an experimental "Customization Marketplace" (`chat.customizations.marketplace.enabled`).
- Old "Copilot Extensions" (GitHub Apps) are not covered here. Agent apps are the current partner model (GH:concepts/agent-capabilities/about-agents/agent-apps). Status of legacy Copilot Extensions: UNVERIFIED.

---

## 9. Custom agents and subagents

### Locations
- **CLI** (Sources: CLI reference §Custom agent locations; GH:how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli), in priority order:
  1. `~/.copilot/agents/`
  2. `.github/agents/` (cwd → git root; deepest wins)
  3. `.claude/agents/`
  4. `--add-dir` roots
  5. plugin `agents/`
  6. org/enterprise
- Extension: `*.agent.md` (plain `*.md` accepted). Agent ID = path relative to `agents/` with `/` → `--`.
- **Org/enterprise level:** `/agents` folder in the org's `.github` or `.github-private` repo.
- **VS Code:** `.github/agents/*.agent.md`, user folder, and `.claude/agents/*.md` (Claude format). Legacy `.chatmode.md` is not mentioned in the current docs (UNVERIFIED whether still read).

### Frontmatter

| Key | Applies to |
|---|---|
| `description` | Required in CLI and cloud |
| `name` | All |
| `tools` | Aliases `execute/shell/Bash`, `read`, `edit`, `search`, `agent`, `web`, `todo`, `server/*`, `server/tool`. `[]` = none. Unknown names ignored. |
| `model` | All. VS Code allows an array. |
| `target: vscode\|github-copilot` | All |
| `disable-model-invocation`, `user-invocable` | All. `infer` is retired. |
| `mcp-servers` | Cloud agent and CLI. Not VS Code. |
| `metadata` | Cloud |
| `include-custom-instructions`, `models[]`, `modelPolicy`, `reasoningEffort`, `hooks`, `sidekick:` | CLI |
| `handoffs[]` (`label`, `agent`, `prompt`, `send`, `model`), `agents[]`, `argument-hint` | **VS Code Local only.** Cloud agent ignores them. |
| `reasoning-effort` | VS Code Copilot harness |

- Body max 30,000 characters (cloud).
- Sources: GH:reference/custom-agents-configuration, VSC:agents/reference/custom-agent-file-reference

### Subagents
- **CLI built-ins** (default models as listed in the docs):

  | Agent | Default model / note |
  |---|---|
  | `code-review` | claude-sonnet-4.6. Will not modify code. |
  | `explore` | gpt-5.4-mini. Fast, parallel-safe, <300-word answers. |
  | `general-purpose` | |
  | `research` | |
  | `rubber-duck` | Complementary-model critique. |
  | `security-review` | |
  | `task` | Runs tests and builds. |

- **Spawning:** tool `task`. Plus `list_agents`, `read_agent`, `write_agent` (background agents can be messaged).
- **Limits:** concurrency is plan-based (Free 2, Pro 4, Max 8, Business 16, Enterprise 32). Depth default 6 per the reference table; ⚠️ the env-var table says 4, a documentation inconsistency. Env: `COPILOT_SUBAGENT_MAX_CONCURRENT`, `COPILOT_SUBAGENT_MAX_DEPTH`.
- **Background / parallel:**
  - `/fleet` or `--fleet` (parallel subagents for a plan).
  - **Sidekick agents** (`sidekick: triggers: [user.message, session.context_changed]`) run in the background and post to the session inbox.
  - `/tasks`.
- **VS Code Local:** `runSubagent` tool (`agent/runSubagent`). Coordinator `agents: [...]`. Nested subagents need `chat.subagents.allowInvocationsFromSubagents`. Source: VSC:agents/run/subagents
- **Delegating to the cloud agent:**
  - CLI `/delegate` or `&`
  - VS Code Session Target → Cloud
  - Assign an issue to Copilot
  - `@copilot` in a PR
  - Agents page
  - REST API (§11)

---

## 10. Hooks

**Support:**
- **Yes in CLI and cloud agent** (one shared schema).
- **Yes in VS Code**: Preview, with *two* implementations depending on harness.
- **Code review hooks: NOT DOCUMENTED.**
- Sources: GH:reference/hooks-reference, GH:how-tos/copilot-cli/customize-copilot/use-hooks, GH:how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/use-hooks, VSC:agent-customization/hooks, VSC:agents/reference/hooks-reference

### Locations (CLI)
All sources are combined, in this order:
1. Policy: `/etc/github-copilot/policy.d/*.json` (root-owned; cannot be disabled).
2. **`.github/hooks/*.json`** (repo).
3. `~/.copilot/hooks/*.json`.
4. Inline `hooks` in `.github/copilot/settings.json`, `.github/copilot/settings.local.json`, **`.claude/settings.json`**, `.claude/settings.local.json`.
5. Inline `hooks` in `~/.copilot/settings.json`. The CLI no longer reads `~/.copilot/config.json` for hooks.
6. Plugin `hooks.json`.
7. Agent-scoped `hooks:` in agent frontmatter.

- **Cloud agent:** reads only `.github/hooks/*.json` from the clone. Linux only: `bash`/`command` honored, `powershell` ignored. CWD `/workspace`.
- **Changes load at CLI start.**

### Format (CLI and cloud)

```json
{ "version": 1,
  "hooks": {
    "preToolUse": [
      { "type": "command", "matcher": "bash|powershell",
        "bash": "./.github/hooks/block-external.sh",
        "powershell": "./.github/hooks/block-external.ps1",
        "cwd": ".", "env": {"K":"V"}, "timeoutSec": 10 }
    ] } }
```

- **Hook types:**
  - `command`: `bash` / `powershell` / `command`, or `exec` + `args` (CLI only).
  - `http`: POST JSON. Must be `https` for `preToolUse` and `permissionRequest`.
  - `prompt`: `sessionStart` only; new interactive sessions only.
- **Events:**
  - `sessionStart`, `sessionEnd`
  - `userPromptSubmitted`, `userPromptTransformed`
  - **`preToolUse`**, `postToolUse`, `postToolUseFailure`
  - `permissionRequest` (CLI only)
  - `agentStop`, `subagentStart`, `subagentStop`
  - `preCompact`
  - `errorOccurred`
  - `notification` (CLI only)
- **PascalCase aliases** (`PreToolUse`, …) switch the payload to VS Code-compatible snake_case (`tool_name`, `tool_input`). They also apply **Claude matcher semantics**: `Bash`, `Edit|Write`; `bash`/`powershell` map to `Bash`, `view` to `Read`, `task` to `Agent`.
- **`preToolUse` input** (camelCase): `{sessionId, timestamp, cwd, toolName, toolArgs}`.
  - ⚠️ The docs type `toolArgs` as `unknown`, but the debug example passes a **JSON string** (`"toolArgs":"{\"command\":\"ls\"}"`). Handle both string and object.
  - Subagent hooks add `agentId`, `agentType`, `parentAgentId`.
- **`preToolUse` output:**
  - `{"permissionDecision":"allow"|"deny"|"ask","permissionDecisionReason":"…","modifiedArgs":{…}}`
  - `permissionDecisionReason` is required for deny.
  - Exactly **one** final JSON object on stdout. Progress lines `{"type":"progress",…}` are allowed.
- **Exit codes:**
  - `0` = parse stdout.
  - **`2` = deny** for `preToolUse` and `permissionRequest`.
  - Other non-zero = **fail-closed deny for `preToolUse`**, fail-open elsewhere.
  - ⚠️ **Timeouts are fail-open for every event, including `preToolUse` and policy hooks.** Default timeout 30 s.
- **`agentStop` / `subagentStop`:** `{"decision":"block","reason":"…"}` forces another turn. Runaway guard after 8 blocks.
- **`permissionRequest`:** `{"behavior":"allow"|"deny","message","interrupt"}`. Cannot pre-approve a sandbox escape.
- **Kill switch:** `disableAllHooks: true` (per file, or in repo `settings.json` for the CLI).
- **Payload format (`hookSpecificOutput`):** Claude-style `hookSpecificOutput` is **NOT DOCUMENTED** for the CLI. Use the top-level `permissionDecision` or exit 2.

### VS Code Local harness hooks (different schema!)
- **Files:** `.github/hooks/*.json`, `~/.copilot/hooks/*.json`, `.claude/settings*.json` (only if `chat.useClaudeHooks`, which is off by default; matchers ignored), agent frontmatter, plugins.
- **Settings:** `chat.useHooks` (on by default), `chat.hookFilesLocations`.
- **Format:** PascalCase events, `command` / `windows` / `linux` / `osx` / `timeout`. Copilot-format files (`version` + camelCase) are parsed, but **runtime payloads use the Local schema**.
- **Local `PreToolUse` input:** `{tool_name, tool_input, tool_use_id, …}`.
- **Local `PreToolUse` output:** `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"…"}}`.
- **Exit 2** = blocking error fed to the model.
- **Events:** `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `SessionStart`, `Stop`, `SubagentStart`, `SubagentStop`, `PreCompact`.
- **VS Code Copilot-harness sessions** use the CLI/SDK hook implementation and the GitHub hooks reference.

### Blocking `git push` / PR / merge (portable recipe)
- **Script:** one script handles both payload shapes:
  - Command source: `toolArgs.command` (parse it if it is a string) or `tool_input.command`.
  - Match pattern: `git push`, `gh pr (create|merge|ready)`, `gh api … /merges`, `terraform apply`, `kubectl apply`, `helm upgrade`, `gh release create`.
  - On a match, print both `{"permissionDecision":"deny","permissionDecisionReason":"…"}` and `hookSpecificOutput` (verify on the target build), then **exit 2**. Exit 2 is the one blocking signal that is documented in both schemas.
- **Where the hook must be registered:**
  - `.github/hooks/block-external.json` with matcher `bash|powershell` (CLI, cloud agent, VS Code Copilot harness).
  - The same file also works in VS Code Local (it is parsed there; Local ignores `matcher`? UNVERIFIED for Copilot-format files). To be safe, also filter on tool name inside the script.
- **Belt and braces for CLI sessions:**
  - `--deny-tool='shell(git push)' --deny-tool='shell(gh pr)'` (deny beats allow, even with `--yolo`).
  - Also deny GitHub MCP write tools if write toolsets are enabled.
- ⚠️ **The CLI has `/pr create|auto|automerge`.** These are first-party slash commands that create and **merge** PRs. Whether they pass through `preToolUse` (as shell or `gh` calls) is UNVERIFIED. Mention them in the instructions file as human-only, and test the hook against them.
- ⚠️ **In `-p`/CI, repo hooks are not loaded in an untrusted folder.** Use `--trust-folder` or `GITHUB_COPILOT_PROMPT_MODE_REPO_HOOKS=true`.

---

## 11. Automation

- **`copilot -p` in scripts and CI:**
  - Install with npm in the workflow.
  - Auth: `COPILOT_GITHUB_TOKEN` (fine-grained PAT with "Copilot Requests"), or `GITHUB_TOKEN` with `permissions: copilot-requests: write`.
  - Use `-s`, `--no-ask-user`, minimal `--allow-tool`, and `--model`.
  - `COPILOT_TASK_WAIT_TIMEOUT_SECONDS` (default 600) controls how long `-p` waits for background tasks.
  - Sources: GH:how-tos/copilot-cli/automate-copilot-cli/automate-with-actions, GH:how-tos/copilot-cli/use-copilot-cli-in-actions
- **GitHub recommends GitHub Agentic Workflows** (`github/gh-aw`) over raw `copilot` steps, because of its guardrails and default `GITHUB_TOKEN`.
  - Sources: GH:how-tos/github-agentic-workflows/quickstart, GH:concepts/agent-capabilities/agent-powered-workflows-and-operations/about-github-agentic-workflows
- **Cloud agent via API (public preview):**
  - `POST https://api.github.com/agents/repos/{owner}/{repo}/tasks` with `{"prompt", "base_ref", "model", "create_pull_request"}`.
  - List: `GET /agents/repos/{o}/{r}/tasks` and `GET /agents/tasks`.
  - **User-to-server tokens only.** Issues can also be assigned to Copilot through REST or GraphQL.
  - Source: GH:how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-via-the-api
- **Cloud agent "Automations":** schedule- or event-triggered, created in the repo **Agents → Automations** pane. You choose the tools. Events from users without write access are ignored by default.
  - Sources: GH:how-tos/use-copilot-agents/cloud-agent/create-automations, GH:concepts/agent-capabilities/agent-powered-workflows-and-operations/about-automations
- **Integrations:** Slack, Teams, Jira, Linear, Azure Boards, Raycast (GH:how-tos/copilot-integrations/*).
- **CLI in-session scheduling:** `/every`, `/after` (experimental).
- **Copilot SDK:**
  - Packages: `@github/copilot-sdk` (npm), `github-copilot-sdk` (pip, `from copilot import CopilotClient`), `github.com/github/copilot-sdk/go`, `GitHub.Copilot.SDK` (.NET), Java.
  - Usage: `new CopilotClient()` → `createSession({model:"auto"})` → `sendAndWait({prompt})`.
  - Programmatic hooks such as `onPreToolUse` return `permissionDecision`.
  - Sources: GH:get-started/sdk-quickstart, GH:how-tos/copilot-sdk/features/hooks
- **Code-review automation:**
  - Repo ruleset rule **"Automatically request Copilot code review"**, with options "Review new pushes" and "Review draft pull requests".
  - Effort level: Lite or Balanced.
  - Optional **Copilot approvals** (preview, off by default) can count toward required approvals.
  - Reads `copilot-instructions.md`, path instructions, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `REVIEW.md`, and `.github/skills` (review-named skills preferred), all **from the head branch**.
  - Sources: GH:how-tos/copilot-on-github/set-up-copilot/configure-code-review, GH:how-tos/use-copilot-agents/use-code-review
- **ACP server:** `copilot --acp`. Source: GH:reference/copilot-cli-reference/acp-server

---

## 12. Mapping the methodology onto Copilot

### Two-level memory (`AGENTS.md` + scoped rules, tier 0/1/2)
- **Tier 1:**
  - Root `AGENTS.md`. It works on all four surfaces; prefer it over `copilot-instructions.md` for one shared voice with Cursor and Claude.
  - Optional small `.github/copilot-instructions.md`. It is the only file that code review in VS Code, Visual Studio and Eclipse reads.
- **Scoped gates:** `.github/instructions/<concern>.instructions.md` with `applyTo`. Use `excludeAgent: "code-review"` for gates that make no sense in review. The CLI also accepts `.claude/rules/*.md` with `paths:`, so Claude-Code rules can be reused as they are.
- **Nested `AGENTS.md`:** works for the cloud agent ("nearest wins"). The CLI reads only root + cwd. VS Code Local needs `chat.useNestedAgentsMdFiles`. The safe pattern: put per-folder rules in `.instructions.md` with `applyTo: "subdir/**"`.
- **Tier 2** (`data/changes/**`): unchanged, read on demand. Use `@path` imports only for what must be eager (CLI). Prefer pointers.
- **Tier 0** `IDENTITY.md`: unchanged (gitignored). It can be read through a `sessionStart` hook that returns `additionalContext` (CLI/cloud), or through `~/.copilot/copilot-instructions.md` (machine-local personal instructions).

### Skills
Put the project copies in `.github/skills/<name>/SKILL.md` (CLI, VS Code, cloud agent, code review).

- **For every ported skill:**
  - Drop `trigger:`.
  - Keep `name` lowercase-hyphen and equal to the folder name. VS Code silently drops skills that violate this.
  - Keep `description` at most 1024 characters.
- **`day`:**
  - Pure local shell + S3 sync. Works in CLI and VS Code.
  - Optional `sessionStart` prompt hook `{"type":"prompt","prompt":"/day start"}` (CLI, interactive new sessions only) to *enforce* the start-of-day routine. That is a real enforcement upgrade over Cursor.
  - Not for the cloud agent: no `~/.aws`, ephemeral.
- **`atlassian`** (read-only Jira/Confluence via REST token in `~/.config/<org>/jira.env`):
  - Works locally.
  - If the CLI sandbox is on, add the Atlassian host to `sandbox.userPolicy.network.allowedHosts`. Consider `sandbox.credentials` masking if the token is moved to an env var.
  - For the cloud agent you would need Agents secrets plus a firewall allow rule. Recommend **local-only**: omit it from the cloud surface, or use `target`/`excludeAgent` patterns. Note that skills have no `excludeAgent`; UNVERIFIED how to hide a skill from the cloud agent other than not committing it (put it in `~/.copilot/skills`).
- **`evidence`** (read-only AWS by matter URL, `uv run --with boto3`, a read-only SSO profile):
  - Local only. The sandbox needs network access to AWS endpoints and read access to `~/.aws`. Path grants: UNVERIFIED; inspect with `/sandbox policy`.
  - Keep read-only enforcement in the script. Optionally use `allowed-tools` for just that command; grammar UNVERIFIED.
- **`kg` / `kg-refresh`:**
  - `kg` is deterministic scripts: a direct port.
  - `kg-refresh` wraps `/graphify`, which is a Claude-Code skill that uses parallel subagents. Port graphify as a Copilot skill (CLI subagents via `task` / `/fleet`), or keep running the semantic step from Claude Code. Publisher-only guard stays in the script.

### MCP servers (CodeGraph, Serena, Playwright, Context7)

| Server | Local (CLI + VS Code Copilot harness) | VS Code Local harness | Cloud agent |
|---|---|---|---|
| **CodeGraph** | stdio in `.mcp.json`: `"codegraph": {"command":"codegraph","args":["serve","--path",".","--mcp"],"tools":["*"]}` | `.vscode/mcp.json` with `--path ${workspaceFolder}` | Repo MCP settings + install via `copilot-setup-steps.yml` |
| **Serena** | stdio via `uvx --from git+https://github.com/oraios/serena serena start-mcp-server` | same | same as CodeGraph |
| **Playwright** | **Built in (CLI)**: don't add it | Add it in `.vscode/mcp.json` if needed | Default on, localhost only |
| **Context7** | `{"type":"http","url":"https://mcp.context7.com/mcp","tools":["*"]}` (the shape is shown verbatim in VSC:agents/reference/mcp-configuration) | same | Needs a firewall allowlist for `mcp.context7.com` |

- ⚠️ `${workspaceFolder}` is VS Code-only. `.mcp.json` expands env vars only. Whether `--path .` resolves against the session cwd for workspace servers is UNVERIFIED; launch from the repo root or use an absolute path in `~/.copilot/mcp-config.json`.

### Hook blocking external git
See §10. Repo file `.github/hooks/block-external.json` + `preToolUse` deny / exit 2. Reinforcing layers:
- Cloud agent guardrails are structural: it cannot merge.
- Optional `permissions.deny` (managed/MDM) for org-wide policy.
- `CODEOWNERS` on `.github/hooks/**`, `.github/agents/**`, `.github/skills/**`, `.mcp.json`, `AGENTS.md`.

### Read-only subagents
`.github/agents/scout.agent.md`:

```yaml
---
name: scout
description: Read-only codebase research; returns a summary
tools: ["read", "search"]      # add "codegraph/*" / "serena/find_symbol" etc.
user-invocable: true
---
```

- CLI: run it with `--agent scout`, by name in a prompt, or via `/fleet … use @scout`.
- The CLI built-in `explore` / `research` are already read-only-ish.
- ⚠️ A read-only *tools* list is the enforcement; prose is not. Custom agents don't get repo instructions as subagents unless `include-custom-instructions: true`.

### GSD (Claude-Code-only) — Copilot substitute
No first-party equivalent of GSD's phase/roadmap state machine exists. The nearest pieces:
- CLI **plan mode** (`/plan`, Shift+Tab, `--plan`). It is enforced at the tool layer.
- **Plan-then-autopilot** (`--plan --mode autopilot`).
- **`/fleet`** for wave-parallel plan execution.
- **Custom agents** per role (planner / executor / verifier).
- **Autopilot** with `--max-autopilot-continues` / `--max-ai-credits`.
- `agentStop` hook `decision: block` as a "verify before stop" gate.
- VS Code `handoffs` (Local) for plan→implement buttons.
- GitHub's open-source **Spec Kit** (`github/spec-kit`, spec-driven templates and prompts; supports Copilot). This is third-party coverage only; current version UNVERIFIED.
- Keep the methodology's own ledgers (`STATUS.md` / `PLAYBOOK.md`) as the state store.

### Memory / claude-mem substitute
- **Copilot Memory:** cloud, public preview. Repo facts and user prefs, 28-day expiry. Not a versioned file.
- **VS Code memory tool** (local `/memories`).
- **CLI session store + `/chronicle`**, and you can ask about past sessions.
- **Canonical, reviewable memory** stays in `data/changes/` + `AGENTS.md` (the write-once rule). Treat Copilot Memory like Cursor Memories: a complement, never a source of truth.
- Whether claude-mem's MCP search server can be attached to Copilot as a plain MCP server: UNVERIFIED (claude-mem is a Claude Code plugin).

---

## 13. Equivalence table: Claude Code → Cursor → Copilot

| Concept | Claude Code | Cursor (from the sibling guide) | GitHub Copilot (Oct 2026) |
|---|---|---|---|
| CLI / headless | `claude -p` | `agent -p --trust [--force]` | `copilot -p "…" -s [--allow-tool …] [--trust-folder]`; piped stdin OK |
| Cloud async agent | (web / remote) | Background/Cloud Agents | **Copilot cloud agent** (issue assign, `/delegate`, `&`, API `POST /agents/repos/{o}/{r}/tasks`) |
| Always-loaded memory | `CLAUDE.md` | `AGENTS.md` + `.cursor/rules` `alwaysApply` | `AGENTS.md` and/or `.github/copilot-instructions.md` (CLI also reads `CLAUDE.md`/`GEMINI.md`) |
| Scoped rules | `.claude/rules` `paths:` | `.mdc` `globs` | `.github/instructions/*.instructions.md` `applyTo` (+`excludeAgent`); CLI also `.claude/rules` |
| Eager import | `@path` | `@file` in `.mdc` | `@path` in AGENTS.md/CLAUDE.md/copilot-instructions.md (CLI) |
| Personal memory | `~/.claude/CLAUDE.md` | user rules | `~/.copilot/copilot-instructions.md`, `~/.copilot/instructions/` |
| Auto memory | auto-memory `MEMORY.md` / claude-mem | Cursor Memories | Copilot Memory (cloud, preview) / VS Code `/memories` / CLI `/chronicle` |
| Reusable prompts | slash commands / skills | skills | skills (all surfaces); prompt files `.github/prompts/*.prompt.md` (VS Code Local, VS, JetBrains only) |
| Permissions | `settings.json` `permissions.allow/deny` (`mcp__srv__tool`) | `permissions.json` `mcpAllowlist`/`terminalAllowlist` | CLI flags `--allow-tool/--deny-tool 'shell(git push)'`, `MyMCP(tool)`; saved `permissions-config.json`; repo-level allow/deny only via **managed** settings; VS Code `chat.tools.*` settings |
| Bypass mode | `--dangerously-skip-permissions` | `--yolo`/`--force` | `--yolo`/`--allow-all`, `/allow-all`; blockable via `permissions.disableBypassPermissionsMode` |
| Sandbox | sandbox settings | — | `/sandbox`, `--sandbox`, `sandbox.*` (MXC; GA 2026-10-07); VS Code `chat.agent.sandbox.enabled` |
| Trust | workspace trust | Workspace Trust / `--trust` | folder trust (`trustedFolders`), `--trust-folder`, `--add-dir` |
| Sessions | `--resume`/`--continue` | chats, CLI sessions | `--resume`/`--continue`/`/resume`, `/fork`, `/rewind`, `/share`, `/remote` |
| Checkpoint / undo | `/rewind` | `/rewind` | `/rewind` (conversation ± files); compaction checkpoints `/session checkpoints`; VS Code checkpoints |
| Context view | `/context` | context ring | `/context` (CLI), context-window control (VS Code) |
| Compaction | `/compact <focus>` | `/summarize` | `/compact [focus]`; auto at ~80% |
| Prompt caching control | API `cache_control` (not in product) | none | none; billed cached-input/cache-write; VS Code **Cache Explorer** for diagnosis |
| MCP config | `.mcp.json`, `claude mcp add` | `.cursor/mcp.json` | `.mcp.json`/`.github/mcp.json` + `~/.copilot/mcp-config.json` (`mcpServers`, `tools` required); VS Code `.vscode/mcp.json` (`servers`); cloud: repo Settings JSON |
| Skills | `.claude/skills`, `~/.claude/skills` | `.cursor/skills` (+ `.claude/skills`) | `.github/skills`, `.claude/skills`, `.agents/skills`; `~/.copilot/skills`, `~/.agents/skills` (VS Code also `~/.claude/skills`) |
| Plugins / marketplace | `/plugin` | Marketplace (UI) | `copilot plugin install`, `/plugin`; built-in `awesome-copilot`; reads `.claude-plugin/` |
| Subagents | `.claude/agents/*.md` | `.cursor/agents/*.md` | `.github/agents/*.agent.md`, `~/.copilot/agents/` (CLI also `.claude/agents/`); built-ins explore/task/code-review/research/rubber-duck/security-review/general-purpose |
| Agent teams / parallel | Agent Teams | Cloud Agents (no messaging) | `/fleet`, background subagents with `write_agent` messaging, sidekick agents, multiple sessions, `/delegate` |
| Hooks | `settings.json` hooks (PreToolUse…) | `.cursor/hooks.json` (`beforeShellExecution`…) | `.github/hooks/*.json` `{version:1}` camelCase (`preToolUse`…); also reads `.claude/settings.json` hooks; VS Code Local schema differs |
| Block a command | PreToolUse exit 2 / deny | `permission:"deny"` / exit 2 | `preToolUse` `permissionDecision:"deny"` / **exit 2** (non-zero = fail-closed; timeout = fail-open) |
| CI | `claude -p` in Actions | Cursor SDK / Bugbot | `copilot -p` in Actions (`copilot-requests: write`), GitHub Agentic Workflows, cloud-agent automations |
| SDK | Agent SDK | `@cursor/sdk` | `@github/copilot-sdk` (+ Python/Go/.NET/Java) |
| PR review bot | — | Bugbot | Copilot code review (ruleset auto-request; `REVIEW.md`) |
| Plan mode | plan mode | Plan mode | `/plan`, `--plan`, Shift+Tab (enforced); VS Code Plan agent |
| GSD | GSD plugin | n/a | n/a: plan mode + `/fleet` + custom agents + (Spec Kit) |

---

## 14. Gotchas and changes in 2025–2026

**Naming and billing:**
1. **Coding agent → cloud agent** rename. Update every slide and link (docs URLs now `/cloud-agent/`).
2. **Premium requests → AI Credits (2026-06-01).** Courses written earlier quoting "300 premium requests / multipliers" are wrong except for legacy annual plans.
3. **Copilot CLI** went public preview in Sep 2025 and **GA 2026-02-25**. Do not confuse it with the retired `gh copilot` extension (2024 GA).
   - https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/
   - https://github.blog/changelog/2024-03-21-github-copilot-general-availability-in-the-cli/
4. **Agent Skills** were announced 2025-12-18 (cloud agent, CLI, VS Code Insiders, then stable).
   - https://github.blog/changelog/2025-12-18-github-copilot-now-supports-agent-skills/

**Configuration:**
5. **CLI config split:** user settings moved to `~/.copilot/settings.json`. `config.json` is now internal state (trusted folders, auth). Settings left in `config.json` are ignored. Hooks are no longer read from `config.json`.
6. **VS Code harness split** (Copilot vs Local). Settings such as `chat.agentSkillsLocations` and `chat.instructionsFilesLocations` are deprecated and **not read by the Copilot harness**. Prompt files and `handoffs` are Local-only. Hooks have two schemas.
7. **Skill name rules differ**: VS Code is strict and silently drops invalid names. The CLI does not read `~/.claude/skills`; VS Code does.

**Instructions and MCP:**
8. **AGENTS.md nesting** differs per surface (CLI: root + cwd only).
9. **No repo-committed allow/deny permission lists in the CLI.** Use hooks, or managed settings for org policy.
10. **`-p` mode skips repo hooks, workspace MCP and extensions in untrusted folders.** This matters for CI gates.
11. MCP `tools` is **required** in CLI and cloud configs. `.vscode/mcp.json` uses `servers`, not `mcpServers`. `${input:}` servers are not forwarded to the Copilot harness. The cloud agent doesn't support OAuth remote MCP, MCP resources or MCP prompts.
12. **Playwright, GitHub, fetch and time MCP servers are built into the CLI.**

**Safety:**
13. **Hook timeouts fail open** (even for policy hooks). Keep blocking hooks fast. A crash or non-zero exit fails closed for `preToolUse`.
14. **`/pr automerge` and `/pr auto`** exist in the CLI. The agent can merge PRs if not blocked. The cloud agent cannot merge.
15. **Copilot code review can now *approve* PRs** (preview, off by default) and count toward merge requirements. Keep it off if "the human owns merge".
16. **Code review uses MCP tools only with `readOnlyHint: true`.** It reads instructions and skills from the **head** branch, so a PR can change its own reviewer's instructions. Protect them with CODEOWNERS.

**Docs reliability:**
17. **Doc inconsistencies:** subagent max depth is 6 (table) vs 4 (env-var row). Built-in agent default models (e.g. `claude-sonnet-4.6`, `gpt-5.4-mini`) differ from the CLI default model table (`claude-sonnet-5.5`). The feature matrix still lists VS Code only up to 1.108. Verify on the target build.

**Platform:**
18. **Sandbox on Linux/WSL2** needs `bubblewrap` + `socat` (VS Code docs). The VS Code sandbox allows network by default.
19. **Copilot Memory** is public preview and auto-expires after 28 days. It is not a substitute for versioned ledgers.
20. **Content exclusions** now apply in the CLI and Copilot app (GA 2026-09-02, Business/Enterprise).
    - https://github.blog/changelog/2026-09-02-content-exclusions-generally-available-in-copilot-app-and-cli/

---

## 15. Checking the old `COPILOT_ADAPTATION.md` against current docs

File: the Cursor volume's `docs/ai-agents-code-methodology/COPILOT_ADAPTATION.md`. It is almost entirely tool-agnostic methodology, with **no concrete Copilot file paths, flags or config**. None of its few product claims is false, but it is badly **outdated and incomplete**:

| § | Claim / gap | Status vs Oct 2026 docs |
|---|---|---|
| Title / §4 | "using GitHub Copilot agent workflows" with no surfaces named | **Outdated.** Name the 4 surfaces (CLI, VS Code harnesses, cloud agent, code review) and what each loads. |
| §4.1 | "Session start: read orientation doc first" as a manual step | **Outdated.** `AGENTS.md` / `copilot-instructions.md` load automatically. A `sessionStart` hook (`additionalContext` or a `prompt` hook running `/day start`) can enforce it. |
| §4.4–4.5 | Plan gate / TDD gate as prose only | **Incomplete.** Copilot now has plan mode enforced at the tool layer (CLI `/plan`, `--plan`), `agentStop` block hooks, and `/rubber-duck` / `/review` agents. |
| §5 | Folder structure has no `.github/` customization files | **Incomplete.** Add `AGENTS.md`, `.github/instructions/`, `.github/skills/`, `.github/agents/`, `.github/hooks/`, `.mcp.json`, `.github/copilot/settings.json`, `.github/workflows/copilot-setup-steps.yml`. |
| §3 | No-KG fallback (STATUS.md + lexical search + commit history) | Still valid. Can add Copilot Memory / `/chronicle` as non-canonical aids. |
| §8.1 | "No direct merge/deploy by agent" as policy only | **Outdated framing.** Now *enforceable*: `preToolUse` deny hook + `--deny-tool`. Cloud agent cannot merge by design. **But** CLI `/pr automerge` and code-review auto-approval are new escape paths to close. |
| §8.3 | "No unexplained bot-review dismissal" | Still valid. Note Copilot code review can now approve PRs (preview). |
| §7 / §11 | Tech mapping questions | Still valid; generic. |
| Missing entirely | MCP (CodeGraph, Serena, Playwright, Context7), skills (`day`, `atlassian`, `evidence`, `kg`), hooks, permissions/sandbox, sessions, context/compaction, caching, headless `copilot -p`, cloud agent, billing in AI credits | Must be written from §1–§12 above. |

`CURSOR_ADAPTATION.md` points to it as the "parallel guide" and shares the fallback and KPI sections. Those cross-references stay valid.

---

## Source index (all fetched 2026-10-17)

**docs.github.com (prefix `https://docs.github.com/en/copilot/`):**
- **CLI reference:** `reference/copilot-cli-reference/cli-command-reference`, `…/cli-config-dir-reference`, `…/cli-plugin-reference`, `…/cli-programmatic-reference`
- **CLI how-tos** (under `how-tos/copilot-cli/`):
  - Setup: `set-up-copilot-cli/{install-copilot-cli,authenticate-copilot-cli,configure-copilot-cli}`
  - Use: `use-copilot-cli/{allowing-tools,work-with-multiple-sessions,roll-back-changes,chronicle,delegate-tasks-to-cca,speed-up-task-completion,invoke-custom-agents,use-autopilot-mode,steer-remotely,set-session-limit}`
  - Automation: `automate-copilot-cli/{run-cli-programmatically,automate-with-actions,schedule-prompts}`, `use-copilot-cli-in-actions`
  - Customization: `customize-copilot/{add-custom-instructions,use-hooks,add-skills,add-mcp-servers,create-custom-agents-for-cli,plugins-finding-installing,plugins-creating,plugins-marketplace}`
- **Concepts:**
  - CLI: `concepts/agents/copilot-cli/{context-management,understanding-local-sandboxing,comparing-cli-features,about-cli-extensions}`
  - Agents: `concepts/agents/{copilot-memory,hooks,about-plugins,about-agent-skills}`, `concepts/agents/cloud-agent/{about-custom-agents,mcp-and-cloud-agent,risks-and-mitigations}`
  - Other: `concepts/context/mcp`, `concepts/models/auto-model-selection`, `concepts/billing-and-usage/individuals/billing`, `concepts/agent-capabilities/about-agents/about-github-copilot-agents`, `concepts/agent-capabilities/agent-powered-workflows-and-operations/{about-automations,about-github-agentic-workflows}`
- **Reference:** `reference/{custom-agents-configuration,custom-instructions-support,hooks-reference,customization-cheat-sheet,copilot-feature-matrix,ai-models/supported-models,copilot-billing/models-and-pricing,copilot-billing/request-based-billing-legacy/what-changed-with-billing}`
- **github.com how-tos** (under `how-tos/copilot-on-github/`):
  - Instructions: `customize-copilot/add-custom-instructions/{add-repository-instructions,add-personal-instructions,add-organization-instructions}`
  - Cloud agent customization: `customize-copilot/customize-cloud-agent/{create-custom-agents,add-skills,use-hooks,customize-the-agent-environment,configure-secrets-and-variables}`
  - Other: `customize-copilot/{customize-the-firewall,configure-mcp-servers}`, `set-up-copilot/configure-code-review`
- **Agent how-tos:** `how-tos/use-copilot-agents/{use-code-review,copilot-memory/manage-for-yourself}`, `how-tos/use-copilot-agents/cloud-agent/{use-cloud-agent-on-github,use-cloud-agent-via-the-api,create-automations,configuring-agent-settings}`
- **IDE how-tos:** `how-tos/copilot-in-your-ide/{use-copilot-agents/use-subagents,use-copilot-agents/use-custom-agents,customize-copilot/configure-custom-instructions/add-repository-instructions-in-your-ide,customize-copilot/extend-copilot-with-tools-and-context/extend-copilot-chat-with-mcp}`
- **Other:** `tutorials/cloud-agent/build-guardrails`, `get-started/sdk-quickstart`, `how-tos/copilot-sdk/features/hooks`, `how-tos/github-agentic-workflows/quickstart`

**code.visualstudio.com/docs/ (DateApproved 2026-10-14..16):**
- `agent-customization/{custom-instructions,agent-skills,custom-agents,hooks,mcp-servers,prompt-files,agent-plugins,migrate-customizations,overview,tool-sets}`
- `agents/reference/{hooks-reference,mcp-configuration,custom-agent-file-reference,ai-settings,tools-reference,agent-plugin-reference}`
- `agents/run/{approvals,agent-sandboxing,memory,subagents,sessions/manage-sessions,remote-agent-sessions,automations,planning}`
- `agents/concepts/{agent-harnesses,context,sessions,language-models,trust-and-safety}`
- `agents/guides/{context-engineering-guide,optimize-usage}`
- `agents/agent-troubleshooting/cache-explorer`
- `chat/copilot-chat-context`

**github.blog changelog:**
- https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/
- https://github.blog/changelog/2025-12-18-github-copilot-now-supports-agent-skills/
- https://github.blog/changelog/2026-10-07-local-sandboxing-for-github-copilot-now-generally-available/
- https://github.blog/changelog/2026-05-18-remote-control-for-copilot-cli-sessions-now-generally-available-on-mobile-web-and-vs-code/
- https://github.blog/changelog/2026-06-23-copilot-cli-new-terminal-interface-is-generally-available/
- https://github.blog/changelog/2026-09-02-content-exclusions-generally-available-in-copilot-app-and-cli/

**Third-party (Spec Kit only):**
- https://visualstudiomagazine.com/articles/2026/05/12/github-spec-kit-takes-off-as-antidote-to-piecemeal-vibe-coding.aspx
