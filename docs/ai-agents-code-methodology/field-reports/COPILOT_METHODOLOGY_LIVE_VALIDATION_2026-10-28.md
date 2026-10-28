# Copilot methodology validation — presentation field notes

**Date:** 2026-10-28
**Purpose:** explain what was actually exercised in the local development workflow, what the evidence supports, and what remains intentionally unverified. This is a bounded field test, not a claim of full parity with another agent or of production readiness.

## Executive summary

The methodology was exercised against a real non-production workday and two real development-environment document runs, while keeping mutation boundaries visible. The user explicitly excluded `day end` and `kg-refresh` from the demonstration scope. In an earlier active Copilot session, the user confirmed all eight personal skills were visible in the customization view; discovery is not treated as proof that every operation is safe or fully verified. The strongest live results are:

- The day-start safety checks identified a stale local sync target before any pull. After the user authorized correcting that local-only setting, the dry run found no files to upload, and the protected pull completed with snapshots and no `--delete`.
- The read-only evidence tool recovered the source, highlighted output, raw Lambda result, and scrubbed logs for two October 27 development runs. The downloaded source hashes matched the already-retained local originals.
- A local-only viewer rendered those captured results in the product frontend, without another AWS fetch, a new extraction run, or model calls.
- A bounded CodeGraph lookup returned source and dependency information for one known symbol.

Other methodology gates were exercised synthetically or remain gated: sanitizer used a disposable fake diff; planning was demonstrated with a synthetic issue and applied as analysis only to the observed case; a small authenticated Jira/Confluence read-only check passed after approval. The user explicitly excluded `kg-refresh` and `day end` from this validation scope.

## What the audience can see

A short demonstration can follow the path of a reported upload without exposing customer data:

1. **Orient safely.** Show the machine identity card and explain that AWS identity, local machine role, and shared activity are separate facts. The day-start routine checks for unpublished work before it can pull.
2. **Establish provenance.** Use the evidence tool to associate a reported development run with the exact source version and outputs captured at that time.
3. **Inspect, do not reprocess.** Open the local viewer made from the captured artifacts. It presents the extracted provisions and highlighted document using the product frontend, but does not invoke extraction again.
4. **Use code intelligence.** Show a one-symbol CodeGraph query and its bounded source/dependency result; do not expose internal graph labels or unrelated files.
5. **State the gates.** Explain that the plan, tests, sanitizer, and final human approval remain separate gates. A green check is only evidence for the scope it actually covered.

Use a redacted screen or synthetic fixture for a public audience. The actual evidence folders contain customer documents and should not be opened or projected to an audience that is not authorized to see them.

## Validation record

### Methodology and operating skills

| Skill / step | Result | What was actually exercised | Limits |
|---|---|---|---|
| `day` — start | **PASS, scoped** | On an actual workday, confirmed the local identity and non-production AWS access. The initial local target pointed at a different checkout; the user authorized a local-only correction. The `changes` dry run found no files to upload and flagged shared hub files newer than the last sync. The subsequent pull ran without `--delete`, created a pre-pull snapshot, moved upstream-deleted files aside, and completed. The relevant shared-file differences were inspected. | A local ownership conflict required an explicit, one-time human authorization for this test. That authorization is scoped to this workday and is not a general instruction to bypass role controls. `day end`/publish is explicitly excluded from this validation scope. `git fetch` was blocked because GitHub credentials were unavailable non-interactively; optional authenticated ticket-status refresh was skipped. |
| `evidence` | **PASS, live read-only fetch** | Fetched two known development runs from October 27 by their documented document IDs. Each capture has `run.json`, source DOCX, highlighted DOCX, raw Lambda `result.json`, and scrubbed `log.txt`. The captured source hashes matched the retained originals. The manifests show bucket versioning enabled and report that the current Lambda image has changed since the runs. | The captured raw Lambda result is not the consumer-facing `get-sl-upload-status` contract. The evidence tool does not collect that contract because it requires an application session. No processing was run on the captured source. The evidence material remains under the local, ignored `_evidence` area. |
| `preview` / viewer | **PASS, local captured-output view** | Built bundles from the already-downloaded evidence, converted the highlighted documents to PDFs using LibreOffice copies, and displayed both documents side-by-side in the local frontend with local mock APIs. Browser and API checks confirmed the viewer rendered extracted rows and document pages. Temporary containers, bundles, and services were stopped and removed. | This was deliberately not the normal before/after preview command: that command fetches from AWS and, unless before-only, runs extraction in Docker against the deployed image and can spend real model calls. This local view used captured results only; it validates visual presentation of those outputs, not the live `get-sl-upload-status` adapter or a new extraction. |
| `methodology-plan` | **PASS, synthetic exercise; real case analysis only** | Earlier, completed the six-part plan using a fabricated issue and stopped before implementation. For the current reported-upload case, the existing findings plus captured evidence were used to distinguish the MSL table-header mismatch from the unsupported LPA path; no implementation was proposed or made in this presentation task. | No production change, RED test, or code fix was attempted. The corrected-compendium parser experiment described in the existing case notes was performed earlier with the real monolith parser; it was not rerun as part of this validation. |
| `sanitise-diff` | **PASS, disposable fixture only** | Earlier, a disposable temporary Git repository with fabricated staged strings verified that the expected sanitizer categories are detected; a clean fixture returned no findings. | No production code diff was staged or sanitized here because this task made no source-code changes. |
| `atlassian` | **PASS, mocked and targeted live read-only** | Earlier, CLI help and the mocked suite passed (62 tests in the offline suite; the skill-specific mocked CLI suite also passed). After explicit approval, two Jira issue reads and one Confluence page metadata read returned successfully. | The raw responses were suppressed and not copied into this report. No page body, comments, XML export, or write path was tested. |
| `kg` | **PASS, metadata and bounded lookup** | A prior active Copilot `/kg count edges` request returned graph-size metadata only (3,921 nodes / 8,508 edges). This session also ran `kg_query.sh find signature`; it exited successfully with 22 matches, and the labels were kept out of the report. | The underlying script supports `explain`, `path`, and `find`, not the `count edges` syntax; a direct invocation with those arguments is not a valid count test and must not be presented as one. Do not refresh the graph from this contributor machine. |
| `kg-refresh` | **OUT OF SCOPE (user-confirmed)** | The user explicitly excluded `kg-refresh` from this validation. | No prepare, graphify, finalize, request, or publish operation was run. |

### Related methodology integrations

| Capability | Result | Evidence and boundary |
|---|---|---|
| CodeGraph | **PASS, bounded** | A query for one known Lambda handler returned one source file and its reported callers/dependencies. It was limited to one file. This is a navigation result, not a test-coverage guarantee. |
| Serena | **PASS, live in Copilot** | Serena was missing from Copilot only because it was never registered (Cursor and Claude Code both have it). After a `serena` entry was added to the personal `~/.copilot/mcp-config.json` (with approval; backup kept) and Copilot restarted, the tools loaded in the session. `initial_instructions` returned the manual; `find_symbol` located the target method; `find_referencing_symbols` returned its caller and the existing tests that use it. A standalone MCP run of the same command had passed earlier. | The first `find_referencing_symbols` call timed out while the Python language server warmed up (about a minute); the retry succeeded, so expect a slow first call per session. Serena writes its cache under the ignored `.serena/` and may report references inside ignored `data/` copies. Fallback order stays CodeGraph, then Pylance usages, then grep. On the pre-fix baseline, `safe_delete_symbol` refused to delete a referenced method and listed all 5 reference sites (nothing changed); `rename_symbol` to a throwaway name reported 7 changes and rewrote the definition, the one internal caller and the tests in 3 files (6 lines), then was reverted with git. The edits appeared on disk a little after the tool returned, so a `git diff` taken immediately showed nothing; re-check after a short wait. `replace_symbol_body` and the insert tools were not exercised. |
| Context7 | **CONNECTED, user-confirmed; not exercised here** | The user previously confirmed it was connected in the course-repository Copilot MCP view. This is discovery evidence, not proof of a documentation lookup in the target repository. |
| Offline suites | **PASS, prior run** | The evidence mocked suite passed 22 tests; the Atlassian mocked suite passed 62 tests. These are previously recorded results and were not rerun for this note. |

## Evidence locations and privacy

The two local run folders are under:

- `../_evidence/dev/2026-10-28/side_letters_27102026/`

The folder above contains customer source documents and raw extraction outputs. It is local evidence, not presentation material. Do not commit it, publish it, copy document contents into slides, or expose its identifiers. For the audience, use synthetic/redacted screenshots and report only aggregate test outcomes and the workflow boundaries.

The temporary viewer output was created outside `data/` and cleaned up after inspection. No commit, push, deployment, external message, or shared-record publish was made during the document-viewer test.

## Honest interpretation

This validates several real links in the methodology chain—orientation, protected read-only evidence capture, artifact provenance, and local visual inspection—and separately demonstrates planning and sanitization with synthetic inputs. It does **not** prove every skill is fully operational end-to-end:

- GitHub remote operations remain blocked by missing non-interactive credentials; broader Atlassian workflows beyond the approved metadata reads remain untested.
- The local viewer is not a real deployed-image re-extraction or consumer-contract test.
- Publisher-only knowledge-graph operations remain deliberately gated.
- Synthetic plan and sanitizer exercises do not demonstrate a real code fix passing RED → GREEN → deployed-runtime verification.

The presentation should describe this as a **bounded Copilot-led workflow validation**, with completed checks and limitations shown together.

## Addendum — SST-6880 historical replay (baseline branch)

A separate baseline replay was performed on branch `replay/sst-6880-pre-fix` at commit `7559f8434ebed84f5a9d3707ada597e356bd66ae` to mirror pre-fix conditions and run methodology gates without implementation. The replay report is in [COPILOT_SST-6880_METHOD_REPLAY_2026-10-28.md](/mnt/d/repos3/ILS_2/document-parser-lambda/data/changes/sst-6880/COPILOT_SST-6880_METHOD_REPLAY_2026-10-28.md).

## Addendum — follow-up checks (SST-6880 replay)

- `sanitise-diff` on the real fix diff (disposable repo): clean except one internal ticket id in a test docstring, which follows repo convention.
- Full suite, baseline vs fix: 1552 vs 1566 passed (+14 new tests), identical 3 failures and 5 broker-version collection errors in both runs; no regression from the fix. Those 5 files did not run.
- Serena rename/safe-delete exercised and reverted (see the Serena row).
- Context7: no tool was exposed in this Copilot session, so it stays "connected per user, not exercised".
- Still not done: deployed-image re-upload check (needs a merge), full `methodology-plan` template agreement, a blind run on an unseen ticket.

## Addendum — end of day state and handover

- `day end` exercised in minimal form: dry-run publish preview plus read-only activity ledger. No upload. The ledger shows this machine (desktop2) pulled today and last pushed 3 days ago.
- Preview caveats for whoever publishes: exclude `knowledge-graph/_corpus` (contributor rule), do not use `--delete`, and write a STATUS row first.
- `sst-6880/canary_leadin_diff.json` restored from the bucket after being overwritten by a re-run; no longer a publish risk.
- Not covered: blind run on an unseen ticket, Context7 lookup (no tool exposed), full `methodology-plan` template agreement, deployed-image re-upload check.
- Full detail: `sst-6880/COPILOT_SST-6880_METHOD_REPLAY_2026-10-28.md`.
