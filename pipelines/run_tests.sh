#!/bin/bash
cd ..
export PYTHONPATH=./
. ./venv/bin/activate
python3 -m pip install -r ./dev_requirements.txt
pytest ./tests
deactivate
