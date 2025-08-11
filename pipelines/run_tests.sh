#!/bin/bash
cd ..
export PYTHONPATH=./
# poetry shell
poetry run pytest ./tests --verbose --lf --maxfail=3
