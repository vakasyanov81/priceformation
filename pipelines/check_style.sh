#!/bin/bash
printf '\n--- black ---\n\n'
uv run black --line-length 120 --target-version py311 --skip-string-normalization "$WORK_DIR"
# poetry run black . --diff --color
# poetry run black .
printf '\n--- ruff ---\n\n'
uv run ruff check "$WORK_DIR"
