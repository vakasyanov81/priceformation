# 09. Явный pipeline парсера

Подробно: [09-parser-pipeline-detail.md](details/09-parser-pipeline-detail.md)

Этап: [3. Разрезать BaseParser](../PLAN_CLEAN_CODE.md#этап-3-разрезать-baseparser)  
Статус: сделана  
Зависит от: [06. Очистка наценки](06-markup-cleanup.md) (сделана); этап 2 закрыт  
Дальше: [10. Хуки vendors](10-parser-hooks.md)

## Зачем

После этапа 1 vendors больше не копируют `process()`. Хук `process_parsed_row` уже заполнен, наценка идёт из него. Но `parse` / `process` всё ещё два комка без имён шагов — новый шаг снова попадёт внутрь blob.

## Сделать

1. Явный pipeline вокруг текущего потока: read → map `RowItem` → filter → enrich → vendor hook (`process_parsed_row`) → drop empty rest → percent action.
2. Оркестрация в `BaseParser.parse` / тонком `process()`; формулы наценки не возвращать в класс (политика из этапа 1).
3. Сохранить поведение фильтров (`_try_prepare_row`, `_keep_row_item`, `remove_null_rest`) и порядок «хук → `remove_null_rest`».
4. **Не** добавлять отдельный `apply_markup` в `parse`: хук уже зовёт наценку (иначе ×2, у Zapaska ещё и `make_price_markup`).

## Файлы

- `src/parsers/base_parser/base_parser.py`
- `src/parsers/base_parser/base_parser_row.py`
- тесты `tests/test_base_parser/`

## Готово, когда

- Шаги pipeline читаются по именам методов/функций, не как один `process()` без сценария.
- Базовые тесты парсера без регрессий (`test_base_parser_process.py` в том числе: суффикс файла, счётчик до фильтров).

## Не делать

Вынос glob ([11](11-parser-price-source.md)), JSON reader ([12](12-parser-json-reader.md)), HTTP ([15](15-zapaska-http.md)), дробление `process_parsed_row` на хуки title/category/rest ([10](10-parser-hooks.md)).
