# Task-23: Архитектурный долг слоёв (`parsers`, оболочка, `ConfigProvider`)

Итог ревью архитектуры (2026-10-28). Контракты `lint-imports` выполняются (6 kept), но структура держится на соглашениях, а не на границах пакетов. Каждый этап — отдельный коммит (одна причина — один фикс), этапы должны быть независимо проверяемыми.

## Проблема

1. **IO-клиенты лежат в `parsers`, а не в `infrastructure`.** `parsers/mail/` (`client.py` на imaplib, `doh.py`, `download.py` на urllib) и `parsers/remote/*_client.py` (HTTP; `four_tochki_client.py` — 352 строки) — адаптеры внешних систем. Из-за них в `parsers` 164 файла из 240 в `src/`.
2. **Плоский корень `src/parsers/`.** Около 40 модулей, связанных только префиксами имён: `common_price_*` (14), `nomenclature_*`, `price_schema_*`, `supplier_price_*`.
3. **Оболочка приложения в корне `src/`.** `run.py`, `run_argv.py`, `run_machine.py`, `parse_report*.py`, `run_dialog/` — не пакет. Контракт «слои не зависят от оболочки» (c6d22ea) держится на ручном списке `forbidden_modules` и глобальном `include_external_packages = true`; новый `run_*.py` в контракт не попадёт.
4. **`ConfigProvider` скрыто достаётся через сервис-локатор.** `get_config_provider()` — 26 вхождений в 24 файлах (включая определение в `domain/config_context.py`): `parsers` — 18 файлов, `infrastructure` — 2 (`config/dotenv.py`, `config/result_folder.py`), `services` — 3 (`mail_service.py`, `help_service.py`, `price_schema_service.py` ×2). Зависимость скрыта в теле функции, тестам нужны `fake_config_provider` и `_config_provider_restored`.
5. **`ServiceProvider` слабо типизирован.** Это отдельная проблема от `ConfigProvider`: глобальные `_factories` / `_instances` и обращения к контейнеру остаются осознанным архитектурным долгом, но `register` / `resolve` / `create` возвращают или принимают `Any`, из-за чего в вызывающем коде нужны `cast`.
6. **Широкие `except Exception` без traceback в месте обработки.** `services/parse_orchestrator.py:102` логирует и пробрасывает ошибку, а `run_machine.py:136` превращает её в JSON и код 1. Тихого пропуска нет; нужно сохранить эти контракты и обеспечить traceback в файловом логе без двойного логирования.

## Решение

1. **Пакет `app/`.** Собрать оболочку в `src/app/` (`run`, `run_argv`, `run_machine`, `parse_report*`, `run_dialog`), поправить `[project.scripts]` (`run:main` → `app.run:main`; `run.sh`/`run.bat` вызывают `uv run --no-dev --locked pf`, путей к `run.py` в них нет — не трогать). В `[tool.importlinter]` заменить `run_dialog` в `root_packages` на `app`, добавить `app` верхним слоем, заменить ручной список `forbidden_modules` на `app` и убрать `include_external_packages`.
2. **Разделить прикладную логику и IO-адаптеры, а не механически переносить клиенты целиком.** В `infrastructure/mail/` и `infrastructure/remote/` переносятся транспорт, сетевой разбор ответа и файловый IO; порты — в `domain/protocols.py` или в отдельных доменных модулях портов. В `infrastructure` не должно быть импортов из `parsers`.
   - Для mail сначала разделить `client.py`: поиск/фильтрация писем и прикладные модели остаются в `parsers/mail`, IMAP-соединение, получение данных и скачивание уходят за порты в `infrastructure/mail`. `dates`, `links`, `message`, `models` нельзя оставлять в списке зависимостей инфраструктурного адаптера.
   - Для four_tochki выбор складов и чтение их конфигурации остаются в `parsers/remote`; транспорт получает уже выбранные склады и параметры API аргументами. `four_tochki_warehouse_selection` и `four_tochki_warehouses` нельзя импортировать из `infrastructure`. Типы на границе порта должны принадлежать домену либо инфраструктуре (`parsers → infrastructure` разрешено, обратная зависимость — нет).
   - Для zapaska и mim действует то же правило: вместе с HTTP-клиентом переносятся только те помощники и модели, которые не тянут зависимости из `parsers`.
3. **Подпакеты `parsers`.** Выделить `common_price/`, `nomenclature/`, `price_schema/`, `supplier_price/`; импорты и строковые пути в `patch(...)` править механически, вывод не меняется.
4. **`ConfigProvider` через конструктор в `parsers`.** Пилот на `parsers/data_provider/black_list.py`: `ConfigProvider` приходит аргументом конструктора. Цепочка: `BlackListProviderFromUserConfig()` создаётся дефолтом в `make_parse_config` (`base_parser/base_parser_config.py:119`) ← `registry.py:109` `make_vendor_entry` ← `all_vendors_including_disabled` / `vendor_entry_for` ← `parsers/all_vendors.py` и `services/parse_orchestrator.py:75`. Провайдер передаётся через сигнатуры реестра из точек композиции, без обратного импорта `services → cfg`. После пилота так же по одному перевести остальные вызовы в `parsers`.
5. **Только типизация `ServiceProvider`.** Типизировать `register`, `resolve` и `create` generic по интерфейсу, убрать ставшие ненужными `cast`. Не перемещать `resolve` между функциями ради имитации DI: полная замена глобального контейнера конструкторным внедрением — отдельная задача.
6. **`except Exception` на границах сохранить.** В оркестраторе ошибка по-прежнему пробрасывается; в JSON-режиме любая ошибка по-прежнему даёт тот же JSON error payload и код 1. Добавить `logger.exception(...)` там, где traceback не попадает в файловый лог, и тесты на traceback, повторный выброс / JSON-ответ. Не сужать граничный `except Exception` в `run_machine`, если это приведёт к потере JSON-ответа; не создавать двойной traceback на пути оркестратор → оболочка.

Вне задачи: вызовы `get_config_provider()` в `services` и `infrastructure`, удаление `domain/config_context.py`, полный отказ от глобального `ServiceProvider`, удаление `get_instance` у ридеров и вынос правил `strategies/product_type.py` в конфиг. Для них нужны отдельные задачи после оценки пилота.

## Переносы путей и документация

Для этапов `app/`, mail и remote обновить все путь-зависимые места, а не только импорты:

- `setup.cfg [flake8] per-file-ignores`: `run.py`, `run_machine.py`, `run_dialog/line_fallback.py`, `parse_report.py`, `parsers/mail/client.py`, `parsers/remote/*_client.py`;
- `pyproject.toml [tool.ruff.lint.per-file-ignores]`: `src/parse_report.py` и другие правила, если их файлы перемещаются;
- обычные импорты и строковые пути в `patch(...)` / `monkeypatch` в `tests/`, `integration_tests/`, `load_tests/`;
- docstring с командами `python src/run.py ...` в переносимой оболочке — заменить на поддерживаемый запуск через `uv run pf ...`;
- `AGENTS.md`: точка входа, состав оболочки и правила слоёв.

`tests/test_architecture_markers.py` дополняется маркером: в корне `src/` нет `run*.py` / `parse_report*.py`, оболочка живёт в `app/`.

## Проверка неизменности поведения

`integration_tests/test_parity_vendor_config.py` — только один из тестов, а не доказательство parity всего вывода. До переносов зафиксировать на одинаковых интеграционных фикстурах разобранные строки после группировки и содержимое результатов writer-шаблонов; после каждого переноса сравнить с эталоном. XLSX сравнивать по содержимому листов, а не по байтам файла. Дополнительно прогнать существующие интеграционные тесты реальных прайсов и writer-шаблонов.

После смены `[project.scripts]` проверить реальную установленную точку входа: `uv run pf get_product_types --json` завершается с кодом 0 и выдаёт валидный JSON. Прямой вызов `main()` в `integration_tests/test_run_entry.py` этой проверки не заменяет.

Подавления (`noqa`, `ignore_imports`) не добавляются.

## План

1. Пакет `app/`: перенос, контракты, путь-зависимые настройки, документация и smoke-тест `pf`.
2. Mail-адаптер: сначала разделение ответственности и портов, затем перенос IO.
3. Remote-адаптеры: four_tochki, zapaska, mim отдельными коммитами; после каждого проверять отсутствие `infrastructure → parsers`.
4. Подпакеты `parsers`: каждое семейство отдельным коммитом.
5. Обработка ошибок и тесты на traceback с сохранением JSON-контракта.
6. Пилот `ConfigProvider` на `black_list`, затем остальные вызовы в `parsers` отдельными коммитами.
7. Generic-типизация `ServiceProvider` без изменения его жизненного цикла и мест разрешения зависимостей.

Перед правкой контракта `app` — негативная проверка: временно добавить запрещённый импорт и убедиться, что контракт его ловит. После каждого этапа — полный набор проверок из AGENTS.md; коммит только после подтверждения.

## Текущее состояние (2026-10-29)

- **Пакет `app/` — выполнен.** Оболочка и `run_dialog` перенесены в `src/app/`; точки входа, import-linter, настройки линтеров, тестовые пути и `AGENTS.md` обновлены. Негативная проверка подтвердила, что контракт ловит запрещённый импорт `app` из нижнего слоя. `uv run pf get_product_types --json` возвращает код 0 и валидный JSON.
- **Mail-адаптер — выполнен.** IMAP, DoH, скачивание и запись вложений находятся в `src/infrastructure/mail/`; поиск и фильтрация писем, прикладные модели остались в `src/parsers/mail/`. Протокол IMAP и почтовые ошибки вынесены в `src/domain/mail.py`; `infrastructure/mail` не импортирует `parsers`.
- **Поведение сохранено после `app` и mail.** Эталон содержит 15 разобранных строк и содержимое четырёх XLSX; канонический JSON имеет SHA-256 `aa592887c36adffcf870788ef6ba6cef001c56c77316fe810a01daad286fb020`. Повторное сравнение: `PARITY OK rows=15 workbooks=4`.
- **Проверки после mail пройдены:** полный `just ci`, включая 3251 тест и покрытие 99,54%; все девять обязательных команд из `AGENTS.md` завершились с кодом 0.
- **Remote-адаптеры — выполнены.** `four_tochki_client`, `zapaska_client`, `mim_client` лежат в `src/infrastructure/remote/` и не импортируют `parsers`. Датаклассы складов Форточек вынесены в `src/domain/four_tochki.py`; выбор складов и чтение их конфига остались в `parsers/remote`; оркестрация «подобрать → залогировать → скачать» — в `services/four_tochki_service.py`. Корень проблемы, из-за которой контракт не ловил `infrastructure → parsers`: у `infrastructure/remote` и `parsers/remote` не было `__init__.py` (namespace-пакеты не попадают в граф grimp) — добавлены; негативная проверка подтвердила, что контракт теперь ловит запрещённый импорт.
- **Проверки после remote пройдены:** все девять команд из `AGENTS.md` с кодом 0, 3251 тест, покрытие 99,54%. Сравнение с эталоном (`PARITY OK`) после этого этапа не перезапускалось.
- **Подпакеты `parsers` — выполнены** (коммиты d08f371, d4e62f1, d4ae12f, 5521646): `common_price/`, `nomenclature/`, `price_schema/` (`price_schema.py` → `schema.py`), `supplier_price/`. В корне остались `load_supplier_prices.py` и `supplier_file_rules.py` — вне префиксных семейств.
- **Traceback — выполнен** (af088f9). `log_exception_once` (`infrastructure/logging/exception_logging.py`) пишет ERROR с traceback один раз на исключение (флаг в `exc.__dict__`: встроенные исключения не weakref-able); `ConsoleFormatter` форматирует копию записи без `exc_info`/`exc_text` (кэш `exc_text` общий для handler'ов). Оркестратор (через `services/parse_logging.log_parse_failure`) и граница `run_machine` вызывают его; JSON-ответ и код 1 не менялись.
- **`ConfigProvider` в `parsers` — выполнен частично** (коммиты 69e9ba9 … 62dba12). Переведены на явную передачу:
  - `black_list`, `markup_rules` — конструктор провайдера данных; цепочка `make_parse_config(config_provider=)` ← `registry` ← `all_vendors(config_provider)` ← `services/vendor_source.py` (`VendorSource`, провайдер берётся лениво в момент вызова). Неиспользуемые переопределения `markup_rules_provider` / `manufacturer_aliases` в `make_parse_config` удалены.
  - `ParseConfiguration.config_provider` (поле `BasePriceParseConfigurationParams`): `price_source` (`FilePricesSource`), `warehouse_filter` (`CityWarehouseFilter`); `FileReader` требует `price_source`, выбор ридера по конфигу — `file_reader.data_reader_for`.
  - `CommonPriceOut(config_provider=)` — `result_folder`, `doubles_settings`, `nomenclature_correction`.
  - `load_config`, `load_supplier_prices` / `place_files`, `load_mail_config`, `load_four_tochki_warehouse_groups` — аргумент `config_provider`; `MailService(config_provider=None)`; точки композиции — `app/run_machine.py` и `services`.
  На каждый перевод есть тест на корень: отдельный `MagicMock`-провайдер вместо глобального.
- **Осталось в `parsers` (4 файла с `get_config_provider()`):**
  - `vendor_config/provider.py` (`load_vendor_configs`, `load_common_settings`; `lru_cache` по папке) и `vendor_config/activation.py`. Около 15 вызывающих мест, часть в `services` (`vendor_activity`, `vendor_activation`, `mim_service`, `price_schema_service`) и `supplier_file_rules`, `reference_priority`, `all_vendors`, `registry`. Нужно решить, как провайдер попадает в эти вызовы и кто владеет кэшем.
  - `data_provider/manufacturer_aliases.py`: `load_aliases_map()` — процессный `lru_cache`, читают `title_wrap`, `title_registry`, `group_key`, `grouper`; `ManufacturerAliasesProviderFromUserConfig` строится в `make_parse_config`.
  - `data_provider/title_aliases.py`: `load_title_aliases(supplier_name)` вызывается из `title_registry`.
- **Не начато:** этап 7 — generic-типизация `ServiceProvider` (`register` / `resolve` / `create`, удаление `cast`).
- **Проверки:** после каждого коммита все девять команд из `AGENTS.md` с кодом 0. Сравнение с эталоном (parity) после этапов 3–6 не перезапускалось — скрипта в репозитории нет.

## Критерии готовности

- [x] В `src/` нет оболочки россыпью: `run*`, `parse_report*`, `run_dialog` лежат в `app/`; в `importlinter` нет `include_external_packages` и ручного списка модулей оболочки.
- [x] `setup.cfg`, `pyproject.toml`, импорты, строковые пути тестов, docstring оболочки и `AGENTS.md` обновлены под новые пути.
- [x] Реальная команда `uv run pf get_product_types --json` возвращает код 0 и валидный JSON.
- [x] В `parsers/` нет IMAP / HTTP / download-адаптеров; порты и типы границ не создают зависимостей `infrastructure → parsers` или `domain → верхние слои`.
- [x] В корне `parsers/` нет россыпи `common_price_*` / `nomenclature_*` / `price_schema_*` / `supplier_price_*`.
- [ ] `get_config_provider()` не вызывается в `parsers`; вызовы в `services` и `infrastructure` явно оставлены за рамками этой задачи.
- [ ] `ServiceProvider.register` / `resolve` / `create` типизированы generic по интерфейсу; связанные `cast` удалены. Полный отказ от контейнера не объявляется выполненным.
- [x] Ошибка парсера по-прежнему пробрасывается, JSON-ошибка и код 1 сохранены; traceback покрыт тестами и не дублируется.
- [ ] Разобранные строки и содержимое writer-результатов на фикстурах совпадают с эталоном до переносов.
- [ ] Проверки по AGENTS.md проходят по всему репозиторию (exit 0).
