#!/bin/bash
echo '\n--- black ---\n'
poetry run black $WORK_DIR
# poetry run black . --diff --color
# poetry run black .
echo '\n--- pylint ---\n'
poetry run pylint --rcfile $WORK_DIR/pipelines/.pylintrc $WORK_DIR
