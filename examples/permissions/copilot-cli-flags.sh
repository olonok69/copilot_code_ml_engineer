#!/usr/bin/env bash
# Illustrative Copilot CLI permission flags (verified against the CLI reference, 2026-10-17).
# Pattern syntax: Kind(argument). Deny ALWAYS beats allow — even with --allow-all / --yolo.
# Flags are never persisted; saved approvals live in ~/.copilot/permissions-config.json.
set -eu
copilot -p "Run the unit tests and summarise failures" -s --no-ask-user \
  --allow-tool='shell(npm test)' \
  --allow-tool='shell(git:*)' \
  --allow-tool='write(src/*.ts)' \
  --allow-tool='codegraph' \
  --deny-tool='shell(git push)' \
  --deny-tool='shell(gh pr)' \
  --deny-tool='read(.env)' \
  --deny-url='example.com'
# Hide tools from the model entirely:      --excluded-tools / --available-tools
# Interactive: /permissions [default|assisted|allow-all|show|reset]   (assisted = an LLM judge recommends)
