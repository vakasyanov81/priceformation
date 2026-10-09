#!/bin/bash
# Прогон mutmut из корня репозитория.
#
# Ловушки:
# 1. mutmut правит src/ и не чистит __pycache__. Если рядом валяются старые
#    .pyc, pytest импортирует мутированный модуль даже после отката source — и
#    результат прогона недостоверен. Поэтому чистим __pycache__ и запрещаем
#    запись bytecode на время прогона.
# 2. Кэш mutmut (mutants/) нельзя переиспользовать после точечного прогона:
#    `mutmut run <фильтр>` записывает результаты только для отфильтрованных
#    мутантов, остальные остаются в прежнем снимке. Следующий `mutmut run`
#    видит файлы «unmodified», берёт частичный кэш и занижает знаменатель
#    (в кампании 2026-10-09 так потерялось 384 мутанта: 5267 вместо 5701).
#    Поэтому сносим кэш перед каждым прогоном — холодный полный прогон
#    занимает около минуты.
set -euo pipefail

cd "$(dirname "$0")/.."

MUTANTS_DIR=mutants

find src -name __pycache__ -type d -print0 | xargs -0 -r rm -rf
rm -rf "$MUTANTS_DIR"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=./

uv run mutmut run "$@"

find src -name __pycache__ -type d -print0 | xargs -0 -r rm -rf

# flake8 [absolute path to src] --select=WPS
