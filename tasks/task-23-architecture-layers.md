# Task-23: Архитектурный долг слоёв (`parsers`, оболочка, DI)

Итог ревью архитектуры (2026-10-28). Контракты `lint-imports` выполняются (6 kept), но структура держится на соглашениях, а не на границах пакетов. Каждый пункт — отдельный коммит (одна причина — один фикс).

## Проблема

1. **IO-клиенты лежат в `parsers`, а не в `infrastructure`.** `parsers/mail/` (`client.py` на imaplib, `doh.py`, `download.py` на urllib) и `parsers/remote/*_client.py` (HTTP; `four_tochki_client.py` — 352 строки) — адаптеры внешних систем. Из-за них в `parsers` 164 файла из 218.
2. **Плоский корень `src/parsers/`.** Около 40 модулей, связанных только префиксами имён: `common_price_*` (14), `nomenclature_*`, `price_schema_*`, `supplier_price_*`.
3. **Оболочка приложения в корне `src/`.** `run.py`, `run_argv.py`, `run_machine.py`, `parse_report*.py`, `run_dialog/` — не пакет. Контракт «слои не зависят от оболочки» (c6d22ea) держится на ручном списке `forbidden_modules` и глобальном `include_external_packages = true`; новый `run_*.py` в контракт не попадёт.
4. **Сервис-локатор вместо внедрения зависимостей.**
   - `get_config_provider()` вызывается в ~18 модулях `parsers` / `infrastructure` и в `services`: зависимость скрыта в теле функции, тестам нужны `fake_config_provider` и `_config_provider_restored`.
   - `ServiceProvider` — глобальное состояние уровня модуля; `run_machine.py` вызывает `resolve(...)` в обработчиках; `resolve` возвращает `Any`.
5. **Широкие `except Exception`** в `services/parse_orchestrator.py:102` и `run_machine.py:136`: проверить, что ошибка логируется с traceback и не превращается в тихий пропуск.
6. **Мелочи.** `get_instance` у ридеров — обёртка над конструктором, протоколу `IXlsReader` она не нужна. Правила `strategies/product_type.py` (451 строка) зашиты в код, а не в конфиг.

## Решение

1. **Клиенты → `infrastructure`.** Перенести `parsers/mail/*` (IO-часть) и `parsers/remote/*_client.py` в `infrastructure/mail/` и `infrastructure/remote/`; порты — в `domain/protocols.py` (часть уже есть: `mail/protocols.py`). Зависимость разворачивать передачей объекта аргументом, не `ignore_imports`.
2. **Подпакеты `parsers`.** Выделить `common_price/`, `nomenclature/`, `price_schema/`, `supplier_price/`; импорты править механически, вывод не меняется.
3. **Пакет `app/`.** Собрать оболочку в `src/app/` (`run`, `run_argv`, `run_machine`, `parse_report*`, `run_dialog`), поправить `[project.scripts]`, `run.sh`/`run.bat`. В `[tool.importlinter]` заменить список `forbidden_modules` на `app`, добавить `app` верхним слоем и убрать `include_external_packages`.
4. **DI вместо локатора.** Пилот на одном провайдере (`parsers/data_provider/black_list.py`): `ConfigProvider` приходит аргументом конструктора, `get_config_provider()` остаётся только в `cfg`. Если пилот чистый — перенести остальные по одному. `ServiceProvider.resolve` типизировать (generic по интерфейсу), в `run_machine` резолвить на входе, а не в обработчиках.
5. **`except Exception`.** Проверить два места; при проглатывании — сузить тип или логировать с traceback (без `noqa`).
6. **Мелочи.** Убрать `get_instance`, если он лишний; решение по `product_type.py` — отдельным обсуждением, не в этой задаче.

Ограничения: вывод парсеров не меняется (`integration_tests/test_parity_vendor_config.py`); подавления (`noqa`, `ignore_imports`) не добавляются; `tests/test_architecture_markers.py` обновляется вместе с переносами.

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
- [ ] `get_config_provider()` не вызывается в `parsers` и `infrastructure` (допустимо только в `cfg` и точках входа).
- [ ] Оба `except Exception` проверены (логирование с traceback либо сужение типа).
- [ ] Вывод парсеров не изменился.
- [ ] Проверки по AGENTS.md проходят по всему репозиторию (exit 0).
