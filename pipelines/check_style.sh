#!/bin/bash
echo '\n--- black ---\n'
poetry run black --line-length 120 --target-version py311 $WORK_DIR
# poetry run black . --diff --color
# poetry run black .
echo '\n--- pylint ---\n'
poetry run pylint --rcfile $WORK_DIR/pipelines/.pylintrc $WORK_DIR
