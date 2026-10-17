# A real example, end to end (GitHub Copilot)

> Same sanitized case as in the Claude Code course; the orchestrating agent is **GitHub Copilot**
> (CLI or VS Code, Copilot harness).
> MCP tools and gates identical in role.

## The symptom

QA: *"The **'applicable law'** field shows empty in the UI, but it is written in the PDF."*
Attaches document + JSON from the `status endpoint`.

---

### 1 · Orient

**Copilot, first, without touching code:**
- Skill **`kg`** with topic `"end of provision"` (or `kg_query.sh` / STATUS fallback) → danger zone +
  sharp edge *"the cut is applied in 3 places; do not unify."*
- Reads the pointed writeup and `STATUS.md`.
- `git branch -a` + `gh pr list` → correct base, no duplicate PR.

### 2 · Inbound triage

Contract JSON: field **empty** → the extraction service's responsibility. Playwright (built into the CLI) confirms on the real UI.

### 3 · Provenance

Repro on prior baseline → **pre-existing**. Changes the story to QA; the fix is still worth doing.

### 4 · Investigate

- CodeGraph `codegraph_explore` (survey + blast radius) — do not open the entire 5k-line extractor.
- Serena for precise symbols / refs.
- `_diag_pdf.py` (oracle): layout without LLM → overflow into 2nd column. **Zero model calls to diagnose.**

### 5 · Plan

**Plan mode** (`/plan`): options + trade-offs; fix keyed on a structural property (multi-column), not on the
client's string. Human approves. Rejected option documented.

### 6 · Implement

Leave plan mode: RED test → minimal code → GREEN.

### 7 · Verify

Scoped + byte-identical regression (no-op) + outbound in **five checks**: validate the instrument ·
wrapper · local JSON (member list, not a total) · Docker image · look at the output.

### 8 · Document

Write-once: ticket note, STATUS, QA acceptance, handover.

### 9 · Sanitise

Skill `sanitise-diff` on added lines of the staged diff.

### 10 · Handoff

Branch + handover ready. **No** push/PR unless the human asks explicitly
(`preToolUse` hook `block-external-git` + instructions; CLI `/pr automerge` is human-only by rule).
Copilot *is* the agent → the human gate remains mandatory. If the work was delegated to the cloud agent, it
lands as a draft PR on a `copilot/` branch that it cannot mark ready, approve or merge.

### 11 · Bot review + persist

Copilot code review triage (approvals off); extra test; lesson → `PLAYBOOK.md`; `kg-refresh` if the graph should see the new ticket.

---

## Tool per stage

| Stage | Tool |
|---|---|
| Orient | Skill **`kg`** · STATUS · git · gh |
| Triage | Playwright / F12 |
| Investigate | CodeGraph · Serena · `_diag_*.py` |
| Plan | Plan mode (`/plan`) |
| Implement / verify | pytest · wrapper · Docker |
| Sanitise / handoff | `sanitise-diff` · human (+ hook) |

## Takeaway

No stage is “ask the LLM to fix it.” Deterministic gates channel the model.
The product (Claude Code, Cursor, Copilot) changes; the discipline does not.
