# 01. Вынести MarkupPolicy — набор задач

Краткая задача: [01-markup-policy.md](../01-markup-policy.md)  
План: [01-markup-policy-detail.md](01-markup-policy-detail.md)

Разбиение этапа 01 на реализуемые тикеты. Порядок: 01.1 → 01.2 → 01.3 → 01.4 → 01.5 → 01.6.

Общие ограничения на все тикеты:

- Не менять цены Mim и остальных поставщиков, которые ходят в базовый `add_price_markup`.
- Не чинить ловушку `and not price_recommended` (ветки min/max recommended при наличии РРЦ не срабатывают).
- Не тащить `RowItem` в политику.
- Не переводить Poshk / Pioner / STK / Zapaska / Autosnab / FourTochki sheet1 / Mim sheet2.
- Округление `math.ceil(price / 10) * 10` живёт **только** в `BaseParser.round_price`. `MarkupPolicy.apply` возвращает цену **до** округления.

---

## 01.1 Класс `MarkupPolicy` и выбор процента по карте

**Зачем.** Вынести из `BaseParser.get_markup_percent` поиск процента по диапазонам закупа. Это независимый кусок, на него опираются `apply` и оставшиеся vendors (Poshk, Pioner, FourTochki sheet1).

**Файлы**

- новый `src/parsers/base_parser/markup_policy.py`
- не трогать `price_markup.py` (`calc_percent`, `get_markup` остаются чистой арифметикой)

**Сделать**

1. Добавить класс:

```python
from parsers.data_provider.markup_rules import MarkUpParams, MarkupRules


class MarkupPolicy:
    def __init__(
        self,
        rules: MarkupRules,
        price_map: tuple[MarkUpParams, ...],
    ) -> None:
        self._rules = rules
        self._price_map = price_map

    def markup_percent_for_opt(self, price_opt: float) -> float:
        """Бывший BaseParser.get_markup_percent."""
```

2. Алгоритм `markup_percent_for_opt` — байт-в-байт как сейчас в `BaseParser.get_markup_percent`:

```python
def markup_percent_for_opt(self, price_opt: float) -> float:
    default_percent = min({rule.percent_markup for rule in self._price_map} or (0,))
    if not price_opt:
        return default_percent
    for rule in self._price_map:
        if rule.min <= price_opt <= rule.max:
            return rule.percent_markup
    return default_percent
```

Поведение, которое нельзя сломать:

- первое правило, где `min <= opt <= max` (границы включены; пересечения диапазонов как в Mim JSON — побеждает первое);
- нет попадания → минимальный `percent_markup` по карте;
- пустая карта → `0`;
- `price_opt == 0` / `False` → сразу `default_percent`, без обхода диапазонов.

3. Типы брать из `parsers.data_provider.markup_rules`: `MarkupRules`, `MarkUpParams`, `AbsoluteMarkUpRules`. Конфиг не парсить внутри политики.

**Готово, когда**

- Класс существует, в `BaseParser` ещё ничего не переведено.
- Есть тесты только на `markup_percent_for_opt` (можно сразу в файле 01.5, либо минимальный набор здесь).

**Не делать:** `apply`, предикаты, правки `BaseParser`.

---

## 01.2 Приватные предикаты политики

**Зависит от:** 01.1

**Зачем.** Перенести сравнения с min/max recommended и абсолютным полом с `BaseParser` в политику. Сигнатуры — числа, не `RowItem`.

**Сделать**

На `MarkupPolicy` добавить приватные методы. Публичный API класса по-прежнему только `__init__` и `markup_percent_for_opt` (плюс `apply` в 01.3).

```python
def _recommended_percent(
    self,
    price_opt: float,
    price_recommended: float | None,
) -> float:
    """Бывший BaseParser.recommended_percent_markup.

    Если РРЦ пустая/0 → 0, иначе calc_percent(recommended, opt).
    """

def _is_small_recommended_percent(
    self,
    price_opt: float,
    price_recommended: float | None,
) -> bool:
    """percent РРЦ < rules.min_recommended_percent_markup."""

def _is_big_recommended_percent(
    self,
    price_opt: float,
    price_recommended: float | None,
) -> bool:
    """False, если max_recommended_percent_markup == 0;
    иначе percent РРЦ > max_recommended_percent_markup.
    """

def _is_small_absolute_markup(
    self,
    selling_price: float,
    purchase_price: float,
) -> bool:
    """selling - purchase < rules.absolute_markup_rules.min_absolute_markup."""

def _price_with_absolute_rule(self, price_opt: float) -> float:
    """opt * rules.absolute_markup_rules.markup_percent."""
```

Реализации (смысл как в `BaseParser`):

```python
from parsers.base_parser.price_markup import calc_percent, get_markup  # get_markup — в 01.3


def _recommended_percent(self, price_opt: float, price_recommended: float | None) -> float:
    recommended = price_recommended or 0
    opt = price_opt or 0
    return calc_percent(recommended, opt) if recommended else 0


def _is_small_recommended_percent(self, price_opt: float, price_recommended: float | None) -> bool:
    return self._recommended_percent(price_opt, price_recommended) < self._rules.min_recommended_percent_markup


def _is_big_recommended_percent(self, price_opt: float, price_recommended: float | None) -> bool:
    if not self._rules.max_recommended_percent_markup:
        return False
    return self._recommended_percent(price_opt, price_recommended) > self._rules.max_recommended_percent_markup


def _is_small_absolute_markup(self, selling_price: float, purchase_price: float) -> bool:
    return selling_price - purchase_price < self._rules.absolute_markup_rules.min_absolute_markup


def _price_with_absolute_rule(self, price_opt: float) -> float:
    return price_opt * self._rules.absolute_markup_rules.markup_percent
```

`calc_percent` импортировать из `parsers.base_parser.price_markup`, не через `BaseParser.calc_percent`.

**Готово, когда** предикаты есть на классе и покрыты тестами на числах (границы `<` / `>`, нулевой max выключает «большой %»).

**Не делать:** `apply`, удаление методов с `BaseParser`.

---

## 01.3 `MarkupPolicy.apply` — базовый алгоритм без округления

**Зависит от:** 01.2

**Зачем.** Единственная реализация шагов 1–4 текущего `BaseParser.add_price_markup`.

**Сделать**

```python
def apply(self, price_opt: float, price_recommended: float | None) -> float:
    """Отпускная цена до округления (шаги 1–4 базового алгоритма)."""
```

Алгоритм (порядок веток сохранить):

```python
from parsers.base_parser.price_markup import get_markup


def apply(self, price_opt: float, price_recommended: float | None) -> float:
    price = price_recommended or 0
    opt = price_opt or 0

    if self._is_small_recommended_percent(opt, price_recommended) and not price_recommended:
        price = get_markup(opt, self.markup_percent_for_opt(opt))

    if self._is_big_recommended_percent(opt, price_recommended) and not price_recommended:
        price = get_markup(opt, self._rules.max_recommended_percent_markup)

    if self._is_small_absolute_markup(price, opt):
        price = self._price_with_absolute_rule(opt)

    return price
```

Ловушка — зафиксировать, не чинить:

- условие веток 2–3: `and not price_recommended` (ложно для `None`, `0`, `0.0`);
- при **наличии** РРЦ min/max recommended **не** применяются: стартовая цена = РРЦ, затем только абсолютный пол;
- при **отсутствии** РРЦ `_recommended_percent` = 0, поэтому `_is_small_recommended_percent` обычно истинно (0 < min, например 0.15) — срабатывает карта %;
- `max_recommended` при пустой РРЦ почти мёртв; при `max_recommended_percent_markup == 0` ветка «большой %» выключена явно.

`apply` **не** вызывает `round_price`. Округление остаётся на парсере.

**Готово, когда** `apply(opt, recommended)` на фикстуре Mim (см. 01.5) даёт те же сырые цены, что шаги 1–4 текущего `add_price_markup` до `round_price`.

**Не делать:** правки `BaseParser`, перевод vendors.

---

## 01.4 Делегат в `BaseParser`: политика приходит снаружи

**Зависит от:** 01.3

**Зачем.** Базовый путь Mim / FourTochki base считает цену через политику, не копируя формулы. Парсер — потребитель политики, не её фабрика: rules/map достаёт тот, кто собирает парсер.

**Файлы**

- `src/parsers/base_parser/markup_policy.py` — `make_markup_policy`
- `src/parsers/base_parser/base_parser.py` — конструктор + делегаты
- `src/parsers/common_price.py` — composition root (`vendor_cls(config)` → передать политику)
- хелперы тестов, которые создают парсер и зовут `add_price_markup` / `get_markup_percent`

**Сделать**

1. Модульная фабрика (не метод `BaseParser`):

```python
def make_markup_policy(parse_config: ParseConfiguration) -> MarkupPolicy:
    return MarkupPolicy(
        rules=parse_config.get_markup_rules(),
        price_map=parse_config.get_price_markup_map(),
    )
```

2. `BaseParser.__init__` принимает готовый объект, только сохраняет. Keyword-only, чтобы не сдвинуть `file_prices` / `xls_reader`:

```python
def __init__(
    self,
    parse_config: ParseConfiguration | None = None,
    file_prices: list[str] | None = None,
    xls_reader: type[XlsReaderFactory] = XlsReader,
    *,
    markup_policy: MarkupPolicy | None = None,
) -> None:
    ...
    self._markup_policy = markup_policy
```

`None` — только для тестов, которые наценку не зовут. В `add_price_markup` / `get_markup_percent` при `None` — явная ошибка (по аналогии с `ParseConfigNotSetError`), **не** молчаливый `make_markup_policy(self.parse_config())`.

3. Composition root. Сейчас `CommonPrice.parse_all_vendors` делает `vendor_cls(vendor_config)`. Заменить на передачу политики, либо тонкий `make_parser(cls, config, *, markup_policy=None, **kwargs)` **рядом с парсером/common_price, не метод класса**: если `markup_policy` не передали — вызвать `make_markup_policy(config)`. Так тесты `get_fake_parser` и прод собирают одинаково.

4. Заменить тело `add_price_markup`:

```python
def add_price_markup(self, row_item: RowItem) -> None:
    price = self._markup_policy.apply(row_item.price_opt or 0, row_item.price_recommended)
    row_item.price_markup = self.round_price(price)
```

5. `get_markup_percent` оставить на `BaseParser`: его всё ещё зовут Poshk, Pioner, FourTochki sheet1 и тесты Pioner. Тонкий делегат в **поле**, не в фабрику:

```python
def get_markup_percent(self, price_value: float) -> float:
    return self._markup_policy.markup_percent_for_opt(price_value)
```

Mim sheet2 **переопределяет** `get_markup_percent` и `add_price_markup` — не ломать override. Политику всё равно передать: базовый конструктор её ждёт, sheet2 может не использовать.

6. `round_price`, `calc_percent`, `get_markup` на `BaseParser` **не удалять**: ими пользуются overrides vendors.

```python
@classmethod
def round_price(cls, price_value: float) -> float:
    return math.ceil(price_value / 10) * 10
```

**Готово, когда**

- в `BaseParser` нет метода `markup_policy()` и нет `MarkupPolicy(rules=..., price_map=...)`;
- `grep` по `BaseParser.add_price_markup` показывает только делегат в `_markup_policy` + `round_price`;
- `CommonPrice` / хелперы тестов с наценкой передают политику сверху;
- Mim sheet1 / FourTochki sheet2 (базовый метод) зелёные, цифры фикстур те же;
- Poshk / Pioner / STK / Zapaska / Autosnab / FourTochki sheet1 / Mim sheet2 без правок логики наценки.

**Не делать:** удаление предикатов с `BaseParser` (это 01.6); override `markup_policy()` у vendors (точки расширения 02/05 — другой объект в конструктор).

---

## 01.5 Тесты политики и округления

**Зависит от:** 01.3 (можно писать параллельно с 01.4, если `apply` уже есть)

**Зачем.** Политика проверяется числами, без парсера и `RowItem`. Ловушка recommended зафиксирована тестом, а не «исправлена».

**Файлы**

- расширить `tests/test_base_parser/test_price_markup.py` **или** новый `tests/test_base_parser/test_markup_policy.py`;
- текущие `test_calc_percent` / `test_get_markup` оставить.

Хелпер для тестов (не тащить Mim-парсер):

```python
from parsers.data_provider.markup_rules import (
    AbsoluteMarkUpRules,
    MarkUpParams,
    MarkupRules,
)
from parsers.base_parser.markup_policy import MarkupPolicy


def _policy(
    *,
    price_map: tuple[MarkUpParams, ...] | None = None,
    min_recommended: float = 0.15,
    max_recommended: float = 0,
    min_absolute: float = 300,
    absolute_percent: float = 1.3,
) -> MarkupPolicy:
    rules = MarkupRules(
        markup_rules={},
        min_recommended_percent_markup=min_recommended,
        max_recommended_percent_markup=max_recommended,
        absolute_markup_rules=AbsoluteMarkUpRules(
            min_absolute_markup=min_absolute,
            markup_percent=absolute_percent,
        ),
    )
    default_map = (
        MarkUpParams(min=0, max=5001, percent_markup=0.20),
        MarkUpParams(min=5000, max=10001, percent_markup=0.19),
    )
    return MarkupPolicy(rules, price_map or default_map)
```

Округление тестировать через `BaseParser.round_price` (classmethod, парсер не нужен):

```python
from parsers.base_parser.base_parser import BaseParser

assert BaseParser.round_price(1121) == 1130
assert BaseParser.round_price(1120) == 1120
```

**Набор кейсов** (каждый — отдельный тест или строка parametrize):

| ID | Вход | Ожидание |
| --- | --- | --- |
| map-in-range | `markup_percent_for_opt(1000)` при правиле `0..5001 → 0.20` | `0.20` |
| map-boundary-min | opt равен `rule.min` | percent этого правила |
| map-boundary-max | opt равен `rule.max` | percent этого правила |
| map-first-wins | opt в пересечении двух правил | percent **первого** в `price_map` |
| map-out-of-range | opt больше всех `max` | `min(percent_markup)` по карте |
| map-opt-zero | `markup_percent_for_opt(0)` | тот же default, что вне диапазонов |
| map-empty | `price_map=()` | `0` |
| no-rrc-small-min | `apply(1000, None)` при `min_recommended=0.15` | `get_markup(1000, map%)` — карта, не РРЦ |
| has-rrc-margin-ok | `apply(1000, 2000)` при `min_absolute=300` | `2000` (РРЦ; ветки 2–3 не трогают) |
| has-rrc-margin-low | `apply(1000, 1100)` при `min_absolute=300`, `markup_percent=1.3` | `1300` (`opt * 1.3`) |
| has-rrc-margin-eq | `selling - opt == min_absolute` | пол **не** срабатывает (`<`, не `<=`) |
| max-off | `max_recommended=0`, нет РРЦ | ветка «большой %» не берёт max; цена с карты |
| max-on-no-rrc | `max_recommended=0.10`, нет РРЦ | `_recommended_percent=0` < 0.10, не `>`; карта, не max (ловушка) |
| round-up | `round_price(1121)` | `1130` |
| round-exact | `round_price(1120)` | `1120` |

Дополнительно перенести смысл Mim-тестов предикатов на политику (числа из `MimMarkupRulesProviderForTests`: min 0.14, max 0.27, абсолют 300 / 1.5):

- `_is_small_absolute_markup(1300, 1000) is False`, `(1299, 1000) is True`;
- `_is_small_recommended_percent(1000, 1140) is False`, `(1000, 1139) is True`;
- `_is_big_recommended_percent(1000, 1270) is False`, `(1000, 1271) is True`;
- `_is_big_recommended_percent` при `max_recommended=0` — всегда `False` (сейчас `test_parse_poshk.test_big_recommended_without_max_is_false`).

**Готово, когда** все строки таблицы зелёные; тесты не импортируют `RowItem` в сценариях политики.

---

## 01.6 Снять методы политики с `BaseParser` и перевести тесты

**Зависит от:** 01.4, 01.5

**Зачем.** Один API расчёта. Не оставлять предикаты и на парсере, и в политике.

**Что удалить с `BaseParser`** (после перевода вызовов):

| Метод | Сейчас зовут | Действие |
| --- | --- | --- |
| `recommended_percent_markup(row_item)` | только `add_price_markup` / соседние предикаты | удалить |
| `is_small_recommended_percent(row_item)` | `tests/.../test_parse_mim_sheet1.py` | удалить, тест → политика |
| `is_big_recommended_percent(row_item)` | Mim sheet1, `test_parse_poshk.py` | удалить, тесты → политика |
| `is_small_absolute_markup(selling, purchase)` | Mim sheet1 | удалить, тест → политика |
| `get_price_with_absolute_rule_markup(price_opt)` | только `add_price_markup` | удалить |

**Что оставить на `BaseParser`**

```python
def add_price_markup(self, row_item: RowItem) -> None: ...  # делегат в _markup_policy + round_price
def get_markup_percent(self, price_value: float) -> float: ...  # делегат в _markup_policy, vendors ещё зовут
def markup_rules(self) -> MarkupRules: ...  # конфиг, не формула
@classmethod
def round_price(cls, price_value: float) -> float: ...
@classmethod
def calc_percent(cls, price_sale: float, price_purchase: float) -> float: ...
@classmethod
def get_markup(cls, price: float, percent: float) -> float: ...
```

Политика — поле `_markup_policy`, не метод-фабрика. `make_markup_policy` живёт снаружи класса.

`calc_percent` / `get_markup` на классе — прокси в `price_markup.py` с `@lru_cache`. Вычищать в задаче 06, не здесь.

**Правки тестов**

- `test_parse_mim_sheet1.py`: убрать `test_small_absolute_markup_at_threshold` и `test_recommended_percent_boundaries` (логика уже в 01.5). Оставить `test_markup`, `test_markup_without_prices_is_zero`, parse/title.
- `test_parse_poshk.py`: убрать `test_big_recommended_without_max_is_false`.
- `test_parse_pioner.py`: `parser.get_markup_percent(...)` оставить — метод ещё публичный.
- `test_parse_mim_sheet2.py`: `get_markup_percent` override Mim sheet2 не трогать.

Прогнать целиком `uv run pytest`. Регрессии фикстур Mim / FourTochki sheet2 быть не должно.

**Готово, когда**

- в `src/` нет `is_small_recommended_percent` / `is_big_recommended_percent` / `is_small_absolute_markup` / `recommended_percent_markup` / `get_price_with_absolute_rule_markup`;
- формулы `(sale-opt)/opt`, min/max recommended и абсолютный пол есть только в `MarkupPolicy` (+ чистые `calc_percent` / `get_markup`);
- vendors со своими `add_price_markup` без изменений;
- `uv run pytest` зелёный.
