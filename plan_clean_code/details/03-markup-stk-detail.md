# 03. STK: наценка в JSON — подробно

Краткая задача: [03-markup-stk.md](../03-markup-stk.md)  
Задачи: [03-markup-stk-tasks.md](03-markup-stk-tasks.md)  
Зависит от: [01-detail](01-markup-policy-detail.md), [02-detail](02-markup-poshk-pioner-detail.md) (нужен `MapOnOptMarkupPolicy`)  
Статус: сделана

## Суть проблемы

STK не использует карту из `stk_markup_rules.json` для отпускной цены. В коде:

```python
STK_PRICE_MARKUP_MULTIPLIER = 1.06
# ...
row_item.price_markup = self.round_price(row_item.price_opt * STK_PRICE_MARKUP_MULTIPLIER)
```

Это фиксированные **+6%** к закупу, затем округление до десятков. `MarkupRulesProviderFromUserConfig("stk")` всё равно создаётся — файл либо есть и **игнорируется** для цены, либо отсутствует и падает только если его реально читают. Смена процента для бизнеса требует релиза Python, хотя для Mim/Poshk процент уже в JSON.

`STKParser.process`: `skip_by_min_rest`, затем свой `add_price_markup`. Пустой `price_opt` — early return, `price_markup` не трогается (потом `remove_null_rest` в `after_process` выкинет строку без opt/rest).

## Как сейчас устроено

- `1.06` = множитель, не доля. Эквивалент `percent_markup = 0.06` в терминах `get_markup(opt, 0.06)` = `opt * 1.06`.
- Округление то же, что у всех: `ceil(x/10)*10`.
- РРЦ у STK в колонках нет (только code, title, opt, rest).

## Подробное решение

1. Завести/обновить `parse_config/stk_markup_rules.json` (и зеркало в `tests/parse_config_example/`, `integration_tests/parse_config_example/`, если STK гоняется с example-конфигом).

   Минимальный эквивалент текущей константы — одна полка на все цены:

   ```json
   {
     "markup_rules": {
       "rule_6": { "min": 0, "max": 999999999, "percent": 0.06 }
     }
   }
   ```

   `max` взять заведомо больше любой закупочной; либо несколько полок, если бизнес уже хочет дифференциацию — **но дефолт должен дать те же цифры, что 1.06**.

2. Удалить `STK_PRICE_MARKUP_MULTIPLIER` и override `add_price_markup`.

3. Политика: тот же **map-on-opt**, что у Poshk ([02](02-markup-poshk-pioner-detail.md)), не Mim-recommended. STK без РРЦ; если включить базовый `apply`, пустая РРЦ + `min_recommended` из чужого/пустого JSON может уехать.

4. Если файла STK ещё нет в прод-`parse_config/`, добавить его в репозиторий-пример и в README_MarkupRules (коротко: STK — карта как у Пошка, сейчас одна полка 6%).

5. Тесты `test_stk.py`: те же `price_markup`. Узкий тест: opt=1000 → 1060 (1000*1.06=1060, округление не меняет). opt=1001 → 1061 → ceil → 1070.

6. Проверить, что провайдер реально читает `stk_markup_rules.json` (не общий `markup_rules.json`): `MarkupRulesProviderFromUserConfig` при `supplier_name` клеит `{supplier}_{file}`.

## Ожидаемый результат

- В `stk.py` нет числа 1.06.
- Отпускная цена на текущих фикстурах совпадает с `round(opt * 1.06)`.
- Правка процента — JSON, без Python.
- `grep STK_PRICE_MARKUP` пуст.

## Риски

- Слишком узкий `max` в JSON → цены выше полки упадут на «минимальный % по карте» (в `get_markup_percent`). Одна полка с огромным max безопаснее.
- Случайно подключить Mim-политику с `min_recommended` / absolute из шаблона README — цены уедут.
- Нет файла в пользовательском `parse_config/` на машине владельца — `PriceRulesConfigFileError`. Положить пример и упомянуть в задаче миграции конфига.
