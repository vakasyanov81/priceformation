#!/bin/bash
cd ..
export PYTHONPATH=$WORK_DIR
# poetry shell
uv run pytest ./tests ./integration_tests --verbose --lf --maxfail=3
