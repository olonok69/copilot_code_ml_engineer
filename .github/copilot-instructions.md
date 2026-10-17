# Copilot instructions — course repo

The always-on project memory is [`AGENTS.md`](../AGENTS.md) (read by the CLI, VS Code, the cloud agent and
code review). This file stays small on purpose: it is the one file that **every** Copilot surface reads,
including code review in IDEs.

## Human-only actions (never run these from the agent)

- `git push` (any remote, any branch)
- `gh pr create`, `gh pr merge` (incl. `--auto`), `gh pr ready`, `gh release create`
- Copilot CLI `/pr create`, `/pr auto`, `/pr automerge` — first-party slash commands that create and merge
  PRs. Whether they pass through the `preToolUse` hook is UNVERIFIED, so treat them as human-only by rule.
- Deploys: `terraform apply`, `kubectl apply`, `helm upgrade`, `npm run deploy:staging` without an explicit OK.

These are also enforced by `.github/hooks/block-external-git.json` (deny + exit 2). Prepare the branch and a
handover note instead.

## Conventions

- Show the real command output; evidence over claims.
- Demo targets: `ex_npm/` (`/audit`), `ex_app/` (`/audit-python`), `ex_staging/` (`/deploy-staging`).
