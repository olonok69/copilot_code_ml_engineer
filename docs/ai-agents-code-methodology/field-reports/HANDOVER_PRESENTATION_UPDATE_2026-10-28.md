# Handover: update the presentation with the 2026-10-28 Copilot field test

Two reports in this folder record what was actually run, on a real workday, with GitHub Copilot on the ILS methodology:

- `COPILOT_METHODOLOGY_LIVE_VALIDATION_2026-10-28.md` — skill-by-skill results (day start, evidence, viewer, Atlassian, kg, CodeGraph, Serena, sanitiser) with addenda.
- `COPILOT_SST-6880_METHOD_REPLAY_2026-10-28.md` — independent historical replay of one ticket through plan, RED, GREEN, 5 gates.

## What we did

1. **Day start** (`day` skill): synced the shared record, fixed `LOCAL_DATA` in `config.env`, regenerated `IDENTITY.md`, pulled with a snapshot first. Passed.
2. **Evidence + viewer**: captured two dev-environment runs read-only, then rendered the captured outputs in the local viewer. Passed.
3. **Atlassian**: read-only Jira/Confluence GETs approved and passed.
4. **Historical replay of SST-6880** on a backup clone, branch cut from the pre-fix commit `7559f84`:
   - From the problem text and evidence alone, Copilot reached the same root cause as the earlier agents (a 13-word title fails the length check; the typed number run stops the underline collector). Caveat: the fix plan had been read earlier, so this is **not a blind test**.
   - RED: 14 tests, 5 failing as intended, 9 guards.
   - GREEN: ~18 added lines plus 2 regexes; 31 targeted tests pass; corpus diff matched the ticket's recorded counts.
   - Real LLM re-extract in the deployed image: 94 provisions, all six checks passed.
   - Sanitiser on the real diff: 0 name/secret/attribution hits; 1 internal ticket id in a test docstring (repo convention).
   - Full suite: baseline 1552 passed / 3 failed; with fix 1566 passed / same 3 failed. 5 files did not run (broker 0.1.3 vs required v0.1.5 in the host venv) — environment, not the fix.
   - Everything reverted; replay branch deleted; nothing committed or pushed. Fix and tests archived as `fix.diff` and a `.txt` test copy.
5. **Serena**: was missing in Copilot because never registered (Cursor and Claude Code had it). Registered in `~/.copilot/mcp-config.json`; after restart `find_symbol`, references, a refusing `safe_delete_symbol` and a 7-change `rename_symbol` all worked (rename reverted). First call per session is slow (~1 min LSP warm-up). Fallback order: CodeGraph, Pylance usages, grep.
6. **Day end**: minimal only — dry-run publish preview and read-only activity ledger. **No upload.** Preview showed two `knowledge-graph/_corpus` files that would upload despite the contributor rule, so a real publish must exclude them; never use `--delete`. An overwritten `canary_leadin_diff.json` was restored from the bucket.

## What to change in the presentation

- Replace "Copilot parity is expected" claims with **measured** results from the list above; cite the two reports.
- Add Serena as a live-verified Copilot capability (with the warm-up caveat and the fallback chain).
- State the limits honestly: not a blind test; Context7 not exposed in Copilot; `kg-refresh` and full `day end` publish not exercised; full `methodology-plan` template agreement and deployed-image re-upload check not done; 5 test files uncollectable in the host venv.
- Practical findings worth a slide: imports from `/mnt/d` take ~5 min cold; the extractor rewrites the DOCX it opens (work on copies); runs need dummy `SQS_*` env values; Serena edits land on disk slightly after the tool returns.

## Do not

- Project or copy customer evidence (IDs, documents) into slides. The reports contain none; keep it that way.
- Treat this as a statement that anything was published or merged. It was not.
