# 18. Law of Demeter для ParseConfiguration — подробно

Краткая задача: [18-demeter.md](../18-demeter.md)  
Зависит от: [07-detail](07-config-factory-detail.md)

## Суть проблемы

`ParseConfiguration` хранит `self.parse_config: BasePriceParseConfigurationParams` (NamedTuple провайдеров + `parser_params`). Снаружи:

```text
config.parse_config.parser_params.supplier.code
self.parse_config().parse_config.parser_params.start_row
parse_config.parse_config.parser_params.supplier.name
```

Цепочка: объект → tuple провайдеров → params → supplier → поле. Закон Деметры: не ходить по внутренностям друзей. Имя `parse_config.parse_config` дублирует смысл.

Известные места в `src/`:

- `all_vendors.all_vendor_supplier_info` — `config.parse_config.parser_params.supplier.code/name`;
- `BaseParser.parser_params()` уже прячет один уровень, но `prepare` всё ещё пишет `self.parse_config().parse_config.parser_params.start_row`;
- `zapaska_disk_json` — `parse_config.parse_config.parser_params` в `__init__` и `raw_parse`.

После фабрики (07) создание конфига проще, но чтение всё ещё дырявое. Закрытие этапа 4: адаптеры не знают NamedTuple.

Финальный grep плана: в `src/parsers` нет `from cfg` / `import cfg` (кроме допустимого отсутствия — `run.py` не в parsers). Задачи 14–16 должны это сделать; 18 — проверка и Demeter. Если импорт cfg ещё есть — не маскировать свойствами, а закрыть хвосты 14–16.

## Подробное решение

1. Свойства:

```python
class ParseConfiguration:
    @property
    def parser_params(self) -> ParserParams:
        return self.parse_config.parser_params

    @property
    def supplier(self) -> ParseParamsSupplier:
        return self.parser_params.supplier
```

Внутри класса доступ к провайдерам может остаться `self.parse_config.markup_rules_provider` — это своя внутренность. Снаружи NamedTuple не торчать. Со временем переименовать поле `parse_config` → `_params` (больше шума, опционально в этом PR если grep маленький).

2. `BaseParser.parser_params()` → `return self.parse_config().parser_params` (без `.parse_config`).

3. `all_vendors`: `config.supplier.code`, `config.supplier.name`.

4. Запрет в code review / при желании простой тест AST не обязателен: `rg "parse_config\.parser_params" src`.

5. Не проксировать все провайдеры без нужды; `black_list()` уже есть.

## Ожидаемый результат

- Нет цепочек `.parse_config.parser_params.supplier` снаружи `ParseConfiguration`.
- `rg "from cfg|import cfg" src/parsers` — пусто.
- Поведение прайсов без изменений.
- План Clean Code по критерию готовности закрыт: vendors — mapping/хуки; наценка — политика; I/O — порты.

## Риски

- Переименовать публичное `.parse_config` сломает тесты, которые собирают `ParseConfiguration` и читают `.parse_config.parser_params`. Обновить тесты или оставить поле, добавив свойства.
- Не тащить `RowItem` и writer в этот PR.
