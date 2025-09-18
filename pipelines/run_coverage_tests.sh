#!/bin/bash
cd ..
export PYTHONPATH=./
# poetry shell
poetry run pytest --cov ./ ./tests  --cov-report term-missing:skip-covered --cov-config=./.coveragerc
