# План усиления тестов по данным mutmut

Актуальный срез — прогон от 2026-10-08: `mutants/mutmut-analysis.json`
(сгенерирован `uv run python -m pipelines.mutmut_stats`).
Предыдущая кампания описана в разделе [История](#история-предыдущей-кампании);
её отчёт лежит в `reports/mutmut/`.

Задачи из [архитектурного плана](./PLAN.md) выполняются независимо от этого документа.

---

## Контекст

| | 2026-09-28 (прошлая кампания) | 2026-10-08 (текущий срез) | 2026-10-09 (после фаз 0–2) | 2026-10-09 (после фазы 3) | 2026-10-09 (после фазы 4) | 2026-10-09 (после фазы 5) | 2026-10-09 (после фазы 6) | 2026-10-09 (после фазы 7) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| мутантов | 4269 | 5651 | 5702 | 5711 | 5718 | 5717 | 5717 | 5717 |
| killed | 3977 | 5013 | 5298 | 5388 | 5473 | 5495 | 5536 | 5610 |
| survived | 292 | 627 | 393 | 312 | 238 | 215 | 174 | 100 |
| timeout | 0 | 11 | 11 | 11 | 7 | 7 | 7 | 7 |
| **mutation score** | **93.2 %** | **88.9 %** | **93.1 %** | **94.5 %** | **95.8 %** | **96.2 %** | **97.0 %** | **98.2 %** |

Числа за 2026-10-09 получены чистым прогоном (`mutants/` удалён): кэш,
оставшийся от точечных `mutmut run <filter>`, терял часть мутантов и занижал
знаменатель. Теперь `pipelines/run_mutation_test.sh` сносит `mutants/` перед
каждым прогоном. Он же показывает 5702 мутанта против 5651 — это эффект полной
перегенерации `mutate_only_covered_lines` после новых тестов и коммита Пошка,
а не рост кода на 350+ мутаций.

**После фазы 3** счётчик снова вырос на 9 (5702 → 5711): новые тесты исполнили
ранее не покрытые строки, и `mutate_only_covered_lines` догенерировал на них
мутантов. survived упал 393 → 312 (−81), killed вырос 5298 → 5388 (+90),
score 93,1 % → **94,5 %**.

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

Скрипт сносит кэш `mutants/` перед прогоном: после точечного
`mutmut run <filter>` в нём остаются результаты только части мутантов, и
следующий прогон берёт неполный снимок (занижает знаменатель).

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
| 2 | [Канонизация размеров и хвостов](#фаза-2-канонизация-размеров-и-хвостов) | C | 84 убито ✅ | P0 |
| 3 | [Прокачка аргументов и DI](#фаза-3-прокачка-аргументов-и-di) | D | 81 убито ✅ | P1 |
| 4 | [Логика и границы предикатов](#фаза-4-логика-и-границы-предикатов) | E | 84 убито ✅ | P1 |
| 5 | [Контракт отчёта и writer](#фаза-5-контракт-отчёта-и-writer) | D, E | 22 убито ✅ | P2 |
| 6 | [CLI, интерактив, тексты исключений](#фаза-6-cli-интерактив-тексты-исключений) | H | 41 убито ✅ | P2 |
| 7 | [Эквивалентные мутанты](#фаза-7-эквивалентные-мутанты) | I | 74 убито ✅ | P2 |

**Прогноз:** 5651 → ~5575 мутантов (фаза 0 уже убрала 76 из генерации),
~500 убитых → **~96 %**.

**Факт (2026-10-09):** после фаз 0–2 score **93.1 %** (5702 / 5298 / 393).
Фаза 2 закрыта; верхний кластер выживших — `base_parser` (32),
`config_driven_parser` (26), `title` (24), `markup_policy` (19) — это фазы 3, 4
и 6.

**Факт (2026-10-09, после фазы 3):** score **94.5 %** (5711 / 5388 / 312).
Прокачаны DI и фабрики: `_enrich_row_item`, `make_config_driven_parser`,
`strategy_hooks_from_section`, `_parser_for_vendor`, `StrategiesIntegration`,
фабрики `make_pricing_strategy`/`make_title_strategy`, реестр вендоров. В
целевых файлах остались только эквивалентные мутанты (фаза 7) и тексты логов
(`enrich_items`, фаза 6); верхний кластер выживших — `title` (24),
`markup_policy` (19), `config_driven_parser` (остаток) — это фазы 4 и 6.

**Факт (2026-10-09, после фазы 4):** score **95.8 %** (5718 / 5473 / 238).
Закрыты предикаты и границы: наценка (`markup_percent_for_opt`, `apply`,
`stored_percent_markup`, delta-маржа), `apply_min_rest`, `XlsReader`
(`ParamsHelper`, `next_row_values`, `parse`/`sheets`), `brand_key_parts`,
`disk_extras_key`, логика `BaseParser` (`category_for`, `apply_category`,
`_run_pipeline`, `set_prepared_title`, `make_parser`, `_type_production_from_filename`),
`base_finder._find`/`_has_word_boundaries`. Из 11 таймаутов разобраны 4
(`readers._unix_has_pending`, `base_finder` — 1 убит); в целевых файлах
остались только эквивалентные мутанты (фаза 7), тексты исключений (фаза 6) и
7 ненаблюдаемых таймаутов (см. фазу 4). Верхний кластер выживших —
`title` (24), `common_price_dispute` (13), `parse_report` (11), `category` (10) —
это фазы 5 и 6.

**Факт (2026-10-09, после фазы 5):** score **96.2 %** (5717 / 5495 / 215).
Закрыт контракт отчёта и writer: точное `elapsed_seconds` и `flush=True` в
`emit_json`, `default=str` в `dump_json`/`jsonl_writer`, точная дата в имени
`.jsonl`, полный разделитель `UnknownWriterTemplateError`, точные тексты
`WorkbookNotInitializedError`/`WorksheetNotInitializedError`, значение
`parse_errors` и список `warnings` в `parse_report_build`, граница пустого
`by_column` в `_get_color`. Удалён мёртвый `ColumnHelper._col` (это убрало один
эквивалентный мутант из генерации: 5718 → 5717). В целевых файлах остались
только эквивалентные мутанты (фаза 7). Верхний кластер выживших —
`title` (24), `common_price_dispute` (13), `category` (10), `run_machine` (10) —
это фаза 6 и фаза 7.

**Факт (2026-10-09, после фазы 6):** score **97.0 %** (5717 / 5536 / 174).
Закрыт CLI, интерактив и тексты исключений: `_emit_command` различает
компактные и полные ответы (в т.ч. на `KeyboardInterrupt`), точный
`elapsed_seconds` в `_json_parse`/`_json_doubles`, пустые значения
`load_config`/`parse_prices_json` не подменяются, `fail_unknown_result_template`
несёт действие; `_machine_human` возвращает 0, `_run_machine` передаёт команду,
`args.prices` доходит до `machine_json`; `_result_template_help` с разделителем
`', '`; `read_unix_key`/`read_windows_key` не сохраняют символ для распознанных
клавиш; `_menu_text`, кадр `screen._rewrite` и `MenuView.finish` закреплены
дословно; тексты `JsonPriceNotListError`, `MarkupPolicyNotSetError`,
`«В прайсе отсутствуют вкладки!»` и лимит стека `CoreExceptionError.to_log`
проверены. В целевых файлах остались только эквивалентные мутанты (фаза 7).
Самый крупный остаток вне фазы 6 — кластеры `title` (24) и `category` (10):
подстановки `or 'XXXX'`, мёртвые ветви `∅ → (` и границы `_is_decimal`; им
нужна отдельная фаза (форма данных стратегий).

**Факт (2026-10-09, после фазы 7):** score **98.2 %** (5717 / 5610 / 100).
Финальная зачистка: у всех 174 выживших перепроверена природа, killable
закрыты тестами (−74), остальные разобраны как эквивалентные/ненаблюдаемые.
Закрыты `field_registry.FieldSpec` (путь VO), стратегии `title`/`category`
(дробный профиль, пустой профиль, `load_velocity`, суффикс диска, границы
`_metric_or_passenger`, контекст `ColumnCanonicalCategory`), счётчики и номера
строк `base_parser_row`, `_has_product_identity`, `load_config` /
`load_supplier_prices` (создание вложенных папок, пути в сообщениях),
`title_filter.reset_caches`,
`price_markup` (округление, деление на ноль), `registry.make_category_strategy`,
`ServiceProvider`, дефолты `make_report`/`write_doubles`, `drop_blank_aliases`,
`fallback_brand`, `FileReader.raw_parse`, сообщения `SupplierPrice*`, `init_cfg`
(пути логов и приёмник исключений). Остаток 100 — эквивалентные мутанты
(разобраны в фазе 7) и 7 ненаблюдаемых таймаутов.

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

## Фаза 2: Канонизация размеров и хвостов ✅ (2026-10-09)

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

### Что сделано и что замерено

Чистый прогон `just mutate` (2026-10-09) дал **total 5702, killed 5298,
survived 393, timeout 11, score 93.1 %**. В трёх целевых модулях после фазы 2
осталось 7 выживших — **все эквивалентные** (фаза 7):

| Модуль | Мутантов | Выжило |
| --- | ---: | ---: |
| `_four_tochki_tire_helper.py` | 229 | 2 |
| `_four_tochki_disk_helper.py` | 74 | 1 |
| `_autosnab_helper.py` | 177 | 4 |

Что закреплено тестами:

- `tests/test_parsers/test_vendors/test_four_tochki/test_four_tochki_title.py`:
  в таблицу `test_prepared_title_width_postfix` добавлены неканонические входы
  (`,` в ширине/диаметре, `RZ`, тире `—`, пустой диаметр, дюймовая пара
  `10/20`, спецшина на границе ширины 100 и на дробной ширине, суффикс `.0`);
  два полных title-теста `test_default_title_all_parts` /
  `test_ext_diameter_title_all_parts` заполняют **все** необязательные поля
  (`layering`, `camera_type`, `inscription_on_the_side`, `us_aff_designation`,
  `run_flat`), поэтому удаление любого аргумента из `compose_tire_title` видно.
- `tests/.../test_four_tochki_disk_title.py`: `disk_name_suffix` проверяется
  полной строкой на нижнем и **верхнем** регистре меток, отдельно `б/к`,
  отдельно хвосты `disk_name_extras`; `disk_diameter(None)`, `et_label('XXXX')`,
  `thickness_from_name('(15,5 мм)')`, `fill_disk_thickness` из title и
  сохранение заполненной колонки.
- `tests/.../test_strategies/test_autosnab_helper.py` (новый): размер
  профильный/плоский/дюймовый, десятичные запятые в каждом из
  width/height/diameter, `_apply_size` не перезаписывает заполненные поля,
  модель срезает manufacturer/brand, отбрасывает скобки, тянется на несколько
  токенов, завершается на стоп-слове (`TL`), PR (16PR) и индексе (104R).
  Отдельно: профильный и плоский разбор проверяют `row.parse_errors == {}` —
  иначе мутант `ext_diameter='XXXX'` маскируется тем, что `set_field` тихо
  складывает ошибку приведения в `_parse_errors`.

### Критерии готовности

- [x] Есть входы с `,`, `RZ`, `—`, `усил`, `под камеру`, `б/к`.
- [x] Композиция title/disk проверяется полной строкой, а не `in`.
- [x] Целевые модули: 473 из 480 мутантов убито; остальные 7 разобраны как
      эквивалентные (фаза 7).

---

## Фаза 3: Прокачка аргументов и DI ✅ (2026-10-09)

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

### Что сделано и что замерено

Чистый прогон `just mutate` (2026-10-09): **killed 5388, survived 312, timeout 11,
score 94,5 %** (было 93,1 %). Целевые 93 мутанта прогнаны точечно
`pipelines/run_mutation_test.sh <имена>` — все, кроме эквивалентных, убиты.

- `tests/test_base_parser/test_row_filters.py` — `test_enrich_row_item_sets_service_fields`
  проверяет все три ключа `_enrich_row_item` (`supplier_name`/`spike`/`season`)
  через `row.get_field(...)`, а не факт разбора (12 мутантов).
- `tests/test_parsers/test_strategies/test_config_driven_parser.py`:
  полное `==` для `parser_params_from_section`; `_reader_for_config` таблицей
  (`json`/`xls`/прочее); `make_config_driven_parser` ассертит `_strategy_hooks`
  и `data_reader` (JsonPriceReader по reader='json'); `strategy_hooks_from_section`
  проверяет `rest is not None`, `min_rest`, `find_manufacturer_on_enrich`,
  `zero_rest_without_category`, `pipeline`; путь ошибки `section <id> <slot>`
  ассертится через `startswith` (обёртка `XX…XX` иначе маскирует подстрокой);
  `vendor_markup_policy_from_config` — `startswith('section.pricing:')`.
- `tests/test_parsers/test_strategies/test_integration.py` — хранение
  `_section`/`_behavior` и путь ошибки `section.category`/`section.title`/
  `behavior.rest` (`startswith`).
- `tests/test_parsers/test_strategies/test_pricing_registry.py` —
  `_rules is rules` и `_price_map == (rule,)` для `base`/`map_on_opt`/
  `recommended_or_map`, `_threshold`/`_low`/`_high` для `percent_by_threshold`.
- `tests/test_parsers/test_strategies/test_title_registry.py` — `WHERE in str(exc)`
  для неизвестной стратегии и вариантов; обёртка `aliases` реально применяет
  карту (`prepare` → замена) и получает `supplier_name` поставщика.
- `tests/test_services/test_parse_orchestrator.py` — пять веток
  `_parser_for_vendor` (`None`; disabled; enabled с метаданными → фабрика;
  без `_vendor_config`; без метаданных), `+=` пропусков black_list на двух
  вендорах, код в `parse_vendor`, знак времени разбора в логе.
- `tests/test_parsers/test_registry.py` — папка и `VendorConfig` в записях,
  `make_vendor_entry` привязывает секцию/конфиг, `vendor_config_is_enabled`
  без `_vendor_config` = True, `UnknownVendorError` несёт код.

Остаток в целевых файлах — только эквивалентные мутанты (класс I), разобраны
в фазе 7: `_parser_for_vendor` `vendor_cls(vendor_config)` → `vendor_cls(None)`;
`getattr(..., None)` → `getattr(...)` (атрибут задан классом `ParseConfiguration`);
`_parse_all_vendors` пробрасывает `parser_factory → None` (в
`_parser_for_vendor` он не используется); `manufacturer_reader=lambda: 0`/`∅`
(0 и None одинаково falsy); `all_vendors_from_registry(include_disabled=None)`
(None falsy); `_brand_probe [0] → [1]` (обёртки-алиасы всегда парные).
`enrich_items` `start=start_row` и `row_id → None` — тексты логов (фаза 6).

### Критерии готовности

- [x] Есть тест на полное равенство `StrategyHooks` и на сохранённые
  `StrategiesIntegration._section`/`._behavior`.
- [x] Каждая ветка `_parser_for_vendor` покрыта отдельным кейсом.
- [x] `_enrich_row_item` ассертит все три поля `RowItem`.
- [x] Фабрики `make_pricing_strategy`/`make_title_strategy` ассертят переданные
  `rules`/`price_map`/`strategy`; реестр вендоров проверен на папку и конфиг.

---

## Фаза 4: Логика и границы предикатов ✅ (2026-10-09)

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

На срезе после фазы 3 часть этих мутантов уже закрыта фазой 2
(`_special_inch_dot`, `_lstrip_name`, `fill_from_title`), а живые остались в
`markup_policy` (19), `row_processor` (10), `xls_reader` (13),
`common_price_group_fields` (13), `base_parser` (3) и `base_finder` (10).

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

### Что сделано и что замерено

Чистый прогон `just mutate` (2026-10-09): **killed 5473, survived 238, timeout 7,
score 95,8 %** (было 94,5 %; +85 убитых, −74 выживших, −4 таймаута).
Добавлены таблицы истинности и граничные кейсы:

- `tests/test_base_parser/test_markup_policy.py` — карта из трёх правил
  (`0…0`/`1…10`/`11…30`) различает границы `min`/`max` (`<=`), дефолтный
  процент и процент правила; `stored_percent_markup` проверяет `price_opt or 0`
  (нулевой закуп и закуп, равный правилу); `apply(0, None)`, `apply(5, None)` и
  `apply(1000, 2000)` с `max_recommended>0` закрывают `opt → None`,
  `price_opt or 1`, `not price_recommended` (мутант `_is_big(…, None)` — экв.,
  фаза 7); `create()` ассертит пустые `_rules`/`_price_map`;
  `_is_small_absolute_markup` проверен в delta-режиме при `margin == floor`.
- `tests/test_base_parser/test_row_processor.py` (новый) —
  `add_price_markup` (нулевой закуп у identity, сохранение РРЦ, округление до
  десятков `//` без `/`, запись процента от реального закупа), `get_markup_percent`,
  `apply_min_rest` (граница `min` и порог).
- `tests/test_parsers/test_xls_reader.py` — `ParamsHelper` (`cur_row` из
  `start_row`), `cur_row_values is None`, guard `is_end_row` на непустой строке,
  ширина из шапки (`end_col`), `parse()` без индексов, `sheets()` на пустой
  книге, точный текст `MaxRowsReachedError`.
- `tests/test_parsers/test_common_price_group_fields.py` — `brand_key_parts`
  (регистр, пустые, совпавший бренд, скрытие бренда той же группы),
  `disk_extras_key` (нижний регистр хвостов, не-диск, без хвостов).
- `tests/test_base_parser/test_row_filters.py`, `test_parser_hooks.py`,
  `test_base_parser_process.py`, `test_markup_defaults.py` — логика
  `BaseParser`: `category_for` без хуков, `apply_category` (категория от строки),
  `apply_manufacturer`, сборка `ManufacturerFinder` на алиасах конфига,
  `set_parse_config`, `raw_parse`, `__repr__` с `sheet_info`, начальные `None`,
  `get_min_rest_count`, `strip_words_in_title(None)`, шаг `min_rest` в pipeline,
  `after_row_mapped` получает строку, `process()` накапливает строки,
  `make_parser` прокидывает `data_reader`/`file_prices`,
  `set_prepared_title` возвращает `True` при неизменном title.
- `tests/test_base_parser/test_base_finder.py` — алиас со второй позиции,
  пустой алиас (guard), первое ограниченное вхождение (не `rfind`),
  `_has_word_boundaries` отвергает букву перед алиасом.
- `tests/test_run_dialog/test_keys.py` — `_unix_has_pending` вызывает
  `select.select` с конечным `_ESCAPE_TIMEOUT` (шпион на `select`).

**Таймауты.** Осталось 7 (было 11). Убито 4:

| Мутант | Почему таймаут | Вердикт |
| --- | --- | --- |
| `readers._unix_has_pending` `_ESCAPE_TIMEOUT → None` / `∅` | `select` без таймаута блокируется на пустой пайпе | убит шпионом `select.select` |
| `base_finder._find` `while position != -1 → != +1` | позиция не совпадает с сигналом `-1`, цикл не выходит | убит тестом «алиас со второй позиции» |
| `line_fallback.ask_by_line` `lower → upper` | `ANSWER_MAP` без `Q`, ввод не распознаётся, диалог зацикливается | убит ограниченным вводом (`_dialog_input`) |

Оставшиеся 7 ненаблюдаемы тестом, потому что мутация убирает сам вызов, который
мог бы завершить цикл:

- `base_finder._find` (4): `!= -2`, `find(…, None)`, `find(…)` без старта,
  `find(…, position - 1)` — цикл вечен, т.к. `-1` больше не останавливает поиск;
- `run_dialog.line_fallback.ask_by_line` (2): `answer = None` и
  `ANSWER_MAP.get(None)` снимают вызов `input()`, `while True` крутится без
  ввода — ни лимит ответов, ни `StopIteration` не наступают;
- `run_dialog.navigation.navigate` (1): `action = None` снимает
  `_handle_press(view, read_key())`, `read_key` больше не вызывается.

Это тот же класс, что снятие `input()` в прошлых кампаниях: убить тестом
нельзя, только объяснить.

### Критерии готовности

- [x] Таблица истинности на каждый из перечисленных предикатов.
- [x] `apply_min_rest` проверяет границу `0` (эквивалент) и `<`/`<=`.
- [x] Все 11 `timeout` разобраны: 4 убиты, 7 объяснены как ненаблюдаемые.

---

## Фаза 5: Контракт отчёта и writer ✅ (2026-10-09)

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

### Что сделано и что замерено

Чистый прогон `just mutate` (2026-10-09): **killed 5495, survived 215, timeout 7,
score 96,2 %** (было 95,8 %; +22 убитых, −23 выживших, −1 мутант в генерации).
Убрано 23 выживших:

- `tests/test_cli/test_parse_report.py` — `test_emit_json_exact_elapsed`
  (monkeypatch `parse_report.time.monotonic`, точное `1.23` вместо `>= 0`;
  закрывает `round(…, None)`, `round(2)`, `round(x)`, `- → +`, `2 → 3`) и
  `test_emit_json_flushes_stream` (поток-шпион считает `flush`; закрывает
  `flush=None`, снятый `flush`, `True → False`); `dump_json` и
  `default=str` проверены несериализуемым объектом; `_item_payload`
  ассертит `payload['parse_errors'] == row.parse_errors` (а не ключ), а
  `report_from_result` — что `warnings` не теряются.
- `tests/test_parsers/test_writer/test_jsonl_writer.py` — запись
  несериализуемого значения через `default=str`, точный формат даты в имени
  файла (`re.fullmatch(r'price_\d{4}-\d{2}-\d{2}\.jsonl', …)`).
- `tests/test_parsers/test_writer/test_all_templates.py` — полное равенство
  текста `UnknownWriterTemplateError` (разделитель `', '`).
- `tests/test_parsers/test_writer/test_xlsx_driver.py` — точные (якорные)
  тексты `WorkbookNotInitializedError`/`WorksheetNotInitializedError`.
- `tests/test_parsers/test_writer/test_get_color.py` — пустой `by_column`
  отключает цвет даже при ключе `''` в строке (закрывает `or → and`).
- `src/parsers/writer/templates/column_helper.py` — удалён мёртвый
  `self._col` (нигде не читается; это убрало мутанта из генерации, а не
  подавило его).

Остаток в целевых файлах — 11 эквивалентных мутантов (фаза 7):
`dump_json`/`_write_jsonl`/`_extend_meta` `ensure_ascii` (промежуточная запись
мета перезаписывается `_save_values`), `xlsx_driver` `known_max <= content_length`
(равенство присваивает то же значение), `solid_fill` `lstrip('XX#XX')`
(в валидном hex нет `X`), `get_value` `(field_name) or True` (ключ `None` в
строке недостижим), `writer_template_name` `rsplit(...)` (`[-1]` при
`maxsplit=1`).

### Критерии готовности

- [x] `elapsed_seconds` проверяется точным значением, не `>= 0`.
- [x] `flush=True` проверяется через поток-шпион.
- [x] `,  → XX, XX` в сообщении `UnknownWriterTemplateError` закреплено.

---

## Фаза 6: CLI, интерактив, тексты исключений ✅ (2026-10-09)

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

### Что сделано и что замерено

Чистый прогон `just mutate` (2026-10-09): **killed 5536, survived 174, timeout 7,
score 97,0 %** (было 96,2 %; +41 убитых, −41 выживший). Убрано 41 выживших:

- `tests/test_cli/test_run_machine.py` — `test_json_keyboard_interrupt` ассертит
  `action`, точный `error` `{'kind': 'KeyboardInterrupt', 'message': 'interrupted'}`
  и наличие `version` (полный ответ); новый
  `test_json_keyboard_interrupt_compact_command` прерывает `load_config` и
  проверяет компактный ответ целиком (закрывает `command → None`,
  `_INTERRUPT → None`, `compact → None/∅` и `in → not in`);
  `test_json_parse_elapsed_is_monotonic_difference` /
  `test_json_doubles_elapsed_is_monotonic_difference` подменяют
  `run_machine.time` на последовательность `monotonic` и требуют точные `2.5`
  (закрывают `- → +`); `test_json_load_config_without_path_is_empty` и
  `test_json_load_supplier_prices_without_raw_is_empty` проверяют, что пустой
  вход не подменяется `'XXXX'`; `test_fail_unknown_json` ассертит `action`;
  `test_run_machine_human_exit_code_zero` — код 0 `_machine_human`;
  `test_run_machine_json_passes_supplier_prices` — `args.prices` доходит до
  `machine_json`.
- `tests/test_cli/test_run_dispatch.py` — `test_run_machine_json_dispatch`
  ассертит `fail_unknown_result_template('parse', None, json_mode=True)`
  (закрывает `command → None` в `_run_machine`).
- `tests/test_cli/test_run_argv.py` — `test_result_template_help_lists_all_templates`
  собирает ожидаемые `available`/`defaults` из реестра и требует подстроки
  `(…)` и `Без флага — ….` с разделителем `', '` (закрывает два `,  → XX, XX`).
- `tests/test_run_dialog/test_keys.py` — параметризованные
  `test_read_unix_key_clears_char_for_recognized_keys` /
  `test_read_windows_key_clears_char_for_recognized_keys` требуют `char == ''`
  для Enter/q (закрывают `else 'XXXX'` и `or True`).
- `tests/test_run_dialog/test_line_fallback.py::test_menu_text_exact` —
  точное сравнение `_menu_text()` с текстом из `MENU_ITEMS`.
- `tests/test_run_dialog/test_menu.py::test_menu_view_finish_passes_current_height`
  (шпион на `navigation.settle`) и
  `test_ask_with_arrows_builds_collapsed_rows` (шпионы на `ServiceProvider.resolve`
  и `build_rows`) закрывают `previous → None`, `resolve(…) → None`,
  `list_vendors() → None` и `expanded=False → None/True`.
- `tests/test_run_dialog/test_screen.py::test_rewrite_writes_exact_control_sequence`
  сравнивает вывод с `'\x1b[J' + '\n'.join(render(...)) + '\n'` (закрывает
  `\x1b[J → XX\x1b[JXX` и два `\n → XX\nXX`).
- Тексты исключений:
  `test_parsers/test_json_reader.py::test_json_price_not_list_error_message`,
  `test_base_parser/test_markup_defaults.py::test_markup_policy_error_message`,
  `test_parsers/test_xls_reader.py::test_sheets_raises_on_empty_book`
  (`str(exc) == 'В прайсе отсутствуют вкладки!'`) и
  `test_domain/test_exceptions.py::test_to_log_limits_stack_depth` (шпион на
  `traceback.extract_stack`, `limit == 10`).

Остаток в целевых файлах — только эквивалентные мутанты (фаза 7): `\x1b`/`\xe0`
и `\x1b[J` в верхнем регистре hex — тот же символ; `_handle_press` дефолт `0`
мёртв из-за guard `if press.key in _STEPS`; `apply_min_rest`/`xls_reader`
эквиваленты (см. фазу 7).

### Критерии готовности

- [x] `_emit_command` различает компактные (`compact=`) и полные команды.
- [x] Тексты намеренно изменённых исключений закреплены.
- [x] `_result_template_help` строится из реестра шаблонов и его формат
  (разделитель `', '`) проверен.

---

## Фаза 7: Эквивалентные мутанты ✅ (2026-10-09)

Финальная зачистка: у всех 174 выживших после фазы 6 перепроверена природа.
74 закрыты тестами, 100 разобраны как эквивалентные или ненаблюдаемые (не
подавляем — обоснование ниже, чтобы будущие кампании не искали их заново).

Чистый прогон `just mutate` (2026-10-09): **killed 5610, survived 100,
timeout 7, score 98,2 %** (было 5536 / 174 / 7 / 97,0 %).

### Что убито тестами (74)

Рекордсмены — кластеры, где тест не доходил до поля или брал уже канонический
вход:

- **`domain/row_item/field_registry.py::FieldSpec` (8).** `__post_init__` бьёт
  только при импорте, поэтому тесты из реестра его не исполняли. Новый тест
  строит `FieldSpec` **в теле** и читает `.path` — падают и `self → None`, и
  подмена `_path`, и удаление аргументов.
- **`strategies/title.py` (21).** Дробный профиль (`31x10.5R15`), пустой профиль
  (`205/R16`), `load_velocity` в simple и truck, пустой `mim_truck`, пустой
  `NormalizeSizeChunks`, `*`→`x` только в размерном куске, приклейка `R…` при
  двух кусках, суффикс диска из исходного наименования.
- **`strategies/category.py` + `tire_category.py` (7).** Контекст
  `ColumnCanonicalCategory` получает исходный тип (не `None`), пустая категория
  до первого заголовка, граница ширины `245`, дюймовый размер без `C`, «кольцо»
  без «уплотнительн».
- **`base_parser/base_parser_row.py` (4).** Накопление `black_list_skips` для
  `_keep_row_item` и `_try_prepare_row`; номер строки в логе берётся из
  `start_row`, а не с нуля и не `None`.
- **`base_parser/title_filter.py` (1).** `strip_words_in_title(None)` не
  превращается в заглушку.
- **`base_parser/price_markup.py` (4).** Округление `percent_markup` до сотых;
  деление на ноль при закупе 0 и заданной РРЦ.
- **`load_config.py` (3).** Вложенный `parse_config` создаётся без заранее
  готовой папки; папка и причина JSON-ошибки в сообщениях.
- **`load_supplier_prices.py` (2).** Путь файла и причина JSON-ошибки в текстах
  исключений.
- **`base_parser/alias_container.py` (1).** Свой канон в нижнем регистре
  исключается из `blocked`, а не в верхнем.
- **`strategies/registry.py` (2).** Список доступных стратегий категории через
  `', '`.
- **`data_provider/manufacturer_aliases.py` (2).** `aliases` без ключа — пустой
  список, а не `None`.
- **`vendor_config/slot_configs.py` (1).** Путь `title → fallback_brand` в
  сообщении об ошибке.
- **`services/` (6).** Дефолты `make_report`/`write_doubles` (`as_jsonl=False`),
  фабрика дублей получает записи, `ServiceNotRegisteredError` называет
  интерфейс.
- **`cfg/__init__.py` (2), `common_price_grouper.py` (2),
  `infrastructure/config/zapaska_api_config.py` (2),
  `base_parser/file_reader.py` (2).** Пути логов и приёмник исключений в
  `init_cfg`, модель без размера но с моделью — дубль, `.strip("'")` не режет
  `X` по краям, `FileReader.raw_parse` передаёт путь и вкладки.

### Эквивалентные и ненаблюдаемые (100)

Не подавляем паттерном: причина не в тексте, а в форме данных или в
недостижимой ветке. Подавление скрыло бы сигнал (см. «Историю»).

- **`common_price_dispute._season_label` / `_spike_label` (13)**: канон
  используется только для подсчёта числа различных значений
  (`len(filled) > 1`), а наружу возвращается имя поля (`'шип'`/`'сезон'`).
  Смена регистра канона, `return 'да' → 'XXдаXX'`, `or 'XXXX'` (не входит в
  наборы) число различных не меняют: синонимы набора делят один `return`.
  Мутация множества-литерала `{'да', …}` — **не** эквивалентна и убита тестами.
- **`common_price_group_fields` (5), `common_price_group_key` (5),
  `common_price_size` (3)**: `or 'XXXX'` там, где `'XXXX'` проходит те же
  фильтры, что пустая строка; `canon_diameter` `count=1` — `^`-якорь даёт не
  более одного вхождения; `_group_key_parts.upper → lower` компенсируется
  `.upper()` в `camera_key`; `canon_number('XXXX')` возвращает `''` как и `''`.
- **`strategies/category` (6), `tire_category` (1), `strategies/title` (3),
  `title_registry` (1), `_autosnab_helper` (4), `_four_tochki_*` (3)**:
  `or 'XXXX'`-заглушка обрабатывается как пустая (`_first_chunk` без default,
  `_canonical` не находит), `split(' ') → split(None)` при пробельных
  заголовках (`_first_chunk`, `_prepend_manufacturer`), `_replace_leading_ship`
  `or True` только при пустом remainder (пробел срезает `.strip()`),
  `disk_name_extras('XXXX') == ''`, `_brand_probe[0] → [1]`.
- **`strategies/pricing.py::PercentByThresholdMarkupPolicy.__init__` (2)**:
  переопределённый `apply` не читает унаследованные `_rules`/`_price_map`.
- **`base_parser` (`base_parser.py` 3, `base_finder.py` 1, `markup_policy.py` 1,
  `row_processor.py` 1, `strategies_integration.py` 3, `category_finder.py` 3)**:
  `set_field('rest_count', None)` приводится `row_format.integer` к 0;
  `rsplit(maxsplit=…)`/`find(…, +1)` неразличимы формой данных;
  `_is_big_recommended_percent(…, None)` — ветка только при falsy РРЦ;
  `manufacturer_reader=None/lambda:0/∅` — `0`/`None` одинаково falsy;
  `zip(*skips, strict=…)` — все пропуски парные.
- **`parsers/registry.py` (3), `vendor_config/models.py` (2),
  `vendor_config/provider.py` (2), `services/parse_orchestrator.py` (4)**:
  `getattr(…, '_vendor_*', None)` — атрибут объявлен классом `ParseConfiguration`;
  `include_disabled=None`/`vendor_cls(None)`/`_parser_factory=None` — falsy или
  неиспользуемые аргументы; `sections=()` перезаписывается `replace`;
  `subn(count=…)` при единственном `enabled`.
- **writer (`jsonl_writer.py` 4, `all_templates.py` 3, `xls_writer.py` 1,
  `xlsx_driver.py` 2), `xls_reader.py` (3), `parse_report.dump_json` (1),
  `common_price_output.py` (1)**: `ensure_ascii=None` ≡ `False`, промежуточная
  запись мета перезаписывается `_save_values`; `rsplit(maxsplit=…)[-1]`,
  `lstrip('#')` (валидный hex без `X`), `known_max <=` (присваивает то же),
  `[None] → None` (потребители не различают), дефолт `_write_with_template` не
  используется публичными вызовами.
- **`run_dialog/navigation.py` (3), `readers.py` (2), `screen.py` (1)**:
  `_STEPS.get(…, 0)` — дефолт недостижим из-за `in _STEPS`; регистр hex-цифры в
  escape-литерале (`\x1b`/`\x1b[J`) символ не меняет.
- **`remote/zapaska_client.py` (2)**: `utf-8`/`ascii`/`ascii` регистронезависимы
  (`UTF-8`/`ASCII`).
- **`nomenclature_title.brand_label` (1)**: `.capitalize()` после `.lower()` и
  `.upper()` даёт одно и то же.
- **`data_provider/manufacturer_aliases.py` (2),
  `manufacturer_group.py` (1)**: `entry.get('aliases', None)` без ключа и так
  даёт `()`; `or → and` возвращает тот же `lower()`.
- **`infrastructure/config/result_folder.py` (2)**: `missing_ok=True → False/None`
  — записи существуют на момент обхода.

**7 таймаутов** (`base_finder._find` 4, `line_fallback.ask_by_line` 2,
`navigation.navigate` 1) — ненаблюдаемы тестом: мутация снимает сам вызов/шаг,
который мог бы завершить цикл (разобрано в фазе 4).

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
