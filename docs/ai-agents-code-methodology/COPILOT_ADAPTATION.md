# Adapting the AI-agent methodology for GitHub Copilot

> Purpose: take the methodology from [`README.md`](README.md) / [`TECHNICAL.md`](TECHNICAL.md) and run it
> end-to-end with **GitHub Copilot**, keeping the same tool *roles* used in Claude Code and Cursor
> (CodeGraph, Serena, Playwright, Context7, the ticket graph `kg`, deterministic oracles).
>
> Copy-ready surface (instructions, skills, MCP, hooks, agents, cloud-agent setup): [`copilot/`](copilot/).
> Every Copilot-specific claim here comes from the research notes
> [`../research/COPILOT_FINDINGS_2026-10-17.md`](../research/COPILOT_FINDINGS_2026-10-17.md)
> (docs verified **2026-10-17**; Copilot moves fast — re-check before reuse). Items marked
> **UNVERIFIED** or **NOT DOCUMENTED** could not be confirmed in the docs; test them on your build.
>
> Sibling guide for Cursor: the Cursor volume's `CURSOR_ADAPTATION.md`
> ([`cursor_code_ml_engineer`](../../../cursor_code_ml_engineer/)).
>
> **This replaces an earlier `COPILOT_ADAPTATION.md`** that was tool-agnostic prose with no Copilot paths,
> flags or config. None of its product claims was false, but it predated the Copilot CLI GA, the cloud
> agent rename, hooks, skills and AI Credits billing. The tool-agnostic parts that still hold (fallback,
> planning template, KPIs, rollout) are kept below.

---

## 1) What transfers unchanged

1. Plan -> agree -> implement.
2. Verify via the consumer-visible output contract, not internal functions.
3. Solve the general class of issue, not one sample input.
4. Keep a durable decision trail (why, what changed, how verified).
5. Human owns irreversible external actions (merge, deploy, stakeholder comms).
6. **Canary the instrument before believing it** — a filter/lock/scan that returns "nothing" or "ok"
   without a known-answer check is not evidence.
7. **Read the machine/session role before writing shared state** — point the always-loaded instructions
   at a machine-local `IDENTITY.md`.

If you keep only five rules, keep **1–5**. Add **6–7** as soon as the trail is shared across machines or people.

---

## 2) "Copilot" is five surfaces — name the one you mean

| Surface | What it is | What it loads (methodology-relevant) |
|---|---|---|
| **Copilot CLI** (`copilot`) | Terminal agent, npm `@github/copilot`, GA 2026-02-25. ⚠️ Not the retired `gh copilot` extension. | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.github/instructions/**`, `.claude/rules/**` (git root **and** cwd, merged); skills; `.github/agents/`; `.github/hooks/*.json`; `.mcp.json` / `.github/mcp.json` (trusted folder only) |
| **VS Code — Copilot harness** | Same runtime as the CLI ("Agent Host") | Shares `~/.copilot/*`, `.github/hooks` (CLI schema), `.mcp.json`, skills and agents with the CLI |
| **VS Code — Local harness** | Classic agent mode in the extension host | `chat.*` settings, `.vscode/mcp.json` (`servers`), prompt files, `handoffs`, its **own hook schema** |
| **Copilot cloud agent** (formerly "coding agent") | Ephemeral GitHub Actions Linux sandbox; opens a draft PR | Repo instructions (nearest `AGENTS.md` wins), `.github/skills`, `.github/agents`, `.github/hooks/*.json` (bash only), MCP JSON pasted in repo **Settings → Copilot**, `copilot-setup-steps.yml` |
| **Copilot code review** | PR reviewer (github.com + IDEs); automatic via rulesets | Instructions, `AGENTS.md`, `CLAUDE.md`, `REVIEW.md`, `.github/skills` — **from the head branch**; MCP tools only with `readOnlyHint: true`; hooks NOT DOCUMENTED |

JetBrains: agent mode and MCP supported; skills, custom agents, custom instructions and prompt files are
**Preview**.

---

## 3) Claude Code → Copilot surface map

| Role in the methodology | Claude Code | GitHub Copilot |
|---|---|---|
| Always-loaded orientation | `CLAUDE.md` | Root `AGENTS.md` (all surfaces) + optional small `.github/copilot-instructions.md` |
| Scoped gates | `.claude/rules` `paths:` | `.github/instructions/*.instructions.md` `applyTo` (+ `excludeAgent`); the CLI also reads `.claude/rules/*.md` |
| Eager import | `@path` | `@path` in `AGENTS.md` / `CLAUDE.md` / `copilot-instructions.md` (CLI). VS Code expansion: NOT DOCUMENTED |
| Personal memory | `~/.claude/CLAUDE.md` | `~/.copilot/copilot-instructions.md` — ⚠️ the CLI does **not** read `~/.claude/CLAUDE.md` |
| Skills (`/kg`, `/day` …) | `~/.claude/skills/` | `.github/skills/<name>/SKILL.md` (project) · `~/.copilot/skills/` (personal) — ⚠️ the CLI does **not** read `~/.claude/skills/` (VS Code does) |
| Hard gates | hooks + `settings.local.json` allowlist | `.github/hooks/*.json` `preToolUse` deny / exit 2 + CLI `--deny-tool` (repo files cannot hold allow/deny lists) |
| Plan gate | plan mode | CLI `/plan`, `--plan`, Shift+Tab (enforced at the tool layer — "safety net, not a guarantee"); VS Code Plan agent |
| Read-only research | subagents | `.github/agents/*.agent.md` with a read-only `tools` list; built-ins `explore`, `research` |
| Parallel work | Agent Teams | `/fleet`, background subagents (`write_agent` messaging), `/delegate` to the cloud agent |
| Headless | `claude -p` | `copilot -p "…" -s` + explicit `--allow-tool` / `--deny-tool` (+ `--trust-folder` for repo hooks) |
| Auto memory | `MEMORY.md` / claude-mem | Copilot Memory (cloud, preview, 28-day expiry) · VS Code `/memories` · CLI `/chronicle` — complements, never source of truth |

---

## 4) The 11 stages in Copilot

| # | Stage | Copilot practice | Preferred tools |
|---|---|---|---|
| 1 | Orient | Instructions load automatically; `/day start` skill; `kg` skill; `git`/`gh` read-only state | skills `day`, `kg` · ledgers · shell |
| 2 | Inbound triage | Reproduce at the **output contract** before any edit | built-in Playwright (CLI) · contract fixture |
| 3 | Provenance | Repro on the pre-change baseline | shell + git |
| 4 | Investigate | Deterministic oracle before a paid model loop | CodeGraph → Serena → `_diag_*.py` |
| 5 | Plan | `/plan` (CLI) or the Plan agent (VS Code); `methodology-plan` skill; explicit agreement | plan mode |
| 6 | Implement | TDD RED → GREEN, minimal diff | editor tools · test runner |
| 7 | Verify | Outbound gate ×5 (canary instrument · contract via the real writer · member list, not totals · shipping artifact · look at the output) | tests · Playwright · Docker |
| 8 | Document | Write-once ledgers under `data/changes/` | templates |
| 9 | Sanitise | Scan **added** staged lines | skill `sanitise-diff` |
| 10 | Hand off | Prepare branch + handover; **no** push / PR / merge | `block-external-git` hook + `--deny-tool` |
| 11 | Review + persist | Triage review findings (Copilot code review included) with stated reasons; refresh the graph | `kg-refresh` (publisher) |

Optional upgrade over Cursor: a `sessionStart` hook of type `prompt` (`{"type":"prompt","prompt":"/day start"}`)
*enforces* the start-of-day routine — CLI, new interactive sessions only.

---

## 5) Memory: tiers 0 / 1 / 2 in Copilot

| Tier | Methodology | Copilot artifact |
|---|---|---|
| 0 — machine-local | `IDENTITY.md` (gitignored, never synced) | Pointer from `AGENTS.md`; or read via a `sessionStart` hook returning `additionalContext` (CLI/cloud); or personal `~/.copilot/copilot-instructions.md` |
| 1 — always loaded | lean orientation + pointers | Root `AGENTS.md` + small `.github/copilot-instructions.md` (the only file code review in VS Code / Visual Studio / Eclipse reads) + `.github/instructions/*.instructions.md` with `applyTo` |
| 2 — on demand | `data/changes/**` | Unchanged; read by path. Use `@path` imports only for what must be eager (CLI). Prefer pointers |

**Nested `AGENTS.md` behaves differently per surface:** the cloud agent uses the *nearest* file; the CLI
reads only the git root and the cwd; VS Code Local needs `chat.useNestedAgentsMdFiles` (off by default).
Safe pattern: per-folder rules go in `.instructions.md` with `applyTo: "subdir/**"`.

---

## 6) Tool prevalence and MCP

Encode the order in `instructions/01-tool-prevalence.instructions.md`: CodeGraph `codegraph_explore` first
(treat its source as already read) → Serena `find_referencing_symbols` before rename/delete → grep only for
literals; `kg` before grepping `data/changes/`.

| Server | CLI + VS Code Copilot harness | VS Code Local harness | Cloud agent |
|---|---|---|---|
| **CodeGraph** | `.mcp.json`: `"codegraph": {"command":"codegraph","args":["serve","--path",".","--mcp"],"tools":["*"]}` | `.vscode/mcp.json` with `--path ${workspaceFolder}` | Repo MCP settings + install via `copilot-setup-steps.yml` |
| **Serena** | stdio via `uvx --from git+https://github.com/oraios/serena serena start-mcp-server` | same | same as CodeGraph |
| **Playwright** | **Built in to the CLI — do not add it** | Add it in `.vscode/mcp.json` if needed | Default on, localhost only |
| **Context7** | `{"type":"http","url":"https://mcp.context7.com/mcp","tools":["*"]}` | same | Needs a firewall allow rule for `mcp.context7.com` |

Notes: `tools` is **required** in CLI and cloud configs; `.vscode/mcp.json` uses `servers`, not
`mcpServers`; servers using `${input:...}` are not forwarded to the Copilot harness; workspace MCP needs
**folder trust**; `${workspaceFolder}` is VS Code-only and whether `--path .` resolves against the session
cwd is **UNVERIFIED** (launch from the repo root, or use an absolute path in `~/.copilot/mcp-config.json`).
Cloud agent: tools only (no resources/prompts, no OAuth remote servers), secrets prefixed `COPILOT_MCP_`,
tools run without approval → allowlist read-only tools.

---

## 7) Skills

Project copies: `.github/skills/<name>/SKILL.md` (CLI, VS Code, cloud agent, code review). Rules for every
ported skill: drop `trigger:` (not a Copilot key; whether unknown keys are ignored is UNVERIFIED); keep
`name` lowercase-hyphen and equal to the folder name (VS Code silently drops violations); `description`
≤ 1024 characters.

| Skill | Surfaces | Notes |
|---|---|---|
| `day` | CLI, VS Code | Local shell + S3 sync. Not for the cloud agent (no `~/.aws`, ephemeral). |
| `atlassian` | CLI, VS Code | Local token file. With the CLI sandbox on, add the Atlassian host to `sandbox.userPolicy.network.allowedHosts`. Skills have no `excludeAgent`; to keep it off the cloud agent, do not commit it — put it in `~/.copilot/skills` (other hiding mechanisms UNVERIFIED). |
| `evidence` | CLI, VS Code | Local only; read-only enforced in the script. Sandbox path grants for `~/.aws` UNVERIFIED — inspect with `/sandbox policy`. `allowed-tools` grammar UNVERIFIED. |
| `kg` | all | Deterministic scripts — direct port. |
| `kg-refresh` | CLI (publisher) | Semantic step via CLI subagents (`task` / `/fleet`), or keep running it from Claude Code. Publisher guard stays in the script. |
| `methodology-plan`, `sanitise-diff` | all | Pure procedure. |

Personal skills from Claude Code: copy or symlink to `~/.copilot/skills/` or `~/.agents/skills/`, or
`copilot skill add <dir>` / `COPILOT_SKILLS_DIRS`.

---

## 8) Human owns merge — now enforceable, with two new holes to close

The old guide stated "no direct merge/deploy by agent" as policy. In Copilot it can be **enforced**:

1. **`preToolUse` deny hook** — `.github/hooks/block-external-git.json` (CLI, cloud agent, VS Code Copilot
   harness; parsed by VS Code Local too). Denies `git push`, `gh pr create|merge|ready`, `gh api …/merge`,
   `gh release create`, `terraform apply`, `kubectl apply`, `helm upgrade|install`, `aws … deploy` with
   `permissionDecision: "deny"` **and exit 2** (the one blocking signal documented in both schemas). The
   script handles `toolArgs` as string or object and the snake_case `tool_input` shape. ⚠️ Timeouts are
   **fail-open**; crashes fail closed — keep it fast.
2. **CLI flags** — `--deny-tool='shell(git push)' --deny-tool='shell(gh pr)'`. Deny beats allow, even with
   `--yolo`. CLI flags are never persisted, so this is a habit/alias or a CI line, not a repo setting.
3. **Cloud agent structural limits** — pushes only to its own `copilot/` branch (or the PR branch when you
   `@copilot` a PR), cannot run `git push` directly, **cannot mark ready, approve or merge**; workflows wait
   for a human "Approve and run workflows"; the requester cannot approve the PR.
4. **CODEOWNERS + "Require review from Code Owners"** on `.github/hooks/**`, `.github/agents/**`,
   `.github/skills/**`, `.github/instructions/**`, `.mcp.json`, `AGENTS.md`, `.github/copilot-instructions.md`
   — code review reads instructions from the **head** branch, so a PR can otherwise rewrite its own reviewer.
5. **`permissions.disableBypassPermissionsMode`** (`"disable"` or `"allow-auto-only"`) in user / managed /
   MDM settings blocks `--yolo` and the other allow-all flags. Org-wide `permissions.deny` exists only as
   enterprise-managed / MDM settings.
6. **Trust in `-p` mode** — in `-p` / CI, repo hooks are **skipped** in an untrusted folder unless
   `--trust-folder` (or `GITHUB_COPILOT_PROMPT_MODE_REPO_HOOKS=true`). A CI gate without it is decorative.

**New holes (did not exist when the old guide was written):**

- ⚠️ **CLI `/pr create | auto | automerge`** — first-party slash commands that create and **merge** PRs.
  Whether they pass through `preToolUse` as shell/`gh` calls is **UNVERIFIED**. Name them as human-only in
  `AGENTS.md`, and **test the hook against them** on your build (expect a deny; if the command bypasses the
  hook, treat it as a policy-only rule plus branch protection).
- ⚠️ **Copilot code review approvals** (preview, **off by default**) can count toward required approvals.
  Keep it **off** if "the human owns merge". Also keep "no unexplained bot-review dismissal": triage Copilot's
  review comments like a human's.

---

## 9) Read-only subagents

`.github/agents/refactor-scout.agent.md` with `tools: ["read", "search"]`. A read-only **tools list** is the
enforcement; prose is not. Custom agents spawned as subagents get **no** repo instructions unless
`include-custom-instructions: true` (CLI). Invoke with `copilot --agent refactor-scout`, by name in a prompt,
or `/fleet … use @refactor-scout`. Built-ins `explore` / `research` are already read-mostly.

Subagent limits: concurrency is plan-based; max depth is **6** in the reference table but **4** in the
env-var table — a documentation inconsistency; verify on your build (`COPILOT_SUBAGENT_MAX_DEPTH`).

---

## 10) GSD and memory substitutes

GSD is Claude-Code-only; no first-party Copilot equivalent of its phase/roadmap state machine. Nearest pieces:
plan mode (`/plan`, `--plan`), plan-then-autopilot (`--plan --mode autopilot`), `/fleet` for wave-parallel
execution, role agents (planner / executor / verifier) in `.github/agents/`, autopilot caps
(`--max-autopilot-continues`, `--max-ai-credits`), an `agentStop` hook with `decision: "block"` as a
"verify before stop" gate, VS Code `handoffs` (Local harness only). **Spec Kit** (`github/spec-kit`) is
reported to support Copilot — **third-party coverage only, current version UNVERIFIED**. The state store
stays the methodology's own ledgers (`STATUS.md`, `PLAYBOOK.md`).

Memory: Copilot Memory (cloud, preview, repo facts + user prefs, unused entries expire after **28 days**),
the VS Code memory tool (local `/memories`), and CLI session history (`/chronicle`). Canonical, reviewable
memory stays in `data/changes/` + `AGENTS.md` (write-once). Whether claude-mem's search server can be
attached as a plain MCP server: UNVERIFIED.

---

## 11) No-knowledge-graph mode (fallback) — unchanged

1. `data/changes/STATUS.md` newest-first + `data/changes/<ticket-or-issue-id>/` folders.
2. Lexical search by symptom terms, key function names and contract fields before broad reading.
3. Commit/PR history as a lightweight graph substitute (file overlap, message keywords).
4. A short "danger zones" list (`SHARP_EDGES.md`).

~80% of the graph's value at minimal setup. Copilot Memory and `/chronicle` can help recall but are
**non-canonical** aids.

---

## 12) Fast path — install the Copilot pack (30–60 minutes)

```powershell
# 1) Ledger templates (tool-agnostic)
Rename-Item data/changes/ai-agent-methodology/scripts/bootstrap-new-repo.ps1.txt bootstrap-new-repo.ps1 -ErrorAction SilentlyContinue
pwsh data/changes/ai-agent-methodology/scripts/bootstrap-new-repo.ps1

# 2) Copilot surface (AGENTS.md, instructions, skills, agents, hooks, MCP, cloud-agent setup)
Rename-Item data/changes/ai-agent-methodology/scripts/bootstrap-copilot-repo.ps1.txt bootstrap-copilot-repo.ps1 -ErrorAction SilentlyContinue
pwsh data/changes/ai-agent-methodology/scripts/bootstrap-copilot-repo.ps1
```

Then: `chmod +x .github/hooks/*.sh` (and `git update-index --chmod=+x` when the human commits) · run
`bash .github/hooks/test-block-external-git.sh` · `codegraph init` · launch `copilot` from the repo root and
trust the folder · `/mcp` and `/skills` to confirm what loaded · `/instructions` to see which instruction
files are active · fill `STATUS.md`, 3–5 `SHARP_EDGES.md` entries and the contract paragraph in `AGENTS.md`
· fill the working agreement · run **one** issue end-to-end. File list: [`copilot/README.md`](copilot/README.md).

---

## 13) Planning template (issue start)

Same template as the other volumes (also the body of the `methodology-plan` skill):

```text
Issue: <tracker-id> - <short title>

1) Contract confirmation
- Consumer-visible contract: <API/UI/event/artifact>
- Symptom reproduced there: <yes/no + evidence source>

2) Provenance
- Reproduced on pre-change baseline: <yes/no>
- Classification: <regression | pre-existing>

3) Root cause hypothesis
- Deterministic probe used: <probe>
- Result: <what proved the hypothesis>

4) Fix shape (general-case)
- Structural class addressed: <class>
- Why not instance-specific: <one sentence>

5) Verification plan
- RED test / scoped suite / regression suite / contract repro / runtime parity

6) Handover outputs
- Change summary doc · acceptance criteria · open follow-ups
```

---

## 14) Folder structure (target repo)

```text
AGENTS.md                                   # tier 1, all surfaces
.github/
  copilot-instructions.md                   # small; code review in IDEs reads only this
  instructions/
    00-methodology-core.instructions.md
    01-tool-prevalence.instructions.md
    02-gates-and-handoff.instructions.md
    atlassian.instructions.md
  skills/{day,atlassian,evidence,kg,kg-refresh,methodology-plan,sanitise-diff}/SKILL.md
  agents/refactor-scout.agent.md
  hooks/block-external-git.{json,sh,ps1}
  workflows/copilot-setup-steps.yml         # cloud agent only; must be on the default branch
  copilot/settings.json                     # optional; only allowlisted keys are read
.mcp.json                                   # CLI + VS Code Copilot harness (trusted folder)
.vscode/mcp.json                            # VS Code Local harness (`servers`)
CODEOWNERS                                  # protect the files above
data/changes/...                            # unchanged
```

---

## 15) Governance policy (minimum)

1. No push / PR / merge / deploy / customer comms by the agent unless the human explicitly requests that
   action in-session — and the hook still denies it; the human runs it.
2. Copilot code-review approvals stay **off**; `/pr automerge` is human-only.
3. No secrets or forbidden identifiers in committed artifacts; `sanitise-diff` before every handoff.
4. No "fixed" claim without command-level evidence.
5. No silent dismissal of automated-review findings.
6. No instruction / hook / MCP / agent changes that weaken gates without explicit acknowledgement (CODEOWNERS).

---

## 16) 14-day rollout and success criteria

- **Days 1–2:** bootstrap ledgers + Copilot pack; wire MCP; test the hook (incl. `/pr` commands); define the contract + 3–5 sharp edges; agree the working agreement.
- **Days 3–5:** one full 11-stage run on a real issue; prove the plan gate, RED → GREEN, contract outbound, sanitise and human-owned push.
- **Days 6–10:** add `kg` or harden the STATUS fallback; add CODEOWNERS; decide cloud-agent scope (which skills are committed vs personal).
- **Days 11–14:** CI with `copilot -p` + `--trust-folder` + explicit `--deny-tool`; publish a one-page "how we run Copilot here".

KPIs for 2–4 weeks: reopened defects per merged fix · time from first repro to verified contract fix ·
% of fixes with an explicit RED → GREEN trace · % of handovers with actionable acceptance criteria ·
number of "pre-existing, not regression" findings proven early.

---

## 17) Honest gaps

| Capability | Status in Copilot |
|---|---|
| 11 gates + durable trail | Full parity |
| CodeGraph / Serena / Context7 | Parity via MCP; Playwright built in to the CLI |
| Plan gate | Parity (enforced plan mode in the CLI) |
| Blocking external actions | **Stronger than policy** — hook + `--deny-tool` + cloud-agent limits; the `/pr automerge` path is UNVERIFIED |
| Prompt-caching control | None (no `cache_control`, TTL or env var); VS Code Cache Explorer is diagnose-only |
| Repo-level allow/deny lists | Not possible in repo files; hooks or managed settings |
| GSD | Not available; plan mode + `/fleet` + role agents |
| `~/.claude` skills / memory | Not read by the CLI; copy to `~/.copilot/` |

Aim for **methodology parity**, not product-clone parity. Start with [`START_HERE.md`](START_HERE.md).
