# Task-08: Типизированные конфиги (dataclasses)

## Проблема

Конфигурация читается везде через `json.loads` → `dict[str, Any]` → `cast()`:

```python
raw_rules = cast(dict[str, dict[str, Any]], raw_rules)
```

Это:

- **Нет валидации** — ошибка в JSON формате проявится позже (или не проявится вообще).
- **Нет автокомплита** — IDE не подсказывает ключи.
- **Cast-спагетти** — `cast(dict[str, dict[str, Any]], markup_data)` — ложное чувство безопасности.
- **Нет дефолтов** — `raw.get("min_recommended_percent_markup") or 0` — костыль.
- **Размазанный разбор** — `extract_markup_rules()` в `base_parser_config.py:52` и
  `markup_params_from_rule()` в `markup_rules.py:30` вручную конвертируют dict в
  NamedTuple в двух разных местах.

## Решение

### 1. Без внешней библиотеки: `dataclasses` + явный `from_dict`

Задача изначально предполагала `pydantic>=2`. Проверено (2026-10-02) на стенде
проекта — библиотека здесь не нужна:

| вариант | что даёт | цена |
|---------|----------|------|
| `pydantic>=2` | `model_validate`, алиасы (`AliasChoices`), JSON Schema | +1 рантайм-зависимость с C-расширением, `.env` в CI, `pip-audit` |
| `msgspec` | wheels для cp314 есть, `mypy --strict` / `ruff` / `flake8` / `pyright` / `vulture` — чисто (проверено) | **нет** field-alias: `dec_hook` для `Struct` не вызывается (проверено) — алиас `percent`/`percent_markup` пришлось бы делать двумя полями; **нет** `forbid_unknown_fields`; сообщения короче наших |
| `dataclasses` + `from_dict` | 0 зависимостей, аннотации дают автокомплит, `mypy --strict` ок, сообщения с именем файла и путём до ключа | поля надо протягивать в `from_dict` руками (лечится тестом, см. п. 5) |

Аргументы «за» скорость/схемы здесь не работают: конфиги **read-only**, читаются
один раз за прогон (декодировать их обратно не нужно — `model_dump`/`asdict` не
требуются), форм всего четыре.

Код ниже извлечён из этого документа и проверен: `mypy --strict`, `ruff`, `flake8`
(wemake), `vulture` — чисто; все 14 конфигов из `parse_config/` и
`tests/parse_config_example/` разобрались без ошибок.

### 2. Модели конфигов

Код разложен на два модуля: примитивы чтения полей — отдельно от форм конфигов
(wemake `WPS202` ограничивает модуль 7 членами, в один файл всё не влезает без
`noqa`).

```python
# parsers/data_provider/json_fields.py — примитивы чтения и проверки типа
type RawConfig = dict[str, Any]


def as_config_object(raw: Any, where: str) -> RawConfig: ...
def read_number(raw: RawConfig, key: str, where: str) -> float: ...
def read_flag(raw: RawConfig, key: str, where: str, default: bool = False) -> bool: ...
def read_zero_one_flag(raw: RawConfig, key: str, where: str) -> bool: ...
def read_object(raw: RawConfig, key: str, where: str) -> RawConfig: ...
def read_mode(raw: RawConfig, where: str, modes: tuple[str, ...]) -> str: ...
```

```python
# parsers/data_provider/models.py — формы конфигов
@dataclass(frozen=True, slots=True)
class MarkUpRule:
    """Правило наценки на диапазон цен."""

    min: float
    max: float
    percent_markup: float

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> MarkUpRule:
        """Разобрать правило. Принимает `percent` или `percent_markup`."""
        rule = as_config_object(raw, where)
        return cls(
            min=read_number(rule, 'min', where),
            max=read_number(rule, 'max', where),
            percent_markup=read_number(rule, _percent_key(rule), where),
        )


@dataclass(frozen=True, slots=True)
class AbsoluteMarkUpRules:
    """Абсолютные правила наценки."""

    min_absolute_markup: float = 0
    markup_percent: float = 0
    mode: str = ABSOLUTE_MODE_MULTIPLIER


@dataclass(frozen=True, slots=True)
class MarkupRulesConfig:
    """Наценки поставщика целиком (`<supplier>_markup_rules.json`)."""

    markup_rules: dict[str, MarkUpRule] = field(default_factory=dict)
    min_recommended_percent_markup: float = 0
    max_recommended_percent_markup: float = 0
    absolute_markup_rules: AbsoluteMarkUpRules = field(default_factory=AbsoluteMarkUpRules)
    replace_small_recommended: bool = False

    @classmethod
    def _read_rules(cls, rules_raw: RawConfig, where: str) -> dict[str, MarkUpRule]:
        """Разобрать секцию `markup_rules`: имя правила → правило на ценовой диапазон."""


@dataclass(frozen=True, slots=True)
class VendorConfigEntry:
    """Запись поставщика в `vendor_list.json`."""

    enabled: bool
```

`from_dict` принимает `Any` и **сам** проверяет, что корень — объект: провайдер
отдаёт результат `read_json_file()` без промежуточного `cast()`, а тестовые двойники
могут отдавать литерал словаря.

`_percent_key(rule)` возвращает тот ключ, который реально написан в JSON
(`percent_markup`, иначе совместимый алиас `percent`), поэтому в сообщении об ошибке
называется ключ пользователя, а не всегда `percent_markup`.

Ключевые отличия от текущих NamedTuple:

- `markup_rules: dict[str, dict[str, Any]]` → `dict[str, MarkUpRule]` — второй проход
  разбора (`markup_params_from_rule`) не нужен.
- `enabled: int` → `bool`: убирает `bool(vendor.enabled)` в
  `base_parser.py:108` и `all_vendors.py:57`.
- `MarkupRules.should_replace_with_map()` переезжает на модель (метод, не логика
  провайдера).
- Модели `frozen=True, slots=True` — иммутабельны, как и NamedTuple; `eq=True`
  по умолчанию, поэтому сравнение по значению в тестах продолжает работать.
- `black_list` (текст, не JSON) и `title_aliases.json` остаются как есть: типизация
  `manufacturer_aliases.json` (значения бывают `list[str]`, `dict` или `str`, см.
  `manufacturer_aliases.py:15-58`) в объём задачи не входит — там останется `Any`.
- Имя `VendorEntry` не годилось: в `parsers/registry.py` и `parsers/all_vendors.py`
  уже есть алиас `VendorEntry = tuple[type[BaseParser], ParseConfiguration]`
  (запись реестра). Модель названа `VendorConfigEntry`.

### 3. Провайдеры возвращают модели, а не dict

```python
# parsers/data_provider/markup_rules.py

class MarkupRulesProviderBase:
    def get_markup_data(self) -> MarkupRulesConfig:
        """Абстрактный метод. Наценки поставщика."""
        raise NotImplementedError


class MarkupRulesProviderFromUserConfig(MarkupRulesProviderBase):
    def get_markup_data(self) -> MarkupRulesConfig:
        """Прочитать и разобрать `<supplier>_markup_rules.json`."""
        raw = json.loads(read_file(self.get_file_path()))
        return MarkupRulesConfig.from_dict(raw, Path(self.get_file_path()).name)
```

Аналогично:

- `VendorListProviderBase.get_config_vendor_list() -> dict[str, VendorConfigEntry]`;
- `BlackListProviderBase` — без изменений (обычный текст);
- `ManufacturerAliasesProviderBase`, `TitleAliasesProviderBase` — без изменений.

### 4. Валидация на границе

`ConfigValidationError(CoreExceptionError)` добавляется в `domain/exceptions.py` и
поднимается в `models.py`; провайдеры по-прежнему ловят только `FileNotFoundError`
(`markup_rules.py:98`, `vendor_list.py:45`) и заменяют его на
`PriceRulesConfigFileError` / `VendorListConfigFileError`. Сообщение содержит имя
файла и путь до ключа:

```
stk_markup_rules.json → markup_rules.r: «min» должно быть числом, получено 'abc'
vendor_list.json → stk: «enabled» должен быть 0 или 1, получено 2
```

Битый JSON (обрезанный файл) тоже должен называть файл, а не падать голым
`json.JSONDecodeError`: за это отвечает `read_json_file()`
(`infrastructure/data/file_reader.py`), который оборачивает декодирование в
`ConfigValidationError` — оба провайдера зовут только его.

### 5. Убираем ручной разбор

- `extract_markup_rules()` (`base_parser_config.py:52`) — удалить.
- `markup_params_from_rule()` (`markup_rules.py:30`) — удалить, экспорт из
  `data_provider/__init__.py` убрать.
- `ParseConfiguration.get_markup_rules()` возвращает `MarkupRulesConfig` из провайдера
  без разбора; `get_price_markup_map()` — `tuple(rules.markup_rules.values())`.
- `ParseConfiguration.all_vendor_config()` — `dict[str, VendorConfigEntry]` напрямую из
  провайдера.
- Именованные типы `MarkUpParams`, `MarkupRules`, `VendorParams` удаляются, их заменяют
  модели из `models.py`; `AbsoluteMarkUpRules` переезжает туда же из
  `markup_rules.py`.
- Тип `_price_markup_map` становится `tuple[MarkUpRule, ...]`.

### 6. Тест-обёртка «модель полностью протянута из JSON»

Главный риск ручного `from_dict` — добавили поле в модель, забыли его прочитать, и
оно молча получит дефолт. Закрывается тестом на равенство: из dict со **всеми**
полями получаем ровно такой же dataclass; непроведённое поле ломает `==`:

```python
def test_markup_config_reads_all_fields():
    raw = {
        'markup_rules': {'rule_1': {'min': 1, 'max': 2, 'percent': 0.3}},
        'min_recommended_percent_markup': 0.1,
        'max_recommended_percent_markup': 0.4,
        'absolute_markup_rules': {'min_absolute_markup': 5, 'markup_percent': 1.5, 'mode': 'delta'},
        'replace_small_recommended': True,
    }

    assert MarkupRulesConfig.from_dict(raw, 'x.json') == MarkupRulesConfig(
        markup_rules={'rule_1': MarkUpRule(min=1, max=2, percent_markup=0.3)},
        min_recommended_percent_markup=0.1,
        max_recommended_percent_markup=0.4,
        absolute_markup_rules=AbsoluteMarkUpRules(min_absolute_markup=5, markup_percent=1.5, mode='delta'),
        replace_small_recommended=True,
    )
```

## План миграции

1. Добавить `ConfigValidationError` в `domain/exceptions.py`.
2. Создать `parsers/data_provider/json_fields.py` (примитивы `as_config_object`,
   `read_number`, `read_flag`, `read_object`, `read_mode`) и
   `parsers/data_provider/models.py` (`MarkUpRule`, `AbsoluteMarkUpRules`,
   `MarkupRulesConfig`, `VendorConfigEntry`).
3. Перевести `MarkupRulesProviderBase` и `MarkupRulesProviderFromUserConfig` на
   `MarkupRulesConfig`.
4. Перевести `VendorListProviderBase` и `VendorListProviderFromUserConfig` на
   `dict[str, VendorConfigEntry]`.
5. Обновить `base_parser_config.py`: убрать `extract_markup_rules()`, упростить
   `get_markup_rules()`, `get_price_markup_map()`, `all_vendor_config()`.
6. Поправить `base_parser.py:103-108`, `all_vendors.py:51-57`, `markup_policy.py` под
   новые типы (`enabled: bool`, `MarkUpRule`).
7. Удалить `MarkUpParams`, `MarkupRules`, `VendorParams`, `markup_params_from_rule`;
   почистить реэкспорт в `data_provider/__init__.py`.
8. Тесты: добавить `tests/test_parsers/test_data_provider/test_models.py` (позитивные
   кейсы + параметризованные негативные на каждый тип + тест-обёртка из п. 6), поправить
   `test_markup_rules.py`, `test_markup_rules_contract.py`, `test_providers.py`,
   `test_vendors/test_zapaska_disk_markup.py`, `test_base_parser/*`, `test_services/*`.
9. Обновить `tasks/PLAN.md` (строка 8) и упоминание pydantic в `AGENTS.md`.

Отклонения от плана, принятые при реализации:

- хелперы вынесены в `json_fields.py`: wemake `WPS202` не даёт держать в одном модуле
  больше 7 членов, а с моделями и константами их было 13;
- модель называется `VendorConfigEntry`, а не `VendorEntry` (конфликт с алиасом
  реестра в `parsers/registry.py`);
- `from_dict` принимает `Any` и сам проверяет корень, провайдеры не делают
  промежуточный `cast(dict[str, Any], ...)`;
- правило `enabled` проходит общий хелпер `read_zero_one_flag`: в JSON это `0`/`1`,
  булевы `true`/`false` принимаются как раньше, а вот `1.0` и `'1'` — уже нет;
- декодирование JSON вынесено в `read_json_file()` (`infrastructure/data/file_reader.py`),
  чтобы нечитанный конфиг тоже давал `ConfigValidationError` с именем файла;
- пункт 6 не потребовал правок в `all_vendors.py`: там `bool(vendor and vendor.enabled)` —
  это защита от пустой записи реестра, а не разбор конфига.

## Критерии готовности

- [x] Все конфиги проходят валидацию при загрузке, ошибка в JSON → `ConfigValidationError`
      с именем файла и путём до ключа.
- [x] Старые NamedTuple и `extract_markup_rules()` / `markup_params_from_rule()` удалены.
- [x] `cast(dict[str, ...], ...)` ушёл из `markup_rules.py`, `vendor_list.py` и
      `base_parser_config.py` (проверить `rg 'cast\(dict' src/parsers/data_provider`).
      Остался только в `manufacturer_aliases.py` и кэше `manufacturer_group.py` —
      они вне объёма задачи.
- [x] Ноль новых рантайм-зависимостей в `pyproject.toml`.
- [x] IDE подсказывает поля при работе с конфигами.
- [x] Тест-обёртка «модель полностью протянута из JSON» проходит.
- [x] `uv run pytest` (покрытие ≥ 95%), `black`, `ruff`, `flake8`, `mypy`, `lint-imports`,
      `vulture`, `bandit`, `pip-audit` — зелёные.

## Что стало строже (намеренно)

Старый разбор молча прощал часть ошибок — это и была цель тикета, но фиксируем явно:

- `"min": null` и `"min_recommended_percent_markup": null` больше не превращаются в `0`
  (было `float(raw.get(...) or 0)`), а дают `ConfigValidationError` с путём до ключа;
- `"replace_small_recommended": 1` больше не приводится к `true` (было `bool(...)`):
  теперь это должно быть `true`/`false`; `"enabled"` — наоборот, остаётся `0`/`1`,
  булевы принимаются, числа с дробной частью и строки — нет;
- неизвестный ключ по-прежнему игнорируется.

Все конфиги из `parse_config/`, `tests/parse_config_example/` и
`integration_tests/parse_config_example/` под новые правила подходят без правок.

## Что НЕ делаем

- Не читаем и не пишем конфиги в `parse_config/` автоматически (никакого
  `model_dump`/`asdict`).
- Не запрещаем лишние ключи в JSON: в `parse_config/four_tochki_markup_rules.json`
  лежит секция `api` с логином и паролем в открытом виде, её никто не читает. Про
  пароли — отдельный тикет: перенести в `.env` (как уже сделано для запаски в
  `infrastructure/config/zapaska_api_config.py`). До этого разбор лишних ключей
  игнорирует.
- Не типизируем `manufacturer_aliases.json` (полиморфные значения) и
  `title_aliases.json` — там нет дефолтов и валидации, а объём выгоды не окупает
  риск регрессий в `manufacturer_group()`.
- Не добавляем `forbid_unknown_fields`-аналог: текущая семантика
  «лишнее игнорируем» совпадает с `pydantic(extra='ignore')` по умолчанию.

## Когда всё-таки понадобится библиотека

Если появятся: больше пяти новых форм конфигов, генерация JSON Schema для
пользователей, или реальный union-тип в `manufacturer_aliases.json`. Тогда —
`msgspec`: wheels для cp314 есть, весь тулчейн (mypy/ruff/flake8/pyright/vulture)
проходит без замечаний. Учесть, что field-alias там придётся делать двумя полями
с `__post_init__`.

## Ссылка

Тикет: [#249](https://github.com/vakasyanov81/priceformation/issues/249).