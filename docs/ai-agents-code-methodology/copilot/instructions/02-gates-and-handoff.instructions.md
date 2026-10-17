---
applyTo: "**"
excludeAgent: "code-review"
---

# Gates and handoff

## Inbound gate (before code)

1. Symptom visible at the **output contract**? If not → push back with evidence; do not patch.
2. **Provenance**: reproduce on the pre-change baseline → regression vs pre-existing.

## Implementation gate

1. Failing scoped test first (RED for the right reason). 2. Minimal code to GREEN. 3. Relevant suites green.

## Outbound gate (before "done") — five checks

1. **Canary the instrument** on a known-answer case before trusting any diagnostic that informs shipping.
2. Reproduce the fixed contract on the real output path (the wrapper/entrypoint the consumer sees).
3. Symptom gone; assert on the **member list**, never on a total alone.
4. Runtime parity inside the **shipping artifact** when applicable (deployed image or equivalent).
5. **Look at the output** (rendered), not only at counts — before/after for visual changes.

State what each gate can and cannot show. A clean run over inputs that cannot exercise the change proves
no-regression and nothing else.

## Document + sanitise

1. Write-once / append-only on shared ledgers (issue note, STATUS row, QA acceptance, handover).
2. Run the **`sanitise-diff` skill** on **added** staged lines (names, ticket IDs in code, secrets,
   agent self-attribution).

## Review loop

Triage automated reviewer findings — including Copilot code review — like a human's: fix, follow-up commit,
or dismiss **with a stated reason**. Copilot code-review approvals stay off; a bot approval is not the human
gate.

## Human gate

Prepare the branch and the handover note, then **stop**. Push, PR create/merge/ready, `/pr auto`,
`/pr automerge`, releases and deploys are the human's. Session continuity = rewrite the rolling entry-point
note for the next Copilot session.
