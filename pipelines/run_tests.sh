#!/bin/bash
cd ..
export PYTHONPATH=./
poetry shell
pytest ./tests
