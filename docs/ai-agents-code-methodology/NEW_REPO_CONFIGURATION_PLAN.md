# New Repo Configuration Plan (GitHub Copilot)

## Phase 1: Foundations (Day 1)

1. Copy the methodology folder into `data/changes/ai-agent-methodology`.
2. Create baseline trackers: `data/changes/STATUS.md`, `FOLLOWUPS.md`, `SHARP_EDGES.md`.
3. Define the product-facing output contract (paragraph in `AGENTS.md`).
4. Define branch and PR naming rules.
5. Run `bootstrap-copilot-repo.ps1`: `AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/`,
   skills, agents, hooks, `.mcp.json`, `.vscode/mcp.json`, `copilot-setup-steps.yml`; fill the Copilot working agreement.

Exit criteria:

1. All baseline docs exist.
2. Team agrees on contract and naming conventions.
3. `copilot` launched from the repo root in a trusted folder shows the MCP servers (`/mcp`), skills
   (`/skills`) and instruction files (`/instructions`).
4. `bash .github/hooks/test-block-external-git.sh` reports 0 failures.

## Phase 2: Operationalization (Days 2-3)

1. Map test suites by component/subsystem.
2. Add handover and QA acceptance templates.
3. Define minimum evidence required to claim "fixed".
4. Sanitisation: `sanitise-diff` skill; the `preToolUse` hook for push/PR/merge/deploy; test it against the
   CLI's `/pr create|auto|automerge` (UNVERIFIED whether they are intercepted).
5. Confirm the plan-mode gate (`/plan`) on the first non-trivial change.

Exit criteria:

1. One issue completed with full trail and evidence.
2. Reviewer can execute QA acceptance checks without extra context.

## Phase 3: Stabilization (Days 4-7)

1. Track reopen rate and cycle time.
2. Add new sharp edges discovered in triage and review.
3. CODEOWNERS on `AGENTS.md`, `.github/**` customisations and `.mcp.json`; Copilot code-review approvals kept off.

Exit criteria:

1. Reopen rate trending down.
2. New contributors can run the flow from docs only.

## Phase 4: Hardening (Week 2)

1. Automate repetitive gates (CI with `copilot -p --trust-folder` and explicit `--allow-tool` / `--deny-tool`).
2. Keep always-loaded docs lean; move detail to ticket folders.
3. Decide the cloud-agent scope: firewall allowlist, read-only MCP tools, which skills are committed.
4. Review the methodology monthly and prune stale rules.

Exit criteria:

1. Durable process with low manual overhead.
2. Clear evidence quality on each fix handover.
