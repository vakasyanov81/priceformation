#!/bin/bash
cd ..
uv PYTHONPATH=$WORK_DIR
# poetry shell
uv run pytest ./tests --verbose --lf --maxfail=3
