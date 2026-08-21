# 02. Poshk / Pioner на общую политику — подробно

Краткая задача: [02-markup-poshk-pioner.md](../02-markup-poshk-pioner.md)  
Зависит от: [01-detail](01-markup-policy-detail.md)

## Суть проблемы

`PoshkParser.add_price_markup` и `PionerParser.add_price_markup` — почти один текст:

```text
price = price_opt (у Пионера: or 0)
percent = get_markup_percent(price)
price = (percent + 1) * price
price_markup = round_price(price)
percent_markup = percent * 100
```

Это **не** базовый алгоритм Mim (`MarkupPolicy` из задачи 01): РРЦ, min/max recommended и абсолютный пол **игнорируются**. Используется только карта `%` из JSON (`poshk_markup_rules.json` / pioner-файл) и округление до десятков.

Две копии той же формулы. При выравнивании округления или записи `percent_markup` правки нужны в двух классах. Оба override **затеняют** `BaseParser.add_price_markup`, поэтому даже после задачи 01 эти поставщики не получат `MarkupPolicy`, пока override не убрать или не заменить.

Отличие Пионера от Пошка: `price_opt or 0` (защита от None); у Пошка `price_opt` идёт в умножение как есть. Поля `percent_markup` оба пишут сами; базовый Mim пишет `percent_markup` позже через `SetPercentMarkupItemAction` в `after_process`. Если у Poshk/Pioner `percent_markup` уже заполнен, action **не** пересчитает его (`already_calculated`).

JSON Пошка (пример тестов) — только `markup_rules` с `percent`, без recommended/absolute. Поведение «карта % на закуп» совпадает с тем, что даёт `get_markup_percent` + `get_markup`.

## Как сейчас устроено

- Оба в `process()` после `super().process()`: цикл по `parsed_items`, у Пошка ещё title/category, у Пионера skip rest, manufacturer, повторный `ManufacturerFinder`.
- Карта % читается через унаследованный `get_markup_percent` → `parse_config.get_price_markup_map()`.
- Формула `(percent + 1) * price` тождественна `price_markup.get_markup(price, percent)`.

## Подробное решение

1. Ввести в политике (или рядом) явный режим **«только карта на закуп»**:  
   `apply_map_on_opt(price_opt) -> float` = `get_markup(opt, markup_percent_for_opt(opt))`.  
   Не подставлять сюда recommended/absolute — иначе изменятся цены Пошка/Пионера.

   Альтернатива без нового метода: параметр политики `use_recommended: bool = True`; для этих vendors `False`. Предпочтительнее **явный метод/класс** `MapOnOptMarkupPolicy`, чтобы не плодить флаги.

2. `add_price_markup` у Poshk и Pioner удалить. В цикле `process()` вызывать тот же вход, что будет у всех (пока: `self.add_price_markup(row_item)` на базе). Политику map-on-opt передаёт тот, кто создаёт парсер, не subclass.

   Минимальный путь без выбора стратегии в BaseParser:

   - в конструктор Poshk/Pioner передавать `MapOnOptMarkupPolicy` (тот же `make_parser(..., markup_policy=...)`, что в задаче 01.4);
   - общий `BaseParser.add_price_markup` уже делегирует в `self._markup_policy` (задача 01).
   - **не** заводить `PoshkParser.markup_policy()` — парсер снова станет фабрикой.

3. `percent_markup`: либо оставить запись в политике/делегате (`percent * 100`), либо положиться на `SetPercentMarkupItemAction`. Сверить фикстуры: Пошок пишет `percent * 100` **до** округления цены; action считает `(price_markup / price_opt - 1) * 100` **после** округления — цифры могут разъехаться на сотые. **Сохранить текущие значения фикстур.** Если тесты ждут `percent_markup` как `map% * 100`, писать его явно в политике map-on-opt, не через action.

4. Тесты: `test_parse_poshk.py` и pioner — snapshot/ожидаемые `price_markup` без изменения. Добавить узкий тест: opt=100 в диапазоне 0–201 при percent=0.7 → markup округлённый `ceil(170/10)*10=170`.

5. Не трогать `process()` кроме вызова наценки: title Пошка, категория из title, skip rest и manufacturer Пионера — задачи 10 и 13.

## Ожидаемый результат

- В `poshk.py` и `pioner.py` нет формулы `(percent + 1) * price`.
- Цены и `percent_markup` в vendor-тестах те же.
- Смена диапазона в `poshk_markup_rules.json` по-прежнему меняет отпускную цену без правки Python.
- Базовый Mim-алгоритм на этих поставщиков **не** включается (нет подмены на РРЦ/absolute).

## Риски

- Смешать с `MarkupPolicy.apply` из задачи 01 → Пошок начнёт учитывать пустую РРЦ как «маленький %» и пересчитает все позиции. Обязателен отдельный режим map-on-opt.
- Пионер: `price_opt` пустой; сейчас `or 0`, затем markup 0. Сохранить.
