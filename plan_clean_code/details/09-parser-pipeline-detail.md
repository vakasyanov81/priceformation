# 09. Явный pipeline парсера — подробно

Краткая задача: [09-parser-pipeline.md](../09-parser-pipeline.md)  
Зависит от: [06-detail](06-markup-cleanup-detail.md)

## Суть проблемы

Фактический поток `BaseParser.parse`:

1. `is_active` → иначе `[]`;
2. `CategoryFinder()`, glob файлов (`get_file_prices`);
3. `process()`: для каждого файла `type_production` из суффикса имени, `raw_parse` → `to_row_items`, concat; `remove_wo_price_purchase_and_check_title`; `prepare` (`_try_prepare_row`);
4. `after_process`: `remove_null_rest`; `SetPercentMarkupItemAction`;
5. лог статистики.

Наценка **не** в этом pipeline: vendors после `super().process()` ещё раз ходят по `parsed_items` и зовут `add_price_markup` / skip rest / category. `prepare` уже делает title, manufacturer, category correction, spike, season, supplier_name.

Читатель не видит шагов; новый шаг (например единая наценка) снова попадёт в `process` или в 7 override. Задача 09 **именует и выстраивает** шаги в базе, не вынося ещё glob/HTTP (11, 15) и не переписывая все vendor-циклы (10).

## Как сейчас устроено (важно для регрессий)

- `type_production` из `price_file.split("_")[-1]` — для xls-поставщиков с именами `price_tire.xls`; JSON Zapaska перезаписывает тип в своём `process`.
- `prepare` может отбросить строку (title, parse_errors, stop/black).
- `_keep_row_item`: выкинуть rest без opt; выкинуть невалидный title.
- `remove_null_rest`: оставить только тех, у кого и opt, и rest (после skip_by_min_rest rest может стать 0 → вылетит здесь). Поэтому **порядок** «наценка/skip rest → remove_null_rest» критичен. Сейчас skip rest в vendor `process` **до** `after_process.remove_null_rest`. Если перенести наценку в `after_process` до `remove_null_rest`, skip rest должен быть **до** фильтра нулей.

## Подробное решение

1. Явные методы или свободные функции шагов, вызываемые из `parse`:

   - `read_rows(paths) -> list[dict]` (пока внутри: цикл файлов + `raw_parse`);
   - `map_items(dicts) -> list[RowItem]`;
   - `filter_keep(items)`;
   - `enrich(items)` (= нынешний `prepare` / `_enrich_row_item`);
   - `apply_vendor_hooks(items)` — пока пустой hook/`process` subclass, задача 10 заполнит;
   - `apply_markup(items)`;
   - `drop_empty_rest(items)`;
   - `fill_percent_markup(items)` (action).

2. На этом шаге **сохранить** вызов `self.process()` как обёртку над read+map+filter+enrich, чтобы 7 vendor override не сломались. Либо: `process()` по умолчанию = эти шаги без markup; markup отдельным вызовом в `parse` **после** `process()`, если vendor ещё сам наценивает — **нельзя включить двойную наценку**.

   Правило перехода: пока vendors сами зовут `add_price_markup`, база **не** вызывает `apply_markup` в `parse`. Флаг/пустой hook. Задача 10 снимет дубли.

3. Логи start/files/finish не потерять (`LoggerParseProcess`).

4. Тесты `test_base_parser`: тот же набор строк. Не менять сигнатуру `parse()` для `CommonPrice`.

## Ожидаемый результат

- В `base_parser.py` шаги названы; `parse` читается как сценарий.
- Никакой смены цифр vendor-фикстур.
- Двойной наценки нет.
- Формул наценки в `BaseParser` по-прежнему нет (политика).

## Риски

- Переставить skip rest и `remove_null_rest` — исчезнут/появятся позиции с rest=0.
- Включить `apply_markup` в базу до снятия vendor-циклов — цены ×2 или override+base.
- `type_production` из имени файла: не выкидывать, пока Zapaska/xls завязаны.
