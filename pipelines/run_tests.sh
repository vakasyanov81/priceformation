#!/bin/bash
cd ..
export PYTHONPATH=$WORK_DIR
# poetry shell
poetry run pytest ./tests --verbose --lf --maxfail=3
