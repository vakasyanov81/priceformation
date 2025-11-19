#!/bin/bash
cd ..
export PYTHONPATH=$WORK_DIR
# poetry shell
uv run pytest --cov ./ ./tests  --cov-report term-missing:skip-covered --cov-config=./.coveragerc
