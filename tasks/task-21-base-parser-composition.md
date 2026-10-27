# Task-21: `BaseParser` — от цепочки наследования к композиции

Продолжение [task-19](./task-19-base-parser-flake8-noqa.md).

## Проблема

Task-19 уложил `BaseParser` в лимит WPS214 цепочкой миксинов: `ParserCore` → `ParserFiles` → `ParserTitle` → `ParserRows` → `ParserCategory` → `ParserMarkup` → `ParserPipeline` → `BaseParser` (`src/parsers/base_parser/parser_*.py`). Лимит выполнен формально, но это та же «большая вещь», разрезанная по файлам:

- слои делят состояние через `self` (`_strategy_hooks`, `_title_filter`, `_category_finder`, `stats`, …), границы ролей не проверяются типами;
- порядок слоёв — скрытый контракт: метод одного слоя вызывает методы следующих через `self`;
- слой нельзя подменить или протестировать отдельно, не создавая `BaseParser`;
- публичный API (≈50 методов) по-прежнему живёт на одном объекте.

## Решение

Выделить роли в самостоятельные объекты с явными зависимостями; `BaseParser` — тонкий оркестратор, который их собирает и ведёт `parse` / `process` / `after_process`.

Целевые коллабораторы (границы уточнить картой вызовов на этапе 1):

| Объект | Роль | Методы из слоёв |
| --- | --- | --- |
| `ParserSettings` | конфиг, параметры, `is_active`, имя поставщика | `ParserCore` |
| `PriceFiles` | файлы, чтение строк, маппинг в `RowItem` | `ParserFiles` |
| `TitleService` | текстовые хелперы и подготовка title | `ParserTitleText`, `ParserTitle` |
| `RowFilters` | склады, минимальный остаток, служебные строки | `ParserRows` |
| `CategoryService` | категория и независимый тип товара (реализует `CategoryContext`) | `ParserCategory` |
| `MarkupService` | производитель и наценка | `ParserManufacturer`, `ParserMarkup` |
| `RowPipeline` | шаги разбора строки | `ParserPipeline` |

Зависимости передаются аргументами конструктора (`StrategyHooks`, `ParserStats`, фильтры), без общего `self`. Протоколы — в `parsers/base_parser/protocols.py`. Хелперы `base_parser_row.py` (`enrich_items`, `_keep_row_item`, …) принимают узкие протоколы вместо `parser: BaseParser`, чтобы убрать `TYPE_CHECKING`-импорт `BaseParser`.

### Что меняется для вызывающих

Фасад с ≤ 7 методами не сохранит ≈50 публичных методов. Поэтому:

1. Вызовы `parser.<метод>` в `src/` и тестах переводятся на коллаборатора (`parser.titles.set_prepared_title(...)`) или на сам объект коллаборатора в тесте.
2. Заглушки в виде `__getattr__`-делегирования не вводить: они прячут тот же монолит.
3. Подклассы `BaseParser` в тестах (`tests/test_base_parser/test_parser_hooks.py`, `test_file_prices.py`, `test_base_parser_process.py`, `test_row_filters.py`), переопределяющие `get_min_rest_count`, `after_row_mapped`, `prepare_title` и т. п., переписываются на подмену коллаборатора или стратегии.
4. `config_driven_parser.make_config_driven_parser` собирает коллабораторов явно.

Ограничение: вывод парсеров не меняется (`integration_tests/test_parity_vendor_config.py`), слои `lint-imports` не нарушаются, подавления не добавляются.

## План миграции

1. Карта вызовов: какой метод какие поля и методы использует; границы коллабораторов.
2. Протоколы и узкие сигнатуры хелперов `base_parser_row.py`.
3. По одному коллаборатору за шаг (порядок: `ParserSettings` → `PriceFiles` → `RowFilters` → `TitleService` → `CategoryService` → `MarkupService` → `RowPipeline`): вынос из слоя, перевод вызовов, удаление слоя-миксина. После каждого шага — полный набор проверок.
4. Удалить пустую цепочку; `BaseParser` остаётся с `parse`, `process`, `after_process` и конструктором.
5. Прямые тесты на коллабораторов (порог 95 %).

## Критерии готовности

- [ ] `BaseParser` не наследует миксины; файлов `parser_core.py` … `parser_pipeline.py` как цепочки нет.
- [ ] Коллабораторы создаются с явными зависимостями и тестируются без `BaseParser`.
- [ ] В `base_parser_row.py` нет `TYPE_CHECKING`-импорта `BaseParser`.
- [ ] `__getattr__`-делегирования и подавлений (`# noqa`, `# type: ignore`) нет.
- [ ] Вывод парсеров не изменился (паритет конфигов, интеграционные тесты).
- [ ] Проверки по AGENTS.md проходят по всему репозиторию (exit 0).
- [ ] Коммит — только после подтверждения пользователя.
