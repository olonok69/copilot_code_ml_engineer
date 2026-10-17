# Copilot surface pack

Copy-ready artifacts that implement the AI-agent methodology for **GitHub Copilot**. Parent guide:
[`../COPILOT_ADAPTATION.md`](../COPILOT_ADAPTATION.md). Facts verified against the docs on **2026-10-17**
([`../../research/COPILOT_FINDINGS_2026-10-17.md`](../../research/COPILOT_FINDINGS_2026-10-17.md)) —
Copilot moves fast, re-check before reuse.

## What each file is, where it goes, who reads it

| File in this pack | Install as (target repo) | Read by |
|---|---|---|
| [`AGENTS.md.example`](./AGENTS.md.example) | `AGENTS.md` (root) | CLI (git root + cwd), VS Code (`chat.useAgentsMdFile`), cloud agent (nearest file wins), code review |
| [`copilot-instructions.md.example`](./copilot-instructions.md.example) | `.github/copilot-instructions.md` | All surfaces; the **only** file Copilot code review in VS Code / Visual Studio / Eclipse reads |
| [`instructions/00-methodology-core.instructions.md`](./instructions/00-methodology-core.instructions.md) | `.github/instructions/` | CLI, VS Code, cloud agent (`excludeAgent: "code-review"`) |
| [`instructions/01-tool-prevalence.instructions.md`](./instructions/01-tool-prevalence.instructions.md) | `.github/instructions/` | same |
| [`instructions/02-gates-and-handoff.instructions.md`](./instructions/02-gates-and-handoff.instructions.md) | `.github/instructions/` | same |
| [`instructions/atlassian.instructions.md`](./instructions/atlassian.instructions.md) | `.github/instructions/` | same; `applyTo: "data/changes/**"` |
| [`mcp.json.example`](./mcp.json.example) | `.mcp.json` (root) | CLI + VS Code **Copilot** harness (`mcpServers`, `tools` required); **trusted folder only** |
| [`.vscode/mcp.json.example`](./.vscode/mcp.json.example) | `.vscode/mcp.json` | VS Code **Local** harness (`servers`, `${workspaceFolder}`) |
| [`hooks/block-external-git.json`](./hooks/block-external-git.json) + `.sh` + `.ps1` | `.github/hooks/` | CLI, cloud agent (bash only), VS Code Copilot harness; parsed by VS Code Local |
| [`hooks/test-block-external-git.sh`](./hooks/test-block-external-git.sh) | `.github/hooks/` | You — offline tests for the hook (canary first) |
| [`agents/refactor-scout.agent.md`](./agents/refactor-scout.agent.md) | `.github/agents/` | CLI, VS Code, cloud agent |
| [`copilot-setup-steps.yml.example`](./copilot-setup-steps.yml.example) | `.github/workflows/copilot-setup-steps.yml` (default branch) | Cloud agent only |
| [`skills/*/SKILL.md`](./skills/) | `.github/skills/<name>/` (or personal `~/.copilot/skills/<name>/`) | CLI, VS Code, cloud agent, code review — see each skill's "Invocation per surface" |

Skills: `day`, `atlassian`, `evidence` (local credentials — **do not** rely on them in the cloud agent),
`kg`, `kg-refresh` (publisher only), `methodology-plan`, `sanitise-diff`.

## Notes the JSON files cannot carry (JSON has no comments)

- **Playwright is not in `mcp.json.example` on purpose**: the Copilot CLI ships `playwright`, `github-mcp-server`,
  `fetch` and `time` built in. Configuring Playwright again duplicates it. It *is* optional in
  `.vscode/mcp.json.example` because the Local harness has no built-ins of that kind.
- `--path .` for CodeGraph: whether `.` resolves against the session cwd for workspace servers is **UNVERIFIED**.
  Launch `copilot` from the repo root, or put an absolute path in `~/.copilot/mcp-config.json`.
  `${workspaceFolder}` works only in VS Code files.
- `.vscode/mcp.json` servers that use `${input:...}` are **not** forwarded to the Copilot harness.
- Migration helper from the docs: `jq '{mcpServers: .servers}' .vscode/mcp.json > .mcp.json` (then add `tools`).
- **Cloud agent MCP** is configured as JSON pasted in repository **Settings → Copilot → MCP servers** (same
  `mcpServers` shape). Only tools are used (no resources/prompts, no OAuth remote servers); secrets must be
  Agents secrets/variables prefixed `COPILOT_MCP_`; tools run **without approval** → allowlist read-only tools.
  Context7 needs a firewall allow rule for `mcp.context7.com`. Binaries (`codegraph`, `uvx`) come from
  `copilot-setup-steps.yml`.
- **Code review** uses an MCP tool only when it has `annotations.readOnlyHint: true`.

## Install (from the target repo root)

Prefer the bootstrap script (never overwrites without `-Force`):

```powershell
Rename-Item data/changes/ai-agent-methodology/scripts/bootstrap-copilot-repo.ps1.txt bootstrap-copilot-repo.ps1
pwsh data/changes/ai-agent-methodology/scripts/bootstrap-copilot-repo.ps1
```

Or by hand (bash):

```bash
src=data/changes/ai-agent-methodology/copilot
mkdir -p .github/instructions .github/skills .github/agents .github/hooks .github/workflows .vscode
cp -n "$src/AGENTS.md.example" AGENTS.md
cp -n "$src/copilot-instructions.md.example" .github/copilot-instructions.md
cp -n "$src"/instructions/*.instructions.md .github/instructions/
cp -rn "$src"/skills/* .github/skills/
cp -n "$src"/agents/*.agent.md .github/agents/
cp -n "$src"/hooks/* .github/hooks/ && chmod +x .github/hooks/*.sh
cp -n "$src/mcp.json.example" .mcp.json
cp -n "$src/.vscode/mcp.json.example" .vscode/mcp.json
cp -n "$src/copilot-setup-steps.yml.example" .github/workflows/copilot-setup-steps.yml
```

## Post-install checklist

1. `bash .github/hooks/test-block-external-git.sh` → `0 failures` (the canary case must deny first).
2. Ensure CLIs exist: `codegraph` (`npm i -g @colbymchenry/codegraph`), `uvx`; then `codegraph init` and
   add `.codegraph/` to `.gitignore`.
3. Launch `copilot` from the repo root and **trust the folder** (repo hooks and workspace MCP are gated by
   trust). Check `/mcp`, `/skills`, `/instructions`.
4. **Test the hook against the CLI's `/pr create`, `/pr auto` and `/pr automerge`** on a throwaway repo —
   whether those slash commands pass through `preToolUse` is UNVERIFIED. Record the result in
   `SHARP_EDGES.md`.
5. In CI, `copilot -p` skips repo hooks in an untrusted folder: always add `--trust-folder` **and**
   `--deny-tool='shell(git push)' --deny-tool='shell(gh pr)'`.
6. Keep **Copilot code-review approvals** (preview) **off**.
7. Add `CODEOWNERS` entries for `AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/**`,
   `.github/hooks/**`, `.github/agents/**`, `.github/skills/**`, `.mcp.json` + "Require review from Code Owners".
8. Personal skills from Claude Code: the CLI does not read `~/.claude/skills/` — copy/symlink to
   `~/.copilot/skills/` or `copilot skill add <dir>`.

## Keeping instructions lean

Do **not** paste ticket history into `AGENTS.md` or `.github/instructions/`. Update
`data/changes/STATUS.md`; keep instructions as a map + gates only. Don't edit instruction files mid-session
(it changes the request prefix and defeats provider-side prompt caching).
