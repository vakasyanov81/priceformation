# Архитектурные улучшения priceformation

План поэтапного улучшения архитектуры проекта по приоритетам.

---

## P0 — Критические (связанность, расширяемость)

| # | Задача | Кратко |
|---|--------|--------|
| 1 | [Vendor Registry](./task-01-vendor-registry.md) | Заменить хардкод списка вендоров на декоратор `@register_vendor`. Политики наценки — атрибут класса, не `if`-цепи. |
| 2 | [Dependency Injection](./task-02-di-container.md) | Легковесный DI-контейнер / `ServiceProvider`. Убрать ручное конструирование зависимостей через `make_parser()`. |

## P1 — Средние (сложность, SRP)

| # | Задача | Кратко |
|---|--------|--------|
| 3 | [Services layer](./task-03-services-layer.md) | Выделить слой оркестрации в `services/`: `ParseOrchestrator`, `PriceReportService`. Убрать бизнес-логику из `run.py` и `common_price.py`. |
| 4 | [Composition over Inheritance в BaseParser](./task-04-composition.md) | Заменить 6-уровневую иерархию наследования на композицию. `BaseParser` получает ридер, политику наценки, обработчик строк через конструктор. |
| 5 | [Value Objects для RowItem](./task-05-value-objects.md) | Разбить `RowItem` на композитные value objects: `TireDimensions`, `DiskParams`, `Pricing`. |
| 6 | [Typed parser stats](./task-06-typed-stats.md) | Убрать `getattr(parser, "black_list_skips", 0)`. Ввести интерфейс `ParserStats`. |

## P2 — Перспективные (качество, тестируемость)

| # | Задача | Кратко |
|---|--------|--------|
| 7 | [Logging через logging.Logger](./task-07-logging.md) | Заменить глобальные `log_msg`/`err_msg`/`warn_msg` на `logging.Logger` с иерархическими именами. |
| 8 | [Pydantic для конфигов](./task-08-pydantic-configs.md) | Заменить `dict[str, Any]` + `cast()` на Pydantic-модели с валидацией. |
| 9 | [Разделение core/ на domain/ и infrastructure/](./task-09-domain-infrastructure.md) | IO-операции (файлы, JSON) — в `infrastructure/`. Чистые сущности и исключения — в `domain/`. |
| 10 | [Абстрактный ConfigProvider](./task-10-config-provider.md) | Вынести управление путями и env в интерфейс `ConfigProvider`. Текущий `MainConfig` — одна из реализаций. |

---

## Диаграмма зависимостей (целевая)

```
run.py / run_machine.py          ← entry points
    │
    ▼
services/                        ← оркестрация
    │
    ├── domain/                   ← сущности, value objects, порты (interfaces)
    │   ├── RowItem / TireDim / ...
    │   ├── MarkupPolicy
    │   ├── ParserStats (protocol)
    │   ├── ConfigProvider (protocol)
    │   └── DataProvider (protocols)
    │
    ├── infrastructure/           ← IO, адаптеры
    │   ├── FileConfigProvider
    │   ├── JsonDataProvider
    │   ├── XlsReader / JsonlReader
    │   └── XlsxWriter / JsonlWriter
    │
    └── parsers/                  ← вендорные парсеры
        ├── registry              ← @register_vendor
        └── vendors/
            └── ...
```

Каждая задача снабжена отдельным файлом с критериями «готово» и планом миграции.