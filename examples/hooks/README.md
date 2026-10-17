# Hooks (GitHub Copilot)

A **hook** is a command that runs on agent events (`preToolUse`, `postToolUse`, `sessionStart`, …). It is the
deterministic way to control the agent: you do not *ask* it not to push — you **make** it unable to.
Facts: findings §10 ([`../../docs/research/COPILOT_FINDINGS_2026-10-17.md`](../../docs/research/COPILOT_FINDINGS_2026-10-17.md)).

## Support per surface

| Surface | Hooks? | Schema |
|---|---|---|
| Copilot CLI | ✓ | GitHub hooks schema (`version: 1`, camelCase events) |
| Cloud agent | ✓ — reads **only** `.github/hooks/*.json` from the clone; Linux only (`bash`/`command` honoured, `powershell` ignored); cwd `/workspace`; a hook `"ask"` is treated as `"deny"` | same |
| VS Code — Copilot harness | ✓ (Preview) | same as the CLI |
| VS Code — Local harness | ✓ (Preview) | **different** — PascalCase events, `tool_name`/`tool_input`, `hookSpecificOutput` |
| Code review | NOT DOCUMENTED | — |

## Where the CLI reads hooks (all combined, in this order)

1. Policy `/etc/github-copilot/policy.d/*.json` (root-owned; cannot be disabled)
2. **`.github/hooks/*.json`** (repo)
3. `~/.copilot/hooks/*.json`
4. Inline `hooks` in `.github/copilot/settings.json`, `.github/copilot/settings.local.json`, **`.claude/settings.json`**, `.claude/settings.local.json`
5. Inline `hooks` in `~/.copilot/settings.json` (no longer `~/.copilot/config.json`)
6. Plugin `hooks.json` · 7. agent-scoped `hooks:` in agent frontmatter

Changes load at CLI start. Kill switch: `disableAllHooks: true`.

## The contract (CLI / cloud agent / VS Code Copilot harness)

| | |
|---|---|
| File | `{"version": 1, "hooks": {"preToolUse": [ … ]}}` |
| Entry | `type: command` with `bash` / `powershell` / `command` (or `exec` + `args`, CLI only), `matcher`, `cwd`, `env`, `timeoutSec` · `type: http` (POST JSON; https for `preToolUse`) · `type: prompt` (`sessionStart` only, new interactive sessions only) |
| Events | `sessionStart`, `sessionEnd`, `userPromptSubmitted`, `userPromptTransformed`, **`preToolUse`**, `postToolUse`, `postToolUseFailure`, `permissionRequest` (CLI), `agentStop`, `subagentStart`, `subagentStop`, `preCompact`, `errorOccurred`, `notification` (CLI) |
| `preToolUse` input | `{sessionId, timestamp, cwd, toolName, toolArgs}` — ⚠️ `toolArgs` is typed `unknown` but the docs' example passes a **JSON string**: handle string and object ([`payloads/preToolUse.cli.json`](./payloads/preToolUse.cli.json)) |
| `preToolUse` output | `{"permissionDecision": "allow"\|"deny"\|"ask", "permissionDecisionReason": "…", "modifiedArgs": {…}}` — reason required for deny; exactly **one** final JSON object on stdout |
| Exit codes | `0` = parse stdout · **`2` = deny** (`preToolUse`, `permissionRequest`) · other non-zero = **fail-closed deny for `preToolUse`**, fail-open elsewhere |
| ⚠️ Timeouts | **fail-OPEN for every event, including `preToolUse` and policy hooks** (default 30 s). Keep blocking hooks fast, no network. |
| `agentStop` / `subagentStop` | `{"decision": "block", "reason": "…"}` forces another turn; runaway guard after 8 blocks |
| PascalCase aliases | `PreToolUse`, … switch the payload to snake_case (`tool_name`, `tool_input`) **and** apply Claude matcher semantics (`Bash`, `Edit\|Write`; `bash`/`powershell`→`Bash`, `view`→`Read`, `task`→`Agent`) |
| `hookSpecificOutput` | Claude-style — NOT DOCUMENTED for the CLI. Use top-level `permissionDecision` or exit 2. |

**VS Code Local harness:** files `.github/hooks/*.json`, `~/.copilot/hooks/*.json`, `.claude/settings*.json`
(only with `chat.useClaudeHooks`, off by default); settings `chat.useHooks`, `chat.hookFilesLocations`;
input `{tool_name, tool_input, tool_use_id, …}`; output
`{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", …}}`; exit 2 = blocking
error fed to the model ([`payloads/PreToolUse.vscode-local.json`](./payloads/PreToolUse.vscode-local.json)).
Copilot-format files are parsed there, but runtime payloads use the Local schema — which is why the scripts
here accept both shapes and **print both decision shapes + exit 2** ([`payloads/deny-response.json`](./payloads/deny-response.json)).

## Examples in this folder

| File | Event | What it does |
|---|---|---|
| [`block-external-git.json`](./block-external-git.json) | `preToolUse` (`bash\|powershell`) | The methodology handoff gate — scripts live in [`../../.github/hooks/`](../../.github/hooks/) (bash + PowerShell twins, offline test `test-block-external-git.sh`). Denies `git push`, `gh pr create\|merge\|ready` (incl. `--auto`), `gh api …/merge`, `gh release create`, `terraform/kubectl apply`, `helm upgrade`. |
| [`deny-env-read.json`](./deny-env-read.json) + [`scripts/deny_env_read.sh`](./scripts/deny_env_read.sh) | `PreToolUse` alias, matcher `Read` | Denies reading `.env` files. Uses the alias so `Read` matches the CLI's `view` tool; the path key is UNVERIFIED, so the script checks several. |
| [`log-tool-use.json`](./log-tool-use.json) + [`scripts/log_hook.sh`](./scripts/log_hook.sh) | `preToolUse` + `postToolUse` | Appends each payload as one JSON line to `.github/hooks/hook-log.jsonl` — the way to see the real payload of *your* build. |
| [`session-start-day.json`](./session-start-day.json) | `sessionStart`, `type: prompt` | Runs `/day start` at the start of every new interactive CLI session — **enforces** the routine a doc could only recommend. Not in `-p` mode. |
| [`agent-stop-verify.json`](./agent-stop-verify.json) + [`scripts/verify_before_stop.sh`](./scripts/verify_before_stop.sh) | `agentStop` | "Verify before stop": blocks the stop if `src/`/`tests/` changed after the last `.verify-ok` marker. |

Install: copy the JSON into `.github/hooks/` and the scripts into `.github/hooks/scripts/` (paths in the JSON are
relative to the repo root via `cwd: "."`), make them executable (`git update-index --chmod=+x` on Windows
checkouts), restart the CLI.

## ⚠️ `-p` / CI: repo hooks are skipped in an untrusted folder

In prompt mode, repo hooks (and workspace MCP, extensions) are **not loaded** unless the folder is trusted:
`--trust-folder`, or `GITHUB_COPILOT_PROMPT_MODE_REPO_HOOKS=true`. A CI "gate" without it silently gates
nothing — see [`../automation/copilot-cli-action.yml`](../automation/copilot-cli-action.yml).

## Belt and braces for the push gate

- `--deny-tool='shell(git push)' --deny-tool='shell(gh pr)'` on CLI runs (deny beats allow, even with `--yolo`).
- ⚠️ CLI **`/pr create|auto|automerge`** are first-party slash commands that create and **merge** PRs. Whether
  they pass through `preToolUse` is UNVERIFIED — declare them human-only in `.github/copilot-instructions.md`
  and test the hook against them on your build.
- `CODEOWNERS` on `.github/hooks/**` so a PR cannot quietly weaken its own gate.

## Mapping from Claude Code and Cursor

| Claude Code | Cursor | Copilot |
|---|---|---|
| `settings.json` hooks, `PreToolUse`, exit 2 | `.cursor/hooks.json`, `beforeShellExecution`, `permission: "deny"` / exit 2 | `.github/hooks/*.json`, `preToolUse`, `permissionDecision: "deny"` / **exit 2** |
| hook timeout | `failClosed` option | **timeout = fail-open**; crash = fail-closed (`preToolUse`) |
| — | — | The CLI also reads hooks from `.claude/settings.json` |
