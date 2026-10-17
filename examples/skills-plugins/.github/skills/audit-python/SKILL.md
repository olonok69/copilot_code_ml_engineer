---
name: audit-python
description: >-
  Audit Python dependencies with pip-audit and verify the app still works.
  Use when the user asks for pip-audit, a Python CVE check, or an audit of a
  requirements.txt project (e.g. the ex_app demo target). For Node/npm, use the audit skill.
---

# Dependency audit (Python)

Target: a folder with `requirements.txt` (demo: `ex_app/`).

1. `cd` into the target app (or the path the user named).
2. Make sure `pip-audit` is available: `python -m pip install pip-audit` if needed.
3. Run `python -m pip_audit -r requirements.txt` (or the requirements file the user names).
4. **Do not** apply major upgrades automatically. If the user asks for a safe fix:
   `python -m pip_audit -r requirements.txt --fix` only after explicit confirmation.
5. Tests:
   - If there is `pytest` / `tests/` / `test_*.py` → run `pytest` (or the README's command).
   - If there is no suite → minimal smoke: `python -m py_compile` / `python -c "import …"` on the main modules.
6. Summarise: CVEs found (if any), fixes applied (if any), test/smoke result.

Always show the real command output (evidence over claims).

If the target is Node (`package.json`), **do not invent pip** — say to use `/audit`.
