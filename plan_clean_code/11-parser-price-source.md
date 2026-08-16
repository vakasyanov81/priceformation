# 11. PriceSource вместо glob в BaseParser

Подробно: [11-parser-price-source-detail.md](details/11-parser-price-source-detail.md)

Этап: [3. Разрезать BaseParser](../PLAN_CLEAN_CODE.md#этап-3-разрезать-baseparser)  
Статус: не начата  
Зависит от: [09. Pipeline](09-parser-pipeline.md)  
Дальше: [12. JSON reader](12-parser-json-reader.md)

## Зачем

`get_file_prices` / `_glob_price_files` живут в `base_parser.py`. Парсер знает про FS и шаблоны файлов — это адаптер, не домен.

## Сделать

1. Вынести glob в `PriceSource` (файлы по `file_templates` и folder поставщика).
2. Парсер принимает список путей или уже открытый источник; не ходит в FS сам.
3. `SupplierNotHavePricesError` остаётся, если источник пуст.

## Файлы

- `src/parsers/base_parser/base_parser.py`
- `src/core/parse_paths.py` (потребитель путей, не импорт cfg)
- тесты `tests/test_base_parser/test_file_prices.py`

## Готово, когда

- В `BaseParser` нет `Path.glob`.
- Тесты отсутствия прайсов зелёные.

## Не делать

HTTP Zapaska ([15](15-zapaska-http.md)). Не менять раскладку `file_prices/`.
