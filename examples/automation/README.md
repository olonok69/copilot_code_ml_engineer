# Automation (GitHub Copilot)

Five levels, from the lightest to the most autonomous. Facts: findings §11
([`../../docs/research/COPILOT_FINDINGS_2026-10-17.md`](../../docs/research/COPILOT_FINDINGS_2026-10-17.md)).

## 1. Hooks — deterministic, inside the session

See [`../hooks/`](../hooks/): the push gate, `.env` read deny, logging, `/day start` at session start,
"verify before stop".

## 2. Headless — `copilot -p`

```bash
copilot -p "Explain ./complex.ts" -s                      # -s = only the answer
echo "Explain ./complex.ts" | copilot                     # piped stdin works (ignored if -p is given)
tail -200 app.log | copilot -s                            # Claude-style log triage
copilot -p "..." --output-format=json                     # JSONL events
copilot -p "..." --share=./report.md                      # export the transcript
copilot -p "..." -s --no-ask-user --allow-tool='shell(git:*)' --deny-tool='shell(git push)' --model=claude-sonnet-5.5
copilot -p "..." --trust-folder                           # load repo hooks/MCP/plugins for this run only
copilot -p "..." --max-ai-credits=5                       # soft per-response spend cap
```

Every `-p` run prints a `copilot --resume=SESSION-ID` hint. `COPILOT_TASK_WAIT_TIMEOUT_SECONDS` (default 600)
controls how long `-p` waits for background tasks.

## 3. CI — GitHub Actions

[`copilot-cli-action.yml`](./copilot-cli-action.yml): `npm install -g @github/copilot`, auth via `GITHUB_TOKEN`
with `permissions: copilot-requests: write` (org policy must allow CLI billed to the org) **or**
`COPILOT_GITHUB_TOKEN` (fine-grained PAT with "Copilot Requests"); `-s --no-ask-user --trust-folder`, explicit
`--allow-tool` and `--deny-tool='shell(git push)'` / `'shell(gh pr)'`.

> GitHub itself **recommends GitHub Agentic Workflows** (`github/gh-aw`) over raw `copilot` steps, because of
> its guardrails and default `GITHUB_TOKEN`. Use raw `copilot -p` when you need full control and accept owning
> the guardrails.

## 4. Cloud agent — async, PR-shaped

- **Tasks API (public preview):** [`cloud-agent-task.sh`](./cloud-agent-task.sh) —
  `POST https://api.github.com/agents/repos/{owner}/{repo}/tasks` with `{"prompt", "base_ref", "model",
  "create_pull_request"}`; list with `GET /agents/repos/{o}/{r}/tasks` and `GET /agents/tasks`. **User-to-server
  tokens only.** Dry run by default.
- Assign an issue to Copilot (REST/GraphQL or UI), `@copilot` on a PR, `/delegate` / `&` from the CLI.
- **Automations:** schedule- or event-triggered, created in the repo **Agents → Automations** pane; you choose
  the tools; events from users without write access are ignored by default.
- Environment: `.github/workflows/copilot-setup-steps.yml` (single job `copilot-setup-steps`, default branch) —
  template in [`../../docs/ai-agents-code-methodology/copilot/copilot-setup-steps.yml.example`](../../docs/ai-agents-code-methodology/copilot/copilot-setup-steps.yml.example).
- Integrations: Slack, Teams, Jira, Linear, Azure Boards, Raycast.

## 5. Code review — via rulesets

Repo ruleset rule **"Automatically request Copilot code review"** (options "Review new pushes", "Review draft pull
requests"); effort Lite or Balanced. It reads `copilot-instructions.md`, path instructions, `AGENTS.md`,
`CLAUDE.md`, `GEMINI.md`, `REVIEW.md` and `.github/skills` **from the head branch** — protect them with CODEOWNERS.

⚠️ **Copilot approvals** (preview, off by default) can count toward required approvals. **Keep it off** if the
human owns merge.

## 6. SDK and ACP

- **Copilot SDK:** `@github/copilot-sdk` (npm), `github-copilot-sdk` (pip), Go, .NET, Java. Flow:
  `new CopilotClient()` → `createSession({model: "auto"})` → `sendAndWait({prompt})`; programmatic hooks such as
  `onPreToolUse` return `permissionDecision`. Python sketch: [`sdk_example.py`](./sdk_example.py) (signatures UNVERIFIED).
- **ACP server:** `copilot --acp`.
- In-session scheduling: `/every`, `/after` (experimental).

## Mapping

| Need | Claude Code | Cursor | Copilot |
|---|---|---|---|
| One-shot CLI | `claude -p` | `agent -p` | `copilot -p … -s` (stdin piping works) |
| CI | `claude -p` in Actions | Cursor SDK / Bugbot | `copilot -p` (`copilot-requests: write`), Agentic Workflows |
| Async cloud | — | Background/Cloud Agents | Cloud agent (tasks API, issues, `/delegate`, Automations) |
| PR review bot | — | Bugbot | Copilot code review (ruleset) |
| SDK | Agent SDK | `@cursor/sdk` | `@github/copilot-sdk` (+ Python/Go/.NET/Java) |
