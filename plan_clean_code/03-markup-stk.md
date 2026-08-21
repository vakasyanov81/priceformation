# 03. STK: наценка в JSON

Подробно: [03-markup-stk-detail.md](details/03-markup-stk-detail.md)  
Задачи: [03-markup-stk-tasks.md](details/03-markup-stk-tasks.md)

Этап: [1. Единая политика наценки](../PLAN_CLEAN_CODE.md#этап-1-единая-политика-наценки)  
Статус: сделана  
Зависит от: [01. MarkupPolicy](01-markup-policy.md), [02. Poshk / Pioner](02-markup-poshk-pioner.md) (`MapOnOptMarkupPolicy`)  
Дальше: [04. Zapaska](04-markup-zapaska.md)

## Зачем

`STK_PRICE_MARKUP_MULTIPLIER = 1.06` зашит в Python. Смена процента — правка кода, хотя у поставщика уже есть (или должен быть) `markup_rules.json`.

## Сделать

1. Перенести 6% в `stk_markup_rules.json` (или файл поставщика по принятой схеме).
2. Удалить константу и свой `add_price_markup` в `stk.py`.
3. Считать через `MarkupPolicy`.

## Файлы

- `src/parsers/vendors/stk.py`
- `parse_config/stk_markup_rules.json` (или актуальный путь)
- `tests/test_parsers/test_vendors/test_stk.py`

## Готово, когда

- Изменение % STK не требует правки Python.
- Тесты STK зелёные, цена с наценкой та же при 1.06.

## Не делать

Общий рефакторинг `process()`, другие поставщики.
