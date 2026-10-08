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

### Быстрые команды (`justfile`)
Рецепты повторяют команды выше, ничего не переопределяя; `just --list` — список. Аргументы pytest передаются **без** `--` (иначе `--` уходит в pytest как путь).

- `just unit` — юнит-тесты `tests/` без покрытия; `just integration` — `integration_tests/` без покрытия.
- `just pick tests/.../test_writer.py -k exclude` — точечный запуск без покрытия (без аргументов — оба каталога из `testpaths`).
- `just test` — полный прогон с покрытием, как в CI.
- `just lint` (black, ruff, flake8), `just types` (mypy, lint-imports), `just audit` (vulture, bandit, pip-audit), `just check` — все проверки без тестов, `just ci` — проверки + `pytest`.
- `just format` — автоформат (`black`, `ruff check --fix`).
- `just run` — само приложение (`uv run priceformation`); аргументы пробрасываются как в CLI: `just run parse --json`. Без `--no-dev`, чтобы рецепт не выгонял тестовые зависимости из venv.

### Запуск приложения
Точка входа — `src/run.py`, объявлена в `pyproject.toml [project.scripts]` как `priceformation` и короткий алиас `pf`. Поэтому запуск: `uv run pf` (меню) или `uv run pf parse --json`; в justfile — `just run`. Штатные файлы запуска: `src/run.sh`, `src/run.bat` (с `--no-dev --locked`, для запуска без тестовых зависимостей). Пути окружения считаются от `__file__` (`infrastructure/config/file_config_provider.py`), поэтому cwd значения не имеет.

## Тесты
- Параметры из `pyproject.toml [tool.pytest.ini_options]`: `-n=2` (xdist), branch-покрытие, html/xml отчёты. `pytest-testmon` доступен, но активируется только флагом `--testmon`.
- `src/parsers/registry.py` — реестр вендоров из `vendors/*.json` конфигов; кэш сбрасывается `clear_registry()`.
- Пути окружения в тестах подменяются фикстурой `fake_config_provider` (временная папка), а автофикстура `_config_provider_restored` возвращает боевой провайдер после теста.
- Интеграционные тесты (`integration_tests/`) и модульные не читают боевой `parse_config/`: эталонные конфиги — `tests/parse_config_example/` и `integration_tests/parse_config_example/` (копия `vendors/*.json` + глобальные файлы), прайсы — `integration_tests/file_prices_for_test/`. Конфиги поставщиков — `parse_config/vendors/*.json`; STK самодостаточен (отдельного `stk_markup_rules.json` больше нет).

## Данные (не код)
- `parse_config/` — пользовательские настройки: `vendors/*.json`, `black_list`, `manufacturer_aliases.json`, `title_aliases.json`, `correct-nomenclature.xlsx`.
- `file_prices/<sup_code>/` — входные прайсы поставщиков; результат — `file_prices/result/`. `--json`-режим CLI пишет `.jsonl` рядом с `result_meta.json`.
- `.env` — `ZAPASKA_API_LOGIN` / `ZAPASKA_API_PASSWORD` для выгрузки данных запаски.

## Архитектура
- Слои: `src/domain/` (чистое: сущности, value objects, порты, исключения, конфиг-контекст — без IO), `src/infrastructure/` (адаптеры: `config/`, `data/`, `logging/`), `src/parsers/`, `src/services/`, `src/cfg/` (композиционный корень). Пакета `src/core/` больше нет; правила слоёв проверяет `uv run lint-imports` (контракты в `pyproject.toml [tool.importlinter]`: `cfg`/`services` → `parsers` → `infrastructure` → `domain`, только вниз), не-импортные маркеры — `tests/test_architecture_markers.py`.
- Логи и чтение файлов лежат в инфраструктуре: `infrastructure/logging/log_setup.py` (`setup_logging` — корневой логгер, консольный handler, файлы логов; JSON-режим глушит консоль фильтром), `infrastructure/data/file_reader.py`, `infrastructure/config/result_folder.py`. Логирование — только `logger = logging.getLogger(__name__)` в каждом модуле; глобальных `log_msg`/`err_msg`/`warn_msg`/`print_log` больше нет (проверяет `tests/test_architecture_markers.py`).
- Пакет логирования разложен по ролям: `log_setup.py` (настройка корневого логгера), `console.py` (`ConsoleHandler` + форматтер + фильтры JSON/file-only, `FILE_ONLY`), `file_logging.py` (файлы логов), `json_mode.py` (`set_json_mode`/`quiet_console`), `exception_logging.py` (traceback только в файл). Тесты логов собирают записи фикстурой `watch_logger` (`tests/log_watch.py`): пары (уровень, текст) из `caplog`.
- Исключения домена (`CoreExceptionError`, `SupplierNotHavePricesError`, `make_raise`) — `src/domain/exceptions.py`; они не пишут логи сами, а отдают сообщение приёмнику (`domain/exception_log.py`), который назначает `init_cfg()` — реализация в `infrastructure/logging/exception_logging.py`.
- Пути окружения (настройки, прайсы, результаты, логи) даёт порт `ConfigProvider` — `src/domain/protocols.py`; реализация по умолчанию `FileConfigProvider` (`src/infrastructure/config/`), тест-дуб `FakeConfigProvider` там же. Активный провайдер ставит `init_cfg()` в `src/cfg/__init__.py`; читать — `get_config_provider()` из `src/domain/config_context.py`. `MainConfig` больше нет.
- Вендоры регистрируются из `vendors/*.json` конфигов; реестр — `src/parsers/registry.py`, сборка записей и каталога поставщиков — `all_vendors.py`. Поведение каждого вендора описывается конфигом, стратегиями из `src/parsers/strategies/` и `BaseParser`. Новый поставщик = JSON-конфиг без правки Python.
- Позиция прайса — `src/domain/row_item/`: `row_item.py` (`RowItem`, `RowField`), `value_objects.py` (семь frozen VO), `field_registry.py` (реестр плоских ключей), `row_item_casts.py` / `row_item_strip.py` / `row_item_formatter.py` (приведение типов), `disk_name_extras.py` (разбор хвоста названия диска). Пакет чистый: ни IO, ни знания о вендорах; тесты — `tests/test_domain/test_row_item/`.
- Политики наценки — `src/parsers/base_parser/markup_policy.py`. Цепочка: `CommonPrice.parse_all_vendors()` → `CommonPriceGrouper` → шаблоны writer (`for_inner` / `for_drom` / `for_full`).
- Пользовательские JSON-конфиги разбираются в frozen-dataclass модели: конфиг поставщика — `src/parsers/vendor_config/models.py` (`VendorConfig` / `VendorSection`) со слотами из `slot_configs.py` (`CategoryConfig` / `TitleConfig` / `PricingConfig` / `BehaviorConfig`), правила наценки — `src/parsers/data_provider/models.py` (`MarkupRulesConfig`, `MarkUpRule`, `AbsoluteMarkUpRules`, `VendorConfigEntry`); примитивы чтения полей — `fields.py` / `json_fields.py`. Провайдеры возвращают модели, а не `dict`; ошибка в конфиге — `ConfigValidationError` (`src/domain/exceptions.py`) с именем файла и путём до ключа.
- Стиль: чёрные, line-length 120, кавычки одинарные (`skip-string-normalization`). Комментарии и docstring — на русском. `tasks/PLAN.md` — план рефакторинга (registry, DI, services, типизированные конфиги).

## Как искать причину, а не править следствие (обязательно)

Главное правило: **сначала локализуй корень проблемы, потом меняй код**. Запрещено «затыкать» симптом (подавить исключение, добавить `# noqa`/`# type: ignore`, расширить `try`, ослабить проверку, подогнать тест под текущее поведение), не поняв, почему он возник. Если причина не найдена — это не повод менять следствие; это повод сузить зону поиска.

Порядок действий при любом падении/расхождении:

1. **Прочитать сообщение целиком.** Не только последнюю строку: traceback, тип исключения, имя файла и путь до ключа (`ConfigValidationError`), имя вендора и позицию прайса, если есть. Ошибки конфигов и домена несут контекст — использовать его.
2. **Определить слой по симптому.** Домен/`row_item` — тип, VO, реестр полей; `parsers` — стратегии, `BaseParser`, `markup_policy`, `VendorConfig`; `infrastructure` — чтение файлов, пути, логи; `cfg`/`services` — сборка и DI. Проверить направление зависимостей (`uv run lint-imports`) и маркеры (`tests/test_architecture_markers.py`): если симптом «протёк» не в свой слой — причина, скорее всего, в нарушении контракта слоёв, а не в месте падения.
3. **Воспроизвести минимально.** `just pick tests/.../test_x.py -k <case>` или `just unit`/`just integration`; для приложения — `uv run pf ...`. Не запускать весь CI, пока не локализован кейс: полный прогон маскирует причину шумом.
4. **Сузить до входа.** Проверить, воспроизводится ли на эталонных данных (`tests/parse_config_example/`, `integration_tests/parse_config_example/`, `integration_tests/file_prices_for_test/`) и на конкретном вендоре/позиции. Отделить «данные» от «кода»: если ломается только один JSON-конфиг — причина в конфиге или в модели `VendorConfig`, а не в writer.
5. **Найти первый неверный шаг, а не последний.** Идти по цепочке от входа: чтение (`file_reader`) → конфиг (`VendorConfig`/`MarkupRulesConfig`) → `BaseParser`/стратегии → `RowItem`/VO → `CommonPriceGrouper` → шаблон writer (`for_inner`/`for_drom`/`for_full`) → запись результата. Ошибка должна быть воспроизведена на самом раннем шаге, где данные уже неверны; фикс — там, а не в конце цепочки.
6. **Проверить инварианты, а не подогнать результат.** Для `row_item`: типы полей и VO, strip/format, разбор хвоста диска. Для конфигов: слоты `slot_configs.py`, примитивы `fields.py`/`json_fields.py`, что провайдеры возвращают модели, а не `dict`. Нарушение инварианта — это и есть причина; менять надо инвариант или его проверку, а не вывод.
7. **Один фикс — одна причина.** Не смешивать в одном изменении рефакторинг, подавление линта и правку логики. Если правка тянет за собой ещё симптом — вернуться к шагу 2: вероятно, найден не корень.
8. **Закрепить тестом на причину.** Тест должен падать на исходном коде и проходить после фикса, проверяя именно корень (например, конкретный слот конфига или конкретное VO), а не следствие (например, «файл записался»). Место теста — рядом с причиной: `tests/test_domain/test_row_item/`, тесты парсеров, интеграционный кейс на вендора.
9. **Подавление — только как явное исключение.** `# noqa`/`# type: ignore` допустимы лишь в крайнем случае, с указанием правила и FIXME-форматом по `.pi/AGENTS.md`; они не являются фиксом и не заменяют поиск причины.
10. **Зафиксировать вывод.** В сообщении/комментарии к правке указать: симптом, найденную причину, слой, почему фикс именно там, какой тест это закрепляет. Если причина не найдена — явно написать, что именно проверено и где остановился поиск, вместо «временного» подавления.

Красные флаги (почти всегда означают, что правят следствие):

- расширение `try/except` вокруг падения без изменения причины;
- `# noqa`/`# type: ignore`/`cast` вместо исправления типа или контракта;
- ослабление проверки в тесте/ассерте под текущий вывод;
- правка шаблона writer или формата результата, когда неверны данные на входе;
- изменение `row_item`/VO ради одного вендора вместо конфига или стратегии;
- обход слоёв (`services`/`cfg` → `domain` напрямую, импорт `infrastructure` из домена) ради «быстрого» доступа к IO;
- «временный» хак без FIXME и без теста на причину.

Полезные команды при поиске: `just pick ...` (точечно), `just unit` / `just integration`, `uv run pf ...` (воспроизведение в приложении), `uv run lint-imports` и `uv run pytest tests/test_architecture_markers.py` (контракты слоёв и маркеры), `uv run mypy .` (типы как индикатор неверного контракта, а не как то, что надо подавить).