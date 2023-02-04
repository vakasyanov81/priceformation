#!/bin/bash
cd ..
export PYTHONPATH=./
. ./venv/bin/activate
python3 -m pip install -r ./dev_requirements.txt
flake8 . --count --select=E9,F63,F7,F82 --exclude venv --show-source --statistics
flake8 . --count --exit-zero --max-complexity=7  --exclude venv --max-line-length=120 --statistics
deactivate
