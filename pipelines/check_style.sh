#!/bin/bash
printf '\n--- black ---\n\n'
uv run black --line-length 120 --target-version py311 --skip-string-normalization "$WORK_DIR"
# poetry run black . --diff --color
# poetry run black .
printf '\n--- pylint ---\n\n'
uv run pylint --rcfile "$WORK_DIR/pipelines/.pylintrc" "$WORK_DIR"
