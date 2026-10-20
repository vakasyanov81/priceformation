# Task-18: Убрать `# flake8: noqa` из `services/parse_orchestrator.py`

## Проблема

В `src/services/parse_orchestrator.py` стоит файловая директива `# flake8: noqa: WPS201`:

- Лимит `max-imports = 18` (`setup.cfg`): в модуле 24 импорта (включая `from __future__`) → `WPS201`.
- Лимит `max-module-members = 7`: 8 членов модуля → `WPS202`.
- Директива скрывает **оба** нарушения и всё остальное WPS в файле, хотя названа одним кодом. Без неё `flake8` на файле падает ровно на этих двух.

Корень: в одном модуле смешаны три роли — оркестрация разбора, сводка логов по пропускам и сборка вендорного парсера из конфига. Импорты логов и фабрики тянут модуль вверх по числу импортов, отдельные функции — по числу членов.

## Решение

### 1. Вынести сводку логов в `services/parse_logging.py`

Переезжают `_log_skips`, `_log_homoglyphs`, `_log_titles_not_composed`. С ними уходят импорты `category_finder`, `black_list`, `product_types`, `title_conflicts`, `title_compose` (минус 5).

### 2. Вынести сборку парсера в `services/vendor_parser.py`

Переезжает `_parser_for_vendor`. С ним уходят `config_driven_parser`, `VendorConfig`, `VendorSection` (минус 3). `vendor_config_is_enabled` импортируется из `parsers.registry` в новом модуле.

### 3. Вынести `ParseResult` в `services/parse_result.py`

Сейчас его импортируют `src/parse_report_build.py` и `tests/test_cli/test_parse_report.py`. Обновить импорты на новый путь; реэкспорт из оркестратора не делать (он оставил бы импорт).

### 4. Снять директиву

Удалить `# flake8: noqa: WPS201`. Не добавлять `per-file-ignores` в `setup.cfg` и не ставить `# noqa` — это то же подавление в другом месте, для `src/` запрещено.

### Открытое решение: логирование

Вариант A: новый модуль логирует сам. Тогда имя логгера меняется, и тесты с `_ORCHESTRATOR_LOGGER = 'services.parse_orchestrator'` (`tests/test_services/test_parse_orchestrator.py`, `integration_tests/test_unknown_category_skips.py`) переводятся на новое имя.

Вариант B: новый модуль возвращает сообщения (уровень, текст), логирует оркестратор. Имя логгера сохраняется, тесты не меняются, но сигнатуры другие.

Выбрать до начала работ.

## План миграции

1. Выбрать вариант логирования (см. выше).
2. Создать `services/parse_result.py`, перенести `ParseResult`, обновить импорты.
3. Создать `services/parse_logging.py` по выбранному варианту.
4. Создать `services/vendor_parser.py`, перенести `_parser_for_vendor`.
5. Обновить `tests/test_services/test_parse_orchestrator.py` (импорт `_parser_for_vendor`, `_MOD`, логгер) и `integration_tests/test_unknown_category_skips.py`.
6. Проверить `tests/conftest.py` и `integration_tests/conftest.py`: `monkeypatch.setattr('services.parse_orchestrator.clear_log_files', ...)` остаётся валидным, если `clear_log_files` остаётся в оркестраторе.
7. Удалить директиву `# flake8: noqa: WPS201`.
8. Добавить прямые тесты на сводку логов и на `_parser_for_vendor`, если они покрыты только косвенно (порог покрытия 95 %).

## Критерии готовности

- [ ] В `parse_orchestrator.py` нет `# flake8: noqa` и `# noqa`.
- [ ] `uv run flake8 src/services/` проходит без директивы (импорты ≤ 18, члены модуля ≤ 7).
- [ ] `ParseResult` импортируется из `services.parse_result` во всех местах.
- [ ] Имена логгеров в тестах соответствуют выбранному варианту.
- [ ] Новые модули покрыты тестами, порог 95 % держится.
- [ ] Проверки по AGENTS.md проходят по всему репозиторию (exit 0): `uv run pytest`, `uv run black --check --diff .`, `uv run ruff check .`, `uv run flake8 .`, `uv run mypy .`, `uv run lint-imports`, `uv run vulture`, `uv run bandit -r src -c pyproject.toml`, `uv run pip-audit`.
- [ ] Коммит — только после подтверждения пользователя.
