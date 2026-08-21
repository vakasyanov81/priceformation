# 03. STK: наценка в JSON — набор задач

Краткая задача: [03-markup-stk.md](../03-markup-stk.md)  
План: [03-markup-stk-detail.md](03-markup-stk-detail.md)

Разбиение этапа 03 на реализуемые тикеты. Порядок: 03.1 → 03.2.  
Статус этапа: **сделана** (все тикеты).

Зависит от [02.3](02-markup-poshk-pioner-tasks.md): STK берёт уже готовый `MapOnOptMarkupPolicy`, новый класс политики не заводить.

Общие ограничения на все тикеты:

- Не включать базовый Mim-алгоритм (РРЦ / min-max recommended / абсолютный пол). У STK нет колонки РРЦ; чужой `min_recommended` из шаблона README уедет цены.
- Не тащить `RowItem` в политику.
- Не заводить `STKParser.markup_policy()` — политику передаёт тот, кто создаёт парсер (`_MAP_ON_OPT_VENDORS` в `common_price`).
- Не трогать `process_parsed_row` / `skip_by_min_rest` / категорию — задача 10.
- Округление по-прежнему только в `BaseParser.round_price`.
- Дефолтная полка должна дать те же цифры, что `opt * 1.06` + `round_price`.
- В JSON STK **не** класть `min_recommended_percent_markup` / `absolute_markup_rules` из шаблона Mim.

---

## 03.1 Пример `stk_markup_rules.json`

**Статус: сделана**

**Зачем.** Провайдер `MarkupRulesProviderFromUserConfig("stk")` уже клеит путь `stk_markup_rules.json`, но файла нет ни в example-конфигах, ни (часто) в пользовательском `parse_config/`. Сейчас это не падает, потому что override считает `* 1.06` и JSON не читает. После 03.2 `make_map_on_opt_markup_policy` начнёт читать файл — без примера будет `PriceRulesConfigFileError`.

**Файлы**

- `tests/parse_config_example/stk_markup_rules.json`
- `integration_tests/parse_config_example/stk_markup_rules.json`
- `README_MarkupRules.md`

`parse_config/` в git не лежит (`.gitignore`). В репозиторий кладём только примеры.

**Сделать**

1. Одна полка на все закупки — эквивалент текущей константы `1.06` (`percent_markup = 0.06`):

```json
{
  "markup_rules": {
    "rule_6": { "min": 0, "max": 999999999, "percent": 0.06 }
  }
}
```

Ключ `percent`, как у Пошка, не `percent_markup`. `max` заведомо больше любой закупочной: слишком узкий `max` отправит дорогие позиции на «минимальный % по карте» (в `markup_percent_for_opt`). Несколько полок можно, **только если** бизнес уже хочет дифференциацию и цифры на текущих фикстурах те же, что `* 1.06`.

2. Не добавлять поля Mim (`min_recommended_percent_markup`, `absolute_markup_rules`). Map-on-opt их игнорирует, но файл не должен выглядеть как Mim-шаблон.

3. В `README_MarkupRules.md` коротко: STK — `stk_markup_rules.json`, карта как у Пошка, сейчас одна полка 6%. Без РРЦ.

4. Напомнить в README / комментарии к задаче миграции: на машине владельца файл нужно положить в `parse_config/stk_markup_rules.json` (скопировать пример), иначе после 03.2 разбор STK упадёт.

**Готово, когда**

- оба example-файла существуют и парсятся той же схемой, что `poshk_markup_rules.json`;
- README упоминает STK;
- в `stk.py` по-прежнему `STK_PRICE_MARKUP_MULTIPLIER = 1.06` (Python ещё не читает карту для цены);
- `tests/test_parsers/test_data_provider/test_markup_rules.py` уже проверяет путь `{supplier}_markup_rules.json` для `"stk"` — не дублировать.

**Не делать:** удаление константы, правка `add_price_markup`, подключение `MapOnOptMarkupPolicy`.

---

## 03.2 Подключить STK к `MapOnOptMarkupPolicy`

**Статус: сделана**

**Зависит от:** 03.1, [02.3](02-markup-poshk-pioner-tasks.md)

**Зачем.** Убрать зашитые +6%. Общий `add_price_markup` уже делегирует в политику; STK нужен тот же map-on-opt, что у Poshk/Pioner, не `make_markup_policy` (Mim).

**Файлы**

- `src/parsers/vendors/stk.py`
- `src/parsers/common_price.py` — `_MAP_ON_OPT_VENDORS`
- `tests/test_parsers/test_vendors/test_stk.py`
- `tests/test_parsers/test_common_price.py` — `test_map_on_opt_vendors_get_map_policy`
- при необходимости тестовый провайдер карты 6% (в `test_stk.py` или `parse_config.py`)

**Сделать**

1. Добавить `STKParser` в `_MAP_ON_OPT_VENDORS` рядом с Poshk/Pioner. Не импортировать STK в `base_parser.py`. Не заводить реестр классов в `make_parser`.

2. Удалить `STK_PRICE_MARKUP_MULTIPLIER` и override `add_price_markup`. Пустой `price_opt`: сейчас early return, `price_markup` не трогается. Базовый метод делает `apply(0)` → `0`. Текущий тест `test_add_price_markup_empty` уже ждёт `0` — сохранить.

3. `percent_markup`: STK его сейчас не пишет. После map-on-opt `percent_to_store` запишет `6.0` (доля с карты × 100 **до** округления). Это правильно: `SetPercentMarkupItemAction` после округления на `opt=1001` дал бы `(1070/1001-1)*100 ≈ 6.89`, не 6. Не отключать запись.

4. Тесты STK: убрать `object.__new__(STKParser)` — без политики базовый `add_price_markup` бросит `MarkupPolicyNotSetError`. Собирать через `make_parser(..., markup_policy=make_map_on_opt_markup_policy(config))` и провайдер с полкой `0.06`.

   Текущие ожидания без изменения:

   - opt=1000 → markup 1060 (1000×1.06, округление не меняет);
   - opt=500, rest=1 → markup 530, rest обнулён.

   Добавить узкий кейс из плана: opt=1001 → 1001×1.06=1061.06 → `ceil` до десятков → **1070**.

5. В `test_map_on_opt_vendors_get_map_policy` добавить `(STKParser, stk_params)`.

**Готово, когда**

- в `stk.py` нет числа `1.06` и нет своего `add_price_markup`;
- `grep STK_PRICE_MARKUP` пуст;
- отпускная на текущих кейсах совпадает с `round_price(opt * 1.06)`;
- смена процента — JSON / тестовый провайдер, без правки Python;
- Mim и остальные vendors без регрессий;
- `uv run pytest` зелёный.

**Не делать:** рефакторинг `process_parsed_row`, перевод Zapaska / Autosnab, подстановка `MarkupPolicy.apply` вместо map-on-opt.
