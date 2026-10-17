#!/usr/bin/env bash
# block-external-git.sh — GitHub Copilot preToolUse guard: the human owns everything external.
#
# Denies, for shell tools only:
#   git push · gh pr create|merge|ready · gh pr merge --auto (the shell form of an auto-merge)
#   gh api …/merges or …/pulls/N/merge · gh release create
#   terraform apply · kubectl apply · helm upgrade|install · aws … deploy
#
# Contract (GitHub hooks reference, verified 2026-10-17):
#   stdin  = one JSON payload. Two shapes are handled:
#            CLI / cloud agent / VS Code Copilot harness: {"toolName": "...", "toolArgs": <string|object>}
#              (toolArgs is typed `unknown`; the docs' own debug example passes a JSON *string*)
#            VS Code Local harness / PascalCase events:     {"tool_name": "...", "tool_input": {...}}
#   deny   = exit 2 (the one blocking signal documented in BOTH schemas) + a JSON decision on stdout
#   no-op  = exit 0 and "{}" — we deliberately do NOT answer "allow": that could auto-approve the
#            tool and skip the normal permission prompt.
#   ⚠️ A hook that TIMES OUT is fail-OPEN (every event). Keep this script fast; no network.
#   ⚠️ A crash / other non-zero exit is fail-CLOSED for preToolUse — so this script must not crash.
set -u

payload="$(cat 2>/dev/null || true)"

tool=""
cmd=""
if command -v python3 >/dev/null 2>&1; then
  parsed="$(PAYLOAD="$payload" python3 - <<'PY' 2>/dev/null
import json, os
raw = os.environ.get("PAYLOAD", "")
try:
    p = json.loads(raw) if raw.strip() else {}
except Exception:
    p = {"toolArgs": {"command": raw}}   # unparseable: scan the raw text (fail-safe)
if not isinstance(p, dict):
    p = {}
tool = p.get("toolName") or p.get("tool_name") or ""
args = p.get("toolArgs", p.get("tool_input", {}))
if isinstance(args, str):
    try:
        args = json.loads(args)
    except Exception:
        args = {"command": args}
cmd = ""
if isinstance(args, dict):
    cmd = args.get("command") or args.get("cmd") or args.get("script") or ""
print(str(tool))
print(str(cmd).replace("\n", " "))
PY
)"
  tool="$(printf '%s\n' "$parsed" | sed -n '1p')"
  cmd="$(printf '%s\n' "$parsed" | sed -n '2p')"
else
  # No python3: fall back to scanning the raw payload text (coarser, still fail-safe).
  cmd="$payload"
fi

# Only shell tools are in scope. The CLI routes via the "bash|powershell" matcher; VS Code Local may
# ignore matchers on Copilot-format files (UNVERIFIED), so filter here too. Unknown/empty tool name →
# still check the command (safer).
if [ -n "$tool" ] && ! printf '%s' "$tool" | grep -qiE 'bash|powershell|shell|terminal|exec|command'; then
  printf '{}\n'
  exit 0
fi

re='(^|[;&|(` ])git([[:space:]]+-[^[:space:]]+([[:space:]]+[^-[:space:]][^[:space:]]*)?)*[[:space:]]+push([[:space:]]|$)'
re="$re"'|gh[[:space:]]+pr[[:space:]]+(create|merge|ready)'
re="$re"'|gh[[:space:]]+api[[:space:]].*(/merges|/pulls/[0-9]+/merge)'
re="$re"'|gh[[:space:]]+release[[:space:]]+create'
re="$re"'|terraform[[:space:]]+apply|kubectl[[:space:]]+apply|helm[[:space:]]+(upgrade|install)'
re="$re"'|aws[[:space:]].*[[:space:]]deploy'

if printf '%s' "$cmd" | grep -qiE -- "$re"; then
  reason="Methodology handoff gate: outward-facing command blocked (push / PR / merge / release / deploy). The human owns these. Prepare the branch and a handover note instead."
  printf '{"permissionDecision":"deny","permissionDecisionReason":"%s","hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$reason" "$reason"
  echo "block-external-git: denied: $cmd" >&2
  exit 2
fi

printf '{}\n'
exit 0
