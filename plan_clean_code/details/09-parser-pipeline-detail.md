# 09. Явный pipeline парсера — подробно

Краткая задача: [09-parser-pipeline.md](../09-parser-pipeline.md)  
План: [этап 3](../../PLAN_CLEAN_CODE.md#этап-3-разрезать-baseparser)  
Статус: сделана  
Зависит от: [06-detail](06-markup-cleanup-detail.md) (сделана). Этап 2 ([07](07-config-factory-detail.md), [08](08-config-cache-detail.md)) закрыт.

## Что уже не так, как в исходном плане 09

Исходная формулировка опиралась на семь override `process()` и наценку **вне** базового потока (`super().process()`, затем цикл по `parsed_items`). Это устарело после этапа 1:

- `process()` переопределяет **только** `BaseParser`. Mim / FourTochki / STK / Poshk / Pioner / Autosnab / Zapaska **не** копируют цикл файлов.
- Наценка уже в базе: после `prepare` вызывается `_process_parsed_items()` → хук `process_parsed_row`.
- `MarkupSkipCategoryParser` (Mim, FourTochki, STK): markup + `skip_by_min_rest` + `set_category`.
- Остальные vendors переопределяют только `process_parsed_row` (Poshk, Pioner, Autosnab, Zapaska disk; tire наследует disk).
- `prepare` / фильтр уже вынесены: `_try_prepare_row`, `_enrich_row_item`, `_keep_row_item` в `base_parser_row.py`.
- Политика наценки инжектится через `make_parser` / `markup_policy`; `add_price_markup` — делегат (исключение: Mim sheet2 со своим override грузовых %).
- Glob уже модульные функции `_glob_price_files` / `get_file_prices`, не методы класса. Вынос в `PriceSource` — задача [11](11-parser-price-source-detail.md).
- Zapaska **не** перезаписывает `process()`: JSON читает в `raw_parse`, тип — в `process_parsed_row` (`get_type_production` / `_type_production`).

Задача 09 **не** изобретает хук и **не** переносит наценку в отдельный шаг `parse` (это [10](10-parser-hooks-detail.md)). Она именует оркестрацию, которая сейчас спрятана в `parse` + одном `process()`.

## Суть проблемы

Фактический поток `BaseParser.parse`:

1. `is_active` → иначе `[]` и лог disable;
2. `CategoryFinder()`, `self.files = self.files or get_file_prices(self)`;
3. `process()`:
   - лог списка файлов;
   - для каждого файла `type_production` из суффикса имени (`price_file.split("_")[-1]`), `raw_parse` → `to_row_items`, concat;
   - `remove_wo_price_purchase_and_check_title` (`_keep_row_item`);
   - `prepare` (`_try_prepare_row` → title / parse_errors / stop-black, затем `_enrich_row_item`);
   - `_process_parsed_items` → `process_parsed_row` (наценка, skip rest, category — **у subclass**);
4. `after_process`: `remove_null_rest`; `SetPercentMarkupItemAction`;
5. лог статистики (`LoggerParseProcess`).

`parse` / `process` по-прежнему читаются как два комка, а не как сценарий шагов. Новый шаг снова попадёт внутрь `process` или в `process_parsed_row`. Задача 09 именует и выстраивает шаги в базе, не вынося glob/HTTP (11, 15), JSON-reader (12) и не дробя vendor-хуки (10).

## Как сейчас устроено (важно для регрессий)

- `type_production` из имени файла — для xls с именами вроде `price_tire.xls`. Тест `test_base_parser_process.py` фиксирует суффикс последнего файла (`disks.xls`). Не выкидывать, пока xls завязаны. Zapaska задаёт тип строки в хуке, не в `process()`.
- `prepare` может отбросить строку (title, parse_errors, stop/black).
- `_keep_row_item`: выкинуть rest без opt; выкинуть невалидный title.
- `_process_parsed_items` идёт **после** `prepare`, **до** `after_process`.
- `remove_null_rest`: оставить только тех, у кого и opt, и rest (после `skip_by_min_rest` rest может стать 0 → вылетит здесь). Поэтому порядок «хук (наценка/skip rest) → `remove_null_rest`» критичен и **уже соблюдён**. Не переставлять.
- Skip rest **не** общий: Poshk и Autosnab его не зовут; Autosnab `get_min_rest_count() == 0`. Не включать `skip_by_min_rest` в базовый шаг 09 — иначе изменятся остатки Poshk.
- `process()` возвращает сумму длин сырых `to_row_items` **до** фильтров. `test_process_sums_rows_from_two_files` и `test_process_without_files_returns_zero` завязаны на это.
- Zapaska: `make_price_markup` (политика + round), не `add_price_markup`. Если в `parse` добавить общий `apply_markup` → `add_price_markup`, будет **двойная** наценка у Zapaska.
- Mim sheet2 override `add_price_markup` (грузовой %). Любой именованный шаг наценки должен идти через **instance** `self.add_price_markup`, не через `BaseParser.add_price_markup` напрямую. В 09 отдельный шаг наценки в `parse` **не включать**.
- Сигнатура `parse() -> list[RowItem]` для `CommonPrice.parse_vendor` не менять.

## Подробное решение

1. Явные методы или свободные функции шагов, вызываемые из `parse` / тонкой обёртки `process`. Опереться на уже существующие имена, не плодить параллельный словарь:

   - `read_rows(paths) -> list[dict]` (пока внутри: цикл файлов + `raw_parse`; glob остаётся `get_file_prices`);
   - `map_items(dicts) -> list[RowItem]` (= `to_row_items`);
   - `filter_keep(items)` (= `remove_wo_price_purchase_and_check_title` / `_keep_row_item`);
   - `enrich(items)` (= `prepare` / `_try_prepare_row` / `_enrich_row_item`);
   - `apply_vendor_hooks(items)` (= уже существующие `_process_parsed_items` / `process_parsed_row`; **не** пустой stub — vendors заполнены);
   - `drop_empty_rest(items)` (= `remove_null_rest`);
   - `fill_percent_markup(items)` (= `SetPercentMarkupItemAction` / `do_items_actions_after_process`).

   Отдельный `apply_markup` в `parse` **не** добавлять: наценка живёт в `process_parsed_row` до задачи 10.

2. Сохранить `process()` как обёртку над read+map+filter+enrich+vendor hook, чтобы не ломать `test_base_parser_process.py` и не тащить 10. `after_process` — drop empty rest + percent action, как сейчас.

3. Логи start / files / finish не потерять (`LoggerParseProcess`). `log_list_files` остаётся на шаге чтения.

4. Тесты `tests/test_base_parser/`: тот же набор строк (`test_base_parser_process.py`, `test_row_filters.py`, вендорные фикстуры без регрессий). Не менять сигнатуру `parse()` для `CommonPrice`.

5. Не трогать кэш `ParseConfiguration` (08), фабрику `make_parse_config` (07), формулы политик и Mim sheet2.

## Ожидаемый результат

- В `base_parser.py` шаги названы; `parse` читается как сценарий.
- Никакой смены цифр vendor-фикстур.
- Двойной наценки нет (нет второго вызова markup в `parse` поверх хука).
- Формул наценки в `BaseParser` по-прежнему нет (политика). `process_parsed_row` / `MarkupSkipCategoryParser` без изменений контракта.

## Риски

- Переставить skip rest и `remove_null_rest` — исчезнут/появятся позиции с rest=0.
- Включить `apply_markup` в `parse` до снятия markup из `process_parsed_row` — цены ×2 (особенно Zapaska: `make_price_markup` + `add_price_markup`).
- Общий `skip_by_min_rest` в базе — Poshk/Autosnab изменят остатки.
- `type_production` из имени файла: не выкидывать; тест суффикса `disks.xls`.
- Сменить возвращаемое значение `process()` (счётчик до фильтров) — упадут юнит-тесты цикла файлов.
