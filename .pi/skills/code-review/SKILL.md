---
name: code-review
description: >-
  Review the current diff for correctness bugs and reuse/simplification/efficiency
  cleanups at the given effort level (low/medium: fewer, high-confidence findings;
  high→max: broader coverage, may include uncertain findings). Use when the user
  asks for a code review, /code-review, or to review a branch, PR, or diff.
  Pass --comment to post findings as inline PR comments, or --fix to apply the
  findings to the working tree after the review.
---

# Code Review

Port of Claude Code's bundled `/code-review` skill. Reviews a diff for
correctness bugs plus reuse, simplification, and efficiency cleanups.

## Arguments

`/code-review [level] [target] [--comment] [--fix]`

| Token | Meaning |
|---|---|
| `low` / `medium` / `high` / `xhigh` / `max` | Effort. Default: `high` |
| `ultra` | Not available here — run `max` instead |
| target | Optional PR number, branch, ref range (`main...feature`), or path |
| `--comment` | After the review, post surviving findings as inline PR comments via `gh` |
| `--fix` | After the review, apply surviving findings to the working tree |

If the user did not name a level, use `high`. Everything after the level and
flags is the review target.

## Cursor mapping

When an effort file says **Task tool**, launch subagents with:

- `subagent_type: generalPurpose`
- `run_in_background: false`
- a short `description` naming the angle or verifier
- the diff (or how to obtain it), the angle/verifier instructions, and the
  required return shape inside `prompt`

Launch **all finder angles in parallel** in one message. After they return,
dedup, then launch **all verifiers in parallel**. Do not wait on one finder
before starting the others.

When an effort file mentions `CLAUDE.md`, also read any of these that exist
and apply the same quote-the-rule bar:

- repo-root `AGENTS.md`, `CLAUDE.md`, `CLAUDE.local.md`
- `.cursor/rules/**/*.mdc`
- `~/.claude/CLAUDE.md` and `~/.cursor/rules/` if present
- any `CLAUDE.md` / `AGENTS.md` in an ancestor of a changed file

There is no `ReportFindings` tool. After verification, show the user a ranked
list (`file:line` — summary, then the failure scenario), then the JSON array
from the effort file. If nothing survived, say so and return `[]`.

Do not flag style, naming, formatting, or lint that this repo's CI already
enforces (Black, Ruff, flake8/WPS, mypy).

## Pipeline

1. Parse arguments (level, target, `--comment`, `--fix`).
2. Follow **Phase 0** in the matching effort file to gather the diff.
3. Read and follow that file exactly (caps, angles, verify, sweep):
   - [low.md](low.md) — 1 diff pass, no subagents, no verify, ≤4 findings
   - [medium.md](medium.md) — 8 angles × 6, precision verify, ≤8 findings
   - [high.md](high.md) — 8 angles × 6, recall-biased verify, ≤10 findings (default)
   - [xhigh.md](xhigh.md) — 10 angles × 8, verify, gap-sweep, ≤15 findings
   - [max.md](max.md) — same pipeline as xhigh
4. If `--fix`: apply surviving findings to the working tree. Do not apply
   cleanup-only items unless the user also asked to clean up.
5. If `--comment`: post only surviving findings as inline comments on the open
   PR (`gh api` / `gh pr comment`). Skip if there is no PR.

## Output to the user

Lead with the count and effort level, then the ranked list. Correctness bugs
always outrank cleanup, altitude, and conventions when the cap forces a cut.
Do not hunt for extra issues beyond the effort file's pipeline.
