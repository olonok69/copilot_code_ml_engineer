# GSD — "Get Stuff Done" — **Claude Code only**

A Claude Code setup for phase-based project management, installed as a Claude **plugin**.
Repo: https://github.com/tomascortereal/claude-code-setup

## Status in GitHub Copilot

| GSD piece | In Copilot? |
|---|---|
| Plugin + `gsd-*` skills / phase state machine | **No first-party equivalent.** (Copilot can read Claude plugin manifests, but GSD's commands are not ported or tested here.) |
| discuss → plan → execute → verify cycle | **Yes, as a discipline** — see substitutes below |
| State in `.planning/` | Adopt the folder by hand if you like; nobody installs the commands for you |
| `gsd-planner`, `gsd-executor`, `gsd-verifier` subagents | Custom agents in `.github/agents/` with those roles |

## The nearest Copilot pieces

| Need | Copilot |
|---|---|
| Discuss/plan gate | CLI **plan mode** (`/plan`, Shift+Tab, `--plan`) — enforced at the tool layer; VS Code Plan agent |
| Plan, then run unattended | `copilot --plan --mode autopilot -p "…"` (plan-then-autopilot), bounded by `--max-autopilot-continues` / `--max-ai-credits` |
| Wave-parallel execution | **`/fleet`** / `--fleet` |
| Role agents | `.github/agents/planner.agent.md`, `executor.agent.md`, `verifier.agent.md` (read-only `tools` for the verifier) |
| "Verify before stop" gate | `agentStop` hook returning `decision: block` ([`../hooks/agent-stop-verify.json`](../hooks/agent-stop-verify.json)) |
| Plan → implement buttons | VS Code `handoffs` (Local harness only) |
| Spec-driven templates | GitHub's open-source **Spec Kit** (`github/spec-kit`) — third-party coverage only; current version UNVERIFIED |
| Durable state | The methodology's own ledgers (`STATUS.md`, `PLAYBOOK.md`) under `data/changes/` |

Do not say "install GSD in Copilot" — there is **no official port** in this material.

## The idea (still valid)

Instead of "chatting", a cycle with gates and durable state:

```
discuss → plan (gate) → execute → verify (evidence)
```

Typical artifacts in `.planning/`: `PROJECT.md`, `ROADMAP.md`, `PLAN.md`, `VERIFICATION.md`.

## Why it fits the methodology

GSD embodies plan → agree → implement and verify with evidence. The Part 2 project **does not use GSD day to
day** (it runs the 11 stages + `data/changes/`). GSD shines in **multi-component greenfield** work; in Copilot,
replicate its gates with plan mode + `/fleet` + role agents + the `methodology-plan` skill
([`../../docs/ai-agents-code-methodology/copilot/skills/methodology-plan/`](../../docs/ai-agents-code-methodology/copilot/skills/methodology-plan/)).
