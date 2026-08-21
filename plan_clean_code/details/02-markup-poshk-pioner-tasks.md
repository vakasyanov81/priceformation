# 02. Poshk / Pioner на общую политику — набор задач

Краткая задача: [02-markup-poshk-pioner.md](../02-markup-poshk-pioner.md)  
План: [02-markup-poshk-pioner-detail.md](02-markup-poshk-pioner-detail.md)

Разбиение этапа 02 на реализуемые тикеты. Порядок: 02.1 → 02.2 → 02.3.  
Статус этапа: **сделана** (все тикеты).

Общие ограничения на все тикеты:

- Не включать базовый Mim-алгоритм (РРЦ / min-max recommended / абсолютный пол) для Пошка и Пионера.
- Не тащить `RowItem` в политику.
- Не заводить `PoshkParser.markup_policy()` / `PionerParser.markup_policy()` — политику передаёт тот, кто создаёт парсер.
- Не трогать `process()` кроме вызова наценки: title Пошка, категория, skip rest и manufacturer Пионера — задачи 10 и 13.
- Округление по-прежнему только в `BaseParser.round_price`. `apply` возвращает цену **до** округления.
- Сохранить текущие `price_markup` и `percent_markup` в vendor-тестах.

---

## 02.1 Класс `MapOnOptMarkupPolicy`

**Статус: сделана**

**Зачем.** Пошок и Пионер считают отпускную как `get_markup(opt, карта%)`. Если подставить обычный `MarkupPolicy.apply`, пустая РРЦ и абсолютный пол пересчитают все позиции. Нужен отдельный тип с тем же входом `apply(opt, recommended)`, без флага `use_recommended`.

**Файлы**

- `src/parsers/base_parser/markup_policy.py`
- `tests/test_base_parser/test_markup_policy.py`

**Сделать**

1. Класс-наследник (тот же конструктор `rules` + `price_map`, чтобы `make_parser` не менял контракт):

```python
class MapOnOptMarkupPolicy(MarkupPolicy):
    def apply(self, price_opt: float, price_recommended: float | None) -> float:
        """Отпускная до округления: только карта % на закуп. РРЦ и absolute игнорируются."""
        opt = price_opt or 0
        return get_markup(opt, self.markup_percent_for_opt(opt))
```

`price_opt or 0` — как у Пионера. `markup_percent_for_opt` уже даёт default при `opt == 0` и при пустой карте.

2. Не писать `percent_markup` и не трогать `BaseParser` / vendors. Не добавлять фабрику, пока её некуда вызывать (иначе vulture).

**Готово, когда**

- `apply(100, None)` при правиле `0..201 → 0.7` даёт `170` (ещё не округлённое).
- `apply(100, 9999)` при тех же правилах тоже `170` (РРЦ игнорируется).
- При `min_absolute`, который у Mim сработал бы, `MapOnOptMarkupPolicy` всё равно возвращает цену с карты.
- `apply(0, None)` → `0`.
- Vendors без изменений; Mim-тесты зелёные.

**Не делать:** запись `percent_markup`, удаление override у Poshk/Pioner, правки `make_parser`.

---

## 02.2 Запись `percent_markup` из карты

**Статус: сделана**

**Зависит от:** 02.1

**Зачем.** Пошок и Пионер пишут `percent_markup = map% * 100` **до** округления. `SetPercentMarkupItemAction` считает `(price_markup / price_opt - 1) * 100` **после** округления — сотые могут разъехаться. Фикстуры ждут значение с карты (`25.0` у Пошка, `5` у Пионера, `0` при пустых правилах). Политика не знает `RowItem`; запись — в делегате парсера.

**Файлы**

- `src/parsers/base_parser/markup_policy.py`
- `src/parsers/base_parser/base_parser.py`
- `tests/test_base_parser/test_markup_policy.py`
- узкий тест делегата (без vendor-парсера), если нужно покрыть запись в `RowItem`

**Сделать**

1. У `MapOnOptMarkupPolicy` метод `stored_percent_markup(opt) -> float` = `map% * 100`. На базовом `MarkupPolicy` хук со stub `return None` нельзя: WPS324.

2. Рядом с политикой, не в парсере:

```python
def percent_to_store(policy: MarkupPolicy, price_opt: float) -> float | None:
    if isinstance(policy, MapOnOptMarkupPolicy):
        return policy.stored_percent_markup(price_opt)
    return None
```

3. `BaseParser.add_price_markup` после `round_price`:

```python
percent = percent_to_store(policy, opt)
if percent is not None:
    row_item.percent_markup = percent
```

Для Mim `percent_to_store` остаётся `None` — `SetPercentMarkupItemAction` как сейчас.

**Готово, когда**

- Mim: `percent_markup` по-прежнему из action после округления (фикстуры sheet1/sheet2).
- `MapOnOptMarkupPolicy.stored_percent_markup(100)` при `0.7` → `70`.
- Vendors ещё со своим `add_price_markup` (поведение прайса не меняется).

**Не делать:** удаление override у Poshk/Pioner.

---

## 02.3 Подключить Poshk и Pioner

**Статус: сделана**

**Зависит от:** 02.2

**Зачем.** Убрать две копии формулы. Общий `add_price_markup` уже делегирует в `_markup_policy`; этим поставщикам нужна `MapOnOptMarkupPolicy` в конструкторе.

**Файлы**

- `src/parsers/base_parser/markup_policy.py` — `make_map_on_opt_markup_policy`
- `src/parsers/base_parser/base_parser.py` — `make_parser` не импортирует vendors
- `src/parsers/common_price.py` и/или `src/parsers/all_vendors.py` — composition root
- `src/parsers/vendors/poshk.py`, `src/parsers/vendors/pioner.py`
- `tests/test_parsers/test_vendors/test_parse_poshk.py`
- `tests/test_parsers/test_vendors/test_parse_pioner.py`

**Сделать**

1. Фабрика рядом с `make_markup_policy`:

```python
def make_map_on_opt_markup_policy(parse_config: ParseConfiguration) -> MapOnOptMarkupPolicy:
    return MapOnOptMarkupPolicy(
        rules=parse_config.get_markup_rules(),
        price_map=parse_config.get_price_markup_map(),
    )
```

2. Выбор политики — **вне** `BaseParser` и **вне** subclass. Не импортировать Poshk/Pioner в `base_parser.py` (цикл, лишний импорт). Варианты:

   - в `_parser_for_vendor` / `all_vendors` отдать `make_parser(..., markup_policy=make_map_on_opt_markup_policy(config))` для этих двух классов;
   - в тестах `get_fake_parser` / `_parser_with_markup` — то же явно.

   Реестр классов в `make_parser` **не** заводить: `base_parser` не должен знать vendors.

3. Удалить `add_price_markup` у `PoshkParser` и `PionerParser`. В `process_parsed_row` оставить `self.add_price_markup(row_item)` — пойдёт в базу.

4. Тесты vendor: snapshot `price_markup` / `percent_markup` без изменения. Узкий кейс из плана: opt=100, правило `0..201` / `0.7` → округлённый markup `170` (у Пошка в `test_markup` уже есть `(100, 170)`).

**Готово, когда**

- в `poshk.py` и `pioner.py` нет формулы `(percent + 1) * price` и нет своего `add_price_markup`;
- смена диапазона в JSON по-прежнему меняет отпускную без правки Python;
- `test_add_price_markup_without_opt_stays_zero` и `test_add_price_markup_empty_rules_keeps_opt` зелёные;
- Mim и остальные vendors без регрессий;
- `uv run pytest` зелёный.

**Не делать:** рефакторинг title/category Пошка, skip rest / manufacturer Пионера, перевод STK / Zapaska / Autosnab.
