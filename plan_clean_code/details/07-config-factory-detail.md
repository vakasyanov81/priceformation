# 07. Фабрика `make_parse_config` — подробно

Краткая задача: [07-config-factory.md](../07-config-factory.md)  
План: [этап 2](../../PLAN_CLEAN_CODE.md#этап-2-фабрика-конфига-поставщика)  
Статус: сделана

## Суть проблемы

Каждый vendor-модуль (Poshk, Pioner, STK, Autosnab, Zapaska disk/tire, Mim ×3 sheet, FourTochki ×2 sheet — **12 мест**) копирует:

```python
ParseConfiguration(
    BasePriceParseConfigurationParams(
        markup_rules_provider=MarkupRulesProviderFromUserConfig(folder_or_name),
        black_list_provider=BlackListProviderFromUserConfig(),
        stop_words_provider=StopWordsProviderFromUserConfig(),
        vendor_list=VendorListProviderFromUserConfig(),
        manufacturer_aliases=ManufacturerAliasesProviderFromUserConfig(),
        parser_params=...,
    )
)
```

Различается только `parser_params` и аргумент markup-провайдера (folder поставщика). Black list, stop words, vendor list, aliases — **общие на всех**. Опечатка в одном файле (забыли aliases) даёт тихий другой набор данных.

`all_vendors()` импортирует все эти модули ради `(ParserClass, config)` — side effect: на import создаются провайдеры и `ParseConfiguration`, читающие диск позже, при первом `get_*`.

Новый поставщик сегодня: скопировать 15 строк, не забыть 5 провайдеров. Это нарушение OCP/DRY.

## Как сейчас устроено

- `ParserParams` — колонки, start_row, folder, templates, `row_item_adaptor`.
- Mim/FourTochki: `dataclasses.replace(base_params)` + sheet_indexes/columns, затем **ещё один** полный `ParseConfiguration(...)`.
- Markup provider: `MarkupRulesProviderFromUserConfig(supplier.folder_name)` — файл `{folder}_markup_rules.json`.

## Подробное решение

1. Функция в `base_parser_config.py`:

```python
def make_parse_config(
    parser_params: ParserParams,
    *,
    markup_rules_provider: MarkupRulesProviderBase | None = None,
    black_list_provider: BlackListProviderBase | None = None,
    # ... остальные с None = дефолт FromUserConfig
) -> ParseConfiguration:
```

Дефолт markup: `MarkupRulesProviderFromUserConfig(parser_params.supplier.folder_name)`.

2. Заменить 12 блоков на `*_config = make_parse_config(*_params)` (для sheet — `make_parse_config(mim_sheet_1_params)`).

3. Не менять состав `all_vendors()` (те же 11 пар class+config). Можно реэкспортировать конфиги как сейчас.

4. Тест: `make_parse_config(params).parse_config.parser_params is params`; markup provider привязан к `folder_name`; подмена одного провайдера через kwarg работает (для юнит-тестов без диска).

5. Не делать entry points и ленивый import списка vendors.

## Ожидаемый результат

- Единственное место, где перечисляются 5 дефолтных провайдеров.
- Vendor-файл: `ParserParams` + `make_parse_config` + class парсера.
- Все существующие parse-тесты зелёные без смены фикстур.

## Риски

- Zapaska tire и disk: **разные** `ParserParams` (folder оба `zapaska`, разные code/name/templates). Фабрика по `folder_name` даст **один** JSON наценок на обоих — так и сейчас (`zapaska_markup_rules.json`). Не сломать.
- Mim sheet1–3 делят folder `mim` — один JSON, ок.
- Случайно передать `supplier.name` вместо `folder_name` в markup provider (сейчас folder). Сохранить folder.
