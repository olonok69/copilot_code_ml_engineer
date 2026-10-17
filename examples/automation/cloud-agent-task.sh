#!/usr/bin/env bash
# Start a Copilot cloud agent task through the REST API (PUBLIC PREVIEW, verified in the docs 2026-10-17).
#   POST https://api.github.com/agents/repos/{owner}/{repo}/tasks
#   body: {"prompt", "base_ref", "model", "create_pull_request"}
# Requires a USER-TO-SERVER token (e.g. `gh auth token` from your own login) — other token types are not accepted.
#
# Dry run by default: prints the request. Add --go to send it. The agent's work lands on a copilot/ branch
# as a draft PR that a human reviews and merges — the agent cannot merge.
#
# Usage: cloud-agent-task.sh OWNER/REPO "prompt" [base_ref] [--go]
set -euo pipefail
repo="${1:?OWNER/REPO}"; prompt="${2:?prompt}"; base="${3:-main}"; go="${4:-}"
[ "$base" = "--go" ] && { base="main"; go="--go"; }

body="$(PROMPT="$prompt" BASE="$base" python3 -c '
import json, os
print(json.dumps({"prompt": os.environ["PROMPT"], "base_ref": os.environ["BASE"], "create_pull_request": True}))')"

echo "POST https://api.github.com/agents/repos/${repo}/tasks"
echo "$body"
if [ "$go" != "--go" ]; then
  echo "(dry run — add --go to send; list tasks with GET /agents/repos/${repo}/tasks)"
  exit 0
fi
: "${COPILOT_USER_TOKEN:?export COPILOT_USER_TOKEN=<user-to-server token>}"
curl -sS -X POST "https://api.github.com/agents/repos/${repo}/tasks" \
  -H "Authorization: Bearer ${COPILOT_USER_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d "$body"
