#!/bin/bash
cd ..
pip install pipx
pipx install poetry
poetry check
poetry lock --check
poetry install
