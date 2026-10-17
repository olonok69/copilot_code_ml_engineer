---
applyTo: "data/changes/**"
excludeAgent: "code-review"
---

# Atlassian (read-only)

When the work under `data/changes/` needs a ticket's live status, links or comments, or a Confluence page,
use the `atlassian` skill (`python3 data/changes/tools/atlassian/atl.py` — `jira issue|search|links|comments|xml`,
`confluence search|page|diff`). Credentials live in `~/.config/<org>/jira.env` (each person's own token;
never commit, paste or print it). The tool only sends GET.

Jira writes (create, edit, transition, comment) stay with the human — draft the text, the human posts it.
A Confluence page update goes through `confluence_write.py` (plan → diff → explicit human OK for that page →
apply) and only when the human asks for it.

Local surfaces only (CLI, VS Code): the cloud agent has no token file. With the CLI sandbox on, the
Atlassian host must be in `sandbox.userPolicy.network.allowedHosts`.
