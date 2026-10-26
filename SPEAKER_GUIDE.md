# GitHub Copilot — Speaker guide (course in two sessions)

> Versión en español: [`GUIA_PRESENTACION.md`](./GUIA_PRESENTACION.md).

> Deck: [`presentation/Copilot_Presentation.pptx`](./presentation/Copilot_Presentation.pptx)
> (regenerate with [`presentation/build_pptx_copilot.py`](./presentation/build_pptx_copilot.py)).
> Copy-paste detail: [`TECHNICAL_GUIDE.md`](./TECHNICAL_GUIDE.md) · live demos per slide:
> [`DEMO_RUNBOOK.md`](./DEMO_RUNBOOK.md) · runnable material: [`examples/`](./examples/).

> This is the guide for the **speaker**. Each section matches a block of slides and gives the story
> to tell, the points that matter, and a closing line 🗣️ you can say as it stands. Audience:
> **technical / developers**. This is the **GitHub Copilot volume** of the course. Its siblings are
> the [Claude Code volume](https://github.com/olonok69/claude_code_ml_engineer) and the
> [Cursor volume](https://github.com/olonok69/cursor_code_ml_engineer) (the [Pi volume](../pi_code_ml_engineer),
> built alongside). The methodology and graph remain distinct topics, but are taught together in Session 2.
>
> The deck has **two sessions** plus an appendix:
> - **Session 1 — GitHub Copilot (§00–§11):** five surfaces, two VS Code engines, and the file each
>   surface reads.
> - **Session 2 — The methodology and ticket graph (§12–§16):** how you actually work with an agent in production. It
>   does not depend on the tool. It started in Claude Code, moved to Cursor, and now runs on Copilot.
>   The graphify case study is the final topic within this same session.
>
> **Verification note:** every Copilot claim in this guide comes from
> [`docs/research/COPILOT_FINDINGS_2026-10-17.md`](./docs/research/COPILOT_FINDINGS_2026-10-17.md),
> which was checked against docs.github.com and code.visualstudio.com on **2026-10-17**. When the
> docs say nothing, this guide says **NOT DOCUMENTED / UNVERIFIED**. Copilot moves fast, so re-check
> the findings before you teach.

---

## Slide index

| # | Slide | Section |
|---|---|---|
| 1 | Title | — |
| 2 | Agenda | — |
| 3 | Session 1 divider | — |
| 4 | “Copilot” is five different surfaces | §00 |
| 5 | VS Code has two Copilot engines | §00 |
| 6 | Feature × surface matrix | §00 |
| 7 | Install, log in, start | §01 |
| 8 | copilot -p, models, and AI Credits | §01 |
| 9 | The two-level pattern, in Copilot files | §02 |
| 10 | What loads where | §02 |
| 11 | Allow, deny — and deny wins | §03 |
| 12 | Trusted folders, sandbox, cloud guardrails | §03 |
| 13 | Sessions: resume, fork, rewind, delegate | §04 |
| 14 | Context window | §05 |
| 15 | Context hygiene | §05 |
| 16 | Caching: the honest answer | §06 |
| 17 | One protocol, four config files | §07 |
| 18 | MCP gotchas per surface | §07 |
| 19 | Skills: one SKILL.md, most surfaces | §08 |
| 20 | Custom agents | §09 |
| 21 | Subagent, /fleet, or cloud agent? | §09 |
| 22 | Hooks: the deterministic veto | §10 |
| 23 | The portable recipe: block push, PR, merge | §10 |
| 24 | From copilot -p to agents in the cloud | §11 |
| 25 | Session 2 divider | — |
| 26 | The real 11-stage flow | §12 |
| 27 | The outbound gate is FIVE checks | §12 |
| 28 | Which tool the agent uses, and when | §13 |
| 29 | CodeGraph + Serena on every Copilot surface | §13 |
| 30 | GSD: Claude Code only — the Copilot substitutes | §13 |
| 31 | From Claude Code to Copilot | §14 |
| 32 | New holes — and how merge stays human | §14 |
| 33 | From transporting (tarball) to sharing (S3) | §15 |
| 34 | Session 2 continued: ticket graph case study | — |
| 35 | The problem, and the pipeline | §16a |
| 36 | The current graph: 3,921 nodes, 178 communities | §16b |
| 37 | Using it from Copilot | §16c |
| 38 | ILS_2 WSL parity check: verified vs gated | — |
| 39 | Claude Code → Cursor → Copilot | Appendix |
| 40 | Close + sources | — |

---

## Slides 1–3 — Opening

**Story:** This is the third volume of the course. The audience already knows (or will meet) the
same method in Claude Code and Cursor. The message for this volume is simple: **"Copilot" is not one
product.** It is a terminal agent, two different engines inside VS Code, a JetBrains plugin, a cloud
agent that opens PRs, and a PR reviewer. Most wrong claims about Copilot come from mixing these up.

The agenda (slide 2) uses the section numbers that run through every document in the repo: §00–§11
in Session 1 and §12–§16 in Session 2. When someone asks a question, send them to the same
§ number in [`TECHNICAL_GUIDE.md`](./TECHNICAL_GUIDE.md).

🗣️ *"Same method, third agent. This time the hard part isn't the method. It's knowing which Copilot you're talking to."*

---

# SESSION 1 — GitHub Copilot

## §00 Surfaces map (slides 4–6)

**Story (slide 4):** Name the five surfaces before you say anything else:

- **Copilot CLI (`copilot`)**: the terminal agent, npm package `@github/copilot`, GA on
  2026-02-25. It is **not** the old `gh copilot` extension, which is retired. Older tutorials that
  show `gh copilot suggest` describe a different product.
- **VS Code agent**: has *harnesses*, namely **Copilot**, **Local**, Claude, Codex, plus a **Cloud**
  target.
- **JetBrains agent mode**: agent mode and MCP are supported. Skills, custom agents, custom
  instructions and prompt files are **Preview**.
- **Copilot cloud agent**: this was called the "coding agent". You give it an issue, a prompt, an
  API call or an automation. It works in an ephemeral GitHub Actions sandbox and opens a **draft PR**.
- **Copilot code review**: a PR reviewer that rulesets can request automatically.
- Also: Copilot on github.com (chat, the Agents page, Spaces) and the desktop Copilot app.

**Story (slide 5) — the most important structural fact in Session 1:** VS Code has **two Copilot
engines**.

- The **Copilot harness** runs the same runtime as the CLI. It shares `~/.copilot`, the
  `.github/hooks` schema, `.mcp.json`, skills and agents with the CLI.
- The **Local harness** is classic agent mode. It has its own `chat.*` settings, its own hook schema
  (PascalCase, `hookSpecificOutput`) and `.vscode/mcp.json` with `servers`. It is the **only** place
  where prompt files and `handoffs` work.

Pick the harness in the **Session Target** control, then read the docs for that harness.

**Story (slide 6):** Walk the matrix one row at a time. Three cells deserve a pause:

- **Prompt files** work only in VS Code Local (plus Visual Studio and JetBrains).
- **Hooks** exist almost everywhere, but VS Code Local uses a **different schema**.
- **Code review hooks** are **NOT DOCUMENTED**.

The full matrix, with a source for every cell, is in the
[findings file](./docs/research/COPILOT_FINDINGS_2026-10-17.md).

🗣️ *"Before any 'Copilot can / can't' claim, ask two questions: which surface, and which harness?"*

---

## §01 Install, auth, headless, models, billing (slides 7–8)

**Story (slide 7):** Installing takes one line: npm (Node 22+), Homebrew, winget, or the install
script. For auth, the CLI takes tokens in a fixed order: `COPILOT_GITHUB_TOKEN` > `GH_TOKEN` >
`GITHUB_TOKEN`. A PAT must be **fine-grained, user-owned**, with the "Copilot Requests" permission.
In Actions, the workflow needs `permissions: copilot-requests: write`, and the org policy must allow
CLI billing.

On the first launch in a repo, the CLI asks whether to **trust the folder**. That prompt comes back
on slide 12, because CI never sees it. `copilot init` writes `.github/copilot-instructions.md`.

**Story (slide 8):** `copilot -p` is the foundation of every automation in §11:

```bash
copilot -p "Explain ./complex.ts" -s
copilot -p '...' -s --allow-tool='shell(git:*)' --deny-tool='shell(git push)' --no-ask-user
copilot -p '...' --trust-folder          # load repo hooks/MCP for this run
copilot -p '...' --max-ai-credits=5      # soft cap per response
```

**Models:** the CLI default is `claude-sonnet-5.5`. Choose another with `--model`, `COPILOT_MODEL` or
`/model`. `auto` lets Copilot pick, with a 10% discount on paid plans.

**Billing changed on 2026-06-01** to **GitHub AI Credits** (1 credit = $0.01). Cost is per token,
and **cached-input and cache-write tokens are billed too**. "Premium requests" and multipliers are
legacy. They apply only to annual Pro/Pro+ plans that stayed on the old model. Code completions are
not billed.

🗣️ *"The CLI is `copilot`, and you pay in AI Credits. If a slide says 'premium requests', it's from last year."*

---

## §02 Memory and instructions (slides 9–10)

**Story (slide 9):** This is the same two-level pattern as in the other volumes, built from
Copilot's files:

- **Level 1 (always loaded, small):** a root `AGENTS.md`, which every surface reads, so it is the
  one shared voice with Claude Code and Cursor. Add an optional small
  `.github/copilot-instructions.md` and scoped `.github/instructions/*.instructions.md` files with
  `applyTo` globs.
- **Level 2 (on demand):** `data/changes/STATUS.md`, `PLAYBOOK.md`, `SHARP_EDGES.md`, per-ticket
  ledgers.
- **Tier 0 (machine-local):** `IDENTITY.md` (gitignored), or `~/.copilot/copilot-instructions.md`
  for personal instructions. ⚠️ The CLI does **not** read `~/.claude/CLAUDE.md`.

The CLI also supports eager `@path` imports in `AGENTS.md`, `CLAUDE.md` and
`copilot-instructions.md`. Use them only for what must be eager. Whether VS Code expands `@path` is
NOT DOCUMENTED.

**Story (slide 10):** five traps about what loads where:

1. **The CLI merges everything:** `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`, `.instructions.md`,
   `.claude/rules`, `copilot-instructions.md`, read at the git root **and** the cwd. Your Claude
   Code rules come along for free.
2. **Nested `AGENTS.md` behaves differently per surface.** The CLI reads root + cwd only. The cloud
   agent uses "nearest wins". VS Code Local needs `chat.useNestedAgentsMdFiles`, which is off by
   default.
3. **The safe pattern for per-folder rules:** `.instructions.md` with `applyTo: "subdir/**"`. Add
   `excludeAgent: "code-review"` (or `"cloud-agent"`) when a rule makes no sense for that agent.
4. **Prompt files are Local-only.** The CLI equivalent is a skill.
5. **Copilot Memory is not your ledger.** It lives in the cloud, is in preview, and memories expire
   after 28 days. The VS Code `/memories` tool and CLI `/chronicle` are separate systems again.

Material: [`examples/agents-md/`](./examples/agents-md/).

🗣️ *"`AGENTS.md` is the only file every surface reads. Keep it to a 30-second onboarding: pointers, not copies."*

---

## §03 Permissions, trust, sandbox (slides 11–12)

**Story (slide 11):** CLI permissions use the pattern `Kind(argument)`: `shell(git:*)`,
`shell(git push)`, `write(src/*.ts)`, `read(.env)`, `MyMCP(tool)`, `url(github.com)`. **Deny always
beats allow**, even with `--yolo`. Flags are never persisted. Approvals you save live in
`~/.copilot/permissions-config.json`.

Then the key fact: **the repo cannot hold an allow/deny list.** `.github/copilot/settings.json`
accepts only a short list of keys. `permissions.*` rules exist only as enterprise-managed or MDM
settings. So a team rule like "never push" must be a **hook** (§10). VS Code has the same gap: a
`false` terminal auto-approve rule only *asks* for approval. To block, the docs point to a
`PreToolUse` deny hook. `permissions.disableBypassPermissionsMode` can switch off `--yolo`.

**Story (slide 12):** three layers:

- **Trusted folders.** Trust gates repo hooks, workspace MCP, repo plugins and the repo model. In
  `-p` mode, an untrusted folder **silently skips them** unless you pass `--trust-folder` (or set the
  `GITHUB_COPILOT_PROMPT_MODE_*` variables).
- **Local sandbox.** GA on 2026-10-07: `/sandbox enable` or `--sandbox`. It controls network hosts,
  denied paths, and credential masking per host. A repo cannot override it.
- **Cloud agent.** All tools are pre-approved, and a hook that answers `"ask"` counts as `"deny"`.
  The agent pushes only to its `copilot/` branch. It cannot mark a PR ready, approve it or merge it.
  Humans approve workflow runs.

Material: [`examples/permissions/`](./examples/permissions/).

🗣️ *"Allowlists decide what runs without asking. Only a hook can veto by content, and in CI the hook loads only if you trusted the folder."*

---

## §04 Sessions (slide 13)

**Story:** These are the session controls you will actually use:

- `--continue` / `--resume` (every `-p` run prints its session ID)
- `/fork`, which works while the agent is running
- `/rewind`: conversation only, or conversation **and** files, with no git needed
- `/share`, `/remote` (steer from the web, mobile or VS Code)
- `/delegate`, or a leading `&`, which hands the session to the cloud agent as a branch and draft PR

⚠️ The "checkpoints" listed by `/session checkpoints` are **compaction summaries**, not file
snapshots. In VS Code, the Session Target control moves a session between harnesses or to Cloud,
and the history comes along.

🗣️ *"A compaction checkpoint is a summary. Only `/rewind` with files puts your tree back."*

---

## §05 Context window (slides 14–15)

**Story (slide 14):** `/context` shows where the tokens go: system prompt, custom instructions,
system tools, MCP tools, messages, free space. Auto-compaction starts at about **80%** and pauses
at about 95%. `/compact [focus]` runs it by hand, and **a compaction cannot be undone**. Tool output
over **20 KiB** goes to a temp file, and the model gets the path plus a preview
(`COPILOT_LARGE_OUTPUT_THRESHOLD_BYTES` changes the limit). In VS Code, the control in the chat input
shows the same breakdown plus AI credits. Note that `#codebase` runs a search; it does not paste the
repo into context. The exact default window per model is NOT DOCUMENTED in a single table.

**Story (slide 15):** six habits, the same ones as in the sibling volumes:

1. Small, stable instructions.
2. Rarely needed material goes into skills, which load on demand.
3. Fewer MCP servers; use `deferTools: "auto"` for large tool sets.
4. Send research to subagents: they have their own context windows.
5. `/plan` before you implement.
6. Start a new session per task.

Material: [`examples/context/`](./examples/context/).

🗣️ *"Compact on purpose, with a focus. Session 2's tool order is really a context policy."*

---

## §06 Prompt caching (slide 16)

**Story — be honest with the room:** Copilot has **no user-facing caching control**. There is no
`cache_control`, TTL setting or env var in the CLI, VS Code or the cloud agent. But caching **does**
happen and **is billed**: the pricing tables charge cached-input and cache-write tokens.

What you can do:

- **Diagnose in VS Code** with the **Cache Explorer** (Agent Debug Logs → Summary). It shows the hit
  % per turn, the reused tokens, and the *first divergence* in the prompt. It diagnoses; it does not
  control anything.
- **Keep the prefix stable:** pick the model, effort and tools before the first request, and don't
  edit instruction or agent files mid-session.
- **Fork instead of restarting.** Forking keeps the cache.

The CLI has no cache view: `/usage` shows tokens and credits only. Whether the OpenTelemetry export
carries cache attributes is UNVERIFIED. The mechanism demo uses the Anthropic API, not Copilot:
[`examples/prompt-caching/`](./examples/prompt-caching/).

🗣️ *"You can't set the cache. You can stop breaking it."*

---

## §07 MCP (slides 17–18)

**Story (slide 17):** there is one protocol but **four config locations**:

| Surface | File | Top key |
|---|---|---|
| CLI (user) | `~/.copilot/mcp-config.json` | `mcpServers` |
| CLI + VS Code Copilot harness (repo) | `.mcp.json` or `.github/mcp.json` (needs folder trust) | `mcpServers` |
| VS Code Local | `.vscode/mcp.json` | **`servers`** |
| Cloud agent | Repo Settings → Copilot → MCP servers (JSON in the UI) | `mcpServers` |

In the CLI and cloud configs, **`tools` is required** (for example `["*"]`). `mcpServers` versus
`servers` is the most common copy-paste bug.

**Story (slide 18):** six gotchas:

1. The CLI has **built-in** servers: GitHub (read-heavy), **Playwright**, fetch and time. **Don't
   configure Playwright twice.**
2. The cloud agent uses tools only (no resources or prompts) and no OAuth remote servers. Secrets
   need the `COPILOT_MCP_` prefix. It runs the tools **without approval**, so allowlist read-only
   ones.
3. Binaries for the cloud agent are installed by `.github/workflows/copilot-setup-steps.yml`: a
   single job named `copilot-setup-steps`, on the default branch.
4. Code review uses an MCP tool only if the tool has `readOnlyHint: true` and the toggle is on.
5. Migrate from VS Code with `jq '{mcpServers: .servers}'`. Servers that use `${input:...}` are not
   forwarded to the Copilot harness.
6. The enterprise allowlist matches by fingerprint and is fail-closed.

Material: [`examples/mcp/`](./examples/mcp/) · the method's set (CodeGraph, Serena, Context7) in
[`docs/ai-agents-code-methodology/copilot/`](./docs/ai-agents-code-methodology/copilot/).

🗣️ *"Config gives the agent the tool. A trigger map in your instructions makes it use the tool."*

---

## §08 Skills and plugins (slide 19)

**Story:** A skill is a `SKILL.md` in `.github/skills/<name>/`. Every surface reads that location,
and also `.claude/skills/` and `.agents/skills/`. For personal skills, use `~/.copilot/skills/`.

Three porting rules that cost real hours:

- ⚠️ **The CLI does not read `~/.claude/skills/`.** VS Code does. Copy or symlink the skills, or
  register them with `copilot skill add`.
- ⚠️ **VS Code silently drops a skill whose `name` is not equal to its folder name** in
  lowercase-hyphen form.
- **Drop `trigger:`.** It is not a Copilot key. Copilot already exposes every skill as `/name` and
  picks skills automatically by `description` (≤1024 characters).

Plugins: `copilot plugin install NAME@MARKETPLACE`. `awesome-copilot` is built in, and Claude-format
`.claude-plugin/` packages are readable.

The strongest reason for a skill is still **enforcement**: "pull at the start, push at the end" sat
in a runbook for months and nobody did it, until it became the `day` skill. Material:
[`examples/skills-plugins/`](./examples/skills-plugins/), live skills in
[`.github/skills/`](./.github/skills/).

The reusable methodology pack is at
[`docs/ai-agents-code-methodology/copilot/skills/`](./docs/ai-agents-code-methodology/copilot/skills/).
For the live WSL Copilot session, the user confirmed these eight personal skills are visible in
Copilot Customizations: `day`, `evidence`, `preview`, `atlassian`, `kg`, `kg-refresh`,
`methodology-plan`, and `sanitise-diff`. Treat this as a discovery check, not proof that every
remote or production behavior is safe to run; Session 2 states what was and was not tested.

🗣️ *"One SKILL.md works on almost every surface. Name it after its folder, and put it where the CLI can see it."*

---

## §09 Custom agents and subagents (slides 20–21)

**Story (slide 20):** a custom agent is `.github/agents/<name>.agent.md`. The example is
`refactor-scout` with `tools: ["read", "search"]`. **That tools list is the enforcement; the prose
is not.** Two gotchas:

- When the CLI runs a custom agent as a subagent, it gets **no repo instructions** unless
  `include-custom-instructions: true` is set.
- `handoffs[]` work only in VS Code Local.

The CLI built-ins are explore, task, general-purpose, research, rubber-duck, security-review and
code-review. ⚠️ Their documented default models (for example `claude-sonnet-4.6`, `gpt-5.4-mini`)
**disagree** with the CLI default-model table. That is a documentation inconsistency, so verify on
your build. Live agent: [`.github/agents/refactor-scout.agent.md`](./.github/agents/refactor-scout.agent.md).

**Story (slide 21):** three ways to run work in parallel:

| | Subagent (`task`) | `/fleet` | Cloud agent (`/delegate`, `&`) |
|---|---|---|---|
| Context | Own window, summary returns | Parallel subagents on one plan | Full async session |
| Result | In your session | In your session | Branch + draft PR |
| Use for | Noisy research | Wave-parallel plan execution | Long, async work |

Concurrency limits depend on the plan (Free 2 · Pro 4 · Max 8 · Business 16 · Enterprise 32).
**Maximum depth is contradictory in the docs:** the reference table says 6, the env-var table says
4. Say so out loud. Material: [`examples/subagents/`](./examples/subagents/).

🗣️ *"Use a subagent when you want the noise to stay outside your session. Use the cloud agent when the work is long. The cost is not the same."*

---

## §10 Hooks (slides 22–23)

**Story (slide 22):** CLI and cloud-agent hooks live in `.github/hooks/*.json`, with the shape
`{"version": 1, "hooks": {"preToolUse": [...]}}`. The CLI also reads hooks from
`.claude/settings.json`. The contract:

- stdin carries `{toolName, toolArgs}`. ⚠️ `toolArgs` can arrive as a **JSON string**; the docs'
  own debug example passes one.
- To deny, return `permissionDecision: "deny"` with a reason, **or exit 2**.
- A crash or any other non-zero exit **fails closed** for `preToolUse`.
- A **timeout fails open for every event**, policy hooks included. Keep blocking hooks fast.

The VS Code Local harness uses a different schema: PascalCase events, `{tool_name, tool_input}`,
`hookSpecificOutput`. Code review hooks are NOT DOCUMENTED.

**Story (slide 23):** the portable recipe that ships live in this repo
([`.github/hooks/block-external-git.json`](./.github/hooks/block-external-git.json) + `.sh` +
`.ps1`):

1. One script reads both payload shapes and also filters on the tool name.
2. It matches `git push`, `gh pr create|merge|ready`, the `gh api` merge endpoints, releases and
   deploys.
3. It answers in both formats and **exits 2**, the one signal both schemas document.
4. It never answers "allow". An allow could auto-approve the tool and skip the normal prompt.
5. In the CLI, add `--deny-tool='shell(git push)' --deny-tool='shell(gh pr)'` as a second layer.
6. It is tested with a **canary first**: `bash .github/hooks/test-block-external-git.sh`.

⚠️ `/pr create|auto|automerge` are first-party CLI slash commands that can create and **merge**
PRs. Whether they pass through `preToolUse` is UNVERIFIED. List them as human-only in the
instructions, and test the hook against them on your build.

Material: [`examples/hooks/`](./examples/hooks/).

🗣️ *"Instructions ask. A hook guarantees, as long as it answers before the timeout."*

---

## §11 Automation (slide 24)

**Story:** four ways to automate, from simplest to most managed:

- **`copilot -p` in GitHub Actions:** install with npm, set `copilot-requests: write` (or use
  `COPILOT_GITHUB_TOKEN`), pass `--trust-folder` so repo hooks load, and keep `--allow-tool` minimal
  with explicit `--deny-tool`.
- **GitHub Agentic Workflows (`github/gh-aw`):** GitHub recommends these over raw `copilot` steps
  because of their guardrails.
- **Cloud agent tasks API** (`POST /agents/repos/{owner}/{repo}/tasks`, public preview, user-to-server
  tokens only) and **Automations** (schedule or event triggers).
- **Code review via rulesets:** "Automatically request Copilot code review". ⚠️ The reviewer reads its
  instructions from the **head** branch, so a PR can change its own reviewer's instructions.

The Copilot SDK (npm, pip, Go, .NET, Java) follows `CopilotClient` → `createSession` →
`sendAndWait`, and has programmatic hooks. Material: [`examples/automation/`](./examples/automation/).

🗣️ *"In CI there's no human to answer the trust prompt, so write the allow-list on the command line."*

---

# SESSION 2 — The methodology and ticket graph

## Slide 25 — Divider

**Story:** Everything from here on works the same with any agent. It started in Claude Code and was
ported to Cursor. This volume shows it running on Copilot, and §14 shows what had to change. Not
much did.

---

## §12 The flow and the outbound gate (slides 26–27)

**Story (slide 26):** **The agent is a disciplined collaborator, and it earns autonomy one decision
at a time.** There are 11 stages, and the coral ones are gates:

1. Orient (`kg` skill + history + status)
2. **Inbound triage against the output contract**
3. **Regression vs pre-existing**
4. Investigate with a deterministic oracle
5. **`/plan` → explicit human agreement**
6. TDD RED → GREEN
7. **Verify (the outbound gate)**
8. Document once
9. Sanitise the added lines
10. Handoff: the human pushes. On Copilot the **hook enforces** this.
11. **Bot review + persist lessons**

Diagram: [`examples/methodology/flow.png`](./examples/methodology/flow.png). Full walkthrough:
[`examples/methodology/WORKFLOW.md`](./examples/methodology/WORKFLOW.md) and the end-to-end case in
[`examples/methodology/REAL_EXAMPLE.md`](./examples/methodology/REAL_EXAMPLE.md).

**Story (slide 27):** The outbound gate is **five checks**, not "the tests pass":

- **(0) Validate the instrument** against a known-answer case.
- **(1) Reproduce at the real output stage**, through the wrapper that builds the contract.
- **(2) Assert on the member list, never on a total.**
- **(3) Verify inside the deployed image.**
- **(4) Look at the output.**

Then tell the five ways a green gate proves nothing. Every one of them has happened:

- a broken instrument that returns a confident uniform "no";
- a total that matches because two errors cancel out;
- a gate that couldn't fail (zero positive cases in the corpus);
- a canary that never applied the perturbation production applies;
- a structural check read as if it were semantic.

🗣️ *"Green tests aren't proof of what ships. The gate has five checks because each one has failed us once."*

---

## §13 The method's tools (slides 28–30)

**Story (slide 28):** the instructions say *which tool, in what order*: cheap → expensive,
deterministic → probabilistic.

| Stage | Tool |
|---|---|
| Orient | `kg` skill |
| Navigate | CodeGraph `codegraph_explore` (one call; treat its output as already read) |
| Refactor-check | Serena `find_referencing_symbols` (**mandatory** before a rename) |
| Diagnose | deterministic oracle |
| Environment | cloud CLI, read-only |
| Contract | Playwright, which is **built into** the CLI |
| Last | the agent's turn, to verify |

It ships as
[`01-tool-prevalence.instructions.md`](./docs/ai-agents-code-methodology/copilot/instructions/).

**Story (slide 29):** where each server is configured on each surface. CodeGraph: `.mcp.json` stdio
with `--path .` (CLI and Copilot harness), `.vscode/mcp.json` with `${workspaceFolder}` (Local), repo
MCP settings plus `copilot-setup-steps.yml` (cloud). Whether `--path .` resolves against the session
cwd is UNVERIFIED, so launch from the repo root or pin an absolute path. Material:
[`examples/codegraph/`](./examples/codegraph/), [`examples/serena/`](./examples/serena/).

**Story (slide 30):** **GSD works only in Claude Code.** Copilot has no first-party equivalent of its
phase/roadmap state machine. The nearest pieces:

- plan mode (`/plan`, `--plan`, enforced at the tool layer) and `--plan --mode autopilot`;
- `/fleet` for waves;
- role custom agents;
- an `agentStop` hook with `decision: block` as a "verify before stop" gate;
- **Spec Kit** (`github/spec-kit`). Only third-party coverage confirms it, and the current version
  is UNVERIFIED.

State stays in `data/changes/`. Material: [`examples/gsd/`](./examples/gsd/).

🗣️ *"The order is the policy: the oracles diagnose, and the model verifies."*

---

## §14 Transfer: from Claude Code to Copilot (slides 31–32)

**Story (slide 31):** The **five rules travel unchanged**:

1. plan → agree → implement;
2. verify on the consumer's contract;
3. fix the general class, not one input;
4. keep a durable trail;
5. the human owns everything external.

Only the surface changes:

| Claude Code | Copilot |
|---|---|
| `CLAUDE.md` | `AGENTS.md` + `.instructions.md` (the CLI reads `CLAUDE.md` too) |
| `~/.claude/skills` | `.github/skills` (mind the CLI gap) |
| settings allow/deny | flags + hooks |
| PreToolUse | `.github/hooks` `preToolUse` |
| Agent Teams | `/fleet` + cloud agent |
| `claude -p` | `copilot -p --trust-folder` |

The starter kit is [`COPILOT_ADAPTATION.md`](./docs/ai-agents-code-methodology/COPILOT_ADAPTATION.md)
plus the ready-to-copy surface in
[`docs/ai-agents-code-methodology/copilot/`](./docs/ai-agents-code-methodology/copilot/).

**Story (slide 32):** this is the slide that matters most for governance. There are **new holes**:

- the CLI's `/pr create|auto|automerge`, which can merge (hook coverage UNVERIFIED);
- **Copilot code review can approve PRs** (preview, off by default; keep it off);
- the reviewer reads its instructions from the head branch, so put CODEOWNERS on `.github/**`,
  `AGENTS.md` and `.mcp.json`.

And, new in this volume, **"the human owns merge" can now be enforced**: the `preToolUse` deny hook
plus `--deny-tool` (deny beats `--yolo`), the cloud agent's structural limits (it cannot approve or
merge, and pushes only to `copilot/`), and `disableBypassPermissionsMode`.

🗣️ *"In 2025 'the agent doesn't merge' was a policy. In 2026 it's a hook, a flag and a branch rule, and you still have to close two new doors."*

---

## §15 Ops: machine sync and the shared record (slide 33)

**Story:** two mechanisms that do not compete:

- **(A) tarball + USB** to bring up a whole machine. Outbound is a full copy; inbound is the `data/`
  delta only. Carry `~/.copilot` on purpose (skills, agents, `mcp-config.json`), and re-pin the
  CodeGraph `--path` on the target.
- **(B) a shared record over S3** for daily work. Scope grows in reviewed phases. Write via sync,
  read via a read-only mount. Dry-run by default. Guard **both** directions. One publisher.
  "Derived" is a property of each file, not of the folder.

The agent-specific part: the machine has a role. `IDENTITY.md` says publisher or contributor, and
`AGENTS.md` points to it. On Copilot, the `day` skill can be enforced by a `sessionStart` prompt hook
that runs `/day start` (CLI, new interactive sessions only). The Cursor volume could not do that.

Runbooks: [`docs/synchro/`](./docs/synchro/) · scripts:
[`examples/methodology/s3-sync/`](./examples/methodology/s3-sync/).

🗣️ *"A rule in a runbook decays silently. A routine you call leaves a trace."*

---

# SESSION 2 CONTINUED — The ticket knowledge graph

## §16 (slides 34–37)

**Story (slide 35):** A "new" bug almost always has earlier context that limits the fix. **graphify**
(not CodeGraph; CodeGraph is only the analogy) builds a graph over the project's *memory*: ticket
writeups, sharp edges, runbooks. `kg_refresh.sh prepare` stages the corpus outside the repo, because
graphify honours `.gitignore` and `data/` is ignored. The agent then does the semantic extraction,
and `finalize` copies the artifacts back and checks for leaks. The bookends are deterministic and
tested.

**Story (slide 36):** the current graph snapshot has **3,921 nodes · 8,508 links · 178 communities ·
73 hyperedges**. Link provenance: 94.3% `EXTRACTED`, 5.6% `INFERRED`, and under 0.1% `AMBIGUOUS`.
The deck image is a topology-only rendering from the current ILS_2 snapshot; labels and metadata are
omitted because the source graph contains internal identifiers. The interactive graph bundled under
[`docs/knowledge-graph/`](./docs/knowledge-graph/) remains a separate, older sanitized snapshot. See
[`docs/KNOWLEDGE_GRAPH.md`](./docs/KNOWLEDGE_GRAPH.md).

**Story (slide 37):** queries use **zero LLM** (`kg_query.sh explain|path|find` reads `graph.json`),
and they hook into stage 1 (Orient): run `kg` *before* grep. Under Copilot:

- Put the skills in `.github/skills/` or `~/.copilot/skills/`. The CLI will not find them in
  `~/.claude/skills`.
- The semantic step of `kg-refresh` can run with CLI subagents (`task`, `/fleet`), or keep running
  from Claude Code.
- The publisher-only guard stays in the script.
- Not for the cloud agent: the corpus is not in its sandbox.

🗣️ *"You pay for one semantic step at build time and zero LLM at query time. The graph is the map; the agent is the guide."*

---

## WSL parity check (slide 38)

The WSL parity check reports only evidence the other agent actually gathered.
The eight personal skills were user-confirmed in the active Copilot Customizations view; CodeGraph
CLI and a bounded MCP query worked in the target repo; the evidence and Atlassian test suites ran
against offline/mocked fixtures. The active course-repo Copilot MCP view was separately confirmed
to show CodeGraph and Context7. Do not collapse these into one claim about every target-repo surface.

The check deliberately did **not** run real preview work (no approved fixture), evidence fetches,
authenticated Atlassian reads, or shared `day` / `kg-refresh` operations. Serena was unavailable;
Pylance supplied local Python navigation, not a Serena replacement. The slide makes this boundary
visible instead of claiming full parity.

🗣️ *"Verified means exactly what we ran; gated means not yet proven."*

---

## Appendix and close (slides 39–40)

**Slide 39:** the Claude Code → Cursor → Copilot equivalence table. It is the slide to photograph.
The longer version is in [`TECHNICAL_GUIDE.md`](./TECHNICAL_GUIDE.md).

**Slide 40:** eight takeaways, then the sources. Read the date out loud: **verified 2026-10-17;
Copilot moves fast, so re-check before reuse.** Sources: docs.github.com/en/copilot,
code.visualstudio.com/docs, github.blog/changelog, and the
[findings file](./docs/research/COPILOT_FINDINGS_2026-10-17.md).

🗣️ *"From assistant to system: the tool changes and the discipline doesn't. On Copilot, part of that discipline can finally be enforced."*
