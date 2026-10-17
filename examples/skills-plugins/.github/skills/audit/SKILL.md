---
name: audit
description: >-
  Audit npm dependencies for vulnerabilities and verify tests still pass.
  Use for Node/JavaScript packages (package.json), e.g. the ex_npm demo target.
  For Python apps with requirements.txt, use the audit-python skill instead.
---

# Dependency audit (npm)

Target: a folder with `package.json` (demo: `ex_npm/`).

1. `cd` into the target app (or the path the user named, e.g. `/audit ex_npm`).
2. Run `npm audit` to find packages with vulnerabilities.
3. Run `npm audit fix` for safe updates only (never `--force` a major upgrade without asking).
4. Run the tests (`npm test`) to verify nothing broke.
5. Summarise what was updated and any vulnerability that needs manual intervention.

Always show the real command output (evidence over claims).

If the target is Python (`requirements.txt`, no `package.json`), **do not invent npm** — say to use `/audit-python`.
