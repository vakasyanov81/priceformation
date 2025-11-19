#!/bin/bash
cd ..
export PYTHONPATH=$WORK_DIR
# poetry shell
poetry run pytest --cov ./ ./tests  --cov-report term-missing:skip-covered --cov-config=./.coveragerc
