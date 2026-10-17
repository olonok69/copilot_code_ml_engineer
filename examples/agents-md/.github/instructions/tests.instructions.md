---
applyTo: "tests/**/*.py,**/test_*.py"
excludeAgent: "code-review"
---

# Tests

- Write the failing test first (RED), then the fix (GREEN).
- Assert on the member **list** (ids/titles), never only on a total `len(...)`.
- Run scoped first: `.venv/bin/pytest tests/<area> -q`, then the full suite.
