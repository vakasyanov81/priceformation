# Task-05: Value Objects для RowItem

Статус: ⬜ не начата. План пересмотрен после задач 7–10 (логгинг, типизированные
конфиги, разделение `core/` на слои, `ConfigProvider`) и после фактического
выполнения задач 4 (`BaseParser` → композиция) и 6 (`ParserStats`).

## Проблема

`RowItem` — God Object: 53 плоских поля, разложенные по смыслу на группы.

- Характеристики шин: `width`, `height_percent`, `diameter`, `ext_diameter`,
  `season`, `spike`, `index_velocity`, `index_load`, `tire_type`, `run_flat`,
  `inscription_on_the_side`, `construction_type`, `axis`, `layering`, `intimacy`,
  `camera_type`, `us_aff_designation`, `mark`
- Характеристики дисков: `disk_thickness`, `slot_count`, `pcd1`, `pcd2`, `eet`,
  `central_diameter`, `fastener`, `disk_type`, `disk_type_1`, `color`, `main_color`
- Цены и наценки: `price_opt`, `price_recommended`, `price_markup`, `percent_markup`
- Остатки и сроки: `rest_count`, `reserve_count`, `delivery_period`, `available`,
  `condition`
- Производитель/бренд/модель/коды: `manufacturer`, `brand`, `model`, `code`,
  `code_man`, `code_art`, `title`
- Служебные: `order`, `group_by_params`, `is_double`, `double_candidate`, `disputed`

Что это даёт:

- Нет группировки семантически связанных полей → вызовы вида `row.pcd1` не
  отличить от `row.price_opt` при чтении.
- Невозможно ввести инварианты (например, `price_markup >= price_opt`).
- `FieldDescriptor` с `_key_value_store` — имитация `dict`, не дающая типобезопасности.
- При появлении нового типа товара (масла, АКБ) поля шин/дисков остаются мусором.

## Что важно учесть в новом плане

Эти ограничения обнаружены при аудите кода и ломают часть исходного плана.

1. **Плоский словарь — контракт сериализации, а не деталь реализации.** `to_dict()`
   отдаёт `PriceRow = dict[str, Any]` (`src/parsers/writer/xls_writer.py:14`), 4
   шаблона колонок ссылаются на `RowItem.<field>.name`
   (`templates/tmpl/for_inner.py`, `for_drom.py`, `for_full.py`, `for_doubles.py`),
   `jsonl_writer` строит по нему payload и накопительный кодовник
   `result_meta.json` (`@N`), `src/parse_report_build.py:74` кладёт его в JSON.
   Значит VO нельзя «собирать `to_dict` вручную» (раздел 3 старого плана) и нельзя
   терять `.name` у полей.
2. **`to_dict()` возвращает только заданные ключи, не все 53.** Если VO начнёт
   эмитить все поля с дефолтами, jsonl наполнится `0` и `''`
   (`jsonl_writer._compact_row` пропускает только `None`), и вывод изменится.
3. **Неизвестные ключи пробрасываются как есть.** `_load_raw_row`
   (`row_item.py:182`) копирует любой ключ из сырого словаря; тесты
   (`tests/test_parsers/fixtures/zapaska.py:27`) вливают `hash_title` и `codes`.
   Строгая схема без pass-through потеряет вендорские колонки.
4. **Семантика `parse_errors`:** неудачная конверсия → поле не установлено +
   запись `{flat_key: {'value': raw, 'error': str(err)}}`. Потребители:
   `base_parser_row.py:48` (лог) и `parse_report_build.py:76` (JSON). У frozen VO
   `_errors` должен жить снаружи VO.
5. **Аннотации дескрипторов местами неверны:** `available` объявлен `int`, но несёт
   шаблонный дефолт `'В наличии'`; `slot_count`, `fastener`, `disk_type`,
   `disk_type_1`, `inscription_on_the_side`, `run_flat` объявлены `int`, но
   получают сырые строки вендоров. Типы VO надо брать по фактическим входам, иначе
   `mypy --strict` на вендорах сразу сорвётся.
6. **Прецедент есть:** задача 8 ввела узор, который надо повторить, — frozen
   dataclass + `slots` (`parsers/data_provider/models.py`), примитивы чтения полей
   в соседнем модуле (`json_fields.py`), ошибка границы с именем файла и путём до
   ключа. Отличается только то, что примитивы уже есть: `row_item_casts.py` и
   `row_item_strip.py`.
7. **Объём механической части:** 184 чтения и 28 записей в 32 модулях; 414
   тест-функций в 47 файлах ссылаются на `RowItem`.

## Решения

| Вопрос | Решение |
| --- | --- |
| Где живут VO | `src/parsers/row_item/value_objects.py`. Переезд в `domain/` — отдельная задача (см. «Отложено»), контракты слоёв его не требуют |
| Неизвестные ключи | Pass-through: поле `extra` в `RowItem`, `to_dict()` эмитит их как есть |
| Порядок | Задача 4 уже выполнена, конфликта по `base_parser/*` больше нет |
| Смежные находки аудита | Только дешёвые, в фазе Ф5 |
| `FieldDescriptor` | Не «переносится в VO», а заменяется реестром полей |

## Решение: реестр полей вместо `FieldDescriptor`

`FieldDescriptor` дублирует одну и ту же информацию в трёх местах: имя плоского
ключа, formatter и дефолт. Дальше эта информация расползлась ещё и по шаблонам
колонок (`RowItem.price_markup.name`). Единый источник правды — реестр:

```python
# src/parsers/row_item/field_registry.py
@dataclass(frozen=True, slots=True)
class FieldSpec:
    """Описание одного плоского поля: путь в VO, приведение типа, дефолт."""
    key: str            # плоский ключ, как в to_dict() и сыром словаре
    path: str           # путь в VO: 'tire.width'
    coercer: Callable[[Any], Any]
    default: Any = None
```

- `RowItem.<field>.name` для шаблонов реализуется как чтение из реестра (или
  остаётся совместимым дескриптором только для чтения `.name`), чтобы
  `templates/tmpl/*.py` и `writer/jsonl_codes.py` не трогать.
- Тест-инвариант: каждый ключ из `FIELD_FORMAT` присутствует в реестре, и каждый
  ключ реестра выводится в `to_dict()`.
- Приведение типов идёт через существующие `row_item_casts`/`row_item_strip`,
  а не через новые обёртки.

## Value Objects

`@dataclass(frozen=True, slots=True)`, разделение по смыслу:

| VO | Поля |
| --- | --- |
| `ProductIdentity` | `manufacturer`, `brand`, `model`, `title`, `code`, `code_man`, `code_art` |
| `TireDimensions` | `width`, `height_percent`, `diameter`, `ext_diameter`, `season`, `spike`, `index_load`, `index_velocity`, `tire_type`, `run_flat`, `inscription_on_the_side`, `construction_type`, `axis`, `layering`, `intimacy`, `camera_type`, `us_aff_designation`, `mark` |
| `DiskParameters` | `disk_thickness`, `slot_count`, `pcd1`, `pcd2`, `eet`, `central_diameter`, `fastener`, `disk_type`, `disk_type_1`, `color`, `main_color` |
| `Pricing` | `price_opt`, `price_recommended`, `price_markup`, `percent_markup` |
| `Stock` | `rest_count`, `reserve_count`, `delivery_period`, `available`, `condition` |
| `DuplicateInfo` | `order`, `group_by_params`, `is_double`, `double_candidate`, `disputed` |
| `VendorMeta` | `supplier_name`, `type_production` |

Оговорки:

- `tire` и `disk` — опциональные (`TireDimensions | None`), как в старом плане:
  товар может быть без дисков.
- Алиас `manufacturer` → плоский ключ `manufacturer_name` живёт в реестре, а не в
  имени поля VO.
- Мёртвое поле `title_chunks` (не пишется и не читается нигде) удаляется.
- Дефолты `price_* = 0` сохраняются в реестре, а не в `__init__` VO.

`RowItem` — обычный (не frozen) dataclass с `_errors` и `extra`:

```python
@dataclass
class RowItem:
    identity: ProductIdentity
    tire: TireDimensions | None = None
    disk: DiskParameters | None = None
    pricing: Pricing
    stock: Stock
    duplicate: DuplicateInfo
    vendor: VendorMeta
    extra: dict[str, Any] = field(default_factory=dict)
```

Порядок фаз таков, что `_errors` и pass-through работают с первого дня.

## План миграции

Каждая фаза — отдельный коммит с зелёными тестами.

| Ф | Содержание | Файлы |
| --- | --- | --- |
| Ф0 | Golden-тесты на форму `to_dict()` для 4 шаблонов и снапшот jsonl/xlsx. Снять устаревшие статусы задач 4 и 6 в `PLAN.md` | `tests/test_parsers/test_row_item/`, `PLAN.md` |
| Ф1 | Реестр полей `field_registry.py` + тест-инвариант реестра. Поведение `RowItem` не меняется | `src/parsers/row_item/field_registry.py` |
| Ф2 | `value_objects.py`: frozen+slots VO, типы по фактическим входам (см. п. 5 ограничений). `FieldDescriptor` пока живёт как есть | `src/parsers/row_item/value_objects.py` |
| Ф3 | `RowItem` на композиции VO + `_errors` снаружи + `extra`; слой приведения собирает VO и пишет ошибки по образцу `json_fields.py`; на все 53 поля — совместимые properties (`row.width` → `self.tire.width`). Ноль изменений в вызывающем коде | `src/parsers/row_item/row_item.py` |
| Ф4 | Механический переезд вызовов `row.X` → `row.<vo>.X`: пакетами `base_parser` → `common_price_*` → `vendors` → `services`/writers, по коммиту на пакет. Хедж: скрипт переименования + `uv run pytest` после каждого пакета | ~32 модуля, 184 чтения, 28 записей |
| Ф5 | Снос совместимых properties и `_key_value_store`; `to_dict()` из реестра + `extra`; `parse_errors` отдаёт копию; удаление мёртвого `from_dict`. `RowItem.from_dict` удаляется — в проде не вызывается | `src/parsers/row_item/row_item.py`, `tests/` |
| Ф6 | Полный CI-набор (см. `.github/workflows/python-app.yml`) + отдельная фаза `mutmut` на новом модуле; при необходимости дописать `do_not_mutate_patterns` | конфиг мутаций |

Динамический доступ по имени строки сохраняется: `base_finder.correction_field`
(`base_finder.py:102`) делает `getattr`/`setattr` по `field_name` — для него в
реестре нужен способ получить VO по плоскому ключу (или явный `set_field(key, value)`).

## Критерии готовности

- [ ] `RowItem` не имеет 53 плоских поля; семантика разложена по VO из таблицы выше.
- [ ] `RowItem.width` и подобные плоские свойства отсутствуют (шим снят).
- [ ] `to_dict()` возвращает ровно тот же набор ключей и значений, что до
      рефакторинга, — проверяется golden-тестами Ф0.
- [ ] `RowItem.<field>.name` продолжает работать: шаблоны колонок и
      `jsonl_codes.py` не меняются.
- [ ] Неизвестные вендорские ключи доходят до `to_dict()` (pass-through).
- [ ] `parse_errors` содержит те же записи, а свойство отдаёт копию словаря.
- [ ] Типы VO соответствуют фактическим входам вендоров: `mypy --strict` зелёный.
- [ ] `uv run pytest` (покрытие ≥ 95%), `black`, `ruff`, `flake8`, `mypy`,
      `lint-imports`, `vulture`, `bandit`, `pip-audit` — все зелёные.
- [ ] Вендорский столбец, для которого нет типизированного места, добавляется без
      правки `RowItem` (в `extra` или новым полем VO).

## Отложено (не в этой задаче)

- **Переезд `RowItem`/VO в `src/domain/`.** Целевая диаграмма `PLAN.md` рисует
  `RowItem` в `domain/`, но контракты слоёв этого не требуют: `services → parsers`
  разрешён. Переезд — механическая правка ~45 импортов и 47 тестовых файлов, его
  разумно делать после того, как VO появятся. → [#275](https://github.com/vakasyanov81/priceformation/issues/275)
- **Находки аудита в слое записи:** потерянный `'format': '@'` в
  `templates/tmpl/for_drom.py:20`, OR-семантика `make_exclude`
  (`xls_writer.py:38`) и расхождение falsy-значений между `xls_writer.py:119`
  (пропускает falsy) и `jsonl_writer.py:101` (пропускает только `None`). →
  [#274](https://github.com/vakasyanov81/priceformation/issues/274)

В этом плане исправляется только `RowItem.parse_errors`, отдающий внутренний
словарь, — это попадает в Ф5.