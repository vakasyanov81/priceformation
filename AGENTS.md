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
6. `uv run lint-imports` — контракты слоёв из `pyproject.toml [tool.importlinter]`.
7. `uv run vulture`
8. `uv run bandit -r src -c pyproject.toml`
9. `uv run pip-audit`

Подавление линт/типов (`# noqa`, `# type: ignore`) — только в крайнем случае, с правилами и FIXME-форматом; подробно в `.pi/AGENTS.md`. `pyright` настроен, но в CI не входит.

## Тесты
- Параметры из `pyproject.toml [tool.pytest.ini_options]`: `-n=2` (xdist), branch-покрытие, html/xml отчёты. `pytest-testmon` доступен, но активируется только флагом `--testmon`.
- `src/parsers/registry.py` держит глобальный `_registry` — тесты не должны чистить его без restore (`tests/test_parsers/test_registry.py`).
- Пути окружения в тестах подменяются фикстурой `fake_config_provider` (временная папка), а автофикстура `_config_provider_restored` возвращает боевой провайдер после теста.
- Интеграционные тесты (`integration_tests/`) и модульные делят общий `parse_config/`; эталонные конфиги — в `tests/parse_config_example/`. STK без `stk_markup_rules.json` в `parse_config/` при разборе падает с ошибкой чтения.

## Данные (не код)
- `parse_config/` — пользовательские настройки: `vendor_list.json`, `<supplier>_markup_rules.json`, `black_list`, `manufacturer_aliases.json`, `title_aliases.json`, `correct-nomenclature.xlsx`.
- `file_prices/<sup_code>/` — входные прайсы поставщиков; результат — `file_prices/result/`. `--json`-режим CLI пишет `.jsonl` рядом с `result_meta.json`.
- `.env` — `ZAPASKA_API_LOGIN` / `ZAPASKA_API_PASSWORD` для выгрузки данных запаски.

## Архитектура
- Слои: `src/domain/` (чистое: порты, исключения, конфиг-контекст — без IO), `src/infrastructure/` (адаптеры: `config/`, `data/`, `logging/`), `src/parsers/`, `src/services/`, `src/cfg/` (композиционный корень). Пакета `src/core/` больше нет; правила слоёв проверяет `uv run lint-imports` (контракты в `pyproject.toml [tool.importlinter]`: `cfg`/`services` → `parsers` → `infrastructure` → `domain`, только вниз), не-импортные маркеры — `tests/test_architecture_markers.py`.
- Логи и чтение файлов лежат в инфраструктуре: `infrastructure/logging/log_setup.py` (`setup_logging` — корневой логгер, консольный handler, файлы логов; JSON-режим глушит консоль фильтром), `infrastructure/data/file_reader.py`, `infrastructure/config/result_folder.py`. Логирование — только `logger = logging.getLogger(__name__)` в каждом модуле; глобальных `log_msg`/`err_msg`/`warn_msg`/`print_log` больше нет (проверяет `tests/test_architecture_markers.py`).
- Пакет логирования разложен по ролям: `log_setup.py` (настройка корневого логгера), `console.py` (`ConsoleHandler` + форматтер + фильтры JSON/file-only, `FILE_ONLY`), `file_logging.py` (файлы логов), `json_mode.py` (`set_json_mode`/`quiet_console`), `exception_logging.py` (traceback только в файл). Тесты логов собирают записи фикстурой `watch_logger` (`tests/log_watch.py`): пары (уровень, текст) из `caplog`.
- Исключения домена (`CoreExceptionError`, `SupplierNotHavePricesError`, `make_raise`) — `src/domain/exceptions.py`; они не пишут логи сами, а отдают сообщение приёмнику (`domain/exception_log.py`), который назначает `init_cfg()` — реализация в `infrastructure/logging/exception_logging.py`.
- Пути окружения (настройки, прайсы, результаты, логи) даёт порт `ConfigProvider` — `src/domain/protocols.py`; реализация по умолчанию `FileConfigProvider` (`src/infrastructure/config/`), тест-дуб `FakeConfigProvider` там же. Активный провайдер ставит `init_cfg()` в `src/cfg/__init__.py`; читать — `get_config_provider()` из `src/domain/config_context.py`. `MainConfig` больше нет.
- Вендоры регистрируются декоратором `@register_vendor(code, markup_policy=...)`; код реестра — `src/parsers/registry.py`. Список вендоров для импорта — один, `_VENDORS_TO_IMPORT` в registry; `all_vendors.py` — чистая делегация. Признак «вендор уже зарегистрирован» — модуль в `sys.modules`, а не заполненность `_registry`, поэтому частичный импорт вендоров (например, в тестах) не мешает `all_vendors_from_registry()` доимпортировать остальных.
- Политики наценки — `src/parsers/base_parser/markup_policy.py`. Цепочка: `CommonPrice.parse_all_vendors()` → `CommonPriceGrouper` → шаблоны writer (`for_inner` / `for_drom` / `for_full`).
- Пользовательские JSON-конфиги разбираются в frozen-dataclass модели — `src/parsers/data_provider/models.py` (`MarkupRulesConfig`, `MarkUpRule`, `AbsoluteMarkUpRules`, `VendorConfigEntry`), примитивы чтения полей — `json_fields.py` в том же пакете. Провайдеры возвращают модели, а не `dict`; ошибка в конфиге — `ConfigValidationError` (`src/domain/exceptions.py`) с именем файла и путём до ключа.
- Стиль: чёрные, line-length 120, кавычки одинарные (`skip-string-normalization`). Комментарии и docstring — на русском. `tasks/PLAN.md` — план рефакторинга (registry, DI, services, типизированные конфиги).