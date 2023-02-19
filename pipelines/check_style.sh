#!/bin/bash
cd ..
export PYTHONPATH=./
. ./venv/bin/activate
python3 -m pip install -r ./dev_requirements.txt
python3 -m ruff .
deactivate
