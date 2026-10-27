# Архитектурные улучшения priceformation

План поэтапного улучшения архитектуры проекта по приоритетам.

---

## P0 — Критические (связанность, расширяемость)

| # | Задача | Кратко | Статус |
|---|--------|--------|--------|
| 1 | [Vendor Registry](./task-01-vendor-registry.md) | Заменить хардкод списка вендоров на декоратор `@register_vendor`. Политики наценки — атрибут класса, не `if`-цепи. | ✅ |
| 2 | [Dependency Injection](./task-02-di-container.md) | Легковесный DI-контейнер / `ServiceProvider`. Убрать ручное конструирование зависимостей через `make_parser()`. | ✅ |

## P1 — Средние (сложность, SRP)

| # | Задача | Кратко | Статус |
|---|--------|--------|--------|
| 3 | [Services layer](./task-03-services-layer.md) | Выделить слой оркестрации в `services/`: `ParseOrchestrator`, `PriceReportService`. Убрать бизнес-логику из `run.py` и `common_price.py`. | ✅ |
| 4 | [Composition over Inheritance в BaseParser](./task-04-composition.md) | Заменить 6-уровневую иерархию наследования на композицию. `BaseParser` получает ридер, политику наценки, обработчик строк через конструктор. | ✅ |
| 5 | [Value Objects для RowItem](./task-05-value-objects.md) | Разбить `RowItem` на композитные value objects: `TireDimensions`, `DiskParams`, `Pricing`. | ✅ |
| 6 | [Typed parser stats](./task-06-typed-stats.md) | Убрать `getattr(parser, "black_list_skips", 0)`. Ввести интерфейс `ParserStats`. | ✅ |

## P2 — Перспективные (качество, тестируемость)

| # | Задача | Кратко | Статус |
|---|--------|--------|--------|
| 7 | [Logging через logging.Logger](./task-07-logging.md) | Заменить глобальные `log_msg`/`err_msg`/`warn_msg` на `logging.Logger` с иерархическими именами. | ✅ |
| 8 | [Типизированные конфиги](./task-08-typed-configs.md) | Заменить `dict[str, Any]` + `cast()` на dataclass-модели с валидацией на границе. Без внешних зависимостей. | ✅ |
| 9 | [Разделение core/ на domain/ и infrastructure/](./task-09-domain-infrastructure.md) | IO-операции (файлы, JSON) — в `infrastructure/`. Чистые сущности и исключения — в `domain/`. | ✅ |
| 10 | [Абстрактный ConfigProvider](./task-10-config-provider.md) | Вынести управление путями и env в интерфейс `ConfigProvider`. Текущий `MainConfig` — одна из реализаций. | ✅ |

## P3 — Расширяемость (конфигурация вместо кода)

| # | Задача | Кратко | Статус |
|---|--------|--------|--------|
| 11 | [Поставщики целиком в конфигурации](./task-11-vendor-config.md) | Один `BaseParser`: колонки, листы, наценки и поведение поставщика — в `parse_config/vendors/<folder>.json`; реестр из конфигов; `src/parsers/vendors/` удаляется. | 🟡 этап 1/7 |

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

---

## Отдельные планы

| Документ | О чём |
| --- | --- |
| [Независимое определение типа товара](./task-12-product-type.md) | Классификатор `type_production` по названию и параметрам (README_ProductType.md §2–§9), слой поверх стратегий категории, признак расхождения `type_corrected` и маркер `*` в `for_inner`. |
| [Усиление тестов по данным mutmut](./MUTATION_TESTS.md) | 9 фаз по результатам прогона `mutmut`: чистка конфига, схема JSON-отчёта, байтовый формат jsonl, диспуты, золотые ключи группировки, значения листа xlsx, поведение CLI, вложенные папки, тексты исключений. Цель — 88 % → ~94 %. |
| [Усиление тестов нового кода по mutmut](./task-13-mutation-new-code.md) | Прогон 2026-10-14: 98.2 % → 94.9 %, +304 выживших только в новом коде — почта (IMAP/DoH, конфиг), классификатор типа товара, названия Пошка/STK, наценка Форточек. 6 фаз M1–M6, цель ≥ 98 %. |
| [Убрать `# flake8: noqa` из оркестратора](./task-18-orchestrator-flake8-noqa.md) | Директива скрывает WPS201 (24 > 18 импортов) и WPS202 (8 > 7 членов модуля). Вынести сводку логов, сборку парсера и `ParseResult` в отдельные модули в `services/`. |
| [Убрать `# flake8: noqa` из `BaseParser`](./task-19-base-parser-flake8-noqa.md) | Директива скрывает WPS201 (24 > 18 импортов), WPS214 (52 > 7 методов в классе) и WPS231 (сложность `_run_pipeline` 15 > 12). Разложить `BaseParser` по ролям. |
| [Убрать `# flake8: noqa` из двух модулей стратегий](./task-20-strategies-flake8-noqa.md) | `_four_tochki_tire_helper.py` и `_tire_title_parser.py`: директива скрывает WPS202 и ещё WPS210/221/237/110. Разбить модули по ролям, упростить функции. |
| [`BaseParser`: от наследования к композиции](./task-21-base-parser-composition.md) | Заменить цепочку миксинов из task-19 коллабораторами с явными зависимостями; `BaseParser` — тонкий оркестратор. |
| [Устранение замечаний по качеству кода](./QUALITY_PLAN.md) | 14 задач по итогам ревью: bandit и pip-audit в CI, тестовые заглушки в колесе, мёртвый код, мутабельные `ParserParams`, опечатки в именах модулей. |

План по тестам не пересекается с архитектурным: он меняет только `tests/` и
конфигурацию `[tool.mutmut]`, production-код не трогает.