# SST-6880 methodology replay (Copilot) — baseline-only run

**Date:** 2026-10-28  
**Goal:** reproduce the pre-fix understanding path for SST-6880 from a historical baseline, without implementing code.

## Scope and constraints

- Used this backup checkout at `/mnt/d/repos3/ILS_2/document-parser-lambda`.
- Created historical branch from the ticket-referenced baseline commit:
  - Branch: `replay/sst-6880-pre-fix`
  - Commit: `7559f8434ebed84f5a9d3707ada597e356bd66ae` (`SST-6811 ...`, 2026-10-01)
- No code edits, no commits, no push.
- Evidence files were read-only; source document mtimes were not changed.
- Note: the existing fix-plan file had already been read earlier in session, so this is not a fully blind replay.

## Problem/evidence-only conclusion

From ticket body + 2026-10-02 evidence:

1. The issue is **not SST-5213 regression**; it was already present in June.
2. The missing provision is the 13-word title:
   - `Sections 6038, 6038B, 6046 and 6046A of the Code and the Treasury Regulations`
3. Symptom matches the user report:
   - expected provision 59 is swallowed into provision 58 description,
   - resulting visible row shift after that point.

## Baseline code check (commit `7559f84`)

In [doc_extractor.py](/mnt/d/repos3/ILS_2/document-parser-lambda/src/data_extractors/doc_extractor.py):

- [is_potential_title](/mnt/d/repos3/ILS_2/document-parser-lambda/src/data_extractors/doc_extractor.py:689) rejects titles at `len(words) >= TITLE_LEN_MAX` (13).
- [_underlined_lead_in_titles](/mnt/d/repos3/ILS_2/document-parser-lambda/src/data_extractors/doc_extractor.py:832) stops at the first non-empty non-underlined run, so typed-number prefixes (`59.`) block lead-in collection when numbering is plain text.
- [_is_acceptable_title](/mnt/d/repos3/ILS_2/document-parser-lambda/src/data_extractors/doc_extractor.py:898) only rescues long titles when they appear in underlined lead-ins.

This baseline logic is consistent with the observed miss for typed-number + underlined-title paragraphs.

## Methodology gates replay (plan-only, no implementation)

### Gate 1 — Problem statement
Pass. Reconstructed precise observable behavior and acceptance target from [\_new_ticket_body_long_underlined_title.md](/mnt/d/repos3/ILS_2/document-parser-lambda/data/changes/sst-6880/_new_ticket_body_long_underlined_title.md) and [qa_acceptance_criteria.md](/mnt/d/repos3/ILS_2/document-parser-lambda/data/changes/sst-6880/qa_acceptance_criteria.md).

### Gate 2 — Root-cause hypothesis
Pass. Hypothesis: length gate is strict at 13+, and underlined rescue is bypassed when a typed number run appears before underlined title text.

### Gate 3 — Contract alignment
Pass. Contract remains: do not raise the 13-word limit globally; only restore intended underlined rescue behavior for typed-number layout.

### Gate 4 — RED test intent
Pass (design). Add RED tests for typed-number + underlined lead-in handling and negative controls (`59.5`, `Section 5.`, `(a)`, missing dot, etc.), while keeping existing [test_sst_5030_long_underlined_title.py](/mnt/d/repos3/ILS_2/document-parser-lambda/tests/test_sst_5030_long_underlined_title.py) green.

### Gate 5 — Blast-radius measurement intent
Pass (design). Re-run lead-in old-vs-new diff over corpus and report only outcome-changing long titles (`ignore_length=True` passers), as ticket notes describe.

### Gate 6 — Agreement before code
Pending user approval. No implementation done in this replay.

## Runtime verification at the baseline (run on a copy; original evidence untouched)

Cold imports of the extractor from `/mnt/d` take ~5 min (I/O bound; ~1.5-2 min once cached), so earlier short timeouts were a tooling limit, not a defect. Running needs dummy `SQS_LAMBDACLIENTSL` / `SQS_MATTERRPCSERVICE` values; no network or LLM was used.

- Existing `tests/test_sst_5030_long_underlined_title.py`: **17 passed** (baseline is green; A6 contract holds).
- Probe on a copy of the evidence letter, paragraph runs: `59.` (not underlined), tab, `Sections ...` (underlined), `. The General Partner...` (not underlined).
  - Title length: 13 words; `is_potential_title` default **False**; with `ignore_length=True` **True** (length is the only failing filter).
  - Title found among underlined lead-ins: **False**; underlined lead-ins collected in the whole document: **1** (of ~94 headings).
  - `_is_acceptable_title`: **False**, so the long-title rescue never fires.
  - Source file modification time unchanged.

This independently reproduces the root cause recorded in the ticket, with the identical mechanism. Not done: wrapper-level re-extract (94 provisions), which needs the full extractor chain and was not run; no RED test written; gate 6 (agreement) still pending.

## RED gate (tests only, no fix)

New file `tests/test_sst_6880_typed_number_underlined_title.py` (14 tests, untracked, not committed) on the baseline branch:

- **5 fail (expected RED):** typed `59.` + tab in separate runs, in one run, followed by a space, number split across runs (`5`,`9`,`.`), and the `_is_acceptable_title` gate for the long underlined title.
- **9 pass (guards that must stay green):** no-number layout unchanged; `59.5`, `Section 5.`, `59. The`, `(a)`, `59` (no dot) not skipped; the number is not part of the lead-in; the same title not underlined is still rejected; `TITLE_LEN_MAX` still 13.
- Failures are assertion failures on the target behaviour, not import or setup errors.

Remaining: gate 6 (agreement), then fix, GREEN, wrapper re-extract (94 provisions) and corpus blast-radius diff.

## GREEN and blast radius (local, uncommitted; to be reverted)

Fix (one function, `_underlined_lead_in_titles` in `doc_extractor.py`, +18/-1, plus two small regexes): while no underlined text is collected yet, buffer the preceding plain text; keep going only while it is still a prefix of a bare typed number (`\d{1,3}\.?`), and accept the underlined run only if the buffer is empty or exactly `\d{1,3}\.`. No threshold, prompt or config change.

- New tests 14/14 GREEN; existing SST-5030 suite 17/17 still GREEN (31 passed together).
- No-LLM lead-in diff over the local DOCX corpus (ticket script, canary first): control silent (no gain/loss on a normal layout); typed-number letter gains its long title; 8 files gain lead-ins (61, 90, 88, 266, 409, 3, 14, 1); exactly **1** entry can change an outcome (the 13-word title). Counts equal the ticket's recorded sweep. The output file differs byte-wise from the recorded one (I overwrote it without keeping a byte copy); its counts match.
- **Not run (needs approval):** the wrapper-level re-extract (expects 94 provisions), because it runs the real extractor, probably including LLM calls on a customer document. The broader regression battery was not run either.
- Revert plan: `git checkout -- src/data_extractors/doc_extractor.py`, delete the new test file, and restore or ignore the ticket-folder JSON.

## Wrapper re-extract with the real LLM path (approved) and regression subset

- The host venv has `ils-message-broker` 0.1.3 while the baseline requires v0.1.5, so the wrapper import fails there. The run used the deployed-image build (`provision/document-parser`, linux/amd64) with this branch mounted read-only, as the ticket's own second run did. Real model calls were made, on a copy of the evidence letter; the original file's modification time was unchanged.
- Result: **94 provisions**; row 59 titled "Sections 6038, 6038B, 6046 and 6046A of the Code and the Treasury Regulations" with the body starting "The General Partner..."; row 58 no longer contains "59. Sections"; row 60 is "Certain Investments - International Boycotts", numbered `60.`. All six script checks passed. This equals the ticket's recorded outcome. Row 57 still shows `[Reserved` (out of scope, as the ticket says).
- Regression subset (14 title, numbering and underline test files, host venv): **235 passed, 1 skipped, 2 deselected**, 0 failed. This is a related subset, not the full battery.
- Check 3 of the acceptance criteria (the other two letters) is covered by the lead-in diff, as the criteria allow; no fresh upload.
- Still owed in the real flow, not testable here: re-upload on the deployed function after a merge.
- Temporary files in `/tmp` were removed. Everything stays uncommitted; revert as described above.

## Sanitiser and full regression (follow-up)

- **Fix revert:** the fix and tests are reverted; archived as `copilot_replay/fix.diff` and `copilot_replay/test_sst_6880_typed_number_underlined_title.py.txt`.
- **sanitise-diff on the real diff:** run in a disposable repo (nothing staged in the checkout) over the 134 added lines of the fix plus tests. Machine-local name list (11 entries): 0 hits. Secrets, account ids, e-mail addresses, agent attribution: 0 hits. One hit: an internal ticket id (SST-5030) in the new test's docstring. The repo's own source and test files carry such ids routinely (106 `test_sst_*` files), so this follows local convention, but a strict handoff would remove or reword it. Ready for human handoff: yes, with that one decision.
- **Full suite, baseline vs fix** (host venv, `--continue-on-collection-errors`):
  - baseline: 1552 passed, 3 failed, 4 skipped, 5 collection errors
  - with the fix: **1566 passed** (+14 = the new tests), the same 3 failed, 4 skipped, same 5 errors
  - Identical failures in both runs, so no regression from the fix. The 3 failures (AI-provider client recreation, two PDF Textract cascade tests) and the 5 collection errors (5 test files that import the broker, hit by the venv's broker 0.1.3 instead of the required v0.1.5) are environment-related and were not investigated further. Those 5 files did not run, so they are not covered here.

## Closing state (end of day, 2026-10-28)

- Replay branch `replay/sst-6880-pre-fix` deleted; checkout back on `fix/sst-5778-numbering-start-value`. Source and test changes reverted; nothing committed or pushed.
- `canary_leadin_diff.json` was overwritten by the corpus-diff re-run. It has been **restored from the bucket** (read-only `s3 cp`, `dev-nonprod`; local copy now matches the 2026-10-06 original, 2689 bytes). The overwritten version differed only in list order of the same entries, so the recorded counts stand.
- Archived fix and tests remain in `copilot_replay/` (`fix.diff`, test as `.txt`).
- `day end`: only a dry-run preview and a read-only activity check were run. No push. Preview flagged that two `knowledge-graph/_corpus` files would upload despite the contributor rule; they must be excluded in any real publish. No STATUS/FOLLOWUPS row written; `kg-refresh` out of scope.
- Serena registered in `~/.copilot/mcp-config.json` (backup `.bak-pre-serena`); fallback order CodeGraph, Pylance usages, grep.
