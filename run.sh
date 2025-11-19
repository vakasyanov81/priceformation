#!/bin/bash
export PYTHONPATH=./
uv sync --no-default-groups
uv run python run.py