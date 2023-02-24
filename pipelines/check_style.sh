#!/bin/bash
cd ..
export PYTHONPATH=./
export WORK_DIR=./
echo '\n--- ruff ---\n'
poetry run ruff .
echo '\n--- black ---\n'
poetry run black . --check
# poetry run black . --diff --color
# poetry run black .
echo '\n--- pylint ---\n'
poetry run pylint --rcfile ./pipelines/.pylintrc ./
