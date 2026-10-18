# Task-15: Выжившие мутанты после дублей, Форточек и почтовых ссылок (2026-10-18)

Статус: ✅ выполнено 2026-10-18 (N1–N7: score 98,3 %, 154 выживших — эквиваленты, см. [MUTATION_TESTS.md](./MUTATION_TESTS.md#task-15-эквивалентные-мутанты-нового-кода--2026-10-18)). Продолжение [task-13](./task-13-mutation-new-code.md) и
[плана по mutmut](./MUTATION_TESTS.md): классы A–I и приёмы — оттуда.

## Контекст

Полный холодный прогон `just mutate` от 2026-10-18 (ветка `dev-10-26`,
коммит `7f0b16a`), отчёт — `just mutate-stats`
(`mutants/mutmut-analysis.md` / `.json`).

| | 2026-10-14 (task-13, до фикса) | 2026-10-18 |
| --- | ---: | ---: |
| мутантов | 7854 | 9216 |
| killed | 7443 | 8923 |
| survived | 404 | **286** |
| timeout | 7 | 7 |
| **mutation score** | 94.9 % | **96.9 %** |

После task-13 score вырос до 98.5 %. Рост числа мутантов (+1362) пришёл с
новым кодом, в нём же и выжившие: **Форточки** (API, склады, шины/диски),
**дубли** (`common_price_dispute`, `group_key`), **почтовые ссылки**
(`mail/client`, `mail/body`). Старый код регрессий не показал.

`mutate_only_covered_lines=true`, значит строки исполняются: проблема в силе
assertions, а не в покрытии. Разбивка по типу мутации: `string_wrap` 78,
`other` 55, `to_none` 55, `string_case` 49, `number` 19, `operator` 16,
`keyword` 9, `method_swap` 8, `none_to_empty` 4.

## Разбивка 286 выживших по фазам

| # | Фаза | Файлы | Выживших | Класс |
| --- | --- | --- | ---: | --- |
| N1 | Клиент Форточек (SOAP) | `remote/four_tochki_client.py` (56), `four_tochki_warehouses.py` (5), `four_tochki_warehouse_selection.py` (1), `infrastructure/config/four_tochki_api_config.py` (3) | 65 | A, C, D |
| N2 | Хелперы Форточек | `strategies/_four_tochki_tire_helper.py` (25), `_four_tochki_disk_helper.py` (1) | 26 | C, E |
| N3 | Дубли и группировка | `common_price_dispute.py` (18), `common_price_group_key.py` (5), `_group_fields.py` (5), `_size.py` (5), `_title_flags.py` (3), `_warehouses.py` (3), `_grouper.py` (2), `_exclude_doubles.py` (1), `_output.py` (1), `data_provider/doubles_settings.py` (5) | 48 | C, D, I |
| N4 | Почта: ссылки и тело письма | `mail/body.py` (14), `client.py` (12), `dates.py` (4), `download.py` (4), `message.py` (4), `links.py` (3), `doh.py` (2), `models.py` (1) | 44 | C, D |
| N5 | Разбор названий | `_tire_title_parser.py` (8), `_disk_title_parser.py` (7), `_tube_title_parser.py` (7), `_autosnab_helper.py` (4), `title.py` (3), `title_conflicts.py` (3), `title_registry.py` (2), `title_markers.py`, `title_params.py`, `domain/row_item/*` (3), `nomenclature_title.py` | 41 | C, E |
| N6 | Конфиги и конвейер | `vendor_config/slot_configs.py` (6), `source.py` (4), `models.py` (2), `provider.py` (2), `base_parser/*` (14), `registry.py` (3), `services/parse_orchestrator.py` (3), `strategies/pricing.py`, `category.py`, `tire_category.py` (6) | ≈ 40 | A, B, D |
| N7 | Остальное | `writer/*` (9), `run_dialog/*` (8), `xls_reader.py` (3), `result_folder.py` (2), `zapaska_client.py` (2), `parse_report.py` (1), прочее | ≈ 22 | F, I |

Порядок: N1 → N3 → N2 → N4 → N5 → N6 → N7.

---

## N1: клиент Форточек (65)

### Причина

`tests/test_parsers/test_remote/test_four_tochki_client.py` проверяет итог
(`rows`, факт исключения), но не структуру запроса и не содержимое ошибок.

### Что выживает (по функциям)

- **`_post` (9)** — заголовок `Content-Type` не проверяется по точному
  значению и регистру (`'content-type'`, `'TEXT/XML...'` проходят); `body=None`
  и опущенный `body` не ловятся (фейк соединения не записывает тело);
  `detail=None` в `FourTochkiApiConnectionError` — текст не ассертится.
- **`_raise_on_error` (5), `_result_element`, `_parse_response`,
  `_call_method`** — `detail=None`, `break` вместо `continue`,
  `_child_text(element, 'XXcodeXX')`: ошибки API проверены `pytest.raises`
  без `match`/`.detail`. Класс A/H.
- **`_disk_filter` (8), `_tire_filter`, `_paid_delivery_field` (4),
  `_warehouse_field`** — состав фильтра: `rim_type` (`'car'`/регистр), `None`
  вместо namespace, `'true'`→`'TRUE'`, разделитель `''.join` → `'XXXX'.join`.
  Тест `test_filters_are_sent_in_contract_namespace...` не сверяет XML целиком.
- **`_tire_rows` (11), `_disk_rows` (3)** — default у `_TIRE_TYPES.get(...)`,
  `_SEASONS.get(...)`, `_DISK_TYPES.get(...)`: нет теста на **неизвестный**
  код типа/сезона (проверен только известный). `spike` — `or True` не ловится
  (нет строки с `thorn != 'true'`).
- **`_local` (4), `_int`, `_float`, `_child_text`** — граничные значения:
  тег без namespace, пустой текст (`int(text or 1)` против `0`).
- **`download_catalogs` (3)** — `mkdir(parents=…)`: нет теста с вложенной,
  ещё не созданной папкой.
- **`four_tochki_warehouses._group` (5)** — `where → None` в
  `read_*`: путь ошибки в конфиге складов (класс A).

### План

1. Фейк соединения записывает `method`, `path`, `headers`, `body`; тест
   сверяет заголовки и тело запроса **целиком** (XML-строка).
2. Параметризованный тест на `_raise_on_error`/`_parse_response`/`_post`:
   ловить `FourTochkiApiError` и проверять `detail` (`method=… code=…`).
3. Таблица `_tire_rows`/`_disk_rows`: известный/неизвестный/пустой тип и
   сезон, `thorn` `true`/`false`/пусто.
4. Тесты `_local`/`_int`/`_float` на `{ns}tag`, `tag`, `''`, `'0'`.
5. `download_catalogs` в `tmp_path / 'a' / 'b'`.
6. Конфиг складов: ошибка в каждом ключе → `match` по пути (`→ groups[0]`).

---

## N2: хелпер шин Форточек (26)

### Причина

`_fill_size_from_title` (11) и `sidewall_from_title` (6): регулярные
подстановки `.sub(..., count=1)` и граница `size_end > 0` проверены без
входов, где `count`, `size_end ∈ {0, 1}` и повтор шаблона в строке различимы.

### План

- Параметризованный тест `_fill_size_from_title`: название, где префикс/
  `ALT`/`RIM` встречаются **дважды** (отличает `count=1` от `count=2`/без
  count); результат сверять по `width/height/diameter`.
- `sidewall_from_title`: названия с пробелом в позиции 0, 1, и без пробела
  (границы `size_end > 0/≥ 0/> 1`; `or True`).
- `_camera`, `_runflat`, `_tire_kind`, `_fill_size_suffix`: пустой `title`
  / `None` при заданном `run_flat`/`tire_type`/`diameter`.
- `_prepare_dimensions`: `'XX\1XX'` — вход с хвостовыми нулями, сверка строки.
- `_compose_title`: `height = None` — шина с высотой и без.

---

## N3: дубли и группировка (48)

### Причина

Новый код из коммитов `c15b9f1` и `7f0b16a`.

- **`common_price_dispute` (18)** — `_season_label` (8), `_spike_label` (5),
  `_xl_label` (5): мутации регистра и текста метки (`'ЗИМНЯЯ'`, `'ДА'`,
  `'XXдаXX'`). Либо сравнение в тестах нечувствительно к регистру, либо
  метка попадает в вывод, а тест её не читает. **Сначала решить: метка —
  часть контракта вывода (тогда ассертить) или внутренняя (тогда эквивалент,
  класс I, задокументировать).**
- **`group_key` (5)** — `define_intimacy`: `diameter or 1`,
  `.lower()`/`.upper()`, `'XXXX'`. Ошибка ключа сливает/разводит позиции,
  поэтому приоритет выше остальных в N3 (это не про текст, а про логику).
- **`doubles_settings` (5)** — `None` вместо `DOUBLES_CONFIG_FILE` в
  `read_str_list` (путь ошибки, класс A), `default=None`,
  `'XX, XX'.join(known_templates)` в тексте ошибки шаблона.
- Остальные модули `common_price_*` (≈20) — разобрать по `mutants/…md`
  после первых тестов: вероятно, класс D (поля группировки).

### План

1. Принять решение по меткам диспута (см. выше), затем таблица
   `(вход → ожидаемая метка)` по каждому из значений.
2. `group_key`: пары позиций, которые **должны** и **не должны** попасть в
   одну группу (интимность `lower/upper`, диаметр `'17,5'`/`17.5`/`None`).
3. `doubles_settings`: `ConfigValidationError` с `match` по имени файла и
   ключу; текст «доступные шаблоны» с разделителем `, `.

---

## N4: почта — ссылки и тело (44)

### Причина

- **`mail/body.py` (14)** — `_part_text`: кодировка по умолчанию
  (`'utf-8'`/`'UTF-8'`), режим ошибок `'replace'`, приоритет
  `get_content_charset() or 'utf-8'`; `_is_body_part` (вложение vs. тело);
  `message_text` — разделитель `'\n'`.
- **`mail/client.py` (12)** — `_price_from_link`: поля `subject/date/when`
  не проверяются, `message.get('Subject')` — заголовок читается без регистра;
  `_epoch` → `-inf`; `_unquote` — `errors='replace'`.
- `dates`, `download`, `message`, `links`, `doh` — по 2–4 на модуль.

### План

- Письмо с телом **не в UTF-8** (`windows-1251` без объявленной кодировки →
  `'replace'`, с объявленной → декодируется верно), вложение + тело.
- Фейк IMAP записывает `subject`/`date` и тест сверяет `PriceFromLink`
  целиком (как для `mail/client` в task-13 M1).
- `_epoch`: письмо без даты не должно выигрывать у письма с датой.

---

## N5–N7: остальное (≈ 100)

Разбирать по `mutants/mutmut-analysis.md` после N1–N4; те же приёмы:

- **N5 (классы C, E)** — таблицы «неканонический вход → канонический
  выход» для парсеров шин/дисков/камер (`_SIZE_SEPARATOR`, `_THREE_DASH`,
  `_MAX_PROFILE`, `fill_tube_fields` — ключи `height_percent`,
  `ext_diameter`).
- **N6 (A, B, D)** — путь ошибки (`where → None`) в `TitleConfig`,
  `MailProfile`, `select_source`; полное равенство dataclass вместо
  проверки одного поля.
- **N7 (F, I)** — `run_dialog/*` и `writer/*` проверить на наблюдаемость,
  ненаблюдаемые задокументировать как эквивалентные (как фаза 7).

---

## Критерии готовности

- `just mutate` → score ≥ **98.5 %** (уровень после task-13); любой
  оставшийся выживший либо убит, либо описан как эквивалентный в
  `MUTATION_TESTS.md` (класс I) с причиной.
- Тесты проверяют **значение** (заголовки, XML, `detail`, путь `where`,
  поля dataclass), а не факт вызова.
- Правится только `tests/`; если мутант указывает на мёртвый код — удалить
  код (vulture), а не писать тест.
- Полный набор проверок из `AGENTS.md` проходит (`just ci`), покрытие
  не ниже 95 %.

## Как запускать

```
just mutate-stats                      # отчёт по последнему прогону
uv run mutmut results | grep survived  # список выживших
uv run mutmut show <имя_мутанта>       # дифф конкретного мутанта
just mutate --paths-to-mutate src/parsers/remote   # прогон по подмножеству
```
