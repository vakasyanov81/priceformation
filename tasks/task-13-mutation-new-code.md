# Task-13: Усиление тестов нового кода по данным mutmut (2026-10-14)

Статус: ✅ выполнено 2026-10-14 — M1–M6, score 94.9 % → 98.5 %. Продолжение [плана по mutmut](./MUTATION_TESTS.md):
классы выживших (A–I) и приёмы фаз 1–7 — оттуда.

## Контекст

Полный холодный прогон `just mutate` от 2026-10-14 (ветка `dev_10_26`,
коммит `52c0698`), отчёт — `uv run python -m pipelines.mutmut_stats`
(`mutants/mutmut-analysis.md` / `.json`).

| | 2026-10-09 (после фазы 7) | 2026-10-14 |
| --- | ---: | ---: |
| мутантов | 5717 | 7854 |
| killed | 5610 | 7443 |
| survived | 100 | **404** |
| timeout | 7 | 7 |
| **mutation score** | **98.2 %** | **94.9 %** |

Регрессии в старом коде нет: прежние 100 выживших (эквивалентные, разобраны
в фазе 7) остались на месте. Все **+304** выживших — в коде, добавленном
после 2026-10-09: почта, классификатор типа товара (task-12), разбор названий
Пошка/STK, диапазоны наценки Форточек, колонка «Наценка руб.», справка.

`mutate_only_covered_lines=true`, значит строки исполняются — проблема,
как и в прошлой кампании, в силе assertions, а не в покрытии. Типичные
причины в новом коде:

- **фейки не записывают аргументы** — IMAP-фейк игнорирует критерии
  `SEARCH`, аргументы `FETCH` и флаг `readonly`, DoH/SSL не проверяют
  host/port/timeout/context;
- **проверяется итог, а не промежуточная структура** — тип товара сверяется,
  а разобранный `_Size` нет; после `fill_*_fields` не сверяются все поля;
- **путь ошибки (`where`) не ассертится** — класс A, как в фазе 1;
- **границы и логические операторы** без таблицы истинности — класс E.

## Разбивка +304 выживших по фазам

| # | Фаза | Файлы | Выживших | Класс |
| --- | --- | --- | ---: | --- |
| M1 | IMAP-клиент и DoH | `parsers/mail/client.py` (63), `parsers/mail/doh.py` (43) | 106 | D, E |
| M2 | Конфиг и разбор письма | `parsers/mail/models.py` (17), `infrastructure/config/mail_credentials.py` (13), `parsers/mail/message.py` (10), `parsers/mail/dates.py` (9), `services/mail_service.py` (3) | 52 | A, D, I |
| M3 | Классификатор типа товара | `parsers/strategies/product_type.py` (62), `product_types.py` (1) | 63 | B, E |
| M4 | Названия Пошка/STK | `_poshk_title_helper.py` (26), `_stk_title_helper.py` (21), `poshk_title.py` (8), `stk_title.py` (1) | 56 | B, C, E |
| M5 | Наценка и тип в конвейере | `strategies/pricing.py` (+3), `data_provider/models.py` (+4), `base_parser/price_markup.py` (+4), `row_processor.py` (+2), `base_parser.py` (+1), `services/parse_orchestrator.py` (+4) | 18 | A, D, E |
| M6 | Мелочь | `services/configure.py` (+2), `strategies/title_markers.py` (+2), `strategies/category.py` (+2), `run_dialog/help_format.py` (+1), `writer/xls_writer.py` (+1), `strategies/tire_category.py` (+1) | 9 | C, D |
| | **Итого** | | **304** | |

Порядок — по убыванию числа: M1 → M3 → M4 → M2 → M5 → M6.

---

## M1: IMAP-клиент и DoH (106)

### Проблема

`tests/test_parsers/test_mail/test_client.py`, фейк IMAP:

- `select(self, mailbox, _readonly=False)` — флаг игнорируется, имя
  `mailbox.strip('"')` — кавычки `_mailbox_arg` не видны;
- `uid(command, *args)` — для `SEARCH` критерии (`None, 'FROM', sender`)
  не читаются, всё прочее считается `FETCH` без проверки `'(RFC822)'`.

Отсюда выживают: `'FETCH'/'(RFC822)'/'FROM'/sender → None`, `or → and` в
проверке статуса `_search_uids`/`_fetch_message`, `True → False` в `_select`,
экранирование `\\`/`\"` в `_mailbox_arg`, `_is_quoted` (`<= → <`, `1 → 2`),
`_delimiter` (`'NIL'`, `upper → lower`), `list_price_folders`
(`'""'`, `'*'`), `_newer_of` (`> → >=`), `_price_from_message`
(прокидка `profile.subject_keyword`, `message`), `save_price`
(`parents=True`, `exist_ok=True`).

`doh.py`: у `open_client` / `_open_client_via_doh` / `_doh_addresses` /
`_ImapSslByAddress._create_socket` по 2–4 теста, аргументы не проверяются:
выживают выбрасывание `account.host`, `account.port`, `ssl_context`,
`timeout`, заголовка `Accept: application/dns-json`, текста ошибки
`'; '.join(errors)`.

### Решение

1. Фейк IMAP записывает каждый вызов (`calls: list[tuple[str, tuple]]`)
   и **не нормализует** вход: `select` хранит сырой `mailbox` и `readonly`.
   Тесты ассертят точный протокол:
   `('select', ('"INBOX.My Prices"', True))`,
   `('uid', ('SEARCH', None, 'FROM', 'a@b.ru'))`,
   `('uid', ('FETCH', b'7', '(RFC822)'))`.
2. Статусы: таблица `status × raw` для `_search_uids` / `_fetch_message`
   (`'NO'` с данными, `'OK'` без данных) — убивает `or → and`.
3. `_mailbox_arg` / `_is_quoted` / `_unquote` / `_delimiter` — таблица
   входов: пустая строка, одна кавычка `'"'`, `'""'`, имя с `\` и `"`,
   разделитель `NIL` в разных регистрах.
4. `_newer_of` — равные даты (граница `>`), `None` с любой стороны.
5. `save_price` — запись в несуществующую вложенную папку и повторная
   запись в существующую.
6. DoH: подменять `urllib.request.urlopen`, `IMAP4_SSL`,
   `socket.create_connection` фейками с записью аргументов; ассертить URL,
   заголовок `Accept`, `timeout`, `(address, port)`, `server_hostname`,
   что `ssl_context` — тот самый объект; при отказе всех адресов — полный
   текст ошибки с `host:port` и списком причин.

### Итог (2026-10-14)

106 → 6 выживших, все эквивалентные (регистр строк — в таблице ниже). Полный
прогон: survived 404 → 304, score 94.9 % → 96.1 %. Правки
кода по причине, а не под тест:

- `_LIST_LINE` принимал только `NIL` в верхнем регистре, поэтому `.upper()` в
  `_delimiter` был мёртвым; `NIL` — атом IMAP, регистр не важен → регулярка
  `(?i:NIL)`, тест на `nil`.
- `_in_subtree(name == root)` дублировал `_with_root`: корень теперь всегда
  первым (`[root, *потомки]`), `_with_root` удалён, `_is_descendant` — строгая
  вложенность.
- `message.get('Subject', '')` → `message.get('Subject')`: дефолт был лишним,
  `decode_header_value(None)` и так даёт `''`.
- `connect` открывал `account.folder` без квотинга, в отличие от поиска —
  папка с пробелом в `mail.json` ломала подключение; теперь `_mailbox_arg`.

Фейк IMAP ведёт журнал `calls`, разбирает SELECT/SEARCH/FETCH строго по
протоколу (неверные аргументы → `BAD`) и по RFC 3501 снимает выбор папки при
неудачном SELECT. DoH-тесты вынесены в `test_doh.py`.

### Ожидаемые эквивалентные

- `'FETCH' → 'fetch'`, `'SEARCH' → 'SEARCH'`: `imaplib.IMAP4.uid`
  делает `command.upper()`.
- текст `'Non-blocking socket (timeout=0) is not supported'` — копия
  stdlib; проверить тестом `timeout=0` или задокументировать.

---

## M2: Конфиг почты и разбор письма (52)

### Проблема

- `mail/models.py`: `where → None` в `MailAccount` / `MailConfig` /
  `MailProfile.from_dict`, `_read_optional_text`, `_read_profiles` (17) —
  класс A, тесты матчат текст ошибки без пути до ключа.
- `mail_credentials.py`: тексты приглашений `input()` (8), `_MSG_MISSING → None`
  (3), `_resolve_missing` (`and → or`), `get_mail_credentials`
  (`password → None`).
- `message.py` / `dates.py`: `'' → None` и обёртки в
  `message.get('From'|'Subject'|'Date', '')` — нет письма без заголовка;
  `subject_matches` покрыт **одним** тестом.
- `mail_service._collect`: `continue → break` — нет списка профилей, где
  пропуск стоит не последним.

### Решение

1. Модели почты — приём фазы 1: `ConfigValidationError` ассертится с
   полным путём (`mail.json: profiles[1].sender`), по одному кейсу на
   каждый вызов `read_*` с `where`.
2. `mail_credentials`: фейк `input` записывает prompt — ассерт точного
   текста; ошибка — полный текст `_MSG_MISSING`; таблица для
   `_resolve_missing` (есть логин/нет пароля, наоборот, оба пусты);
   `get_mail_credentials` — сверка обоих полей результата.
3. Письма без `From` / `Subject` / `Date` — для каждой функции
   (`sender_matches`, `subject_matches`, `format_date`, `message_datetime`,
   `_price_from_message`). Для `subject_matches` — таблица: пустое
   ключевое слово, регистр, отсутствие темы.
4. `_collect`: три профиля, пропускается средний — третий должен попасть
   в результат.

### Итог (2026-10-14)

52 → 8 выживших, все эквивалентные (регистр имени заголовка). Полный прогон:
survived 187 → 143, score 97.5 % → 98.1 %. Правки кода:

- `message.get('From'|'Subject'|'Date', '')` → без дефолта: пустую строку и
  так дают `decode_header_value(None)` / `or 'дата неизвестна'`;
  `message_datetime` проверяет отсутствие заголовка явно.
- `MailAccount.from_dict` принимает уже проверенный объект: `read_object`
  проверял `imap` раньше, повторная `as_config_object` была мёртвой.

Тесты: точный текст `ConfigValidationError` с путём до ключа на каждый `where`,
приглашения `input`/`getpass` и полный `_MSG_MISSING`, письма без
заголовков, профиль без письма в середине списка.

### Ожидаемые эквивалентные

- `'From'/'Subject'/'Date' → нижний/верхний регистр` (~10):
  `email.message.Message.get` нечувствителен к регистру. Добавить паттерн
  в `do_not_mutate_patterns` нельзя (он построчный и задел бы `''`), —
  задокументировать в разделе эквивалентных.
- `'utf-8' → 'UTF-8'` в `_unquote` (M1) — имя кодека.

---

## M3: Классификатор типа товара (63)

### Проблема

`product_type.py`, 154+ теста на `classify`, но:

- `_parse_title_size` (33): выживает выбрасывание `width=` / `profile=` /
  `diameter=`, сдвиг номера группы, `'slash_dash'/'agro' → None` почти во
  всех формах размера. Тесты проверяют итоговый тип, а не разобранный
  `_Size`; часть полей в решении о семействе не читается.
- Границы `0 → 1` и `or → and` в `_is_moto`, `_is_special`,
  `_metric_family`, `_inch_family`, `_flotation_family`,
  `_width_only_family` (`>= → >`), `_is_truck_dash` (`4 → 5`), `_pr`,
  `_decimals` (`partition → rpartition`) — ~20.
- `ProductTypeClassifier.classify`: строка `'c'` (регистр/обёртка);
  `product_types.canonical_declared`: `or → and`.

### Решение

1. **Сначала разобрать, какие поля `_Size` реально читаются** решающими
   функциями. Поля, которые не читаются ни в одной форме, — мёртвые данные:
   удалить из `_Size`/разбора (фикс в коде, а не в тестах), а не писать на
   них тесты. Это сократит часть из 33 без новых тестов.
2. Для оставшихся — табличный тест прямо на `_parse_title_size`:
   вход → **полное** равенство `_Size` (форма, ширина, профиль, диаметр,
   суффикс) для каждой из форм: `metric2`, `metric`, `flotation`,
   `width_only`, `inch`, `slash_dash`, `agro`.
3. Таблицы истинности на пороги: значения ровно на границе и ±1 для
   каждого предиката семейства; `_is_truck_dash` — дефис на позиции 4/5;
   `_decimals` — строка с двумя точками.
4. `canonical_declared`: кейс, где истинна только одна сторона `or`.
5. `classify`: кейс, на котором срабатывает ветка с `'c'` (выяснить
   смысл: если это суффикс размера — ассерт в таблице п. 2).

Тесты — рядом с golden: `tests/.../test_product_type/`, идентификаторы
параметров только ASCII (ловушка mutmut, см. MUTATION_TESTS.md).

### Итог (2026-10-14)

63 → 0 выживших в `product_type.py`/`product_types.py`; полный прогон:
survived 304 → 241, score 96.1 % → 96.9 %. Почти все выжившие указывали на
мёртвые данные и дублирующие решения — правка в коде:

- `_Size` разведён на формы `_Metric` / `_Inch` / `_Flotation` / `_WidthOnly` /
  `_Dash` / `_SpecialForm`, в каждой только читаемые поля. Ширина у флотации
  и `width_only`, все числа у `slash_dash`/`agro` не читались ни одним
  решением — удалены. Ширина и диаметр из названия теперь `float`, без
  мёртвых `(x or 0)`; неизвестный профиль (размер из полей) — `_at_least`.
- `suffix: str` → `commercial: bool`: значение суффикса нигде не сравнивалось.
- Спец-формы (`slash_dash`, `agro`) решаются в `classify` по типу формы;
  диагональ — только в `_family` (раньше дублировалась в `_is_special`).
- `_is_moto` больше не проверяет мото-слова — `classify` вернул MOTO раньше.
- `_pr` + `default=0` → `_has_truck_pr`: дефолт был неотличим от любого < 14.
- `_decimals` + `first < 10` → регулярка `_TRUCK_DASH_WIDTH` (`[1-9]\d\.\d{2}`).
- `_dimension` без замены запятой: её уже убирает `normalize_text`.
- `canonical_declared`: проверка `_GENERIC_LABELS` дублировала поиск в
  `_DECLARED_ALIASES` (общих ярлыков и `''` там нет) — список удалён.

Тесты на причину — `test_size_parse.py`: полное равенство формы для
каждой регулярки и таблицы порогов (диагональ 17.5–24 и ширина `dd.dd`,
14PR, мото, неизвестный профиль, маркер C по формам).

---

## M4: Названия Пошка и STK (56)

### Проблема

- `fill_poshk_fields` / `fill_stk_fields`: ключи `'height_percent'`,
  `'intimacy'` → `XX…XX`/верхний регистр, `model = '' → 'XXXX'` — поля после
  заполнения не сверяются (класс B).
- `_size_label` (оба хелпера): `upper → lower`, `'R' → 'XXRXX'`,
  `== → !=` на `construct` — метка размера в названии не ассертится точно.
- `_merge_pr` (`and → or`, `- → +`, `1 → 2`), `_strip_kind_suffix`
  (`> → >=`), `StkTitleParts.from_raw` (`> → >=`, `1 → 2`),
  `parse_poshk_title` (`lstrip → rstrip`) — граничные входы.
- `(raw or '')`, `\1PR → \1pr` в `_prepare_text` / `parse_stk_title` — нет
  пустого входа и PR в нижнем регистре (класс C).
- `PoshkTireCompose`: `brand_probe` не прокидывается в тестах
  (`__init__`), `_ship_without_brand` — `or → and`.

### Решение

1. После `fill_*_fields` — полное сравнение всех заполняемых полей
   `RowItem` (через `field_registry`), включая `height_percent`, `intimacy`,
   и кейс, когда `model` уже был заполнен.
2. Таблица `_size_label`: R/ZR/без конструкции, нижний регистр на входе,
   `construct` совпадает/не совпадает.
3. Граничные названия: одно слово после размера (`len(rest) == 1`),
   два PR подряд, PR в начале, суффикс вида ровно на границе длины,
   пробелы слева и справа.
4. Пустое/`None` название и `pr` в нижнем регистре.
5. `PoshkTireCompose`: фейковый `brand_probe` с записью вызовов; таблица
   для `_ship_without_brand`.

### Итог (2026-10-14)

`PoshkTireCompose` оказался «сиротой» (не в реестре, `poshk.json` ссылался на
`stk_tire_compose`), а в `tasks/merge-poshk-stk-tire-compose.md` ждало слияние.
Сначала выполнено слияние → `PoshkStkTireCompose` / `_poshk_stk_title_helper`
(итоги и сверка на боевых прайсах — в файле плана), тесты M4 написаны уже на
общий код. Правки по выжившим:

- `raw or ''` (×4) → `parse_poshk_stk_title(raw: str | None)` с ранним `None`.
- `_merge_pr` → регулярка `_SPLIT_PR` в `_prepare_text`.
- `_strip_kind_suffix`: проверка длины мертва — токен-обёртку целиком уже
  отбросил `_KIND_WORDS`.
- `_size_label`: `'R' if upper == 'R' else construct` → `construct.upper()`.
- `fill_*_fields`: `model = '' if model else …` дублировал общую проверку
  «не перетирать готовое».
- Попутно найдена ошибка суффикса `C`/`LT` (съедал первую букву бренда).

56 → 3 выживших (2 эквивалентных — в таблице; 1 — `title_registry._brand_probe`
`[0] → [1]`, вне M4). Полный прогон: survived 241 → 187, score 96.9 % → 97.5 %.

---

## M5: Наценка и тип в конвейере (18)

- `pricing.RecommendedRangeMarkupPolicy.apply`: `0 → 1`,
  `type_production or ''`, `opt → None` — кейсы: тип отсутствует,
  нулевая оптовая цена, цена ровно на границе диапазона.
- `PercentByThresholdMarkupPolicy.__init__`: дефолтные правила при `None` —
  сверить, что применяется пустой `MarkupRulesConfig`.
- `data_provider/models.py`: `where → None` в `MarkupRulesConfig` /
  `PercentRange.from_dict` — путь ошибки (фаза 1).
- `price_markup.fill_absolute_markup`: `continue → break` (пропуск не
  последним), округление `2 → 3` / `2 → None` — значение с третьим знаком.
- `row_processor.add_price_markup`: прокидка `type_production` в политику
  (фейковая политика записывает аргумент); `apply_min_rest`: `0 → None`.
- `base_parser`: `apply_category` (прокидка `title`),
  `zero_rest_without_category` (точный `0`), `_type_production_from_filename`
  (`maxsplit=1`: имя файла с двумя разделителями).
- `parse_orchestrator`: `_parse_supplier` (`+= → =`, `+ → -` — два
  поставщика, счётчик суммируется), `_log_skips` (сообщение о
  `type_corrections`), `_parser_for_vendor` (прокидка `vendor_config`).

### Итог M5 (2026-10-14)

18 → 7 выживших: 6 эквивалентных (таблица ниже) и 1 открытый вопрос
(`ParserFactory`, ниже). Правки кода: `RecommendedRangeMarkupPolicy.apply` без
мёртвого `price_opt or 0` (закуп уже `float`), `_type_production_from_filename`
через `rpartition` (`maxsplit` у `rsplit(...)[-1]` ненаблюдаем), ветки
`vendor_config is None` и «выключен» в `_parser_for_vendor` слиты. Тесты:
процент карты внутри диапазона, `markup_percent_for_opt` порога, обход и
округление `fill_absolute_markup`, прокидка `type_production` в политику,
полный текст debug-лога расхождения, пути ошибок `category_markup_ranges`,
сумма `type_corrections` и её сводка.

**Открытый вопрос.** `_parser_for_vendor` не использует параметр
`parser_factory`: зарегистрированная в DI `ParserFactory` (`make_parser`) нигде
не строит парсеры (включённые — `make_config_driven_parser`, остальные —
`vendor_cls(...)`). Удалить фабрику из DI или начать её использовать — решение
по архитектуре, не по тестам.

## M6: Мелочь (9)

- `services/configure._register_services`: `HelpService → None` выживает
  при 2186 тестах — проверить, что `HelpService` резолвится из контейнера
  в тесте (иначе регистрация не наблюдаема).
- `title_markers._apply_markers`: `continue → break`, пустое название.
- `category.HeaderRowsCategory`: `None → ""` в `__init__`, `'/'` в
  `_first_chunk` — кейсы на исходное состояние и заголовок с `/`.
- `help_format.colorize_markdown`: `False → None` — уточнить, что флаг
  наблюдаем; иначе эквивалентный.
- `xls_writer.get_value` / `tire_category`: пустой `cell_value` / `raw_title`
  (класс C).

### Итог M6 (2026-10-14)

`HeaderRowsCategory.current_category` стал `str` (начально `''`) вместо
`str | None` — ушли четыре мёртвых `or ''`; `_is_header_row` → `_header_title`.
Тесты: `HelpService` из контейнера, несовпавший первый маркер, суффикс к
пустой ячейке, смешанный раздел без уточнения, начальное состояние раздела.
Остаток — эквивалентные (таблица ниже).

---

## Как работать

```bash
just mutate                       # полный холодный прогон (сносит mutants/)
just mutate-stats                 # mutants/mutmut-analysis.md / .json
just mutate "parsers.mail.*"      # точечно по фазе — только для итерации
```

Точечный прогон годится для итерации, но score считать только по полному
прогону (см. ловушку кэша в `pipelines/run_mutation_test.sh`). Не запускать
mutmut параллельно с `pytest`.

Правила из `AGENTS.md` действуют: если выживший указывает на мёртвый код
или лишнее поле — правится код (с тестом на причину), а не пишется тест под
текущее поведение. Новые `do_not_mutate_patterns` — только для доказанно
ненаблюдаемого текста, с комментарием в `pyproject.toml`.

## Критерии готовности

- [x] Полный прогон: score **≥ 98 %** — 98.5 % (7322 / 112).
- [x] В файлах из таблицы фаз каждый оставшийся выживший разобран:
      эквивалентный / ненаблюдаемый — с причиной в разделе ниже
      (кроме открытого вопроса `ParserFactory` в M5).
- [x] Мёртвые поля `_Size` (M3, п. 1) удалены.
- [x] Таблица «Контекст» в [MUTATION_TESTS.md](./MUTATION_TESTS.md)
      дополнена колонкой с итогом этой задачи.
- [x] `just ci` зелёный.

## Эквивалентные (заполнять по ходу)

| Файл / функция | Мутация | Почему эквивалентна |
| --- | --- | --- |
| `mail/client._fetch_message`, `_search_uids` | `'FETCH'/'SEARCH'` → другой регистр | `imaplib.IMAP4.uid` делает `command.upper()` |
| `mail/message`, `mail/dates`, `_price_from_message` | `'From'/'Subject'/'Date'` → другой регистр | `Message.get` нечувствителен к регистру имени заголовка |
| `mail/client._unquote` | `'utf-8' → 'UTF-8'` | имя кодека нечувствительно к регистру |
| `mail/client._epoch` | `'-inf' → '-INF'` | `float()` разбирает `inf` без учёта регистра |
| `mail/doh._doh_addresses` | `'Accept'` → другой регистр | `urllib.request.Request` хранит заголовок как `key.capitalize()` |
| `base_parser.zero_rest_without_category`, `row_processor.apply_min_rest` | `0 → None` в `rest_count` | `RowItem` приводит `rest_count=None` к `0` |
| `pricing.RecommendedRangeMarkupPolicy.apply` | `type_production or '' → 'XXXX'` | ни `''`, ни `'XXXX'` не ключ `category_markup_ranges` |
| `pricing.PercentByThresholdMarkupPolicy.__init__` | `MarkupRulesConfig() → None` | собственный `apply` не читает `_rules`; карту % проверяет тест |
| `parse_orchestrator._parser_for_vendor` | `getattr(..., None)` без дефолта | `_vendor_section`/`_vendor_config` объявлены в `ParseConfiguration` |
| `category.TitleKeywordsCategory`, `FieldMapCategory`, `tire_category`, `title_markers` | `x or '' → 'XXXX'` | заглушка не совпадает ни с ключом карты, ни с маркером, ни с размером |
| `xls_writer.get_value` | `field_name or True` | `PriceRow` — `dict`, `get('')` даёт `None` |
| `help_format.colorize_markdown` | `in_code = False → None` | флаг только инвертируется `not`: `not None == not False` |
| `_poshk_stk_title_helper._prepare_text` | `r'\1PR' → r'\1pr'` (×2) | `_PR` без учёта регистра, слойность приводится `.upper()` |
