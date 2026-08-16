# 14. Writer без cfg и без I/O в конструкторе

Подробно: [14-writer-layers-detail.md](details/14-writer-layers-detail.md)

Этап: [4. Слои и побочные эффекты](../PLAN_CLEAN_CODE.md#этап-4-слои-и-побочные-эффекты)  
Статус: не начата  
Зависит от: [11. PriceSource](11-parser-price-source.md) (пути уже через порты)  
Дальше: [15. HTTP Zapaska](15-zapaska-http.md)

## Зачем

`xls_writer.py` делает `from cfg import init_cfg` и `config = init_cfg()` на импорте. Конструктор `XlsWriter` сам создаёт папку и пишет файл. Adapters не должны импортировать композиционный корень.

## Сделать

1. Путь результата — `get_parse_paths()` или явный аргумент, не `cfg`.
2. Убрать `init_cfg()` с уровня модуля.
3. Не писать workbook в `__init__`; `write()` / фабрика вызывается из `CommonPriceOut`.

## Файлы

- `src/parsers/writer/xls_writer.py`
- `src/parsers/common_price_output.py`
- `tests/test_parsers/test_writer/`

## Готово, когда

- Импорт `parsers.writer.xls_writer` не вызывает `init_cfg()`.
- В `src/parsers/writer` нет `from cfg`.
- Тесты writer зелёные.

## Не делать

Смена шаблонов inner/drom, HTTP Zapaska.
