# 01. Вынести MarkupPolicy — подробно

Краткая задача: [01-markup-policy.md](../01-markup-policy.md)  
План: [этап 1](../../PLAN_CLEAN_CODE.md#этап-1-единая-политика-наценки)  
Задачи: [01-markup-policy-tasks.md](01-markup-policy-tasks.md)

## Суть проблемы

Наценка — центральное бизнес-правило продукта (отпускная цена в общем прайсе и для drom). Сейчас оно живёт не в одном месте.

1. **Арифметика** вынесена в `price_markup.py` (`calc_percent`, `get_markup`) — это только ` (sale-opt)/opt ` и ` opt*(1+percent) `.
2. **Политика** (когда брать РРЦ, когда карту процентов, когда абсолютный пол) сидит методами в `BaseParser`: `get_markup_percent`, `recommended_percent_markup`, `is_small_recommended_percent`, `is_big_recommended_percent`, `is_small_absolute_markup`, `get_price_with_absolute_rule_markup`, `add_price_markup`, плюс `round_price`.
3. **Поставщики** либо вызывают этот метод из своего `process()`, либо **полностью подменяют** формулу (Poshk, Pioner, STK, Zapaska, Autosnab, FourTochki sheet1).

Итог: `BaseParser` — God-object. Чтобы понять «какая будет цена», нужно читать базовый класс **и** subclass. JSON `*_markup_rules.json` описывает правила, но часть vendors его не использует. Тесты `test_price_markup.py` проверяют только две чистые функции, не политику.

Задача 01 **не** переводит поставщиков. Она вынимает **базовый** алгоритм (тот, что в `add_price_markup`) в отдельный объект, чтобы следующие задачи подключались к нему, а не копировали методы парсера.

## Как сейчас устроено

Конфиг (пример Mim, `tests/parse_config_example/mim_markup_rules.json`):

- `markup_rules.rule_*.min/max/percent` — карта % от закупочной цены;
- `min_recommended_percent_markup` / `max_recommended_percent_markup` — границы наценки относительно РРЦ;
- `absolute_markup_rules.min_absolute_markup` / `markup_percent` — если рублёвая маржа мала, цена = `opt * markup_percent`.

Загрузка: `ParseConfiguration.get_markup_rules` → `extract_markup_rules`; карта — `get_price_markup_map` через `markup_params_from_rule` (ключ `percent` или `percent_markup`).

Алгоритм `BaseParser.add_price_markup` (сохранить **байт-в-байт** по смыслу):

1. `price = price_recommended or 0`, `price_opt = price_opt or 0`.
2. Если «маленький % РРЦ» **и** РРЦ пустая → `price = get_markup(opt, percent_из_карты)`.
3. Если «большой % РРЦ» **и** РРЦ пустая → `price = get_markup(opt, max_recommended_percent)`.
4. Если `price - opt < min_absolute_markup` → `price = opt * absolute.markup_percent`.
5. `price_markup = ceil(price/10)*10`.

`get_markup_percent`: первое правило, где `min <= opt <= max`; иначе минимальный `percent_markup` по карте (или 0).

**Ловушка поведения (не чинить в этой задаче).** Ветки 2–3 содержат `and not row_item.price_recommended`. При **наличии** РРЦ min/max recommended **не применяются**: берётся РРЦ, затем только абсолютный пол. При **отсутствии** РРЦ `recommended_percent_markup` = 0, поэтому `is_small_recommended_percent` обычно истинно (0 < min, например 0.15) — срабатывает карта %. `max_recommended` при пустой РРЦ почти мёртв. Mim как раз ходит в базовый метод. Зафиксировать это тестами политики, не «исправлять» молча.

Кто вызывает базовый метод сегодня: Mim (`mim_base.process`), FourTochki base (но sheet1 **переопределяет** `add_price_markup`), STK вызывает свой override. FourTochki sheet1: если есть РРЦ — она, иначе карта %; без абсолютного пола и без min/max recommended. Это **другая** политика, не предмет задачи 01.

## Подробное решение

1. Новый тип, например `MarkupPolicy` в `src/parsers/base_parser/price_markup.py` **или** соседний `markup_policy.py` (если файл раздуется). Не класс `BaseParser`.

Предпочтительный контракт:

```python
class MarkupPolicy:
    def __init__(self, rules: MarkupRules, price_map: tuple[MarkUpParams, ...]) -> None: ...

    def markup_percent_for_opt(self, price_opt: float) -> float: ...  # бывший get_markup_percent

    def apply(self, price_opt: float, price_recommended: float | None) -> float:
        """Возвращает ещё не округлённую отпускную цену (шаги 1–4)."""
```

Округление можно оставить на `BaseParser.round_price` **или** вызывать из `apply` последним шагом — выбрать одно место и не дублировать `math.ceil(/10)*10`.

2. Методы-предикаты (`is_small_recommended_percent` и т.д.) перенести в политику как приватные функции от `(opt, recommended, rules)`, без `RowItem`, чтобы политику тестировать числами.

3. `BaseParser.add_price_markup` становится:

```python
def add_price_markup(self, row_item: RowItem) -> None:
    policy = self.markup_policy()  # из parse_config
    price = policy.apply(row_item.price_opt or 0, row_item.price_recommended)
    row_item.price_markup = self.round_price(price)
```

`markup_policy()` собирать из `parse_config().get_markup_rules()` и `get_price_markup_map()`. Кэшировать на экземпляре парсера необязательно (это задача 08 про кэш конфига).

4. Удалить с `BaseParser` публичные методы политики, если больше никто в `src/` и тестах их не зовёт. Если тесты парсера дергают `is_small_recommended_percent` — перевести на политику, не оставлять два API.

5. Тесты (расширить `tests/test_base_parser/test_price_markup.py` или новый `test_markup_policy.py`):

   - карта: opt внутри диапазона → нужный percent; вне диапазонов → min percent;
   - opt=0 → default percent;
   - нет РРЦ, min_recommended > 0 → цена как `get_markup(opt, map%)`;
   - есть РРЦ, маржа в рублях ≥ порога → цена = РРЦ (текущее поведение веток 2–3);
   - есть РРЦ, маржа в рублях < `min_absolute_markup` → `opt * markup_percent`;
   - `max_recommended_percent_markup = 0` → ветка «большой %» выключена;
   - округление 1121 → 1130, 1120 → 1120.

6. Прогнать Mim/FourTochki-тесты, которые всё ещё зовут `add_price_markup` базовый: цифры в фикстурах не должны измениться.

## Ожидаемый результат

- В `BaseParser` нет формул `(sale-opt)/opt`, сравнения с min/max recommended и абсолютного пола — только делегат и округление (если округление не внутри политики).
- `MarkupPolicy.apply` воспроизводит текущий базовый алгоритм, включая ловушку с `not price_recommended`.
- Vendors **не** переведены: Poshk/Pioner/STK/Zapaska/Autosnab/FourTochki sheet1 по-прежнему со своими `add_price_markup`.
- `uv run pytest` зелёный; поведение Mim на тех же прайсах то же.

## Риски

- Соблазн «починить» ветки recommended в том же PR — это смена цен Mim. Не делать.
- Не тащить `RowItem` в политику: иначе снова связь с парсером.
- Не объединять FourTochki/Zapaska в этот PR.
