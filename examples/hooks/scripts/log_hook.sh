#!/usr/bin/env bash
# Observability hook: append each payload (one JSON line) to .github/hooks/hook-log.jsonl.
#   log_hook.sh pre|post
# Never blocks: always exit 0 with no decision. Keep it fast — timeouts are fail-open anyway.
set -u
phase="${1:-event}"
log="${HOOK_LOG:-.github/hooks/hook-log.jsonl}"
payload="$(cat 2>/dev/null || true)"
mkdir -p "$(dirname "$log")" 2>/dev/null || true
if command -v python3 >/dev/null 2>&1; then
  PHASE="$phase" PAYLOAD="$payload" python3 -c '
import json, os, time
raw = os.environ["PAYLOAD"]
try: p = json.loads(raw) if raw.strip() else {}
except Exception: p = {"raw": raw}
print(json.dumps({"phase": os.environ["PHASE"], "loggedAt": int(time.time()), "payload": p}))
' >> "$log" 2>/dev/null || true
else
  printf '{"phase":"%s","raw":%s}\n' "$phase" "\"(python3 missing)\"" >> "$log" 2>/dev/null || true
fi
exit 0
