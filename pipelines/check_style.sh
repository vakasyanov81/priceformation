#!/bin/bash
echo '\n--- ruff ---\n'
poetry run ruff $WORK_DIR --fix
echo '\n--- black ---\n'
poetry run black $WORK_DIR
# poetry run black . --diff --color
# poetry run black .
echo '\n--- pylint ---\n'
poetry run pylint --rcfile $WORK_DIR/pipelines/.pylintrc $WORK_DIR
