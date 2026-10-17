---
applyTo: "**"
excludeAgent: "code-review"
---

# Tool prevalence (cheap and deterministic before expensive and probabilistic)

## Navigation / investigation

1. **CodeGraph `codegraph_explore` first** for "what is this / who depends / blast radius / is it tested?".
   Treat the returned source as already read.
2. **Serena `find_referencing_symbols`** before any rename or delete (disambiguates homonyms by class).
3. grep / file reads only for literals, configs or docs the graphs cannot follow.
4. Noisy research → a read-only subagent (`refactor-scout`, or the built-in `explore`); only its summary
   comes back.

## Orientation / history

- The **`kg` skill** (ticket knowledge graph) before grepping `data/changes/`.
- Fallback: `STATUS.md` newest-first + per-ticket folders + git file-overlap history.

## Diagnosis

- Confirm root cause with a free deterministic oracle (parser, schema check, `_diag_*.py`) before a paid
  model loop. Reserve expensive runs to verify the finished fix against the live contract.

## Contract verification

- Inbound and outbound: Playwright against the consumer-visible surface (built in to the Copilot CLI — do
  not configure it twice).
- If the product ships in a container/image: verify inside that runtime, not only with green unit tests.
- External library questions: Context7 instead of training-cutoff guesses.
