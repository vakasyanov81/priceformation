# 12. JSON reader для Zapaska

Подробно: [12-parser-json-reader-detail.md](details/12-parser-json-reader-detail.md)

Этап: [3. Разрезать BaseParser](../PLAN_CLEAN_CODE.md#этап-3-разрезать-baseparser)  
Статус: сделана  
Зависит от: [09. Pipeline](09-parser-pipeline.md)  
Дальше: [13. Мёртвый код](13-parser-dead-code.md)

## Зачем

`ZapaskaDiskJSON.raw_parse` — override God-object: чтение JSON и rename ключей внутри парсера. Рядом уже есть `IXlsReader`.

## Сделать

1. Reader JSON с тем же контрактом, что `IXlsReader.parse` → `list[dict]`.
2. Rename полей (`rename_fields` / `column_mapping`) — в reader или тонком адаптере, не в `BaseParser`.
3. `ZapaskaDiskJSON` / tire не держат низкоуровневый `Path.open` + `json.loads`.

## Файлы

- `src/parsers/vendors/zapaska_disk_json.py`
- `src/parsers/xls_reader.py` (ориентир интерфейса)
- `src/parsers/fake_xls_reader.py` (аналог fake для JSON, если нужен тестам)
- `tests/test_parsers/test_vendors/test_parse_zapaska_disk_json.py`
- `tests/test_parsers/test_vendors/test_parse_zapaska_tire_json.py`

## Готово, когда

- JSON Zapaska читается через reader, не через override `raw_parse` с I/O внутри класса парсера.
- Parse-тесты зелёные.

## Не делать

HTTP `get_data` / `save_data` — [15](15-zapaska-http.md).
