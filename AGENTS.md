# priceformation

Формирование прайсов из прайс-листов поставщиков шин. Python `==3.14.*`, пакетный менеджер — `uv` (запрещено вызывать голые бинари, только `uv run ...`).

## Импорты (важно)
Пакет лежит в `src/`, но импортируется как верхний уровень: `from parsers.all_vendors import all_vendors`, `from cfg import init_cfg`. НЕ писать `src.parsers.*` — `src/` добавляется в `sys.path` в `tests/conftest.py` и `integration_tests/conftest.py`.

## Проверки после правок кода
Порядок и команды — из CI `.github/workflows/python-app.yml`; тот же набор в `.pre-commit-config.yaml`. Запускать из корня по всему репозиторию:

1. `uv run pytest` — порог покрытия 95% (`--cov-fail-under=95`), при недостижении тесты «падают».
2. `uv run black --check --diff .`
3. `uv run ruff check .`
4. `uv run flake8 .`
5. `uv run mypy .`
6. `uv run vulture`
7. `uv run bandit -r src -c pyproject.toml`
8. `uv run pip-audit`

Подавление линт/типов (`# noqa`, `# type: ignore`) — только в крайнем случае, с правилами и FIXME-форматом; подробно в `.pi/AGENTS.md`. `pyright` настроен, но в CI не входит.

## Тесты
- Параметры из `pyproject.toml [tool.pytest.ini_options]`: `-n=2` (xdist), branch-покрытие, html/xml отчёты. `pytest-testmon` доступен, но активируется только флагом `--testmon`.
- `src/parsers/registry.py` держит глобальный `_registry` — тесты не должны чистить его без restore (`tests/test_parsers/test_registry.py`).
- Интеграционные тесты (`integration_tests/`) и модульные делят общий `parse_config/`; эталонные конфиги — в `tests/parse_config_example/`. STK без `stk_markup_rules.json` в `parse_config/` при разборе падает с ошибкой чтения.

## Данные (не код)
- `parse_config/` — пользовательские настройки: `vendor_list.json`, `<supplier>_markup_rules.json`, `black_list`, `manufacturer_aliases.json`, `title_aliases.json`, `correct-nomenclature.xlsx`.
- `file_prices/<sup_code>/` — входные прайсы поставщиков; результат — `file_prices/result/`. `--json`-режим CLI пишет `.jsonl` рядом с `result_meta.json`.
- `.env` — `ZAPASKA_API_LOGIN` / `ZAPASKA_API_PASSWORD` для выгрузки данных запаски.

## Архитектура
- Вендоры регистрируются декоратором `@register_vendor(code, markup_policy=...)`; код реестра — `src/parsers/registry.py`. Список вендоров для импорта — один, `_VENDORS_TO_IMPORT` в registry; `all_vendors.py` — чистая делегация.
- Политики наценки — `src/parsers/base_parser/markup_policy.py`. Цепочка: `CommonPrice.parse_all_vendors()` → `CommonPriceGrouper` → шаблоны writer (`for_inner` / `for_drom` / `for_full`).
- Стиль: чёрные, line-length 120, кавычки одинарные (`skip-string-normalization`). Комментарии и docstring — на русском. `tasks/PLAN.md` — план рефакторинга (registry, DI, services, pydantic).