#!/usr/bin/env bash
# Deny reading .env files. Registered under the PascalCase alias "PreToolUse" with matcher "Read":
# per the GitHub hooks reference, PascalCase aliases switch the payload to VS Code-style snake_case
# (tool_name, tool_input) and apply Claude matcher semantics, where the CLI's `view` tool maps to `Read`.
# The exact argument key holding the path is UNVERIFIED, so several candidates are checked.
# Deny = exit 2 + a decision on stdout. Anything else = exit 0 + "{}".
set -u
payload="$(cat 2>/dev/null || true)"
path=""
if command -v python3 >/dev/null 2>&1; then
  path="$(PAYLOAD="$payload" python3 -c '
import json, os
raw = os.environ["PAYLOAD"]
try: p = json.loads(raw) if raw.strip() else {}
except Exception: p = {}
a = p.get("tool_input", p.get("toolArgs", {}))
if isinstance(a, str):
    try: a = json.loads(a)
    except Exception: a = {"path": a}
if not isinstance(a, dict): a = {}
print(a.get("file_path") or a.get("path") or a.get("filePath") or "")
' 2>/dev/null)"
else
  path="$payload"
fi
case "$path" in
  *.example|*.sample) ;;   # templates are fine
  *.env|*.env.*|*/.env|.env)
    r="Blocked: .env files hold secrets. Use the process environment or a vault, do not read the file."
    printf '{"permissionDecision":"deny","permissionDecisionReason":"%s","hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$r" "$r"
    exit 2 ;;
esac
printf '{}\n'
exit 0
