# 10. Хуки vendors вместо циклов `process()`

Подробно: [10-parser-hooks-detail.md](details/10-parser-hooks-detail.md)

Этап: [3. Разрезать BaseParser](../PLAN_CLEAN_CODE.md#этап-3-разрезать-baseparser)  
Статус: сделана  
Зависит от: [09. Pipeline](09-parser-pipeline.md)  
Дальше: [11. PriceSource](11-parser-price-source.md)

## Зачем

Mim и FourTochki копируют один цикл; Poshk/Pioner/STK/Autosnab/Zapaska — каждый свой, с одними шагами (markup, skip rest, category).

## Сделать

1. Хук поставщика: title, category, rest (min count / резерв Пионера).
2. Убрать копипасту `for row_item in self.parsed_items: add_price_markup; skip_by_min_rest; set_category`.
3. Перевести Mim, FourTochki, Poshk, Pioner, STK, Autosnab, Zapaska на хуки.

## Файлы

- `src/parsers/vendors/mim/mim_base.py`
- `src/parsers/vendors/four_tochki/four_tochki_base.py`
- `src/parsers/vendors/poshk.py`, `pioner.py`, `stk.py`, `autosnab54_ru.py`
- `src/parsers/vendors/zapaska_disk_json.py`
- vendor-тесты `tests/test_parsers/test_vendors/`

## Готово, когда

- Vendors без копипасты общего цикла по `parsed_items`.
- Фикстуры прайсов без регрессий.

## Не делать

HTTP Zapaska, смена колонок и шаблонов XLSX.
