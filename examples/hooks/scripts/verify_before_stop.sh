#!/usr/bin/env bash
# agentStop "verify before stop" gate. If the working tree has changes under src/ or tests/ but no fresh
# verification marker (.verify-ok, written by your test command, newer than the newest change), force one
# more turn: {"decision":"block","reason":"..."}. The CLI has a runaway guard after 8 blocks.
# Otherwise: exit 0 + "{}" (let the agent stop).
set -u
cat >/dev/null 2>&1 || true
changed="$(git status --porcelain -- src tests 2>/dev/null | awk '{print $2}')"
[ -z "$changed" ] && { printf '{}\n'; exit 0; }
newest=0
for f in $changed; do
  [ -e "$f" ] || continue
  t="$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null || echo 0)"
  [ "$t" -gt "$newest" ] && newest="$t"
done
marker=0
[ -e .verify-ok ] && marker="$(stat -c %Y .verify-ok 2>/dev/null || stat -f %m .verify-ok 2>/dev/null || echo 0)"
if [ "$marker" -lt "$newest" ]; then
  printf '{"decision":"block","reason":"src/ or tests/ changed after the last verification. Run the scoped tests (they touch .verify-ok on success) and show the output before stopping."}\n'
  exit 0
fi
printf '{}\n'
exit 0
