# 08. Кэш наценки на экземпляре

Подробно: [08-config-cache-detail.md](details/08-config-cache-detail.md)

Этап: [2. Фабрика конфига поставщика](../PLAN_CLEAN_CODE.md#этап-2-фабрика-конфига-поставщика)  
Статус: не начата  
Зависит от: [07. Фабрика](07-config-factory.md)  
Дальше: этап 3 — [09. Pipeline](09-parser-pipeline.md)

## Зачем

`ParseConfiguration._markup_rules` и `_price_markup_map` объявлены на классе. Повторный `parse()` разных vendors в одном процессе может делить чужой кэш. Integration-тест сбрасывает поле вручную.

## Сделать

1. Кэш — атрибуты **экземпляра**, инициализация в `__init__`.
2. Убрать ручной сброс в integration-тестах, если он больше не нужен.
3. Тест: два `ParseConfiguration` с разными markup provider не делят правила.

## Файлы

- `src/parsers/base_parser/base_parser_config.py`
- `integration_tests/test_four_tochki_real_price.py`
- тесты конфига `tests/test_base_parser/` или `tests/test_parsers/test_data_provider/`

## Готово, когда

- Повторный `parse()` разных vendors не делит чужой кэш наценки.
- Этап 2 закрыт: [план](../PLAN_CLEAN_CODE.md#этап-2-фабрика-конфига-поставщика).

## Не делать

Смена схемы JSON, ленивый import vendors.
