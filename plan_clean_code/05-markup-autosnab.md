# 05. Autosnab: политика «без наценки»

Подробно: [05-markup-autosnab-detail.md](details/05-markup-autosnab-detail.md)

Этап: [1. Единая политика наценки](../PLAN_CLEAN_CODE.md#этап-1-единая-политика-наценки)  
Статус: сделана  
Зависит от: [01. MarkupPolicy](01-markup-policy.md)  
Дальше: [06. Очистка BaseParser](06-markup-cleanup.md)

## Зачем

`Autosnab54Parser.process` пишет `price_markup = price_opt` прямо в цикле. Это внутренний склад: цена уже с наценкой, правил в JSON нет.

## Сделать

1. Явная политика «без наценки» (`price_markup = price_opt`, с округлением если оно уже есть в поведении).
2. Убрать ветку из `process()`.
3. Прогнать `test_parse_autosnab54_ru.py`.

## Файлы

- `src/parsers/vendors/autosnab54_ru.py`
- `src/parsers/base_parser/price_markup.py` (или модуль политики)
- `tests/test_parsers/test_vendors/test_parse_autosnab54_ru.py`

## Готово, когда

- В `process()` Autosnab нет присвоения `price_markup`.
- Цены в фикстурах без регрессий.

## Не делать

Рефакторинг `fill_from_title` и общего `process()` — этап 3.
