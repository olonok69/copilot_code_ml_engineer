---
name: deploy-staging
description: >-
  Deploy the current app to staging — runs tests, builds, asks for human
  confirmation, then runs the staging deploy script and a health smoke check.
  Use when the user wants to deploy to staging (demo target: ex_staging).
---

# Deploy to staging

A repeatable, safe flow for deploying to staging.
**Demo target:** the `ex_staging/` folder (a simulated local staging — no real cloud).

## Steps

1. `cd` into the target (`ex_staging` or the path the user named).
2. Check the git tree **of the target**: `git status --porcelain -- .` (from that folder).
   If there are uncommitted changes **in the target**, STOP and say so. (Dirt in other folders of the
   course repo can be ignored after saying so.)
3. Run the tests: `npm test`. If they fail, STOP and show the output.
4. Build: `npm run build`. If it fails, STOP.
5. **Ask for human confirmation** before deploying (an external, in production irreversible action).
   Do not run the deploy until the user gives an explicit OK in this session.
6. After the OK: `npm run deploy:staging` (equivalent to `node scripts/deploy.mjs staging`).
   - In this demo that starts a local server and writes `.staging-url`.
   - In a real repo substitute `./scripts/deploy.sh staging` or your pipeline.
7. Smoke check: read `.staging-url` and call `GET {url}/health` (curl, `Invoke-WebRequest`, or `fetch`).
   It must be HTTP 200 with `ok: true`.
8. Summarise: what was deployed, the URL, the smoke result. Mention `npm run staging:stop` to stop the demo.

## Rules

- **Never** deploy with red tests or a dirty target.
- **Never** deploy without an explicit human request/confirmation (handoff gate).
- Always show the real output of every command.
- Do not use `staging.example.com` in this repo — the smoke check runs against the local URL in `.staging-url`.
