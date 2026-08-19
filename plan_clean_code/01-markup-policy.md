# 01. Вынести MarkupPolicy

Подробно: [01-markup-policy-detail.md](details/01-markup-policy-detail.md)  
Задачи: [01-markup-policy-tasks.md](details/01-markup-policy-tasks.md)

Этап: [1. Единая политика наценки](../PLAN_CLEAN_CODE.md#этап-1-единая-политика-наценки)  
Статус: не начата  
Зависит от: —  
Дальше: [02. Poshk / Pioner](02-markup-poshk-pioner.md)

## Зачем

Расчёт наценки сидит в `BaseParser.add_price_markup`. Vendors копируют или обходят его. Смена правила требует правок в нескольких классах.

## Сделать

1. Модуль рядом с `price_markup.py`: класс/функции `MarkupPolicy` (не методы `BaseParser`).
2. Базовый алгоритм (`min/max` percent, recommended, absolute) — единственная реализация из `markup_rules.json`.
3. `BaseParser.add_price_markup` пока делегирует в политику (удаление — [06](06-markup-cleanup.md)).
4. Существующие тесты `test_price_markup.py` перевести на политику.

## Файлы

- `src/parsers/base_parser/price_markup.py`
- `src/parsers/base_parser/base_parser.py`
- `tests/test_base_parser/test_price_markup.py`

## Готово, когда

- Формулы наценки не в `BaseParser`, а в `MarkupPolicy`.
- Поведение базового алгоритма без регрессий.
- `uv run pytest` зелёный.

## Не делать

Перевод poshk/pioner/stk/zapaska/autosnab — отдельные задачи. Не трогать `process()`, колонки, HTTP.
