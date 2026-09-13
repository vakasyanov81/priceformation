---
name: vulture-check
description: >-
  Run vulture unused-code checks via `uv run vulture`.
  Use when the user asks to check for dead code, run vulture, verify unused
  names after edits, or fix vulture findings.
---

# Vulture Check

## When to use

- User asks to check for unused / dead code or run vulture
- After editing Python files, before considering the work done
- When fixing vulture findings

## How to run

From the project root, always use the project config:

```bash
uv run vulture
```

Rules:

1. Always use `uv run vulture` (project env), never system `vulture`.
2. Do not pass paths or `--min-confidence` unless the user explicitly asks. Config comes from `[tool.vulture]` in `pyproject.toml`.
3. Do not scan `.` — that would include `.venv` and `mutants`.

## After the check

1. If vulture exits 0 — report that the repository is clean.
2. If there are findings — list them briefly (file:line + name + confidence).
3. Fix issues only when the user asked to fix them (or when you are finishing edits you just made and need a clean result).
4. Prefer deleting unused code. For protocol / hook arguments, prefix the name with `_`. For remaining false positives, add a whitelist module and include it in `[tool.vulture] paths`.
5. Re-run `uv run vulture` after fixes until clean.
