# 13. Мёртвый Command, контракт title, Пионер

Подробно: [13-parser-dead-code-detail.md](details/13-parser-dead-code-detail.md)

Этап: [3. Разрезать BaseParser](../PLAN_CLEAN_CODE.md#этап-3-разрезать-baseparser)  
Статус: не начата  
Зависит от: [10. Хуки](10-parser-hooks.md)  
Дальше: [14. Writer](14-writer-layers.md) (этап 4)

## Зачем

`_item_actions = []` не используется. `get_prepared_title` — classmethod в базе и instance method у Zapaska (`type: ignore[override]`). Пионер вызывает `ManufacturerFinder` второй раз в `process()`.

## Сделать

1. Удалить `_item_actions`, если Command так и не нужен. `SetPercentMarkupItemAction` — встроить в pipeline или оставить единственным post-step.
2. `get_prepared_title` — один контракт (instance method). Убрать `# type: ignore[override]` у Zapaska.
3. Пионер: не вызывать `ManufacturerFinder` повторно, если enrich уже это делает.

## Файлы

- `src/parsers/base_parser/base_parser.py`
- `src/parsers/base_item_actions/*`
- `src/parsers/vendors/zapaska_disk_json.py`
- `src/parsers/vendors/pioner.py`
- `tests/test_base_parser/test_parse_statistic.py`

## Готово, когда

- Нет пустого списка `_item_actions`.
- Нет `type: ignore[override]` на `get_prepared_title`.
- Этап 3 закрыт: [план](../PLAN_CLEAN_CODE.md#этап-3-разрезать-baseparser).
- Vendor-фикстуры без регрессий.

## Не делать

HTTP Zapaska, смена формата XLSX.
