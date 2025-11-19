#!/bin/bash
export PYTHONPATH=./
uv sync --no-dev --locked
uv run python run.py