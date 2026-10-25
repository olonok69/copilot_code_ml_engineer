# DEMO_RUNBOOK — GitHub Copilot presentation (40 slides)

This is the runbook for the **presenter**. Speaker guide: [`SPEAKER_GUIDE.md`](./SPEAKER_GUIDE.md) ·
deck: [`presentation/Copilot_Presentation.pptx`](./presentation/Copilot_Presentation.pptx) ·
reference: [`TECHNICAL_GUIDE.md`](./TECHNICAL_GUIDE.md).

> ⚠️ **What has been verified, and what hasn't.** The commands, flags, file paths and settings
> below come from [`docs/research/COPILOT_FINDINGS_2026-10-17.md`](./docs/research/COPILOT_FINDINGS_2026-10-17.md)
> (the docs as of 2026-10-17). Only the offline parts were run while this repo was built: the hook
> tests, the demo targets' `npm test`, and the deck build. **Do a full dry run on your own machine
> and Copilot build before you present.** Copilot changes between releases.

---

## What is live in *this* repo

When you run `copilot` from the repo root, or open the repo in VS Code with the **Copilot**
harness, these are picked up:

| Piece | Path | How to try it |
|---|---|---|
| Always-on memory | [`AGENTS.md`](./AGENTS.md), [`.github/copilot-instructions.md`](./.github/copilot-instructions.md), [`.github/instructions/`](./.github/instructions/) | `/instructions` in the CLI lists the sources |
| Skills | [`.github/skills/`](./.github/skills/): `audit`, `audit-python`, `deploy-staging` | `/audit`, `/audit-python`, `/deploy-staging` |
| Custom agent | [`.github/agents/refactor-scout.agent.md`](./.github/agents/refactor-scout.agent.md) | `copilot --agent refactor-scout`, or ask for it by name |
| Hook | [`.github/hooks/block-external-git.json`](./.github/hooks/block-external-git.json) + `.sh` / `.ps1` | ask the agent to `git push` → **denied** |
| MCP | [`.mcp.json`](./.mcp.json) (`mcpServers`, workspace) | `copilot mcp list` · `/mcp` |

The teaching copies under `examples/**` are **not** loaded until you copy them into `.github/`.
For Session 1, also point to the reusable personal methodology skills under
[`docs/ai-agents-code-methodology/copilot/skills/`](./docs/ai-agents-code-methodology/copilot/skills/).

---

## Preflight (T-30 min)

```bash
# 1. Node 22+ and the CLI (one of these)
node --version                      # must be >= 22 for the npm install
npm install -g @github/copilot      # or: brew install --cask copilot-cli / winget install GitHub.Copilot
copilot --version
copilot update                      # auto-update is on by default; force it once before the talk

# 2. Auth
copilot login                       # --device-code on remote terminals; or COPILOT_GITHUB_TOKEN

# 3. First launch in the repo -> answer the TRUST-FOLDER prompt ("trust for future sessions")
cd copilot_code_ml_engineer
copilot
#   in the session:
#   /instructions   -> AGENTS.md, copilot-instructions.md, instructions/*.instructions.md listed
#   /skills list    -> audit, audit-python, deploy-staging
#   /mcp            -> workspace servers + built-ins (github, playwright, fetch, time)
#   /context        -> note the "Custom Instructions" share for slide 14

# 4. Hook self-test (offline, both twins if you have PowerShell)
bash .github/hooks/test-block-external-git.sh            # expect "0 failures"
PS=1 bash .github/hooks/test-block-external-git.sh       # also the .ps1 twin

# 5. Demo targets
(cd ex_npm && npm install && npm test)
(cd ex_staging && npm test && npm run build)
(cd ex_app && python -m pip install pip-audit && python -m pip_audit -r requirements.txt)
```

**VS Code:** install the Copilot extension, sign in, open this folder, and pick the **Copilot**
harness in the Session Target control. For slide 5 you will switch to **Local** to show the
difference. Open **Chat: Open Customizations** and check that the three repo skills appear; show the
personal methodology skill pack as a separate live configuration. A missing repo skill may mean its
`name` doesn't match its folder name.

**WSL two-session setup:** use this course repo for Session 1, then open the user-approved
`/mnt/d/repos3/ILS_2` WSL workspace for Session 2. Confirm the personal skill list in Copilot
Customizations and inspect the MCP list in the active window; do not assume course-repo discovery
proves discovery in the target repo. The 2026-10-25 check verified bounded CodeGraph use and
offline/mocked skill checks, but left real preview, remote evidence fetch, authenticated Atlassian
reads, and shared `day` / `kg-refresh` operations gated. Keep those gates closed during the talk.

**Fallback if there is no network or login:** run every demo from the slide captions plus the
hook test (offline) and `copilot --help` / `copilot help permissions`.

---

## Command per slide

| # | Slide | Demo (≤ 2 min unless noted) |
|---|---|---|
| 1–3 | Title, agenda, divider | — |
| 4 | Five surfaces | `copilot --version`. Point out that `gh copilot` is the retired extension, not this tool. |
| 5 | Two VS Code engines | Switch Session Target **Copilot ↔ Local**. In Local, show a prompt file appearing as `/name`; in the Copilot harness it doesn't. |
| 6 | Feature matrix | Open [`docs/research/COPILOT_FINDINGS_2026-10-17.md`](./docs/research/COPILOT_FINDINGS_2026-10-17.md) §2 table. |
| 7 | Install / auth | `copilot login --help`; show the env-var token order. |
| 8 | Headless + billing | `copilot -p "Summarise AGENTS.md in 3 bullets" -s` · then `/usage` in an interactive session. |
| 9 | Two-level memory | Open [`AGENTS.md`](./AGENTS.md) (short), then a pointer target. |
| 10 | What loads where | `/instructions` in the CLI. Mention that the CLI also reads `CLAUDE.md` / `.claude/rules`, but not `~/.claude/CLAUDE.md`. |
| 11 | Permissions | Headless denial demo (below, **D1**). |
| 12 | Trust / sandbox | `copilot help permissions` · `/sandbox` (if enabled on your build). |
| 13 | Sessions | Run a `-p` command, copy the printed `copilot --resume=…`, resume it; `/rewind` on a scratch edit. |
| 14 | Context window | `/context`, then `/compact "keep only the hook design"`. |
| 15 | Hygiene | Slide only. |
| 16 | Caching | VS Code: Agent Debug Logs → Summary → **Cache Explorer** (only if your build has it). CLI: `/usage`. |
| 17 | MCP files | `copilot mcp list` · open [`.mcp.json`](./.mcp.json) — note `tools: ["*"]` and **no Playwright** entry. |
| 18 | MCP gotchas | Ask: “use context7 to look up python-pptx `add_picture`”. |
| 19 | Skills | Skill demos **S1–S3** (below). |
| 20 | Custom agent | “Use the refactor-scout agent to find every caller of `health` in ex_npm” — it must **not** edit files. |
| 21 | Subagents / fleet | `/subagents` · optional `/fleet` on a 2-task plan (costs credits). `/delegate` only if you want a live draft PR. |
| 22–23 | Hooks | Hook demo **H1** (below). |
| 24 | Automation | Show [`examples/automation/`](./examples/automation/) workflow (`--trust-folder`, explicit allow/deny) — do **not** run the cloud-agent task script live. |
| 25–33 | Session 2 · methodology | Slides + open [`examples/methodology/WORKFLOW.md`](./examples/methodology/WORKFLOW.md), [`docs/ai-agents-code-methodology/COPILOT_ADAPTATION.md`](./docs/ai-agents-code-methodology/COPILOT_ADAPTATION.md). Real-code demos: **R1** (below). |
| 34–37 | Session 2 · graph case study | `bash docs/knowledge-graph/kg_query.sh find letter`, then `kg_query.sh TKT-104` against the sanitised real graph (see [`docs/knowledge-graph/`](./docs/knowledge-graph/)). |
| 38 | Session 2 · parity evidence | Present the verified/gated boundary; do not run real preview, remote fetches, authenticated reads, or shared operations. |
| 39–40 | Appendix, close | — |

---

## Demo scripts

### S1–S3 — skills on the demo targets

| Skill | Target | What it does |
|---|---|---|
| `/audit` | [`ex_npm/`](./ex_npm/) | `npm audit` → safe fix → `npm test` |
| `/audit-python` | [`ex_app/`](./ex_app/) | `pip-audit -r requirements.txt` → smoke |
| `/deploy-staging` | [`ex_staging/`](./ex_staging/) | `npm test` → `build` → **asks for your OK** → `deploy:staging` (local server) → `GET /health` |

```text
/audit ex_npm
/audit-python ex_app
/deploy-staging ex_staging
```

On `/deploy-staging` the agent **must stop** before `npm run deploy:staging` and wait for you.
"Staging" here is a local server, with no cloud. Clean up with `npm run staging:stop`.

### H1 — the hook says no

Interactive, in the repo root (the folder must be trusted, otherwise the repo hook doesn't load):

```text
> commit nothing, just run: git push origin main
```

The expected result: the tool call is **denied** with the "Methodology handoff gate" reason. Then
try `gh pr create --fill` and `gh pr merge 1 --auto`, which should also be denied. Then `git status`,
which should run normally.

Offline proof that needs no Copilot: `bash .github/hooks/test-block-external-git.sh`. It runs a
canary first (a known deny), so a pass means something.

⚠️ Also try `/pr automerge` on a scratch repo. Whether first-party `/pr` commands go through
`preToolUse` is **UNVERIFIED**. Whatever you observe is the answer for your build, so say it out loud.

### D1 — headless allow/deny (slide 11)

```bash
copilot -p "Show the last 3 commits, then push the branch" -s \
  --allow-tool='shell(git:*)' \
  --deny-tool='shell(git push)' --deny-tool='shell(gh pr)' \
  --no-ask-user --trust-folder
```

The expected result: `git log` runs and the push is refused. Deny beats allow, even with
`--allow-tool='shell(git:*)'`. Without `--trust-folder`, the repo hook is skipped in `-p` mode
(only the `--deny-tool` layer protects you). Run it once without the flag to show that.

### R1 — CodeGraph / Serena / kg on real code

This course repo is not an indexed product codebase. For slides 28–29 and 37, **open your own
indexed repo** (one with `.codegraph/`) that has the CodeGraph and Serena servers in its `.mcp.json`
(template:
[`docs/ai-agents-code-methodology/copilot/mcp.json.example`](./docs/ai-agents-code-methodology/copilot/mcp.json.example)).
Then run:

```text
> use codegraph_explore to show who calls <a function you know>, then Serena find_referencing_symbols before we rename it
```

Launch `copilot` **from that repo's root**. Whether `--path .` resolves against the session cwd is
UNVERIFIED.

---

## Timings (90-minute slot)

| Block | Slides | Minutes |
|---|---|---|
| Opening + §00 surfaces | 1–6 | 12 |
| §01–§03 install, memory, permissions | 7–12 | 15 |
| §04–§06 sessions, context, caching | 13–16 | 10 |
| §07–§09 MCP, skills, agents | 17–21 | 15 |
| §10–§11 hooks, automation | 22–24 | 10 |
| Session 2 · methodology + graph | 25–38 | 25 |
| Appendix + close | 39–40 | 3 |

For 60 minutes, drop the live demos for 13, 16, 21 and 24 and show the slide only.

---

## Common failures

| Symptom | Cause | Fix |
|---|---|---|
| Hook doesn't fire in `copilot -p` / CI | `-p` skips repo hooks, workspace MCP and plugins in an **untrusted folder** | `--trust-folder` (or `GITHUB_COPILOT_PROMPT_MODE_REPO_HOOKS=true`) |
| Hook doesn't fire interactively | Folder not trusted, or hooks changed after the CLI started (hooks load at start) | Trust the folder; restart `copilot` |
| Hook "allowed" a push | The hook **timed out**. Timeouts fail **open** for every event | Keep the hook fast (no network); check `timeoutSec` |
| Every tool call is blocked | The hook script crashes. A non-zero exit fails closed for `preToolUse` | Run the test script; check `bash`/`python3` on PATH and the exec bit on `.sh` |
| Skill missing in VS Code | `name` ≠ folder name (lowercase-hyphen). VS Code drops it silently | Rename to match |
| Personal skill missing in the CLI | The CLI does **not** read `~/.claude/skills/` | Copy or symlink to `~/.copilot/skills/`, or `copilot skill add <dir>` |
| Two Playwright servers / duplicate tools | Playwright is **built into** the CLI and was also configured | Remove it from `.mcp.json` (keep it only in `.vscode/mcp.json` for Local if needed) |
| MCP server ignored | Missing `tools` (required in CLI configs), or `servers` used instead of `mcpServers` in `.mcp.json` | Add `"tools": ["*"]`; use the right top key |
| `.vscode/mcp.json` server absent in the Copilot harness | It uses `${input:...}`, and those are not forwarded | Move it to `.mcp.json` with env vars |
| Prompt file `/name` doesn't exist | You are in the Copilot harness or the CLI | Switch to Local, or convert it to a skill |
| Nested `AGENTS.md` ignored | The CLI reads root + cwd only; VS Code Local needs `chat.useNestedAgentsMdFiles` | Use `.instructions.md` with `applyTo` |
| Cost surprise | `/fleet`, autopilot, 1M context and cloud tasks all spend AI Credits | `--max-ai-credits`, `/usage`, `auto` model |
