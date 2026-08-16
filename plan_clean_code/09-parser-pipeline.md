# 09. Явный pipeline парсера

Подробно: [09-parser-pipeline-detail.md](details/09-parser-pipeline-detail.md)

Этап: [3. Разрезать BaseParser](../PLAN_CLEAN_CODE.md#этап-3-разрезать-baseparser)  
Статус: не начата  
Зависит от: [06. Очистка наценки](06-markup-cleanup.md)  
Дальше: [10. Хуки vendors](10-parser-hooks.md)

## Зачем

`BaseParser` смешивает чтение, маппинг, фильтры, enrich и наценку. Без явных шагов vendors продолжат копировать циклы в `process()`.

## Сделать

1. Явный pipeline: read → map `RowItem` → filter → enrich → markup.
2. Оркестрация в `BaseParser.parse` / тонком runner; формулы наценки не возвращать в класс (политика из этапа 1).
3. Сохранить текущее поведение фильтров (`_try_prepare_row`, `_keep_row_item`, `remove_null_rest`).

## Файлы

- `src/parsers/base_parser/base_parser.py`
- `src/parsers/base_parser/base_parser_row.py`
- тесты `tests/test_base_parser/`

## Готово, когда

- Шаги pipeline читаются по именам методов/функций, не как один `process()` на 30 строк.
- Базовые тесты парсера без регрессий.

## Не делать

Вынос glob ([11](11-parser-price-source.md)), JSON reader ([12](12-parser-json-reader.md)), HTTP ([15](15-zapaska-http.md)).
