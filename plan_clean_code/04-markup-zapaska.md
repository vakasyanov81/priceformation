# 04. Zapaska: наценка в JSON

Подробно: [04-markup-zapaska-detail.md](details/04-markup-zapaska-detail.md)

Этап: [1. Единая политика наценки](../PLAN_CLEAN_CODE.md#этап-1-единая-политика-наценки)  
Статус: сделана  
Зависит от: [01. MarkupPolicy](01-markup-policy.md)  
Дальше: [05. Autosnab](05-markup-autosnab.md)

## Зачем

`zapaska_disk_markup.py` держит `_percent_map()`, `MIN_RECOMMENDED_MARGIN_PERCENT`, `_ABSOLUTE_MARKUP_DELTA` в коде. JSON правил поставщика обходится.

## Сделать

1. Перенести диапазоны %, порог recommended и абсолютную дельту в JSON Zapaska.
2. Считать через ту же `MarkupPolicy`, что и остальные vendors.
3. Удалить или свести к адаптеру JSON `zapaska_disk_markup.py`.
4. Обновить тесты `test_zapaska_disk_markup.py` и parse-тесты disk/tire.

## Файлы

- `src/parsers/vendors/zapaska_disk_markup.py`
- `src/parsers/vendors/zapaska_disk_json.py`
- `parse_config/zapaska_markup_rules.json` (актуальное имя)
- `tests/test_parsers/test_vendors/test_zapaska_disk_markup.py`
- `tests/test_parsers/test_vendors/test_parse_zapaska_disk_json.py`
- `tests/test_parsers/test_vendors/test_parse_zapaska_tire_json.py`

## Готово, когда

- Изменение диапазона % Zapaska — только JSON.
- Числа в фикстурах те же при тех же правилах.

## Не делать

HTTP-клиент и `load_remote_data` — [15](15-zapaska-http.md). JSON reader — [12](12-parser-json-reader.md).
