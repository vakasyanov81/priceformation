# План усиления тестов по данным mutmut

Актуальный срез — прогон от 2026-10-08: `mutants/mutmut-analysis.json`
(сгенерирован `uv run python -m pipelines.mutmut_stats`).
Предыдущая кампания описана в разделе [История](#история-предыдущей-кампании);
её отчёт лежит в `reports/mutmut/`.

Задачи из [архитектурного плана](./PLAN.md) выполняются независимо от этого документа.

---

## Контекст

| | 2026-09-28 (прошлая кампания) | 2026-10-08 (текущий срез) |
| --- | ---: | ---: |
| мутантов | 4269 | 5651 |
| killed | 3977 | 5013 |
| survived | 292 | 627 |
| timeout | 0 | 11 |
| **mutation score** | **93.2 %** | **88.9 %** |

Score считается как `killed / (killed + survived)`; `timeout` и прочие статусы
в знаменатель не входят.

**Почему score упал.** После прошлой кампании в код добавились новые модули —
типизированные конфиги (`parsers/vendor_config/`), стратегии
(`parsers/strategies/`), DI-обвязка (`base_parser/strategies_integration.py`,
`config_driven_parser.py`, `services/parse_orchestrator.py`). Мутантов стало
больше на 1382, а тесты на новый код слабее: они проверяют, что разбор
«прошёл успешно», но не закрепляют ни путь ошибки, ни каждое прокачиваемое
поле. Поэтому план ниже целится прежде всего в новый код, а не в уже
закрытые кластеры прошлой кампании.

`mutate_only_covered_lines=true`, поэтому все 627 выживших лежат на строках,
которые тесты **исполняют**. Вывод тот же, что и в прошлой кампании: дело
не в покрытии, а в силе assertions. Добивать строки бесполезно, надо менять
характер проверок.

Прогон:

```bash
just mutate                                                   # pipelines/run_mutation_test.sh
uv run python -m pipelines.mutmut_stats --output-dir reports/mutmut
```

---

## Классификация выживших

### По коду

| Кластер | Шт. | Файлы |
| --- | ---: | --- |
| Типизированные конфиги | 129 | `parsers/vendor_config/`, `parsers/data_provider/` |
| Хелперы шин и дисков | 90 | `strategies/_four_tochki_*_helper.py`, `_autosnab_helper.py` |
| `base_parser` + строка + интеграция стратегий | 136 | `base_parser/` |
| Прочие стратегии | 55 | `strategies/title.py`, `category.py`, `pricing_registry.py`, `title_registry.py`, `markup_policy.py` |
| DI, оркестратор, реестр | 32 | `services/parse_orchestrator.py`, `parsers/registry.py` |
| CLI и интерактив | 68 | `run.py`, `run_argv.py`, `run_machine.py`, `run_dialog/` |
| Writer и отчёт | 33 | `parsers/writer/`, `parse_report.py` |
| Группировка и диспуты | 34 | `common_price_group_*`, `common_price_size.py`, `common_price_dispute.py` |
| XLS-ридер | 14 | `parsers/xls_reader*.py` |
| Домен/инфраструктура/загрузчики | 22 | `domain/`, `infrastructure/`, `parsers/load*` |
| Прочее | 14 | `common_price_grouper.py`, `json_reader.py`, `cfg/__init__.py`, … |

### По причине

Классификация ниже — сквозная (каждый выживший ровно в одной строке), поэтому
сумма ровно 627; она не совпадает с разбивкой по файлам выше, но покрывает её.

| Класс | Шт. | Суть | Что делать |
| --- | ---: | --- | --- |
| **A. Путь ошибки (`where`) в конфигах** | 80 | `where` попадает только в текст `ConfigValidationError`; тесты матчат подстроку без пути | ✅ фаза 1: ассерт пути (в паре с B убито 120, 2 экв. → фаза 7) |
| **B. Поля слотов конфига** | 47 | `read_flag(...) → None`, имя ключа → `'XX...'`; значение не проверяется вниз по потоку | ✅ фаза 1: полное равенство dataclass |
| **C. Канонизация строк** | 109 | `.replace(',', '.')`, `'—'`, `'усил'`, `'RZ'`, `or '' → 'XXXX'` | тест: неканонический вход |
| **D. Прокачка аргументов/хуков** | 237 | `StrategiesIntegration`, `config_driven_parser`, `_enrich_row_item`, `make_*_strategy`, `set_field(...)` | тест: ассертить поля/хуки |
| **E. Операторы и границы** | 85 | `operator` 43, `number` 18, `keyword` 17, `method_swap` 11 | тест: таблица истинности |
| **F. UI/платформенный текст** | 37 | `_attach_commands` (описания позиционно), `run_dialog/readers.py` | подавить (фаза 0 закрыла 31, остаток readers — фаза 6) |
| **H. Тексты исключений** | 16 | `WorkbookNotInitializedError`, `JsonPriceNotListError`, … | тест текста |
| **I. Эквивалентные** | 16 | диспуты шипа/сезона, `ensure_ascii`, `_extend_meta` | задокументировать |

Итого 627. Классы A–E и H — работы (≈574 шт.), F и I (≈53) — ненаблюдаемы
или эквивалентны. Класс D — самый крупный и самый «размазанный»: он
распределён по фазам 2–4.

---

## Сводка фаз

| # | Фаза | Класс | Убитых (оценка) | Приоритет |
| --- | --- | --- | ---: | --- |
| 0 | [Чистка конфига mutmut](#фаза-0-чистка-конфига-mutmut) | F | −31 выживший ✅ | P0 |
| 1 | [Путь ошибки и полное сравнение слотов](#фаза-1-конфиг-путь-ошибки-и-полное-сравнение-слотов) | A, B | 120 убито ✅ | P0 |
| 2 | [Канонизация размеров и хвостов](#фаза-2-канонизация-размеров-и-хвостов) | C | ~90 | P0 |
| 3 | [Прокачка аргументов и DI](#фаза-3-прокачка-аргументов-и-di) | D | ~120 | P1 |
| 4 | [Логика и границы предикатов](#фаза-4-логика-и-границы-предикатов) | E | ~85 | P1 |
| 5 | [Контракт отчёта и writer](#фаза-5-контракт-отчёта-и-writer) | D, E | ~25 | P2 |
| 6 | [CLI, интерактив, тексты исключений](#фаза-6-cli-интерактив-тексты-исключений) | H | ~35 | P2 |
| 7 | [Эквивалентные мутанты](#фаза-7-эквивалентные-мутанты) | I | — | P2 |

**Прогноз:** 5651 → ~5575 мутантов (фаза 0 уже убрала 76 из генерации),
~500 убитых → **~96 %**.

---

## Фаза 0: Чистка конфига mutmut ✅ (2026-10-08)

### Проблема

31 выживший (класс F) — не дыры в тестах, а мутации ненаблюдаемого текста:

- **`run_argv._attach_commands` (24 шт.)**: описания подкоманд передаются
  **позиционно** в `_json_parser(subparsers, json_flag, PARSE, 'Разобрать …')`,
  поэтому существующий паттерн `help=` их не ловит. Это тот же случай, что
  закрытые в прошлой кампании `help=`/`description=`: текст виден только в
  `--help`, поведение разбора от него не зависит.
- **`run_dialog/readers.py` (7 шт.)**: `'ignore'`, `utf-8`, `'msvcrt'` —
  константы терминального ввода; тесты подменяют источник символов
  (`read_char` / `getwch` приходят параметрами). Ещё 6 выживших readers
  (`\x1b`, `\x00`, обёртки `KeyPress`) — в `read_unix_key` /
  `read_windows_key`, их добивает фаза 6.

### Решение

`pyproject.toml`, секция `[tool.mutmut]` — четыре построчных паттерна:

```toml
do_not_mutate_patterns = [
    # ... существующие строки (cast(, encoding=, help=, description=, metavar=) ...
    # Описания подкоманд в run_argv._attach_commands передаются позиционно,
    # поэтому help= их не ловит: текст виден только в --help, разбор от него
    # не зависит. Паттерн построчный — покрывает однострочные вызовы.
    '_json_parser\(subparsers, json_flag,',
    # Те же описания в многострочных вызовах: строка-аргумент целиком состоит
    # из help-предложения. Сегодня в src только две такие строки (run_argv).
    '''^\s*'.+\.\',$''',
    # Платформенные константы чтения терминала: тесты подменяют источник
    # символов, эти две строки в тестовом окружении не исполняются.
    '''\.decode\('utf-8', 'ignore'\)''',
    '''import_module\('msvcrt'\)''',
]
```

Паттерн построчный, поэтому readers-паттерны сделаны точечными: широкий
вариант из первоначального проекта (`'ignore'|\bmsvcrt\b|\butf-8\b`) совпал бы
с посторонними строками в других файлах src. Проверено: под новыми паттернами
лежат ровно 8 строк — 6 в `run_argv` и 2 в `readers`, больше нигде.

`where`, `help`-подобные строки исключений и `or 'XXXX'` **не подавлять** —
они проверяемы (фазы 1, 2, 6).

### Что подавляется и что это даёт (замерено, не оценка)

Сравнение генерации `create_mutations` с 6 старыми паттернами и со всеми 10:

| Файл | без новых | с новыми | Δ |
| --- | ---: | ---: | ---: |
| `src/run_argv.py` | 160 | 101 | −59 |
| `src/run_dialog/readers.py` | 71 | 54 | −17 |
| **Итого** | **231** | **155** | **−76** |

Из 76: ровно 31 — выжившие (всё, что и было целью), 45 — уже убитые.
Подавление построчное, поэтому под строкой исчезают и тривиально убитые
мутанты на ней же (`parse_cmd = None`, `arg → None`, удаление аргументов).
Прогноз эффекта: killed 5013 → 4968, survived 627 → 596,
score **88,9 % → 89,3 %** (точный замер — после следующего `just mutate`).

**Отклонённая альтернатива** — вынести описания в константы уровня модуля
(в стиле существующих `_PRICES_HELP`): mutmut код уровня модуля не мутирует,
но `operator_arg_removal` генерирует `arg → None` для каждого аргумента, и
новый вызов `_json_parser(subparsers, json_flag, PARSE, _CMD_PARSE_HELP)`
получил бы мутанта `help=None`, который выживает (argparse допускает None).
Снялось бы 18 из 24, а не все 24, коллатерал в readers — тот же. Форма
данных здесь не даёт выигрыша, поэтому остаёмся на конфиге.

### Критерии готовности

- [x] Генерация теряет 31 выжившего (76 мутантов), score не падает:
      31/76 — замерено на `create_mutations`, выжившие придут в `interesting`
      ровно 596; контрольный прогон `just mutate` — при следующем замере.
- [x] Каждый паттерн снабжён комментарием «почему ненаблюдаемо».
- [x] Поведенческие мутанты `run_argv` на неподавленных строках:
      `required=True` (60), `*argv[1:]` (106), `_result_template_help` (110–112) —
      генерируются и остаются убитыми; тексты help-ов закрываются в фазе 6.

---

## Фаза 1: Конфиг — путь ошибки и полное сравнение слотов ✅ (2026-10-08)

### Проблема

129 выживших в конфигах, два независимых корня.

**A. `where` — 68 шт.** `where` (`'vendors/poshk.json → sections[0] → pricing'`)
используется только в тексте `ConfigValidationError`. Тесты проверяют
подстроку без пути:

```python
with pytest.raises(ConfigValidationError, match='«reader»'):
    VendorConfig.from_dict(bad, 'poshk', 'poshk')
```

Мутант `payload = as_config_object(raw, where)` → `as_config_object(raw, None)`
проходит: `'ожидается объект'` в сообщении остаётся.

**B. Поля и имена ключей — 61 шт.** `BehaviorConfig.from_dict` собирает
`skip_markup_without_opt=read_flag(payload, 'skip_markup_without_opt', where)`
; мутант `read_flag(...) → None` или ключ `'skip_markup_with…' → 'XX…XX'`
не виден, потому что тест парсит конфиг с **дефолтами** (все флаги falsy) и
не проверяет итоговый объект целиком. На дефолтах `None` и `False` неразличимы,
поэтому часть мутантов эквивалентна именно для текущих данных.

### Решение

**A.** Параметризованный тест, который триггерит ошибку в каждом слоте и
проверяет путь:

```python
@pytest.mark.parametrize(
    ('raw', 'path_part'),
    [
        ({'pricing': {'mode': 'нет'}}, 'pricing'),
        ({'sections': [{'pricing': 'нет'}]}, 'sections[0] → pricing'),
        ({'columns': {'x': 'unknown_field'}}, 'columns → x'),
    ],
)
def test_config_error_message_has_path(raw: dict, path_part: str) -> None:
    """Сообщение об ошибке содержит путь до ключа — по нему правят конфиг."""
    with pytest.raises(ConfigValidationError, match=re.escape(path_part)):
        VendorConfig.from_dict(raw, 'poshk', 'poshk')
```

**B.** На каждый слот — тест с конфигом, где заданы **все** ключи, и полным
равенством dataclass:

```python
def test_behavior_config_all_fields() -> None:
    """Все ключи behavior читаются и попадают в объект без потерь."""
    config = BehaviorConfig.from_dict(
        {
            'min_rest': 3,
            'rest': 'остаток',
            'skip_markup_without_opt': True,
            'zero_rest_without_category': True,
            'collect_missing_recommended': True,
            'find_manufacturer_on_enrich': False,
            'pipeline': ['manufacturer', 'category'],
        },
        'behavior',
    )
    assert config == BehaviorConfig(
        min_rest=3, rest='остаток', skip_markup_without_opt=True,
        zero_rest_without_category=True, collect_missing_recommended=True,
        find_manufacturer_on_enrich=False, pipeline=('manufacturer', 'category'),
    )
```

Аналогично для `CategoryConfig`, `PricingConfig`, `TitleConfig`,
`VendorSection`, `VendorConfig`, `MarkupRulesConfig`, `MarkUpRule`,
`AbsoluteMarkUpRules`, `VendorConfigEntry`.

### Что сделано и что замерено

В `interesting` под фазу 1 попали **122 выживших** (119 в `vendor_config/*`,
`data_provider/models.py` + 3 в `json_fields.read_mode`):

- `tests/test_parsers/test_vendor_config/test_error_path.py` — ~90 параметров:
  корень, все ключи верхнего уровня, каждый слот, `sections[i]`;
  ассерт — `path in str(exc)`, поэтому мутант `where → None` меняет
  `mim.json → pricing` на `None → pricing` и падает;
- `tests/test_parsers/test_data_provider/test_error_path.py` — корневые тесты
  4 моделей + 10 кейсов пути через `MarkupRulesConfig` + `multiplier или delta`
  (убивает 3 мутанта `read_mode`);
- в `test_models.py` (vendor_config) — полное `==` для всех ключей
  `BehaviorConfig`/`CategoryConfig`/`TitleConfig`/`PricingConfig`, равенство
  пустого слота дефолту, полное `==` для `VendorSection` и `VendorConfig`.

Все 122 прогнаны точечно `mutmut run <имена>` (пакеты 6 + 116 + 3 доработка):
**120 убито, 2 эквивалентных** (`VendorConfig.from_dict`: `sections=()` → `None`
и удаление `sections=` — оба перезаписываются `replace(config, sections=…)`,
класс I, фаза 7). Промежуточная итерация: первые 116 оставили 5 выживших —
не хватало корневых кейсов `{'pricing': 'x'}` / `{'category': 'x'}` /
`{'title': 'x'}`: только ошибка типа в `read_object` показывает передаваемый
туда `where`, добавлены — 3/3 убиты.

Счётчик mutmut после фазы: **killed 5133, survived 507, timeout 11** —
score **91,0 %** (было 88,9 %); ещё 76 мутантов уйдёт из генерации
по фазе 0 при следующем полном `just mutate`.

### Критерии готовности

- [x] Тест на путь ошибки для каждого слота (`pricing`, `behavior`, `category`,
  `title`, `sections[i]`, `columns`) — и для корней слотов.
- [x] На каждый `from_dict` — тест с полным `==` dataclass и всеми ключами
      (класс B `data_provider` был покрыт существующими тестами).
- [x] Вручную проверено ≥20 мутантов класса A/B: прогнаны все 122 через
      `mutmut run` (скрипта `check_mut.sh` в репо нет — использован
      `pipelines/run_mutation_test.sh` с явным списком имён).

---

## Фаза 2: Канонизация размеров и хвостов

### Проблема

~90 выживших в `_four_tochki_tire_helper.py` (36), `_four_tochki_disk_helper.py`
(29), `_autosnab_helper.py` (25). Мутанты `string_wrap` вида:

- `.replace(',', '.')` / `.replace('.', ',')` (шина `_prepare_dimensions:7`,
  `_parse_size:as_size`);
- `.replace('RZ', 'ZR')`, `.replace('—', _DASH)`, `_resolve_width_postfix`
  (`'10'`, `'20'`);
- `'усил.'`, `'под камеру'`, `'б/к'` в `_tube_label`/`disk_name_suffix`;
- `or '' → 'XXXX'` у `width`/`height`/`diameter`/`run_flat`.

Все они выживают по одной причине: тесты подают уже канонический вход
(`'225'`, `'40'`, `'R18'`), где `replace` — no-op, а ветка пустого поля не
задействована.

### Решение

Тесты на **неканонический** вход и на полную строку:

```python
@pytest.mark.parametrize(
    ('width', 'height', 'diameter', 'expected'),
    [
        ('225', '40', 'R18', '225/40R18'),
        ('225', '40', 'RZ18', '225/40ZR18'),   # replace RZ → ZR
        ('225', '—', '18', '225/18'),          # _DASH
    ],
)
def test_compose_disk_full(width: str, height: str, diameter: str, expected: str) -> None:
    ...
```

Плюс отдельно:

- `test_separator_dot_is_replaced` — `_prepare_dimensions` на `width='22,5'`
  даёт `'22.5'` (не `'22,5'`);
- `test_disk_suffix_thickness_and_tube` — `disk_name_suffix('… 16мм усил. б/к')`
  содержит `'(16 мм)'`, `'усил.'`, `'б/к'`;
- `test_default_title_includes_runflat` — `ext_diameter_title` с непустыми
  `index_load` / `us_aff_designation` / `sidewall` / `runflat` проверяется
  **всей** строкой (закрывает `ext_diameter_title` и `default_tire_title`, 36 шт.);
- `test_apply_size_fills_empty_only` — `_apply_size` на строке с уже
  заполненным `width` не перезаписывает (закрывает `and → or`, `not → ∅`).

### Критерии готовности

- [ ] Есть входы с `,`, `RZ`, `—`, `усил`, `под камеру`, `б/к`.
- [ ] Композиция title/disk проверяется полной строкой, а не `in`.
- [ ] ~70 из 90 убито; остальное разобрано как эквивалентное.

---

## Фаза 3: Прокачка аргументов и DI

### Проблема

~120 выживших класса D — значения, которые «протекают» через фабрики и хуки,
но не проверяются на выходе:

| Функция | Шт. | Пример мутанта |
| --- | ---: | --- |
| `StrategiesIntegration.__init__` | 14 | `self._section = None`, `section.category → 'XX…'` |
| `strategy_hooks_from_section` | 11 | `rest=make_rest_strategy(...) → ∅` |
| `_enrich_row_item` | 12 | `set_field('supplier_name', …) → None` |
| `config_driven_parser` | 26 | `strategy_hooks=hooks → ∅`, `data_reader → None` |
| `_parser_for_vendor` | 15 | `if vendor_config is None` → `is not`, `getattr(..., None) → None` |
| `make_pricing_strategy` / `make_title_strategy` | 12 | `rules → None`, `price_map → None` |
| `_read_columns` / `parser_params_from_section` | 9 | `() → None`, аргумент `section → None` |

Тесты вызывают фабрики, но результат связывается со сквозным разбором, а не
с конкретным полем.

### Решение

1. Ассертить сохранённое состояние и полный хук:

```python
def test_strategies_integration_keeps_section_and_behavior() -> None:
    section, behavior = _fixture_section(), _fixture_behavior()
    integration = StrategiesIntegration(section, behavior)
    assert integration._section is section
    assert integration._behavior is behavior

def test_strategy_hooks_full() -> None:
    hooks = strategy_hooks_from_section(section, behavior)
    assert hooks == StrategyHooks(
        category=..., title=..., rest=...,
        min_rest=behavior.min_rest,
        find_manufacturer_on_enrich=behavior.find_manufacturer_on_enrich,
        zero_rest_without_category=behavior.zero_rest_without_category,
        pipeline=behavior.pipeline,
    )
```

2. `_enrich_row_item` проверять через `RowItem`: все три ключа
   (`supplier_name`, `spike`, `season`) присутствуют со значениями.

3. `_parser_for_vendor` — три ветки таблицей: `None` → `vendor_cls(None)`;
   выключенный конфиг → `vendor_cls(parse_config=...)`; включённый с
   `_vendor_section`/`_vendor_config` → `make_config_driven_parser(...)`.

4. `make_pricing_strategy` / `make_title_strategy` — фабрики возвращают объект,
   собранный из переданных `rules`/`price_map`/`strategy`.

### Критерии готовности

- [ ] Есть тест на полное равенство `StrategyHooks` и на сохранённые
  `StrategiesIntegration._section`/`._behavior`.
- [ ] Каждая ветка `_parser_for_vendor` покрыта отдельным кейсом.
- [ ] `_enrich_row_item` ассертит все три поля `RowItem`.

---

## Фаза 4: Логика и границы предикатов

### Проблема

85 выживших класса E (`operator`/`number`/`keyword`/`method_swap`) — непокрытые ветви:

- `_special_inch_dot`: `or → and`, `not → ∅`, `== → !=`, `< → <=` (7);
- `_lstrip_name`: пустое/`None` имя (`not prefix → prefix`) (3);
- `fill_from_title`: `model and not row_item.identity.model` (2);
- `brand_key_parts`: `.lower() → .upper()`, `'' → None` (6);
- `MarkupPolicy.apply` / `markup_percent_for_opt` / `stored_percent_markup`:
  `0 → 1`, `<= → <`, `opt → None` (12);
- `apply_min_rest`: `< → <=`, `0 → None`;
- `XlsReader.next_row_values`: `<= → <`, `[None] → None`, `is_end_row(None, …)`;
- `_type_production_from_filename`: `maxsplit=1`, `1 → 2`, `- → +`.

### Решение

Таблицы истинности на минимальных входах. Пример:

```python
@pytest.mark.parametrize(
    ('special', 'height', 'width', 'expected'),
    [
        (True, '55', '225', False),   # не спецшина
        (False, '', '225', False),    # нет профиля
        (False, 'L', '225', False),   # профиль L
        (False, '55', '140', False),  # метрика 140/55
        (False, '55', '15', True),    # дюймовая спецшина
    ],
)
def test_special_inch_dot(special, height, width, expected): ...
```

Для `_lstrip_name` — обязательный кейс `name=None` и `name=''`; для
`brand_key_parts` — строка, где регистр `manufacturer`/`brand` различается.

**Таймауты.** 11 статусов `timeout`: `BaseFinder._find` (5 — бесконечный цикл
при мутации индекса) и `run_dialog` (6 — снятый `input()` крутит `while True`).
Разобрать каждый вручную, как в прошлой кампании: либо убить тестом, либо
зафиксировать через заглушку `input`/лимит итераций.

### Критерии готовности

- [ ] Таблица истинности на каждый из перечисленных предикатов.
- [ ] `apply_min_rest` проверяет границу `0` и `<`/`<=`.
- [ ] Все 11 `timeout` разобраны: убиты или объяснены.

---

## Фаза 5: Контракт отчёта и writer

### Проблема

33 выживших в `parse_report.py` (11), `jsonl_writer.py` (7),
`xlsx_driver.py` (6), `xls_writer.py`, `templates/all_templates.py`.

- `emit_json`: `round(…, 2)` (`2 → None/3`, `- → +`) и `flush=True`
  выживают, потому что `test_emit_json_adds_elapsed` проверяет
  `payload['elapsed_seconds'] >= 0`.
- `dump_json`: `ensure_ascii=False → None` (эквивалент, `None` falsy),
  `default=str → ∅` (заметно только на несериализуемом объекте).
- `_extend_meta` `ensure_ascii` — эквивалент (см. фазу 7).
- `xlsx_driver`/`all_templates`: `'#' → 'XX#XX'`, `,  → XX, XX`.

### Решение

```python
def test_emit_json_exact_elapsed(monkeypatch: pytest.MonkeyPatch) -> None:
    """elapsed_seconds округляется до сотых от переданного started."""
    monkeypatch.setattr(parse_report.time, 'monotonic', lambda: 101.234)
    stream = StringIO()
    emit_json({'ok': True}, stream, started=100.0)
    assert json.loads(stream.getvalue())['elapsed_seconds'] == 1.23


class _FlushSpy(StringIO):
    def __init__(self) -> None:
        super().__init__()
        self.flushed = 0
    def flush(self) -> None:
        self.flushed += 1


def test_emit_json_flushes() -> None:
    stream = _FlushSpy()
    emit_json({'ok': True}, stream)
    assert stream.flushed == 1
```

`xlsx_driver`/`all_templates` — ассертить текст исключения с разделителем
(см. фазу 6).

### Критерии готовности

- [ ] `elapsed_seconds` проверяется точным значением, не `>= 0`.
- [ ] `flush=True` проверяется через поток-шпион.
- [ ] ``,  → XX, XX`` в сообщении `UnknownWriterTemplateError` закреплено.

---

## Фаза 6: CLI, интерактив, тексты исключений

### Проблема

- `run_machine._emit_command`: `command in _COMPACT_ERROR_COMMANDS` удалён,
  `in → not in`, `command → None`; `_json_parse`/`_json_doubles`: `- → +`.
- `run._run_machine`: `getattr(args, 'prices', …)`, `command → None`.
- `run_dialog/readers.py`: `read_unix_key`/`read_windows_key`,
  `else 'XXXX'`, `\x00`/`\x1b` — проверяемые при подмене источника символов.
- Тексты исключений (17): `WorkbookNotInitializedError`,
  `WorksheetNotInitializedError`, `JsonPriceNotListError`,
  `MarkupPolicyNotSetError`, `MaxRowsReachedError`, `CoreExceptionError.to_log`.

Тексты исключений в проекте значимы (коммит `7753afc`): пользователь их
читает, значит их стоит закреплять.

### Решение

```python
def test_emit_command_compact_error() -> None:
    """ошибочные команды пишутся компактно (без полного каталога)."""
    ...

def test_json_parse_counts_errors() -> None:
    """битые строки снижают успешные, а не увеличивают."""
    ...

@pytest.mark.parametrize('exc, fragment', [
    (WorkbookNotInitializedError(), 'workbook is not initialized'),
    (JsonPriceNotListError(), 'JSON price must be a list of objects'),
])
def test_exception_message(exc: Exception, fragment: str) -> None:
    assert fragment in str(exc)
```

Интерактивные `read_unix_key`/`read_windows_key` — подменить функцию чтения
символов, проверить `KeyPress` для стрелок и `OTHER`; платформенные константы
подавлены фазой 0.

### Критерии готовности

- [ ] `_emit_command` различает компактные (`compact=`) и полные команды.
- [ ] Тексты намеренно изменённых исключений закреплены.
- [ ] `_result_template_help` строится из реестра шаблонов и его формат
  (разделитель `', '`) проверен.

---

## Фаза 7: Эквивалентные мутанты

Эти нельзя убить тестом — их либо подавляем, либо оставляем с обоснованием
в отчёте:

- **`common_price_dispute._season_label` / `_spike_label` (~13)**: канон
  используется только для подсчёта числа различных значений
  (`len(filled) > 1`), а наружу возвращается имя поля (`'шип'`/`'сезон'`).
  Смена регистра канона или `return 'да' → 'XXдаXX'` результат не меняет.
  Мутация множества-литерала `{'да', …}` — **не** эквивалентна и уже убита
  тестами.
- **`jsonl_writer._extend_meta` `ensure_ascii` (3)**: промежуточная запись
  метаданных перезаписывается `_save_values`, наблюдать нечего.
- **`emit_json` `ensure_ascii=False → None` / `dump_json`**: `None` falsy,
  поведение идентично. `,  → XX, XX` в `_result_template_help` **не**
  эквивалентен — закрывается тестом формата (фаза 6).

Правило: подавлять паттерном только после ручной проверки, что мутант
действительно эквивалентен, с комментарием в `pyproject.toml`.

---

## История предыдущей кампании

Кампания 2026-09-28 подняла score с 88.0 % (4515 мутантов) до **93.2 %**
(4269 мутантов, 3977 killed, 292 survived). Отчёт — `reports/mutmut/`,
детали фаз — в git-истории этого файла. Что переносится в текущий план:

1. **Stale `__pycache__`** — главная ловушка. `pipelines/run_mutation_test.sh`
   чистит `src/**/__pycache__` до и после и ставит `PYTHONDONTWRITEBYTECODE=1`;
   `mutmut run` нельзя запускать параллельно с `pytest`.
2. **`test_registry.py` и `sys.modules`** — clean-прогон падал; тест вычищает
   модуль из `sys.modules` и сравнивает классы по имени.
3. **`help=` подавляет всю строку**, а не «один мутант»: паттерн влияет на
   число мутантов сильнее, чем кажется по точечной оценке.
4. **`mkdir(parents=True)`** нельзя проверить тестом «создать вложенную папку»:
   нужны два кейса — вложенный путь и повторный вызов в готовую папку.
5. **Эквивалентный мутант — сигнал о форме данных.** Если `path` хранится
   строкой, потребители заново её разбирают; разделение `group`/`attribute`
   убирает и разбор, и класс эквивалентных мутантов. Сначала менять форму
   данных, потом подавлять.

---

## Проверки после каждой фазы

Полный набор из корня, порядок — из `.github/workflows/python-app.yml`:

```bash
uv run pytest
uv run black --check --diff .
uv run ruff check .
uv run flake8 .
uv run mypy .
uv run lint-imports
uv run vulture
uv run bandit -r src -c pyproject.toml
uv run pip-audit
```

Плюс контрольный прогон мутаций (только когда `pytest` не запущен):

```bash
just mutate
uv run python -m pipelines.mutmut_stats --output-dir reports/mutmut
```

Комментарии и docstring в новых тестах — на русском, кавычки одинарные,
line-length 120.

---

## Чего сознательно не делаем

- **Не добирать покрытие строк.** `mutate_only_covered_lines=true`; все
  выжившие уже покрыты. Проблема в силе assertions.
- **Не тестировать `--help` / описания подкоманд** — не влияют на разбор
  (фаза 0).
- **Не тестировать `cast()` / `encoding='utf-8'`** — аннотация и эквивалент
  при локали UTF-8 (закрыто прошлой кампанией).
- **Не подавлять `where`.** Путь до ключа — часть пользовательского сообщения,
  его надо проверять, а не прятать (фаза 1).
- **Не гнаться за 100 %.** Потолок ~97 %; дальше — тексты исключений и
  мутации `rsplit(..., maxsplit=N)` при фиксированной глубине модулей.
