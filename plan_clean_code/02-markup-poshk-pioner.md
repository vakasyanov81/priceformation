# 02. Poshk / Pioner на общую политику

Подробно: [02-markup-poshk-pioner-detail.md](details/02-markup-poshk-pioner-detail.md)

Этап: [1. Единая политика наценки](../PLAN_CLEAN_CODE.md#этап-1-единая-политика-наценки)  
Статус: не начата  
Зависит от: [01. MarkupPolicy](01-markup-policy.md)  
Дальше: [03. STK](03-markup-stk.md)

## Зачем

`PoshkParser.add_price_markup` и `PionerParser.add_price_markup` дублируют `get_markup_percent` + `round_price`. Две копии той же формулы.

## Сделать

1. Удалить собственные `add_price_markup` у Poshk и Pioner.
2. Использовать политику из [01](01-markup-policy.md) (`get_markup_percent` + `round_price`).
3. Прогнать vendor-тесты poshk и pioner.

## Файлы

- `src/parsers/vendors/poshk.py`
- `src/parsers/vendors/pioner.py`
- `tests/test_parsers/test_vendors/test_parse_poshk.py`
- тесты pioner, если есть отдельные кейсы наценки

## Готово, когда

- В poshk/pioner нет своей формулы наценки.
- Фикстуры разбора без регрессий.

## Не делать

Рефакторинг `process()`, повторный `ManufacturerFinder` у Пионера — [13](13-parser-dead-code.md).
