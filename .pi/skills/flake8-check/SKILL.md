---
name: flake8-check
description: >-
  Run flake8 lint checks on Python files via `uv run flake8`.
  Use when the user asks to check code for errors/lint, run flake8, verify
  style after edits, or fix flake8/WPS violations.
---

# Flake8 Check

## When to use

- User asks to check code for errors or run lint
- After editing Python files, before considering the work done
- When fixing flake8 / wemake (WPS) style issues

## How to run

From the project root, always check the whole repository:

```bash
uv run flake8 .
```

Rules:

1. Always use `uv run flake8` (project env), never system `flake8`.
2. Always run against the whole repository (`.`). Do not narrow to changed files or directories unless the user explicitly asks.
3. Config comes from project `setup.cfg` — do not override with flags unless the user asks.

## After the check

1. If flake8 exits 0 — report that the repository is clean.
2. If there are violations — list them briefly (file:line + code + message).
3. Fix issues only when the user asked to fix them (or when you are finishing edits you just made and need a clean result).
4. Re-run `uv run flake8 .` after fixes until clean.
