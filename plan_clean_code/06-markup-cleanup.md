# 06. Очистка BaseParser и контракт JSON

Подробно: [06-markup-cleanup-detail.md](details/06-markup-cleanup-detail.md)

Этап: [1. Единая политика наценки](../PLAN_CLEAN_CODE.md#этап-1-единая-политика-наценки)  
Статус: не начата  
Зависит от: [02](02-markup-poshk-pioner.md), [03](03-markup-stk.md), [04](04-markup-zapaska.md), [05](05-markup-autosnab.md)  
Дальше: [09. Pipeline](09-parser-pipeline.md) (этап 3) или [07. Фабрика](07-config-factory.md)

## Зачем

После перевода vendors `add_price_markup` в `BaseParser` либо тонкий делегат, либо мёртвый код. Ключи JSON `percent` / `percent_markup` должны быть зафиксированы тестом, иначе схема снова разъедется.

## Сделать

1. `BaseParser.add_price_markup` — тонкий делегат в политику или удалить, если все вызовы уже через pipeline/политику.
2. Контрактный тест: ключи `percent` и `percent_markup` в JSON → одинаковый `MarkUpParams` (опереться на `markup_params_from_rule`).
3. Проверить, что в vendors нет локальных формул наценки (`grep` по `add_price_markup`, `1.06`, `_percent_map`).

## Файлы

- `src/parsers/base_parser/base_parser.py`
- `src/parsers/data_provider/markup_rules.py`
- `tests/test_base_parser/test_price_markup.py`
- `tests/test_parsers/test_data_provider/test_markup_rules_contract.py` (создать при необходимости)

## Готово, когда

- Нет дублирующих формул наценки в vendors.
- Оба ключа JSON покрыты тестом.
- Этап 1 закрыт: [план](../PLAN_CLEAN_CODE.md#этап-1-единая-политика-наценки).

## Не делать

Резать `process()`, glob, HTTP.
