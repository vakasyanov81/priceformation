#!/bin/bash
cd ..
pip install pipx
pipx install poetry
poetry check
poetry check --lock
poetry install --no-root
