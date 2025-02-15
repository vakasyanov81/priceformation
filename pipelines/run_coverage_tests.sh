#!/bin/bash
cd ..
export PYTHONPATH=./
# poetry shell
coverage run --branch -m pytest ./tests  --cov-report term-missing:skip-covered --cov-config=./.coveragerc
