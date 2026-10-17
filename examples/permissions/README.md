# Permissions, trust and sandboxing (GitHub Copilot)

What the agent may do without asking — and, more importantly, what it may **never** do. Facts: findings §3
([`../../docs/research/COPILOT_FINDINGS_2026-10-17.md`](../../docs/research/COPILOT_FINDINGS_2026-10-17.md)).

## 1. Copilot CLI — tool patterns

Syntax `Kind(argument)`:

| Kind | Examples |
|---|---|
| `shell` | `shell(git:*)` (`:*` = command stem + space), `shell(git push)`; for `git`/`gh` match on the first-level subcommand: `shell(gh pr)` |
| `write` | `write(src/*.ts)` — for `--deny-tool='write(PATH)'`: exact or trailing-segment matching, "no glob support yet" |
| `read` | `read(.env)` |
| `url` | `url(github.com)` |
| `memory` | `memory` |
| MCP server | `MyMCP(tool)`, `MyMCP` |

Flags: `--allow-tool`, `--deny-tool`, `--available-tools` / `--excluded-tools`, `--allow-url` / `--deny-url` /
`--allow-all-urls`, `--allow-all-paths`, `--disallow-temp-dir`, `--allow-all-tools` (`COPILOT_ALLOW_ALL`),
`--allow-all` (alias `--yolo`). Example: [`copilot-cli-flags.sh`](./copilot-cli-flags.sh).

- **Deny always beats allow**, even with `--allow-all` or saved approvals.
- Prompt keys: `y`, `n`, `!` (allow similar for the session), `#` (deny similar); dialog: Once / This location (saved) / Always.
- Saved approvals: `~/.copilot/permissions-config.json` (per location); URL approvals: `allowedUrls` in
  `~/.copilot/settings.json`. **CLI flags are never persisted.**

## 2. ⚠️ No repo-level allow/deny lists

`.github/copilot/settings.json` accepts only an allowlist of keys (`companyAnnouncements`, `contextTier`,
`deniedUrls`, `disableAllHooks`, `disabledMcpServers`, `disabledSkills`, `effortLevel`, `enabledPlugins`,
`extraKnownMarketplaces`, `hooks`, `includeCoAuthoredBy`, `mergeStrategy`, `model`, `respectGitignore`); everything
else is **silently ignored**. `permissions.deny/ask/allow` rules (`Shell(...)`, `Bash(...)`, `Read(...)`,
`Edit(...)`, `Domain(...)`…) exist **only as enterprise-managed / MDM settings**.

**Consequence:** a team-wide "never push" rule committed to the repo must be a **hook**
([`../hooks/`](../hooks/), live: [`../../.github/hooks/block-external-git.json`](../../.github/hooks/block-external-git.json)).
Bypass modes can be blocked with `permissions.disableBypassPermissionsMode: "disable" | "allow-auto-only"`
(user, managed or MDM settings).

## 3. Trusted folders

First launch asks: trust for this session, or for future sessions (stored as `trustedFolders` in
`~/.copilot/config.json` — auto-managed state; user settings live in `settings.json`). Trust gates **repo
hooks, workspace MCP (`.mcp.json`, `.github/mcp.json`), repo plugin settings and repo `model`/`effortLevel`**.
In `-p` mode these are skipped for untrusted folders unless `--trust-folder`,
`GITHUB_COPILOT_PROMPT_MODE_REPO_HOOKS=true`, `…_WORKSPACE_MCP=true`, `…_EXTENSIONS=true` or
`COPILOT_ALLOW_ALL=true`.

## 4. Sandbox (GA 2026-10-07: CLI, Copilot app, VS Code Agent Host)

`/sandbox enable`, `--sandbox`, or `sandbox.enabled` in `~/.copilot/settings.json`. Engine MXC (Seatbelt / Bubblewrap /
ProcessContainer). Policy keys: `sandbox.userPolicy.network.allowedHosts|blockedHosts|allowLocalNetwork|proxy`,
`sandbox.userPolicy.filesystem.deniedPaths`, `sandbox.credentials.envVars{…injectHosts}` (the process sees
placeholders; the proxy injects real values only toward listed hosts), `sandbox.auth.git`, `sandbox.auth.gh`.
**Not repo-overridable.** Plan mode blocks project-file edits at the tool layer ("safety net, not a guarantee").

## 5. VS Code

Permission levels (`chat.permissions.default`): **Manual** (default), **Assisted** (not in Local), **Allow all**.
Settings: `chat.tools.eligibleForAutoApproval`, `chat.tools.urls.autoApprove`, `chat.tools.terminal.autoApprove`
(command or `/regex/` → `true`/`false`; `false` wins), `chat.tools.global.autoApprove`, `chat.agent.sandbox.enabled`
(network allowed by default; Linux/WSL2 needs `bubblewrap` + `socat`). Example:
[`.vscode/settings.json.example`](./.vscode/settings.json.example).

⚠️ A `false` terminal rule only **requires approval** — it does **not block**. To block, the docs point to a
`PreToolUse` hook returning `permissionDecision: "deny"`. Workspace Trust gates workspace hook files.

## 6. Cloud agent

- **All tools pre-approved**, no prompts; a hook `"ask"` = `"deny"`.
- **Firewall** (repo "Internet access" settings; covers the cloud agent and code review): GitHub/Copilot hosts +
  a recommended allowlist for dependency downloads; not compatible with self-hosted runners.
- **Structural guardrails:** only users with write access can trigger it; it pushes **only to its own
  `copilot/` branch** (or the PR branch when you `@copilot` a PR); "cannot directly run `git push`"; **cannot mark
  ready, approve or merge**; Actions workflows wait for a human "Approve and run workflows"; the requester cannot
  approve the PR; commits are signed and co-authored.
- Protect Copilot/MCP config with `CODEOWNERS` + "Require review from Code Owners".

## The layers — compared

| Layer | Claude Code | Cursor | Copilot |
|---|---|---|---|
| Static allow/deny | `settings.json` `permissions` | `permissions.json` | CLI flags (session) · managed settings (org) · VS Code `chat.tools.*` |
| Content-based veto | `PreToolUse` hook | `beforeShellExecution` hook | `preToolUse` hook (`.github/hooks`) — the only repo-committable deny |
| Prose policy | `CLAUDE.md` | rules | `AGENTS.md` / `copilot-instructions.md` (steers, does not veto) |

The *policy* — the human owns everything external — is identical; the mechanism changes.
