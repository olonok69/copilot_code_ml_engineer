# Skills, prompt files and plugins (GitHub Copilot)

Claude Code has three layers — **tools**, **slash commands** (`.claude/commands/`), **skills** — plus
**plugins/marketplaces**. Copilot has all of them, with its own paths and rules. Facts: findings §2 and §8
([`../../docs/research/COPILOT_FINDINGS_2026-10-17.md`](../../docs/research/COPILOT_FINDINGS_2026-10-17.md)).

## 1. Skills — the main mechanism (all surfaces)

A skill is a folder with `SKILL.md` + frontmatter. `description` drives **auto-selection**; users invoke it
as `/<name>`. Surfaces: CLI, VS Code agent mode, cloud agent, code review (prefers review-named skills),
Copilot app, JetBrains (Preview).

| Surface | Project | Personal |
|---|---|---|
| CLI | `.github/skills/`, `.agents/skills/`, `.claude/skills/` (+ parent `.github/skills/` in a monorepo) | `~/.copilot/skills/`, `~/.agents/skills/` |
| VS Code | `.github/skills/`, `.claude/skills/`, `.agents/skills/` | `~/.copilot/skills/`, **`~/.claude/skills/`**, `~/.agents/skills/` |
| Cloud agent + code review | `.github/skills`, `.claude/skills`, `.agents/skills` | — |

> ⚠️ **The CLI does NOT read `~/.claude/skills/`** (VS Code does). Personal Claude Code skills must be copied
> or symlinked to `~/.copilot/skills/` / `~/.agents/skills/`, or registered with `copilot skill add <dir>` /
> `COPILOT_SKILLS_DIRS`.

### Frontmatter — keep it portable

| Key | Notes |
|---|---|
| `name` (required) | **Lowercase, digits, hyphens; must equal the folder name; ≤ 64.** VS Code *silently* drops a skill that violates this (the CLI is laxer). |
| `description` (required) | ≤ 1024 chars. It is what gets matched. |
| `argument-hint`, `user-invocable`, `disable-model-invocation` | CLI + VS Code |
| `allowed-tools` | CLI + cloud docs (example `allowed-tools: shell`); entry grammar such as `shell(python3:*)` is UNVERIFIED. Don't pre-approve `shell` for untrusted skills. |
| `context: fork` | VS Code only, feature-flagged |
| ~~`trigger:`~~ | **Not a Copilot key** — remove it when porting from Claude Code (whether unknown keys are ignored is UNVERIFIED). |

Management: CLI `/skills list|info|add [--project]|remove|reload`, `copilot skill …`; VS Code **Chat: Open
Customizations**; `/chronicle skills create` drafts skills from observed usage.

### Skills in this folder (`.github/skills/`)

- [`audit`](./.github/skills/audit/SKILL.md) — npm (`package.json`); demo target [`../../ex_npm/`](../../ex_npm/)
- [`audit-python`](./.github/skills/audit-python/SKILL.md) — Python (`requirements.txt`); demo target [`../../ex_app/`](../../ex_app/)
- [`deploy-staging`](./.github/skills/deploy-staging/SKILL.md) — deploy with a human gate; demo target [`../../ex_staging/`](../../ex_staging/)
- [`day`](./.github/skills/day/SKILL.md) — start/end-of-day shared-record routine (read for shape; scripts in
  [`../methodology/s3-sync/`](../methodology/s3-sync/)). `day start` also refreshes the ticket status table from
  the tracker, counts the last 24 h of service failures without downloading anything, and on the publisher runs
  `delete.sh --check`. Copilot bonus: a `sessionStart` prompt hook can **enforce** `/day start`
  ([`../hooks/session-start-day.json`](../hooks/session-start-day.json)).
- [`atlassian`](./.github/skills/atlassian/SKILL.md) — **read-only** Jira + Confluence. ⚠️ The boundary lives in
  code: one network function, GET only, with a test. Writing to Confluence is a different tool: plan → diff →
  **human OK per page** → apply. Tickets: always the person. Tool: [`../methodology/tools/atlassian/`](../methodology/tools/atlassian/)
- [`evidence`](./.github/skills/evidence/SKILL.md) — a run's evidence (source as it was, artefact, result, log).
  ⚠️⚠️ Its first canary **passed with the wrong versions** (two byte-identical uploads); it now asserts known
  timestamps. Core and design: [`../methodology/tools/README.md`](../methodology/tools/README.md)

**Live** (repo root): [`../../.github/skills/`](../../.github/skills/) (`audit`, `audit-python`, `deploy-staging`) —
see [`../../DEMO_RUNBOOK.md`](../../DEMO_RUNBOOK.md).

Methodology pack: `kg`, `kg-refresh`, `methodology-plan`, `sanitise-diff`, `day`, `atlassian`, `evidence` in
[`../../docs/ai-agents-code-methodology/copilot/skills/`](../../docs/ai-agents-code-methodology/copilot/skills/).

## 2. Slash commands → prompt files or skills

| From Claude Code `.claude/commands/x.md` | Copilot |
|---|---|
| CLI | Reads `.claude/commands/*.md` as an alternative skill format (`description`, `argument-hint`, `allowed-tools`, `disable-model-invocation`) |
| VS Code (Local harness only), Visual Studio, JetBrains | **Prompt files** `.github/prompts/*.prompt.md` (`description`, `name`, `argument-hint`, `agent`, `model`, `tools`), invoked as `/name` |
| Everywhere else | Convert it into a **skill** — VS Code's own docs say to convert prompt files to skills for non-Local harnesses |

⚠️ Prompt files run **only** in the VS Code *Local* harness (and VS / JetBrains). The CLI does not load them.

## 3. Plugins and marketplace

```bash
copilot plugin install NAME@MARKETPLACE | OWNER/REPO | URL | PATH
copilot plugin marketplace add OWNER/REPO
# interactive: /plugin …
```

- Formats: **Agent Plugins 1.0** (`plugin.json` with the agent-plugins.org schema) and legacy Copilot
  `plugin.json`; the legacy loader also accepts `.claude-plugin/plugin.json`, and Claude Code marketplaces are readable.
- Built-in, non-removable marketplace: **`awesome-copilot`**.
- Repo-declared plugins: `enabledPlugins` / `extraKnownMarketplaces` in `.github/copilot/settings.json`
  (the cloud agent reads these too).
- VS Code: agent plugins + an experimental "Customization Marketplace".

For a team, the simplest distribution is still a versioned `.github/` folder (instructions + skills + agents +
hooks) plus `.mcp.json`, or the starter kit [`../../docs/ai-agents-code-methodology/`](../../docs/ai-agents-code-methodology/).

## 4. Subagents

See [`../subagents/`](../subagents/) — built-ins + `.github/agents/*.agent.md` for custom roles.
