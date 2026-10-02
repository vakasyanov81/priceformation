# План усиления тестов по данным mutmut

План закрывает дыры, найденные прогоном `mutmut` (`reports/mutmut/mutmut-analysis.json`).
Задачи из [архитектурного плана](./PLAN.md) выполняются независимо от этого документа.

---

## Контекст

Ниже — состояние **до** работ (срез, на котором писался план), и итог **после**:

| | было | стало |
| --- | ---: | ---: |
| мутантов | 4515 | 4269 |
| killed | 3969 | 3977 |
| survived | 543 | 292 |
| timeout | 3 | 0 |
| **mutation score** | **88.0 %** | **93.2 %** |

Score считается как `killed / (killed + survived)`, `timeout` и прочие статусы в
знаменатель не входят.

`mutate_only_covered_lines=true`, поэтому все выжившие мутанты **покрыты** строками — проблема
не в покрытии, а в силе assertions. Это ключевой вывод: добивать покрытие кода бесполезно,
нужно менять характер проверок.

Прогон:

```bash
./pipelines/run_mutation_test.sh
uv run python -m pipelines.mutmut_stats --output-dir reports/mutmut
```

---

## Классификация выживших

| Корзина | Шт. | Доля | Суть |
| --- | ---: | ---: | --- |
| **G. Реальные дыры в тестах** | 325 | 60 % | assertions проверяют не то поведение |
| **F. Схема отчёта без точного сравнения** | 83 | 15 % | `parse_report.py`, `parse_report_build.py` |
| **C. Тексты argparse `help`/`description`** | 41 | 8 % | косметика, тестировать не нужно |
| **B. `encoding='utf-8'`** | 30 | 6 % | эквивалентно, пока локаль UTF-8 |
| **A. `cast(...)`** | 23 | 4 % | аннотация, рантайм-шум |
| **D. Тексты исключений** | 16 | 3 % | сообщения не ассертятся |
| **E. `fake_*` тест-дубли** | 13 | 2 % | мутируются сами фейки |

Классы A, B, C, E — **не дыры**, их правильно убрать из мутации (фаза 1, 107 шт.).
Классы D, F, G — **работы** (фазы 2–9, 436 шт.).

---

## Сводка фаз

| # | Фаза | Что делаем | Убитых мутантов | Приоритет |
| --- | --- | --- | ---: | --- |
| 1 | [Чистка конфига](#фаза-1-чистка-конфига-mutmut) | `do_not_mutate` для `cast`, `encoding`, `help`, `fake_*` | — (убрать 107) | P0 |
| 2 | [Схема отчёта целиком](#фаза-2-схема-отчёта-сравнивать-словарь-целиком) | точное сравнение `empty_stats` / `ok_payload` / `error_payload` / `stats_from_result` | ~60 | P0 |
| 3 | [Байтовый формат jsonl](#фаза-3-байтовый-формат-jsonl) | ассертить сырой текст файла, не `json.loads` | ~35 | P0 |
| 4 | [Диспуты шипа и сезона](#фаза-4-диспуты-шипа-и-сезона) | модуль `common_price_dispute.py` без тестов | ~15 | P0 |
| 5 | [Золотые значения ключа группировки](#фаза-5-золотые-значения-ключа-группировки) | буквальный `group_key`, а не только «равны / не равны» | ~25 | P1 |
| 6 | [Значения листа xlsx](#фаза-6-значения-листа-и-ячеек-xlsx) | имя листа, цвета, `exclude` вместо `call_count` | ~12 | P1 |
| 7 | [Поведение CLI](#фаза-7-поведение-cli-вместо-текстов-help) | `required=True`, inline-форма + флаги, help из реестра | ~8 | P1 |
| 8 | [Вложенные папки и `continue`](#фаза-8-вложенные-папки-и-continue-в-циклах) | `mkdir(parents=True)`, два нечисловых ключа подряд | ~14 | P2 |
| 9 | [Тексты исключений и таймауты](#фаза-9-тексты-исключений-и-таймауты) | 16 мутантов + разбор 3 `timeout` | ~10 | P2 |

**Прогноз (на момент плана):** 4515 → 4408 мутантов, ~169 дополнительно убитых → **~94 %**.

**Факт реализации:** все девять фаз выполнены, контрольный прогон сделан.
Итог: 4269 мутантов, 3977 убито, 292 выжило, 0 `timeout`, score **93.2 %**
(было 88.0 %). Мутантов стало меньше на 246 сильнее, чем ждали (паттерны
`help=`, `encoding=`, `cast\(` подавляют мутации целой строки, а не одну).

Ключевая поправка к прогнозу: часть «выживших» мутантов эквивалентна, и тест
на неё написать нельзя (см. «Эквивалентные мутанты»).


---

## Результаты реализации

Все фазы выполнены. Ниже — что реально дала каждая, по ручной проверке мутаций
скриптом `check_mut.sh` (патч одного мутанта → чистка `__pycache__` → pytest → откат).

| Фаза | Проверено вручную | Итог |
| --- | ---: | --- |
| 1 | — | конфиг изменён: 4515 → 4269 мутантов (−246) |
| 2 | 14 | 14 убиты |
| 3 | 16 | 13 убиты, 3 эквивалентны |
| 4 | 17 | 3 убиты, 14 эквивалентны |
| 5 | 15 | 13 убиты, 2 эквивалентны/нестабильны |
| 6 | 11 | 10 убиты, 1 эквивалентен |
| 7 | 5 | 5 убиты |
| 8 | 5 | 5 убиты |
| 9 | 9 | 9 убиты, 3 `timeout` закрыты |

### Находки, которых не было в плане

**Stale `__pycache__` — главная находка.** mutmut 3.8.0 правит файл в `src/`
и не чистит `.pyc`. Если кэш от предыдущего прогона лежит рядом, тесты
импортируют мутированный модуль уже после отката source: размер файла и
секунда mtime совпадают, выглядит как «мутация не применилась».
Следствия, зафиксированные в репозитории:

- `pipelines/run_mutation_test.sh` чистит `src/**/__pycache__` до и после
  прогона и выставляет `PYTHONDONTWRITEBYTECODE=1`;
- то же описано в `pipelines/mutmut_stats/README.md`;
- `uv run mutmut run` нельзя запускать параллельно с `uv run pytest`.

**`help=` подавляет мутантов, а не «съедает 4 мутанта».** Паттерн `help=`
совпадает со строкой целиком, поэтому подавляет все мутации на ней, а не
только текстовые. Аналогично `encoding=` и `cast\(`. Ровно поэтому ожидаемые
4408 мутантов — оценка, а не факт.

**Мутация `to_none` убирает вызов `input()` целиком.** Из-за этого
`ask_action` с `answer = None` крутит `while True` вообще без ввода: подсказка
логируется бесконечно. Лечится заглушкой `input` в тесте — `_dialog_input`
падает с `AssertionError`, когда ответы кончились, поэтому диалог не виснет.

**Тест на импорт вендора ломается в clean-прогоне mutmut.** `test_registry.py`
импортирует стаб-модуль `tests.test_parsers._registry_import_vendor` ради
проверки `_ensure_vendors_imported()`. В обычном прогоне модуль ещё не импортирован,
и всё в порядке; mutmut же сначала прогоняет `--collect-only`, после чего модуль
лежит в `sys.modules`, повторный импорт не выполняется, регистрация не происходит —
и clean-тесты падают с `Failed to run clean test`. Лечится вычисткой модуля из
`sys.modules` перед импортом и сверкой по имени класса, а не по идентичности
объекта: при повторном импорте это разные объекты.

**`mkdir(parents=True)` не проверяется «папкой, которой ещё нет».** Первый
написанный тест на вложенный путь использовал `tmp_path / 'nested' / 'zapaska'`,
а мутант `exist_ok=False` на нём выживал: `parents=True` и создаёт
промежуточные папки, и `exist_ok` касается только конечной. Нужны два разных
теста — вложенный путь и повторный вызов в уже существующую папку.

### Эквивалентные мутанты

Эти нельзя убить тестом, тест на них невозможен:

- **`_extend_meta` / `ensure_ascii=True`** в `jsonl_writer.py`: финальный файл
  перезаписывает `_save_values`, поэтому промежуточная запись метаданных
  в экранированном виде не наблюдаема.
- **14 мутантов `common_price_dispute.py`**: внутренние каноны используются
  только для подсчёта числа различных значений и нигде не сравниваются с
  литералами, поэтому смена регистра или неинъективная перенумерация
  не меняют результат.
- **`sorted(unique, key=None, reverse=True)`** в `group_key`: порядок обхода
  `set` зависит от hash seed, поведение мутанта нестабильно между прогонами.
- **`intimacy.upper() → .lower()`** в `group_key`: значение тут же приводится
  к верхнему регистру в `camera_key`.
- **`if not column_name and column_name not in product`** в `_get_color`:
  чтобы различить ветви, нужен шаблон, у которого `by_column` — пустая строка,
  а продукт содержит ключ `''`.
- **`_get_color` для неизвестного поставщика**: `or '' → 'XXXX'` даёт тот же
  результат, потому что неизвестный поставщик и так отображается в `''`.

Итог по критерию фазы 4 «выживших ≤ 2» был неверен: модуль содержит 14
эквивалентных мутантов, и добивать их не нужно.

---

## Фаза 1: Чистка конфига mutmut

### Проблема

107 выживших — не эквивалентные мутации, а мутации кода, который не меняет поведение:

- `cast(X, y)` — аннотация для mypy, в рантайме ничего не делает. Мутировать нечего.
  23 шт.: `common_price_output.py`, `parse_orchestrator.py`, `xls_reader.py`, `column_helper.py`, `run_argv.py`.
- `encoding='utf-8'` → `None` / `'UTF-8'` — при `locale.getpreferredencoding() == 'UTF-8'`
  результат идентичен. 30 шт. в 9 файлах.
- `help=`, `description=`, `metavar=` — тексты argparse. 41 шт. в `run_argv.py`,
  `run_dialog.py`.
- `fake_xls_reader.py`, `fake_json_reader.py`, `writer/fake_driver.py` — тест-дубли.
  13 шт. мутаций внутреннего состояния фейков.

### Решение

`pyproject.toml`, секция `[tool.mutmut]`:

```toml
do_not_mutate = [
    "src/infrastructure/logging/wrappers.py",
    "src/services/async_utils.py",
    "src/infrastructure/logging/console.py",
    "src/infrastructure/logging/exception_logging.py",
    "src/infrastructure/logging/file_logging.py",
    "src/infrastructure/logging/json_mode.py",
    "src/infrastructure/logging/log_resolve.py",
    "src/infrastructure/logging/log_setup.py",
    "src/parsers/base_parser/log_parser_process.py",
    # Фейки: мутируем их внутреннее состояние, а не тесты, которые их проверяют.
    "src/parsers/fake_xls_reader.py",
    "src/parsers/fake_json_reader.py",
    "src/parsers/writer/fake_driver.py",
]
do_not_mutate_patterns = [
    'logger\.\w+',              # тексты логов проверяются снаружи
    'cast\(',                    # аннотация, не рантайм
    'encoding=',                 # эквивалентно при locale == UTF-8
    'help=',
    'description=',
    'metavar=',
]
```

### Критерии готовности

- [x] `mutmut run` даёт 4269 мутантов (ожидалось 4408) и score 93.2 % при 3977 killed
      (было 3969 при 4515).
- [x] Комментарии в `pyproject.toml` объясняют, почему каждая строка подавлена.
- [x] `help=` не съел ничего поведенческого: мутанты `_result_template_help`
      добиты тестом фазы 7 (4 из 4 убиты).

---

## Фаза 2: Схема отчёта — сравнивать словарь целиком

### Проблема

83 выживших в `src/parse_report.py` (67) и `src/parse_report_build.py` (16):

| Функция | Выживших |
| --- | ---: |
| `empty_stats` (`parse_report.py:55`) | 37 |
| `stats_from_result` (`parse_report_build.py:14`) | 14 |
| `error_payload` (`parse_report.py:93`) | 13 |
| `emit_json` | 8 |
| `dump_json` | 5 |
| `ok_payload` (`parse_report.py:69`) | 4 |
| прочие | 2 |

`tests/test_cli/test_parse_report.py:124-151` проверяет **по одному ключу**:

```python
assert stats['items'] == 1
assert stats['doubles'] == 1
```

Поэтому не видно ни переименования ключа (`'items' → 'ITEMS'` / `'XXitemsXX'`), ни мутации
значения (`0 → 1`), ни вложенных словарей (`percent_markup`, `absolute_markup`).
`error_payload` проверяется на 4 ключа из 9.

Модуль сам декларирует контракт — `JsonReport` TypedDict в `parse_report.py:22` и docstring
«Стабильная схема ответа CLI». Схема, на которую опирается Django, и должна быть закреплена
точным сравнением.

### Решение

Один тест на функцию, полное сравнение словаря:

```python
def test_empty_stats_exact() -> None:
    """все ключи и значения нулевой статистики — контракт для внешних скриптов."""
    assert empty_stats(1.234) == {
        'items': 0,
        'priced_items': 0,
        'doubles': 0,
        'unknown_category_skips': 0,
        'black_list_skips': 0,
        'elapsed_seconds': 1.23,
        'percent_markup': {'min': 0, 'max': 0},
        'absolute_markup': {'min': 0, 'max': 0},
    }
```

Аналогично:

- `test_ok_payload_exact` — все 9 ключей `ok_payload`;
- `test_error_payload_exact` — все 9 ключей не-compact ветки (существующий
  `test_error_payload_stable_keys` оставить как пример для читателя, либо заменить);
- `test_stats_from_result_exact` — полный словарь на непустом `ParseResult`, включая
  `percent_markup` / `absolute_markup`;
- `test_dump_json_keeps_cyrillic` — `dump_json({'a': 'шина'})` содержит `шина`, а не `\u0448`.

### Проверено

Ручная мутация, тест падает в обоих случаях:

| Мутация | Результат |
| --- | --- |
| `'items': 0` → `'items': 1` | KILLED |
| `'percent_markup': {'min': 0, …}` → `{'min': 1, …}` | KILLED |
| `dump_json`: `ensure_ascii=False` → `True` | KILLED |

### Критерии готовности

- [x] На каждый из 4 конструкторов отчёта есть тест с полным `==` словаря.
- [x] `test_dump_json_keeps_cyrillic` присутствует (убивает 3 мутанта `ensure_ascii`).
- [x] 14 из 14 проверенных вручную мутантов убиты.

---

## Фаза 3: Байтовый формат jsonl

### Проблема

49 выживших в `jsonl_writer.py` (29), `jsonl_codes.py` (16), `jsonl_codeable.py` (4).

`tests/test_parsers/test_writer/test_jsonl_writer.py` **везде** читает файл через
`json.loads(...)` и проверяет распарсенный объект. Формат файла при этом ничем не закреплен:

| Что не видно | Мутантов |
| --- | ---: |
| `separators=_SEPARATORS` (`jsonl_writer.py:50`) — компактность строки | 7 |
| `ensure_ascii=False` — кириллица уедет в `\uXXXX` | 21 (3 файла) |
| `strftime('%Y-%m-%d') → '%y-%m-%d'` (`jsonl_writer.py:38`) — имя файла | 3 |
| `read_value_codes`: `loaded.get(VALUES_KEY)` (`jsonl_codes.py:42`) | 2 |
| `_save_values`: `loaded.pop(VALUES_KEY, None)` (`jsonl_codes.py:105`) | 2 |
| `_assign_keys` / `_read_meta` / `_title_keys`: `continue → break` | 3 |
| `_count_cells`: `or → and` (`jsonl_codes.py:62`) | 1 |
| `usable_codes` — переиспользование кодов | 4 |
| прочее | 7 |

Файл `.jsonl` — внешний контракт (его читает Django), имя файла с датой — тоже.

### Решение

```python
def test_jsonl_raw_bytes(tmp_path: Path) -> None:
    """jsonl: компактный JSON, кириллица литералом, вложенная папка создаётся."""
    row = {'title': '225/40R18', 'type_production': 'Автошина', 'price_markup': 3980.0}
    path = write_template_jsonl([row], ForInner, str(tmp_path / 'nested' / 'deeper'))
    text = Path(path).read_text(encoding='utf-8')
    assert 'Автошина' in text       # ensure_ascii=False
    assert '\\u' not in text
    assert '": ' not in text        # компактные separators
    assert text.endswith('\n')
```

Плюс отдельными тестами:

- `test_jsonl_file_name_has_full_year` — имя файла через `monkeypatch` на `datetime`
  или `freezegun`-подобной подмене; проверяем `%Y` (четыре цифры), не `%y`;
- `test_value_codes_survive_second_write` — после второго `write_template_jsonl`
  словарь `values` в `result_meta.json` **не теряется** (убивает `read_value_codes` → `None`);
- `test_meta_without_codes_drops_values` — если кодов нет, ключ `values` удаляется
  (убивает `_save_values` → `pop(None, None)`);
- `test_meta_ignores_two_non_numeric_keys` — в `result_meta.json` лежат **два**
  нечисловых ключа; оба пропускаются, а не прерывают разбор (убивает `continue → break`).

### Проверено

| Мутация | Результат |
| --- | --- |
| убрать `separators=_SEPARATORS` | KILLED |
| `ensure_ascii=False` → `True` | KILLED |
| `folder.mkdir(parents=True, exist_ok=True)` → `mkdir(exist_ok=True)` | KILLED |

### Критерии готовности

- [x] Есть хотя бы один тест, читающий `.jsonl` **как текст**, а не через `json.loads`.
- [x] Имя jsonl-файла проверяется с зафиксированной датой.
- [x] 13 из 16 проверенных вручную мутантов убиты; 3 эквивалентны.

---

## Фаза 4: Диспуты шипа и сезона

### Проблема

`src/parsers/common_price_dispute.py` — **17 выживших и ноль тестов**: модуль не
упоминается ни в одном файле `tests/`, но покрыт по линиям (вызывается из
`CommonPriceOut` при полном разборе).

Внутри — словари синонимов и канонические метки:

```python
if text in {'да', 'yes', 'ш.'}:   return 'да'
if text in {'нет', 'no'}:        return 'нет'
if text in {'зима', 'зимняя'}:   return 'зимняя'
if text in {'лето', 'летняя'}:   return 'летняя'
```

Ни одна мутация не видна: `'ЗИМНЯЯ'`, `'ш.' → 'Ш.'`, `', ' → 'XX, XX'` в `dispute_note`.

### Решение

Один параметризованный тест на модуль:

```python
@pytest.mark.parametrize(
    ('fields', 'expected'),
    [
        ({'spike': 'да'}, {'spike': 'нет'}, 'шип'),
        ({'spike': 'да'}, {'spike': 'Ш.'}, ''),            # синонимы схлопываются
        ({'season': 'зимняя'}, {'season': 'лето'}, 'сезон'),
        ({'season': 'ЗИМНЯЯ'}, {'season': 'зима'}, ''),     # регистр не конфликт
        ({'spike': 'да'}, {'spike': 'да'}, ''),            # одинаковые — не конфликт
    ],
)
def test_dispute_note(...): ...
```

Плюс тест на объединение меток: `spike да/нет` + `season зима/лето` → `'шип, сезон'`
(убивает мутацию разделителя в `dispute_note`).

### Критерии готовности

- [x] `common_price_dispute` покрыт параметризованным тестом.
- [x] Поведенческие мутанты убиты (3 из 17). Остальные 14 эквивалентны —
      исходный критерий «выживших осталось 2» был неверен, см. «Эквивалентные мутанты».

---

## Фаза 5: Золотые значения ключа группировки

### Проблема

40 выживших: `common_price_group_key.py` (16), `common_price_group_fields.py` (18),
`common_price_size.py` (6).

`tests/test_parsers/test_common_price_group_key.py` — 39 тестов, и они **реляционные**:
«X группируется с Y», «Z — нет». Для таких утверждений принципиально невидимы:

- `mark = (row_item.manufacturer or '').lower()` → `or 'XXXX'` (25 мутантов `or '' → or 'XXXX'`);
- `.lower()` → `.upper()` (25 мутантов `method_swap`);
- `clear_model(row_item.model, mark, brand)` (`common_price_group_key.py:89`) —
  **перестановка аргументов** `mark` / `brand` даёт тот же результат в тестах;
- `canon_number(row_item.height_percent)` → `canon_number(None)`;
- `_model_prefixes`: `sorted(unique, key=len, reverse=True)` — порядок не проверяется,
  хотя именно он решает, какой префикс срежется первым;
- `canon_diameter`: `count=1` → `count=2` (`re.sub` заменяет только первое вхождение).

### Решение

1–2 теста с **буквальным** ключом на канонической строке:

```python
def test_group_key_exact() -> None:
    row = RowItem({
        'title': '225/40R18 KAMA PRO 205 TL', 'manufacturer': 'KAMA', 'brand': 'KAMA',
        'model': 'KAMA PRO 205', 'width': '225', 'height_percent': '40',
        'diameter': '18', 'type_production': 'Автошина',
    })
    assert group_key(row, {}) == (
        'автошина', '225', '18', '', '40', '', '', 'pro205',
        '', '', 'kama', '', '', '', '', '',
    )
```

Плюс:

- `test_clear_model_strips_longest_prefix_first` — `manufacturer='KAMA PRO'`,
  `model='KAMA PRO 205'` → `'205'`; если бы сортировка исчезла, результат отличается;
- `test_canon_diameter_replaces_only_first_prefix` — title с двумя `R`
  (`'225/40R18 R17'`): меняется только первое вхождение;
- `test_group_key_drops_manufacturer_but_keeps_brand` — строка, где `manufacturer`
  и `brand` различаются и оба попадают в модель; ловит перестановку аргументов
  в `clear_model`.

### Критерии готовности

- [x] Есть тест с буквальным `group_key` на полной строке.
- [x] `clear_model` различает `manufacturer` и `brand` (тест, где они не равны).
- [x] 13 из 15 проверенных вручную мутантов убиты; 2 эквивалентны/нестабильны.

---

## Фаза 6: Значения листа и ячеек xlsx

### Проблема

19 выживших в `xls_writer.py`. `tests/test_parsers/test_writer/test_writer.py:17-38`
проверяет **только `call_count`** заглушенных методов драйвера:

```python
with patch(method) as mock_method:
    ...
    XlsWriter(...).write()
assert mock_method.call_count == call_count
```

Отсюда живут:

- `self.driver.add_sheet('price')` (`xls_writer.py:72`) → `'PRICE'` — **имя листа**;
- `self.exclude = self.template.exclude()` (`xls_writer.py:63`) → `None`;
- `cell_color = color[0] if color and color[1] == col_index else None`
  (`xls_writer.py:122`) — `color[0]` → `color[1]`, `==` → `!=`, `or` → `and`;
- `_get_color`: `or → and`.

Имя листа — пользовательский контракт: файл открывают в Excel.

### Решение

Тест, который читает состояние `FakeXlwtDriver` после `write()`:

```python
def test_write_sheet_name_and_cells(tmp_path: Path) -> None:
    driver = FakeXlwtDriver()
    XlsWriter(driver, write_data, template=FixtureTemplate, result_folder=str(tmp_path)).write()
    assert driver.sheet_name == 'price'
    assert driver.body == result_body_fixture
```

`result_body_*` уже есть в `tests/test_parsers/test_writer/fixtures.py:31-50` — данные
посчитаны вручную, осталось их зафиксировать в ассерте. Отдельно:

- `test_write_applies_column_colors` — `ColorsWithoutMapTemplate` и шаблон с непустой
  картой: цвет ставится в нужную колонку;
- `test_write_respects_template_exclude` — колонка из `exclude()` не попадает в лист.

### Критерии готовности

- [x] Есть тест, ассертящий `driver.sheet_name` и `driver.body`.
- [x] 10 из 11 проверенных вручную мутантов убиты; 1 эквивалентен.

---

## Фаза 7: Поведение CLI вместо текстов help

### Проблема

57 выживших в `run_argv.py`, из них 41 — тексты `help` (закрываются фазой 1) и
**16 поведенческих**:

| Что | Мутантов | Где |
| --- | ---: | --- |
| `add_subparsers(..., required=True)` → `False` / `None` / убрано | 3 | `run_argv.py:60` |
| `*argv[1:]` → `*argv[2:]` | 1 | `run_argv.py:106` |
| `_result_template_help`: `available` / `defaults` → `None` | 4 | `run_argv.py:110-113` |
| тексты `help=` у `load_supplier_prices` / `load_config` | 8 | `run_argv.py:71-84` |

`tests/test_cli/test_run_argv.py` покрывает сценарии с флагами, но не проверяет
обязательность подкоманды и не комбинирует inline-форму с флагами.

### Решение

```python
def test_no_command_is_error() -> None:
    """пустой argv — ошибка argparse, а не молчаливый Namespace(command=None)."""
    with pytest.raises(SystemExit) as exit_info:
        parse_machine_args([])
    assert exit_info.value.code == 2


def test_inline_keeps_extra_flags() -> None:
    """load_config=path разворачивается в команду, хвост argv не теряется."""
    args = parse_machine_args(['load_config=/p/black_list', '--json'])
    assert args.command == 'load_config'
    assert args.config == '/p/black_list'
    assert args.json is True


def test_help_lists_all_writer_templates() -> None:
    """--help перечисляет все зарегистрированные шаблоны записи."""
    text = parser_help(PARSE)
    for name in writer_templates_by_name():
        assert name in text
```

Последний тест ловит дрейф реестра шаблонов — единственная причина считать
`_result_template_help` не-косметикой: текст строится из `writer_templates_by_name()`.

### Проверено

| Мутация | Результат |
| --- | --- |
| `required=True` → `required=False` | KILLED |
| `*argv[1:]]` → `*argv[2:]]` | KILLED |

### Критерии готовности

- [x] Есть тест на пустой argv (`SystemExit(2)`).
- [x] Есть тест на inline-форму **с флагом** после неё.
- [x] 5 из 5 проверенных вручную мутантов убиты.

---

## Фаза 8: Вложенные папки и `continue` в циклах

### Проблема

**15 одинаковых мутантов** `mkdir(parents=True, exist_ok=True)`: во всех существующих
тестах родительская папка уже есть, поэтому `parents=True → False` эквивалентно.

| Файл | Строка |
| --- | --- |
| `src/parsers/load_config.py` | 74 (`_move_config`) |
| `src/parsers/load_supplier_prices.py` | 88 (`_move_price`) |
| `src/parsers/remote/zapaska_client.py` | 57 (`download_catalogs`) |
| `src/parsers/writer/jsonl_writer.py` | 31 (`write_template_jsonl`) |
| `src/parsers/writer/xls_writer.py` | 70 (`XlsWriter.write`) |

Плюс 5 мутантов `continue → break` в циклах, которые должны **пропускать** плохие записи
и идти дальше: `_assign_keys`, `_read_meta` (`jsonl_writer.py`),
`_filled_aliases`, `drop_blank_aliases` (`manufacturer_aliases.py`). Выживают, потому что
тестам хватает **одной** плохой записи — `break` и `continue` дают тот же результат.

### Решение

1. В одном тесте на каждый `mkdir` использовать путь на два уровня глубже `tmp_path`
   (`tmp_path / 'a' / 'b'`). Для jsonl это уже сделано в фазе 3.
2. В тестах на парсер алиасов и на чтение `result_meta.json` — **две** невалидные записи
   подряд, а не одна.

### Критерии готовности

- [x] Есть отдельные тесты на вложенный путь и на повторный вызов в готовую
      папку: одного теста на вложенный путь недостаточно (см. «Находки»).
- [x] Есть тест с двумя невалидными записями подряд для алиасов и для `result_meta.json`.

---

## Фаза 9: Тексты исключений и таймауты

### Проблема

**16 выживших** — тексты в конструкторах исключений:

- `WorkbookNotInitializedError`, `WorksheetNotInitializedError` (`xwlt_driver.py`);
- `JsonPriceNotListError`, `MarkupPolicyNotSetError`, `MaxRowsReached`, `CoreExceptionError.to_log`;
- `ParsePathsNotConfiguredError`;
- `ConfigFileNotFoundError` / `InvalidConfigJsonError` (`load_config.py`).

Тексты исключений в этом проекте **значимы**: коммит `7753afc` —
«fix: понятное сообщение при битом correct-nomenclature.xlsx вместо сырого стектрейса».
Пользователь читает эти сообщения, значит их стоит закреплять.

**3 мутанта в статусе `timeout`** — не `survived`. Это отдельная проблема: mutmut не
различает «тест упал» и «тест не успел за лимит». Нужно найти их номера в
`mutants/mutmut-stats.json` и проверить вручную.

### Решение

Точечные проверки сообщений там, где текст меняли намеренно:

```python
def test_max_rows_message_includes_limit() -> None:
    assert '500' in str(MaxRowsReached(500))
```

Остальное (`workbook is not initialized`, `Parse paths are not configured`) — либо
закрепить, либо осознанно оставить выжившим как эквивалентные.

### Критерии готовности

- [x] Тексты изменённых намеренно исключений закреплены тестами.
- [x] Каждый из 3 `timeout` разобран вручную: убит тестом или признан ложным.

---

## Обслуживание

Мелочи, которые видно рядом с прогоном:

| Проблема | Файл |
| --- | --- |
| Скрипт заканчивается на закомментированной `# mutmut run` — ничего не запускает | `pipelines/run_mutation_test.sh` |
| `reports/` не в `.gitignore` (в отличие от `mutants`), артефакты попадут в git | `.gitignore` |
| `pipeline` выводит score как `killed / (killed + survived)`, `timeout` в знаменатель не входит | `pipelines/mutmut_stats/aggregate.py` |

Правки: раскомментировать `mutmut run` (со `set -euo pipefail`), добавить `reports/`
в `.gitignore`, задокументировать формулу score в `pipelines/mutmut_stats/README.md`.

Дополнительно, по итогам контрольного прогона: чистка `__pycache__` в
`pipelines/run_mutation_test.sh` до и после запуска, `PYTHONDONTWRITEBYTECODE=1` и
изоляция `test_registry.py` от `sys.modules` (см. «Находки, которых не было в плане»).

---

## Проверки после каждой фазы

Полный набор из корня, порядок — из `.github/workflows/python-app.yml`:

```bash
uv run pytest                                     # порог покрытия 95 %
uv run black --check --diff .
uv run ruff check .
uv run flake8 .
uv run mypy .
uv run vulture
uv run bandit -r src -c pyproject.toml
uv run pip-audit
```

Плюс после фаз 1, 2–8 — контрольный прогон мутаций (только когда pytest не запущен):

```bash
./pipelines/run_mutation_test.sh
uv run python -m pipelines.mutmut_stats --output-dir reports/mutmut
```

Комментарии и docstring в новых тестах — на русском, кавычки одинарные, line-length 120
(`.pi/AGENTS.md`).

---

## Чего сознательно не делаем

- **Не добирать покрытие строк.** `mutate_only_covered_lines=true`; все выжившие уже
  покрыты. Проблема в силе assertions, а не в покрытии.
- **Не тестировать тексты `help` / `description` argparse** (41 мутант) — они не влияют
  на поведение; подавляются в фазе 1.
- **Не тестировать `cast()`** — аннотация, не рантайм.
- **Не бороться с `encoding=None`.** Пока локаль UTF-8, это эквивалентно; менять поведение
  через `monkeypatch` локали дороже, чем честно подавить паттерн с комментарием.
- **Не гнаться за 100 %.** Потолок ~97 %; дальше — тексты исключений и мутации
  `rsplit(..., maxsplit=N)` при фиксированной глубине модулей.
