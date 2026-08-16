# 18. Law of Demeter для ParseConfiguration

Подробно: [18-demeter-detail.md](details/18-demeter-detail.md)

Этап: [4. Слои и побочные эффекты](../PLAN_CLEAN_CODE.md#этап-4-слои-и-побочные-эффекты)  
Статус: не начата  
Зависит от: [07. Фабрика](07-config-factory.md)  
Дальше: — (закрывает [этап 4](../PLAN_CLEAN_CODE.md#этап-4-слои-и-побочные-эффекты))

## Зачем

Цепочки `config.parse_config.parser_params.supplier` (4 уровня) размазаны по `all_vendors`, парсерам и логам. `ParseConfiguration` — дырявая обёртка над NamedTuple.

## Сделать

1. Свойства на `ParseConfiguration`: `parser_params`, `supplier` (folder, name, code).
2. Заменить внешние цепочки на эти свойства.
3. Не тащить весь `NamedTuple` наружу без нужды.

## Файлы

- `src/parsers/base_parser/base_parser_config.py`
- `src/parsers/all_vendors.py`
- `src/parsers/base_parser/base_parser.py`
- вызовы `parse_config.parse_config.parser_params` по `src/`

## Готово, когда

- Нет (или единичные внутренние) цепочек из 4 уровней к `supplier`.
- `grep` по `src/parsers`: нет `from cfg` / `import cfg` (кроме точки входа `run.py`).
- Этап 4 и весь [план](../PLAN_CLEAN_CODE.md) закрыты по критерию готовности.

## Не делать

Переписывание `RowItem`, entry points поставщиков.
