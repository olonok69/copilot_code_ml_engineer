# COPILOT_WORKING_AGREEMENT_TEMPLATE

> Fill in with the team; keep the filled copy under `data/changes/`. Facts about Copilot behaviour were
> verified against the docs on 2026-10-17 — re-check before relying on a detail.

## Scope and role

1. Copilot may investigate, propose, implement and test, on these surfaces: `[ ] CLI  [ ] VS Code (Copilot harness)  [ ] VS Code (Local harness)  [ ] JetBrains  [ ] cloud agent  [ ] code review`.
2. The human approves the plan before code for non-trivial changes (CLI `/plan` / Shift+Tab, VS Code Plan agent).
3. The human owns merge, deploy and external communication — always, including when the agent "could".

## Files we keep (tier 1 = always loaded, keep small)

| File | Owner | Purpose |
|---|---|---|
| `AGENTS.md` | | orientation + pointers + output contract + human-only actions |
| `.github/copilot-instructions.md` | | short; the only file IDE code review reads |
| `.github/instructions/*.instructions.md` | | scoped gates (`applyTo`, `excludeAgent`) |
| `.github/skills/*` | | `kg`, `kg-refresh`, `methodology-plan`, `sanitise-diff` (+ personal: `day`, `atlassian`, `evidence`, `preview`) |
| `.github/agents/*.agent.md` | | read-only scouts (`tools: ["read","search"]`) |
| `.github/hooks/block-external-git.*` | | deny push / PR / merge / release / deploy |
| `.mcp.json`, `.vscode/mcp.json` | | CodeGraph, Serena, Context7 (Playwright is built into the CLI) |

All of the above are protected by `CODEOWNERS` + "Require review from Code Owners": `[ ] done`.

## Required gates

1. Inbound gate: symptom reproduced at the output contract.
2. Provenance gate: pre-change baseline check (regression vs pre-existing).
3. TDD gate: RED -> GREEN.
4. Outbound gate (five checks): canary the instrument · contract via the real writer · member list, not totals · shipping artifact · look at the output.
5. Sanitise gate: `sanitise-diff` on added staged lines before handoff.

## Permissions and merge ownership

1. The `preToolUse` hook `.github/hooks/block-external-git.json` is installed and its test passes (`bash .github/hooks/test-block-external-git.sh`).
2. Headless / CI runs always pass `--trust-folder` (otherwise repo hooks are skipped) **and** `--deny-tool='shell(git push)' --deny-tool='shell(gh pr)'`; `--allow-tool` lists only what the job needs.
3. `--yolo` / `--allow-all`: `[ ] never  [ ] only in a sandboxed throwaway clone`. Machines that must never bypass set `permissions.disableBypassPermissionsMode` in user or managed settings.
4. CLI `/pr create`, `/pr auto`, `/pr automerge` are **human-only**. Hook result against them on our build: `[ blocked | not intercepted — policy only ]` (UNVERIFIED in the docs; test it).
5. **Copilot code-review approvals (preview) stay OFF.** Copilot review comments are triaged like a human's; a bot approval is not the human gate.
6. Local sandbox (`/sandbox enable`, `--sandbox`): `[ on | off ]`; allowed hosts: `[ ... ]`.

## Cloud agent rules

1. Who may assign issues / `/delegate`: users with write access (enforced by GitHub).
2. It works on its own `copilot/` branch and opens a **draft** PR; it cannot approve or merge. A human runs "Approve and run workflows".
3. Firewall allowlist (Settings → Internet access): `[ ... ]`.
4. MCP servers (Settings → Copilot → MCP servers): read-only tools only; secrets named `COPILOT_MCP_*`.
5. `copilot-setup-steps.yml` lives on the default branch and installs: `[ codegraph, uv, ... ]`.
6. Skills needing local credentials (`day`, `atlassian`, `evidence`, `preview`) are **not** committed; they live in `~/.copilot/skills/`.

## Billing

1. Usage is billed in GitHub AI Credits (since 2026-06-01). Spend cap for autonomous runs: `--max-ai-credits=[N]`.

## Documentation outputs per issue

1. Issue note. 2. Handover note. 3. QA acceptance criteria. 4. STATUS / FOLLOWUPS / SHARP_EDGES rows (append-only).

## Security and confidentiality

1. No secrets in committed files. 2. No forbidden names/IDs per repo policy (list kept in a gitignored `.sanitise-names`). 3. Sanitise before handoff.

## Review policy

1. Automated reviewer comments (Copilot code review included) are triaged like human comments.
2. No unresolved valid findings at merge time.
