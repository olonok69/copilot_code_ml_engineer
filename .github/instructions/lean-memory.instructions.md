---
applyTo: "**"
description: Keep always-on agent memory lean (AGENTS.md + instructions); detail lives in data/changes/
---

# Lean memory

- `AGENTS.md`, `.github/copilot-instructions.md` and `.github/instructions/` stay small: map, gates, one-line pointers.
- Ticket history, playbooks and sharp edges live under `data/changes/` — read on demand, never paste into always-on files.
- One canonical ledger per fact (write-once). Instructions point; they do not duplicate.
