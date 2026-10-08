#!/bin/bash
# Прогон mutmut из корня репозитория.
# Ловушка: mutmut правит src/ и не чистит __pycache__. Если рядом валяются
# старые .pyc, pytest импортирует мутированный модуль даже после отката source —
# и результат прогона становится недостоверным. Поэтому чистим кэш и запрещаем
# запись bytecode на время прогона.
set -euo pipefail

cd "$(dirname "$0")/.."

find src -name __pycache__ -type d -print0 | xargs -0 -r rm -rf
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=./

uv run mutmut run "$@"

find src -name __pycache__ -type d -print0 | xargs -0 -r rm -rf

# flake8 [absolute path to src] --select=WPS
