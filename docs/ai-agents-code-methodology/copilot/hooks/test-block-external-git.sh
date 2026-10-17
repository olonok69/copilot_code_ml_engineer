#!/usr/bin/env bash
# Offline tests for block-external-git.{sh,ps1}. Run from the repo root:
#   bash .github/hooks/test-block-external-git.sh          # bash twin
#   PS=1 bash .github/hooks/test-block-external-git.sh     # also the PowerShell twin (pwsh or powershell.exe)
# Canary first: a known-deny case must deny, or every "allow" below proves nothing.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
fail=0; n=0

run_sh() { printf '%s' "$1" | bash "$HERE/block-external-git.sh" >/dev/null 2>&1; echo $?; }
run_ps() {
  local exe
  exe="$(command -v pwsh || command -v powershell.exe)"
  local script="$HERE/block-external-git.ps1"
  if [[ "$exe" == *.exe ]] && command -v wslpath >/dev/null; then script="$(wslpath -w "$script")"; fi
  printf '%s' "$1" | "$exe" -NoProfile -ExecutionPolicy Bypass -File "$script" >/dev/null 2>&1; echo $?
}

check() { # expected_exit description payload
  local want="$1" desc="$2" payload="$3" got
  n=$((n+1)); got="$(run_sh "$payload")"
  if [ "$got" != "$want" ]; then echo "FAIL sh  [$desc] want=$want got=$got"; fail=$((fail+1)); else echo "ok   sh  [$desc]"; fi
  if [ "${PS:-0}" = "1" ]; then
    got="$(run_ps "$payload")"
    if [ "$got" != "$want" ]; then echo "FAIL ps1 [$desc] want=$want got=$got"; fail=$((fail+1)); else echo "ok   ps1 [$desc]"; fi
  fi
}

# --- canary (known answer) ---
check 2 "canary: git push, toolArgs as JSON string" '{"toolName":"bash","toolArgs":"{\"command\":\"git push origin main\"}"}'
# --- deny ---
check 2 "git push, toolArgs object"            '{"toolName":"bash","toolArgs":{"command":"git push"}}'
check 2 "git -C dir push"                      '{"toolName":"bash","toolArgs":{"command":"git -C repo push --force"}}'
check 2 "chained after commit"                 '{"toolName":"bash","toolArgs":{"command":"git commit -m x && git push"}}'
check 2 "gh pr create"                         '{"toolName":"bash","toolArgs":{"command":"gh pr create --fill"}}'
check 2 "gh pr merge --auto (automerge shape)" '{"toolName":"bash","toolArgs":{"command":"gh pr merge 12 --auto --squash"}}'
check 2 "gh pr ready"                          '{"toolName":"powershell","toolArgs":{"command":"gh pr ready 12"}}'
check 2 "gh api merge endpoint"                '{"toolName":"bash","toolArgs":{"command":"gh api -X PUT repos/o/r/pulls/7/merge"}}'
check 2 "terraform apply"                      '{"toolName":"bash","toolArgs":{"command":"terraform apply -auto-approve"}}'
check 2 "VS Code Local snake_case payload"     '{"tool_name":"run_in_terminal","tool_input":{"command":"git push"}}'
check 2 "unparseable payload mentioning push"  'not json git push'
# --- no-op (exit 0) ---
check 0 "git status"                           '{"toolName":"bash","toolArgs":{"command":"git status"}}'
check 0 "git log"                              '{"toolName":"bash","toolArgs":{"command":"git log --oneline -5"}}'
check 0 "gh pr view"                           '{"toolName":"bash","toolArgs":{"command":"gh pr view 12"}}'
check 0 "non-shell tool whose content says git push" '{"toolName":"edit","toolArgs":{"path":"README.md","content":"never git push"}}'
check 0 "empty payload"                        ''

echo "---"; echo "$n cases, $fail failures"
[ "$fail" -eq 0 ]
