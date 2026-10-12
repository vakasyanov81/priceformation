# Task-12: Независимое определение типа товара (`type_production`)

Статус: 📝 план. Спецификация алгоритма — [`README_ProductType.md`](../README_ProductType.md)
(§2–§9 — правила, §11 — статистика согласия с категориями поставщиков).

## Проблема

Тип товара (`type_production`) сегодня берётся из прайса или из грубых
эвристик, и поставщику здесь доверяют:

- `column_canonical` канонизирует **колонку поставщика** и записывает её как
  итоговый тип (`category.py:116`, `category_finder.map_categories`);
- `header_rows` берёт тип из **строки-заголовка** раздела (`category.py:168`);
- `tire_size_category` (`tire_category.py`) — частичный прототип независимого
  подхода, но он сам является *единственным* источником типа и не сверяется с
  поставщиком; у него нет ни камер/колец/лент в полном объёме, ни мото/сельхоз
  по README, ни нормализации гомоглифов.

Категория поставщика регулярно неверна (README §7, §11): сельхоз-шины в
грузовых листах (`mim`), легковые в «легкогрузовых» (`zapaska`), `SUV` как
отдельный тип. Согласие независимого расчёта с поставщиком — **94.7 %**, то
есть ~5 % типов у поставщиков ошибочны.

Требование:

1. **Не доверять** типу поставщика. Тип всегда вычисляется самостоятельно по
   названию и параметрам строки (README §2–§9).
2. В `type_production` пишем **свой** вычисленный тип.
3. Если вычисленный тип **расходится** с заявленным поставщиком — в шаблоне
   `for_inner` у «Тип товара» ставим `*` (признак изменения).

## Решения

| Вопрос | Решение |
| --- | --- |
| Где считаем | Чистый классификатор `src/parsers/strategies/product_type.py` (домена не касается, IO нет) |
| Как соотносится со стратегиями | **Слой поверх**: существующие стратегии дают «заявленный» тип, классификатор его перекрывает и метит расхождение |
| Единый словарь типов и синонимов | `src/parsers/strategies/product_types.py` — каноничные имена + карта синонимов поставщиков; `category_finder.map_categories` и `_HEADER_CATEGORIES` берут имена оттуда |
| Признак расхождения | Новое булево поле `type_corrected` (group `VENDOR`) в `field_registry`/`VendorMeta`; `type_production` остаётся **чистым** |
| Маркер `*` | Опция шаблона колонки: `'suffix': '*'` + `'suffix_when': 'type_corrected'`; рендерится в `get_value` (`xls_writer.py:17`) |
| Где включается | Секция конфига: `category: { "strategy": ..., "independent_type": true }`; по умолчанию **выключено** (включаем по поставщику после сверки) |
| Судьба `tires_by_size` | Удаляется: режим становится частным случаем нового слоя (заявленный = заголовок раздела, свой = размер) |
| Нераспознанный тип поставщика | Не расхождение: `type_corrected` не ставится, только инфо-заметка в статистике (README §7) |

Почему `type_corrected` — отдельное поле, а не `*` в `type_production`:
`type_production` участвует в ключе группировки (`common_price_group_key.py:73`),
в jsonl и в отчётах. `*` в значении разорвал бы группы одного типа. Маркер —
чисто визуальный (шаблонный), данные остаются чистыми.

## Классификатор: `ProductTypeClassifier`

Публичный интерфейс (чистая функция над позицией):

```python
# src/parsers/strategies/product_type.py
class ProductTypeClassifier:
    """Независимый тип товара по названию и параметрам (README §2–§9)."""

    def classify(self, row_item: RowItem) -> str:
        """Вернуть каноничный тип; пустая строка — не определено."""
```

Порядок внутри `classify` ровно по README §2/§10 (первое совпадение):

0. **Нормализация** — регистр, гомоглифы (`С/C`, `Р/P`, `Х/X`, `М/M`, `Е/E`,
   `О/O`, `А/A`, `В/B`, `Т/T`, `Н/H`, `К/K`), `\xa0` → пробел, десятичные
   запятые в размерах → точка. Отдельный модуль `src/parsers/strategies/normalize.py`
   (нужен и тестам).
1. **Нешинные** по слову: `уплотнительн…кольц` → `Уплотнительное кольцо`;
   `камер` → `Автокамера`; `лент` → `Ободная лента`; `диск` → `Диск`
   (переиспользовать `non_tire_product_type`, `tire_category.py:62`).
2. **Шинный размер** → форма размера (README §4): метрический / дюймовый /
   сельхоз / индустриальный / мото.
3. **Спецшина** — маркеры спецтехники и TRA-коды (README §5.1).
4. **Мотошина** — маркеры мото или форма (д) (§5.2).
5. **Грузовая / легкогрузовая / легковая** — по диаметру, PR, двойному индексу,
   оси, суффиксам `C/LT/CP` (§5.3–§5.5).
6. Иначе — `''` (не определено; позиция не метится, но остаётся без типа, как и
   сегодня при пустом заголовке).

Источники признаков, по приоритету:

1. **Структурированные поля позиции** (`row_item.tire.*`, `row_item.identity.title`):
   `diameter`, `width`, `height_percent`, `index_load`, `index_velocity`,
   `construction_type`, `layering`, `tire_type`, `axis`. Если поставщик разобрал
   параметры в колонки — берём их, это устойчивее парсинга строки.
2. **Название** `identity.title` — если полей нет (парсинг регулярками README §6).

Приоритет коллизий — README §8 (явное слово типа > маркеры спец/TRA >
суффикс `C/LT/CP` > грузовой диаметр/PR > легковая).

Каноничные типы — из `product_types.py` (значения совпадают с
`tire_category.CAMERA/DISK/…` и таблицей README §1):

```
Легковая шина, Легкогрузовая шина, Грузовая шина, Спецшина, Мотошина,
Автокамера, Ободная лента, Уплотнительное кольцо, Диск
```

## Сравнение с заявленным типом

Заявленный поставщиком тип = результат текущей стратегии слота `category`
(до перекрытия). Чтобы сравнение не «ложнилось», его надо **привести к
каноничному и отсеять общее**:

- общие/неспецифичные ярлыки — **не сравниваем** (нет расхождения):
  `Автошина`, `Шина`, `Автопокрышка`, `Прочие`, пусто, нераспознанное;
- конкретные ярлыки — канонизируем по таблице README §7
  (`Легковая/SUV/Грязевая` → `Легковая шина`, `Спецтехника/Сельхоз` →
  `Спецшина`, `Мото` → `Мотошина`, …) и сравниваем с вычисленным.

Правило (вынести в `product_types.py: declared_matches(declared, own) -> bool`):

```
own == ''                        → расхождения нет (не определено)
declared пусто/общее/неизвестно  → расхождения нет (README §7 п.4)
declared_canonical == own        → расхождения нет
иначе                            → type_corrected = True
```

Примеры верного срабатывания (из README §11):

- `mim`, лист «Грузовые шины», строка `11.2-20 … 114A6` → declared
  `Грузовая шина`, own `Спецшина` → `*`;
- `zapaska`, `275/65R20`, declared `Легкогрузовая`, own `Легковая` → `*`;
- `four_tochki`, `325/95R24`, declared `Спецшина`, own `Грузовая` → `*`.

## Интеграция в pipeline

`StrategyHooks` (`strategy_hooks.py:15`) получает поле
`product_type: ProductTypeClassifier | None = None`; `CategoryConfig`
(`slot_configs.py:20`) — флаг `independent_type: bool = False`.

Шаг `category` (`base_parser.py:236`) после `apply_category`:

```python
def apply_category(self, row_item: RowItem) -> None:
    declared = self.category_for(row_item)          # заявленный (может быть None)
    if self._strategy_hooks and self._strategy_hooks.product_type is not None:
        own = self._strategy_hooks.product_type.classify(row_item)
        row_item.set_field('type_production', own)
        row_item.set_field('type_corrected', _is_correction(declared, own))
    elif declared is not None:
        row_item.set_field('type_production', declared)
```

- `category_fields` (`CategoryFields`) продолжает работать: он сам считает
  категорию по размеру — после Ф1 источником станет `ProductTypeClassifier`
  (единый расчёт), поле `size_fields` не меняется.
- `zero_rest_without_category` (`base_parser.py:268`) смотрит на
  `type_production`: при включённом слое тип почти всегда будет, это меняет
  поведение zapaska — **проверить тестами** до включения `independent_type` у
  неё.
- `tires_by_size` (`category.py:154`) удаляется вместе с `_tire_size` внутри
  `HeaderRowsCategory`; ветка `tires_by_size` в конфигах переезжает в
  `independent_type`.

## Поле `type_corrected`

- `src/domain/row_item/value_objects.py`: `VendorMeta.type_corrected: bool | None = None`.
- `src/domain/row_item/field_registry.py`: `FieldSpec('type_corrected', VENDOR,
  'type_corrected', row_format.boolean)`.
- `src/domain/row_item/row_item.py`: `type_corrected = RowField('type_corrected')`.
- Тест-инвариант реестра (`tests/test_domain/test_row_item/`) подхватит поле сам.

## Маркер `*` в шаблоне

`ColumnHelper` (`column_helper.py:30`) читает новые ключи:

```python
self.suffix = self.column.get('suffix')
self.suffix_when = self.column.get('suffix_when')
```

`get_value` (`xls_writer.py:17`) после получения `raw_value`:

```python
if col.suffix and col.suffix_when and row_item.get(col.suffix_when):
    return f'{raw_value or ""}{col.suffix}'
```

`for_inner.py:16`:

```python
{'Тип товара': {'style': {'width': 256 * 10},
                'field': RowItem.type_production.name,
                'suffix': '*', 'suffix_when': 'type_corrected'}},
```

Следствие: jsonl собирается по `template.columns()` тем же `get_value`
(`jsonl_writer.py:100`), поэтому `*` попадёт и в jsonl шаблона `for_inner`.
Это ожидаемо (тот же шаблон), но зафиксировать тестом; если нужно только в
xlsx — переносить добавление суффикса в `XlsWriter._write_row`.

## План миграции (фазы)

Каждая фаза — отдельный коммит с зелёными тестами.

| Ф | Содержание | Файлы |
| --- | --- | --- |
| Ф0 | Golden-датасет: перенести аналитический скрипт README §11 в регрессионный прогон по `integration_tests/file_prices_for_test/`; зафиксировать ожидаемые типы и расхождения. Скелет `product_types.py` + `normalize.py` с тестами нормализации | `tests/test_parsers/test_strategies/test_product_type/`, `tasks/` |
| Ф1 | `ProductTypeClassifier` по README §2–§9 (нешинные → формы размеров → спец → мото → грузовая/легкогрузовая/легковая); юнит-кейсы из README §3–§5 и §8 | `src/parsers/strategies/product_type.py`, `normalize.py`, `product_types.py` |
| Ф2 | Флаг `type_corrected`: VO, реестр, `RowField`; golden `to_dict()` обновить | `src/domain/row_item/*` |
| Ф3 | Интеграция слоя: `StrategyHooks.product_type`, `CategoryConfig.independent_type`, `apply_category`, реестр стратегий; удаление `tires_by_size` | `strategy_hooks.py`, `slot_configs.py`, `base_parser.py`, `category.py` |
| Ф4 | Маркер `*`: `ColumnHelper` + `get_value` + `for_inner`; тест xlsx и jsonl | `column_helper.py`, `xls_writer.py`, `for_inner.py` |
| Ф5 | Включение по поставщикам: сверить прогон, включить `independent_type` в `parse_config/vendors/*.json` (начать с `mim`, `zapaska`, `four_tochki`); логирование расхождений и счётчик в `ParserStats` | `parse_config/vendors/*.json`, `parse_statistic.py`, логи |
| Ф6 | Полный CI + `mutmut` по новым модулям; закрыть выживших мутантов | — |

## Критерии готовности

- [ ] Тип товара вычисляется независимо в `ProductTypeClassifier`; поставщику
      не доверяем.
- [ ] `type_production` содержит **свой** тип, без `*`; jsonl и группировка не
      изменились по формату.
- [ ] `type_corrected` выставлен ровно при конкретном расхождении; общие ярлыки
      (`Автошина`) и пустой тип расхождением не считаются.
- [ ] `for_inner` пишет `*` у изменённых типов.
- [ ] Нешинные (камера/лента/кольцо/диск), спец, мото, грузовая,
      легкогрузовая, легковая классифицируются по README §3–§5.
- [ ] Golden-регрессия README §11 воспроизводится: согласие ~94.7 %, кросс-семья
      ~0.6 %.
- [ ] `uv run pytest` (≥ 95 %), `black`, `ruff`, `flake8`, `mypy`,
      `lint-imports`, `vulture`, `bandit`, `pip-audit` — зелёные.
- [ ] Новый тип/синоним добавляется в `product_types.py`, а не по коду класса.

## Риски

1. **Порядок pipeline.** Классификатор зависит от подготовленного `title` и
   разобранных полей; `category` идёт после `title` в дефолтном pipeline, но у
   Пионера порядок иной (`task-11`) — проверить.
2. **`zero_rest_without_category` (zapaska).** Слой почти всегда даёт тип; до
   включения — тест на поведение остатков.
3. **Пионер.** Stateful-заголовки + перестановка шагов: заявленный тип берётся
   из заголовка, свой — по строке; кейсы смешанных разделов
   (`Автокамеры/Ободная лента`) сохранить тестами.
4. **Мото vs мелкая индустрия** — README §11 признаёт объективную неоднозначность
   (`8-11`, `9-11`). Такие кейсы решает явный конфиг/подсказка, а не эвристика;
   зафиксировать списком.
5. **Покрытие 95 %** — новые модули пишутся вместе с тестами.

## Что НЕ делаем

- Не пишем `*` в `type_production` (только визуальный суффикс шаблона).
- Не удаляем `non_tire_product_type`/`map_categories` — переиспользуем.
- Не вводим подтипы (сезон, шипы, ось, TRA, `SUV`/`M/T`) как отдельные
  `type_production` — это атрибуты (README §1, §9).
- Не трогаем наценки, группировку и формат jsonl.
