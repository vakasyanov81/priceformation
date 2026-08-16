# 07. Фабрика `make_parse_config`

Подробно: [07-config-factory-detail.md](details/07-config-factory-detail.md)

Этап: [2. Фабрика конфига поставщика](../PLAN_CLEAN_CODE.md#этап-2-фабрика-конфига-поставщика)  
Статус: не начата  
Зависит от: — (можно параллельно с этапом 1 после стабилизации тестов наценки)  
Дальше: [08. Кэш на экземпляре](08-config-cache.md)

## Зачем

Один и тот же блок `BasePriceParseConfigurationParams` (7 провайдеров) скопирован в 12 vendor-файлах. Ошибка размножается, новый поставщик копирует простыню.

## Сделать

1. `make_parse_config(parser_params) -> ParseConfiguration` с дефолтными провайдерами из `data_provider`.
2. Vendor-файлы оставляют только `ParserParams` и вызов фабрики.
3. Состав поставщиков в `all_vendors.py` не менять; убрать лишние импорты, если конфиг создаётся рядом с params.

## Файлы

- `src/parsers/base_parser/base_parser_config.py`
- все `src/parsers/vendors/**` с `ParseConfiguration(...)`
- `src/parsers/all_vendors.py`

## Готово, когда

- Повторяющийся блок провайдеров встречается один раз.
- Добавление поставщика не копирует 7 строк провайдеров.
- Все vendor-тесты зелёные.

## Не делать

Plugin/entry points, ленивая загрузка vendors, смена `vendor_list.json`. Кэш класса — [08](08-config-cache.md).
