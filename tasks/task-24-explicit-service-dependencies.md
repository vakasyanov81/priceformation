# Task-24: Явные зависимости сервисов вместо Service Locator

Итог архитектурного ревью (2026-10-30). Контракты слоёв соблюдаются, но внедрение зависимостей реализовано непоследовательно: сервисы сами разрешают зависимости через глобальный `ServiceProvider`, а переданная в `ParseOrchestrator` фабрика парсеров фактически не используется.

## Проблема

1. **`ParserFactory` не участвует в создании парсеров.** `ParseOrchestrator` сохраняет `self._parser_factory` (`services/parse_orchestrator.py:73`), но `_parse_all_vendors()` вызывает `parser_for_vendor()` напрямую (`services/parse_orchestrator.py:108`). Явно переданная фабрика не влияет на поведение и не является рабочей точкой расширения или тестовой подменой.
2. **Контракт `ParserFactory` не совпадает с данными оркестратора.** В контейнере зарегистрирован `make_parser`: он принимает непустой `ParseConfiguration` (+ `markup_policy`) и не умеет ни `None`, ни `is_enabled=False`, ни `make_config_driven_parser`. Список поставщиков (`VendorList`) состоит из `(type[BaseParser], ParseConfiguration | None)`, а ветвление «config-driven парсер или `vendor_cls(parse_config=…)`» живёт только в `services/vendor_parser.parser_for_vendor`. Подстановка фабрики «как есть» изменила бы поведение.
3. **Сервисы используют Service Locator.** `ParseOrchestrator` самостоятельно разрешает `ParserFactory` и `GrouperFactory`, `PriceReportService` — фабрики writer через `common_price_out()`, `PriceSchemaService` — себя через `ServiceProvider.resolve()` в `schema_guard()`. Обязательные зависимости скрыты в телах методов и конструкторов, а работоспособность зависит от предварительной глобальной регистрации.
4. **Скрытый источник поставщиков.** Оркестратор внутри конструктора создаёт `VendorSource(config_provider)` (с откатом на глобальный `ConfigProvider`) и берёт из него `entry_for`, `aliases_map`, `reference_priority`; внедряется лишь `vendors_provider: Callable`. Замена одного `vendors_provider` оставила бы остальной граф скрытым.
5. **`DoublesService` скрывает зависимости прямым конструированием.** Он сам создаёт `ParseOrchestrator()` и `PriceReportService()` (`services/doubles_service.py:31-32`). После перехода этих сервисов на обязательные зависимости оба вызова упадут с `TypeError`, а регистрация `DoublesService` в `configure.py` сломает `ServiceProvider.resolve(DoublesService)`.
6. **Композиционный корень не владеет всем графом.** `services/configure.py` регистрирует классы сервисов без их конкретных зависимостей, поэтому по сигнатурам конструкторов нельзя восстановить реальный граф объектов.

## Цель

Сделать зависимости сервисов явными и проверяемыми через конструкторы. Конкретный граф собирается в `services/configure.py`; обращения к `ServiceProvider` остаются только в композиционном корне и на границе приложения `app`.

## Что нужно сделать

1. **Починить создание парсеров через `ParserFactory`.**
   - Новый контракт: `ParserFactory = (parser_cls: type[BaseParser], parse_config: ParseConfiguration | None) -> BaseParser`, то есть принимает запись из `VendorList` как есть и возвращает готовый `BaseParser` (стратегии, ридер, политика наценки).
   - Реализация по умолчанию в `configure.py` — логика `parser_for_vendor` (все три ветки: нет/выключенный конфиг, нет секции, config-driven). `make_parser` как зарегистрированная фабрика заменяется; параметр `markup_policy` убрать из протокола, если у него нет вызывающих (проверить `vulture`/grep), иначе оставить и обосновать.
   - В цикле разбора вызывать `self._parser_factory(vendor_cls, vendor_config)`. Прямых вызовов `parser_for_vendor()` из `ParseOrchestrator` не остаётся; сама функция живёт как реализация по умолчанию, а не удаляется.
2. **Передавать зависимости `ParseOrchestrator` через конструктор.**
   - Обязательные keyword-аргументы: `parser_factory`, `grouper_factory`, `vendor_source` (`VendorSource` целиком — он даёт и список поставщиков, и `entry_for`, `aliases_map`, `reference_priority`). Параметр `vendors_provider` убрать, если он дублирует `vendor_source.all`; оставить — только с обоснованием.
   - Убрать `or ServiceProvider.resolve(...)` и значения `None` по умолчанию; импорт `ServiceProvider` из модуля удалить. Сборку реализаций по умолчанию выполнять в `configure_services()`.
3. **Убрать Service Locator из `PriceReportService`.**
   - Передавать фабрику `CommonPriceOut` (callable `list[RowItem] -> CommonPriceOut`) обязательным аргументом; конкретную фабрику с `XlsWriterFactory`, `WriteDriverFactory` и `ConfigProvider` собирает `configure.py`.
   - Функцию `common_price_out()` с `ServiceProvider.resolve` удалить; импорт `ServiceProvider` из `price_report.py` убрать.
4. **Убрать саморазрешение `PriceSchemaService`.**
   - Функцию `schema_guard()` удалить. В `app` (`run.py`, `run_machine.py`) использовать `ServiceProvider.resolve(PriceSchemaService).guard()`; оставшиеся тесты, патчащие `schema_guard` (сейчас `tests/test_cli/test_run_update_all_json.py`, `app.run_machine.schema_guard`), обновить на новый вызов без ослабления проверок; тесты `app.run`, патчащие `ServiceProvider.resolve(PriceSchemaService)` (например `tests/test_run_mail.py`), уже в нужном виде.
   - Контракт `guard()` (копия до, сравнение после, вложенные блоки через `_depth`) не меняется. Зафиксировать и покрыть тестом время жизни сервиса в контейнере (один экземпляр или новый на каждый `resolve`), чтобы вложенные `guard()` вели себя как сейчас.
5. **Собрать граф в `services/configure.py`.**
   - Регистрации `ParseOrchestrator`, `PriceReportService`, `PriceSchemaService` создают объекты с конкретными зависимостями.
   - В `app` сохранить текущий способ получения сервисов через `ServiceProvider.resolve()`.
6. **Перевести `DoublesService` на обязательные зависимости.**
   - `orchestrator: ParseOrchestrator` и `report_service: PriceReportService` — обязательные аргументы конструктора; создание сервисов внутри класса и `or ...()` убрать.
   - В `configure.py` собирать `DoublesService` из `ServiceProvider.resolve(ParseOrchestrator)` и `ServiceProvider.resolve(PriceReportService)`; порядок регистраций учесть.
7. **Сохранить поведение.** CLI, разбор прайсов, группировка, запись XLSX/JSONL, проверка схем, обработка ошибок и коды возврата не меняются.

## Тесты

- Тест на причину: `ParseOrchestrator` вызывает именно переданную `ParserFactory`, а не `parser_for_vendor()`. Использовать фейковую фабрику, записывающую вызовы (не monkeypatch функции); тест должен падать на исходной реализации.
- Фабрика получает `(vendor_cls, vendor_config)` ровно из записи списка (включая `None`-конфиг), а возвращённый ею парсер используется для разбора.
- Реализация по умолчанию (бывший `parser_for_vendor`) сохраняет все три ветви сборки — покрыто существующими или новыми тестами.
- `ParseOrchestrator`, `PriceReportService`, `DoublesService` и сценарий `PriceSchemaService` создаются с явными тестовыми зависимостями без предварительной регистрации в глобальном контейнере.
- Тест композиционного корня (расширить `tests/test_services/test_configure.py`): после `configure_services()` разрешаются `ParseOrchestrator`, `PriceReportService`, `PriceSchemaService` и `DoublesService`; оркестратор и отчёт используют зарегистрированные фабрики, `DoublesService` получает собранные контейнером сервисы (транзитивный граф отчёта о дублях), а время жизни `PriceSchemaService` соответствует зафиксированному.
- Сохранить существующие тесты CLI, записи прайсов и проверки схем; при необходимости обновить только сборку зависимостей, не ослабляя проверки поведения.

## План

Каждый пункт — отдельный коммит (после подтверждения пользователя):

1. Падающий тест на неиспользуемую `ParserFactory`; новый контракт фабрики, регистрация `parser_for_vendor` по умолчанию, вызов через `self._parser_factory`.
2. `ParseOrchestrator`: обязательные constructor-зависимости (включая `VendorSource`), обновление регистрации.
3. `PriceReportService`: явная фабрика writer, удаление `common_price_out()`.
3а. `DoublesService`: обязательные `orchestrator` и `report_service`, сборка в `configure.py` (делать вместе с шагами 2–3 или сразу после, чтобы не ломать `resolve(DoublesService)` между коммитами).
4. `PriceSchemaService`: удаление `schema_guard()`, переход `app` на `resolve(...).guard()`.
5. Проверить, что в `src/services/` не осталось `ServiceProvider.resolve()` / `create()` вне `service_provider.py` и `configure.py`.
6. Полный набор проверок из `AGENTS.md`.

## Вне области задачи

- Удаление `ServiceProvider` из `app` или полная замена контейнера.
- Удаление глобального `ConfigProvider` и `domain/config_context.py`. Сервисы обновления (`ZapaskaService`, `MimService`, `MailService`, `FourTochkiService`) и `VendorActivationService` с необязательным `config_provider` и откатом на `get_config_provider()` не меняются — отдельная задача. В рамках task-24 `ConfigProvider` передаётся явно только в новые сборки `PriceReportService`/`ParseOrchestrator`/`PriceSchemaService`.
- Изменение строкового API `RowItem.get_field()` / `set_field()`.
- Изменение архитектурных слоёв и правил `import-linter`.

## Критерии готовности

- [x] `ParseOrchestrator` создаёт парсеры через переданную `ParserFactory` с контрактом `(cls, ParseConfiguration | None) -> BaseParser`; это закреплено тестом на исходную причину.
- [x] Зависимости `ParseOrchestrator`, `PriceReportService`, `PriceSchemaService`, `DoublesService` видны в сигнатурах конструкторов и не разрешаются через глобальный контейнер внутри сервисов; `schema_guard()` и `common_price_out()` удалены.
- [x] Конкретный граф зависимостей собирается в `services/configure.py`.
- [x] `ServiceProvider.resolve()` / `create()` в `src/services/` остаются только в `service_provider.py` и `configure.py`.
- [x] Пользовательское поведение CLI, разбор прайсов, запись результатов и проверка схем сохранены.
- [x] `uv run pytest`, `uv run mypy .`, `uv run lint-imports` и остальные обязательные проверки из `AGENTS.md` проходят по всему репозиторию с кодом 0.
