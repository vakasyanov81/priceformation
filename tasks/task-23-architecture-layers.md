# Task-23: Архитектурный долг слоёв (`parsers`, оболочка, DI)

Итог ревью архитектуры (2026-10-28). Контракты `lint-imports` выполняются (6 kept), но структура держится на соглашениях, а не на границах пакетов. Каждый пункт — отдельный коммит (одна причина — один фикс).

## Проблема

1. **IO-клиенты лежат в `parsers`, а не в `infrastructure`.** `parsers/mail/` (`client.py` на imaplib, `doh.py`, `download.py` на urllib) и `parsers/remote/*_client.py` (HTTP; `four_tochki_client.py` — 352 строки) — адаптеры внешних систем. Из-за них в `parsers` 164 файла из 240 в `src/`.
2. **Плоский корень `src/parsers/`.** Около 40 модулей, связанных только префиксами имён: `common_price_*` (14), `nomenclature_*`, `price_schema_*`, `supplier_price_*`.
3. **Оболочка приложения в корне `src/`.** `run.py`, `run_argv.py`, `run_machine.py`, `parse_report*.py`, `run_dialog/` — не пакет. Контракт «слои не зависят от оболочки» (c6d22ea) держится на ручном списке `forbidden_modules` и глобальном `include_external_packages = true`; новый `run_*.py` в контракт не попадёт.
4. **Сервис-локатор вместо внедрения зависимостей.**
   - `get_config_provider()` — 26 вхождений в 24 файлах (включая определение в `domain/config_context.py`): `parsers` — 18 файлов, `infrastructure` — 2 (`config/dotenv.py`, `config/result_folder.py`), `services` — 3 (`mail_service.py`, `help_service.py`, `price_schema_service.py` ×2). Зависимость скрыта в теле функции, тестам нужны `fake_config_provider` и `_config_provider_restored`.
   - `ServiceProvider` — глобальное состояние уровня модуля; `run_machine.py` вызывает `resolve(...)` в обработчиках; `resolve` возвращает `Any`.
5. **Широкие `except Exception`** в `services/parse_orchestrator.py:102` и `run_machine.py:136`: проверить, что ошибка логируется с traceback и не превращается в тихий пропуск.
6. **Мелочи.** `get_instance` у ридеров — фабричная обёртка над конструктором; объявлена в самом протоколе `IXlsReader` (`base_parser/protocols.py:17`) и вызывается из `base_parser/file_reader.py:26`, так что убрать её значит поменять протокол и точку вызова. Правила `strategies/product_type.py` (451 строка) зашиты в код, а не в конфиг.

## Решение

1. **Клиенты → `infrastructure`.** Перенести `parsers/mail/*` (IO-часть) и `parsers/remote/*_client.py` в `infrastructure/mail/` и `infrastructure/remote/`; порты — в `domain/protocols.py` (часть уже есть: `mail/protocols.py`). Зависимость разворачивать передачей объекта аргументом, не `ignore_imports`.
2. **Подпакеты `parsers`.** Выделить `common_price/`, `nomenclature/`, `price_schema/`, `supplier_price/`; импорты править механически, вывод не меняется.
3. **Пакет `app/`.** Собрать оболочку в `src/app/` (`run`, `run_argv`, `run_machine`, `parse_report*`, `run_dialog`), поправить `[project.scripts]` (`run:main` → `app.run:main`; `run.sh`/`run.bat` вызывают `uv run --no-dev --locked pf`, путей к `run.py` в них нет — не трогать). Обновить импорты оболочки в тестах (~15 файлов: `tests/test_run_dialog/*`, `tests/test_cli/*`, `tests/test_run.py`, `tests/test_run_mail.py`, `tests/test_run_help.py`, `integration_tests/test_run_entry.py`, `load_tests/_make_price_once.py`) и `AGENTS.md` («Точка входа — `src/run.py`», список оболочки в разделе «Архитектура», запуск). В `[tool.importlinter]` заменить список `forbidden_modules` на `app`, добавить `app` верхним слоем и убрать `include_external_packages`.
4. **DI вместо локатора.** Пилот на `parsers/data_provider/black_list.py`: `ConfigProvider` приходит аргументом конструктора. Цепочка непростая: `BlackListProviderFromUserConfig()` создаётся дефолтом в `make_parse_config` (`base_parser/base_parser_config.py:119`) ← `registry.py:109` `make_vendor_entry` ← `all_vendors_including_disabled` / `vendor_entry_for` ← `parsers/all_vendors.py` и `services/parse_orchestrator.py:75`. Значит провайдер протаскивается через 4–5 сигнатур реестра, а резолвят его точки входа (`cfg` / `services`). Сначала описать эту цепочку в подзадаче и провести пилот, затем остальные парсерные провайдеры по одному. Отдельными шагами: `services` (3 файла) получают `ConfigProvider` из `cfg`; `infrastructure/config/dotenv.py` и `result_folder.py` — решить, принимают ли они провайдер аргументом или остаются единственным допустимым местом чтения (зафиксировать в критерии). `ServiceProvider.resolve` типизировать (generic по интерфейсу), в `run_machine` резолвить на входе, а не в обработчиках.
5. **`except Exception`.** Проверить два места; при проглатывании — сузить тип или логировать с traceback (без `noqa`).
6. **Мелочи.** Убрать `get_instance`, если он лишний; решение по `product_type.py` — отдельным обсуждением, не в этой задаче.

Ограничения: вывод парсеров не меняется (`integration_tests/test_parity_vendor_config.py`); подавления (`noqa`, `ignore_imports`) не добавляются; `tests/test_architecture_markers.py` дополняется маркером: в корне `src/` нет `run*.py` / `parse_report*.py`, оболочка живёт в `app/` (сейчас хардкода путей оболочки в файле нет).

## План

1. Пункт 3 (`app/`): механический перенос, контракт проверяет сам себя.
2. Пункт 1 (клиенты → `infrastructure`).
3. Пункт 2 (подпакеты `parsers`).
4. Пункт 5 (быстрая проверка `except`).
5. Пункт 4: пилот на `black_list`, затем остальные провайдеры; отдельные коммиты.
6. Пункт 6.

Перед правкой пункта 3 — негативная проверка: временно добавить запрещённый импорт и убедиться, что контракт его ловит. После каждого шага — полный набор проверок из AGENTS.md; коммит только после подтверждения.

## Критерии готовности

- [ ] В `src/` нет оболочки россыпью: `run*`, `parse_report*`, `run_dialog` лежат в `app/`; в `importlinter` нет `include_external_packages` и ручного списка модулей.
- [ ] В `parsers/` нет модулей с imaplib / urllib / HTTP-клиентами; порты в `domain/protocols.py`.
- [ ] В корне `parsers/` нет россыпи `common_price_*` / `nomenclature_*` / `price_schema_*` / `supplier_price_*`.
- [ ] `get_config_provider()` не вызывается в `parsers` (этап 1); `services` и `infrastructure` — отдельными шагами с явным решением, какие вызовы остаются допустимыми (`cfg`, точки входа).
- [ ] `AGENTS.md` и импорты тестов обновлены под `app/`.
- [ ] Оба `except Exception` проверены (логирование с traceback либо сужение типа).
- [ ] Вывод парсеров не изменился.
- [ ] Проверки по AGENTS.md проходят по всему репозиторию (exit 0).
