# 10. Хуки vendors вместо циклов `process()` — подробно

Краткая задача: [10-parser-hooks.md](../10-parser-hooks.md)  
Зависит от: [09-detail](09-parser-pipeline-detail.md)
Статус: сделана

## Суть проблемы

После `super().process()` почти все парсеры делают один паттерн:

```python
for row_item in self.parsed_items:
    self.add_price_markup(row_item)       # Mim, FourTochki, Poshk, Pioner, STK; Zapaska — make_price_markup
    self.skip_by_min_rest(row_item)       # Mim, FourTochki, Pioner, STK, Zapaska
    self.set_category(row_item)           # Mim, FourTochki; Poshk — set_type_production; Zapaska — get_type_production
    # плюс уникальное: title, manufacturer, fill_from_title
```

Mim base и FourTochki base — **копии** друг друга (ещё и закомментированный `correction_category`). Poshk: markup, `clear_and_set_title`, `prepare_title`, category. Pioner: skip, markup, manufacturer в title, **второй** ManufacturerFinder. Autosnab: `fill_from_title` + identity markup. Zapaska: побочные dict `price_sup_codes`, skip, type, обнуление rest без категории.

Это Template Method, в котором hook — весь цикл, а не «как собрать title». Наценка после этапа 1 должна быть шагом pipeline, не телом subclass.

## Подробное решение

1. Контракт хуков на `BaseParser` (имена можно уточнить):

   - `prepare_title(row)` — уже есть `get_prepared_title` / `set_prepared_title` в enrich;
   - `category_for(row) -> str | None`;
   - `rest_value(row)` — уже `get_item_rest` / `get_min_rest_count`;
   - `after_row_mapped(row)` — редкое уникальное (Poshk strip `, , шт`, Autosnab `fill_from_title`, Pioner manufacturer-in-title).

2. Базовый pipeline после enrich:

   - для каждой строки: vendor `after_row_mapped`, `skip_by_min_rest`, выставить category если хук вернул значение, `add_price_markup`;
   - затем `remove_null_rest`.

3. Снести override `process()` у Mim, FourTochki, Poshk, Pioner, STK, Autosnab, Zapaska **если** их уникальная логика переехала в хуки.

   Zapaska: блок `price_mrp_result` / `price_sup_codes` / `not_matched_position` — проверить тестами, живое ли это. Если мёртвое (никогда не наполняется) — удалить в задаче 13, не тащить в хуки. Если живое — отдельный hook `after_all_rows`.

4. `set_category`: Mim — константа листа («Легковая шина»); FourTochki sheet1 — карта `tire_type`; Poshk — разбор title; Zapaska disk — `"Диск"`, tire — поле строки. Один хук `category_for`.

5. Порядок относительно текущего **поставщика** сохранить там, где есть зависимость (Пионер: `skip_by_min_rest` смотрит category row и выставляет `current_category` — это **stateful** хук на последовательность строк, не чистая функция от одной строки). Для Пионера хук `on_row(row)` с состоянием парсера обязателен; не пытаться сделать его stateless в этом PR.

6. Регрессия: полный набор `tests/test_parsers/test_vendors/**`.

## Ожидаемый результат

- Нет копипасты `for row_item in self.parsed_items: add_price_markup; skip; set_category`.
- `process()` у типичного xls-vendor не переопределён.
- Фикстуры прайсов без изменения строк/цен.
- Наценка вызывается один раз из pipeline.

## Риски

- Пионер: категория из «заголовочных» строк без цены — если фильтр выкинет category-row до хука, сломается manufacturer. Сейчас `is_category_row` живёт в `skip_by_min_rest` на уже собранном `parsed_items` после prepare. Сохранить момент вызова.
- Zapaska обнуляет rest без `type_production` — позиция вылетит в `remove_null_rest`. Порядок: type, потом skip/null rest.
- Двойной ManufacturerFinder у Пионера — чинить в [13](13-parser-dead-code-detail.md), здесь не усиливать.
