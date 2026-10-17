# Repository instructions (small on purpose)

The full orientation is `AGENTS.md`. This file exists because it is the **only** instruction file that
code review in VS Code, Visual Studio and Eclipse reads — so it carries just the non-negotiables:

- The human owns `git push`, PR creation/merge (incl. CLI `/pr create|auto|automerge`) and deploys.
- Never put client names, ticket IDs or secrets in code, commits or PR text.
- Verify against the output contract, not an internal function.
