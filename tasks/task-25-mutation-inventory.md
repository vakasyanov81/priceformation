# Реестр мутаций к task-25

Источник: `mutants/mutmut-analysis.json`, SHA-256 `c7d7e5424b80986e8b7301bd39ed6963e9f0d571de8ca7db4ff1babedfc5190c`.

Снимок анализа 2026-11-13. Все 885 survived и 9 timeout приведены раздельными записями.
Удаляемые строки diff присутствуют в текущих файлах. Это не подтверждает актуальность результатов тестов.
Индивидуальная эквивалентность всех записей не установлена; выводы — в [задаче](task-25-mutation-survivors.md).
Число тестов означает список выбора mutmut, а не число проверок контракта; точные списки остаются в исходном JSON.

## Индивидуальная классификация: проверка 2026-11-14

Повторные целевые запуски выполнены на рабочем дереве поверх `4fde65b`
с пятью новыми тестами схем прайсов. Имена в заголовках и строки «Статус»
по-прежнему относятся к историческому отчёту. Номера mutmut между генерациями
меняются: результат перенесён только при совпадении удаляемых и добавляемых
строк diff внутри той же функции; текущий ID указан при отличии от исторического.
Пробелы отступа при сопоставлении не учитывались, содержимое строк сохранялось.
Несопоставленные изменения не объявлялись убитыми по одному совпадению номера.

Команды, на которые ссылаются записи этого блока:

- R1: `uv run mutmut run 'app.parse_report.*' 'app.parse_report_groups.*' 'app.run.*'`.
- R2: `uv run mutmut run 'domain.battery.*' 'domain.product_group_result.*' 'parsers.battery.*' 'parsers.price_schema.*'`.
- R3: `uv run mutmut run 'parsers.price_schema.*'` после добавления тестов.

В этом блоке классифицировано ещё 118 записей: 104 killed с сопоставленным
изменением, 12 эквивалентов с доказательствами и 2 отдельно воспроизведённых timeout.
После этого блока было классифицировано 155 из 894 записей; актуальный итог
после продолжения приведён ниже. Все девять timeout
теперь имеют индивидуальное объяснение. Это не новый полный отчёт mutmut.

## Продолжение индивидуальной классификации: сервисы и инфраструктура

Проверка 2026-11-14 выполнена поверх `699690c` с изменениями тестов этого блока.
Все 63 записи сопоставлены по удаляемым и добавляемым строкам diff внутри той же
функции; текущие ID совпадают с историческими. Исторические статусы сохранены.

- R4: `uv run mutmut run 'services.price_schema_service.*' 'services.vendor_activity.*' 'services.zapaska_service.*' 'services.mim_service.*' 'services.four_tochki_service.*'`.
- R5: `uv run mutmut run 'infrastructure.mail.*' 'infrastructure.remote.*' 'infrastructure.data.price_backup.*' 'infrastructure.config.mim_api_config.*' 'infrastructure.config.result_folder.*'`.
- R6: `uv run mutmut run 'services.mim_service.*' 'services.four_tochki_service.*' 'infrastructure.config.mim_api_config.*' 'infrastructure.config.result_folder.*'` после усиления тестов.

Добавлено 63 индивидуальных классификации: 48 killed (40 на существующих тестах,
8 после усиления) и 15 эквивалентов с объяснениями. Всего завершены **218 из 894**,
остались **676**: 675 без классификации и одна с незавершённым разбором.
Все девять timeout разобраны ранее. Это целевые прогоны, а не новый полный отчёт.

Вывод прежнего группового разбора `clear_result_folder` уточнён: missing_ok=False
или None различимы при исчезновении файла после перечисления каталога. Новый тест
детерминированно задаёт такой вход и убивает обе мутации; они не эквивалентны.
Исторический `PriceSchemaService.__init____mutmut_3` меняет `or` на `and` при выборе
backup_folder и убит; эквиваленты начального `_copied` — исторические `6` и `7`.

## Продолжение индивидуальной классификации: оркестрация и фабрики отчётов

Проверка 2026-11-14 выполнена поверх `da9893a` с новыми и усиленными тестами
этого блока. Все 23 записи сопоставлены по удаляемым и добавляемым строкам diff
внутри той же функции; текущие ID совпали с историческими. Исторические статусы
не переписаны.

- R7: `uv run mutmut run 'services.doubles_service.*' 'services.mail_service.*' 'services.parse_logging.*'` до усиления тестов.
- R8: `uv run mutmut run 'services.doubles_service.*' 'services.mail_service.*' 'services.parse_logging.*' 'services.group_processing.*' 'services.parse_orchestrator.*' 'services.price_report.*'` после первых проверок дублей и почты.
- R9: та же команда, что R8, после проверки фабрик, очереди эталонов и аккумуляторного выбора.
- R10: `uv run mutmut run 'services.parse_orchestrator.xǁParseOrchestratorǁ_parse_supplier__mutmut_26'` после уточнения ненулевых шинных счётчиков чужой группы.

Итог: 23 killed — 3 на существующих тестах, 20 после усиления.
Всего завершена **241 из 894** записей; остаются **653**:
652 без классификации и одна с незавершённым разбором. Девять timeout
разобраны ранее. Код приложения не менялся. Это целевые прогоны;
новый полный отчёт mutmut на отдельном коммите ещё не сформирован.

## Продолжение индивидуальной классификации: оставшиеся записи JSON-оболочки CLI

Проверка 2026-11-14 выполнена поверх `8abf3ba` с изменениями тестов этого блока.
Завершены 13 записей из `app.parse_report_build`, `app.parse_report_groups` и
`app.run_machine`: **10 killed на существующих тестах, 3 после усиления**.
Всего завершены **254 из 894**, остаются **640**: 639 без классификации
и одна с незавершённым разбором. Все девять timeout разобраны ранее.

- R11: `uv run mutmut run 'app.run_machine.*' 'app.parse_report_build.*'`.
  Текущая генерация содержит только часть исторических изменений; номера
  не использованы как доказательство совпадения. Округление времени осталось survived.
- R12: каждое из 13 исторических изменений применено отдельно по полному
  контексту сохранённого diff к исходному файлу во временной копии `src/` и
  `tests/` с `pyproject.toml`, `setup.cfg`, `.coveragerc` из рабочего дерева.
  Перед заменой проверено единственное точное вхождение удаляемого блока с
  контекстом; после каждого запуска исходный файл восстановлен.
  Команда из этой копии (repo — корень исходного репозитория, copy — временная копия):
  `PYTHONPATH="$copy/src" PYTHONDONTWRITEBYTECODE=1 uv run --project "$repo" python -m pytest -c "$copy/pyproject.toml" --rootdir "$copy" --no-cov -n=0 "$copy/tests/test_cli"`.
  Базовый запуск: 139 passed; каждый мутант: exit 1 с конкретным провалом
  проверки, имена проверок приведены в индивидуальных записях.
  Для сравнения тесты трёх изменённых файлов заменены версиями из `8abf3ba`:
  базовый запуск 135 passed, 10 мутаций убиты, три survived.

Три пропуска находились в слое app: точность округления результата до сотых,
сохранение выбранных групп при KeyboardInterrupt и сообщение команды в файловом
логе при исключении вне оркестратора. Добавлены дробное время, прерывание при
чтении/записи и после получения отчёта дублей, проверка сообщения в реальном логе.
Код приложения не менялся. Целевые и прямые прогоны не заменяют новый полный отчёт.

## Продолжение индивидуальной классификации: доменные признаки и почтовый разбор

Проверка 2026-11-14 выполнена поверх `1a6ac52`. Завершены 22 записи:
четыре оставшиеся из `domain.row_item` и все 18 из `parsers.mail`.
Каждая признана эквивалентной с индивидуальным объяснением ниже.
Всего завершены **276 из 894**, остаются **618**: 617 без классификации
и одна с незавершённым разбором. Все девять timeout разобраны ранее.

- R13: каждое из 22 исторических изменений применено отдельно во временной
  копии `src/` и `tests/` с `pyproject.toml`, `setup.cfg`, `.coveragerc`.
  Перед заменой проверено единственное точное вхождение полного удаляемого
  блока вместе с контекстом; исходный файл восстановлен после каждого запуска.
  Команда (repo — исходный репозиторий, copy — временная копия):
  `PYTHONPATH="$copy/src" PYTHONDONTWRITEBYTECODE=1 uv run --project "$repo" python -m pytest -c "$copy/pyproject.toml" --rootdir "$copy" --no-cov -n=0 "$copy/tests/test_parsers/test_mail" "$copy/tests/test_domain/test_row_item/test_disk_name_extras.py" "$copy/tests/test_domain/test_row_item/test_markdown_title.py" "$copy/tests/test_domain/test_row_item/test_production_plant.py" "$copy/tests/test_domain/test_row_item/test_production_year.py"`.
  Базовый запуск и все 22 отдельных запуска: **184 passed**, exit 0.
  Номера новой генерации mutmut не использовались.

Доказательства опираются на поток данных и контракты: короткое замыкание `and`,
невозможность совпадения fallback с доменными шаблонами, скобки заводской метки,
регистронезависимый поиск заголовков `Message.get`, одинаковые кодеки UTF-8,
перехват неизвестной кодировки и сохранение последнего сегмента URL.
Код и тесты не менялись; эквиваленты не требуют искусственных проверок ради score.
Это прямые целевые прогоны, а не новый полный отчёт mutmut.
Все девять команд AGENTS.md завершились с exit 0: 4159 тестов, покрытие 99,44 %.

## Продолжение индивидуальной классификации: имена и резервирование файлов writer

Проверка 2026-11-14 выполнена поверх `c5001be` с тестами этого блока.
Завершены все 24 оставшиеся записи `group_files`, `jsonl_meta`, `output_names`
и `output_paths`: **19 killed** (13 на существующих тестах, 6 после усиления)
и **5 эквивалентов** в рамках указанных контрактов.
Всего завершены **300 из 894**, остаются **594**: 593 без классификации
и одна с незавершённым разбором. Все девять timeout разобраны ранее.

- R14: 24 исторических diff по одному применены во временной копии `src/`
  и `tests/` с `pyproject.toml`, `setup.cfg`, `.coveragerc` из рабочего дерева
  до усиления тестов: база 248 passed, 13 killed, 11 survived.
- R15: тот же набор после трёх новых сценариев и исправления входа теста
  регистра JSONL: база 251 passed, 18 killed, 6 survived.
- R16: после добавления диагностики пустого имени: база 252 passed;
  `register_paths__mutmut_14` — 1 failed, 251 passed. Остальные diff повторно
  не запускались: R15 уже дал их индивидуальные результаты.

Для каждой замены проверялось единственное точное вхождение удаляемого блока
с полным контекстом; файл восстанавливался перед следующим мутантом.
Команда R14–R16 (repo — исходный репозиторий, copy — временная копия):
`PYTHONPATH="$copy/src" PYTHONDONTWRITEBYTECODE=1 uv run --project "$repo" python -m pytest -c "$copy/pyproject.toml" --rootdir "$copy" --no-cov -n=0 "$copy/tests/test_parsers/test_writer"`.
Номера текущей генерации mutmut для сопоставления не использовались.

Исправлены прежние групповые выводы: добавление X к запрещённым символам
меняет множество допустимых имён; `and → or` разрешает конфликт книг разных
шаблонов; `write_plan` имеет наблюдаемый дефолт XLSX; отключение поиска регистра
JSONL различимо при корректном расширении .jsonl и переименованном файле.
Пустое имя доходит до register_paths и обязано сохраняться в диагностике.
Корень пробелов — неполные входы тестов writer; исходный код проходит новые
проверки и не менялся. Целевые прогоны не заменяют новый полный отчёт mutmut.
Все девять команд AGENTS.md завершились с exit 0: 4163 теста, покрытие 99,46 %.

## Продолжение индивидуальной классификации: XLSX-драйвер

Проверка 2026-11-14 выполнена поверх `c618609` с тестами этого блока.
Проверены 14 записей `xlsxwriter_adapter` и `ixlsx_driver`: завершены **13**
(**9 killed после усиления**, **4 эквивалента**). Одна запись получила
воспроизводимое различие, но её разбор остаётся незавершённым.
Всего завершены **313 из 894**, остаются **581**: 579 без классификации
и две с незавершённым разбором (base_finder._search и _update_width).
Все девять timeout разобраны ранее.

- R17: все 14 исторических diff по одному применены во временной копии
  `src/`, `tests/`, `pyproject.toml`, `setup.cfg`, `.coveragerc` до усиления:
  база и каждый мутант — 252 passed, exit 0.
- R18: тот же набор после добавления семи параметризованных случаев:
  база 259 passed; 9 мутантов — exit 1 с конкретным провалом нового теста,
  5 — 259 passed, exit 0. Позднее только имя параметра и таблица коротких
  значений приведены к правилам flake8; входы и проверки не менялись.
- R19: исходник и точный diff `_update_width__mutmut_1` проверены отдельно
  через публичный API и openpyxl. Последовательность и различающиеся ширины
  приведены в индивидуальной записи. Это survived с открытым вопросом
  контракта, а не эквивалент.

Перед каждой заменой проверено единственное точное вхождение полного блока
с контекстом; после запуска файл восстановлен. Команда R17/R18 (repo — корень
исходного репозитория, copy — временная копия):
`PYTHONPATH="$copy/src" PYTHONDONTWRITEBYTECODE=1 uv run --project "$repo" python -m pytest -c "$copy/pyproject.toml" --rootdir "$copy" --no-cov -n=0 "$copy/tests/test_parsers/test_writer"`.
R19 использует те же окружение и `uv run --project "$repo" python`, записывает
XLSX после указанной последовательности и читает ширину через openpyxl.
Номера текущей генерации mutmut для сопоставления не использовались.

Прежние групповые объяснения уточнены: форматы колонок видны на листе без ячеек;
книга без листа достижима штатно; дефолт +1 различим на первом коротком значении.
Граница <= → < тоже различима после повторного форматирования; эквивалентность
для всех публичных вызовов не доказана. Код приложения не менялся.
Это прямые целевые проверки, а не новый полный отчёт mutmut.
Все девять команд AGENTS.md завершились с exit 0: 4170 тестов, покрытие 99,46 %.

## Продолжение индивидуальной классификации: план записи и структура шаблонов

Проверка 2026-11-14 выполнена на чистом дереве `e59df5b`. Завершены все
12 записей `output_plan`, `output_structure` и `output_validation`:
**8 killed на существующих тестах и 4 эквивалента** в контракте публичного
`prepare_output_plan`. Всего завершены **325 из 894**, остаются **569**:
567 без классификации и две с незавершённым разбором (`base_finder._search`
и `_update_width`). Все девять timeout разобраны ранее.

- R20: каждый из 12 исторических diff отдельно применён во временной копии
  `src/`, `tests/`, `pyproject.toml`, `setup.cfg`, `.coveragerc`.
  Проверено единственное точное вхождение удаляемого блока с полным контекстом;
  после каждого запуска исходный файл восстановлен. База: **259 passed**;
  восемь мутаций — exit 1 с конкретным провалом, четыре — 259 passed, exit 0.
  Команда (repo — корень исходного репозитория, copy — временная копия):
  `PYTHONPATH="$copy/src" PYTHONDONTWRITEBYTECODE=1 uv run --project "$repo" python -m pytest -c "$copy/pyproject.toml" --rootdir "$copy" --no-cov -n=0 "$copy/tests/test_parsers/test_writer"`.

Эквивалентность четырёх мутаций `_place_sheets` основана на предварительной
проверке имён в `validate_outputs → register_paths`, а не только на survived:
пустые/неверные имена отклонены до построения плана, where используется только
в ошибках. Приватный вызов без валидации вне рассмотренного контракта.
Остальные изменения обнаруживают проверки режима книги, явного выбора групп,
пустого template_id и контекста диагностик. Код и тесты не менялись.
Исторические статусы сохранены; это не новый полный отчёт mutmut.

Все девять команд AGENTS.md завершились с exit 0: 4170 тестов, покрытие 99,46 %.

## Продолжение индивидуальной классификации: JSONL и диагностика драйвера

Проверка 2026-11-14 выполнена поверх `5309d17`. Завершены все восемь
оставшихся записей `writer.errors`, `jsonl_packing`, `jsonl_publish`,
`jsonl_schema` и `jsonl_writer`: **5 killed** (3 на существующих тестах,
2 после усиления) и **3 эквивалента** с индивидуальными объяснениями.
Всего завершены **333 из 894**, остаются **561**: 559 без классификации
и две с незавершённым разбором (`base_finder._search` и `_update_width`).
Все девять timeout разобраны ранее.

- R21: каждый из восьми исторических diff отдельно применён во временной
  копии `src/`, `tests/`, `pyproject.toml`, `setup.cfg`, `.coveragerc`,
  с версией test_xlsxwriter_adapter.py из `5309d17`.
  База: **259 passed**; 3 killed, 5 survived.
- R22: тот же набор с проверкой полного сообщения ошибок драйвера.
  База: **259 passed**; 5 killed, 3 survived. Для killed зафиксированы
  конкретные провалы тестов, перечисленных в индивидуальных записях.

Перед каждой заменой проверено единственное точное вхождение удаляемого
блока вместе с полным контекстом; после запуска исходный файл восстановлен.
Команда R21/R22 (repo — корень репозитория, copy — временная копия):
`PYTHONPATH="$copy/src" PYTHONDONTWRITEBYTECODE=1 uv run --project "$repo" python -m pytest -c "$copy/pyproject.toml" --rootdir "$copy" --no-cov -n=0 "$copy/tests/test_parsers/test_writer"`.
Номера новой генерации mutmut не использовались.

Корень двух пробелов — regex без границ в тестах диагностик XLSX-драйвера:
обрамление сообщения лишним текстом сохраняло совпадение подстроки.
Проверки ограничены полным сообщением; код приложения не менялся.
Эквивалентность расширения .JSONL установлена по повторному построению имени
в jsonl_name, а не по одному survived. Исторические статусы сохранены;
целевые прогоны не заменяют новый полный отчёт mutmut.

Все девять команд AGENTS.md завершились с exit 0: 4170 тестов, покрытие 99,46 %.

## src/app/parse_report.py

### `app.parse_report.x_dump_json__mutmut_2`

Классификация 2026-11-14: Эквивалент: json.dumps проверяет ensure_ascii по истинности; False и None выключают экранирование Unicode одинаково. Остальные аргументы и возвращаемая строка не меняются. Прогон R1 оставляет survived.

Статус: **survived**; тип: `to_none`; выбрано тестов: 51.

```diff
--- src/app/parse_report.py
+++ src/app/parse_report.py
@@ -1,3 +1,3 @@
 def dump_json(payload: Mapping[str, Any]) -> str:
     """Сериализовать отчёт в одну JSON-строку."""
-    return json.dumps(payload, ensure_ascii=False, default=str)
+    return json.dumps(payload, ensure_ascii=None, default=str)
```

### `app.parse_report.x_error_payload__mutmut_23`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R1 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 19.

```diff
--- src/app/parse_report.py
+++ src/app/parse_report.py
@@ -17,7 +17,7 @@
         'groups': {
             group: {
                 'positions': [],
-                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), 0),
+                'XXstatsXX': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), 0),
             }
             for group in groups
         },
```

### `app.parse_report.x_error_payload__mutmut_24`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R1 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 19.

```diff
--- src/app/parse_report.py
+++ src/app/parse_report.py
@@ -17,7 +17,7 @@
         'groups': {
             group: {
                 'positions': [],
-                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), 0),
+                'STATS': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), 0),
             }
             for group in groups
         },
```

### `app.parse_report.x_error_payload__mutmut_26`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R1 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 19.

```diff
--- src/app/parse_report.py
+++ src/app/parse_report.py
@@ -17,7 +17,7 @@
         'groups': {
             group: {
                 'positions': [],
-                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), 0),
+                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), None),
             }
             for group in groups
         },
```

### `app.parse_report.x_error_payload__mutmut_28`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R1 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 19.

```diff
--- src/app/parse_report.py
+++ src/app/parse_report.py
@@ -17,7 +17,7 @@
         'groups': {
             group: {
                 'positions': [],
-                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), 0),
+                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), ),
             }
             for group in groups
         },
```

### `app.parse_report.x_error_payload__mutmut_29`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R1 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 19.

```diff
--- src/app/parse_report.py
+++ src/app/parse_report.py
@@ -17,7 +17,7 @@
         'groups': {
             group: {
                 'positions': [],
-                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), 0),
+                'stats': dict.fromkeys(('XXitemsXX', 'priced_items', 'doubles', 'black_list_skips'), 0),
             }
             for group in groups
         },
```

### `app.parse_report.x_error_payload__mutmut_30`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R1 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 19.

```diff
--- src/app/parse_report.py
+++ src/app/parse_report.py
@@ -17,7 +17,7 @@
         'groups': {
             group: {
                 'positions': [],
-                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), 0),
+                'stats': dict.fromkeys(('ITEMS', 'priced_items', 'doubles', 'black_list_skips'), 0),
             }
             for group in groups
         },
```

### `app.parse_report.x_error_payload__mutmut_31`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R1 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 19.

```diff
--- src/app/parse_report.py
+++ src/app/parse_report.py
@@ -17,7 +17,7 @@
         'groups': {
             group: {
                 'positions': [],
-                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), 0),
+                'stats': dict.fromkeys(('items', 'XXpriced_itemsXX', 'doubles', 'black_list_skips'), 0),
             }
             for group in groups
         },
```

### `app.parse_report.x_error_payload__mutmut_32`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R1 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 19.

```diff
--- src/app/parse_report.py
+++ src/app/parse_report.py
@@ -17,7 +17,7 @@
         'groups': {
             group: {
                 'positions': [],
-                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), 0),
+                'stats': dict.fromkeys(('items', 'PRICED_ITEMS', 'doubles', 'black_list_skips'), 0),
             }
             for group in groups
         },
```

### `app.parse_report.x_error_payload__mutmut_33`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R1 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 19.

```diff
--- src/app/parse_report.py
+++ src/app/parse_report.py
@@ -17,7 +17,7 @@
         'groups': {
             group: {
                 'positions': [],
-                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), 0),
+                'stats': dict.fromkeys(('items', 'priced_items', 'XXdoublesXX', 'black_list_skips'), 0),
             }
             for group in groups
         },
```

### `app.parse_report.x_error_payload__mutmut_34`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R1 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 19.

```diff
--- src/app/parse_report.py
+++ src/app/parse_report.py
@@ -17,7 +17,7 @@
         'groups': {
             group: {
                 'positions': [],
-                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), 0),
+                'stats': dict.fromkeys(('items', 'priced_items', 'DOUBLES', 'black_list_skips'), 0),
             }
             for group in groups
         },
```

### `app.parse_report.x_error_payload__mutmut_35`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R1 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 19.

```diff
--- src/app/parse_report.py
+++ src/app/parse_report.py
@@ -17,7 +17,7 @@
         'groups': {
             group: {
                 'positions': [],
-                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), 0),
+                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'XXblack_list_skipsXX'), 0),
             }
             for group in groups
         },
```

### `app.parse_report.x_error_payload__mutmut_36`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R1 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 19.

```diff
--- src/app/parse_report.py
+++ src/app/parse_report.py
@@ -17,7 +17,7 @@
         'groups': {
             group: {
                 'positions': [],
-                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), 0),
+                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'BLACK_LIST_SKIPS'), 0),
             }
             for group in groups
         },
```

### `app.parse_report.x_error_payload__mutmut_37`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R1 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `number`; выбрано тестов: 19.

```diff
--- src/app/parse_report.py
+++ src/app/parse_report.py
@@ -17,7 +17,7 @@
         'groups': {
             group: {
                 'positions': [],
-                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), 0),
+                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), 1),
             }
             for group in groups
         },
```

## src/app/parse_report_build.py

### `app.parse_report_build.x_stats_from_result__mutmut_18`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff применён отдельно к исходному файлу в временной копии рабочего дерева поверх `8abf3ba`. Прогон R12 подтвердил killed после усиления тестов этого блока. Падающие проверки: `test_result_elapsed_rounds_to_hundredths`. Исходный код проходит тот же набор. Это прямой запуск исторического изменения, без переноса результата по номеру текущего mutmut; исторический survived сохранён.

Статус: **survived**; тип: `number`; выбрано тестов: 18.

```diff
--- src/app/parse_report_build.py
+++ src/app/parse_report_build.py
@@ -7,5 +7,5 @@
         'doubles': totals.doubles,
         'black_list_skips': totals.black_list_skips,
         'unrouted_rows': parse_result.unrouted_rows,
-        'elapsed_seconds': round(elapsed, 2),
+        'elapsed_seconds': round(elapsed, 3),
     }
```

## src/app/parse_report_groups.py

### `app.parse_report_groups.x_groups_from_result__mutmut_22`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff применён отдельно к исходному файлу в временной копии рабочего дерева поверх `8abf3ba`. Прогон R12 подтвердил killed на существующих тестах. Падающие проверки: `test_report_rows_limit_only_tire_positions`. Исходный код проходит тот же набор. Это прямой запуск исторического изменения, без переноса результата по номеру текущего mutmut; исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 20.

```diff
--- src/app/parse_report_groups.py
+++ src/app/parse_report_groups.py
@@ -14,7 +14,7 @@
         if group is ProductGroup.TIRE_AND_DISK:
             stats.update(_tire_statistics(parsed))
         groups[group.value] = {
-            'positions': _report_positions(selected, all_result, rows is not None),
+            'positions': _report_positions(selected, all_result, None),
             'stats': stats,
         }
     return groups
```

## src/app/run.py

### `app.run.x__update_api_sources__mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R1 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 3.

```diff
--- src/app/run.py
+++ src/app/run.py
@@ -4,7 +4,7 @@
     failed: list[str] = []
     for folder, update in (
         ('zapaska', run_upload_zapaska_data),
-        ('four_tochki', run_upload_four_tochki_data),
+        ('XXfour_tochkiXX', run_upload_four_tochki_data),
         ('mim', run_upload_mim_data),
     ):
         outcome = _try_api_update(update)
```

### `app.run.x__update_api_sources__mutmut_6`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R1 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 3.

```diff
--- src/app/run.py
+++ src/app/run.py
@@ -4,7 +4,7 @@
     failed: list[str] = []
     for folder, update in (
         ('zapaska', run_upload_zapaska_data),
-        ('four_tochki', run_upload_four_tochki_data),
+        ('FOUR_TOCHKI', run_upload_four_tochki_data),
         ('mim', run_upload_mim_data),
     ):
         outcome = _try_api_update(update)
```

### `app.run.x_run_update_all_supplier_prices__mutmut_14`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R1 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 3.

```diff
--- src/app/run.py
+++ src/app/run.py
@@ -11,5 +11,5 @@
             failed.append(run_fetch_mail_prices.__name__)
     _log_prices_received('по API', uploaded)
     if failed:
-        names = ', '.join(failed)
+        names = 'XX, XX'.join(failed)
         raise CoreExceptionError(f'Не обновлены источники прайсов: {names}')
```

## src/app/run_dialog/help_format.py

### `app.run_dialog.help_format.x_colorize_markdown__mutmut_2`

Классификация 2026-11-14: Эквивалент: до первого fence False и None одинаково ложны; после первого `not in_code` оба превращаются в True и далее имеют одинаковую историю. Повторный прогон `uv run mutmut run 'app.run_dialog.navigation.*' 'app.run_dialog.help_format.*'` оставляет survived.

Статус: **survived**; тип: `to_none`; выбрано тестов: 7.

```diff
--- src/app/run_dialog/help_format.py
+++ src/app/run_dialog/help_format.py
@@ -1,7 +1,7 @@
 def colorize_markdown(text: str) -> str:
     """Раскрасить markdown ANSI-кодами: заголовки, блоки кода, жирный, ссылки."""
     lines: list[str] = []
-    in_code = False
+    in_code = None
     for line in text.splitlines():
         if _FENCE.match(line):
             in_code = not in_code
```

## src/app/run_dialog/items.py

### `app.run_dialog.items.x__assign_keys__mutmut_1`

Классификация 2026-11-14: Пробел теста закрыт: повторный вызов `_assign_keys` в `test_assigned_keys_reserve_activation_before_help` проверяет весь словарь и клавишу активации. Убит прогоном `uv run mutmut run 'app.run_dialog.items.*'`.

Статус: **survived**; тип: `to_none`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -1,6 +1,6 @@
 def _assign_keys() -> tuple[dict[AnswerResult, str], str]:
     """Номера по порядку расположения; активация поставщиков стоит перед справкой и получает свой номер."""
-    keys: dict[AnswerResult, str] = {}
+    keys: dict[AnswerResult, str] = None
     number = 0
     activation_key = ''
     for menu_item in MENU_ITEMS:
```

### `app.run_dialog.items.x__assign_keys__mutmut_2`

Классификация 2026-11-14: Пробел теста закрыт: повторный вызов `_assign_keys` в `test_assigned_keys_reserve_activation_before_help` проверяет весь словарь и клавишу активации. Убит прогоном `uv run mutmut run 'app.run_dialog.items.*'`.

Статус: **survived**; тип: `to_none`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -1,7 +1,7 @@
 def _assign_keys() -> tuple[dict[AnswerResult, str], str]:
     """Номера по порядку расположения; активация поставщиков стоит перед справкой и получает свой номер."""
     keys: dict[AnswerResult, str] = {}
-    number = 0
+    number = None
     activation_key = ''
     for menu_item in MENU_ITEMS:
         if menu_item.action is AnswerResult.SHOW_HELP:
```

### `app.run_dialog.items.x__assign_keys__mutmut_3`

Классификация 2026-11-14: Пробел теста закрыт: повторный вызов `_assign_keys` в `test_assigned_keys_reserve_activation_before_help` проверяет весь словарь и клавишу активации. Убит прогоном `uv run mutmut run 'app.run_dialog.items.*'`.

Статус: **survived**; тип: `number`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -1,7 +1,7 @@
 def _assign_keys() -> tuple[dict[AnswerResult, str], str]:
     """Номера по порядку расположения; активация поставщиков стоит перед справкой и получает свой номер."""
     keys: dict[AnswerResult, str] = {}
-    number = 0
+    number = 1
     activation_key = ''
     for menu_item in MENU_ITEMS:
         if menu_item.action is AnswerResult.SHOW_HELP:
```

### `app.run_dialog.items.x__assign_keys__mutmut_4`

Классификация 2026-11-14: Эквивалент при текущем `MENU_ITEMS`: начальное значение `activation_key` перезаписывается при обязательном пункте SHOW_HELP до возврата. Повторный прогон оставляет survived.

Статус: **survived**; тип: `to_none`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -2,7 +2,7 @@
     """Номера по порядку расположения; активация поставщиков стоит перед справкой и получает свой номер."""
     keys: dict[AnswerResult, str] = {}
     number = 0
-    activation_key = ''
+    activation_key = None
     for menu_item in MENU_ITEMS:
         if menu_item.action is AnswerResult.SHOW_HELP:
             number += 1
```

### `app.run_dialog.items.x__assign_keys__mutmut_5`

Классификация 2026-11-14: Эквивалент при текущем `MENU_ITEMS`: начальное значение `activation_key` перезаписывается при обязательном пункте SHOW_HELP до возврата. Повторный прогон оставляет survived.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -2,7 +2,7 @@
     """Номера по порядку расположения; активация поставщиков стоит перед справкой и получает свой номер."""
     keys: dict[AnswerResult, str] = {}
     number = 0
-    activation_key = ''
+    activation_key = 'XXXX'
     for menu_item in MENU_ITEMS:
         if menu_item.action is AnswerResult.SHOW_HELP:
             number += 1
```

### `app.run_dialog.items.x__assign_keys__mutmut_6`

Классификация 2026-11-14: Пробел теста закрыт: повторный вызов `_assign_keys` в `test_assigned_keys_reserve_activation_before_help` проверяет весь словарь и клавишу активации. Убит прогоном `uv run mutmut run 'app.run_dialog.items.*'`.

Статус: **survived**; тип: `operator`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -4,7 +4,7 @@
     number = 0
     activation_key = ''
     for menu_item in MENU_ITEMS:
-        if menu_item.action is AnswerResult.SHOW_HELP:
+        if menu_item.action is not AnswerResult.SHOW_HELP:
             number += 1
             activation_key = str(number)
         if menu_item.action is AnswerResult.EXIT:
```

### `app.run_dialog.items.x__assign_keys__mutmut_7`

Классификация 2026-11-14: Пробел теста закрыт: повторный вызов `_assign_keys` в `test_assigned_keys_reserve_activation_before_help` проверяет весь словарь и клавишу активации. Убит прогоном `uv run mutmut run 'app.run_dialog.items.*'`.

Статус: **survived**; тип: `operator`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -5,7 +5,7 @@
     activation_key = ''
     for menu_item in MENU_ITEMS:
         if menu_item.action is AnswerResult.SHOW_HELP:
-            number += 1
+            number = 1
             activation_key = str(number)
         if menu_item.action is AnswerResult.EXIT:
             keys[menu_item.action] = EXIT_KEY
```

### `app.run_dialog.items.x__assign_keys__mutmut_8`

Классификация 2026-11-14: Пробел теста закрыт: повторный вызов `_assign_keys` в `test_assigned_keys_reserve_activation_before_help` проверяет весь словарь и клавишу активации. Убит прогоном `uv run mutmut run 'app.run_dialog.items.*'`.

Статус: **survived**; тип: `operator`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -5,7 +5,7 @@
     activation_key = ''
     for menu_item in MENU_ITEMS:
         if menu_item.action is AnswerResult.SHOW_HELP:
-            number += 1
+            number -= 1
             activation_key = str(number)
         if menu_item.action is AnswerResult.EXIT:
             keys[menu_item.action] = EXIT_KEY
```

### `app.run_dialog.items.x__assign_keys__mutmut_9`

Классификация 2026-11-14: Пробел теста закрыт: повторный вызов `_assign_keys` в `test_assigned_keys_reserve_activation_before_help` проверяет весь словарь и клавишу активации. Убит прогоном `uv run mutmut run 'app.run_dialog.items.*'`.

Статус: **survived**; тип: `number`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -5,7 +5,7 @@
     activation_key = ''
     for menu_item in MENU_ITEMS:
         if menu_item.action is AnswerResult.SHOW_HELP:
-            number += 1
+            number += 2
             activation_key = str(number)
         if menu_item.action is AnswerResult.EXIT:
             keys[menu_item.action] = EXIT_KEY
```

### `app.run_dialog.items.x__assign_keys__mutmut_10`

Классификация 2026-11-14: Пробел теста закрыт: повторный вызов `_assign_keys` в `test_assigned_keys_reserve_activation_before_help` проверяет весь словарь и клавишу активации. Убит прогоном `uv run mutmut run 'app.run_dialog.items.*'`.

Статус: **survived**; тип: `to_none`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -6,7 +6,7 @@
     for menu_item in MENU_ITEMS:
         if menu_item.action is AnswerResult.SHOW_HELP:
             number += 1
-            activation_key = str(number)
+            activation_key = None
         if menu_item.action is AnswerResult.EXIT:
             keys[menu_item.action] = EXIT_KEY
             continue
```

### `app.run_dialog.items.x__assign_keys__mutmut_11`

Классификация 2026-11-14: Пробел теста закрыт: повторный вызов `_assign_keys` в `test_assigned_keys_reserve_activation_before_help` проверяет весь словарь и клавишу активации. Убит прогоном `uv run mutmut run 'app.run_dialog.items.*'`.

Статус: **survived**; тип: `to_none`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -6,7 +6,7 @@
     for menu_item in MENU_ITEMS:
         if menu_item.action is AnswerResult.SHOW_HELP:
             number += 1
-            activation_key = str(number)
+            activation_key = str(None)
         if menu_item.action is AnswerResult.EXIT:
             keys[menu_item.action] = EXIT_KEY
             continue
```

### `app.run_dialog.items.x__assign_keys__mutmut_12`

Классификация 2026-11-14: Пробел теста закрыт: повторный вызов `_assign_keys` в `test_assigned_keys_reserve_activation_before_help` проверяет весь словарь и клавишу активации. Убит прогоном `uv run mutmut run 'app.run_dialog.items.*'`.

Статус: **survived**; тип: `operator`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -7,7 +7,7 @@
         if menu_item.action is AnswerResult.SHOW_HELP:
             number += 1
             activation_key = str(number)
-        if menu_item.action is AnswerResult.EXIT:
+        if menu_item.action is not AnswerResult.EXIT:
             keys[menu_item.action] = EXIT_KEY
             continue
         number += 1
```

### `app.run_dialog.items.x__assign_keys__mutmut_13`

Классификация 2026-11-14: Пробел теста закрыт: повторный вызов `_assign_keys` в `test_assigned_keys_reserve_activation_before_help` проверяет весь словарь и клавишу активации. Убит прогоном `uv run mutmut run 'app.run_dialog.items.*'`.

Статус: **survived**; тип: `to_none`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -8,7 +8,7 @@
             number += 1
             activation_key = str(number)
         if menu_item.action is AnswerResult.EXIT:
-            keys[menu_item.action] = EXIT_KEY
+            keys[menu_item.action] = None
             continue
         number += 1
         keys[menu_item.action] = str(number)
```

### `app.run_dialog.items.x__assign_keys__mutmut_14`

Классификация 2026-11-14: Эквивалент при текущем `MENU_ITEMS`: EXIT — последний пункт; `continue` и `break` завершают обход с одинаковыми ключами и activation_key. Повторный прогон оставляет survived.

Статус: **survived**; тип: `keyword`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -9,7 +9,7 @@
             activation_key = str(number)
         if menu_item.action is AnswerResult.EXIT:
             keys[menu_item.action] = EXIT_KEY
-            continue
+            break
         number += 1
         keys[menu_item.action] = str(number)
     return keys, activation_key
```

### `app.run_dialog.items.x__assign_keys__mutmut_15`

Классификация 2026-11-14: Пробел теста закрыт: повторный вызов `_assign_keys` в `test_assigned_keys_reserve_activation_before_help` проверяет весь словарь и клавишу активации. Убит прогоном `uv run mutmut run 'app.run_dialog.items.*'`.

Статус: **survived**; тип: `operator`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -10,6 +10,6 @@
         if menu_item.action is AnswerResult.EXIT:
             keys[menu_item.action] = EXIT_KEY
             continue
-        number += 1
+        number = 1
         keys[menu_item.action] = str(number)
     return keys, activation_key
```

### `app.run_dialog.items.x__assign_keys__mutmut_16`

Классификация 2026-11-14: Пробел теста закрыт: повторный вызов `_assign_keys` в `test_assigned_keys_reserve_activation_before_help` проверяет весь словарь и клавишу активации. Убит прогоном `uv run mutmut run 'app.run_dialog.items.*'`.

Статус: **survived**; тип: `operator`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -10,6 +10,6 @@
         if menu_item.action is AnswerResult.EXIT:
             keys[menu_item.action] = EXIT_KEY
             continue
-        number += 1
+        number -= 1
         keys[menu_item.action] = str(number)
     return keys, activation_key
```

### `app.run_dialog.items.x__assign_keys__mutmut_17`

Классификация 2026-11-14: Пробел теста закрыт: повторный вызов `_assign_keys` в `test_assigned_keys_reserve_activation_before_help` проверяет весь словарь и клавишу активации. Убит прогоном `uv run mutmut run 'app.run_dialog.items.*'`.

Статус: **survived**; тип: `number`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -10,6 +10,6 @@
         if menu_item.action is AnswerResult.EXIT:
             keys[menu_item.action] = EXIT_KEY
             continue
-        number += 1
+        number += 2
         keys[menu_item.action] = str(number)
     return keys, activation_key
```

### `app.run_dialog.items.x__assign_keys__mutmut_18`

Классификация 2026-11-14: Пробел теста закрыт: повторный вызов `_assign_keys` в `test_assigned_keys_reserve_activation_before_help` проверяет весь словарь и клавишу активации. Убит прогоном `uv run mutmut run 'app.run_dialog.items.*'`.

Статус: **survived**; тип: `to_none`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -11,5 +11,5 @@
             keys[menu_item.action] = EXIT_KEY
             continue
         number += 1
-        keys[menu_item.action] = str(number)
+        keys[menu_item.action] = None
     return keys, activation_key
```

### `app.run_dialog.items.x__assign_keys__mutmut_19`

Классификация 2026-11-14: Пробел теста закрыт: повторный вызов `_assign_keys` в `test_assigned_keys_reserve_activation_before_help` проверяет весь словарь и клавишу активации. Убит прогоном `uv run mutmut run 'app.run_dialog.items.*'`.

Статус: **survived**; тип: `to_none`; выбрано тестов: 1.

```diff
--- src/app/run_dialog/items.py
+++ src/app/run_dialog/items.py
@@ -11,5 +11,5 @@
             keys[menu_item.action] = EXIT_KEY
             continue
         number += 1
-        keys[menu_item.action] = str(number)
+        keys[menu_item.action] = str(None)
     return keys, activation_key
```

## src/app/run_dialog/line_fallback.py

### `app.run_dialog.line_fallback.x_ask_by_line__mutmut_3`

Классификация 2026-11-14: таймаут подтверждён прогоном `uv run mutmut run 'app.run_dialog.line_fallback.*'` с ограничением mutmut. Мутант удаляет `input` и всегда получает answer=None, поэтому цикл не читает ввод и не достигает return. Исходная функция по-прежнему завершается при корректном действии; дефекта приложения нет.

Статус: **timeout**; тип: `to_none`; выбрано тестов: 8.

```diff
--- src/app/run_dialog/line_fallback.py
+++ src/app/run_dialog/line_fallback.py
@@ -2,7 +2,7 @@
     """Спросить действие цифрой/буквой, повторяя запрос при неверном вводе."""
     prompt = _menu_text()
     while True:
-        answer = ANSWER_MAP.get(input(prompt).strip().lower())
+        answer = None
         if answer:
             return answer
         logger.info('Не понял, давай ещё раз. \n')
```

### `app.run_dialog.line_fallback.x_ask_by_line__mutmut_4`

Классификация 2026-11-14: таймаут подтверждён прогоном `uv run mutmut run 'app.run_dialog.line_fallback.*'` с ограничением mutmut. Мутант удаляет `input` и всегда получает answer=None, поэтому цикл не читает ввод и не достигает return. Исходная функция по-прежнему завершается при корректном действии; дефекта приложения нет.

Статус: **timeout**; тип: `other`; выбрано тестов: 8.

```diff
--- src/app/run_dialog/line_fallback.py
+++ src/app/run_dialog/line_fallback.py
@@ -2,7 +2,7 @@
     """Спросить действие цифрой/буквой, повторяя запрос при неверном вводе."""
     prompt = _menu_text()
     while True:
-        answer = ANSWER_MAP.get(input(prompt).strip().lower())
+        answer = ANSWER_MAP.get(None)
         if answer:
             return answer
         logger.info('Не понял, давай ещё раз. \n')
```

## src/app/run_dialog/navigation.py

### `app.run_dialog.navigation.x__handle_press__mutmut_5`

Классификация 2026-11-14: Эквивалент: `get` вызывается только внутри `if press.key in _STEPS`, поэтому значение по умолчанию никогда не используется. Повторный прогон `uv run mutmut run 'app.run_dialog.navigation.*' 'app.run_dialog.help_format.*'` оставляет survived.

Статус: **survived**; тип: `to_none`; выбрано тестов: 16.

```diff
--- src/app/run_dialog/navigation.py
+++ src/app/run_dialog/navigation.py
@@ -3,7 +3,7 @@
     if press.key is Key.EXIT:
         return AnswerResult.EXIT
     if press.key in _STEPS:
-        step = _STEPS.get(press.key, 0)
+        step = _STEPS.get(press.key, None)
         view.active = (view.active + step) % len(view.rows)
     elif press.key is Key.ENTER:
         return _commit(view)
```

### `app.run_dialog.navigation.x__handle_press__mutmut_7`

Классификация 2026-11-14: Эквивалент: `get` вызывается только внутри `if press.key in _STEPS`, поэтому значение по умолчанию никогда не используется. Повторный прогон `uv run mutmut run 'app.run_dialog.navigation.*' 'app.run_dialog.help_format.*'` оставляет survived.

Статус: **survived**; тип: `other`; выбрано тестов: 16.

```diff
--- src/app/run_dialog/navigation.py
+++ src/app/run_dialog/navigation.py
@@ -3,7 +3,7 @@
     if press.key is Key.EXIT:
         return AnswerResult.EXIT
     if press.key in _STEPS:
-        step = _STEPS.get(press.key, 0)
+        step = _STEPS.get(press.key, )
         view.active = (view.active + step) % len(view.rows)
     elif press.key is Key.ENTER:
         return _commit(view)
```

### `app.run_dialog.navigation.x__handle_press__mutmut_8`

Классификация 2026-11-14: Эквивалент: `get` вызывается только внутри `if press.key in _STEPS`, поэтому значение по умолчанию никогда не используется. Повторный прогон `uv run mutmut run 'app.run_dialog.navigation.*' 'app.run_dialog.help_format.*'` оставляет survived.

Статус: **survived**; тип: `number`; выбрано тестов: 16.

```diff
--- src/app/run_dialog/navigation.py
+++ src/app/run_dialog/navigation.py
@@ -3,7 +3,7 @@
     if press.key is Key.EXIT:
         return AnswerResult.EXIT
     if press.key in _STEPS:
-        step = _STEPS.get(press.key, 0)
+        step = _STEPS.get(press.key, 1)
         view.active = (view.active + step) % len(view.rows)
     elif press.key is Key.ENTER:
         return _commit(view)
```

### `app.run_dialog.navigation.x_navigate__mutmut_2`

Классификация 2026-11-14: Таймаут мутанта подтверждён отдельным прогоном navigation/help_format с ограничением mutmut: присваивание `action = None` удаляет чтение клавиши и делает условие выхода постоянно ложным. Это зацикливание мутанта, а не исходного приложения.

Статус: **timeout**; тип: `to_none`; выбрано тестов: 16.

```diff
--- src/app/run_dialog/navigation.py
+++ src/app/run_dialog/navigation.py
@@ -1,7 +1,7 @@
 def navigate(view: MenuView) -> AnswerResult:
     """Крутить ввод, пока не выбрано действие или выход."""
     while True:
-        action = _handle_press(view, read_key())
+        action = None
         if action is not None:
             view.finish()
             return action
```

## src/app/run_machine.py

### `app.run_machine.x__emit_command__mutmut_30`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff применён отдельно к исходному файлу в временной копии рабочего дерева поверх `8abf3ba`. Прогон R12 подтвердил killed после усиления тестов этого блока. Падающие проверки: `test_known_selection_on_failure[KeyboardInterrupt-False]`; `test_known_selection_on_failure[KeyboardInterrupt-True]`; `test_doubles_failure_preserves_returned_groups`. Исходный код проходит тот же набор. Это прямой запуск исторического изменения, без переноса результата по номеру текущего mutmut; исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 40.

```diff
--- src/app/run_machine.py
+++ src/app/run_machine.py
@@ -15,8 +15,7 @@
                 'KeyboardInterrupt',
                 _INTERRUPT,
                 compact=command in _COMPACT_ERROR_COMMANDS,
-                groups=tuple(group.value for group in selection.groups),
-            ),
+                ),
             started=started,
         )
         return 1
```

### `app.run_machine.x__emit_command__mutmut_38`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff применён отдельно к исходному файлу в временной копии рабочего дерева поверх `8abf3ba`. Прогон R12 подтвердил killed после усиления тестов этого блока. Падающие проверки: `test_json_error_outside_orchestrator_gets_traceback_in_log`. Исходный код проходит тот же набор. Это прямой запуск исторического изменения, без переноса результата по номеру текущего mutmut; исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 40.

```diff
--- src/app/run_machine.py
+++ src/app/run_machine.py
@@ -21,7 +21,7 @@
         )
         return 1
     except Exception as exc:
-        log_exception_once(logger, f'Команда {command} завершилась ошибкой // {exc}', exc)
+        log_exception_once(logger, None, exc)
         emit_json(
             error_payload(
                 command,
```

### `app.run_machine.x__json_doubles__mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff применён отдельно к исходному файлу в временной копии рабочего дерева поверх `8abf3ba`. Прогон R12 подтвердил killed на существующих тестах. Падающие проверки: `test_json_doubles`; `test_doubles_failure_preserves_returned_groups`. Исходный код проходит тот же набор. Это прямой запуск исторического изменения, без переноса результата по номеру текущего mutmut; исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 3.

```diff
--- src/app/run_machine.py
+++ src/app/run_machine.py
@@ -1,6 +1,6 @@
 def _json_doubles(all_result: bool, _result_template: str | None, selection: ParseSelection) -> JsonReport:
     started = time.monotonic()
-    report = ServiceProvider.resolve(doubles_service.DoublesService).make_report(as_jsonl=True, selection=selection)
+    report = ServiceProvider.resolve(doubles_service.DoublesService).make_report(as_jsonl=True, selection=None)
     selection.groups = tuple(report.parse_result.groups)
     return report_from_result(
         DOUBLES,
```

### `app.run_machine.x__json_doubles__mutmut_6`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff применён отдельно к исходному файлу в временной копии рабочего дерева поверх `8abf3ba`. Прогон R12 подтвердил killed на существующих тестах. Падающие проверки: `test_json_doubles`; `test_doubles_failure_preserves_returned_groups`. Исходный код проходит тот же набор. Это прямой запуск исторического изменения, без переноса результата по номеру текущего mutmut; исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/app/run_machine.py
+++ src/app/run_machine.py
@@ -1,6 +1,6 @@
 def _json_doubles(all_result: bool, _result_template: str | None, selection: ParseSelection) -> JsonReport:
     started = time.monotonic()
-    report = ServiceProvider.resolve(doubles_service.DoublesService).make_report(as_jsonl=True, selection=selection)
+    report = ServiceProvider.resolve(doubles_service.DoublesService).make_report(as_jsonl=True, )
     selection.groups = tuple(report.parse_result.groups)
     return report_from_result(
         DOUBLES,
```

### `app.run_machine.x__json_doubles__mutmut_9`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff применён отдельно к исходному файлу в временной копии рабочего дерева поверх `8abf3ba`. Прогон R12 подтвердил killed на существующих тестах. Падающие проверки: `test_json_doubles`; `test_doubles_failure_preserves_returned_groups`. Исходный код проходит тот же набор. Это прямой запуск исторического изменения, без переноса результата по номеру текущего mutmut; исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 3.

```diff
--- src/app/run_machine.py
+++ src/app/run_machine.py
@@ -1,7 +1,7 @@
 def _json_doubles(all_result: bool, _result_template: str | None, selection: ParseSelection) -> JsonReport:
     started = time.monotonic()
     report = ServiceProvider.resolve(doubles_service.DoublesService).make_report(as_jsonl=True, selection=selection)
-    selection.groups = tuple(report.parse_result.groups)
+    selection.groups = None
     return report_from_result(
         DOUBLES,
         report.parse_result,
```

### `app.run_machine.x__json_load_prices__mutmut_6`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff применён отдельно к исходному файлу в временной копии рабочего дерева поверх `8abf3ba`. Прогон R12 подтвердил killed на существующих тестах. Падающие проверки: `test_json_load_supplier_prices`. Исходный код проходит тот же набор. Это прямой запуск исторического изменения, без переноса результата по номеру текущего mutmut; исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 4.

```diff
--- src/app/run_machine.py
+++ src/app/run_machine.py
@@ -1,6 +1,6 @@
 def _json_load_prices(raw: str | None) -> dict[str, object]:
     mapping = parse_prices_json(raw or '')
-    catalog = all_vendor_supplier_catalog(get_config_provider())
+    catalog = all_vendor_supplier_catalog(None)
     return {
         'ok': True,
         'action': LOAD_SUPPLIER_PRICES,
```

### `app.run_machine.x__json_update_all__mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff применён отдельно к исходному файлу в временной копии рабочего дерева поверх `8abf3ba`. Прогон R12 подтвердил killed на существующих тестах. Падающие проверки: `test_json_update_all_errors_use_canonical_source_names`. Исходный код проходит тот же набор. Это прямой запуск исторического изменения, без переноса результата по номеру текущего mutmut; исторический survived сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 3.

```diff
--- src/app/run_machine.py
+++ src/app/run_machine.py
@@ -4,7 +4,7 @@
     with ServiceProvider.resolve(PriceSchemaService).guard():
         for source, update in (
             ('zapaska', _upload_zapaska),
-            ('four_tochki', upload_four_tochki_data),
+            ('XXfour_tochkiXX', upload_four_tochki_data),
             ('mim', _upload_mim),
         ):
             _collect_error(errors, source, update)
```

### `app.run_machine.x__json_update_all__mutmut_6`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff применён отдельно к исходному файлу в временной копии рабочего дерева поверх `8abf3ba`. Прогон R12 подтвердил killed на существующих тестах. Падающие проверки: `test_json_update_all_errors_use_canonical_source_names`. Исходный код проходит тот же набор. Это прямой запуск исторического изменения, без переноса результата по номеру текущего mutmut; исторический survived сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 3.

```diff
--- src/app/run_machine.py
+++ src/app/run_machine.py
@@ -4,7 +4,7 @@
     with ServiceProvider.resolve(PriceSchemaService).guard():
         for source, update in (
             ('zapaska', _upload_zapaska),
-            ('four_tochki', upload_four_tochki_data),
+            ('FOUR_TOCHKI', upload_four_tochki_data),
             ('mim', _upload_mim),
         ):
             _collect_error(errors, source, update)
```

### `app.run_machine.x__json_update_all__mutmut_7`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff применён отдельно к исходному файлу в временной копии рабочего дерева поверх `8abf3ba`. Прогон R12 подтвердил killed на существующих тестах. Падающие проверки: `test_json_update_all_errors_use_canonical_source_names`. Исходный код проходит тот же набор. Это прямой запуск исторического изменения, без переноса результата по номеру текущего mutmut; исторический survived сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 3.

```diff
--- src/app/run_machine.py
+++ src/app/run_machine.py
@@ -5,7 +5,7 @@
         for source, update in (
             ('zapaska', _upload_zapaska),
             ('four_tochki', upload_four_tochki_data),
-            ('mim', _upload_mim),
+            ('XXmimXX', _upload_mim),
         ):
             _collect_error(errors, source, update)
         files = _collect_mail(errors)
```

### `app.run_machine.x__json_update_all__mutmut_8`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff применён отдельно к исходному файлу в временной копии рабочего дерева поверх `8abf3ba`. Прогон R12 подтвердил killed на существующих тестах. Падающие проверки: `test_json_update_all_errors_use_canonical_source_names`. Исходный код проходит тот же набор. Это прямой запуск исторического изменения, без переноса результата по номеру текущего mutmut; исторический survived сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 3.

```diff
--- src/app/run_machine.py
+++ src/app/run_machine.py
@@ -5,7 +5,7 @@
         for source, update in (
             ('zapaska', _upload_zapaska),
             ('four_tochki', upload_four_tochki_data),
-            ('mim', _upload_mim),
+            ('MIM', _upload_mim),
         ):
             _collect_error(errors, source, update)
         files = _collect_mail(errors)
```

### `app.run_machine.x__reference_payload__mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff применён отдельно к исходному файлу в временной копии рабочего дерева поверх `8abf3ba`. Прогон R12 подтвердил killed на существующих тестах. Падающие проверки: `test_json_get_supliers`. Исходный код проходит тот же набор. Это прямой запуск исторического изменения, без переноса результата по номеру текущего mutmut; исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 40.

```diff
--- src/app/run_machine.py
+++ src/app/run_machine.py
@@ -1,7 +1,7 @@
 def _reference_payload(command: str, payload_arg: str | None) -> Mapping[str, Any] | None:
     """Справочные команды: каталог поставщиков, типы товара и активность поставщиков; None — команда не справочная."""
     if command == GET_SUPLIERS:
-        return all_vendor_supplier_catalog(get_config_provider())
+        return all_vendor_supplier_catalog(None)
     if command == GET_PRODUCT_TYPES:
         return {_JSON_OK: True, _JSON_ACTION: GET_PRODUCT_TYPES, 'types': list(CANONICAL_TYPES)}
     if command == GET_VENDORS:
```

## src/cfg/vendor_parser.py

### `cfg.vendor_parser.x_parser_for_vendor__mutmut_4`

Статус: **survived**; тип: `to_none`; выбрано тестов: 1.

```diff
--- src/cfg/vendor_parser.py
+++ src/cfg/vendor_parser.py
@@ -3,4 +3,4 @@
     if vendor_config is not None and isinstance(vendor_config.vendor_section, BatterySection):
         section = vendor_config.vendor_section
         return BatteryParser(vendor_config, make_battery_handler(section, section.name))
-    return tire_parser_for_vendor(vendor_cls, vendor_config)
+    return tire_parser_for_vendor(vendor_cls, None)
```

## src/domain/battery/case.py

### `domain.battery.case.xǁBatteryCaseǁ__post_init____mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 216.

```diff
--- src/domain/battery/case.py
+++ src/domain/battery/case.py
@@ -1,5 +1,5 @@
     def __post_init__(self) -> None:
-        check_number(self.length_mm, 'length_mm')
+        check_number(self.length_mm, 'XXlength_mmXX')
         check_number(self.width_mm, 'width_mm')
         check_number(self.height_mm, 'height_mm')
         check_number(self.weight, 'weight')
```

### `domain.battery.case.xǁBatteryCaseǁ__post_init____mutmut_11`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 216.

```diff
--- src/domain/battery/case.py
+++ src/domain/battery/case.py
@@ -1,6 +1,6 @@
     def __post_init__(self) -> None:
         check_number(self.length_mm, 'length_mm')
-        check_number(self.width_mm, 'width_mm')
+        check_number(self.width_mm, 'XXwidth_mmXX')
         check_number(self.height_mm, 'height_mm')
         check_number(self.weight, 'weight')
         check_flag(self.serviceable, 'serviceable')
```

### `domain.battery.case.xǁBatteryCaseǁ__post_init____mutmut_17`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 216.

```diff
--- src/domain/battery/case.py
+++ src/domain/battery/case.py
@@ -1,6 +1,6 @@
     def __post_init__(self) -> None:
         check_number(self.length_mm, 'length_mm')
         check_number(self.width_mm, 'width_mm')
-        check_number(self.height_mm, 'height_mm')
+        check_number(self.height_mm, 'XXheight_mmXX')
         check_number(self.weight, 'weight')
         check_flag(self.serviceable, 'serviceable')
```

### `domain.battery.case.xǁBatteryCaseǁ__post_init____mutmut_23`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 216.

```diff
--- src/domain/battery/case.py
+++ src/domain/battery/case.py
@@ -2,5 +2,5 @@
         check_number(self.length_mm, 'length_mm')
         check_number(self.width_mm, 'width_mm')
         check_number(self.height_mm, 'height_mm')
-        check_number(self.weight, 'weight')
+        check_number(self.weight, 'XXweightXX')
         check_flag(self.serviceable, 'serviceable')
```

### `domain.battery.case.xǁBatteryCaseǁ__post_init____mutmut_29`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 216.

```diff
--- src/domain/battery/case.py
+++ src/domain/battery/case.py
@@ -3,4 +3,4 @@
         check_number(self.width_mm, 'width_mm')
         check_number(self.height_mm, 'height_mm')
         check_number(self.weight, 'weight')
-        check_flag(self.serviceable, 'serviceable')
+        check_flag(self.serviceable, 'XXserviceableXX')
```

## src/domain/battery/conversions.py

### `domain.battery.conversions.x_flag__mutmut_14`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 218.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -8,4 +8,4 @@
         normalized = raw.strip().casefold()
         if normalized in {'да', 'нет'}:
             return normalized == 'да'
-    raise ValueError('требуется да/нет или bool')
+    raise ValueError(None)
```

### `domain.battery.conversions.x_flag__mutmut_15`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 218.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -8,4 +8,4 @@
         normalized = raw.strip().casefold()
         if normalized in {'да', 'нет'}:
             return normalized == 'да'
-    raise ValueError('требуется да/нет или bool')
+    raise ValueError('XXтребуется да/нет или boolXX')
```

### `domain.battery.conversions.x_flag__mutmut_16`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 218.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -8,4 +8,4 @@
         normalized = raw.strip().casefold()
         if normalized in {'да', 'нет'}:
             return normalized == 'да'
-    raise ValueError('требуется да/нет или bool')
+    raise ValueError('ТРЕБУЕТСЯ ДА/НЕТ ИЛИ BOOL')
```

### `domain.battery.conversions.x_integer__mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 199.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -4,5 +4,5 @@
     if numeric is None:
         return None
     if numeric != numeric.to_integral_value():
-        raise ValueError('требуется целое число')
+        raise ValueError(None)
     return int(numeric)
```

### `domain.battery.conversions.x_integer__mutmut_6`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 199.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -4,5 +4,5 @@
     if numeric is None:
         return None
     if numeric != numeric.to_integral_value():
-        raise ValueError('требуется целое число')
+        raise ValueError('XXтребуется целое числоXX')
     return int(numeric)
```

### `domain.battery.conversions.x_integer__mutmut_7`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 199.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -4,5 +4,5 @@
     if numeric is None:
         return None
     if numeric != numeric.to_integral_value():
-        raise ValueError('требуется целое число')
+        raise ValueError('ТРЕБУЕТСЯ ЦЕЛОЕ ЧИСЛО')
     return int(numeric)
```

### `domain.battery.conversions.x_number__mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `operator`; выбрано тестов: 226.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -2,7 +2,7 @@
     """Прочитать десятичное число без потери точности денежных значений."""
     if raw is None or (isinstance(raw, str) and not raw.strip()):
         return None
-    if isinstance(raw, bool) or not isinstance(raw, _SCALAR_TYPES):
+    if isinstance(raw, bool) and not isinstance(raw, _SCALAR_TYPES):
         raise ValueError('требуется число')
     prepared = ''.join(str(raw).split()).replace(',', '.')
     try:
```

### `domain.battery.conversions.x_number__mutmut_7`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 226.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -3,7 +3,7 @@
     if raw is None or (isinstance(raw, str) and not raw.strip()):
         return None
     if isinstance(raw, bool) or not isinstance(raw, _SCALAR_TYPES):
-        raise ValueError('требуется число')
+        raise ValueError(None)
     prepared = ''.join(str(raw).split()).replace(',', '.')
     try:
         numeric = Decimal(prepared)
```

### `domain.battery.conversions.x_number__mutmut_8`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 226.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -3,7 +3,7 @@
     if raw is None or (isinstance(raw, str) and not raw.strip()):
         return None
     if isinstance(raw, bool) or not isinstance(raw, _SCALAR_TYPES):
-        raise ValueError('требуется число')
+        raise ValueError('XXтребуется числоXX')
     prepared = ''.join(str(raw).split()).replace(',', '.')
     try:
         numeric = Decimal(prepared)
```

### `domain.battery.conversions.x_number__mutmut_9`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 226.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -3,7 +3,7 @@
     if raw is None or (isinstance(raw, str) and not raw.strip()):
         return None
     if isinstance(raw, bool) or not isinstance(raw, _SCALAR_TYPES):
-        raise ValueError('требуется число')
+        raise ValueError('ТРЕБУЕТСЯ ЧИСЛО')
     prepared = ''.join(str(raw).split()).replace(',', '.')
     try:
         numeric = Decimal(prepared)
```

### `domain.battery.conversions.x_number__mutmut_22`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 226.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -8,7 +8,7 @@
     try:
         numeric = Decimal(prepared)
     except InvalidOperation as exc:
-        raise ValueError('требуется число') from exc
+        raise ValueError(None) from exc
     if not numeric.is_finite():
         raise ValueError('требуется конечное число')
     return numeric
```

### `domain.battery.conversions.x_number__mutmut_23`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 226.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -8,7 +8,7 @@
     try:
         numeric = Decimal(prepared)
     except InvalidOperation as exc:
-        raise ValueError('требуется число') from exc
+        raise ValueError('XXтребуется числоXX') from exc
     if not numeric.is_finite():
         raise ValueError('требуется конечное число')
     return numeric
```

### `domain.battery.conversions.x_number__mutmut_24`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 226.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -8,7 +8,7 @@
     try:
         numeric = Decimal(prepared)
     except InvalidOperation as exc:
-        raise ValueError('требуется число') from exc
+        raise ValueError('ТРЕБУЕТСЯ ЧИСЛО') from exc
     if not numeric.is_finite():
         raise ValueError('требуется конечное число')
     return numeric
```

### `domain.battery.conversions.x_number__mutmut_26`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 226.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -10,5 +10,5 @@
     except InvalidOperation as exc:
         raise ValueError('требуется число') from exc
     if not numeric.is_finite():
-        raise ValueError('требуется конечное число')
+        raise ValueError(None)
     return numeric
```

### `domain.battery.conversions.x_number__mutmut_27`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 226.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -10,5 +10,5 @@
     except InvalidOperation as exc:
         raise ValueError('требуется число') from exc
     if not numeric.is_finite():
-        raise ValueError('требуется конечное число')
+        raise ValueError('XXтребуется конечное числоXX')
     return numeric
```

### `domain.battery.conversions.x_number__mutmut_28`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 226.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -10,5 +10,5 @@
     except InvalidOperation as exc:
         raise ValueError('требуется число') from exc
     if not numeric.is_finite():
-        raise ValueError('требуется конечное число')
+        raise ValueError('ТРЕБУЕТСЯ КОНЕЧНОЕ ЧИСЛО')
     return numeric
```

### `domain.battery.conversions.x_text__mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 230.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -3,7 +3,7 @@
     if raw is None:
         return None
     if isinstance(raw, bool) or not isinstance(raw, _SCALAR_TYPES):
-        raise ValueError('требуется текст или число')
+        raise ValueError(None)
     if isinstance(raw, (float, Decimal)):
         numeric = number(raw)
         if numeric is not None and numeric == numeric.to_integral_value():
```

### `domain.battery.conversions.x_text__mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 230.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -3,7 +3,7 @@
     if raw is None:
         return None
     if isinstance(raw, bool) or not isinstance(raw, _SCALAR_TYPES):
-        raise ValueError('требуется текст или число')
+        raise ValueError('XXтребуется текст или числоXX')
     if isinstance(raw, (float, Decimal)):
         numeric = number(raw)
         if numeric is not None and numeric == numeric.to_integral_value():
```

### `domain.battery.conversions.x_text__mutmut_6`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 230.

```diff
--- src/domain/battery/conversions.py
+++ src/domain/battery/conversions.py
@@ -3,7 +3,7 @@
     if raw is None:
         return None
     if isinstance(raw, bool) or not isinstance(raw, _SCALAR_TYPES):
-        raise ValueError('требуется текст или число')
+        raise ValueError('ТРЕБУЕТСЯ ТЕКСТ ИЛИ ЧИСЛО')
     if isinstance(raw, (float, Decimal)):
         numeric = number(raw)
         if numeric is not None and numeric == numeric.to_integral_value():
```

## src/domain/battery/field_registry.py

### `domain.battery.field_registry.x_validate_fields__mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 234.

```diff
--- src/domain/battery/field_registry.py
+++ src/domain/battery/field_registry.py
@@ -2,5 +2,5 @@
     """Чужие поля не должны незаметно пропадать при создании аккумулятора."""
     unknown = fields.keys() - FIELD_CONVERTERS.keys()
     if unknown:
-        unknown_keys = ', '.join(sorted(unknown))
+        unknown_keys = 'XX, XX'.join(sorted(unknown))
         raise ValueError(f'Неизвестные поля batteries: {unknown_keys}')
```

## src/domain/battery/offer.py

### `domain.battery.offer.xǁBatteryOfferǁ__post_init____mutmut_3`

Классификация 2026-11-14: Эквивалент: для `price_opt` positive=False заменён на None. В check_number флаг используется только в `positive and numeric == 0`; оба значения ложны. Проверки конечности и отрицательного знака не меняются, ноль остаётся допустимым. Прогон R2 оставляет survived.

Статус: **survived**; тип: `to_none`; выбрано тестов: 202.

```diff
--- src/domain/battery/offer.py
+++ src/domain/battery/offer.py
@@ -1,5 +1,5 @@
     def __post_init__(self) -> None:
-        check_number(self.price_opt, 'price_opt', positive=False)
+        check_number(self.price_opt, 'price_opt', positive=None)
         check_number(self.price_recommended, 'price_recommended', positive=False)
         check_number(self.price_markup, 'price_markup', positive=False)
         check_integer(self.rest_count, 'rest_count')
```

### `domain.battery.offer.xǁBatteryOfferǁ__post_init____mutmut_7`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 202.

```diff
--- src/domain/battery/offer.py
+++ src/domain/battery/offer.py
@@ -1,5 +1,5 @@
     def __post_init__(self) -> None:
-        check_number(self.price_opt, 'price_opt', positive=False)
+        check_number(self.price_opt, 'XXprice_optXX', positive=False)
         check_number(self.price_recommended, 'price_recommended', positive=False)
         check_number(self.price_markup, 'price_markup', positive=False)
         check_integer(self.rest_count, 'rest_count')
```

### `domain.battery.offer.xǁBatteryOfferǁ__post_init____mutmut_12`

Классификация 2026-11-14: Эквивалент: для `price_recommended` positive=False заменён на None. В check_number флаг используется только в `positive and numeric == 0`; оба значения ложны. Проверки конечности и отрицательного знака не меняются, ноль остаётся допустимым. Прогон R2 оставляет survived.

Статус: **survived**; тип: `to_none`; выбрано тестов: 202.

```diff
--- src/domain/battery/offer.py
+++ src/domain/battery/offer.py
@@ -1,6 +1,6 @@
     def __post_init__(self) -> None:
         check_number(self.price_opt, 'price_opt', positive=False)
-        check_number(self.price_recommended, 'price_recommended', positive=False)
+        check_number(self.price_recommended, 'price_recommended', positive=None)
         check_number(self.price_markup, 'price_markup', positive=False)
         check_integer(self.rest_count, 'rest_count')
         check_integer(self.warranty_months, 'warranty_months')
```

### `domain.battery.offer.xǁBatteryOfferǁ__post_init____mutmut_16`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 202.

```diff
--- src/domain/battery/offer.py
+++ src/domain/battery/offer.py
@@ -1,6 +1,6 @@
     def __post_init__(self) -> None:
         check_number(self.price_opt, 'price_opt', positive=False)
-        check_number(self.price_recommended, 'price_recommended', positive=False)
+        check_number(self.price_recommended, 'XXprice_recommendedXX', positive=False)
         check_number(self.price_markup, 'price_markup', positive=False)
         check_integer(self.rest_count, 'rest_count')
         check_integer(self.warranty_months, 'warranty_months')
```

### `domain.battery.offer.xǁBatteryOfferǁ__post_init____mutmut_19`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 202.

```diff
--- src/domain/battery/offer.py
+++ src/domain/battery/offer.py
@@ -1,6 +1,6 @@
     def __post_init__(self) -> None:
         check_number(self.price_opt, 'price_opt', positive=False)
         check_number(self.price_recommended, 'price_recommended', positive=False)
-        check_number(self.price_markup, 'price_markup', positive=False)
+        check_number(None, 'price_markup', positive=False)
         check_integer(self.rest_count, 'rest_count')
         check_integer(self.warranty_months, 'warranty_months')
```

### `domain.battery.offer.xǁBatteryOfferǁ__post_init____mutmut_20`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 202.

```diff
--- src/domain/battery/offer.py
+++ src/domain/battery/offer.py
@@ -1,6 +1,6 @@
     def __post_init__(self) -> None:
         check_number(self.price_opt, 'price_opt', positive=False)
         check_number(self.price_recommended, 'price_recommended', positive=False)
-        check_number(self.price_markup, 'price_markup', positive=False)
+        check_number(self.price_markup, None, positive=False)
         check_integer(self.rest_count, 'rest_count')
         check_integer(self.warranty_months, 'warranty_months')
```

### `domain.battery.offer.xǁBatteryOfferǁ__post_init____mutmut_21`

Классификация 2026-11-14: Эквивалент: для `price_markup` positive=False заменён на None. В check_number флаг используется только в `positive and numeric == 0`; оба значения ложны. Проверки конечности и отрицательного знака не меняются, ноль остаётся допустимым. Прогон R2 оставляет survived.

Статус: **survived**; тип: `to_none`; выбрано тестов: 202.

```diff
--- src/domain/battery/offer.py
+++ src/domain/battery/offer.py
@@ -1,6 +1,6 @@
     def __post_init__(self) -> None:
         check_number(self.price_opt, 'price_opt', positive=False)
         check_number(self.price_recommended, 'price_recommended', positive=False)
-        check_number(self.price_markup, 'price_markup', positive=False)
+        check_number(self.price_markup, 'price_markup', positive=None)
         check_integer(self.rest_count, 'rest_count')
         check_integer(self.warranty_months, 'warranty_months')
```

### `domain.battery.offer.xǁBatteryOfferǁ__post_init____mutmut_25`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 202.

```diff
--- src/domain/battery/offer.py
+++ src/domain/battery/offer.py
@@ -1,6 +1,6 @@
     def __post_init__(self) -> None:
         check_number(self.price_opt, 'price_opt', positive=False)
         check_number(self.price_recommended, 'price_recommended', positive=False)
-        check_number(self.price_markup, 'price_markup', positive=False)
+        check_number(self.price_markup, 'XXprice_markupXX', positive=False)
         check_integer(self.rest_count, 'rest_count')
         check_integer(self.warranty_months, 'warranty_months')
```

### `domain.battery.offer.xǁBatteryOfferǁ__post_init____mutmut_26`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 202.

```diff
--- src/domain/battery/offer.py
+++ src/domain/battery/offer.py
@@ -1,6 +1,6 @@
     def __post_init__(self) -> None:
         check_number(self.price_opt, 'price_opt', positive=False)
         check_number(self.price_recommended, 'price_recommended', positive=False)
-        check_number(self.price_markup, 'price_markup', positive=False)
+        check_number(self.price_markup, 'PRICE_MARKUP', positive=False)
         check_integer(self.rest_count, 'rest_count')
         check_integer(self.warranty_months, 'warranty_months')
```

### `domain.battery.offer.xǁBatteryOfferǁ__post_init____mutmut_32`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 202.

```diff
--- src/domain/battery/offer.py
+++ src/domain/battery/offer.py
@@ -2,5 +2,5 @@
         check_number(self.price_opt, 'price_opt', positive=False)
         check_number(self.price_recommended, 'price_recommended', positive=False)
         check_number(self.price_markup, 'price_markup', positive=False)
-        check_integer(self.rest_count, 'rest_count')
+        check_integer(self.rest_count, 'XXrest_countXX')
         check_integer(self.warranty_months, 'warranty_months')
```

### `domain.battery.offer.xǁBatteryOfferǁ__post_init____mutmut_38`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 202.

```diff
--- src/domain/battery/offer.py
+++ src/domain/battery/offer.py
@@ -3,4 +3,4 @@
         check_number(self.price_recommended, 'price_recommended', positive=False)
         check_number(self.price_markup, 'price_markup', positive=False)
         check_integer(self.rest_count, 'rest_count')
-        check_integer(self.warranty_months, 'warranty_months')
+        check_integer(self.warranty_months, 'XXwarranty_monthsXX')
```

## src/domain/battery/parameters.py

### `domain.battery.parameters.xǁBatteryParametersǁ__post_init____mutmut_11`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 223.

```diff
--- src/domain/battery/parameters.py
+++ src/domain/battery/parameters.py
@@ -1,5 +1,5 @@
     def __post_init__(self) -> None:
         check_number(self.capacity_ah, 'capacity_ah')
-        check_number(self.starting_current_a, 'starting_current_a')
+        check_number(self.starting_current_a, 'XXstarting_current_aXX')
         check_flag(self.efb, 'efb')
         check_flag(self.agm, 'agm')
```

### `domain.battery.parameters.xǁBatteryParametersǁ__post_init____mutmut_17`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 223.

```diff
--- src/domain/battery/parameters.py
+++ src/domain/battery/parameters.py
@@ -1,5 +1,5 @@
     def __post_init__(self) -> None:
         check_number(self.capacity_ah, 'capacity_ah')
         check_number(self.starting_current_a, 'starting_current_a')
-        check_flag(self.efb, 'efb')
+        check_flag(self.efb, 'XXefbXX')
         check_flag(self.agm, 'agm')
```

### `domain.battery.parameters.xǁBatteryParametersǁ__post_init____mutmut_23`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 223.

```diff
--- src/domain/battery/parameters.py
+++ src/domain/battery/parameters.py
@@ -2,4 +2,4 @@
         check_number(self.capacity_ah, 'capacity_ah')
         check_number(self.starting_current_a, 'starting_current_a')
         check_flag(self.efb, 'efb')
-        check_flag(self.agm, 'agm')
+        check_flag(self.agm, 'XXagmXX')
```

## src/domain/battery/result.py

### `domain.battery.result.xǁBatteryResultǁ__post_init____mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 156.

```diff
--- src/domain/battery/result.py
+++ src/domain/battery/result.py
@@ -1,5 +1,5 @@
     def __post_init__(self) -> None:
         if not isinstance(self.positions, tuple):
-            raise TypeError('Позиции пакета должны быть кортежем')
+            raise TypeError(None)
         if any(not isinstance(position, BatteryItem) for position in self.positions):
             raise TypeError('Пакет batteries принимает только BatteryItem')
```

### `domain.battery.result.xǁBatteryResultǁ__post_init____mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 156.

```diff
--- src/domain/battery/result.py
+++ src/domain/battery/result.py
@@ -1,5 +1,5 @@
     def __post_init__(self) -> None:
         if not isinstance(self.positions, tuple):
-            raise TypeError('Позиции пакета должны быть кортежем')
+            raise TypeError('XXПозиции пакета должны быть кортежемXX')
         if any(not isinstance(position, BatteryItem) for position in self.positions):
             raise TypeError('Пакет batteries принимает только BatteryItem')
```

### `domain.battery.result.xǁBatteryResultǁ__post_init____mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 156.

```diff
--- src/domain/battery/result.py
+++ src/domain/battery/result.py
@@ -1,5 +1,5 @@
     def __post_init__(self) -> None:
         if not isinstance(self.positions, tuple):
-            raise TypeError('Позиции пакета должны быть кортежем')
+            raise TypeError('позиции пакета должны быть кортежем')
         if any(not isinstance(position, BatteryItem) for position in self.positions):
             raise TypeError('Пакет batteries принимает только BatteryItem')
```

### `domain.battery.result.xǁBatteryResultǁ__post_init____mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 156.

```diff
--- src/domain/battery/result.py
+++ src/domain/battery/result.py
@@ -1,5 +1,5 @@
     def __post_init__(self) -> None:
         if not isinstance(self.positions, tuple):
-            raise TypeError('Позиции пакета должны быть кортежем')
+            raise TypeError('ПОЗИЦИИ ПАКЕТА ДОЛЖНЫ БЫТЬ КОРТЕЖЕМ')
         if any(not isinstance(position, BatteryItem) for position in self.positions):
             raise TypeError('Пакет batteries принимает только BatteryItem')
```

### `domain.battery.result.xǁBatteryResultǁ__post_init____mutmut_8`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 156.

```diff
--- src/domain/battery/result.py
+++ src/domain/battery/result.py
@@ -2,4 +2,4 @@
         if not isinstance(self.positions, tuple):
             raise TypeError('Позиции пакета должны быть кортежем')
         if any(not isinstance(position, BatteryItem) for position in self.positions):
-            raise TypeError('Пакет batteries принимает только BatteryItem')
+            raise TypeError(None)
```

### `domain.battery.result.xǁBatteryResultǁ__post_init____mutmut_9`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 156.

```diff
--- src/domain/battery/result.py
+++ src/domain/battery/result.py
@@ -2,4 +2,4 @@
         if not isinstance(self.positions, tuple):
             raise TypeError('Позиции пакета должны быть кортежем')
         if any(not isinstance(position, BatteryItem) for position in self.positions):
-            raise TypeError('Пакет batteries принимает только BatteryItem')
+            raise TypeError('XXПакет batteries принимает только BatteryItemXX')
```

### `domain.battery.result.xǁBatteryResultǁ__post_init____mutmut_10`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 156.

```diff
--- src/domain/battery/result.py
+++ src/domain/battery/result.py
@@ -2,4 +2,4 @@
         if not isinstance(self.positions, tuple):
             raise TypeError('Позиции пакета должны быть кортежем')
         if any(not isinstance(position, BatteryItem) for position in self.positions):
-            raise TypeError('Пакет batteries принимает только BatteryItem')
+            raise TypeError('пакет batteries принимает только batteryitem')
```

### `domain.battery.result.xǁBatteryResultǁ__post_init____mutmut_11`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 156.

```diff
--- src/domain/battery/result.py
+++ src/domain/battery/result.py
@@ -2,4 +2,4 @@
         if not isinstance(self.positions, tuple):
             raise TypeError('Позиции пакета должны быть кортежем')
         if any(not isinstance(position, BatteryItem) for position in self.positions):
-            raise TypeError('Пакет batteries принимает только BatteryItem')
+            raise TypeError('ПАКЕТ BATTERIES ПРИНИМАЕТ ТОЛЬКО BATTERYITEM')
```

### `domain.battery.result.xǁBatteryResultǁmerge__mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/domain/battery/result.py
+++ src/domain/battery/result.py
@@ -1,5 +1,5 @@
     def merge(self, other: ProductGroupResult[ProductPosition]) -> BatteryResult:
         """Объединить только аккумуляторы с сохранением порядка и исходных пакетов."""
         if not isinstance(other, BatteryResult):
-            raise TypeError('Пакет batteries объединяется только с той же моделью')
+            raise TypeError(None)
         return BatteryResult(self.positions + other.positions)
```

### `domain.battery.result.xǁBatteryResultǁmerge__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 2.

```diff
--- src/domain/battery/result.py
+++ src/domain/battery/result.py
@@ -1,5 +1,5 @@
     def merge(self, other: ProductGroupResult[ProductPosition]) -> BatteryResult:
         """Объединить только аккумуляторы с сохранением порядка и исходных пакетов."""
         if not isinstance(other, BatteryResult):
-            raise TypeError('Пакет batteries объединяется только с той же моделью')
+            raise TypeError('XXПакет batteries объединяется только с той же модельюXX')
         return BatteryResult(self.positions + other.positions)
```

### `domain.battery.result.xǁBatteryResultǁmerge__mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 2.

```diff
--- src/domain/battery/result.py
+++ src/domain/battery/result.py
@@ -1,5 +1,5 @@
     def merge(self, other: ProductGroupResult[ProductPosition]) -> BatteryResult:
         """Объединить только аккумуляторы с сохранением порядка и исходных пакетов."""
         if not isinstance(other, BatteryResult):
-            raise TypeError('Пакет batteries объединяется только с той же моделью')
+            raise TypeError('пакет batteries объединяется только с той же моделью')
         return BatteryResult(self.positions + other.positions)
```

### `domain.battery.result.xǁBatteryResultǁmerge__mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 2.

```diff
--- src/domain/battery/result.py
+++ src/domain/battery/result.py
@@ -1,5 +1,5 @@
     def merge(self, other: ProductGroupResult[ProductPosition]) -> BatteryResult:
         """Объединить только аккумуляторы с сохранением порядка и исходных пакетов."""
         if not isinstance(other, BatteryResult):
-            raise TypeError('Пакет batteries объединяется только с той же моделью')
+            raise TypeError('ПАКЕТ BATTERIES ОБЪЕДИНЯЕТСЯ ТОЛЬКО С ТОЙ ЖЕ МОДЕЛЬЮ')
         return BatteryResult(self.positions + other.positions)
```

## src/domain/product_group_result.py

### `domain.product_group_result.xǁTireAndDiskResultǁ__post_init____mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 226.

```diff
--- src/domain/product_group_result.py
+++ src/domain/product_group_result.py
@@ -1,5 +1,5 @@
     def __post_init__(self) -> None:
         if not isinstance(self.positions, tuple):
-            raise TypeError('Позиции пакета должны быть кортежем')
+            raise TypeError(None)
         if any(not isinstance(position, RowItem) for position in self.positions):
             raise TypeError('Пакет tire_and_disk принимает только RowItem')
```

### `domain.product_group_result.xǁTireAndDiskResultǁ__post_init____mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 226.

```diff
--- src/domain/product_group_result.py
+++ src/domain/product_group_result.py
@@ -1,5 +1,5 @@
     def __post_init__(self) -> None:
         if not isinstance(self.positions, tuple):
-            raise TypeError('Позиции пакета должны быть кортежем')
+            raise TypeError('XXПозиции пакета должны быть кортежемXX')
         if any(not isinstance(position, RowItem) for position in self.positions):
             raise TypeError('Пакет tire_and_disk принимает только RowItem')
```

### `domain.product_group_result.xǁTireAndDiskResultǁ__post_init____mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 226.

```diff
--- src/domain/product_group_result.py
+++ src/domain/product_group_result.py
@@ -1,5 +1,5 @@
     def __post_init__(self) -> None:
         if not isinstance(self.positions, tuple):
-            raise TypeError('Позиции пакета должны быть кортежем')
+            raise TypeError('позиции пакета должны быть кортежем')
         if any(not isinstance(position, RowItem) for position in self.positions):
             raise TypeError('Пакет tire_and_disk принимает только RowItem')
```

### `domain.product_group_result.xǁTireAndDiskResultǁ__post_init____mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 226.

```diff
--- src/domain/product_group_result.py
+++ src/domain/product_group_result.py
@@ -1,5 +1,5 @@
     def __post_init__(self) -> None:
         if not isinstance(self.positions, tuple):
-            raise TypeError('Позиции пакета должны быть кортежем')
+            raise TypeError('ПОЗИЦИИ ПАКЕТА ДОЛЖНЫ БЫТЬ КОРТЕЖЕМ')
         if any(not isinstance(position, RowItem) for position in self.positions):
             raise TypeError('Пакет tire_and_disk принимает только RowItem')
```

### `domain.product_group_result.xǁTireAndDiskResultǁ__post_init____mutmut_8`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 226.

```diff
--- src/domain/product_group_result.py
+++ src/domain/product_group_result.py
@@ -2,4 +2,4 @@
         if not isinstance(self.positions, tuple):
             raise TypeError('Позиции пакета должны быть кортежем')
         if any(not isinstance(position, RowItem) for position in self.positions):
-            raise TypeError('Пакет tire_and_disk принимает только RowItem')
+            raise TypeError(None)
```

### `domain.product_group_result.xǁTireAndDiskResultǁ__post_init____mutmut_9`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 226.

```diff
--- src/domain/product_group_result.py
+++ src/domain/product_group_result.py
@@ -2,4 +2,4 @@
         if not isinstance(self.positions, tuple):
             raise TypeError('Позиции пакета должны быть кортежем')
         if any(not isinstance(position, RowItem) for position in self.positions):
-            raise TypeError('Пакет tire_and_disk принимает только RowItem')
+            raise TypeError('XXПакет tire_and_disk принимает только RowItemXX')
```

### `domain.product_group_result.xǁTireAndDiskResultǁ__post_init____mutmut_10`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 226.

```diff
--- src/domain/product_group_result.py
+++ src/domain/product_group_result.py
@@ -2,4 +2,4 @@
         if not isinstance(self.positions, tuple):
             raise TypeError('Позиции пакета должны быть кортежем')
         if any(not isinstance(position, RowItem) for position in self.positions):
-            raise TypeError('Пакет tire_and_disk принимает только RowItem')
+            raise TypeError('пакет tire_and_disk принимает только rowitem')
```

### `domain.product_group_result.xǁTireAndDiskResultǁ__post_init____mutmut_11`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 226.

```diff
--- src/domain/product_group_result.py
+++ src/domain/product_group_result.py
@@ -2,4 +2,4 @@
         if not isinstance(self.positions, tuple):
             raise TypeError('Позиции пакета должны быть кортежем')
         if any(not isinstance(position, RowItem) for position in self.positions):
-            raise TypeError('Пакет tire_and_disk принимает только RowItem')
+            raise TypeError('ПАКЕТ TIRE_AND_DISK ПРИНИМАЕТ ТОЛЬКО ROWITEM')
```

### `domain.product_group_result.xǁTireAndDiskResultǁmerge__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 6.

```diff
--- src/domain/product_group_result.py
+++ src/domain/product_group_result.py
@@ -1,4 +1,4 @@
     def merge(self, other: ProductGroupResult[ProductPosition]) -> TireAndDiskResult:
         if not isinstance(other, TireAndDiskResult):
-            raise TypeError('Пакет tire_and_disk объединяется только с той же моделью')
+            raise TypeError('XXПакет tire_and_disk объединяется только с той же модельюXX')
         return TireAndDiskResult(self.positions + other.positions)
```

### `domain.product_group_result.xǁTireAndDiskResultǁmerge__mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 6.

```diff
--- src/domain/product_group_result.py
+++ src/domain/product_group_result.py
@@ -1,4 +1,4 @@
     def merge(self, other: ProductGroupResult[ProductPosition]) -> TireAndDiskResult:
         if not isinstance(other, TireAndDiskResult):
-            raise TypeError('Пакет tire_and_disk объединяется только с той же моделью')
+            raise TypeError('пакет tire_and_disk объединяется только с той же моделью')
         return TireAndDiskResult(self.positions + other.positions)
```

## src/domain/row_item/disk_name_extras.py

### `domain.row_item.disk_name_extras.x_disk_name_extras__mutmut_1`

Классификация 2026-11-14: Эквивалент: Значение model используется только в проверке label not in model; каждый label завода имеет вид «(XX)»–«(XXXXX)» и содержит скобки. Ни один такой label не входит ни в пустую строку, ни в XXXX. При явном model дефолт не используется; остальные метки от model не зависят. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 40.

```diff
--- src/domain/row_item/disk_name_extras.py
+++ src/domain/row_item/disk_name_extras.py
@@ -1,4 +1,4 @@
-def disk_name_extras(title: str, model: str = '') -> str:
+def disk_name_extras(title: str, model: str = 'XXXX') -> str:
     """Завод, alive, вентиль, нагрузка в кг и хвосты диска; без толщины и складского кода.
 
     Скобка, которая уже есть в модели (`R004 (Logan)`), заводом не считается и в хвост не попадает.
```

## src/domain/row_item/markdown_title.py

### `domain.row_item.markdown_title.x_is_markdown_title__mutmut_5`

Классификация 2026-11-14: Эквивалент: При пустом title или None bool(title) останавливает and до поиска регулярного выражения. При непустой строке title or fallback возвращает исходный title, поэтому изменённый fallback недостижим. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 29.

```diff
--- src/domain/row_item/markdown_title.py
+++ src/domain/row_item/markdown_title.py
@@ -1,3 +1,3 @@
 def is_markdown_title(title: str | None) -> bool:
     """Уценённый товар: в названии «Уценка», «уценённый», «Дефект ЛКП»."""
-    return bool(title) and _MARKDOWN_RE.search(title or '') is not None
+    return bool(title) and _MARKDOWN_RE.search(title or 'XXXX') is not None
```

## src/domain/row_item/production_plant.py

### `domain.row_item.production_plant.x_production_plant__mutmut_4`

Классификация 2026-11-14: Эквивалент: Для непустого title поиск не меняется. Для пустой строки и None ни пустая строка, ни XXXX не совпадают с перечислением кириллических названий заводов в _PLANT_RE; результат в обоих случаях None. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 33.

```diff
--- src/domain/row_item/production_plant.py
+++ src/domain/row_item/production_plant.py
@@ -1,4 +1,4 @@
 def production_plant(title: str | None) -> str | None:
     """Завод из «НкШЗ», «ОШЗ», «ЯШЗ», «ВолШЗ», «БШК» (любой регистр); нет признака → None."""
-    match = _PLANT_RE.search(title or '')
+    match = _PLANT_RE.search(title or 'XXXX')
     return _PLANTS[match[1].lower()] if match else None
```

## src/domain/row_item/production_year.py

### `domain.row_item.production_year.x_production_year__mutmut_3`

Классификация 2026-11-14: Эквивалент: Для непустого title текст не меняется. Для пустой строки и None ни пустая строка, ни XXXX не содержат год 20xx с г.в. или цифры с «года и старше»; оба регулярных выражения не совпадают, результат None. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 31.

```diff
--- src/domain/row_item/production_year.py
+++ src/domain/row_item/production_year.py
@@ -1,6 +1,6 @@
 def production_year(title: str | None) -> int | None:
     """Год выпуска из «2023г.в.», «2022 г.в.»; «2 года и старше» → OLDEST_YEAR; нет признака → None."""
-    text = title or ''
+    text = title or 'XXXX'
     match = _YEAR_RE.search(text)
     if match:
         return int(match[1])
```

## src/infrastructure/config/mim_api_config.py

### `infrastructure.config.mim_api_config.x_get_mim_api_config__mutmut_1`

Классификация 2026-11-14: Закрытый пробел проверки: Усилен test_missing_token_with_env_file: точное сообщение отличает существующий .env без токена от отсутствующего файла; прежний match проверял только имя переменной и пропускал удаление вызова load_dotenv. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R6: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 5.

```diff
--- src/infrastructure/config/mim_api_config.py
+++ src/infrastructure/config/mim_api_config.py
@@ -1,6 +1,6 @@
 def get_mim_api_config() -> MimApiConfig:
     """MIM API settings from env / .env."""
-    has_env_file = load_dotenv()
+    has_env_file = None
 
     token = os.environ.get(_ENV_TOKEN, '').strip()
     host = os.environ.get(_ENV_HOST, _DEFAULT_HOST).strip() or _DEFAULT_HOST
```

### `infrastructure.config.mim_api_config.x_get_mim_api_config__mutmut_16`

Классификация 2026-11-14: Закрытый пробел проверки: Усилен test_missing_token_with_env_file: точное сообщение отличает существующий .env без токена от отсутствующего файла; прежний match проверял только имя переменной и пропускал потерю флага has_env_file. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R6: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 5.

```diff
--- src/infrastructure/config/mim_api_config.py
+++ src/infrastructure/config/mim_api_config.py
@@ -6,6 +6,6 @@
     host = os.environ.get(_ENV_HOST, _DEFAULT_HOST).strip() or _DEFAULT_HOST
 
     if not token:
-        raise MimApiConfigError(_token_error_message(has_env_file))
+        raise MimApiConfigError(_token_error_message(None))
 
     return MimApiConfig(host=host, token=token)
```

## src/infrastructure/config/result_folder.py

### `infrastructure.config.result_folder.x_clear_result_folder__mutmut_8`

Классификация 2026-11-14: Закрытый пробел проверки: Добавлен test_clear_result_folder_tolerates_disappeared_file: перечисленный файл уже отсутствует к моменту unlink. missing_ok=None вызывает FileNotFoundError, исходный True сохраняет успешную очистку. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R6: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 3.

```diff
--- src/infrastructure/config/result_folder.py
+++ src/infrastructure/config/result_folder.py
@@ -7,4 +7,4 @@
         if entry.is_dir() and not entry.is_symlink():
             shutil.rmtree(entry)
             continue
-        entry.unlink(missing_ok=True)
+        entry.unlink(missing_ok=None)
```

### `infrastructure.config.result_folder.x_clear_result_folder__mutmut_9`

Классификация 2026-11-14: Закрытый пробел проверки: Добавлен test_clear_result_folder_tolerates_disappeared_file: перечисленный файл уже отсутствует к моменту unlink. missing_ok=False вызывает FileNotFoundError, исходный True сохраняет успешную очистку. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R6: killed. Исторический survived сохранён.

Статус: **survived**; тип: `keyword`; выбрано тестов: 3.

```diff
--- src/infrastructure/config/result_folder.py
+++ src/infrastructure/config/result_folder.py
@@ -7,4 +7,4 @@
         if entry.is_dir() and not entry.is_symlink():
             shutil.rmtree(entry)
             continue
-        entry.unlink(missing_ok=True)
+        entry.unlink(missing_ok=False)
```

## src/infrastructure/data/price_backup.py

### `infrastructure.data.price_backup.x_backup_prices__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 8.

```diff
--- src/infrastructure/data/price_backup.py
+++ src/infrastructure/data/price_backup.py
@@ -3,6 +3,6 @@
     if target.exists():
         shutil.rmtree(target)
     if not source.is_dir():
-        target.mkdir(parents=True)
+        target.mkdir(parents=None)
         return
     shutil.copytree(source, target, ignore=_skip_folder(skip))
```

### `infrastructure.data.price_backup.x_backup_prices__mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `keyword`; выбрано тестов: 8.

```diff
--- src/infrastructure/data/price_backup.py
+++ src/infrastructure/data/price_backup.py
@@ -3,6 +3,6 @@
     if target.exists():
         shutil.rmtree(target)
     if not source.is_dir():
-        target.mkdir(parents=True)
+        target.mkdir(parents=False)
         return
     shutil.copytree(source, target, ignore=_skip_folder(skip))
```

## src/infrastructure/mail/doh.py

### `infrastructure.mail.doh.x__doh_addresses__mutmut_8`

Классификация 2026-11-14: Эквивалент: urllib.request.Request нормализует имя заголовка через capitalize; Accept и accept дают одинаковый заголовок Accept с прежним значением. Прогон R5 оставляет survived.

Статус: **survived**; тип: `string_case`; выбрано тестов: 5.

```diff
--- src/infrastructure/mail/doh.py
+++ src/infrastructure/mail/doh.py
@@ -3,7 +3,7 @@
     for template in _DOH_URLS:
         request = urllib.request.Request(  # noqa: S310
             template.format(host=host),
-            headers={'Accept': 'application/dns-json'},
+            headers={'accept': 'application/dns-json'},
         )
         try:
             with urllib.request.urlopen(request, timeout=_DOH_TIMEOUT_SECONDS) as response:  # noqa: S310  # nosec B310
```

### `infrastructure.mail.doh.x__doh_addresses__mutmut_9`

Классификация 2026-11-14: Эквивалент: urllib.request.Request нормализует имя заголовка через capitalize; Accept и ACCEPT дают одинаковый заголовок Accept с прежним значением. Прогон R5 оставляет survived.

Статус: **survived**; тип: `string_case`; выбрано тестов: 5.

```diff
--- src/infrastructure/mail/doh.py
+++ src/infrastructure/mail/doh.py
@@ -3,7 +3,7 @@
     for template in _DOH_URLS:
         request = urllib.request.Request(  # noqa: S310
             template.format(host=host),
-            headers={'Accept': 'application/dns-json'},
+            headers={'ACCEPT': 'application/dns-json'},
         )
         try:
             with urllib.request.urlopen(request, timeout=_DOH_TIMEOUT_SECONDS) as response:  # noqa: S310  # nosec B310
```

### `infrastructure.mail.doh.x__doh_addresses__mutmut_19`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 5.

```diff
--- src/infrastructure/mail/doh.py
+++ src/infrastructure/mail/doh.py
@@ -9,7 +9,7 @@
             with urllib.request.urlopen(request, timeout=_DOH_TIMEOUT_SECONDS) as response:  # noqa: S310  # nosec B310
                 payload = json.load(response)
         except (OSError, ValueError) as exc:
-            _log_doh_failure(template, host, exc)
+            _log_doh_failure(template, None, exc)
             continue
         addresses = _doh_answers(payload)
         if addresses:
```

### `infrastructure.mail.doh.x__log_doh_failure__mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 3.

```diff
--- src/infrastructure/mail/doh.py
+++ src/infrastructure/mail/doh.py
@@ -1,4 +1,4 @@
 def _log_doh_failure(template: str, host: str, exc: Exception) -> None:
     """Записать сбой одного DoH-провайдера: без лога причина пустого результата теряется."""
-    endpoint = template.split('?', maxsplit=1)[0]
+    endpoint = template.split(None, maxsplit=1)[0]
     logger.warning(f'DoH {endpoint}, хост {host!r}: {exc!r}')
```

### `infrastructure.mail.doh.x__log_doh_failure__mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/infrastructure/mail/doh.py
+++ src/infrastructure/mail/doh.py
@@ -1,4 +1,4 @@
 def _log_doh_failure(template: str, host: str, exc: Exception) -> None:
     """Записать сбой одного DoH-провайдера: без лога причина пустого результата теряется."""
-    endpoint = template.split('?', maxsplit=1)[0]
+    endpoint = template.split(maxsplit=1)[0]
     logger.warning(f'DoH {endpoint}, хост {host!r}: {exc!r}')
```

### `infrastructure.mail.doh.x__log_doh_failure__mutmut_5`

Классификация 2026-11-14: Эквивалент: Берётся первый фрагмент split по вопросительному знаку; снятие maxsplit не меняет этот фрагмент даже при нескольких разделителях. Прогон R5 оставляет survived.

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/infrastructure/mail/doh.py
+++ src/infrastructure/mail/doh.py
@@ -1,4 +1,4 @@
 def _log_doh_failure(template: str, host: str, exc: Exception) -> None:
     """Записать сбой одного DoH-провайдера: без лога причина пустого результата теряется."""
-    endpoint = template.split('?', maxsplit=1)[0]
+    endpoint = template.split('?', )[0]
     logger.warning(f'DoH {endpoint}, хост {host!r}: {exc!r}')
```

### `infrastructure.mail.doh.x__log_doh_failure__mutmut_6`

Классификация 2026-11-14: Эквивалент: Оба шаблона из _DOH_URLS содержат ровно один вопросительный знак; split и rsplit с maxsplit=1 возвращают один и тот же endpoint. Произвольные внешние шаблоны функция не получает. Прогон R5 оставляет survived.

Статус: **survived**; тип: `method_swap`; выбрано тестов: 3.

```diff
--- src/infrastructure/mail/doh.py
+++ src/infrastructure/mail/doh.py
@@ -1,4 +1,4 @@
 def _log_doh_failure(template: str, host: str, exc: Exception) -> None:
     """Записать сбой одного DoH-провайдера: без лога причина пустого результата теряется."""
-    endpoint = template.split('?', maxsplit=1)[0]
+    endpoint = template.rsplit('?', maxsplit=1)[0]
     logger.warning(f'DoH {endpoint}, хост {host!r}: {exc!r}')
```

### `infrastructure.mail.doh.x__log_doh_failure__mutmut_7`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 3.

```diff
--- src/infrastructure/mail/doh.py
+++ src/infrastructure/mail/doh.py
@@ -1,4 +1,4 @@
 def _log_doh_failure(template: str, host: str, exc: Exception) -> None:
     """Записать сбой одного DoH-провайдера: без лога причина пустого результата теряется."""
-    endpoint = template.split('?', maxsplit=1)[0]
+    endpoint = template.split('XX?XX', maxsplit=1)[0]
     logger.warning(f'DoH {endpoint}, хост {host!r}: {exc!r}')
```

### `infrastructure.mail.doh.x__log_doh_failure__mutmut_8`

Классификация 2026-11-14: Эквивалент: Берётся первый фрагмент split по вопросительному знаку; maxsplit=1 и maxsplit=2 сохраняют его одинаковым. Прогон R5 оставляет survived.

Статус: **survived**; тип: `number`; выбрано тестов: 3.

```diff
--- src/infrastructure/mail/doh.py
+++ src/infrastructure/mail/doh.py
@@ -1,4 +1,4 @@
 def _log_doh_failure(template: str, host: str, exc: Exception) -> None:
     """Записать сбой одного DoH-провайдера: без лога причина пустого результата теряется."""
-    endpoint = template.split('?', maxsplit=1)[0]
+    endpoint = template.split('?', maxsplit=2)[0]
     logger.warning(f'DoH {endpoint}, хост {host!r}: {exc!r}')
```

## src/infrastructure/mail/imap.py

### `infrastructure.mail.imap.x__message_body__mutmut_1`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `operator`; выбрано тестов: 15.

```diff
--- src/infrastructure/mail/imap.py
+++ src/infrastructure/mail/imap.py
@@ -1,6 +1,6 @@
 def _message_body(entry: Any) -> bytes | None:
     """Тело письма из элемента ответа FETCH, если он его содержит."""
-    if not isinstance(entry, tuple) or len(entry) <= 1:
+    if not isinstance(entry, tuple) and len(entry) <= 1:
         return None
     body = entry[1]
     if isinstance(body, (bytes, bytearray)):
```

### `infrastructure.mail.imap.x__message_body__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `operator`; выбрано тестов: 15.

```diff
--- src/infrastructure/mail/imap.py
+++ src/infrastructure/mail/imap.py
@@ -1,6 +1,6 @@
 def _message_body(entry: Any) -> bytes | None:
     """Тело письма из элемента ответа FETCH, если он его содержит."""
-    if not isinstance(entry, tuple) or len(entry) <= 1:
+    if not isinstance(entry, tuple) or len(entry) < 1:
         return None
     body = entry[1]
     if isinstance(body, (bytes, bytearray)):
```

### `infrastructure.mail.imap.x__unquote__mutmut_7`

Классификация 2026-11-14: Эквивалент: Имена кодировки utf-8 и UTF-8 обозначают один и тот же кодек; режим replace, снятие кавычек и результат сохраняются. Прогон R5 оставляет survived.

Статус: **survived**; тип: `string_case`; выбрано тестов: 18.

```diff
--- src/infrastructure/mail/imap.py
+++ src/infrastructure/mail/imap.py
@@ -1,6 +1,6 @@
 def _unquote(token: bytes) -> str:
     """Снять кавычки и обратные слэши со строкового токена IMAP."""
-    text = token.decode('utf-8', 'replace').strip()
+    text = token.decode('UTF-8', 'replace').strip()
     if not _is_quoted(text):
         return text
     return re.sub(r'\\(.)', r'\1', text[1:-1])
```

### `infrastructure.mail.imap.x_connect__mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 4.

```diff
--- src/infrastructure/mail/imap.py
+++ src/infrastructure/mail/imap.py
@@ -1,6 +1,6 @@
 def connect(host: str, port: int, folder: str, credentials: MailCredentials) -> ImapClient:
     """Подключиться, войти и открыть папку только для чтения."""
-    client = open_client(host, port)
+    client = open_client(None, port)
     try:
         client.login(credentials.login, credentials.password)
     except imaplib.IMAP4.error:
```

### `infrastructure.mail.imap.x_connect__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 4.

```diff
--- src/infrastructure/mail/imap.py
+++ src/infrastructure/mail/imap.py
@@ -1,6 +1,6 @@
 def connect(host: str, port: int, folder: str, credentials: MailCredentials) -> ImapClient:
     """Подключиться, войти и открыть папку только для чтения."""
-    client = open_client(host, port)
+    client = open_client(host, None)
     try:
         client.login(credentials.login, credentials.password)
     except imaplib.IMAP4.error:
```

## src/infrastructure/remote/four_tochki_client.py

### `infrastructure.remote.four_tochki_client.x__local__mutmut_4`

Классификация 2026-11-14: Эквивалент: Последний фрагмент rsplit после последнего разделителя не зависит от ограничения числа разбиений: maxsplit=1 и отсутствие ограничения дают тот же результат. Прогон R5 оставляет survived.

Статус: **survived**; тип: `other`; выбрано тестов: 43.

```diff
--- src/infrastructure/remote/four_tochki_client.py
+++ src/infrastructure/remote/four_tochki_client.py
@@ -1,3 +1,3 @@
 def _local(tag: str) -> str:
     """Имя тега без пространства имён."""
-    return tag.rsplit('}', 1)[-1]
+    return tag.rsplit('}', )[-1]
```

### `infrastructure.remote.four_tochki_client.x__local__mutmut_5`

Классификация 2026-11-14: Эквивалент: В тегах SOAP-контрактов Форточек разделитель } встречается только между пространством имён и локальным именем; split и rsplit возвращают одинаковое локальное имя. Эквивалентность ограничена этим входным контрактом, а не произвольной строкой с несколькими }. Прогон R5 оставляет survived.

Статус: **survived**; тип: `method_swap`; выбрано тестов: 43.

```diff
--- src/infrastructure/remote/four_tochki_client.py
+++ src/infrastructure/remote/four_tochki_client.py
@@ -1,3 +1,3 @@
 def _local(tag: str) -> str:
     """Имя тега без пространства имён."""
-    return tag.rsplit('}', 1)[-1]
+    return tag.split('}', 1)[-1]
```

### `infrastructure.remote.four_tochki_client.x__local__mutmut_7`

Классификация 2026-11-14: Эквивалент: Последний фрагмент rsplit после последнего разделителя одинаков при maxsplit=1 и maxsplit=2. Прогон R5 оставляет survived.

Статус: **survived**; тип: `number`; выбрано тестов: 43.

```diff
--- src/infrastructure/remote/four_tochki_client.py
+++ src/infrastructure/remote/four_tochki_client.py
@@ -1,3 +1,3 @@
 def _local(tag: str) -> str:
     """Имя тега без пространства имён."""
-    return tag.rsplit('}', 1)[-1]
+    return tag.rsplit('}', 2)[-1]
```

### `infrastructure.remote.four_tochki_client.x__raise_on_http_status__mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/infrastructure/remote/four_tochki_client.py
+++ src/infrastructure/remote/four_tochki_client.py
@@ -1,6 +1,6 @@
 def _raise_on_http_status(reply: _HttpReply, method: str) -> None:
     """Не-2xx ответ (например, 504 с HTML от прокси) — ошибка API со статусом и началом тела."""
-    if _HTTP_STATUS_OK_FROM <= reply.status <= _HTTP_STATUS_OK_TO:
+    if _HTTP_STATUS_OK_FROM <= reply.status < _HTTP_STATUS_OK_TO:
         return
     snippet = reply.payload[:_BODY_SNIPPET_LIMIT].decode('utf-8', 'replace')
     raise FourTochkiApiError(
```

### `infrastructure.remote.four_tochki_client.x__raise_on_http_status__mutmut_7`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/infrastructure/remote/four_tochki_client.py
+++ src/infrastructure/remote/four_tochki_client.py
@@ -2,7 +2,7 @@
     """Не-2xx ответ (например, 504 с HTML от прокси) — ошибка API со статусом и началом тела."""
     if _HTTP_STATUS_OK_FROM <= reply.status <= _HTTP_STATUS_OK_TO:
         return
-    snippet = reply.payload[:_BODY_SNIPPET_LIMIT].decode('utf-8', 'replace')
+    snippet = reply.payload[:_BODY_SNIPPET_LIMIT].decode('utf-8', )
     raise FourTochkiApiError(
         detail=f'{_MSG_HTTP_STATUS} status={reply.status} {reply.reason} method={method}\n{snippet}',
     )
```

### `infrastructure.remote.four_tochki_client.x__raise_on_http_status__mutmut_9`

Классификация 2026-11-14: Эквивалент: Имена кодировки utf-8 и UTF-8 обозначают один кодек; срез тела, режим replace и сообщение ошибки сохраняются. Прогон R5 оставляет survived.

Статус: **survived**; тип: `string_case`; выбрано тестов: 3.

```diff
--- src/infrastructure/remote/four_tochki_client.py
+++ src/infrastructure/remote/four_tochki_client.py
@@ -2,7 +2,7 @@
     """Не-2xx ответ (например, 504 с HTML от прокси) — ошибка API со статусом и началом тела."""
     if _HTTP_STATUS_OK_FROM <= reply.status <= _HTTP_STATUS_OK_TO:
         return
-    snippet = reply.payload[:_BODY_SNIPPET_LIMIT].decode('utf-8', 'replace')
+    snippet = reply.payload[:_BODY_SNIPPET_LIMIT].decode('UTF-8', 'replace')
     raise FourTochkiApiError(
         detail=f'{_MSG_HTTP_STATUS} status={reply.status} {reply.reason} method={method}\n{snippet}',
     )
```

### `infrastructure.remote.four_tochki_client.x__raise_on_http_status__mutmut_10`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 3.

```diff
--- src/infrastructure/remote/four_tochki_client.py
+++ src/infrastructure/remote/four_tochki_client.py
@@ -2,7 +2,7 @@
     """Не-2xx ответ (например, 504 с HTML от прокси) — ошибка API со статусом и началом тела."""
     if _HTTP_STATUS_OK_FROM <= reply.status <= _HTTP_STATUS_OK_TO:
         return
-    snippet = reply.payload[:_BODY_SNIPPET_LIMIT].decode('utf-8', 'replace')
+    snippet = reply.payload[:_BODY_SNIPPET_LIMIT].decode('utf-8', 'XXreplaceXX')
     raise FourTochkiApiError(
         detail=f'{_MSG_HTTP_STATUS} status={reply.status} {reply.reason} method={method}\n{snippet}',
     )
```

### `infrastructure.remote.four_tochki_client.x__raise_on_http_status__mutmut_11`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 3.

```diff
--- src/infrastructure/remote/four_tochki_client.py
+++ src/infrastructure/remote/four_tochki_client.py
@@ -2,7 +2,7 @@
     """Не-2xx ответ (например, 504 с HTML от прокси) — ошибка API со статусом и началом тела."""
     if _HTTP_STATUS_OK_FROM <= reply.status <= _HTTP_STATUS_OK_TO:
         return
-    snippet = reply.payload[:_BODY_SNIPPET_LIMIT].decode('utf-8', 'replace')
+    snippet = reply.payload[:_BODY_SNIPPET_LIMIT].decode('utf-8', 'REPLACE')
     raise FourTochkiApiError(
         detail=f'{_MSG_HTTP_STATUS} status={reply.status} {reply.reason} method={method}\n{snippet}',
     )
```

## src/infrastructure/remote/mim_client.py

### `infrastructure.remote.mim_client.x__get__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 6.

```diff
--- src/infrastructure/remote/mim_client.py
+++ src/infrastructure/remote/mim_client.py
@@ -1,7 +1,7 @@
 def _get(api_config: MimApiAuth, path: str, query: str) -> bytes:
     """GET path?query; токен лежит в query-строке, поэтому в детали ошибок идут только хост и путь."""
     try:
-        with closing(HTTPSConnection(api_config.host, timeout=_TIMEOUT_SECONDS)) as connection:
+        with closing(HTTPSConnection(api_config.host, timeout=None)) as connection:
             connection.request('GET', f'{path}?{query}')
             response = connection.getresponse()
             status, body = response.status, response.read()
```

### `infrastructure.remote.mim_client.x__get__mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 6.

```diff
--- src/infrastructure/remote/mim_client.py
+++ src/infrastructure/remote/mim_client.py
@@ -1,7 +1,7 @@
 def _get(api_config: MimApiAuth, path: str, query: str) -> bytes:
     """GET path?query; токен лежит в query-строке, поэтому в детали ошибок идут только хост и путь."""
     try:
-        with closing(HTTPSConnection(api_config.host, timeout=_TIMEOUT_SECONDS)) as connection:
+        with closing(HTTPSConnection(api_config.host, )) as connection:
             connection.request('GET', f'{path}?{query}')
             response = connection.getresponse()
             status, body = response.status, response.read()
```

### `infrastructure.remote.mim_client.x_download_catalog__mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 2.

```diff
--- src/infrastructure/remote/mim_client.py
+++ src/infrastructure/remote/mim_client.py
@@ -3,7 +3,7 @@
 
     Файлы пишутся только после успешных обоих запросов: сбой не оставит прайс без списка складов.
     """
-    body = get_catalog(api)
+    body = get_catalog(None)
     territories = get_territories(api)
     dest_dir.mkdir(parents=True, exist_ok=True)
     (dest_dir / _CATALOG_FILENAME).write_bytes(body)
```

### `infrastructure.remote.mim_client.x_download_catalog__mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 2.

```diff
--- src/infrastructure/remote/mim_client.py
+++ src/infrastructure/remote/mim_client.py
@@ -4,7 +4,7 @@
     Файлы пишутся только после успешных обоих запросов: сбой не оставит прайс без списка складов.
     """
     body = get_catalog(api)
-    territories = get_territories(api)
+    territories = get_territories(None)
     dest_dir.mkdir(parents=True, exist_ok=True)
     (dest_dir / _CATALOG_FILENAME).write_bytes(body)
     (dest_dir / _TERRITORIES_FILENAME).write_bytes(territories)
```

### `infrastructure.remote.mim_client.x_resolve_types__mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R5: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 9.

```diff
--- src/infrastructure/remote/mim_client.py
+++ src/infrastructure/remote/mim_client.py
@@ -2,5 +2,5 @@
     """Категории выгрузки из настроек: без дублей, по порядку; пусто — набор по умолчанию."""
     unknown = [type_id for type_id in configured if type_id not in _KNOWN_TYPES]
     if unknown:
-        raise MimApiTypesError(_MSG_BAD_TYPES.format(value=unknown))
+        raise MimApiTypesError(_MSG_BAD_TYPES.format(value=None))
     return tuple(dict.fromkeys(configured)) or DEFAULT_TYPES
```

## src/infrastructure/remote/zapaska_client.py

### `infrastructure.remote.zapaska_client.x__request_zapaska__mutmut_21`

Классификация 2026-11-14: Эквивалент: Имена кодировки utf-8 и UTF-8 обозначают один кодек; декодированное тело ответа сохраняется. Прогон R5 оставляет survived.

Статус: **survived**; тип: `string_case`; выбрано тестов: 2.

```diff
--- src/infrastructure/remote/zapaska_client.py
+++ src/infrastructure/remote/zapaska_client.py
@@ -3,4 +3,4 @@
     with closing(HTTPSConnection(api_config.host)) as connection:
         headers = {'Authorization': basic_auth(api_config.login, api_config.password)}
         connection.request('GET', url, headers=headers)
-        return connection.getresponse().read().decode('utf-8')
+        return connection.getresponse().read().decode('UTF-8')
```

### `infrastructure.remote.zapaska_client.x_basic_auth__mutmut_5`

Классификация 2026-11-14: Эквивалент: Имена кодировки ascii и ASCII обозначают один кодек; base64 состоит из ASCII-символов, поэтому заголовок Basic сохраняется. Прогон R5 оставляет survived.

Статус: **survived**; тип: `string_case`; выбрано тестов: 3.

```diff
--- src/infrastructure/remote/zapaska_client.py
+++ src/infrastructure/remote/zapaska_client.py
@@ -1,4 +1,4 @@
 def basic_auth(username: str, password: str) -> str:
     """Basic Authorization header value."""
-    token = b64encode(f'{username}:{password}'.encode()).decode('ascii')
+    token = b64encode(f'{username}:{password}'.encode()).decode('ASCII')
     return f'Basic {token}'
```

## src/parsers/base_parser/alias_search.py

### `parsers.base_parser.alias_search.x_find_bounded__mutmut_12`

Классификация 2026-11-14: Timeout подтверждён отдельным процессом с лимитом 2 с: `find_bounded('xbrand', 'brand')`. После отклонения позиции 1 поиск возвращает -1, но условие `!= -2` продолжает цикл; проверка границ при -1 ложна, следующий поиск снова возвращает позицию 1. Исходная функция возвращает -1.

Статус: **timeout**; тип: `number`; выбрано тестов: 61.

```diff
--- src/parsers/base_parser/alias_search.py
+++ src/parsers/base_parser/alias_search.py
@@ -9,7 +9,7 @@
         return -1
     alias_len = len(lower_alias)
     position = title_lower.find(lower_alias)
-    while position != -1:
+    while position != -2:
         if _has_word_boundaries(title_lower, position, alias_len):
             return position
         position = title_lower.find(lower_alias, position + 1)
```

### `parsers.base_parser.alias_search.x_find_bounded__mutmut_21`

Классификация 2026-11-14: Timeout подтверждён отдельным процессом с лимитом 2 с на `find_bounded('xbrand', 'brand')`: повторный find без начальной позиции (или с None) снова находит позицию 1 внутри слова. Исходная функция продвигает поиск и возвращает -1.

Статус: **timeout**; тип: `other`; выбрано тестов: 61.

```diff
--- src/parsers/base_parser/alias_search.py
+++ src/parsers/base_parser/alias_search.py
@@ -12,5 +12,5 @@
     while position != -1:
         if _has_word_boundaries(title_lower, position, alias_len):
             return position
-        position = title_lower.find(lower_alias, position + 1)
+        position = title_lower.find(lower_alias, None)
     return -1
```

### `parsers.base_parser.alias_search.x_find_bounded__mutmut_23`

Классификация 2026-11-14: Timeout подтверждён отдельным процессом с лимитом 2 с на `find_bounded('xbrand', 'brand')`: повторный find без начальной позиции (или с None) снова находит позицию 1 внутри слова. Исходная функция продвигает поиск и возвращает -1.

Статус: **timeout**; тип: `other`; выбрано тестов: 61.

```diff
--- src/parsers/base_parser/alias_search.py
+++ src/parsers/base_parser/alias_search.py
@@ -12,5 +12,5 @@
     while position != -1:
         if _has_word_boundaries(title_lower, position, alias_len):
             return position
-        position = title_lower.find(lower_alias, position + 1)
+        position = title_lower.find(lower_alias, )
     return -1
```

### `parsers.base_parser.alias_search.x_find_bounded__mutmut_25`

Классификация 2026-11-14: Timeout подтверждён отдельным процессом с лимитом 2 с на `find_bounded('xbrand', 'brand')`: поиск от position - 1 снова находит ту же позицию 1 внутри слова. Исходная функция возвращает -1.

Статус: **timeout**; тип: `operator`; выбрано тестов: 61.

```diff
--- src/parsers/base_parser/alias_search.py
+++ src/parsers/base_parser/alias_search.py
@@ -12,5 +12,5 @@
     while position != -1:
         if _has_word_boundaries(title_lower, position, alias_len):
             return position
-        position = title_lower.find(lower_alias, position + 1)
+        position = title_lower.find(lower_alias, position - 1)
     return -1
```

### `parsers.base_parser.alias_search.x_find_bounded__mutmut_26`

Классификация 2026-11-14: Подтверждённый пробел теста: `find_bounded('a++ ', '+')` должен вернуть 2. Первое вхождение в позиции 1 отвергается из-за буквы слева, соседнее в позиции 2 допустимо. Шаг +2 пропускает его. Небуквенные алиасы не запрещены контрактом AliasContainer; `test_find_symbol_alias_after_rejected_occurrence` закрепляет этот случай. Убит прогоном `uv run mutmut run 'parsers.base_parser.alias_search.x_find_bounded__mutmut_26'`.

Статус: **survived**; тип: `number`; выбрано тестов: 61.

```diff
--- src/parsers/base_parser/alias_search.py
+++ src/parsers/base_parser/alias_search.py
@@ -12,5 +12,5 @@
     while position != -1:
         if _has_word_boundaries(title_lower, position, alias_len):
             return position
-        position = title_lower.find(lower_alias, position + 1)
+        position = title_lower.find(lower_alias, position + 2)
     return -1
```

### `parsers.base_parser.alias_search.x_find_bracket_alias__mutmut_13`

Классификация 2026-11-14: Пробел теста закрыт: `test_bracket_alias_preserves_exact_supplier_spelling` проверяет оба элемента результата при смещениях 0, 1 и 10; `test_absent_bracket_alias_allows_regular_manufacturer` проверяет отсутствие составного алиаса. Убит прогоном `uv run mutmut run 'parsers.base_parser.alias_search.*' 'parsers.base_parser.base_finder.*'`.

Статус: **survived**; тип: `operator`; выбрано тестов: 88.

```diff
--- src/parsers/base_parser/alias_search.py
+++ src/parsers/base_parser/alias_search.py
@@ -9,6 +9,6 @@
     lower = title.lower()
     for alias in bracket_aliases:
         position = find_bounded(lower, alias)
-        if position != -1:
+        if position != +1:
             return correct_by_alias[alias], title[position : position + len(alias)]
     return None
```

### `parsers.base_parser.alias_search.x_find_bracket_alias__mutmut_14`

Классификация 2026-11-14: Пробел теста закрыт: `test_bracket_alias_preserves_exact_supplier_spelling` проверяет оба элемента результата при смещениях 0, 1 и 10; `test_absent_bracket_alias_allows_regular_manufacturer` проверяет отсутствие составного алиаса. Убит прогоном `uv run mutmut run 'parsers.base_parser.alias_search.*' 'parsers.base_parser.base_finder.*'`.

Статус: **survived**; тип: `number`; выбрано тестов: 88.

```diff
--- src/parsers/base_parser/alias_search.py
+++ src/parsers/base_parser/alias_search.py
@@ -9,6 +9,6 @@
     lower = title.lower()
     for alias in bracket_aliases:
         position = find_bounded(lower, alias)
-        if position != -1:
+        if position != -2:
             return correct_by_alias[alias], title[position : position + len(alias)]
     return None
```

### `parsers.base_parser.alias_search.x_find_bracket_alias__mutmut_15`

Классификация 2026-11-14: Пробел теста закрыт: `test_bracket_alias_preserves_exact_supplier_spelling` проверяет оба элемента результата при смещениях 0, 1 и 10; `test_absent_bracket_alias_allows_regular_manufacturer` проверяет отсутствие составного алиаса. Убит прогоном `uv run mutmut run 'parsers.base_parser.alias_search.*' 'parsers.base_parser.base_finder.*'`.

Статус: **survived**; тип: `operator`; выбрано тестов: 88.

```diff
--- src/parsers/base_parser/alias_search.py
+++ src/parsers/base_parser/alias_search.py
@@ -10,5 +10,5 @@
     for alias in bracket_aliases:
         position = find_bounded(lower, alias)
         if position != -1:
-            return correct_by_alias[alias], title[position : position + len(alias)]
+            return correct_by_alias[alias], title[position : position - len(alias)]
     return None
```

## src/parsers/base_parser/base_finder.py

### `parsers.base_parser.base_finder.xǁBaseFinderǁ__init____mutmut_2`

Классификация 2026-11-14: Эквивалент через публичный API: `_search` присваивает `_title = title` до любого чтения в `_match_lower_alias`; при попадании в кэш `_title` не читается. Начальное None или пустая строка ненаблюдаемы. Целевой прогон оставляет survived.

Статус: **survived**; тип: `none_to_empty`; выбрано тестов: 90.

```diff
--- src/parsers/base_parser/base_finder.py
+++ src/parsers/base_parser/base_finder.py
@@ -1,7 +1,7 @@
     def __init__(self, alias_container: AliasContainer) -> None:
         """init"""
         self.alias_container = alias_container
-        self._title: str | None = None
+        self._title: str | None = ""
         self._title_lower: str | None = None
         self._found: dict[str | None, tuple[str | None, str | None]] = {}
         self._incorrect_lowers: list[str] = self.alias_container.incorrect_words_lower
```

### `parsers.base_parser.base_finder.xǁBaseFinderǁ_match_lower_alias__mutmut_16`

Классификация 2026-11-14: Пробел теста закрыт: `test_unbounded_alias_allows_next_manufacturer` проверяет Bridgestoneish перед Nortec. Bridgestone длиннее и проверяется первым; его вхождение внутри слова должно пропускаться с продолжением перебора. Убит прогоном `uv run mutmut run 'parsers.base_parser.base_finder.*'`.

Статус: **survived**; тип: `keyword`; выбрано тестов: 87.

```diff
--- src/parsers/base_parser/base_finder.py
+++ src/parsers/base_parser/base_finder.py
@@ -12,7 +12,7 @@
                 continue
             found_position = find_bounded(title_lower, lower_alias)
             if found_position == -1:
-                continue
+                break
             return (
                 lower_alias,
                 title[found_position : found_position + len(lower_alias)],
```

### `parsers.base_parser.base_finder.xǁBaseFinderǁ_search__mutmut_9`

Классификация 2026-11-14: Эквивалент: `haystacks` всегда возвращает непустой кортеж (один или два элемента), а каждая итерация присваивает found до break и return. Начальное значение перезаписывается. Целевой прогон оставляет survived.

Статус: **survived**; тип: `to_none`; выбрано тестов: 88.

```diff
--- src/parsers/base_parser/base_finder.py
+++ src/parsers/base_parser/base_finder.py
@@ -4,7 +4,7 @@
         bracketed = find_bracket_alias(title, self._bracket_aliases, self._aliases)
         if bracketed:
             return bracketed
-        found: tuple[str | None, str | None] = (None, None)
+        found: tuple[str | None, str | None] = None
         for haystack in haystacks(title):
             self._title_lower = haystack.lower() if haystack else haystack
             correct, incorrect = self._find_from_lower_list(self._correct_lowers, return_correct=True)
```

### `parsers.base_parser.base_finder.xǁBaseFinderǁ_search__mutmut_25`

Классификация 2026-11-14: Не классифицирован окончательно. Для непустых канонических имён найденное совпадение имеет одновременно непустые correct и исходный алиас; отсутствие совпадения даёт (None, None), поэтому условия совпадают. Но AliasContainer не запрещает пустое каноническое имя с непустым алиасом: прежде чем объявлять эквивалентность, требуется установить допустимость такого конфига. Целевой прогон оставляет survived.

Статус: **survived**; тип: `number`; выбрано тестов: 88.

```diff
--- src/parsers/base_parser/base_finder.py
+++ src/parsers/base_parser/base_finder.py
@@ -9,6 +9,6 @@
             self._title_lower = haystack.lower() if haystack else haystack
             correct, incorrect = self._find_from_lower_list(self._correct_lowers, return_correct=True)
             found = (correct, incorrect) if correct else self._find_from_lower_list(self._incorrect_lowers)
-            if found[0]:
+            if found[1]:
                 break
         return found
```

## src/parsers/base_parser/base_parser.py

### `parsers.base_parser.base_parser.xǁBaseParserǁ__init____mutmut_2`

Статус: **survived**; тип: `to_none`; выбрано тестов: 79.

```diff
--- src/parsers/base_parser/base_parser.py
+++ src/parsers/base_parser/base_parser.py
@@ -9,7 +9,7 @@
         group_handler: TireAndDiskHandler | None = None,
     ) -> None:
         self.parsed_items: list[RowItem] = []
-        self._package = TireAndDiskResult()
+        self._package = None
         self.settings = group_handler.settings if group_handler else ParserSettings(parse_config)
         self._logger = LoggerParseProcess(f'{self!r} [tire_and_disk]')
         self.stats = group_handler.stats if group_handler else ParserStats()
```

### `parsers.base_parser.base_parser.xǁBaseParserǁ__init____mutmut_15`

Статус: **survived**; тип: `other`; выбрано тестов: 79.

```diff
--- src/parsers/base_parser/base_parser.py
+++ src/parsers/base_parser/base_parser.py
@@ -16,7 +16,7 @@
         self.price_files = PriceFiles(
             self.settings.parser_params(),
             file_reader or _default_file_reader(self.settings, data_reader),
-            self.settings.parse_config().routing,
+            None,
         )
         self.group_handler = group_handler or TireAndDiskHandler(
             settings=self.settings,
```

### `parsers.base_parser.base_parser.xǁBaseParserǁ__init____mutmut_18`

Статус: **survived**; тип: `other`; выбрано тестов: 79.

```diff
--- src/parsers/base_parser/base_parser.py
+++ src/parsers/base_parser/base_parser.py
@@ -16,8 +16,7 @@
         self.price_files = PriceFiles(
             self.settings.parser_params(),
             file_reader or _default_file_reader(self.settings, data_reader),
-            self.settings.parse_config().routing,
-        )
+            )
         self.group_handler = group_handler or TireAndDiskHandler(
             settings=self.settings,
             stats=self.stats,
```

### `parsers.base_parser.base_parser.xǁBaseParserǁ__init____mutmut_29`

Статус: **survived**; тип: `to_none`; выбрано тестов: 79.

```diff
--- src/parsers/base_parser/base_parser.py
+++ src/parsers/base_parser/base_parser.py
@@ -22,7 +22,7 @@
             settings=self.settings,
             stats=self.stats,
             row_processor=row_processor,
-            title_filter=title_filter,
+            title_filter=None,
         )
         self.row_filters = self.group_handler.row_filters
         self.enricher = self.group_handler.enricher
```

### `parsers.base_parser.base_parser.xǁBaseParserǁ__init____mutmut_33`

Статус: **survived**; тип: `other`; выбрано тестов: 79.

```diff
--- src/parsers/base_parser/base_parser.py
+++ src/parsers/base_parser/base_parser.py
@@ -22,8 +22,7 @@
             settings=self.settings,
             stats=self.stats,
             row_processor=row_processor,
-            title_filter=title_filter,
-        )
+            )
         self.row_filters = self.group_handler.row_filters
         self.enricher = self.group_handler.enricher
         self.pipeline = self.group_handler.pipeline
```

### `parsers.base_parser.base_parser.x__default_file_reader__mutmut_1`

Статус: **survived**; тип: `to_none`; выбрано тестов: 75.

```diff
--- src/parsers/base_parser/base_parser.py
+++ src/parsers/base_parser/base_parser.py
@@ -1,4 +1,4 @@
 def _default_file_reader(settings: ParserSettings, data_reader: type[Any] | None) -> FileReader:
     """Читатель прайсов с источником файлов на диске, путь к которому даёт провайдер конфига."""
-    price_source = FilePricesSource(settings.parse_config().config_provider)
+    price_source = None
     return FileReader(data_reader=data_reader, price_source=price_source)
```

### `parsers.base_parser.base_parser.x__default_file_reader__mutmut_2`

Статус: **survived**; тип: `other`; выбрано тестов: 75.

```diff
--- src/parsers/base_parser/base_parser.py
+++ src/parsers/base_parser/base_parser.py
@@ -1,4 +1,4 @@
 def _default_file_reader(settings: ParserSettings, data_reader: type[Any] | None) -> FileReader:
     """Читатель прайсов с источником файлов на диске, путь к которому даёт провайдер конфига."""
-    price_source = FilePricesSource(settings.parse_config().config_provider)
+    price_source = FilePricesSource(None)
     return FileReader(data_reader=data_reader, price_source=price_source)
```

### `parsers.base_parser.base_parser.x__default_file_reader__mutmut_4`

Статус: **survived**; тип: `to_none`; выбрано тестов: 75.

```diff
--- src/parsers/base_parser/base_parser.py
+++ src/parsers/base_parser/base_parser.py
@@ -1,4 +1,4 @@
 def _default_file_reader(settings: ParserSettings, data_reader: type[Any] | None) -> FileReader:
     """Читатель прайсов с источником файлов на диске, путь к которому даёт провайдер конфига."""
     price_source = FilePricesSource(settings.parse_config().config_provider)
-    return FileReader(data_reader=data_reader, price_source=price_source)
+    return FileReader(data_reader=data_reader, price_source=None)
```

### `parsers.base_parser.base_parser.x_make_parser__mutmut_2`

Статус: **survived**; тип: `other`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/base_parser.py
+++ src/parsers/base_parser/base_parser.py
@@ -7,7 +7,7 @@
     data_reader: type[Any] | None = None,
 ) -> TParser:
     """Собрать парсер с политикой наценки. Не метод BaseParser."""
-    policy = make_markup_policy(parse_config) if markup_policy is None else markup_policy
+    policy = make_markup_policy(parse_config) if (markup_policy is None) and False else markup_policy
     kwargs: dict[str, Any] = {
         'parse_config': parse_config,
         'row_processor': RowProcessor(markup_policy=policy),
```

## src/parsers/base_parser/base_parser_config.py

### `parsers.base_parser.base_parser_config.xǁParseConfigurationǁ__init____mutmut_6`

Статус: **survived**; тип: `to_none`; выбрано тестов: 99.

```diff
--- src/parsers/base_parser/base_parser_config.py
+++ src/parsers/base_parser/base_parser_config.py
@@ -9,7 +9,7 @@
         self.vendor_section = vendor_section
         self.vendor_config = vendor_config
         self.product_group = vendor_section.product_group if vendor_section else None
-        self.routing = routing
+        self.routing = None
         self.parse_config: BasePriceParseConfigurationParams = parse_config
         self.parser_params = parse_config.parser_params
         self.config_provider = parse_config.config_provider
```

### `parsers.base_parser.base_parser_config.xǁParseConfigurationǁ__init____mutmut_9`

Статус: **survived**; тип: `to_none`; выбрано тестов: 99.

```diff
--- src/parsers/base_parser/base_parser_config.py
+++ src/parsers/base_parser/base_parser_config.py
@@ -12,7 +12,7 @@
         self.routing = routing
         self.parse_config: BasePriceParseConfigurationParams = parse_config
         self.parser_params = parse_config.parser_params
-        self.config_provider = parse_config.config_provider
+        self.config_provider = None
         self.supplier = self.parser_params.supplier
         self._markup_rules: data_provider.MarkupRulesConfig | None = None
         self._price_markup_map: tuple[data_provider.MarkUpRule, ...] | None = None
```

### `parsers.base_parser.base_parser_config.x_make_parse_config__mutmut_5`

Статус: **survived**; тип: `to_none`; выбрано тестов: 28.

```diff
--- src/parsers/base_parser/base_parser_config.py
+++ src/parsers/base_parser/base_parser_config.py
@@ -19,5 +19,5 @@
         ),
         vendor_section,
         vendor_config,
-        routing,
+        None,
     )
```

### `parsers.base_parser.base_parser_config.x_make_parse_config__mutmut_9`

Статус: **survived**; тип: `other`; выбрано тестов: 28.

```diff
--- src/parsers/base_parser/base_parser_config.py
+++ src/parsers/base_parser/base_parser_config.py
@@ -19,5 +19,4 @@
         ),
         vendor_section,
         vendor_config,
-        routing,
-    )
+        )
```

### `parsers.base_parser.base_parser_config.x_make_parse_config__mutmut_13`

Статус: **survived**; тип: `to_none`; выбрано тестов: 28.

```diff
--- src/parsers/base_parser/base_parser_config.py
+++ src/parsers/base_parser/base_parser_config.py
@@ -14,7 +14,7 @@
             markup_rules_provider=data_provider.MarkupRulesProviderFromUserConfig(config_provider, folder_name),
             black_list_provider=black_list_provider or data_provider.BlackListProviderFromUserConfig(config_provider),
             manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(config_provider),
-            config_provider=config_provider,
+            config_provider=None,
             parser_params=parser_params,
         ),
         vendor_section,
```

### `parsers.base_parser.base_parser_config.x_make_parse_config__mutmut_20`

Статус: **survived**; тип: `to_none`; выбрано тестов: 28.

```diff
--- src/parsers/base_parser/base_parser_config.py
+++ src/parsers/base_parser/base_parser_config.py
@@ -11,7 +11,7 @@
     folder_name = parser_params.supplier.folder_name
     return ParseConfiguration(
         BasePriceParseConfigurationParams(
-            markup_rules_provider=data_provider.MarkupRulesProviderFromUserConfig(config_provider, folder_name),
+            markup_rules_provider=data_provider.MarkupRulesProviderFromUserConfig(None, folder_name),
             black_list_provider=black_list_provider or data_provider.BlackListProviderFromUserConfig(config_provider),
             manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(config_provider),
             config_provider=config_provider,
```

## src/parsers/base_parser/category_finder.py

### `parsers.base_parser.category_finder.x_skipped_unknown_categories_message__mutmut_3`

Статус: **survived**; тип: `to_none`; выбрано тестов: 49.

```diff
--- src/parsers/base_parser/category_finder.py
+++ src/parsers/base_parser/category_finder.py
@@ -2,7 +2,7 @@
     """Summary of rows skipped because the supplier category is unknown."""
     if not skips:
         return None
-    suppliers, categories = zip(*skips, strict=True)
+    suppliers, categories = zip(*skips, strict=None)
     return _MSG_SKIPPED_CATEGORIES.format(
         count=len(skips),
         suppliers=_joined_unique(suppliers),
```

### `parsers.base_parser.category_finder.x_skipped_unknown_categories_message__mutmut_5`

Статус: **survived**; тип: `other`; выбрано тестов: 49.

```diff
--- src/parsers/base_parser/category_finder.py
+++ src/parsers/base_parser/category_finder.py
@@ -2,7 +2,7 @@
     """Summary of rows skipped because the supplier category is unknown."""
     if not skips:
         return None
-    suppliers, categories = zip(*skips, strict=True)
+    suppliers, categories = zip(*skips, )
     return _MSG_SKIPPED_CATEGORIES.format(
         count=len(skips),
         suppliers=_joined_unique(suppliers),
```

### `parsers.base_parser.category_finder.x_skipped_unknown_categories_message__mutmut_6`

Статус: **survived**; тип: `keyword`; выбрано тестов: 49.

```diff
--- src/parsers/base_parser/category_finder.py
+++ src/parsers/base_parser/category_finder.py
@@ -2,7 +2,7 @@
     """Summary of rows skipped because the supplier category is unknown."""
     if not skips:
         return None
-    suppliers, categories = zip(*skips, strict=True)
+    suppliers, categories = zip(*skips, strict=False)
     return _MSG_SKIPPED_CATEGORIES.format(
         count=len(skips),
         suppliers=_joined_unique(suppliers),
```

## src/parsers/base_parser/category_service.py

### `parsers.base_parser.category_service.xǁCategoryLookupǁfind_canonical_category__mutmut_3`

Статус: **survived**; тип: `to_none`; выбрано тестов: 1.

```diff
--- src/parsers/base_parser/category_service.py
+++ src/parsers/base_parser/category_service.py
@@ -2,4 +2,4 @@
         """Сопоставить категорию поставщика известному типу (CategoryContext)."""
         if self._finder is None:
             self._finder = CategoryFinder()
-        return self._finder.find_canonical(raw_type)
+        return self._finder.find_canonical(None)
```

### `parsers.base_parser.category_service.xǁCategoryServiceǁzero_rest_without_category__mutmut_6`

Статус: **survived**; тип: `to_none`; выбрано тестов: 18.

```diff
--- src/parsers/base_parser/category_service.py
+++ src/parsers/base_parser/category_service.py
@@ -1,4 +1,4 @@
     def zero_rest_without_category(self, row_item: RowItem) -> None:
         """Обнулить остаток строки без категории, чтобы она не попала в прайс."""
         if self._hooks is not None and self._hooks.zero_rest_without_category and not row_item.vendor.type_production:
-            row_item.set_field('rest_count', 0)
+            row_item.set_field('rest_count', None)
```

## src/parsers/base_parser/config_driven_parser.py

### `parsers.base_parser.config_driven_parser.x_make_config_driven_parser__mutmut_1`

Статус: **survived**; тип: `to_none`; выбрано тестов: 3.

```diff
--- src/parsers/base_parser/config_driven_parser.py
+++ src/parsers/base_parser/config_driven_parser.py
@@ -5,7 +5,7 @@
 ) -> BaseParser:
     """Собрать ``BaseParser`` с обработчиком выбранной товарной группы."""
     return BaseParser(
-        parse_config=parse_config,
+        parse_config=None,
         group_handler=make_tire_and_disk_handler(section, vendor_config, parse_config),
         data_reader=data_reader_for(vendor_config.reader),
     )
```

### `parsers.base_parser.config_driven_parser.x_make_config_driven_parser__mutmut_4`

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/parsers/base_parser/config_driven_parser.py
+++ src/parsers/base_parser/config_driven_parser.py
@@ -5,7 +5,6 @@
 ) -> BaseParser:
     """Собрать ``BaseParser`` с обработчиком выбранной товарной группы."""
     return BaseParser(
-        parse_config=parse_config,
         group_handler=make_tire_and_disk_handler(section, vendor_config, parse_config),
         data_reader=data_reader_for(vendor_config.reader),
     )
```

### `parsers.base_parser.config_driven_parser.x_make_tire_and_disk_handler__mutmut_4`

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/parsers/base_parser/config_driven_parser.py
+++ src/parsers/base_parser/config_driven_parser.py
@@ -4,7 +4,7 @@
     parse_config: ParseConfiguration,
 ) -> TireAndDiskHandler:
     """Собрать модель, стратегии и pipeline группы шин и дисков."""
-    hooks = strategy_hooks_from_section(section, section.behavior, parse_config.config_provider, vendor_config.folder)
+    hooks = strategy_hooks_from_section(section, section.behavior, None, vendor_config.folder)
     policy = vendor_markup_policy_from_config(section)
     return make_handler(
         parse_config,
```

### `parsers.base_parser.config_driven_parser.x_make_tire_and_disk_handler__mutmut_5`

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/parsers/base_parser/config_driven_parser.py
+++ src/parsers/base_parser/config_driven_parser.py
@@ -4,7 +4,7 @@
     parse_config: ParseConfiguration,
 ) -> TireAndDiskHandler:
     """Собрать модель, стратегии и pipeline группы шин и дисков."""
-    hooks = strategy_hooks_from_section(section, section.behavior, parse_config.config_provider, vendor_config.folder)
+    hooks = strategy_hooks_from_section(section, section.behavior, parse_config.config_provider, None)
     policy = vendor_markup_policy_from_config(section)
     return make_handler(
         parse_config,
```

### `parsers.base_parser.config_driven_parser.x_make_tire_and_disk_handler__mutmut_8`

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/parsers/base_parser/config_driven_parser.py
+++ src/parsers/base_parser/config_driven_parser.py
@@ -4,7 +4,7 @@
     parse_config: ParseConfiguration,
 ) -> TireAndDiskHandler:
     """Собрать модель, стратегии и pipeline группы шин и дисков."""
-    hooks = strategy_hooks_from_section(section, section.behavior, parse_config.config_provider, vendor_config.folder)
+    hooks = strategy_hooks_from_section(section, section.behavior, vendor_config.folder)
     policy = vendor_markup_policy_from_config(section)
     return make_handler(
         parse_config,
```

### `parsers.base_parser.config_driven_parser.x_make_tire_and_disk_handler__mutmut_9`

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/parsers/base_parser/config_driven_parser.py
+++ src/parsers/base_parser/config_driven_parser.py
@@ -4,7 +4,7 @@
     parse_config: ParseConfiguration,
 ) -> TireAndDiskHandler:
     """Собрать модель, стратегии и pipeline группы шин и дисков."""
-    hooks = strategy_hooks_from_section(section, section.behavior, parse_config.config_provider, vendor_config.folder)
+    hooks = strategy_hooks_from_section(section, section.behavior, parse_config.config_provider, )
     policy = vendor_markup_policy_from_config(section)
     return make_handler(
         parse_config,
```

### `parsers.base_parser.config_driven_parser.x_strategy_hooks_from_section__mutmut_21`

Статус: **survived**; тип: `other`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/config_driven_parser.py
+++ src/parsers/base_parser/config_driven_parser.py
@@ -28,7 +28,7 @@
         product_type=_product_type(section),
         min_rest=behavior.min_rest,
         find_manufacturer_on_enrich=behavior.find_manufacturer_on_enrich,
-        manufacturer_column_first=behavior.manufacturer_column_first,
+        manufacturer_column_first=None,
         zero_rest_without_category=behavior.zero_rest_without_category,
         pipeline=behavior.pipeline,
         warehouse_filter=warehouse_filter_for(behavior, folder, config_provider),
```

### `parsers.base_parser.config_driven_parser.x_strategy_hooks_from_section__mutmut_25`

Статус: **survived**; тип: `other`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/config_driven_parser.py
+++ src/parsers/base_parser/config_driven_parser.py
@@ -32,5 +32,5 @@
         zero_rest_without_category=behavior.zero_rest_without_category,
         pipeline=behavior.pipeline,
         warehouse_filter=warehouse_filter_for(behavior, folder, config_provider),
-        order_from_warehouse_name=behavior.order_from_warehouse_name,
+        order_from_warehouse_name=None,
     )
```

### `parsers.base_parser.config_driven_parser.x_strategy_hooks_from_section__mutmut_33`

Статус: **survived**; тип: `other`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/config_driven_parser.py
+++ src/parsers/base_parser/config_driven_parser.py
@@ -28,7 +28,6 @@
         product_type=_product_type(section),
         min_rest=behavior.min_rest,
         find_manufacturer_on_enrich=behavior.find_manufacturer_on_enrich,
-        manufacturer_column_first=behavior.manufacturer_column_first,
         zero_rest_without_category=behavior.zero_rest_without_category,
         pipeline=behavior.pipeline,
         warehouse_filter=warehouse_filter_for(behavior, folder, config_provider),
```

### `parsers.base_parser.config_driven_parser.x_strategy_hooks_from_section__mutmut_37`

Статус: **survived**; тип: `other`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/config_driven_parser.py
+++ src/parsers/base_parser/config_driven_parser.py
@@ -32,5 +32,4 @@
         zero_rest_without_category=behavior.zero_rest_without_category,
         pipeline=behavior.pipeline,
         warehouse_filter=warehouse_filter_for(behavior, folder, config_provider),
-        order_from_warehouse_name=behavior.order_from_warehouse_name,
-    )
+        )
```

### `parsers.base_parser.config_driven_parser.x_strategy_hooks_from_section__mutmut_41`

Статус: **survived**; тип: `to_none`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/config_driven_parser.py
+++ src/parsers/base_parser/config_driven_parser.py
@@ -20,7 +20,7 @@
             section.title,
             f'section {section.id} title',
             manufacturer_reader=manufacturer_reader,
-            config_provider=config_provider,
+            config_provider=None,
             column_first=behavior.manufacturer_column_first,
         ),
         rest=make_rest_strategy(behavior, f'section {section.id} rest'),
```

### `parsers.base_parser.config_driven_parser.x_strategy_hooks_from_section__mutmut_42`

Статус: **survived**; тип: `other`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/config_driven_parser.py
+++ src/parsers/base_parser/config_driven_parser.py
@@ -21,7 +21,7 @@
             f'section {section.id} title',
             manufacturer_reader=manufacturer_reader,
             config_provider=config_provider,
-            column_first=behavior.manufacturer_column_first,
+            column_first=None,
         ),
         rest=make_rest_strategy(behavior, f'section {section.id} rest'),
         category_fields=_category_fields(section),
```

### `parsers.base_parser.config_driven_parser.x_strategy_hooks_from_section__mutmut_47`

Статус: **survived**; тип: `other`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/config_driven_parser.py
+++ src/parsers/base_parser/config_driven_parser.py
@@ -21,8 +21,7 @@
             f'section {section.id} title',
             manufacturer_reader=manufacturer_reader,
             config_provider=config_provider,
-            column_first=behavior.manufacturer_column_first,
-        ),
+            ),
         rest=make_rest_strategy(behavior, f'section {section.id} rest'),
         category_fields=_category_fields(section),
         product_type=_product_type(section),
```

### `parsers.base_parser.config_driven_parser.x_strategy_hooks_from_section__mutmut_55`

Статус: **survived**; тип: `to_none`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/config_driven_parser.py
+++ src/parsers/base_parser/config_driven_parser.py
@@ -31,6 +31,6 @@
         manufacturer_column_first=behavior.manufacturer_column_first,
         zero_rest_without_category=behavior.zero_rest_without_category,
         pipeline=behavior.pipeline,
-        warehouse_filter=warehouse_filter_for(behavior, folder, config_provider),
+        warehouse_filter=warehouse_filter_for(behavior, None, config_provider),
         order_from_warehouse_name=behavior.order_from_warehouse_name,
     )
```

### `parsers.base_parser.config_driven_parser.x_strategy_hooks_from_section__mutmut_56`

Статус: **survived**; тип: `to_none`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/config_driven_parser.py
+++ src/parsers/base_parser/config_driven_parser.py
@@ -31,6 +31,6 @@
         manufacturer_column_first=behavior.manufacturer_column_first,
         zero_rest_without_category=behavior.zero_rest_without_category,
         pipeline=behavior.pipeline,
-        warehouse_filter=warehouse_filter_for(behavior, folder, config_provider),
+        warehouse_filter=warehouse_filter_for(behavior, folder, None),
         order_from_warehouse_name=behavior.order_from_warehouse_name,
     )
```

## src/parsers/base_parser/file_reader.py

### `parsers.base_parser.file_reader.xǁFileReaderǁraw_tables__mutmut_8`

Статус: **survived**; тип: `number`; выбрано тестов: 6.

```diff
--- src/parsers/base_parser/file_reader.py
+++ src/parsers/base_parser/file_reader.py
@@ -1,5 +1,5 @@
     def raw_tables(self, path: str, sheet_indexes: Sequence[int]) -> list[RawTable]:
-        reader = self.data_reader.get_instance(path, {'start_row': 0, 'columns': {}})
+        reader = self.data_reader.get_instance(path, {'start_row': 1, 'columns': {}})
         if isinstance(reader, XlsReader):
             return read_xls_raw_tables(reader, sheet_indexes)
         if isinstance(reader, JsonPriceReader):
```

## src/parsers/base_parser/manufacturer_finder.py

### `parsers.base_parser.manufacturer_finder.xǁManufacturerFinderǁprocess__mutmut_1`

Статус: **survived**; тип: `keyword`; выбрано тестов: 35.

```diff
--- src/parsers/base_parser/manufacturer_finder.py
+++ src/parsers/base_parser/manufacturer_finder.py
@@ -1,4 +1,4 @@
-    def process(self, row_item: RowItem, column_first: bool = False) -> None:
+    def process(self, row_item: RowItem, column_first: bool = True) -> None:
         """Поставить производителя; ``column_first`` — колонка приоритетнее названия, название — если колонка пуста."""
 
         if column_first and row_item.identity.manufacturer:
```

## src/parsers/base_parser/manufacturer_service.py

### `parsers.base_parser.manufacturer_service.xǁManufacturerServiceǁapply_manufacturer__mutmut_9`

Статус: **survived**; тип: `other`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/manufacturer_service.py
+++ src/parsers/base_parser/manufacturer_service.py
@@ -1,3 +1,3 @@
     def apply_manufacturer(self, row_item: RowItem) -> None:
         find_on_enrich = True if self._hooks is None else self._hooks.find_manufacturer_on_enrich
-        apply_manufacturer(row_item, find_on_enrich, self._settings.manufacturer_finder(), self._column_first())
+        apply_manufacturer(row_item, find_on_enrich, self._settings.manufacturer_finder(), None)
```

### `parsers.base_parser.manufacturer_service.xǁManufacturerServiceǁapply_manufacturer__mutmut_13`

Статус: **survived**; тип: `other`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/manufacturer_service.py
+++ src/parsers/base_parser/manufacturer_service.py
@@ -1,3 +1,3 @@
     def apply_manufacturer(self, row_item: RowItem) -> None:
         find_on_enrich = True if self._hooks is None else self._hooks.find_manufacturer_on_enrich
-        apply_manufacturer(row_item, find_on_enrich, self._settings.manufacturer_finder(), self._column_first())
+        apply_manufacturer(row_item, find_on_enrich, self._settings.manufacturer_finder(), )
```

## src/parsers/base_parser/markup_policy.py

### `parsers.base_parser.markup_policy.xǁMarkupPolicyǁapply__mutmut_23`

Статус: **survived**; тип: `to_none`; выбрано тестов: 18.

```diff
--- src/parsers/base_parser/markup_policy.py
+++ src/parsers/base_parser/markup_policy.py
@@ -9,7 +9,7 @@
         ):
             price = get_markup(opt, self.markup_percent_for_opt(opt))
 
-        if self._is_big_recommended_percent(opt, price_recommended) and not price_recommended:
+        if self._is_big_recommended_percent(opt, None) and not price_recommended:
             price = get_markup(opt, self._rules.max_recommended_percent_markup)
 
         if self._is_small_absolute_markup(price, opt):
```

## src/parsers/base_parser/routing.py

### `parsers.base_parser.routing.xǁVendorRoutingǁ__init____mutmut_6`

Статус: **survived**; тип: `none_to_empty`; выбрано тестов: 29.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -2,7 +2,7 @@
         self._config = config
         self._sections = tuple(section for group in config.product_groups for section in group.sections)
         self._section_params = {section.id: self._params_for(section) for section in self._sections}
-        self._reader: FileReaderProtocol | None = None
+        self._reader: FileReaderProtocol | None = ""
         self._paths: dict[str, str] = {}
         self._path_sections: dict[str, list[RouteSection]] = defaultdict(list)
         self._section_paths: dict[str, list[str]] = defaultdict(list)
```

### `parsers.base_parser.routing.xǁVendorRoutingǁ__init____mutmut_14`

Статус: **survived**; тип: `to_none`; выбрано тестов: 29.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -7,6 +7,6 @@
         self._path_sections: dict[str, list[RouteSection]] = defaultdict(list)
         self._section_paths: dict[str, list[str]] = defaultdict(list)
         self._section_rows: SectionRows = defaultdict(list)
-        self._resolved = False
+        self._resolved = None
         self._routed = False
         self._unrouted_rows = 0
```

### `parsers.base_parser.routing.xǁVendorRoutingǁ__init____mutmut_16`

Статус: **survived**; тип: `to_none`; выбрано тестов: 29.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -8,5 +8,5 @@
         self._section_paths: dict[str, list[str]] = defaultdict(list)
         self._section_rows: SectionRows = defaultdict(list)
         self._resolved = False
-        self._routed = False
+        self._routed = None
         self._unrouted_rows = 0
```

### `parsers.base_parser.routing.xǁVendorRoutingǁ__init____mutmut_18`

Статус: **survived**; тип: `to_none`; выбрано тестов: 29.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -9,4 +9,4 @@
         self._section_rows: SectionRows = defaultdict(list)
         self._resolved = False
         self._routed = False
-        self._unrouted_rows = 0
+        self._unrouted_rows = None
```

### `parsers.base_parser.routing.xǁVendorRoutingǁ__init____mutmut_19`

Статус: **survived**; тип: `number`; выбрано тестов: 29.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -9,4 +9,4 @@
         self._section_rows: SectionRows = defaultdict(list)
         self._resolved = False
         self._routed = False
-        self._unrouted_rows = 0
+        self._unrouted_rows = 1
```

### `parsers.base_parser.routing.xǁVendorRoutingǁ_params_for__mutmut_1`

Статус: **survived**; тип: `other`; выбрано тестов: 29.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -1,6 +1,6 @@
     def _params_for(self, section: RouteSection) -> ParserParams:
         return ParserParams(
-            supplier=ParseParamsSupplier(folder_name=self._config.folder, name=section.name, code=section.id),
+            supplier=None,
             start_row=section.start_row,
             sheet_info=section.sheet_info,
             columns=dict(section.columns),
```

### `parsers.base_parser.routing.xǁVendorRoutingǁ_params_for__mutmut_2`

Статус: **survived**; тип: `other`; выбрано тестов: 29.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -1,7 +1,7 @@
     def _params_for(self, section: RouteSection) -> ParserParams:
         return ParserParams(
             supplier=ParseParamsSupplier(folder_name=self._config.folder, name=section.name, code=section.id),
-            start_row=section.start_row,
+            start_row=None,
             sheet_info=section.sheet_info,
             columns=dict(section.columns),
             stop_words=(),
```

### `parsers.base_parser.routing.xǁVendorRoutingǁ_params_for__mutmut_3`

Статус: **survived**; тип: `other`; выбрано тестов: 29.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -2,7 +2,7 @@
         return ParserParams(
             supplier=ParseParamsSupplier(folder_name=self._config.folder, name=section.name, code=section.id),
             start_row=section.start_row,
-            sheet_info=section.sheet_info,
+            sheet_info=None,
             columns=dict(section.columns),
             stop_words=(),
             file_templates=section.file_templates,
```

### `parsers.base_parser.routing.xǁVendorRoutingǁ_params_for__mutmut_5`

Статус: **survived**; тип: `to_none`; выбрано тестов: 29.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -4,7 +4,7 @@
             start_row=section.start_row,
             sheet_info=section.sheet_info,
             columns=dict(section.columns),
-            stop_words=(),
+            stop_words=None,
             file_templates=section.file_templates,
             sheet_indexes=section.sheet_indexes,
         )
```

### `parsers.base_parser.routing.xǁVendorRoutingǁ_params_for__mutmut_6`

Статус: **survived**; тип: `other`; выбрано тестов: 29.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -5,6 +5,6 @@
             sheet_info=section.sheet_info,
             columns=dict(section.columns),
             stop_words=(),
-            file_templates=section.file_templates,
+            file_templates=None,
             sheet_indexes=section.sheet_indexes,
         )
```

### `parsers.base_parser.routing.xǁVendorRoutingǁ_params_for__mutmut_7`

Статус: **survived**; тип: `other`; выбрано тестов: 29.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -6,5 +6,5 @@
             columns=dict(section.columns),
             stop_words=(),
             file_templates=section.file_templates,
-            sheet_indexes=section.sheet_indexes,
+            sheet_indexes=None,
         )
```

### `parsers.base_parser.routing.xǁVendorRoutingǁ_params_for__mutmut_15`

Статус: **survived**; тип: `other`; выбрано тестов: 29.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -1,6 +1,6 @@
     def _params_for(self, section: RouteSection) -> ParserParams:
         return ParserParams(
-            supplier=ParseParamsSupplier(folder_name=self._config.folder, name=section.name, code=section.id),
+            supplier=ParseParamsSupplier(folder_name=None, name=section.name, code=section.id),
             start_row=section.start_row,
             sheet_info=section.sheet_info,
             columns=dict(section.columns),
```

### `parsers.base_parser.routing.xǁVendorRoutingǁ_params_for__mutmut_16`

Статус: **survived**; тип: `other`; выбрано тестов: 29.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -1,6 +1,6 @@
     def _params_for(self, section: RouteSection) -> ParserParams:
         return ParserParams(
-            supplier=ParseParamsSupplier(folder_name=self._config.folder, name=section.name, code=section.id),
+            supplier=ParseParamsSupplier(folder_name=self._config.folder, name=None, code=section.id),
             start_row=section.start_row,
             sheet_info=section.sheet_info,
             columns=dict(section.columns),
```

### `parsers.base_parser.routing.xǁVendorRoutingǁ_params_for__mutmut_17`

Статус: **survived**; тип: `other`; выбрано тестов: 29.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -1,6 +1,6 @@
     def _params_for(self, section: RouteSection) -> ParserParams:
         return ParserParams(
-            supplier=ParseParamsSupplier(folder_name=self._config.folder, name=section.name, code=section.id),
+            supplier=ParseParamsSupplier(folder_name=self._config.folder, name=section.name, code=None),
             start_row=section.start_row,
             sheet_info=section.sheet_info,
             columns=dict(section.columns),
```

### `parsers.base_parser.routing.xǁVendorRoutingǁ_remember_paths__mutmut_1`

Статус: **survived**; тип: `to_none`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -1,6 +1,6 @@
     def _remember_paths(self, section: RouteSection, paths: list[str]) -> None:
         for path in paths:
-            canonical = str(Path(path).resolve())
+            canonical = None
             self._paths.setdefault(canonical, path)
             if section not in self._path_sections[canonical]:
                 self._path_sections[canonical].append(section)
```

### `parsers.base_parser.routing.xǁVendorRoutingǁ_remember_paths__mutmut_2`

Статус: **survived**; тип: `to_none`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -1,6 +1,6 @@
     def _remember_paths(self, section: RouteSection, paths: list[str]) -> None:
         for path in paths:
-            canonical = str(Path(path).resolve())
+            canonical = str(None)
             self._paths.setdefault(canonical, path)
             if section not in self._path_sections[canonical]:
                 self._path_sections[canonical].append(section)
```

### `parsers.base_parser.routing.xǁVendorRoutingǁresolve__mutmut_5`

Статус: **survived**; тип: `other`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -8,7 +8,7 @@
         if not self._resolved:
             self._reader = reader
             for section in self._sections:
-                paths = given_files or reader.price_files(self._section_params[section.id])
+                paths = given_files or reader.price_files(None)
                 self._remember_paths(section, paths)
             self._resolved = True
         files = self._section_paths[section_id]
```

### `parsers.base_parser.routing.xǁVendorRoutingǁresolve__mutmut_10`

Статус: **survived**; тип: `to_none`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -10,7 +10,7 @@
             for section in self._sections:
                 paths = given_files or reader.price_files(self._section_params[section.id])
                 self._remember_paths(section, paths)
-            self._resolved = True
+            self._resolved = None
         files = self._section_paths[section_id]
         if not files:
             supplier_name = self._section_params[section_id].supplier.name
```

### `parsers.base_parser.routing.xǁVendorRoutingǁresolve__mutmut_11`

Статус: **survived**; тип: `keyword`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -10,7 +10,7 @@
             for section in self._sections:
                 paths = given_files or reader.price_files(self._section_params[section.id])
                 self._remember_paths(section, paths)
-            self._resolved = True
+            self._resolved = False
         files = self._section_paths[section_id]
         if not files:
             supplier_name = self._section_params[section_id].supplier.name
```

### `parsers.base_parser.routing.x__assign_row__mutmut_9`

Статус: **survived**; тип: `to_none`; выбрано тестов: 10.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -8,7 +8,7 @@
 ) -> bool:
     matched = [section for section in sections if matches(section, row)]
     if len(matched) > 1:
-        raise_ambiguous(config, path, table, row, matched)
+        raise_ambiguous(config, None, table, row, matched)
     if not matched:
         return False
     section_rows[matched[0].id].append(row)
```

### `parsers.base_parser.routing.x__route_file__mutmut_9`

Статус: **survived**; тип: `to_none`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -7,5 +7,5 @@
 ) -> int:
     sheet_indexes = tuple(sorted({index for section in sections for index in section.sheet_indexes}))
     tables = reader.raw_tables(path, sheet_indexes)
-    ensure_sheet_indexes(path, sections, tables)
+    ensure_sheet_indexes(None, sections, tables)
     return sum(_route_table(config, path, sections, table, section_rows) for table in tables)
```

### `parsers.base_parser.routing.x__route_table__mutmut_7`

Статус: **survived**; тип: `to_none`; выбрано тестов: 13.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -8,7 +8,7 @@
     sections = [section for section in file_sections if selects_table(section, table)]
     if not sections:
         return 0
-    validate_table(path, table, sections)
+    validate_table(None, table, sections)
     unrouted = 0
     for row, candidates in section_candidates(table, sections):
         if not _assign_row(config, path, table, row, candidates, section_rows):
```

### `parsers.base_parser.routing.x__route_table__mutmut_21`

Статус: **survived**; тип: `to_none`; выбрано тестов: 13.

```diff
--- src/parsers/base_parser/routing.py
+++ src/parsers/base_parser/routing.py
@@ -11,7 +11,7 @@
     validate_table(path, table, sections)
     unrouted = 0
     for row, candidates in section_candidates(table, sections):
-        if not _assign_row(config, path, table, row, candidates, section_rows):
+        if not _assign_row(config, None, table, row, candidates, section_rows):
             unrouted += 1
     if unrouted:
         log_unrouted(config, path, table, unrouted)
```

## src/parsers/base_parser/routing_rows.py

### `parsers.base_parser.routing_rows.x_log_unrouted__mutmut_2`

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/parsers/base_parser/routing_rows.py
+++ src/parsers/base_parser/routing_rows.py
@@ -1,5 +1,5 @@
 def log_unrouted(config: VendorConfig, path: str, table: RawTable, unrouted: int) -> None:
-    sheet = 'JSON' if table.sheet_index is None else str(table.sheet_index + 1)
+    sheet = 'JSON' if (table.sheet_index is None) and False else str(table.sheet_index + 1)
     logger.warning(
         '%s: файл %s, лист %s: пропущено строк — %d (не подходят под настройки отбора разделов или товаров)',
         config.name,
```

### `parsers.base_parser.routing_rows.x_log_unrouted__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 2.

```diff
--- src/parsers/base_parser/routing_rows.py
+++ src/parsers/base_parser/routing_rows.py
@@ -1,5 +1,5 @@
 def log_unrouted(config: VendorConfig, path: str, table: RawTable, unrouted: int) -> None:
-    sheet = 'JSON' if table.sheet_index is None else str(table.sheet_index + 1)
+    sheet = 'XXJSONXX' if table.sheet_index is None else str(table.sheet_index + 1)
     logger.warning(
         '%s: файл %s, лист %s: пропущено строк — %d (не подходят под настройки отбора разделов или товаров)',
         config.name,
```

### `parsers.base_parser.routing_rows.x_log_unrouted__mutmut_5`

Статус: **survived**; тип: `string_case`; выбрано тестов: 2.

```diff
--- src/parsers/base_parser/routing_rows.py
+++ src/parsers/base_parser/routing_rows.py
@@ -1,5 +1,5 @@
 def log_unrouted(config: VendorConfig, path: str, table: RawTable, unrouted: int) -> None:
-    sheet = 'JSON' if table.sheet_index is None else str(table.sheet_index + 1)
+    sheet = 'json' if table.sheet_index is None else str(table.sheet_index + 1)
     logger.warning(
         '%s: файл %s, лист %s: пропущено строк — %d (не подходят под настройки отбора разделов или товаров)',
         config.name,
```

### `parsers.base_parser.routing_rows.x_raise_ambiguous__mutmut_3`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 2.

```diff
--- src/parsers/base_parser/routing_rows.py
+++ src/parsers/base_parser/routing_rows.py
@@ -5,7 +5,7 @@
     row: RawRow,
     sections: list[RouteSection],
 ) -> None:
-    routes = ', '.join(f'{section.id} ({section.product_group})' for section in sections)
+    routes = 'XX, XX'.join(f'{section.id} ({section.product_group})' for section in sections)
     sheet = 'JSON' if table.sheet_index is None else str(table.sheet_index)
     location = f'Поставщик {config.folder}, файл {path}'
     row_location = f'лист {sheet}, строка {row.row_number}'
```

### `parsers.base_parser.routing_rows.x_raise_ambiguous__mutmut_4`

Статус: **survived**; тип: `to_none`; выбрано тестов: 2.

```diff
--- src/parsers/base_parser/routing_rows.py
+++ src/parsers/base_parser/routing_rows.py
@@ -6,7 +6,7 @@
     sections: list[RouteSection],
 ) -> None:
     routes = ', '.join(f'{section.id} ({section.product_group})' for section in sections)
-    sheet = 'JSON' if table.sheet_index is None else str(table.sheet_index)
+    sheet = None
     location = f'Поставщик {config.folder}, файл {path}'
     row_location = f'лист {sheet}, строка {row.row_number}'
     raise RowRoutingError(f'{location}, {row_location}: неоднозначная маршрутизация — {routes}')
```

### `parsers.base_parser.routing_rows.x_raise_ambiguous__mutmut_5`

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/parsers/base_parser/routing_rows.py
+++ src/parsers/base_parser/routing_rows.py
@@ -6,7 +6,7 @@
     sections: list[RouteSection],
 ) -> None:
     routes = ', '.join(f'{section.id} ({section.product_group})' for section in sections)
-    sheet = 'JSON' if table.sheet_index is None else str(table.sheet_index)
+    sheet = 'JSON' if (table.sheet_index is None) and False else str(table.sheet_index)
     location = f'Поставщик {config.folder}, файл {path}'
     row_location = f'лист {sheet}, строка {row.row_number}'
     raise RowRoutingError(f'{location}, {row_location}: неоднозначная маршрутизация — {routes}')
```

### `parsers.base_parser.routing_rows.x_raise_ambiguous__mutmut_6`

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/parsers/base_parser/routing_rows.py
+++ src/parsers/base_parser/routing_rows.py
@@ -6,7 +6,7 @@
     sections: list[RouteSection],
 ) -> None:
     routes = ', '.join(f'{section.id} ({section.product_group})' for section in sections)
-    sheet = 'JSON' if table.sheet_index is None else str(table.sheet_index)
+    sheet = 'JSON' if (table.sheet_index is None) or True else str(table.sheet_index)
     location = f'Поставщик {config.folder}, файл {path}'
     row_location = f'лист {sheet}, строка {row.row_number}'
     raise RowRoutingError(f'{location}, {row_location}: неоднозначная маршрутизация — {routes}')
```

### `parsers.base_parser.routing_rows.x_raise_ambiguous__mutmut_7`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 2.

```diff
--- src/parsers/base_parser/routing_rows.py
+++ src/parsers/base_parser/routing_rows.py
@@ -6,7 +6,7 @@
     sections: list[RouteSection],
 ) -> None:
     routes = ', '.join(f'{section.id} ({section.product_group})' for section in sections)
-    sheet = 'JSON' if table.sheet_index is None else str(table.sheet_index)
+    sheet = 'XXJSONXX' if table.sheet_index is None else str(table.sheet_index)
     location = f'Поставщик {config.folder}, файл {path}'
     row_location = f'лист {sheet}, строка {row.row_number}'
     raise RowRoutingError(f'{location}, {row_location}: неоднозначная маршрутизация — {routes}')
```

### `parsers.base_parser.routing_rows.x_raise_ambiguous__mutmut_8`

Статус: **survived**; тип: `string_case`; выбрано тестов: 2.

```diff
--- src/parsers/base_parser/routing_rows.py
+++ src/parsers/base_parser/routing_rows.py
@@ -6,7 +6,7 @@
     sections: list[RouteSection],
 ) -> None:
     routes = ', '.join(f'{section.id} ({section.product_group})' for section in sections)
-    sheet = 'JSON' if table.sheet_index is None else str(table.sheet_index)
+    sheet = 'json' if table.sheet_index is None else str(table.sheet_index)
     location = f'Поставщик {config.folder}, файл {path}'
     row_location = f'лист {sheet}, строка {row.row_number}'
     raise RowRoutingError(f'{location}, {row_location}: неоднозначная маршрутизация — {routes}')
```

### `parsers.base_parser.routing_rows.x_raise_ambiguous__mutmut_9`

Статус: **survived**; тип: `operator`; выбрано тестов: 2.

```diff
--- src/parsers/base_parser/routing_rows.py
+++ src/parsers/base_parser/routing_rows.py
@@ -6,7 +6,7 @@
     sections: list[RouteSection],
 ) -> None:
     routes = ', '.join(f'{section.id} ({section.product_group})' for section in sections)
-    sheet = 'JSON' if table.sheet_index is None else str(table.sheet_index)
+    sheet = 'JSON' if table.sheet_index is not None else str(table.sheet_index)
     location = f'Поставщик {config.folder}, файл {path}'
     row_location = f'лист {sheet}, строка {row.row_number}'
     raise RowRoutingError(f'{location}, {row_location}: неоднозначная маршрутизация — {routes}')
```

### `parsers.base_parser.routing_rows.x_raise_ambiguous__mutmut_10`

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/parsers/base_parser/routing_rows.py
+++ src/parsers/base_parser/routing_rows.py
@@ -6,7 +6,7 @@
     sections: list[RouteSection],
 ) -> None:
     routes = ', '.join(f'{section.id} ({section.product_group})' for section in sections)
-    sheet = 'JSON' if table.sheet_index is None else str(table.sheet_index)
+    sheet = 'JSON' if table.sheet_index is None else str(None)
     location = f'Поставщик {config.folder}, файл {path}'
     row_location = f'лист {sheet}, строка {row.row_number}'
     raise RowRoutingError(f'{location}, {row_location}: неоднозначная маршрутизация — {routes}')
```

### `parsers.base_parser.routing_rows.x_raise_ambiguous__mutmut_11`

Статус: **survived**; тип: `to_none`; выбрано тестов: 2.

```diff
--- src/parsers/base_parser/routing_rows.py
+++ src/parsers/base_parser/routing_rows.py
@@ -7,6 +7,6 @@
 ) -> None:
     routes = ', '.join(f'{section.id} ({section.product_group})' for section in sections)
     sheet = 'JSON' if table.sheet_index is None else str(table.sheet_index)
-    location = f'Поставщик {config.folder}, файл {path}'
+    location = None
     row_location = f'лист {sheet}, строка {row.row_number}'
     raise RowRoutingError(f'{location}, {row_location}: неоднозначная маршрутизация — {routes}')
```

## src/parsers/base_parser/routing_validation.py

### `parsers.base_parser.routing_validation.x__selector_overlap__mutmut_1`

Статус: **survived**; тип: `operator`; выбрано тестов: 5.

```diff
--- src/parsers/base_parser/routing_validation.py
+++ src/parsers/base_parser/routing_validation.py
@@ -1,5 +1,5 @@
 def _selector_overlap(first: RouteSection, second: RouteSection) -> set[str]:
-    if first.row_selector is None or second.row_selector is None:
+    if first.row_selector is None and second.row_selector is None:
         return set()
     first_selector = first.row_selector
     second_selector = second.row_selector
```

### `parsers.base_parser.routing_validation.x__validate_required_selectors__mutmut_10`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 12.

```diff
--- src/parsers/base_parser/routing_validation.py
+++ src/parsers/base_parser/routing_validation.py
@@ -3,5 +3,5 @@
     if len(sections) > 1 and missing:
         raise ConfigValidationError(
             f'Общий лист {path}, {table.sheet_index}: каждая секция должна задать row_selector или section_selector; '
-            + ', '.join(section.config_path for section in sections)
+            + 'XX, XX'.join(section.config_path for section in sections)
         )
```

### `parsers.base_parser.routing_validation.x_validate_table__mutmut_1`

Статус: **survived**; тип: `to_none`; выбрано тестов: 13.

```diff
--- src/parsers/base_parser/routing_validation.py
+++ src/parsers/base_parser/routing_validation.py
@@ -1,4 +1,4 @@
 def validate_table(path: str, table: RawTable, sections: list[RouteSection]) -> None:
-    _validate_start_row(path, table, sections)
+    _validate_start_row(None, table, sections)
     _validate_required_selectors(path, table, sections)
     _validate_selector_overlaps(sections)
```

### `parsers.base_parser.routing_validation.x_validate_table__mutmut_7`

Статус: **survived**; тип: `to_none`; выбрано тестов: 13.

```diff
--- src/parsers/base_parser/routing_validation.py
+++ src/parsers/base_parser/routing_validation.py
@@ -1,4 +1,4 @@
 def validate_table(path: str, table: RawTable, sections: list[RouteSection]) -> None:
     _validate_start_row(path, table, sections)
-    _validate_required_selectors(path, table, sections)
+    _validate_required_selectors(None, table, sections)
     _validate_selector_overlaps(sections)
```

## src/parsers/base_parser/row_enricher.py

### `parsers.base_parser.row_enricher.xǁRowEnricherǁ_try_prepare_row__mutmut_3`

Статус: **survived**; тип: `operator`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/row_enricher.py
+++ src/parsers/base_parser/row_enricher.py
@@ -1,7 +1,7 @@
     def _try_prepare_row(self, row_id: int, row_item: RowItem) -> RowItem | None:
         """Подготовить одну строку или вернуть None при ошибке/фильтре."""
         homoglyphs = fix_row_homoglyphs(row_item)
-        self._stats.homoglyph_fixes += len(homoglyphs.fixed)
+        self._stats.homoglyph_fixes = len(homoglyphs.fixed)
         self._stats.homoglyph_suspects += len(homoglyphs.suspects)
         if not self._set_title_or_log(row_id, row_item):
             return None
```

### `parsers.base_parser.row_enricher.xǁRowEnricherǁ_try_prepare_row__mutmut_4`

Статус: **survived**; тип: `operator`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/row_enricher.py
+++ src/parsers/base_parser/row_enricher.py
@@ -1,7 +1,7 @@
     def _try_prepare_row(self, row_id: int, row_item: RowItem) -> RowItem | None:
         """Подготовить одну строку или вернуть None при ошибке/фильтре."""
         homoglyphs = fix_row_homoglyphs(row_item)
-        self._stats.homoglyph_fixes += len(homoglyphs.fixed)
+        self._stats.homoglyph_fixes -= len(homoglyphs.fixed)
         self._stats.homoglyph_suspects += len(homoglyphs.suspects)
         if not self._set_title_or_log(row_id, row_item):
             return None
```

### `parsers.base_parser.row_enricher.xǁRowEnricherǁ_try_prepare_row__mutmut_5`

Статус: **survived**; тип: `operator`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/row_enricher.py
+++ src/parsers/base_parser/row_enricher.py
@@ -2,7 +2,7 @@
         """Подготовить одну строку или вернуть None при ошибке/фильтре."""
         homoglyphs = fix_row_homoglyphs(row_item)
         self._stats.homoglyph_fixes += len(homoglyphs.fixed)
-        self._stats.homoglyph_suspects += len(homoglyphs.suspects)
+        self._stats.homoglyph_suspects = len(homoglyphs.suspects)
         if not self._set_title_or_log(row_id, row_item):
             return None
         if row_item.parse_errors:
```

### `parsers.base_parser.row_enricher.xǁRowEnricherǁ_try_prepare_row__mutmut_6`

Статус: **survived**; тип: `operator`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/row_enricher.py
+++ src/parsers/base_parser/row_enricher.py
@@ -2,7 +2,7 @@
         """Подготовить одну строку или вернуть None при ошибке/фильтре."""
         homoglyphs = fix_row_homoglyphs(row_item)
         self._stats.homoglyph_fixes += len(homoglyphs.fixed)
-        self._stats.homoglyph_suspects += len(homoglyphs.suspects)
+        self._stats.homoglyph_suspects -= len(homoglyphs.suspects)
         if not self._set_title_or_log(row_id, row_item):
             return None
         if row_item.parse_errors:
```

### `parsers.base_parser.row_enricher.xǁRowEnricherǁ_try_prepare_row__mutmut_12`

Статус: **survived**; тип: `other`; выбрано тестов: 14.

```diff
--- src/parsers/base_parser/row_enricher.py
+++ src/parsers/base_parser/row_enricher.py
@@ -6,7 +6,7 @@
         if not self._set_title_or_log(row_id, row_item):
             return None
         if row_item.parse_errors:
-            _log_row_parse_errors(self._settings.title(), row_id, row_item)
+            _log_row_parse_errors(None, row_id, row_item)
             return None
         if not self.titles.is_valid_title(row_item.identity.title):
             if row_item.identity.title:
```

### `parsers.base_parser.row_enricher.x_make_row_enricher__mutmut_21`

Статус: **survived**; тип: `to_none`; выбрано тестов: 82.

```diff
--- src/parsers/base_parser/row_enricher.py
+++ src/parsers/base_parser/row_enricher.py
@@ -8,7 +8,7 @@
     return RowEnricher(
         settings,
         TitleService(hooks, title_filter or TitleFilter(settings.parse_config())),
-        CategoryService(hooks, CategoryLookup(stats)),
+        CategoryService(hooks, CategoryLookup(None)),
         ManufacturerService(settings, hooks),
         stats,
     )
```

## src/parsers/base_parser/row_pipeline.py

### `parsers.base_parser.row_pipeline.xǁRowPipelineǁprocess_row__mutmut_6`

Статус: **survived**; тип: `to_none`; выбрано тестов: 23.

```diff
--- src/parsers/base_parser/row_pipeline.py
+++ src/parsers/base_parser/row_pipeline.py
@@ -10,6 +10,6 @@
         if self.hooks is None:
             self._run_steps(_DEFAULT_STEPS, row_item)
             return
-        self.row_filters.apply_warehouse_order(row_item)
+        self.row_filters.apply_warehouse_order(None)
         self._run_steps(self.hooks.pipeline, row_item)
         self.enricher.manufacturers.apply_manufacturer_after_pipeline(row_item)
```

## src/parsers/base_parser/row_processor.py

### `parsers.base_parser.row_processor.x_apply_min_rest__mutmut_5`

Статус: **survived**; тип: `to_none`; выбрано тестов: 16.

```diff
--- src/parsers/base_parser/row_processor.py
+++ src/parsers/base_parser/row_processor.py
@@ -1,4 +1,4 @@
 def apply_min_rest(row_item: RowItem, rest: Any, min_rest: int) -> None:
     """Обнулить остаток, если он меньше минимального."""
     if rest is None or rest < min_rest:
-        row_item.set_field('rest_count', 0)
+        row_item.set_field('rest_count', None)
```

## src/parsers/base_parser/section_selection.py

### `parsers.base_parser.section_selection.xǁSectionSelectionǁ__init____mutmut_2`

Статус: **survived**; тип: `to_none`; выбрано тестов: 15.

```diff
--- src/parsers/base_parser/section_selection.py
+++ src/parsers/base_parser/section_selection.py
@@ -1,3 +1,3 @@
     def __init__(self, selector: SectionSelector | None) -> None:
         self._selector = selector
-        self._selected = False
+        self._selected = None
```

### `parsers.base_parser.section_selection.xǁSectionSelectionǁaccepts__mutmut_14`

Статус: **survived**; тип: `none_to_empty`; выбрано тестов: 15.

```diff
--- src/parsers/base_parser/section_selection.py
+++ src/parsers/base_parser/section_selection.py
@@ -7,7 +7,7 @@
         if not isinstance(title, str) or not title.strip():
             return False
         other_fields = dict(row.fields)
-        other_fields.pop(selector.column, None)
+        other_fields.pop(selector.column, )
         if any(cell not in ('', None) for cell in other_fields.values()):
             return self._selected
         if title == title.lstrip():
```

### `parsers.base_parser.section_selection.x__selected_sections__mutmut_4`

Статус: **survived**; тип: `to_none`; выбрано тестов: 10.

```diff
--- src/parsers/base_parser/section_selection.py
+++ src/parsers/base_parser/section_selection.py
@@ -2,7 +2,7 @@
     row: RawRow, sections: list[RouteSection], selections: list[SectionSelection]
 ) -> list[RouteSection]:
     selected = []
-    for section, selection in zip(sections, selections, strict=True):
+    for section, selection in zip(sections, selections, strict=None):
         if selection.accepts(row):
             selected.append(section)
     return selected
```

### `parsers.base_parser.section_selection.x__selected_sections__mutmut_7`

Статус: **survived**; тип: `other`; выбрано тестов: 10.

```diff
--- src/parsers/base_parser/section_selection.py
+++ src/parsers/base_parser/section_selection.py
@@ -2,7 +2,7 @@
     row: RawRow, sections: list[RouteSection], selections: list[SectionSelection]
 ) -> list[RouteSection]:
     selected = []
-    for section, selection in zip(sections, selections, strict=True):
+    for section, selection in zip(sections, selections, ):
         if selection.accepts(row):
             selected.append(section)
     return selected
```

### `parsers.base_parser.section_selection.x__selected_sections__mutmut_8`

Статус: **survived**; тип: `keyword`; выбрано тестов: 10.

```diff
--- src/parsers/base_parser/section_selection.py
+++ src/parsers/base_parser/section_selection.py
@@ -2,7 +2,7 @@
     row: RawRow, sections: list[RouteSection], selections: list[SectionSelection]
 ) -> list[RouteSection]:
     selected = []
-    for section, selection in zip(sections, selections, strict=True):
+    for section, selection in zip(sections, selections, strict=False):
         if selection.accepts(row):
             selected.append(section)
     return selected
```

## src/parsers/base_parser/strategy_hooks.py

### `parsers.base_parser.strategy_hooks.x_warehouse_filter_for__mutmut_2`

Статус: **survived**; тип: `to_none`; выбрано тестов: 11.

```diff
--- src/parsers/base_parser/strategy_hooks.py
+++ src/parsers/base_parser/strategy_hooks.py
@@ -4,4 +4,4 @@
     """Фильтр складов по городам, если они заданы в `behavior.warehouse_cities`."""
     if not behavior.warehouse_cities:
         return None
-    return CityWarehouseFilter(folder=folder, cities=behavior.warehouse_cities, config_provider=config_provider)
+    return CityWarehouseFilter(folder=None, cities=behavior.warehouse_cities, config_provider=config_provider)
```

### `parsers.base_parser.strategy_hooks.x_warehouse_filter_for__mutmut_3`

Статус: **survived**; тип: `other`; выбрано тестов: 11.

```diff
--- src/parsers/base_parser/strategy_hooks.py
+++ src/parsers/base_parser/strategy_hooks.py
@@ -4,4 +4,4 @@
     """Фильтр складов по городам, если они заданы в `behavior.warehouse_cities`."""
     if not behavior.warehouse_cities:
         return None
-    return CityWarehouseFilter(folder=folder, cities=behavior.warehouse_cities, config_provider=config_provider)
+    return CityWarehouseFilter(folder=folder, cities=None, config_provider=config_provider)
```

### `parsers.base_parser.strategy_hooks.x_warehouse_filter_for__mutmut_4`

Статус: **survived**; тип: `to_none`; выбрано тестов: 11.

```diff
--- src/parsers/base_parser/strategy_hooks.py
+++ src/parsers/base_parser/strategy_hooks.py
@@ -4,4 +4,4 @@
     """Фильтр складов по городам, если они заданы в `behavior.warehouse_cities`."""
     if not behavior.warehouse_cities:
         return None
-    return CityWarehouseFilter(folder=folder, cities=behavior.warehouse_cities, config_provider=config_provider)
+    return CityWarehouseFilter(folder=folder, cities=behavior.warehouse_cities, config_provider=None)
```

## src/parsers/base_parser/tire_and_disk_handler.py

### `parsers.base_parser.tire_and_disk_handler.xǁTireAndDiskHandlerǁ__init____mutmut_10`

Статус: **survived**; тип: `to_none`; выбрано тестов: 82.

```diff
--- src/parsers/base_parser/tire_and_disk_handler.py
+++ src/parsers/base_parser/tire_and_disk_handler.py
@@ -11,6 +11,6 @@
         self.settings = settings
         self.stats = stats or ParserStats()
         self.row_filters = RowFilters(strategy_hooks)
-        self.enricher = make_row_enricher(self.settings, self.stats, strategy_hooks, title_filter)
+        self.enricher = make_row_enricher(self.settings, self.stats, strategy_hooks, None)
         self.pipeline = RowPipeline(strategy_hooks, self.row_filters, self.enricher, row_processor or RowProcessor())
         self._grouper_factory = grouper_factory or CommonPriceGrouper
```

### `parsers.base_parser.tire_and_disk_handler.xǁTireAndDiskHandlerǁ__init____mutmut_14`

Статус: **survived**; тип: `other`; выбрано тестов: 82.

```diff
--- src/parsers/base_parser/tire_and_disk_handler.py
+++ src/parsers/base_parser/tire_and_disk_handler.py
@@ -11,6 +11,6 @@
         self.settings = settings
         self.stats = stats or ParserStats()
         self.row_filters = RowFilters(strategy_hooks)
-        self.enricher = make_row_enricher(self.settings, self.stats, strategy_hooks, title_filter)
+        self.enricher = make_row_enricher(self.settings, self.stats, strategy_hooks, )
         self.pipeline = RowPipeline(strategy_hooks, self.row_filters, self.enricher, row_processor or RowProcessor())
         self._grouper_factory = grouper_factory or CommonPriceGrouper
```

## src/parsers/base_parser/title_filter.py

### `parsers.base_parser.title_filter.xǁTitleFilterǁis_valid_title__mutmut_6`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 21.

```diff
--- src/parsers/base_parser/title_filter.py
+++ src/parsers/base_parser/title_filter.py
@@ -1,2 +1,2 @@
     def is_valid_title(self, title: str | None) -> bool:
-        return bool(title) and not self._block_list.blocks(title or '')
+        return bool(title) and not self._block_list.blocks(title or 'XXXX')
```

## src/parsers/base_parser/title_service.py

### `parsers.base_parser.title_service.xǁTitleServiceǁset_prepared_title__mutmut_24`

Статус: **survived**; тип: `other`; выбрано тестов: 23.

```diff
--- src/parsers/base_parser/title_service.py
+++ src/parsers/base_parser/title_service.py
@@ -6,7 +6,7 @@
         if source_title and prepared_title and not title_is_prepared:
             row_item.set_field('source_title', source_title)
         row_item.set_field('title', prepared_title or source_title)
-        if is_markdown_title(source_title) or is_markdown_title(row_item.identity.title):
+        if is_markdown_title(source_title) or is_markdown_title(None):
             row_item.set_field('marked_down', True)
         year = production_year(source_title) or production_year(row_item.identity.title)
         if year:
```

### `parsers.base_parser.title_service.xǁTitleServiceǁset_prepared_title__mutmut_35`

Статус: **survived**; тип: `other`; выбрано тестов: 23.

```diff
--- src/parsers/base_parser/title_service.py
+++ src/parsers/base_parser/title_service.py
@@ -8,7 +8,7 @@
         row_item.set_field('title', prepared_title or source_title)
         if is_markdown_title(source_title) or is_markdown_title(row_item.identity.title):
             row_item.set_field('marked_down', True)
-        year = production_year(source_title) or production_year(row_item.identity.title)
+        year = production_year(source_title) or production_year(None)
         if year:
             row_item.set_field('production_year', year)
         plant = production_plant(source_title) or production_plant(row_item.identity.title)
```

### `parsers.base_parser.title_service.xǁTitleServiceǁset_prepared_title__mutmut_45`

Статус: **survived**; тип: `other`; выбрано тестов: 23.

```diff
--- src/parsers/base_parser/title_service.py
+++ src/parsers/base_parser/title_service.py
@@ -11,7 +11,7 @@
         year = production_year(source_title) or production_year(row_item.identity.title)
         if year:
             row_item.set_field('production_year', year)
-        plant = production_plant(source_title) or production_plant(row_item.identity.title)
+        plant = production_plant(source_title) or production_plant(None)
         if plant:
             row_item.set_field('production_plant', plant)
         return title_is_prepared
```

## src/parsers/base_parser/warehouse_filter.py

### `parsers.base_parser.warehouse_filter.xǁCityWarehouseFilterǁ_load_ids__mutmut_7`

Статус: **survived**; тип: `to_none`; выбрано тестов: 18.

```diff
--- src/parsers/base_parser/warehouse_filter.py
+++ src/parsers/base_parser/warehouse_filter.py
@@ -1,7 +1,7 @@
     def _load_ids(self) -> frozenset[int]:
         path = Path(self._config_provider.price_folder(self._folder)) / TERRITORIES_FILENAME
         if not path.is_file():
-            raise WarehouseFilterError(_MSG_NO_FILE.format(path=path))
+            raise WarehouseFilterError(_MSG_NO_FILE.format(path=None))
         matchers = [_city_pattern(city) for city in self._cities]
         allowed = frozenset(
             int(territory['id']) for territory in _read_territories(path) if _in_cities(territory, matchers)
```

### `parsers.base_parser.warehouse_filter.xǁCityWarehouseFilterǁ_load_ids__mutmut_22`

Статус: **survived**; тип: `to_none`; выбрано тестов: 18.

```diff
--- src/parsers/base_parser/warehouse_filter.py
+++ src/parsers/base_parser/warehouse_filter.py
@@ -7,5 +7,5 @@
             int(territory['id']) for territory in _read_territories(path) if _in_cities(territory, matchers)
         )
         if not allowed:
-            raise WarehouseFilterError(_MSG_NO_MATCH.format(path=path, cities=', '.join(self._cities)))
+            raise WarehouseFilterError(_MSG_NO_MATCH.format(path=None, cities=', '.join(self._cities)))
         return allowed
```

### `parsers.base_parser.warehouse_filter.xǁCityWarehouseFilterǁ_load_ids__mutmut_27`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 18.

```diff
--- src/parsers/base_parser/warehouse_filter.py
+++ src/parsers/base_parser/warehouse_filter.py
@@ -7,5 +7,5 @@
             int(territory['id']) for territory in _read_territories(path) if _in_cities(territory, matchers)
         )
         if not allowed:
-            raise WarehouseFilterError(_MSG_NO_MATCH.format(path=path, cities=', '.join(self._cities)))
+            raise WarehouseFilterError(_MSG_NO_MATCH.format(path=path, cities='XX, XX'.join(self._cities)))
         return allowed
```

### `parsers.base_parser.warehouse_filter.x__read_territories__mutmut_2`

Статус: **survived**; тип: `to_none`; выбрано тестов: 17.

```diff
--- src/parsers/base_parser/warehouse_filter.py
+++ src/parsers/base_parser/warehouse_filter.py
@@ -2,4 +2,4 @@
     try:
         return [_normalized(territory) for territory in json.loads(path.read_text(encoding='utf-8'))]
     except (ValueError, KeyError, TypeError) as exc:
-        raise WarehouseFilterError(_MSG_BAD_FILE.format(path=path)) from exc
+        raise WarehouseFilterError(_MSG_BAD_FILE.format(path=None)) from exc
```

## src/parsers/base_parser/warehouse_order.py

### `parsers.base_parser.warehouse_order.x_apply_warehouse_order__mutmut_3`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 7.

```diff
--- src/parsers/base_parser/warehouse_order.py
+++ src/parsers/base_parser/warehouse_order.py
@@ -1,6 +1,6 @@
 def apply_warehouse_order(row_item: RowItem) -> None:
     """Склад «под заказ»: наличие «Под заказ» и срок доставки в днях, если он указан в названии."""
-    name = row_item.stock.warehouse_name or ''
+    name = row_item.stock.warehouse_name or 'XXXX'
     if not _ORDER_MARKER.search(name):
         return
     row_item.set_field('available', ORDER_AVAILABLE)
```

## src/parsers/battery/group_keys.py

### `parsers.battery.group_keys.x_normalized__mutmut_3`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 38.

```diff
--- src/parsers/battery/group_keys.py
+++ src/parsers/battery/group_keys.py
@@ -1,5 +1,5 @@
 def normalized(part: object) -> object:
     """Сравнить строки без регистра и лишних пробелов, сохранив числа и bool."""
     if isinstance(part, str):
-        return ' '.join(part.split()).casefold() or None
+        return 'XX XX'.join(part.split()).casefold() or None
     return part
```

### `parsers.battery.group_keys.x_resolve_optional__mutmut_4`

Статус: **survived**; тип: `to_none`; выбрано тестов: 38.

```diff
--- src/parsers/battery/group_keys.py
+++ src/parsers/battery/group_keys.py
@@ -1,4 +1,4 @@
 def resolve_optional(key: BatteryKey, variants: list[set[object]]) -> BatteryKey:
     """Подставить единственный вариант только в сравнительный ключ, не в позицию."""
-    compared = zip(key, variants, strict=True)
+    compared = zip(key, variants, strict=None)
     return tuple(resolve_part(part, known) for part, known in compared)
```

### `parsers.battery.group_keys.x_resolve_optional__mutmut_7`

Статус: **survived**; тип: `other`; выбрано тестов: 38.

```diff
--- src/parsers/battery/group_keys.py
+++ src/parsers/battery/group_keys.py
@@ -1,4 +1,4 @@
 def resolve_optional(key: BatteryKey, variants: list[set[object]]) -> BatteryKey:
     """Подставить единственный вариант только в сравнительный ключ, не в позицию."""
-    compared = zip(key, variants, strict=True)
+    compared = zip(key, variants, )
     return tuple(resolve_part(part, known) for part, known in compared)
```

### `parsers.battery.group_keys.x_resolve_optional__mutmut_8`

Статус: **survived**; тип: `keyword`; выбрано тестов: 38.

```diff
--- src/parsers/battery/group_keys.py
+++ src/parsers/battery/group_keys.py
@@ -1,4 +1,4 @@
 def resolve_optional(key: BatteryKey, variants: list[set[object]]) -> BatteryKey:
     """Подставить единственный вариант только в сравнительный ключ, не в позицию."""
-    compared = zip(key, variants, strict=True)
+    compared = zip(key, variants, strict=False)
     return tuple(resolve_part(part, known) for part, known in compared)
```

## src/parsers/battery/grouping.py

### `parsers.battery.grouping.x_offer_price__mutmut_6`

Классификация 2026-11-14: Эквивалент: Decimal принимает Infinity без учёта регистра. Значение положительной бесконечности, порядок сравнения цен и выбор главного предложения не меняются. Прогон R2 оставляет survived.

Статус: **survived**; тип: `string_case`; выбрано тестов: 38.

```diff
--- src/parsers/battery/grouping.py
+++ src/parsers/battery/grouping.py
@@ -1,4 +1,4 @@
 def offer_price(position: BatteryItem) -> Decimal:
     """Неизвестная РРЦ не выигрывает у известной; ноль является известной ценой."""
     price = position.offer.sale_price
-    return Decimal('Infinity') if price is None else price
+    return Decimal('infinity') if price is None else price
```

### `parsers.battery.grouping.x_offer_price__mutmut_7`

Классификация 2026-11-14: Эквивалент: Decimal принимает Infinity без учёта регистра. Значение положительной бесконечности, порядок сравнения цен и выбор главного предложения не меняются. Прогон R2 оставляет survived.

Статус: **survived**; тип: `string_case`; выбрано тестов: 38.

```diff
--- src/parsers/battery/grouping.py
+++ src/parsers/battery/grouping.py
@@ -1,4 +1,4 @@
 def offer_price(position: BatteryItem) -> Decimal:
     """Неизвестная РРЦ не выигрывает у известной; ноль является известной ценой."""
     price = position.offer.sale_price
-    return Decimal('Infinity') if price is None else price
+    return Decimal('INFINITY') if price is None else price
```

### `parsers.battery.grouping.x_split_optional__mutmut_9`

Классификация 2026-11-14: Эквивалент: каждый optional_key строится из четырёх фиксированных полей BatteryItem, поэтому все элементы keys имеют одинаковую длину. zip(*keys) не может увидеть разные длины; strict=None, False и отсутствие strict дают тот же результат. При пустом positions оба варианта zip также пусты. Прогон R2 оставляет survived.

Статус: **survived**; тип: `to_none`; выбрано тестов: 38.

```diff
--- src/parsers/battery/grouping.py
+++ src/parsers/battery/grouping.py
@@ -1,7 +1,7 @@
 def split_optional(positions: list[BatteryItem]) -> list[list[BatteryItem]]:
     """Неизвестное совместимо только с единственным вариантом всего основного ключа."""
     keys = [optional_key(position) for position in positions]
-    variants = list(map(known_parts, zip(*keys, strict=True)))
+    variants = list(map(known_parts, zip(*keys, strict=None)))
     groups: dict[tuple[object, ...], list[BatteryItem]] = {}
     for position, key in zip(positions, keys, strict=True):
         groups.setdefault(resolve_optional(key, variants), []).append(position)
```

### `parsers.battery.grouping.x_split_optional__mutmut_11`

Классификация 2026-11-14: Эквивалент: каждый optional_key строится из четырёх фиксированных полей BatteryItem, поэтому все элементы keys имеют одинаковую длину. zip(*keys) не может увидеть разные длины; strict=None, False и отсутствие strict дают тот же результат. При пустом positions оба варианта zip также пусты. Прогон R2 оставляет survived.

Статус: **survived**; тип: `other`; выбрано тестов: 38.

```diff
--- src/parsers/battery/grouping.py
+++ src/parsers/battery/grouping.py
@@ -1,7 +1,7 @@
 def split_optional(positions: list[BatteryItem]) -> list[list[BatteryItem]]:
     """Неизвестное совместимо только с единственным вариантом всего основного ключа."""
     keys = [optional_key(position) for position in positions]
-    variants = list(map(known_parts, zip(*keys, strict=True)))
+    variants = list(map(known_parts, zip(*keys, )))
     groups: dict[tuple[object, ...], list[BatteryItem]] = {}
     for position, key in zip(positions, keys, strict=True):
         groups.setdefault(resolve_optional(key, variants), []).append(position)
```

### `parsers.battery.grouping.x_split_optional__mutmut_12`

Классификация 2026-11-14: Эквивалент: каждый optional_key строится из четырёх фиксированных полей BatteryItem, поэтому все элементы keys имеют одинаковую длину. zip(*keys) не может увидеть разные длины; strict=None, False и отсутствие strict дают тот же результат. При пустом positions оба варианта zip также пусты. Прогон R2 оставляет survived.

Статус: **survived**; тип: `keyword`; выбрано тестов: 38.

```diff
--- src/parsers/battery/grouping.py
+++ src/parsers/battery/grouping.py
@@ -1,7 +1,7 @@
 def split_optional(positions: list[BatteryItem]) -> list[list[BatteryItem]]:
     """Неизвестное совместимо только с единственным вариантом всего основного ключа."""
     keys = [optional_key(position) for position in positions]
-    variants = list(map(known_parts, zip(*keys, strict=True)))
+    variants = list(map(known_parts, zip(*keys, strict=False)))
     groups: dict[tuple[object, ...], list[BatteryItem]] = {}
     for position, key in zip(positions, keys, strict=True):
         groups.setdefault(resolve_optional(key, variants), []).append(position)
```

### `parsers.battery.grouping.x_split_optional__mutmut_16`

Классификация 2026-11-14: Эквивалент: keys создаётся list comprehension ровно по одному ключу на каждый элемент positions. Поэтому длины аргументов zip(positions, keys) равны по построению; отключение strict не меняет ни одну пару и итоговые группы. Прогон R2 оставляет survived.

Статус: **survived**; тип: `to_none`; выбрано тестов: 38.

```diff
--- src/parsers/battery/grouping.py
+++ src/parsers/battery/grouping.py
@@ -3,6 +3,6 @@
     keys = [optional_key(position) for position in positions]
     variants = list(map(known_parts, zip(*keys, strict=True)))
     groups: dict[tuple[object, ...], list[BatteryItem]] = {}
-    for position, key in zip(positions, keys, strict=True):
+    for position, key in zip(positions, keys, strict=None):
         groups.setdefault(resolve_optional(key, variants), []).append(position)
     return list(groups.values())
```

### `parsers.battery.grouping.x_split_optional__mutmut_19`

Классификация 2026-11-14: Эквивалент: keys создаётся list comprehension ровно по одному ключу на каждый элемент positions. Поэтому длины аргументов zip(positions, keys) равны по построению; отключение strict не меняет ни одну пару и итоговые группы. Прогон R2 оставляет survived.

Статус: **survived**; тип: `other`; выбрано тестов: 38.

```diff
--- src/parsers/battery/grouping.py
+++ src/parsers/battery/grouping.py
@@ -3,6 +3,6 @@
     keys = [optional_key(position) for position in positions]
     variants = list(map(known_parts, zip(*keys, strict=True)))
     groups: dict[tuple[object, ...], list[BatteryItem]] = {}
-    for position, key in zip(positions, keys, strict=True):
+    for position, key in zip(positions, keys, ):
         groups.setdefault(resolve_optional(key, variants), []).append(position)
     return list(groups.values())
```

### `parsers.battery.grouping.x_split_optional__mutmut_20`

Классификация 2026-11-14: Эквивалент: keys создаётся list comprehension ровно по одному ключу на каждый элемент positions. Поэтому длины аргументов zip(positions, keys) равны по построению; отключение strict не меняет ни одну пару и итоговые группы. Прогон R2 оставляет survived.

Статус: **survived**; тип: `keyword`; выбрано тестов: 38.

```diff
--- src/parsers/battery/grouping.py
+++ src/parsers/battery/grouping.py
@@ -3,6 +3,6 @@
     keys = [optional_key(position) for position in positions]
     variants = list(map(known_parts, zip(*keys, strict=True)))
     groups: dict[tuple[object, ...], list[BatteryItem]] = {}
-    for position, key in zip(positions, keys, strict=True):
+    for position, key in zip(positions, keys, strict=False):
         groups.setdefault(resolve_optional(key, variants), []).append(position)
     return list(groups.values())
```

## src/parsers/battery/handler.py

### `parsers.battery.handler.xǁBatteryHandlerǁ__init____mutmut_4`

Статус: **survived**; тип: `other`; выбрано тестов: 45.

```diff
--- src/parsers/battery/handler.py
+++ src/parsers/battery/handler.py
@@ -1,4 +1,4 @@
     def __init__(self, settings: BatterySettings, supplier: str) -> None:
         self._settings = settings
         self._supplier = supplier
-        self._markup_policy = MarkupPolicy(settings.rules, tuple(settings.rules.markup_rules.values()))
+        self._markup_policy = MarkupPolicy(None, tuple(settings.rules.markup_rules.values()))
```

### `parsers.battery.handler.xǁBatteryHandlerǁprocess__mutmut_14`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `keyword`; выбрано тестов: 40.

```diff
--- src/parsers/battery/handler.py
+++ src/parsers/battery/handler.py
@@ -5,7 +5,7 @@
             issue = publication_issue(position, self._settings.min_rest)
             if issue is not None:
                 log_skipped(position, self._supplier, issue)
-                continue
+                break
             try:
                 normalized = normalize_title(position, self._settings.lines)
             except ValueError as exc:
```

### `parsers.battery.handler.xǁBatteryHandlerǁprocess__mutmut_20`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 40.

```diff
--- src/parsers/battery/handler.py
+++ src/parsers/battery/handler.py
@@ -9,7 +9,7 @@
             try:
                 normalized = normalize_title(position, self._settings.lines)
             except ValueError as exc:
-                offer_code = position.identity.code
+                offer_code = None
                 raise ValueError(f'[batteries] {self._supplier}, код {offer_code}: {exc}') from exc
             kept.append(apply_markup(normalized, self._markup_policy))
         return BatteryResult(tuple(kept))
```

## src/parsers/battery/offer_repeats.py

### `parsers.battery.offer_repeats.x_unique_offers__mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (текущий ID `parsers.battery.offer_repeats.x_unique_offers__mutmut_3`). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 43.

```diff
--- src/parsers/battery/offer_repeats.py
+++ src/parsers/battery/offer_repeats.py
@@ -3,7 +3,7 @@
     seen: dict[tuple[str, str], BatteryItem] = {}
     kept: list[BatteryItem] = []
     for original in positions:
-        position = replace(original, duplicate=BatteryDuplicate())
+        position = replace(original, duplicate=None)
         if is_new_offer(position, seen):
             kept.append(position)
     return kept
```

### `parsers.battery.offer_repeats.x_unique_offers__mutmut_7`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (текущий ID `parsers.battery.offer_repeats.x_unique_offers__mutmut_5`). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 43.

```diff
--- src/parsers/battery/offer_repeats.py
+++ src/parsers/battery/offer_repeats.py
@@ -3,7 +3,7 @@
     seen: dict[tuple[str, str], BatteryItem] = {}
     kept: list[BatteryItem] = []
     for original in positions:
-        position = replace(original, duplicate=BatteryDuplicate())
+        position = replace(original, )
         if is_new_offer(position, seen):
             kept.append(position)
     return kept
```

## src/parsers/battery/output.py

### `parsers.battery.output.xǁBatteryOutputSourceǁprepare__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 67.

```diff
--- src/parsers/battery/output.py
+++ src/parsers/battery/output.py
@@ -1,7 +1,7 @@
     def prepare(self, template_id: str, settings: GroupOutput) -> tuple[OutputFields, ...]:
         """Фильтры применяются к аккумуляторным полям, включая разметку дублей."""
         if settings.id != self.package.product_group:
-            raise ValueError('Преобразователь batteries получил настройки другой группы')
+            raise ValueError('XXПреобразователь batteries получил настройки другой группыXX')
         if settings.merge_warehouses:
             raise ValueError('batteries: сведение складов недоступно без отдельных складских данных')
         positions = self.package.positions
```

### `parsers.battery.output.xǁBatteryOutputSourceǁprepare__mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 67.

```diff
--- src/parsers/battery/output.py
+++ src/parsers/battery/output.py
@@ -1,7 +1,7 @@
     def prepare(self, template_id: str, settings: GroupOutput) -> tuple[OutputFields, ...]:
         """Фильтры применяются к аккумуляторным полям, включая разметку дублей."""
         if settings.id != self.package.product_group:
-            raise ValueError('Преобразователь batteries получил настройки другой группы')
+            raise ValueError('преобразователь batteries получил настройки другой группы')
         if settings.merge_warehouses:
             raise ValueError('batteries: сведение складов недоступно без отдельных складских данных')
         positions = self.package.positions
```

### `parsers.battery.output.xǁBatteryOutputSourceǁprepare__mutmut_7`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 67.

```diff
--- src/parsers/battery/output.py
+++ src/parsers/battery/output.py
@@ -3,7 +3,7 @@
         if settings.id != self.package.product_group:
             raise ValueError('Преобразователь batteries получил настройки другой группы')
         if settings.merge_warehouses:
-            raise ValueError('batteries: сведение складов недоступно без отдельных складских данных')
+            raise ValueError('XXbatteries: сведение складов недоступно без отдельных складских данныхXX')
         positions = self.package.positions
         if template_id == 'for_doubles':
             positions = double_positions(positions)
```

## src/parsers/battery/parser.py

### `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_3`

Статус: **survived**; тип: `to_none`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -1,6 +1,6 @@
     def __init__(self, config: ParseConfiguration, group_handler: BatteryHandler) -> None:
         self.settings = ParserSettings(config)
-        self.stats = ParserStats()
+        self.stats = None
         self._group_handler = group_handler
         vendor = config.vendor_config
         reader = FileReader(
```

### `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_5`

Статус: **survived**; тип: `to_none`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -2,7 +2,7 @@
         self.settings = ParserSettings(config)
         self.stats = ParserStats()
         self._group_handler = group_handler
-        vendor = config.vendor_config
+        vendor = None
         reader = FileReader(
             data_reader=data_reader_for(vendor.reader if vendor else 'xls'),
             price_source=FilePricesSource(config.config_provider),
```

### `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_6`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (текущий ID `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_3`). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -3,8 +3,5 @@
         self.stats = ParserStats()
         self._group_handler = group_handler
         vendor = config.vendor_config
-        reader = FileReader(
-            data_reader=data_reader_for(vendor.reader if vendor else 'xls'),
-            price_source=FilePricesSource(config.config_provider),
-        )
+        reader = None
         self.price_files = PriceFiles(config.parser_params, reader, config.routing)
```

### `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_7`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (текущий ID `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_4`). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -4,7 +4,7 @@
         self._group_handler = group_handler
         vendor = config.vendor_config
         reader = FileReader(
-            data_reader=data_reader_for(vendor.reader if vendor else 'xls'),
+            data_reader=None,
             price_source=FilePricesSource(config.config_provider),
         )
         self.price_files = PriceFiles(config.parser_params, reader, config.routing)
```

### `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_8`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (текущий ID `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_5`). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -5,6 +5,6 @@
         vendor = config.vendor_config
         reader = FileReader(
             data_reader=data_reader_for(vendor.reader if vendor else 'xls'),
-            price_source=FilePricesSource(config.config_provider),
+            price_source=None,
         )
         self.price_files = PriceFiles(config.parser_params, reader, config.routing)
```

### `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_9`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (текущий ID `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_6`). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -4,7 +4,6 @@
         self._group_handler = group_handler
         vendor = config.vendor_config
         reader = FileReader(
-            data_reader=data_reader_for(vendor.reader if vendor else 'xls'),
             price_source=FilePricesSource(config.config_provider),
         )
         self.price_files = PriceFiles(config.parser_params, reader, config.routing)
```

### `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_11`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (текущий ID `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_8`). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -4,7 +4,7 @@
         self._group_handler = group_handler
         vendor = config.vendor_config
         reader = FileReader(
-            data_reader=data_reader_for(vendor.reader if vendor else 'xls'),
+            data_reader=data_reader_for(None),
             price_source=FilePricesSource(config.config_provider),
         )
         self.price_files = PriceFiles(config.parser_params, reader, config.routing)
```

### `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_12`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (текущий ID `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_9`). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -4,7 +4,7 @@
         self._group_handler = group_handler
         vendor = config.vendor_config
         reader = FileReader(
-            data_reader=data_reader_for(vendor.reader if vendor else 'xls'),
+            data_reader=data_reader_for(vendor.reader if (vendor) and False else 'xls'),
             price_source=FilePricesSource(config.config_provider),
         )
         self.price_files = PriceFiles(config.parser_params, reader, config.routing)
```

### `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_14`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -4,7 +4,7 @@
         self._group_handler = group_handler
         vendor = config.vendor_config
         reader = FileReader(
-            data_reader=data_reader_for(vendor.reader if vendor else 'xls'),
+            data_reader=data_reader_for(vendor.reader if vendor else 'XXxlsXX'),
             price_source=FilePricesSource(config.config_provider),
         )
         self.price_files = PriceFiles(config.parser_params, reader, config.routing)
```

### `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_15`

Статус: **survived**; тип: `string_case`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -4,7 +4,7 @@
         self._group_handler = group_handler
         vendor = config.vendor_config
         reader = FileReader(
-            data_reader=data_reader_for(vendor.reader if vendor else 'xls'),
+            data_reader=data_reader_for(vendor.reader if vendor else 'XLS'),
             price_source=FilePricesSource(config.config_provider),
         )
         self.price_files = PriceFiles(config.parser_params, reader, config.routing)
```

### `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_16`

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -5,6 +5,6 @@
         vendor = config.vendor_config
         reader = FileReader(
             data_reader=data_reader_for(vendor.reader if vendor else 'xls'),
-            price_source=FilePricesSource(config.config_provider),
+            price_source=FilePricesSource(None),
         )
         self.price_files = PriceFiles(config.parser_params, reader, config.routing)
```

### `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_18`

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -7,4 +7,4 @@
             data_reader=data_reader_for(vendor.reader if vendor else 'xls'),
             price_source=FilePricesSource(config.config_provider),
         )
-        self.price_files = PriceFiles(config.parser_params, reader, config.routing)
+        self.price_files = PriceFiles(None, reader, config.routing)
```

### `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_19`

Статус: **survived**; тип: `to_none`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -7,4 +7,4 @@
             data_reader=data_reader_for(vendor.reader if vendor else 'xls'),
             price_source=FilePricesSource(config.config_provider),
         )
-        self.price_files = PriceFiles(config.parser_params, reader, config.routing)
+        self.price_files = PriceFiles(config.parser_params, None, config.routing)
```

### `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_20`

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -7,4 +7,4 @@
             data_reader=data_reader_for(vendor.reader if vendor else 'xls'),
             price_source=FilePricesSource(config.config_provider),
         )
-        self.price_files = PriceFiles(config.parser_params, reader, config.routing)
+        self.price_files = PriceFiles(config.parser_params, reader, None)
```

### `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_21`

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -7,4 +7,4 @@
             data_reader=data_reader_for(vendor.reader if vendor else 'xls'),
             price_source=FilePricesSource(config.config_provider),
         )
-        self.price_files = PriceFiles(config.parser_params, reader, config.routing)
+        self.price_files = PriceFiles(reader, config.routing)
```

### `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_22`

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -7,4 +7,4 @@
             data_reader=data_reader_for(vendor.reader if vendor else 'xls'),
             price_source=FilePricesSource(config.config_provider),
         )
-        self.price_files = PriceFiles(config.parser_params, reader, config.routing)
+        self.price_files = PriceFiles(config.parser_params, config.routing)
```

### `parsers.battery.parser.xǁBatteryParserǁ__init____mutmut_23`

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -7,4 +7,4 @@
             data_reader=data_reader_for(vendor.reader if vendor else 'xls'),
             price_source=FilePricesSource(config.config_provider),
         )
-        self.price_files = PriceFiles(config.parser_params, reader, config.routing)
+        self.price_files = PriceFiles(config.parser_params, reader, )
```

### `parsers.battery.parser.xǁBatteryParserǁparse__mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -4,7 +4,7 @@
         if not self.settings.is_active:
             process_log.log_disable_status()
             return BatteryResult()
-        paths = self.price_files.resolve()
+        paths = None
         process_log.log_start()
         process_log.log_list_files(paths)
         package = self._group_handler.process_fields(self.price_files.read_rows(paths))
```

### `parsers.battery.parser.xǁBatteryParserǁparse__mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -6,7 +6,7 @@
             return BatteryResult()
         paths = self.price_files.resolve()
         process_log.log_start()
-        process_log.log_list_files(paths)
+        process_log.log_list_files(None)
         package = self._group_handler.process_fields(self.price_files.read_rows(paths))
         process_log.log_finish(BatteryResultStatistic(package.positions))
         return package
```

### `parsers.battery.parser.xǁBatteryParserǁparse__mutmut_8`

Статус: **survived**; тип: `to_none`; выбрано тестов: 2.

```diff
--- src/parsers/battery/parser.py
+++ src/parsers/battery/parser.py
@@ -7,6 +7,6 @@
         paths = self.price_files.resolve()
         process_log.log_start()
         process_log.log_list_files(paths)
-        package = self._group_handler.process_fields(self.price_files.read_rows(paths))
+        package = self._group_handler.process_fields(self.price_files.read_rows(None))
         process_log.log_finish(BatteryResultStatistic(package.positions))
         return package
```

## src/parsers/battery/processing.py

### `parsers.battery.processing.x__required_issue__mutmut_2`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 38.

```diff
--- src/parsers/battery/processing.py
+++ src/parsers/battery/processing.py
@@ -1,7 +1,7 @@
 def _required_issue(position: BatteryItem) -> str | None:
     """Наличие РРЦ проверяется отдельно от её величины: нулевая цена не означает неизвестную."""
     required = {
-        'code': position.identity.code,
+        'XXcodeXX': position.identity.code,
         'title': position.identity.title,
         'price_recommended': position.offer.sale_price,
     }
```

### `parsers.battery.processing.x__required_issue__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 38.

```diff
--- src/parsers/battery/processing.py
+++ src/parsers/battery/processing.py
@@ -2,7 +2,7 @@
     """Наличие РРЦ проверяется отдельно от её величины: нулевая цена не означает неизвестную."""
     required = {
         'code': position.identity.code,
-        'title': position.identity.title,
+        'XXtitleXX': position.identity.title,
         'price_recommended': position.offer.sale_price,
     }
     missing = [key for key, field_value in required.items() if field_value is None]
```

### `parsers.battery.processing.x__required_issue__mutmut_6`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 38.

```diff
--- src/parsers/battery/processing.py
+++ src/parsers/battery/processing.py
@@ -3,7 +3,7 @@
     required = {
         'code': position.identity.code,
         'title': position.identity.title,
-        'price_recommended': position.offer.sale_price,
+        'XXprice_recommendedXX': position.offer.sale_price,
     }
     missing = [key for key, field_value in required.items() if field_value is None]
     if missing:
```

### `parsers.battery.processing.x__required_issue__mutmut_12`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (текущий ID `parsers.battery.processing.x__required_issue__mutmut_3`). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 38.

```diff
--- src/parsers/battery/processing.py
+++ src/parsers/battery/processing.py
@@ -7,6 +7,6 @@
     }
     missing = [key for key, field_value in required.items() if field_value is None]
     if missing:
-        fields = ', '.join(missing)
+        fields = 'XX, XX'.join(missing)
         return f'отсутствуют обязательные поля: {fields}'
     return None
```

### `parsers.battery.processing.x_apply_markup__mutmut_11`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (текущий ID `parsers.battery.processing.x_apply_markup__mutmut_9`). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 30.

```diff
--- src/parsers/battery/processing.py
+++ src/parsers/battery/processing.py
@@ -3,6 +3,6 @@
     offer = position.offer
     price = offer.price_recommended
     if offer.price_opt is not None and price is not None and price <= offer.price_opt:
-        percent = Decimal(str(policy.markup_percent_for_opt(float(offer.price_opt))))
+        percent = Decimal(str(policy.markup_percent_for_opt(None)))
         price = (offer.price_opt * (1 + percent)).normalize()
     return replace(position, offer=replace(offer, price_markup=price))
```

## src/parsers/battery/statistic.py

### `parsers.battery.statistic.xǁBatteryResultStatisticǁ__init____mutmut_10`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R2 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `number`; выбрано тестов: 8.

```diff
--- src/parsers/battery/statistic.py
+++ src/parsers/battery/statistic.py
@@ -5,7 +5,7 @@
         for position in positions:
             purchase = position.offer.price_opt
             sale = position.offer.sale_price
-            if purchase is not None and purchase > 0 and sale is not None:
+            if purchase is not None and purchase > 1 and sale is not None:
                 margin = sale - purchase
                 self._margins.append(margin)
                 self._percents.append(margin / purchase * _PERCENT)
```

## src/parsers/battery/title.py

### `parsers.battery.title.x_normalize_title__mutmut_5`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 32.

```diff
--- src/parsers/battery/title.py
+++ src/parsers/battery/title.py
@@ -1,6 +1,6 @@
 def normalize_title(position: BatteryItem, lines: tuple[str, ...]) -> BatteryItem:
     """Сохранить любое название; список линеек служит подсказкой для заполнения модели."""
-    title = ' '.join((position.identity.title or '').split())
+    title = ' '.join((position.identity.title or 'XXXX').split())
     matches = [line for line in lines if _matches(title, line)]
     if not matches:
         return replace(position, identity=replace(position.identity, title=title))
```

### `parsers.battery.title.x_normalize_title__mutmut_15`

Статус: **survived**; тип: `other`; выбрано тестов: 32.

```diff
--- src/parsers/battery/title.py
+++ src/parsers/battery/title.py
@@ -3,7 +3,7 @@
     title = ' '.join((position.identity.title or '').split())
     matches = [line for line in lines if _matches(title, line)]
     if not matches:
-        return replace(position, identity=replace(position.identity, title=title))
+        return replace(position, )
     if len(matches) > 1:
         raise ValueError(f'ожидается одна известная линейка, найдены {matches}: {title!r}')
     model = matches[0]
```

### `parsers.battery.title.x_normalize_title__mutmut_19`

Статус: **survived**; тип: `other`; выбрано тестов: 32.

```diff
--- src/parsers/battery/title.py
+++ src/parsers/battery/title.py
@@ -3,7 +3,7 @@
     title = ' '.join((position.identity.title or '').split())
     matches = [line for line in lines if _matches(title, line)]
     if not matches:
-        return replace(position, identity=replace(position.identity, title=title))
+        return replace(position, identity=replace(position.identity, ))
     if len(matches) > 1:
         raise ValueError(f'ожидается одна известная линейка, найдены {matches}: {title!r}')
     model = matches[0]
```

### `parsers.battery.title.x_normalize_title__mutmut_30`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 32.

```diff
--- src/parsers/battery/title.py
+++ src/parsers/battery/title.py
@@ -8,7 +8,7 @@
         raise ValueError(f'ожидается одна известная линейка, найдены {matches}: {title!r}')
     model = matches[0]
     declared = position.identity.model
-    normalized_model = ' '.join((declared or '').split()).casefold()
+    normalized_model = ' '.join((declared or 'XXXX').split()).casefold()
     if declared is not None and normalized_model != model.casefold():
         raise ValueError(f'линейка {declared!r} не совпадает с названием {title!r}')
     return replace(position, identity=replace(position.identity, title=title, model=model))
```

### `parsers.battery.title.x_normalize_title__mutmut_43`

Статус: **survived**; тип: `other`; выбрано тестов: 32.

```diff
--- src/parsers/battery/title.py
+++ src/parsers/battery/title.py
@@ -11,4 +11,4 @@
     normalized_model = ' '.join((declared or '').split()).casefold()
     if declared is not None and normalized_model != model.casefold():
         raise ValueError(f'линейка {declared!r} не совпадает с названием {title!r}')
-    return replace(position, identity=replace(position.identity, title=title, model=model))
+    return replace(position, identity=replace(position.identity, model=model))
```

## src/parsers/common_price/availability.py

### `parsers.common_price.availability.x_is_on_order__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 76.

```diff
--- src/parsers/common_price/availability.py
+++ src/parsers/common_price/availability.py
@@ -1,3 +1,3 @@
 def is_on_order(row_item: RowItem) -> bool:
     """Под заказ — в «Наличии» поставщика есть слово «заказ»; пусто — в наличии."""
-    return _ON_ORDER_MARKER in (row_item.stock.available or '').lower()
+    return _ON_ORDER_MARKER in (row_item.stock.available or 'XXXX').lower()
```

## src/parsers/common_price/dispute.py

### `parsers.common_price.dispute.x__season_label__mutmut_9`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -1,6 +1,6 @@
 def _season_label(raw: Any) -> str:
     text = str(raw or '').strip().lower()
-    if text in {'зима', 'зимняя'}:
+    if text in {'зима', 'XXзимняяXX'}:
         return 'зимняя'
     if text in {'лето', 'летняя'}:
         return 'летняя'
```

### `parsers.common_price.dispute.x__season_label__mutmut_10`

Статус: **survived**; тип: `string_case`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -1,6 +1,6 @@
 def _season_label(raw: Any) -> str:
     text = str(raw or '').strip().lower()
-    if text in {'зима', 'зимняя'}:
+    if text in {'зима', 'ЗИМНЯЯ'}:
         return 'зимняя'
     if text in {'лето', 'летняя'}:
         return 'летняя'
```

### `parsers.common_price.dispute.x__season_label__mutmut_11`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -1,7 +1,7 @@
 def _season_label(raw: Any) -> str:
     text = str(raw or '').strip().lower()
     if text in {'зима', 'зимняя'}:
-        return 'зимняя'
+        return 'XXзимняяXX'
     if text in {'лето', 'летняя'}:
         return 'летняя'
     return text
```

### `parsers.common_price.dispute.x__season_label__mutmut_12`

Статус: **survived**; тип: `string_case`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -1,7 +1,7 @@
 def _season_label(raw: Any) -> str:
     text = str(raw or '').strip().lower()
     if text in {'зима', 'зимняя'}:
-        return 'зимняя'
+        return 'ЗИМНЯЯ'
     if text in {'лето', 'летняя'}:
         return 'летняя'
     return text
```

### `parsers.common_price.dispute.x__season_label__mutmut_16`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -2,6 +2,6 @@
     text = str(raw or '').strip().lower()
     if text in {'зима', 'зимняя'}:
         return 'зимняя'
-    if text in {'лето', 'летняя'}:
+    if text in {'лето', 'XXлетняяXX'}:
         return 'летняя'
     return text
```

### `parsers.common_price.dispute.x__season_label__mutmut_17`

Статус: **survived**; тип: `string_case`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -2,6 +2,6 @@
     text = str(raw or '').strip().lower()
     if text in {'зима', 'зимняя'}:
         return 'зимняя'
-    if text in {'лето', 'летняя'}:
+    if text in {'лето', 'ЛЕТНЯЯ'}:
         return 'летняя'
     return text
```

### `parsers.common_price.dispute.x__season_label__mutmut_18`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -3,5 +3,5 @@
     if text in {'зима', 'зимняя'}:
         return 'зимняя'
     if text in {'лето', 'летняя'}:
-        return 'летняя'
+        return 'XXлетняяXX'
     return text
```

### `parsers.common_price.dispute.x__season_label__mutmut_19`

Статус: **survived**; тип: `string_case`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -3,5 +3,5 @@
     if text in {'зима', 'зимняя'}:
         return 'зимняя'
     if text in {'лето', 'летняя'}:
-        return 'летняя'
+        return 'ЛЕТНЯЯ'
     return text
```

### `parsers.common_price.dispute.x__spike_label__mutmut_5`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -1,5 +1,5 @@
 def _spike_label(raw: Any) -> str:
-    text = str(raw or '').strip().lower()
+    text = str(raw or 'XXXX').strip().lower()
     if text in {'да', 'yes', 'ш.'}:
         return 'да'
     if text in {'нет', 'no'}:
```

### `parsers.common_price.dispute.x__spike_label__mutmut_13`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -1,7 +1,7 @@
 def _spike_label(raw: Any) -> str:
     text = str(raw or '').strip().lower()
     if text in {'да', 'yes', 'ш.'}:
-        return 'да'
+        return 'XXдаXX'
     if text in {'нет', 'no'}:
         return 'нет'
     return ''
```

### `parsers.common_price.dispute.x__spike_label__mutmut_14`

Статус: **survived**; тип: `string_case`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -1,7 +1,7 @@
 def _spike_label(raw: Any) -> str:
     text = str(raw or '').strip().lower()
     if text in {'да', 'yes', 'ш.'}:
-        return 'да'
+        return 'ДА'
     if text in {'нет', 'no'}:
         return 'нет'
     return ''
```

### `parsers.common_price.dispute.x__spike_label__mutmut_20`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -3,5 +3,5 @@
     if text in {'да', 'yes', 'ш.'}:
         return 'да'
     if text in {'нет', 'no'}:
-        return 'нет'
+        return 'XXнетXX'
     return ''
```

### `parsers.common_price.dispute.x__spike_label__mutmut_21`

Статус: **survived**; тип: `string_case`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -3,5 +3,5 @@
     if text in {'да', 'yes', 'ш.'}:
         return 'да'
     if text in {'нет', 'no'}:
-        return 'нет'
+        return 'НЕТ'
     return ''
```

### `parsers.common_price.dispute.x__xl_label__mutmut_3`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -1,3 +1,3 @@
 def _xl_label(title: str | None) -> str:
     """XL в названии — «да», иначе «нет»: Мим и Форточки XL не пишут, поэтому это лишь пометка, а не ключ."""
-    return 'да' if _XL_RE.search(title or '') else 'нет'
+    return 'XXдаXX' if _XL_RE.search(title or '') else 'нет'
```

### `parsers.common_price.dispute.x__xl_label__mutmut_4`

Статус: **survived**; тип: `string_case`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -1,3 +1,3 @@
 def _xl_label(title: str | None) -> str:
     """XL в названии — «да», иначе «нет»: Мим и Форточки XL не пишут, поэтому это лишь пометка, а не ключ."""
-    return 'да' if _XL_RE.search(title or '') else 'нет'
+    return 'ДА' if _XL_RE.search(title or '') else 'нет'
```

### `parsers.common_price.dispute.x__xl_label__mutmut_7`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -1,3 +1,3 @@
 def _xl_label(title: str | None) -> str:
     """XL в названии — «да», иначе «нет»: Мим и Форточки XL не пишут, поэтому это лишь пометка, а не ключ."""
-    return 'да' if _XL_RE.search(title or '') else 'нет'
+    return 'да' if _XL_RE.search(title or 'XXXX') else 'нет'
```

### `parsers.common_price.dispute.x__xl_label__mutmut_8`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -1,3 +1,3 @@
 def _xl_label(title: str | None) -> str:
     """XL в названии — «да», иначе «нет»: Мим и Форточки XL не пишут, поэтому это лишь пометка, а не ключ."""
-    return 'да' if _XL_RE.search(title or '') else 'нет'
+    return 'да' if _XL_RE.search(title or '') else 'XXнетXX'
```

### `parsers.common_price.dispute.x__xl_label__mutmut_9`

Статус: **survived**; тип: `string_case`; выбрано тестов: 70.

```diff
--- src/parsers/common_price/dispute.py
+++ src/parsers/common_price/dispute.py
@@ -1,3 +1,3 @@
 def _xl_label(title: str | None) -> str:
     """XL в названии — «да», иначе «нет»: Мим и Форточки XL не пишут, поэтому это лишь пометка, а не ключ."""
-    return 'да' if _XL_RE.search(title or '') else 'нет'
+    return 'да' if _XL_RE.search(title or '') else 'НЕТ'
```

## src/parsers/common_price/doubles_order.py

### `parsers.common_price.doubles_order.x__group_of__mutmut_1`

Статус: **survived**; тип: `other`; выбрано тестов: 9.

```diff
--- src/parsers/common_price/doubles_order.py
+++ src/parsers/common_price/doubles_order.py
@@ -1,2 +1,2 @@
 def _group_of(row: RowItem) -> DuplicateGroupKey:
-    return DuplicateGroupKey(row.product_group, row.duplicate.group_by_params or 0)
+    return DuplicateGroupKey(None, row.duplicate.group_by_params or 0)
```

### `parsers.common_price.doubles_order.x__group_of__mutmut_6`

Статус: **survived**; тип: `number`; выбрано тестов: 9.

```diff
--- src/parsers/common_price/doubles_order.py
+++ src/parsers/common_price/doubles_order.py
@@ -1,2 +1,2 @@
 def _group_of(row: RowItem) -> DuplicateGroupKey:
-    return DuplicateGroupKey(row.product_group, row.duplicate.group_by_params or 0)
+    return DuplicateGroupKey(row.product_group, row.duplicate.group_by_params or 1)
```

### `parsers.common_price.doubles_order.x__supplier_rank__mutmut_6`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 9.

```diff
--- src/parsers/common_price/doubles_order.py
+++ src/parsers/common_price/doubles_order.py
@@ -1,2 +1,2 @@
 def _supplier_rank(row: RowItem, rank: _Ranks) -> int:
-    return rank.get(row.vendor.supplier_name or '', _NONE)
+    return rank.get(row.vendor.supplier_name or 'XXXX', _NONE)
```

## src/parsers/common_price/exclude_doubles.py

### `parsers.common_price.exclude_doubles.x__double_group__mutmut_6`

Статус: **survived**; тип: `other`; выбрано тестов: 6.

```diff
--- src/parsers/common_price/exclude_doubles.py
+++ src/parsers/common_price/exclude_doubles.py
@@ -2,4 +2,4 @@
     duplicate = row_item.duplicate
     if not (duplicate.is_double or duplicate.double_candidate) or duplicate.group_by_params is None:
         return None
-    return DuplicateGroupKey(row_item.product_group, duplicate.group_by_params)
+    return DuplicateGroupKey(None, duplicate.group_by_params)
```

## src/parsers/common_price/group_fields.py

### `parsers.common_price.group_fields.x_camera_from_field__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 144.

```diff
--- src/parsers/common_price/group_fields.py
+++ src/parsers/common_price/group_fields.py
@@ -1,6 +1,6 @@
 def camera_from_field(camera_type: Any) -> str | None:
     """TT / TTF / «только шина»; TL не отличает."""
-    text = str(camera_type or '').strip()
+    text = str(camera_type or 'XXXX').strip()
     if not text:
         return None
     upper = text.upper()
```

### `parsers.common_price.group_fields.x_camera_key__mutmut_6`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 134.

```diff
--- src/parsers/common_price/group_fields.py
+++ src/parsers/common_price/group_fields.py
@@ -3,7 +3,7 @@
     from_field = camera_from_field(row_item.tire.camera_type)
     if from_field:
         return from_field
-    token = (intimacy or '').upper()
+    token = (intimacy or 'XXXX').upper()
     if token in _DISTINGUISHING_INTIMACY:
         return token
     return None
```

### `parsers.common_price.group_fields.x_disk_extras_key__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 135.

```diff
--- src/parsers/common_price/group_fields.py
+++ src/parsers/common_price/group_fields.py
@@ -1,6 +1,6 @@
 def disk_extras_key(row_item: RowItem) -> str:
     """Хвосты диска в ключе; пусто если не диск или хвоста нет."""
-    kind = (row_item.vendor.type_production or '').lower()
+    kind = (row_item.vendor.type_production or 'XXXX').lower()
     if _DISK_KIND not in kind:
         return ''
     return disk_name_extras(row_item.identity.title or '').lower()
```

### `parsers.common_price.group_fields.x_disk_extras_key__mutmut_10`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 135.

```diff
--- src/parsers/common_price/group_fields.py
+++ src/parsers/common_price/group_fields.py
@@ -3,4 +3,4 @@
     kind = (row_item.vendor.type_production or '').lower()
     if _DISK_KIND not in kind:
         return ''
-    return disk_name_extras(row_item.identity.title or '').lower()
+    return disk_name_extras(row_item.identity.title or 'XXXX').lower()
```

### `parsers.common_price.group_fields.x_yes_flag__mutmut_5`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 145.

```diff
--- src/parsers/common_price/group_fields.py
+++ src/parsers/common_price/group_fields.py
@@ -1,4 +1,4 @@
 def yes_flag(raw: Any) -> str:
     """Да/RunFlat → одна метка."""
-    text = str(raw or '').strip().lower()
+    text = str(raw or 'XXXX').strip().lower()
     return 'да' if text in _YES_FLAGS else ''
```

## src/parsers/common_price/group_key.py

### `parsers.common_price.group_key.x__group_key_parts__mutmut_7`

Статус: **survived**; тип: `method_swap`; выбрано тестов: 132.

```diff
--- src/parsers/common_price/group_key.py
+++ src/parsers/common_price/group_key.py
@@ -1,7 +1,7 @@
 def _group_key_parts(row_item: RowItem, aliases_map: dict[str, Any]) -> list[Any]:
     """Значения полей для ключа группировки."""
     mark, brand, mark_group, key_brand = brand_key_parts(row_item, aliases_map)
-    intimacy = (row_item.tire.intimacy or define_intimacy(row_item) or '').upper()
+    intimacy = (row_item.tire.intimacy or define_intimacy(row_item) or '').lower()
     return [
         (row_item.vendor.type_production or '').lower(),
         *size_fields(row_item),
```

### `parsers.common_price.group_key.x__group_key_parts__mutmut_11`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 132.

```diff
--- src/parsers/common_price/group_key.py
+++ src/parsers/common_price/group_key.py
@@ -1,7 +1,7 @@
 def _group_key_parts(row_item: RowItem, aliases_map: dict[str, Any]) -> list[Any]:
     """Значения полей для ключа группировки."""
     mark, brand, mark_group, key_brand = brand_key_parts(row_item, aliases_map)
-    intimacy = (row_item.tire.intimacy or define_intimacy(row_item) or '').upper()
+    intimacy = (row_item.tire.intimacy or define_intimacy(row_item) or 'XXXX').upper()
     return [
         (row_item.vendor.type_production or '').lower(),
         *size_fields(row_item),
```

### `parsers.common_price.group_key.x__layering_key__mutmut_3`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 132.

```diff
--- src/parsers/common_price/group_key.py
+++ src/parsers/common_price/group_key.py
@@ -1,5 +1,5 @@
 def _layering_key(row_item: RowItem) -> str:
     """Слойность `<N>PR` для ключа; у грузовых шин и спецшин не учитывается."""
-    if (row_item.vendor.type_production or '').lower() in _LAYERING_IGNORED_TYPES:
+    if (row_item.vendor.type_production or 'XXXX').lower() in _LAYERING_IGNORED_TYPES:
         return ''
     return layering_label(row_item.tire.layering)
```

### `parsers.common_price.group_key.x__layering_key__mutmut_5`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 132.

```diff
--- src/parsers/common_price/group_key.py
+++ src/parsers/common_price/group_key.py
@@ -1,5 +1,5 @@
 def _layering_key(row_item: RowItem) -> str:
     """Слойность `<N>PR` для ключа; у грузовых шин и спецшин не учитывается."""
     if (row_item.vendor.type_production or '').lower() in _LAYERING_IGNORED_TYPES:
-        return ''
+        return 'XXXX'
     return layering_label(row_item.tire.layering)
```

### `parsers.common_price.group_key.x_define_intimacy__mutmut_8`

Статус: **survived**; тип: `number`; выбрано тестов: 138.

```diff
--- src/parsers/common_price/group_key.py
+++ src/parsers/common_price/group_key.py
@@ -2,7 +2,7 @@
     """Определить камерность (TL/TT/TTF) из title."""
 
     def is_float_diameter(diameter: Any) -> bool:
-        diameter_str = str(diameter or 0).replace(',', '.')
+        diameter_str = str(diameter or 1).replace(',', '.')
         try:
             return not float(diameter_str).is_integer()
         except ValueError, TypeError:
```

### `parsers.common_price.group_key.x_define_intimacy__mutmut_18`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 138.

```diff
--- src/parsers/common_price/group_key.py
+++ src/parsers/common_price/group_key.py
@@ -8,7 +8,7 @@
         except ValueError, TypeError:
             return False
 
-    chunks = replace_homoglyphs((row_item.identity.title or '').lower()).split()
+    chunks = replace_homoglyphs((row_item.identity.title or 'XXXX').lower()).split()
     for intimacy in ('tl', 'tt', 'ttf'):
         if intimacy in chunks:
             return intimacy.upper()
```

### `parsers.common_price.group_key.x_define_intimacy__mutmut_30`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 138.

```diff
--- src/parsers/common_price/group_key.py
+++ src/parsers/common_price/group_key.py
@@ -13,7 +13,7 @@
         if intimacy in chunks:
             return intimacy.upper()
 
-    type_prod = (row_item.vendor.type_production or '').lower()
+    type_prod = (row_item.vendor.type_production or 'XXXX').lower()
     if 'грузовая' in type_prod and is_float_diameter(row_item.tire.diameter):
         return 'TL'
     return None
```

### `parsers.common_price.group_key.x_group_key__mutmut_6`

Статус: **survived**; тип: `other`; выбрано тестов: 132.

```diff
--- src/parsers/common_price/group_key.py
+++ src/parsers/common_price/group_key.py
@@ -3,4 +3,4 @@
     aliases_map: dict[str, Any] | None = None,
 ) -> tuple[str, ...]:
     """Ключ группировки; без карты алиасов производителей — пустая карта."""
-    return sanitize_value(_group_key_parts(row_item, {} if aliases_map is None else aliases_map))
+    return sanitize_value(_group_key_parts(row_item, {} if (aliases_map is None) and False else aliases_map))
```

## src/parsers/common_price/group_output.py

### `parsers.common_price.group_output.x_output_sources__mutmut_2`

Статус: **survived**; тип: `other`; выбрано тестов: 20.

```diff
--- src/parsers/common_price/group_output.py
+++ src/parsers/common_price/group_output.py
@@ -4,7 +4,7 @@
     """Чужая модель пакета отклоняется до подготовки и записи файлов."""
     clear_nomenclature_cache()
     sources: dict[ProductGroup, GroupOutputSource] = {
-        ProductGroup.TIRE_AND_DISK: TireOutputSource(TireAndDiskResult()),
+        ProductGroup.TIRE_AND_DISK: TireOutputSource(None),
         ProductGroup.BATTERIES: BatteryOutputSource(BatteryResult()),
     }
     for group, package in packages.items():
```

### `parsers.common_price.group_output.x_output_sources__mutmut_3`

Статус: **survived**; тип: `other`; выбрано тестов: 20.

```diff
--- src/parsers/common_price/group_output.py
+++ src/parsers/common_price/group_output.py
@@ -5,7 +5,7 @@
     clear_nomenclature_cache()
     sources: dict[ProductGroup, GroupOutputSource] = {
         ProductGroup.TIRE_AND_DISK: TireOutputSource(TireAndDiskResult()),
-        ProductGroup.BATTERIES: BatteryOutputSource(BatteryResult()),
+        ProductGroup.BATTERIES: BatteryOutputSource(None),
     }
     for group, package in packages.items():
         if isinstance(package, BatteryResult):
```

### `parsers.common_price.group_output.x_output_sources__mutmut_7`

Статус: **survived**; тип: `other`; выбрано тестов: 20.

```diff
--- src/parsers/common_price/group_output.py
+++ src/parsers/common_price/group_output.py
@@ -11,7 +11,7 @@
         if isinstance(package, BatteryResult):
             sources[group] = BatteryOutputSource(package)
         elif isinstance(package, TireAndDiskResult):
-            settings = load_doubles_settings(tuple(writer_templates_by_name()), config)
+            settings = load_doubles_settings(None, config)
             sources[group] = TireOutputSource(
                 package, settings, partial(get_nomenclature_corrected_title, config_provider=config)
             )
```

### `parsers.common_price.group_output.x_output_sources__mutmut_15`

Статус: **survived**; тип: `other`; выбрано тестов: 20.

```diff
--- src/parsers/common_price/group_output.py
+++ src/parsers/common_price/group_output.py
@@ -13,7 +13,7 @@
         elif isinstance(package, TireAndDiskResult):
             settings = load_doubles_settings(tuple(writer_templates_by_name()), config)
             sources[group] = TireOutputSource(
-                package, settings, partial(get_nomenclature_corrected_title, config_provider=config)
+                package, settings, None
             )
         else:
             raise TypeError(f'Нет выходного преобразователя для {group.value}: {type(package).__name__}')
```

### `parsers.common_price.group_output.x_output_sources__mutmut_18`

Статус: **survived**; тип: `other`; выбрано тестов: 20.

```diff
--- src/parsers/common_price/group_output.py
+++ src/parsers/common_price/group_output.py
@@ -13,8 +13,7 @@
         elif isinstance(package, TireAndDiskResult):
             settings = load_doubles_settings(tuple(writer_templates_by_name()), config)
             sources[group] = TireOutputSource(
-                package, settings, partial(get_nomenclature_corrected_title, config_provider=config)
-            )
+                package, settings, )
         else:
             raise TypeError(f'Нет выходного преобразователя для {group.value}: {type(package).__name__}')
     return sources
```

### `parsers.common_price.group_output.x_write_group_prices__mutmut_4`

Статус: **survived**; тип: `to_none`; выбрано тестов: 20.

```diff
--- src/parsers/common_price/group_output.py
+++ src/parsers/common_price/group_output.py
@@ -9,7 +9,7 @@
     """Проверить весь набор шаблонов, затем записать явно выбранные для них группы."""
     if template is None:
         outputs = _default_outputs(selected)
-        selections = {output.template_id: _groups(output).intersection(selected) for output in outputs}
+        selections = None
         paths = writer.write_plan(
             prepare_output_plan(outputs, sources, selections=selections, skip_empty=True), as_jsonl=as_jsonl
         )
```

### `parsers.common_price.group_output.x_write_group_prices__mutmut_14`

Статус: **survived**; тип: `to_none`; выбрано тестов: 20.

```diff
--- src/parsers/common_price/group_output.py
+++ src/parsers/common_price/group_output.py
@@ -11,7 +11,7 @@
         outputs = _default_outputs(selected)
         selections = {output.template_id: _groups(output).intersection(selected) for output in outputs}
         paths = writer.write_plan(
-            prepare_output_plan(outputs, sources, selections=selections, skip_empty=True), as_jsonl=as_jsonl
+            prepare_output_plan(outputs, sources, selections=None, skip_empty=True), as_jsonl=as_jsonl
         )
     else:
         output = named_group_output(template)
```

### `parsers.common_price.group_output.x_write_group_prices__mutmut_18`

Статус: **survived**; тип: `other`; выбрано тестов: 20.

```diff
--- src/parsers/common_price/group_output.py
+++ src/parsers/common_price/group_output.py
@@ -11,7 +11,7 @@
         outputs = _default_outputs(selected)
         selections = {output.template_id: _groups(output).intersection(selected) for output in outputs}
         paths = writer.write_plan(
-            prepare_output_plan(outputs, sources, selections=selections, skip_empty=True), as_jsonl=as_jsonl
+            prepare_output_plan(outputs, sources, skip_empty=True), as_jsonl=as_jsonl
         )
     else:
         output = named_group_output(template)
```

### `parsers.common_price.group_output.x_write_group_prices__mutmut_26`

Статус: **survived**; тип: `to_none`; выбрано тестов: 20.

```diff
--- src/parsers/common_price/group_output.py
+++ src/parsers/common_price/group_output.py
@@ -15,6 +15,6 @@
         )
     else:
         output = named_group_output(template)
-        plan = prepare_output_plan([output], sources, selected=selected, skip_empty=True)
+        plan = prepare_output_plan([output], sources, selected=None, skip_empty=True)
         paths = writer.write_plan(plan, as_jsonl=as_jsonl)
     return jsonl_output_files(paths) if as_jsonl else paths
```

### `parsers.common_price.group_output.x_write_group_prices__mutmut_30`

Статус: **survived**; тип: `other`; выбрано тестов: 20.

```diff
--- src/parsers/common_price/group_output.py
+++ src/parsers/common_price/group_output.py
@@ -15,6 +15,6 @@
         )
     else:
         output = named_group_output(template)
-        plan = prepare_output_plan([output], sources, selected=selected, skip_empty=True)
+        plan = prepare_output_plan([output], sources, skip_empty=True)
         paths = writer.write_plan(plan, as_jsonl=as_jsonl)
     return jsonl_output_files(paths) if as_jsonl else paths
```

## src/parsers/common_price/group_title.py

### `parsers.common_price.group_title.x__merged_title__mutmut_5`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 18.

```diff
--- src/parsers/common_price/group_title.py
+++ src/parsers/common_price/group_title.py
@@ -2,7 +2,7 @@
     """Название эталона с признаками шины всей группы; без нагрузки+скорости в названии — как есть."""
     split = split_title(reference)
     if split is None:
-        return reference.identity.title or ''
+        return reference.identity.title or 'XXXX'
     head, tail = split
     other_tails = [other_split[1] for other in others if (other_split := split_title(other))]
     return ' '.join([*head, *merge_tails(tail, other_tails)])
```

### `parsers.common_price.group_title.x__reference_key__mutmut_1`

Статус: **survived**; тип: `to_none`; выбрано тестов: 18.

```diff
--- src/parsers/common_price/group_title.py
+++ src/parsers/common_price/group_title.py
@@ -1,6 +1,6 @@
 def _reference_key(group: list[RowItem], priority: Mapping[str, int]) -> _SortKey:
     """Ключ выбора эталона: выше очередь, полнее модель (нет моделей — длиннее название), название по алфавиту."""
-    has_models = any(_model_size(row_item) for row_item in group)
+    has_models = None
 
     def key(row_item: RowItem) -> tuple[int, int, str]:
         title = row_item.identity.title or ''
```

### `parsers.common_price.group_title.x__reference_key__mutmut_6`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 18.

```diff
--- src/parsers/common_price/group_title.py
+++ src/parsers/common_price/group_title.py
@@ -3,7 +3,7 @@
     has_models = any(_model_size(row_item) for row_item in group)
 
     def key(row_item: RowItem) -> tuple[int, int, str]:
-        title = row_item.identity.title or ''
+        title = row_item.identity.title or 'XXXX'
         fullness = _model_size(row_item) if has_models else len(title.split())
         return priority.get(row_item.vendor.supplier_name or '', _NO_PRIORITY), -fullness, title
 
```

### `parsers.common_price.group_title.x__reference_key__mutmut_8`

Статус: **survived**; тип: `other`; выбрано тестов: 18.

```diff
--- src/parsers/common_price/group_title.py
+++ src/parsers/common_price/group_title.py
@@ -4,7 +4,7 @@
 
     def key(row_item: RowItem) -> tuple[int, int, str]:
         title = row_item.identity.title or ''
-        fullness = _model_size(row_item) if has_models else len(title.split())
+        fullness = _model_size(row_item) if (has_models) and False else len(title.split())
         return priority.get(row_item.vendor.supplier_name or '', _NO_PRIORITY), -fullness, title
 
     return key
```

### `parsers.common_price.group_title.x__reference_key__mutmut_16`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 18.

```diff
--- src/parsers/common_price/group_title.py
+++ src/parsers/common_price/group_title.py
@@ -5,6 +5,6 @@
     def key(row_item: RowItem) -> tuple[int, int, str]:
         title = row_item.identity.title or ''
         fullness = _model_size(row_item) if has_models else len(title.split())
-        return priority.get(row_item.vendor.supplier_name or '', _NO_PRIORITY), -fullness, title
+        return priority.get(row_item.vendor.supplier_name or 'XXXX', _NO_PRIORITY), -fullness, title
 
     return key
```

## src/parsers/common_price/grouper.py

### `parsers.common_price.grouper.xǁCommonPriceGrouperǁ__init____mutmut_3`

Статус: **survived**; тип: `other`; выбрано тестов: 85.

```diff
--- src/parsers/common_price/grouper.py
+++ src/parsers/common_price/grouper.py
@@ -6,7 +6,7 @@
         priority_suppliers: tuple[str, ...] = (),
     ):
         self.row_items = row_items
-        self._aliases_map = {} if aliases_map is None else aliases_map
+        self._aliases_map = {} if (aliases_map is None) and False else aliases_map
         self._reference_priority = {} if reference_priority is None else reference_priority
         self._priority_suppliers = priority_suppliers
         self._is_grouped = False
```

### `parsers.common_price.grouper.xǁCommonPriceGrouperǁ__init____mutmut_8`

Статус: **survived**; тип: `other`; выбрано тестов: 85.

```diff
--- src/parsers/common_price/grouper.py
+++ src/parsers/common_price/grouper.py
@@ -7,6 +7,6 @@
     ):
         self.row_items = row_items
         self._aliases_map = {} if aliases_map is None else aliases_map
-        self._reference_priority = {} if reference_priority is None else reference_priority
+        self._reference_priority = {} if (reference_priority is None) or True else reference_priority
         self._priority_suppliers = priority_suppliers
         self._is_grouped = False
```

### `parsers.common_price.grouper.xǁCommonPriceGrouperǁ__init____mutmut_11`

Статус: **survived**; тип: `to_none`; выбрано тестов: 85.

```diff
--- src/parsers/common_price/grouper.py
+++ src/parsers/common_price/grouper.py
@@ -9,4 +9,4 @@
         self._aliases_map = {} if aliases_map is None else aliases_map
         self._reference_priority = {} if reference_priority is None else reference_priority
         self._priority_suppliers = priority_suppliers
-        self._is_grouped = False
+        self._is_grouped = None
```

### `parsers.common_price.grouper.x__optional_parts__mutmut_8`

Статус: **survived**; тип: `method_swap`; выбрано тестов: 78.

```diff
--- src/parsers/common_price/grouper.py
+++ src/parsers/common_price/grouper.py
@@ -4,6 +4,6 @@
     numbers = [disk.slot_count, disk.pcd1, disk.eet, disk.central_diameter]
     parts = [canon_number(number) for number in numbers]
     parts.append(canon_number(row_item.tire.height_percent))
-    parts.append((disk.color or '').strip().lower())
+    parts.append((disk.color or '').strip().upper())
     parts.append(tube_model(row_item))
     return tuple(parts)
```

## src/parsers/common_price/main_double.py

### `parsers.common_price.main_double.x_is_doubtful_price__mutmut_3`

Статус: **survived**; тип: `keyword`; выбрано тестов: 46.

```diff
--- src/parsers/common_price/main_double.py
+++ src/parsers/common_price/main_double.py
@@ -2,5 +2,5 @@
     """Закупочная цена дубля отклоняется от закупочной цены главного дубля на 5% и более (в любую сторону)."""
     main_price = main_item.pricing.price_opt
     if not main_price:
-        return False
+        return True
     return abs(row_item.pricing.price_opt - main_price) / main_price >= _DOUBTFUL_PRICE_DEVIATION
```

## src/parsers/common_price/model.py

### `parsers.common_price.model.x__lstrip_brand_prefix__mutmut_8`

Статус: **survived**; тип: `to_none`; выбрано тестов: 128.

```diff
--- src/parsers/common_price/model.py
+++ src/parsers/common_price/model.py
@@ -6,5 +6,5 @@
     if not rest:
         return ''
     if rest[0] in _PREFIX_SEPARATORS:
-        return rest.lstrip(_PREFIX_SEPARATORS)
+        return rest.lstrip(None)
     return model
```

### `parsers.common_price.model.x_model_tokens__mutmut_4`

Статус: **survived**; тип: `to_none`; выбрано тестов: 94.

```diff
--- src/parsers/common_price/model.py
+++ src/parsers/common_price/model.py
@@ -7,7 +7,7 @@
     if not model:
         return frozenset()
     normalized = model.lower()
-    for prefix in _model_prefixes(manufacturer, brand):
+    for prefix in _model_prefixes(None, brand):
         normalized = _lstrip_brand_prefix(normalized, prefix)
     words = (_latinize(word.translate(_MODEL_PUNCTUATION)) for word in normalized.split())
     return frozenset(word for word in words if word)
```

### `parsers.common_price.model.x_model_tokens__mutmut_5`

Статус: **survived**; тип: `to_none`; выбрано тестов: 94.

```diff
--- src/parsers/common_price/model.py
+++ src/parsers/common_price/model.py
@@ -7,7 +7,7 @@
     if not model:
         return frozenset()
     normalized = model.lower()
-    for prefix in _model_prefixes(manufacturer, brand):
+    for prefix in _model_prefixes(manufacturer, None):
         normalized = _lstrip_brand_prefix(normalized, prefix)
     words = (_latinize(word.translate(_MODEL_PUNCTUATION)) for word in normalized.split())
     return frozenset(word for word in words if word)
```

## src/parsers/common_price/model_keys.py

### `parsers.common_price.model_keys.x__core_key__mutmut_3`

Статус: **survived**; тип: `number`; выбрано тестов: 78.

```diff
--- src/parsers/common_price/model_keys.py
+++ src/parsers/common_price/model_keys.py
@@ -1,3 +1,3 @@
 def _core_key(key: GroupKey) -> GroupKey:
     """Ключ без модели: по нему модели сравниваются между собой."""
-    return key[:MODEL_KEY_INDEX] + key[MODEL_KEY_INDEX + 1 :]
+    return key[:MODEL_KEY_INDEX] + key[MODEL_KEY_INDEX + 2 :]
```

### `parsers.common_price.model_keys.x__replace_model__mutmut_5`

Статус: **survived**; тип: `other`; выбрано тестов: 78.

```diff
--- src/parsers/common_price/model_keys.py
+++ src/parsers/common_price/model_keys.py
@@ -1,5 +1,5 @@
 def _replace_model(key: GroupKey, canonical: dict[str, str]) -> GroupKey:
     """Подставить в ключ каноническую модель; модели без записи в карте остаются как есть."""
     parts = list(key)
-    parts[MODEL_KEY_INDEX] = canonical.get(key[MODEL_KEY_INDEX], key[MODEL_KEY_INDEX])
+    parts[MODEL_KEY_INDEX] = canonical.get(key[MODEL_KEY_INDEX], None)
     return tuple(parts)
```

### `parsers.common_price.model_keys.x__replace_model__mutmut_6`

Статус: **survived**; тип: `other`; выбрано тестов: 78.

```diff
--- src/parsers/common_price/model_keys.py
+++ src/parsers/common_price/model_keys.py
@@ -1,5 +1,5 @@
 def _replace_model(key: GroupKey, canonical: dict[str, str]) -> GroupKey:
     """Подставить в ключ каноническую модель; модели без записи в карте остаются как есть."""
     parts = list(key)
-    parts[MODEL_KEY_INDEX] = canonical.get(key[MODEL_KEY_INDEX], key[MODEL_KEY_INDEX])
+    parts[MODEL_KEY_INDEX] = canonical.get(key[MODEL_KEY_INDEX])
     return tuple(parts)
```

### `parsers.common_price.model_keys.x__replace_model__mutmut_7`

Статус: **survived**; тип: `other`; выбрано тестов: 78.

```diff
--- src/parsers/common_price/model_keys.py
+++ src/parsers/common_price/model_keys.py
@@ -1,5 +1,5 @@
 def _replace_model(key: GroupKey, canonical: dict[str, str]) -> GroupKey:
     """Подставить в ключ каноническую модель; модели без записи в карте остаются как есть."""
     parts = list(key)
-    parts[MODEL_KEY_INDEX] = canonical.get(key[MODEL_KEY_INDEX], key[MODEL_KEY_INDEX])
+    parts[MODEL_KEY_INDEX] = canonical.get(key[MODEL_KEY_INDEX], )
     return tuple(parts)
```

### `parsers.common_price.model_keys.x__tokens__mutmut_11`

Статус: **survived**; тип: `other`; выбрано тестов: 78.

```diff
--- src/parsers/common_price/model_keys.py
+++ src/parsers/common_price/model_keys.py
@@ -7,4 +7,4 @@
     """
     identity = row_item.identity
     model = _ALIAS_SUFFIX.sub('', identity.model) if identity.model else identity.model
-    return model_tokens(model, identity.manufacturer, identity.brand)
+    return model_tokens(model, None, identity.brand)
```

### `parsers.common_price.model_keys.x__tokens__mutmut_12`

Статус: **survived**; тип: `other`; выбрано тестов: 78.

```diff
--- src/parsers/common_price/model_keys.py
+++ src/parsers/common_price/model_keys.py
@@ -7,4 +7,4 @@
     """
     identity = row_item.identity
     model = _ALIAS_SUFFIX.sub('', identity.model) if identity.model else identity.model
-    return model_tokens(model, identity.manufacturer, identity.brand)
+    return model_tokens(model, identity.manufacturer, None)
```

### `parsers.common_price.model_keys.x__tokens__mutmut_14`

Статус: **survived**; тип: `other`; выбрано тестов: 78.

```diff
--- src/parsers/common_price/model_keys.py
+++ src/parsers/common_price/model_keys.py
@@ -7,4 +7,4 @@
     """
     identity = row_item.identity
     model = _ALIAS_SUFFIX.sub('', identity.model) if identity.model else identity.model
-    return model_tokens(model, identity.manufacturer, identity.brand)
+    return model_tokens(model, identity.brand)
```

### `parsers.common_price.model_keys.x__tokens__mutmut_15`

Статус: **survived**; тип: `other`; выбрано тестов: 78.

```diff
--- src/parsers/common_price/model_keys.py
+++ src/parsers/common_price/model_keys.py
@@ -7,4 +7,4 @@
     """
     identity = row_item.identity
     model = _ALIAS_SUFFIX.sub('', identity.model) if identity.model else identity.model
-    return model_tokens(model, identity.manufacturer, identity.brand)
+    return model_tokens(model, identity.manufacturer, )
```

## src/parsers/common_price/model_merge.py

### `parsers.common_price.model_merge.x__split_pair__mutmut_3`

Статус: **survived**; тип: `method_swap`; выбрано тестов: 8.

```diff
--- src/parsers/common_price/model_merge.py
+++ src/parsers/common_price/model_merge.py
@@ -1,7 +1,7 @@
 def _split_pair(word: str, unmatched: set[str]) -> tuple[str, str] | None:
     """Две раздельные части из `unmatched`, дающие `word` при склейке."""
     for first in unmatched:
-        second = word.removeprefix(first)
+        second = word.removesuffix(first)
         if second not in {word, first} and second in unmatched:
             return first, second
     return None
```

### `parsers.common_price.model_merge.x__split_pair__mutmut_4`

Статус: **survived**; тип: `operator`; выбрано тестов: 8.

```diff
--- src/parsers/common_price/model_merge.py
+++ src/parsers/common_price/model_merge.py
@@ -2,6 +2,6 @@
     """Две раздельные части из `unmatched`, дающие `word` при склейке."""
     for first in unmatched:
         second = word.removeprefix(first)
-        if second not in {word, first} and second in unmatched:
+        if second not in {word, first} or second in unmatched:
             return first, second
     return None
```

### `parsers.common_price.model_merge.x_merge_models__mutmut_2`

Статус: **survived**; тип: `operator`; выбрано тестов: 86.

```diff
--- src/parsers/common_price/model_merge.py
+++ src/parsers/common_price/model_merge.py
@@ -1,6 +1,6 @@
 def merge_models(entries: Iterable[ModelEntry]) -> dict[str, str]:
     """Карта «ключ модели → канонический ключ модели» для моделей одного ядра ключа."""
-    token_sets = {model_key: tokens for model_key, tokens in entries if model_key and tokens}
+    token_sets = {model_key: tokens for model_key, tokens in entries if model_key or tokens}
     canonical = _canonical_keys(token_sets)
     target = partial(_target_tokens, canonical=canonical)
     return {model_key: canonical[target(tokens)] for model_key, tokens in token_sets.items()}
```

## src/parsers/common_price/output.py

### `parsers.common_price.output.xǁCommonPriceOutǁ_write_jsonl__mutmut_3`

Статус: **survived**; тип: `operator`; выбрано тестов: 3.

```diff
--- src/parsers/common_price/output.py
+++ src/parsers/common_price/output.py
@@ -3,7 +3,7 @@
         books: list[WorkbookPlan] = []
         for template in templates:
             rows = self.row_items
-            if template is ForDoubles:
+            if template is not ForDoubles:
                 rows = double_positions(rows, self._settings())
             source = TireOutputSource(TireAndDiskResult(tuple(rows)), self._settings())
             books.extend(
```

### `parsers.common_price.output.xǁCommonPriceOutǁ_write_jsonl__mutmut_13`

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/parsers/common_price/output.py
+++ src/parsers/common_price/output.py
@@ -5,7 +5,7 @@
             rows = self.row_items
             if template is ForDoubles:
                 rows = double_positions(rows, self._settings())
-            source = TireOutputSource(TireAndDiskResult(tuple(rows)), self._settings())
+            source = TireOutputSource(TireAndDiskResult(tuple(rows)), )
             books.extend(
                 prepare_output_plan(
                     [template().output_spec()],
```

### `parsers.common_price.output.xǁCommonPriceOutǁ_write_jsonl__mutmut_19`

Статус: **survived**; тип: `to_none`; выбрано тестов: 3.

```diff
--- src/parsers/common_price/output.py
+++ src/parsers/common_price/output.py
@@ -10,7 +10,7 @@
                 prepare_output_plan(
                     [template().output_spec()],
                     {ProductGroup.TIRE_AND_DISK: source},
-                    current_date=current_date,
+                    current_date=None,
                 )
             )
         return write_plan_jsonl(tuple(books), self._config_provider.result_folder())
```

### `parsers.common_price.output.xǁCommonPriceOutǁ_write_jsonl__mutmut_22`

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/parsers/common_price/output.py
+++ src/parsers/common_price/output.py
@@ -10,7 +10,6 @@
                 prepare_output_plan(
                     [template().output_spec()],
                     {ProductGroup.TIRE_AND_DISK: source},
-                    current_date=current_date,
-                )
+                    )
             )
         return write_plan_jsonl(tuple(books), self._config_provider.result_folder())
```

### `parsers.common_price.output.xǁCommonPriceOutǁ_write_with_template__mutmut_1`

Статус: **survived**; тип: `keyword`; выбрано тестов: 12.

```diff
--- src/parsers/common_price/output.py
+++ src/parsers/common_price/output.py
@@ -3,7 +3,7 @@
         rows: list[RowItem],
         template: type[IWriteTemplate],
         *,
-        as_jsonl: bool = False,
+        as_jsonl: bool = True,
         current_date: str | None = None,
     ) -> str:
         """Записать файл шаблона (xlsx или jsonl) и вернуть путь."""
```

### `parsers.common_price.output.xǁCommonPriceOutǁ_write_with_template__mutmut_5`

Статус: **survived**; тип: `to_none`; выбрано тестов: 12.

```diff
--- src/parsers/common_price/output.py
+++ src/parsers/common_price/output.py
@@ -9,7 +9,7 @@
         """Записать файл шаблона (xlsx или jsonl) и вернуть путь."""
         folder = self._config_provider.result_folder()
         if as_jsonl:
-            validate_outputs([template().output_spec()], {ProductGroup.TIRE_AND_DISK}, current_date=current_date)
+            validate_outputs([template().output_spec()], {ProductGroup.TIRE_AND_DISK}, current_date=None)
             return self._write_jsonl([template], current_date)[0]
         writer = GroupFileWriter(
             xls_writer=self.xls_writer,
```

### `parsers.common_price.output.xǁCommonPriceOutǁ_write_with_template__mutmut_8`

Статус: **survived**; тип: `other`; выбрано тестов: 12.

```diff
--- src/parsers/common_price/output.py
+++ src/parsers/common_price/output.py
@@ -9,7 +9,7 @@
         """Записать файл шаблона (xlsx или jsonl) и вернуть путь."""
         folder = self._config_provider.result_folder()
         if as_jsonl:
-            validate_outputs([template().output_spec()], {ProductGroup.TIRE_AND_DISK}, current_date=current_date)
+            validate_outputs([template().output_spec()], {ProductGroup.TIRE_AND_DISK}, )
             return self._write_jsonl([template], current_date)[0]
         writer = GroupFileWriter(
             xls_writer=self.xls_writer,
```

### `parsers.common_price.output.xǁCommonPriceOutǁ_write_with_template__mutmut_10`

Статус: **survived**; тип: `to_none`; выбрано тестов: 12.

```diff
--- src/parsers/common_price/output.py
+++ src/parsers/common_price/output.py
@@ -10,7 +10,7 @@
         folder = self._config_provider.result_folder()
         if as_jsonl:
             validate_outputs([template().output_spec()], {ProductGroup.TIRE_AND_DISK}, current_date=current_date)
-            return self._write_jsonl([template], current_date)[0]
+            return self._write_jsonl([template], None)[0]
         writer = GroupFileWriter(
             xls_writer=self.xls_writer,
             write_driver=self.write_driver,
```

### `parsers.common_price.output.xǁCommonPriceOutǁnomenclature_title_correction__mutmut_10`

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/parsers/common_price/output.py
+++ src/parsers/common_price/output.py
@@ -4,4 +4,4 @@
             title = row_item.identity.title
             if title is None:
                 continue
-            row_item.set_field('title', get_nomenclature_corrected_title(title, self._config_provider))
+            row_item.set_field('title', get_nomenclature_corrected_title(title, None))
```

### `parsers.common_price.output.xǁCommonPriceOutǁwrite_all_prices__mutmut_7`

Статус: **survived**; тип: `to_none`; выбрано тестов: 12.

```diff
--- src/parsers/common_price/output.py
+++ src/parsers/common_price/output.py
@@ -13,7 +13,7 @@
         validate_outputs(
             [template().output_spec() for template in (*templates, ForDoubles)],
             {ProductGroup.TIRE_AND_DISK},
-            current_date=current_date,
+            current_date=None,
         )
         clear_nomenclature_cache()
         self.nomenclature_title_correction()
```

### `parsers.common_price.output.xǁCommonPriceOutǁwrite_all_prices__mutmut_10`

Статус: **survived**; тип: `other`; выбрано тестов: 12.

```diff
--- src/parsers/common_price/output.py
+++ src/parsers/common_price/output.py
@@ -13,8 +13,7 @@
         validate_outputs(
             [template().output_spec() for template in (*templates, ForDoubles)],
             {ProductGroup.TIRE_AND_DISK},
-            current_date=current_date,
-        )
+            )
         clear_nomenclature_cache()
         self.nomenclature_title_correction()
         if as_jsonl:
```

### `parsers.common_price.output.xǁCommonPriceOutǁwrite_all_prices__mutmut_13`

Статус: **survived**; тип: `to_none`; выбрано тестов: 12.

```diff
--- src/parsers/common_price/output.py
+++ src/parsers/common_price/output.py
@@ -18,7 +18,7 @@
         clear_nomenclature_cache()
         self.nomenclature_title_correction()
         if as_jsonl:
-            return jsonl_output_files(self._write_jsonl([*templates, ForDoubles], current_date))
+            return jsonl_output_files(self._write_jsonl([*templates, ForDoubles], None))
         written = [
             self._write_with_template(
                 self.row_items,
```

### `parsers.common_price.output.xǁCommonPriceOutǁwrite_all_prices__mutmut_19`

Статус: **survived**; тип: `to_none`; выбрано тестов: 12.

```diff
--- src/parsers/common_price/output.py
+++ src/parsers/common_price/output.py
@@ -23,7 +23,7 @@
             self._write_with_template(
                 self.row_items,
                 write_template,
-                as_jsonl=as_jsonl,
+                as_jsonl=None,
                 current_date=current_date,
             )
             for write_template in templates
```

### `parsers.common_price.output.xǁCommonPriceOutǁwrite_all_prices__mutmut_23`

Статус: **survived**; тип: `other`; выбрано тестов: 12.

```diff
--- src/parsers/common_price/output.py
+++ src/parsers/common_price/output.py
@@ -23,7 +23,6 @@
             self._write_with_template(
                 self.row_items,
                 write_template,
-                as_jsonl=as_jsonl,
                 current_date=current_date,
             )
             for write_template in templates
```

### `parsers.common_price.output.xǁCommonPriceOutǁwrite_all_prices__mutmut_26`

Статус: **survived**; тип: `to_none`; выбрано тестов: 12.

```diff
--- src/parsers/common_price/output.py
+++ src/parsers/common_price/output.py
@@ -28,5 +28,5 @@
             )
             for write_template in templates
         ]
-        written.append(self.write_doubles_report(as_jsonl=as_jsonl, current_date=current_date))
+        written.append(self.write_doubles_report(as_jsonl=None, current_date=current_date))
         return written
```

### `parsers.common_price.output.xǁCommonPriceOutǁwrite_all_prices__mutmut_28`

Статус: **survived**; тип: `other`; выбрано тестов: 12.

```diff
--- src/parsers/common_price/output.py
+++ src/parsers/common_price/output.py
@@ -28,5 +28,5 @@
             )
             for write_template in templates
         ]
-        written.append(self.write_doubles_report(as_jsonl=as_jsonl, current_date=current_date))
+        written.append(self.write_doubles_report(current_date=current_date))
         return written
```

## src/parsers/common_price/size.py

### `parsers.common_price.size.x_canon_diameter__mutmut_13`

Статус: **survived**; тип: `other`; выбрано тестов: 150.

```diff
--- src/parsers/common_price/size.py
+++ src/parsers/common_price/size.py
@@ -3,5 +3,5 @@
     text = str(raw or '').strip()
     if not text:
         return ''
-    text = _DIAMETER_PREFIX_RE.sub('', text, count=1)
+    text = _DIAMETER_PREFIX_RE.sub('', text, )
     return canon_number(_DIAMETER_SUFFIX_RE.sub('', text, count=1))
```

### `parsers.common_price.size.x_canon_diameter__mutmut_15`

Статус: **survived**; тип: `number`; выбрано тестов: 150.

```diff
--- src/parsers/common_price/size.py
+++ src/parsers/common_price/size.py
@@ -3,5 +3,5 @@
     text = str(raw or '').strip()
     if not text:
         return ''
-    text = _DIAMETER_PREFIX_RE.sub('', text, count=1)
+    text = _DIAMETER_PREFIX_RE.sub('', text, count=2)
     return canon_number(_DIAMETER_SUFFIX_RE.sub('', text, count=1))
```

### `parsers.common_price.size.x_canon_diameter__mutmut_22`

Статус: **survived**; тип: `other`; выбрано тестов: 150.

```diff
--- src/parsers/common_price/size.py
+++ src/parsers/common_price/size.py
@@ -4,4 +4,4 @@
     if not text:
         return ''
     text = _DIAMETER_PREFIX_RE.sub('', text, count=1)
-    return canon_number(_DIAMETER_SUFFIX_RE.sub('', text, count=1))
+    return canon_number(_DIAMETER_SUFFIX_RE.sub('', text, ))
```

### `parsers.common_price.size.x_canon_diameter__mutmut_24`

Статус: **survived**; тип: `number`; выбрано тестов: 150.

```diff
--- src/parsers/common_price/size.py
+++ src/parsers/common_price/size.py
@@ -4,4 +4,4 @@
     if not text:
         return ''
     text = _DIAMETER_PREFIX_RE.sub('', text, count=1)
-    return canon_number(_DIAMETER_SUFFIX_RE.sub('', text, count=1))
+    return canon_number(_DIAMETER_SUFFIX_RE.sub('', text, count=2))
```

### `parsers.common_price.size.x_canon_number__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 157.

```diff
--- src/parsers/common_price/size.py
+++ src/parsers/common_price/size.py
@@ -1,6 +1,6 @@
 def canon_number(raw: Any) -> str:
     """Запятая → точка; 12.50 и 12.5 — одно число."""
-    if raw is None or raw == '':
+    if raw is None or raw == 'XXXX':
         return ''
     text = str(raw).replace(',', '.').strip()
     if not text:
```

## src/parsers/common_price/tire_output.py

### `parsers.common_price.tire_output.xǁTireOutputSourceǁ_correct_titles__mutmut_2`

Статус: **survived**; тип: `operator`; выбрано тестов: 78.

```diff
--- src/parsers/common_price/tire_output.py
+++ src/parsers/common_price/tire_output.py
@@ -1,5 +1,5 @@
     def _correct_titles(self, rows: list[RowItem]) -> None:
         if self.title_correction is not None:
             for row in rows:
-                if row.identity.title is not None:
+                if row.identity.title is None:
                     row.set_field('title', self.title_correction(row.identity.title))
```

### `parsers.common_price.tire_output.xǁTireOutputSourceǁ_correct_titles__mutmut_3`

Статус: **survived**; тип: `other`; выбрано тестов: 78.

```diff
--- src/parsers/common_price/tire_output.py
+++ src/parsers/common_price/tire_output.py
@@ -2,4 +2,4 @@
         if self.title_correction is not None:
             for row in rows:
                 if row.identity.title is not None:
-                    row.set_field('title', self.title_correction(row.identity.title))
+                    row.set_field(None, self.title_correction(row.identity.title))
```

### `parsers.common_price.tire_output.xǁTireOutputSourceǁ_correct_titles__mutmut_4`

Статус: **survived**; тип: `other`; выбрано тестов: 78.

```diff
--- src/parsers/common_price/tire_output.py
+++ src/parsers/common_price/tire_output.py
@@ -2,4 +2,4 @@
         if self.title_correction is not None:
             for row in rows:
                 if row.identity.title is not None:
-                    row.set_field('title', self.title_correction(row.identity.title))
+                    row.set_field('title', None)
```

### `parsers.common_price.tire_output.xǁTireOutputSourceǁ_correct_titles__mutmut_7`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 78.

```diff
--- src/parsers/common_price/tire_output.py
+++ src/parsers/common_price/tire_output.py
@@ -2,4 +2,4 @@
         if self.title_correction is not None:
             for row in rows:
                 if row.identity.title is not None:
-                    row.set_field('title', self.title_correction(row.identity.title))
+                    row.set_field('XXtitleXX', self.title_correction(row.identity.title))
```

### `parsers.common_price.tire_output.xǁTireOutputSourceǁ_correct_titles__mutmut_8`

Статус: **survived**; тип: `string_case`; выбрано тестов: 78.

```diff
--- src/parsers/common_price/tire_output.py
+++ src/parsers/common_price/tire_output.py
@@ -2,4 +2,4 @@
         if self.title_correction is not None:
             for row in rows:
                 if row.identity.title is not None:
-                    row.set_field('title', self.title_correction(row.identity.title))
+                    row.set_field('TITLE', self.title_correction(row.identity.title))
```

### `parsers.common_price.tire_output.xǁTireOutputSourceǁ_correct_titles__mutmut_9`

Статус: **survived**; тип: `other`; выбрано тестов: 78.

```diff
--- src/parsers/common_price/tire_output.py
+++ src/parsers/common_price/tire_output.py
@@ -2,4 +2,4 @@
         if self.title_correction is not None:
             for row in rows:
                 if row.identity.title is not None:
-                    row.set_field('title', self.title_correction(row.identity.title))
+                    row.set_field('title', self.title_correction(None))
```

### `parsers.common_price.tire_output.xǁTireOutputSourceǁpositions_for__mutmut_3`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 78.

```diff
--- src/parsers/common_price/tire_output.py
+++ src/parsers/common_price/tire_output.py
@@ -1,7 +1,7 @@
     def positions_for(self, template_id: str, settings: GroupOutput) -> list[RowItem]:
         """Применить правила вывода к модели до передачи её сериализатору."""
         if settings.id != self.package.product_group:
-            raise ValueError('Преобразователь tire_and_disk получил настройки другой группы')
+            raise ValueError('XXПреобразователь tire_and_disk получил настройки другой группыXX')
         rows = list(self.package.positions)
         self._correct_titles(rows)
         if template_id == 'for_doubles':
```

### `parsers.common_price.tire_output.xǁTireOutputSourceǁpositions_for__mutmut_4`

Статус: **survived**; тип: `string_case`; выбрано тестов: 78.

```diff
--- src/parsers/common_price/tire_output.py
+++ src/parsers/common_price/tire_output.py
@@ -1,7 +1,7 @@
     def positions_for(self, template_id: str, settings: GroupOutput) -> list[RowItem]:
         """Применить правила вывода к модели до передачи её сериализатору."""
         if settings.id != self.package.product_group:
-            raise ValueError('Преобразователь tire_and_disk получил настройки другой группы')
+            raise ValueError('преобразователь tire_and_disk получил настройки другой группы')
         rows = list(self.package.positions)
         self._correct_titles(rows)
         if template_id == 'for_doubles':
```

## src/parsers/common_price/title_flags.py

### `parsers.common_price.title_flags.x__kind__mutmut_3`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 146.

```diff
--- src/parsers/common_price/title_flags.py
+++ src/parsers/common_price/title_flags.py
@@ -1,2 +1,2 @@
 def _kind(row_item: RowItem) -> str:
-    return (row_item.vendor.type_production or '').lower()
+    return (row_item.vendor.type_production or 'XXXX').lower()
```

### `parsers.common_price.title_flags.x_has_valve__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 123.

```diff
--- src/parsers/common_price/title_flags.py
+++ src/parsers/common_price/title_flags.py
@@ -1,3 +1,3 @@
 def has_valve(title: str | None) -> bool:
     """В названии указан вентиль (`с вентилем`)."""
-    return bool(_VALVE_RE.search(title or ''))
+    return bool(_VALVE_RE.search(title or 'XXXX'))
```

### `parsers.common_price.title_flags.x_tube_model_from_title__mutmut_7`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 25.

```diff
--- src/parsers/common_price/title_flags.py
+++ src/parsers/common_price/title_flags.py
@@ -1,5 +1,5 @@
 def tube_model_from_title(title: str | None, *, is_rim_tape: bool) -> str:
     """Модель камеры (`ГК-145`) или ободной ленты (`300-508А`) из названия; пусто, если не указана."""
     pattern = _RIM_TAPE_MODEL_RE if is_rim_tape else _CAMERA_MODEL_RE
-    match = pattern.search(title or '')
+    match = pattern.search(title or 'XXXX')
     return ''.join(match[1].split()).upper() if match else ''
```

## src/parsers/common_price/title_tail.py

### `parsers.common_price.title_tail.x__is_addable__mutmut_3`

Статус: **survived**; тип: `operator`; выбрано тестов: 4.

```diff
--- src/parsers/common_price/title_tail.py
+++ src/parsers/common_price/title_tail.py
@@ -1,2 +1,2 @@
 def _is_addable(rank: int, taken: set[int]) -> bool:
-    return rank in _SET_RANKS or (rank in _SINGLE_RANKS and rank not in taken)
+    return rank in _SET_RANKS or (rank in _SINGLE_RANKS or rank not in taken)
```

### `parsers.common_price.title_tail.x__rank__mutmut_6`

Статус: **survived**; тип: `number`; выбрано тестов: 4.

```diff
--- src/parsers/common_price/title_tail.py
+++ src/parsers/common_price/title_tail.py
@@ -2,4 +2,4 @@
     """Место слова хвоста в каноническом порядке; незнакомые слова (0) остаются впереди."""
     if _LAYERING.fullmatch(word):
         return _LAYERING_RANK
-    return _FIXED_RANKS.get(word, 0)
+    return _FIXED_RANKS.get(word, 1)
```

### `parsers.common_price.title_tail.x__tail_start__mutmut_7`

Статус: **survived**; тип: `operator`; выбрано тестов: 18.

```diff
--- src/parsers/common_price/title_tail.py
+++ src/parsers/common_price/title_tail.py
@@ -3,4 +3,4 @@
     positions = [position for position, word in enumerate(words) if word == load]
     if not load or not positions:
         return None
-    return positions[-1] + 1
+    return positions[-1] - 1
```

### `parsers.common_price.title_tail.x_merge_tails__mutmut_8`

Статус: **survived**; тип: `operator`; выбрано тестов: 9.

```diff
--- src/parsers/common_price/title_tail.py
+++ src/parsers/common_price/title_tail.py
@@ -4,7 +4,7 @@
     taken = {_rank(word) for word in merged}
     for word in chain.from_iterable(others):
         rank = _rank(word)
-        if _is_addable(rank, taken) and word not in merged:
+        if _is_addable(rank, taken) or word not in merged:
             merged.append(word)
             taken.add(rank)
     return sorted(merged, key=_rank)
```

### `parsers.common_price.title_tail.x_merge_tails__mutmut_15`

Статус: **survived**; тип: `to_none`; выбрано тестов: 9.

```diff
--- src/parsers/common_price/title_tail.py
+++ src/parsers/common_price/title_tail.py
@@ -6,5 +6,5 @@
         rank = _rank(word)
         if _is_addable(rank, taken) and word not in merged:
             merged.append(word)
-            taken.add(rank)
+            taken.add(None)
     return sorted(merged, key=_rank)
```

### `parsers.common_price.title_tail.x_split_title__mutmut_3`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 18.

```diff
--- src/parsers/common_price/title_tail.py
+++ src/parsers/common_price/title_tail.py
@@ -1,6 +1,6 @@
 def split_title(row_item: RowItem) -> TitleSplit | None:
     """Название шины: слова до нагрузки+скорости включительно и слова хвоста; нет такого токена — None."""
-    words = (row_item.identity.title or '').split()
+    words = (row_item.identity.title or 'XXXX').split()
     end = _tail_start(words, load_velocity(row_item))
     if end is None:
         return None
```

## src/parsers/common_price/warehouses.py

### `parsers.common_price.warehouses.x__merge_key__mutmut_7`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 81.

```diff
--- src/parsers/common_price/warehouses.py
+++ src/parsers/common_price/warehouses.py
@@ -4,4 +4,4 @@
     code = row_item.identity.code
     if not group or not code:
         return None
-    return row_item.product_group, row_item.vendor.supplier_name or '', code, group
+    return row_item.product_group, row_item.vendor.supplier_name or 'XXXX', code, group
```

### `parsers.common_price.warehouses.x_cheapest_with_summed_rest__mutmut_18`

Статус: **survived**; тип: `number`; выбрано тестов: 84.

```diff
--- src/parsers/common_price/warehouses.py
+++ src/parsers/common_price/warehouses.py
@@ -7,6 +7,6 @@
     if len(cheapest) == 1:
         return cheapest[0]
     total_rest = sum(row.stock.rest_count or 0 for row in cheapest)
-    merged = deepcopy(cheapest[0])
+    merged = deepcopy(cheapest[1])
     merged.set_field('rest_count', total_rest)
     return merged
```

## src/parsers/data_provider/manufacturer_aliases.py

### `parsers.data_provider.manufacturer_aliases.x_aliases_for_finder__mutmut_5`

Статус: **survived**; тип: `to_none`; выбрано тестов: 55.

```diff
--- src/parsers/data_provider/manufacturer_aliases.py
+++ src/parsers/data_provider/manufacturer_aliases.py
@@ -6,7 +6,7 @@
     for brand, entry in aliases_map.items():
         raw: Any = entry
         if isinstance(entry, dict):
-            raw = entry.get('aliases', [])
+            raw = entry.get('aliases', None)
         if isinstance(raw, str):
             raw = [raw]
         if isinstance(raw, tuple):
```

### `parsers.data_provider.manufacturer_aliases.x_aliases_for_finder__mutmut_7`

Статус: **survived**; тип: `other`; выбрано тестов: 55.

```diff
--- src/parsers/data_provider/manufacturer_aliases.py
+++ src/parsers/data_provider/manufacturer_aliases.py
@@ -6,7 +6,7 @@
     for brand, entry in aliases_map.items():
         raw: Any = entry
         if isinstance(entry, dict):
-            raw = entry.get('aliases', [])
+            raw = entry.get('aliases', )
         if isinstance(raw, str):
             raw = [raw]
         if isinstance(raw, tuple):
```

## src/parsers/data_provider/manufacturer_group.py

### `parsers.data_provider.manufacturer_group.x_manufacturer_group__mutmut_4`

Статус: **survived**; тип: `operator`; выбрано тестов: 140.

```diff
--- src/parsers/data_provider/manufacturer_group.py
+++ src/parsers/data_provider/manufacturer_group.py
@@ -4,7 +4,7 @@
 ) -> str:
     """Canon for grouping: JSON group, alias owner, or the brand key in lowercase."""
     name = (manufacturer or '').strip()
-    if not name or not aliases_map:
+    if not name and not aliases_map:
         return name.lower()
     if aliases_map is not _GROUP_CACHE[0]:
         _GROUP_CACHE[1] = _build_lookup(aliases_map)
```

## src/parsers/load_supplier_prices.py

### `parsers.load_supplier_prices.x__plan_upload__mutmut_2`

Статус: **survived**; тип: `to_none`; выбрано тестов: 31.

```diff
--- src/parsers/load_supplier_prices.py
+++ src/parsers/load_supplier_prices.py
@@ -1,6 +1,6 @@
 def _plan_upload(
     folder: str, sources: PriceSources, unpack_dir: Path, config_provider: ConfigProvider
 ) -> SupplierUpload:
-    rules = vendor_file_rules(config_provider)[folder]
+    rules = vendor_file_rules(None)[folder]
     files = plan_files(folder, rules, expand_sources(sources, unpack_dir))
     return SupplierUpload(folder, rules, files)
```

### `parsers.load_supplier_prices.x__supplier_folders__mutmut_13`

Статус: **survived**; тип: `to_none`; выбрано тестов: 34.

```diff
--- src/parsers/load_supplier_prices.py
+++ src/parsers/load_supplier_prices.py
@@ -4,4 +4,4 @@
     """Папка поставщика для каждого ключа; неизвестный ключ — ошибка до проверки файлов."""
     catalog = all_vendor_supplier_catalog(config_provider)
     folders = [catalog_entry_for(key, catalog)['sup_code'] for key in mapping]
-    return list(zip(folders, mapping.values(), strict=True))
+    return list(zip(folders, mapping.values(), strict=None))
```

### `parsers.load_supplier_prices.x__supplier_folders__mutmut_16`

Статус: **survived**; тип: `other`; выбрано тестов: 34.

```diff
--- src/parsers/load_supplier_prices.py
+++ src/parsers/load_supplier_prices.py
@@ -4,4 +4,4 @@
     """Папка поставщика для каждого ключа; неизвестный ключ — ошибка до проверки файлов."""
     catalog = all_vendor_supplier_catalog(config_provider)
     folders = [catalog_entry_for(key, catalog)['sup_code'] for key in mapping]
-    return list(zip(folders, mapping.values(), strict=True))
+    return list(zip(folders, mapping.values(), ))
```

### `parsers.load_supplier_prices.x__supplier_folders__mutmut_17`

Статус: **survived**; тип: `keyword`; выбрано тестов: 34.

```diff
--- src/parsers/load_supplier_prices.py
+++ src/parsers/load_supplier_prices.py
@@ -4,4 +4,4 @@
     """Папка поставщика для каждого ключа; неизвестный ключ — ошибка до проверки файлов."""
     catalog = all_vendor_supplier_catalog(config_provider)
     folders = [catalog_entry_for(key, catalog)['sup_code'] for key in mapping]
-    return list(zip(folders, mapping.values(), strict=True))
+    return list(zip(folders, mapping.values(), strict=False))
```

### `parsers.load_supplier_prices.x_load_supplier_prices__mutmut_10`

Статус: **survived**; тип: `to_none`; выбрано тестов: 34.

```diff
--- src/parsers/load_supplier_prices.py
+++ src/parsers/load_supplier_prices.py
@@ -2,5 +2,5 @@
     """Разложить файлы по папкам поставщиков; вернуть пути положенных файлов."""
     targets = _supplier_folders(mapping, config_provider)
     with unpacked_dir() as unpack_dir:
-        uploads = [_plan_upload(folder, sources, unpack_dir, config_provider) for folder, sources in targets]
+        uploads = [_plan_upload(folder, sources, unpack_dir, None) for folder, sources in targets]
         return [dest for upload in uploads for dest in place_files(upload, config_provider)]
```

## src/parsers/mail/body.py

### `parsers.mail.body.x__part_text__mutmut_10`

Классификация 2026-11-14: Эквивалент: При заданной кодировке она не меняется. При отсутствующей кодировке неизвестная XXutf-8XX вызывает LookupError, который уже перехватывается: fallback декодирует те же bytes тем же utf-8 с тем же errors=replace. Изменяется только внутренний путь до идентичного результата. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 13.

```diff
--- src/parsers/mail/body.py
+++ src/parsers/mail/body.py
@@ -4,6 +4,6 @@
     if not isinstance(payload, bytes):
         return None
     try:
-        return payload.decode(part.get_content_charset() or 'utf-8', 'replace')
+        return payload.decode(part.get_content_charset() or 'XXutf-8XX', 'replace')
     except LookupError:
         return payload.decode('utf-8', 'replace')
```

### `parsers.mail.body.x__part_text__mutmut_11`

Классификация 2026-11-14: Эквивалент: UTF-8 и utf-8 разрешаются Python в один кодек; payload и errors=replace сохранены. Это верно и для основного декодирования, и для fallback после неизвестной кодировки. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_case`; выбрано тестов: 13.

```diff
--- src/parsers/mail/body.py
+++ src/parsers/mail/body.py
@@ -4,6 +4,6 @@
     if not isinstance(payload, bytes):
         return None
     try:
-        return payload.decode(part.get_content_charset() or 'utf-8', 'replace')
+        return payload.decode(part.get_content_charset() or 'UTF-8', 'replace')
     except LookupError:
         return payload.decode('utf-8', 'replace')
```

### `parsers.mail.body.x__part_text__mutmut_19`

Классификация 2026-11-14: Эквивалент: UTF-8 и utf-8 разрешаются Python в один кодек; payload и errors=replace сохранены. Это верно и для основного декодирования, и для fallback после неизвестной кодировки. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_case`; выбрано тестов: 13.

```diff
--- src/parsers/mail/body.py
+++ src/parsers/mail/body.py
@@ -6,4 +6,4 @@
     try:
         return payload.decode(part.get_content_charset() or 'utf-8', 'replace')
     except LookupError:
-        return payload.decode('utf-8', 'replace')
+        return payload.decode('UTF-8', 'replace')
```

## src/parsers/mail/client.py

### `parsers.mail.client.x__epoch__mutmut_4`

Классификация 2026-11-14: Эквивалент: float принимает inf без учёта регистра: -inf и -INF дают одну отрицательную бесконечность. Ветка известной даты не меняется; порядок выбора письма сохраняется. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_case`; выбрано тестов: 7.

```diff
--- src/parsers/mail/client.py
+++ src/parsers/mail/client.py
@@ -1,5 +1,5 @@
 def _epoch(when: datetime | None) -> float:
     """Сортируемое время письма; неизвестная дата — как самое старое."""
     if when is None:
-        return float('-inf')
+        return float('-INF')
     return when.timestamp()
```

### `parsers.mail.client.x__price_from_link__mutmut_17`

Классификация 2026-11-14: Эквивалент: По контракту вход — email.message.Message: Message.get приводит к нижнему регистру и имя поиска, и имена сохранённых заголовков. Изменение регистра Subject, Date или From сохраняет выбранный заголовок, его значение и поведение при отсутствии/повторении заголовков. Проверена реализация Message.get в Python 3.14; подмена Message регистрозависимым словарём не соответствует контракту. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_case`; выбрано тестов: 4.

```diff
--- src/parsers/mail/client.py
+++ src/parsers/mail/client.py
@@ -4,7 +4,7 @@
     if link is None:
         return None
     return FoundPrice(
-        subject=decode_header_value(message.get('Subject')),
+        subject=decode_header_value(message.get('subject')),
         date=format_date(message),
         filename=url_filename(link),
         link=link,
```

### `parsers.mail.client.x__price_from_link__mutmut_18`

Классификация 2026-11-14: Эквивалент: По контракту вход — email.message.Message: Message.get приводит к нижнему регистру и имя поиска, и имена сохранённых заголовков. Изменение регистра Subject, Date или From сохраняет выбранный заголовок, его значение и поведение при отсутствии/повторении заголовков. Проверена реализация Message.get в Python 3.14; подмена Message регистрозависимым словарём не соответствует контракту. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_case`; выбрано тестов: 4.

```diff
--- src/parsers/mail/client.py
+++ src/parsers/mail/client.py
@@ -4,7 +4,7 @@
     if link is None:
         return None
     return FoundPrice(
-        subject=decode_header_value(message.get('Subject')),
+        subject=decode_header_value(message.get('SUBJECT')),
         date=format_date(message),
         filename=url_filename(link),
         link=link,
```

### `parsers.mail.client.x__price_from_message__mutmut_39`

Классификация 2026-11-14: Эквивалент: По контракту вход — email.message.Message: Message.get приводит к нижнему регистру и имя поиска, и имена сохранённых заголовков. Изменение регистра Subject, Date или From сохраняет выбранный заголовок, его значение и поведение при отсутствии/повторении заголовков. Проверена реализация Message.get в Python 3.14; подмена Message регистрозависимым словарём не соответствует контракту. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_case`; выбрано тестов: 15.

```diff
--- src/parsers/mail/client.py
+++ src/parsers/mail/client.py
@@ -12,7 +12,7 @@
         return None
     filename, part = attachments[0]
     return FoundPrice(
-        subject=decode_header_value(message.get('Subject')),
+        subject=decode_header_value(message.get('subject')),
         date=format_date(message),
         filename=filename,
         payload=attachment_content(part),
```

### `parsers.mail.client.x__price_from_message__mutmut_40`

Классификация 2026-11-14: Эквивалент: По контракту вход — email.message.Message: Message.get приводит к нижнему регистру и имя поиска, и имена сохранённых заголовков. Изменение регистра Subject, Date или From сохраняет выбранный заголовок, его значение и поведение при отсутствии/повторении заголовков. Проверена реализация Message.get в Python 3.14; подмена Message регистрозависимым словарём не соответствует контракту. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_case`; выбрано тестов: 15.

```diff
--- src/parsers/mail/client.py
+++ src/parsers/mail/client.py
@@ -12,7 +12,7 @@
         return None
     filename, part = attachments[0]
     return FoundPrice(
-        subject=decode_header_value(message.get('Subject')),
+        subject=decode_header_value(message.get('SUBJECT')),
         date=format_date(message),
         filename=filename,
         payload=attachment_content(part),
```

## src/parsers/mail/dates.py

### `parsers.mail.dates.x_format_date__mutmut_7`

Классификация 2026-11-14: Эквивалент: По контракту вход — email.message.Message: Message.get приводит к нижнему регистру и имя поиска, и имена сохранённых заголовков. Изменение регистра Subject, Date или From сохраняет выбранный заголовок, его значение и поведение при отсутствии/повторении заголовков. Проверена реализация Message.get в Python 3.14; подмена Message регистрозависимым словарём не соответствует контракту. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_case`; выбрано тестов: 17.

```diff
--- src/parsers/mail/dates.py
+++ src/parsers/mail/dates.py
@@ -2,5 +2,5 @@
     """Дата письма (заголовок Date) в локальном времени, ``ДД.ММ.ГГГГ ЧЧ:ММ``."""
     moment = message_datetime(message)
     if moment is None:
-        return message.get('Date') or 'дата неизвестна'
+        return message.get('date') or 'дата неизвестна'
     return moment.astimezone().strftime(_DATE_FORMAT)
```

### `parsers.mail.dates.x_format_date__mutmut_8`

Классификация 2026-11-14: Эквивалент: По контракту вход — email.message.Message: Message.get приводит к нижнему регистру и имя поиска, и имена сохранённых заголовков. Изменение регистра Subject, Date или From сохраняет выбранный заголовок, его значение и поведение при отсутствии/повторении заголовков. Проверена реализация Message.get в Python 3.14; подмена Message регистрозависимым словарём не соответствует контракту. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_case`; выбрано тестов: 17.

```diff
--- src/parsers/mail/dates.py
+++ src/parsers/mail/dates.py
@@ -2,5 +2,5 @@
     """Дата письма (заголовок Date) в локальном времени, ``ДД.ММ.ГГГГ ЧЧ:ММ``."""
     moment = message_datetime(message)
     if moment is None:
-        return message.get('Date') or 'дата неизвестна'
+        return message.get('DATE') or 'дата неизвестна'
     return moment.astimezone().strftime(_DATE_FORMAT)
```

### `parsers.mail.dates.x_message_datetime__mutmut_4`

Классификация 2026-11-14: Эквивалент: По контракту вход — email.message.Message: Message.get приводит к нижнему регистру и имя поиска, и имена сохранённых заголовков. Изменение регистра Subject, Date или From сохраняет выбранный заголовок, его значение и поведение при отсутствии/повторении заголовков. Проверена реализация Message.get в Python 3.14; подмена Message регистрозависимым словарём не соответствует контракту. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_case`; выбрано тестов: 20.

```diff
--- src/parsers/mail/dates.py
+++ src/parsers/mail/dates.py
@@ -1,6 +1,6 @@
 def message_datetime(message: Message) -> datetime | None:
     """Момент отправки из заголовка Date; нет или неразобранная дата — None."""
-    raw = message.get('Date')
+    raw = message.get('date')
     if not raw:
         return None
     try:
```

### `parsers.mail.dates.x_message_datetime__mutmut_5`

Классификация 2026-11-14: Эквивалент: По контракту вход — email.message.Message: Message.get приводит к нижнему регистру и имя поиска, и имена сохранённых заголовков. Изменение регистра Subject, Date или From сохраняет выбранный заголовок, его значение и поведение при отсутствии/повторении заголовков. Проверена реализация Message.get в Python 3.14; подмена Message регистрозависимым словарём не соответствует контракту. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_case`; выбрано тестов: 20.

```diff
--- src/parsers/mail/dates.py
+++ src/parsers/mail/dates.py
@@ -1,6 +1,6 @@
 def message_datetime(message: Message) -> datetime | None:
     """Момент отправки из заголовка Date; нет или неразобранная дата — None."""
-    raw = message.get('Date')
+    raw = message.get('DATE')
     if not raw:
         return None
     try:
```

## src/parsers/mail/links.py

### `parsers.mail.links.x_url_filename__mutmut_5`

Классификация 2026-11-14: Эквивалент: rsplit с положительным maxsplit=1, maxsplit=2 и без ограничения даёт один и тот же последний сегмент по разделителю /. Это верно также при отсутствии /, пустом пути и завершающем /. urlsplit и unquote применяются в прежнем порядке. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `other`; выбрано тестов: 8.

```diff
--- src/parsers/mail/links.py
+++ src/parsers/mail/links.py
@@ -1,3 +1,3 @@
 def url_filename(url: str) -> str:
     """Имя файла из последнего сегмента пути ссылки."""
-    return unquote(urlsplit(url).path.rsplit('/', 1)[-1])
+    return unquote(urlsplit(url).path.rsplit('/', )[-1])
```

### `parsers.mail.links.x_url_filename__mutmut_9`

Классификация 2026-11-14: Эквивалент: rsplit с положительным maxsplit=1, maxsplit=2 и без ограничения даёт один и тот же последний сегмент по разделителю /. Это верно также при отсутствии /, пустом пути и завершающем /. urlsplit и unquote применяются в прежнем порядке. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `number`; выбрано тестов: 8.

```diff
--- src/parsers/mail/links.py
+++ src/parsers/mail/links.py
@@ -1,3 +1,3 @@
 def url_filename(url: str) -> str:
     """Имя файла из последнего сегмента пути ссылки."""
-    return unquote(urlsplit(url).path.rsplit('/', 1)[-1])
+    return unquote(urlsplit(url).path.rsplit('/', 2)[-1])
```

## src/parsers/mail/message.py

### `parsers.mail.message.x_sender_matches__mutmut_6`

Классификация 2026-11-14: Эквивалент: По контракту вход — email.message.Message: Message.get приводит к нижнему регистру и имя поиска, и имена сохранённых заголовков. Изменение регистра Subject, Date или From сохраняет выбранный заголовок, его значение и поведение при отсутствии/повторении заголовков. Проверена реализация Message.get в Python 3.14; подмена Message регистрозависимым словарём не соответствует контракту. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_case`; выбрано тестов: 21.

```diff
--- src/parsers/mail/message.py
+++ src/parsers/mail/message.py
@@ -1,6 +1,6 @@
 def sender_matches(message: Message, sender: str, *, sender_is_domain: bool) -> bool:
     """Совпадает ли From письма с адресом или доменом отправителя (без учёта регистра)."""
-    _, address = parseaddr(decode_header_value(message.get('From')))
+    _, address = parseaddr(decode_header_value(message.get('from')))
     address = address.lower()
     if sender_is_domain:
         return address.endswith(f'@{sender.lower()}')
```

### `parsers.mail.message.x_sender_matches__mutmut_7`

Классификация 2026-11-14: Эквивалент: По контракту вход — email.message.Message: Message.get приводит к нижнему регистру и имя поиска, и имена сохранённых заголовков. Изменение регистра Subject, Date или From сохраняет выбранный заголовок, его значение и поведение при отсутствии/повторении заголовков. Проверена реализация Message.get в Python 3.14; подмена Message регистрозависимым словарём не соответствует контракту. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_case`; выбрано тестов: 21.

```diff
--- src/parsers/mail/message.py
+++ src/parsers/mail/message.py
@@ -1,6 +1,6 @@
 def sender_matches(message: Message, sender: str, *, sender_is_domain: bool) -> bool:
     """Совпадает ли From письма с адресом или доменом отправителя (без учёта регистра)."""
-    _, address = parseaddr(decode_header_value(message.get('From')))
+    _, address = parseaddr(decode_header_value(message.get('FROM')))
     address = address.lower()
     if sender_is_domain:
         return address.endswith(f'@{sender.lower()}')
```

### `parsers.mail.message.x_subject_matches__mutmut_5`

Классификация 2026-11-14: Эквивалент: По контракту вход — email.message.Message: Message.get приводит к нижнему регистру и имя поиска, и имена сохранённых заголовков. Изменение регистра Subject, Date или From сохраняет выбранный заголовок, его значение и поведение при отсутствии/повторении заголовков. Проверена реализация Message.get в Python 3.14; подмена Message регистрозависимым словарём не соответствует контракту. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_case`; выбрано тестов: 9.

```diff
--- src/parsers/mail/message.py
+++ src/parsers/mail/message.py
@@ -1,4 +1,4 @@
 def subject_matches(message: Message, keyword: str) -> bool:
     """Есть ли слово (подстрока) в теме письма без учёта регистра."""
-    subject = decode_header_value(message.get('Subject'))
+    subject = decode_header_value(message.get('subject'))
     return keyword.casefold() in subject.casefold()
```

### `parsers.mail.message.x_subject_matches__mutmut_6`

Классификация 2026-11-14: Эквивалент: По контракту вход — email.message.Message: Message.get приводит к нижнему регистру и имя поиска, и имена сохранённых заголовков. Изменение регистра Subject, Date или From сохраняет выбранный заголовок, его значение и поведение при отсутствии/повторении заголовков. Проверена реализация Message.get в Python 3.14; подмена Message регистрозависимым словарём не соответствует контракту. Прямое применение исторического diff в R13: 184 passed; прохождение тестов само по себе не использовано как доказательство эквивалентности.

Статус: **survived**; тип: `string_case`; выбрано тестов: 9.

```diff
--- src/parsers/mail/message.py
+++ src/parsers/mail/message.py
@@ -1,4 +1,4 @@
 def subject_matches(message: Message, keyword: str) -> bool:
     """Есть ли слово (подстрока) в теме письма без учёта регистра."""
-    subject = decode_header_value(message.get('Subject'))
+    subject = decode_header_value(message.get('SUBJECT'))
     return keyword.casefold() in subject.casefold()
```

## src/parsers/nomenclature/brand.py

### `parsers.nomenclature.brand.x__brand_rest__mutmut_13`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 100.

```diff
--- src/parsers/nomenclature/brand.py
+++ src/parsers/nomenclature/brand.py
@@ -3,5 +3,5 @@
     rest = model[len(brand) :]
     starts_with_brand = bool(brand) and model.lower().startswith(brand.lower())
     if starts_with_brand and rest[:1] in _BRAND_SEPARATORS:
-        return rest.lstrip(' -').strip()
+        return rest.lstrip('XX -XX').strip()
     return None
```

## src/parsers/nomenclature/labels.py

### `parsers.nomenclature.labels.x_axis_label__mutmut_5`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 173.

```diff
--- src/parsers/nomenclature/labels.py
+++ src/parsers/nomenclature/labels.py
@@ -1,6 +1,6 @@
 def axis_label(raw: object) -> str:
     """Ось/назначение из канонического словаря; незнакомое слово не пишется."""
-    lower = str(raw or '').strip().lower()
+    lower = str(raw or 'XXXX').strip().lower()
     for root, label in _AXIS_LABELS:
         if lower.startswith(root):
             return label
```

### `parsers.nomenclature.labels.x_layering_label__mutmut_5`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 264.

```diff
--- src/parsers/nomenclature/labels.py
+++ src/parsers/nomenclature/labels.py
@@ -1,4 +1,4 @@
 def layering_label(raw: object) -> str:
     """Слойность как `<N>PR`: `16`, `16PR`, `PR16` → `16PR`; без числа — пусто."""
-    found = _DIGITS.search(str(raw or ''))
+    found = _DIGITS.search(str(raw or 'XXXX'))
     return f'{found[0]}PR' if found else ''
```

### `parsers.nomenclature.labels.x_run_flat_label__mutmut_5`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 68.

```diff
--- src/parsers/nomenclature/labels.py
+++ src/parsers/nomenclature/labels.py
@@ -1,4 +1,4 @@
 def run_flat_label(flag: object, title: str | None) -> str:
     """`RunFlat`, если колонка прайса отмечена («да») или в названии есть `RFT`/`Run Flat`/`Run-Flat`; иначе пусто."""
-    marked = str(flag or '').strip().lower() in _RUN_FLAT_YES
+    marked = str(flag or 'XXXX').strip().lower() in _RUN_FLAT_YES
     return 'RunFlat' if marked or _RUN_FLAT.search(title or '') else ''
```

### `parsers.nomenclature.labels.x_run_flat_label__mutmut_15`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 68.

```diff
--- src/parsers/nomenclature/labels.py
+++ src/parsers/nomenclature/labels.py
@@ -1,4 +1,4 @@
 def run_flat_label(flag: object, title: str | None) -> str:
     """`RunFlat`, если колонка прайса отмечена («да») или в названии есть `RFT`/`Run Flat`/`Run-Flat`; иначе пусто."""
     marked = str(flag or '').strip().lower() in _RUN_FLAT_YES
-    return 'RunFlat' if marked or _RUN_FLAT.search(title or '') else ''
+    return 'RunFlat' if marked or _RUN_FLAT.search(title or 'XXXX') else ''
```

### `parsers.nomenclature.labels.x_season_marks_label__mutmut_9`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 270.

```diff
--- src/parsers/nomenclature/labels.py
+++ src/parsers/nomenclature/labels.py
@@ -1,7 +1,7 @@
 def season_marks_label(*sources: object) -> tuple[str, ...]:
     """`M+S` и `3PMSF` из текстов (название, надпись на боковине) в каноническом порядке; нет маркера — пусто."""
     found = {
-        'M+S' if match[1][0] in 'Mm' else '3PMSF'
+        'M+S' if match[1][0] in 'XXMmXX' else '3PMSF'
         for source in sources
         for match in _SEASON_MARK.finditer(str(source or ''))
     }
```

### `parsers.nomenclature.labels.x_season_marks_label__mutmut_17`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 270.

```diff
--- src/parsers/nomenclature/labels.py
+++ src/parsers/nomenclature/labels.py
@@ -3,6 +3,6 @@
     found = {
         'M+S' if match[1][0] in 'Mm' else '3PMSF'
         for source in sources
-        for match in _SEASON_MARK.finditer(str(source or ''))
+        for match in _SEASON_MARK.finditer(str(source or 'XXXX'))
     }
     return tuple(mark for mark in _SEASON_MARKS if mark in found)
```

### `parsers.nomenclature.labels.x_xl_label__mutmut_6`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 269.

```diff
--- src/parsers/nomenclature/labels.py
+++ src/parsers/nomenclature/labels.py
@@ -1,4 +1,4 @@
 def xl_label(*sources: object) -> str:
     """`XL`, если он есть хотя бы в одном из текстов; иначе пусто."""
-    text = ' '.join(str(source or '') for source in sources)
+    text = ' '.join(str(source or 'XXXX') for source in sources)
     return 'XL' if _XL.search(text) else ''
```

## src/parsers/nomenclature/title.py

### `parsers.nomenclature.title.x_compose_disk_title__mutmut_1`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 8.

```diff
--- src/parsers/nomenclature/title.py
+++ src/parsers/nomenclature/title.py
@@ -1,4 +1,4 @@
-def compose_disk_title(row_item: RowItem, suffix: str = '') -> str:
+def compose_disk_title(row_item: RowItem, suffix: str = 'XXXX') -> str:
     """Название диска в каноническом порядке из полей позиции.
 
     `<ширина>x<диаметр> <отверстия>x<PCD> ET<вылет> <DIA> <Цвет> <бренд> <модель> [хвост]`;
```

### `parsers.nomenclature.title.x_compose_tire_title__mutmut_2`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 64.

```diff
--- src/parsers/nomenclature/title.py
+++ src/parsers/nomenclature/title.py
@@ -3,7 +3,7 @@
     size: str,
     *,
     camera: str = '',
-    axis: str = '',
+    axis: str = 'XXXX',
     after_load: tuple[object, ...] = (),
     run_flat: str = '',
 ) -> str:
```

### `parsers.nomenclature.title.x_compose_tire_title__mutmut_32`

Статус: **survived**; тип: `to_none`; выбрано тестов: 64.

```diff
--- src/parsers/nomenclature/title.py
+++ src/parsers/nomenclature/title.py
@@ -18,7 +18,7 @@
         brand_label(row_item),
         model_label(row_item),
         load_velocity=load_velocity(row_item),
-        xl=xl_label(source_title, sidewall),
+        xl=xl_label(source_title, None),
         layering=row_item.tire.layering,
         camera=camera,
         season_marks=season_marks_label(source_title, sidewall),
```

### `parsers.nomenclature.title.x_compose_tire_title__mutmut_34`

Статус: **survived**; тип: `other`; выбрано тестов: 64.

```diff
--- src/parsers/nomenclature/title.py
+++ src/parsers/nomenclature/title.py
@@ -18,7 +18,7 @@
         brand_label(row_item),
         model_label(row_item),
         load_velocity=load_velocity(row_item),
-        xl=xl_label(source_title, sidewall),
+        xl=xl_label(source_title, ),
         layering=row_item.tire.layering,
         camera=camera,
         season_marks=season_marks_label(source_title, sidewall),
```

## src/parsers/nomenclature/tube_title.py

### `parsers.nomenclature.tube_title.x_compose_tube_title__mutmut_1`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 15.

```diff
--- src/parsers/nomenclature/tube_title.py
+++ src/parsers/nomenclature/tube_title.py
@@ -1,4 +1,4 @@
-def compose_tube_title(is_rim_tape: bool, size: str, brand: str = '', model: str = '', *, valve: bool = False) -> str:
+def compose_tube_title(is_rim_tape: bool, size: str, brand: str = 'XXXX', model: str = '', *, valve: bool = False) -> str:
     """Название камеры или ободной ленты: `<Камера|Ободная лента> <размер> [бренд] [модель] [с вентилем]`.
 
     ``model`` — модель камеры (`ГК-145`) или ленты (`300-508А`); модель ленты уже содержит размер
```

### `parsers.nomenclature.tube_title.x_compose_tube_title__mutmut_2`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 15.

```diff
--- src/parsers/nomenclature/tube_title.py
+++ src/parsers/nomenclature/tube_title.py
@@ -1,4 +1,4 @@
-def compose_tube_title(is_rim_tape: bool, size: str, brand: str = '', model: str = '', *, valve: bool = False) -> str:
+def compose_tube_title(is_rim_tape: bool, size: str, brand: str = '', model: str = 'XXXX', *, valve: bool = False) -> str:
     """Название камеры или ободной ленты: `<Камера|Ободная лента> <размер> [бренд] [модель] [с вентилем]`.
 
     ``model`` — модель камеры (`ГК-145`) или ленты (`300-508А`); модель ленты уже содержит размер
```

### `parsers.nomenclature.tube_title.x_compose_tube_title__mutmut_3`

Статус: **survived**; тип: `keyword`; выбрано тестов: 15.

```diff
--- src/parsers/nomenclature/tube_title.py
+++ src/parsers/nomenclature/tube_title.py
@@ -1,4 +1,4 @@
-def compose_tube_title(is_rim_tape: bool, size: str, brand: str = '', model: str = '', *, valve: bool = False) -> str:
+def compose_tube_title(is_rim_tape: bool, size: str, brand: str = '', model: str = '', *, valve: bool = True) -> str:
     """Название камеры или ободной ленты: `<Камера|Ободная лента> <размер> [бренд] [модель] [с вентилем]`.
 
     ``model`` — модель камеры (`ГК-145`) или ленты (`300-508А`); модель ленты уже содержит размер
```

### `parsers.nomenclature.tube_title.x_compose_tube_title__mutmut_7`

Статус: **survived**; тип: `other`; выбрано тестов: 15.

```diff
--- src/parsers/nomenclature/tube_title.py
+++ src/parsers/nomenclature/tube_title.py
@@ -5,5 +5,5 @@
     и ставится вместо него.
     """
     if is_rim_tape:
-        return join_title_parts('Ободная лента', model or size, brand, 'с вентилем' if valve else '')
+        return join_title_parts('Ободная лента', model or size, brand, None)
     return join_title_parts('Камера', size, brand, model, 'с вентилем' if valve else '')
```

### `parsers.nomenclature.tube_title.x_compose_tube_title__mutmut_11`

Статус: **survived**; тип: `other`; выбрано тестов: 15.

```diff
--- src/parsers/nomenclature/tube_title.py
+++ src/parsers/nomenclature/tube_title.py
@@ -5,5 +5,5 @@
     и ставится вместо него.
     """
     if is_rim_tape:
-        return join_title_parts('Ободная лента', model or size, brand, 'с вентилем' if valve else '')
+        return join_title_parts('Ободная лента', model or size, brand, )
     return join_title_parts('Камера', size, brand, model, 'с вентилем' if valve else '')
```

### `parsers.nomenclature.tube_title.x_compose_tube_title__mutmut_16`

Статус: **survived**; тип: `other`; выбрано тестов: 15.

```diff
--- src/parsers/nomenclature/tube_title.py
+++ src/parsers/nomenclature/tube_title.py
@@ -5,5 +5,5 @@
     и ставится вместо него.
     """
     if is_rim_tape:
-        return join_title_parts('Ободная лента', model or size, brand, 'с вентилем' if valve else '')
+        return join_title_parts('Ободная лента', model or size, brand, 'с вентилем' if (valve) and False else '')
     return join_title_parts('Камера', size, brand, model, 'с вентилем' if valve else '')
```

### `parsers.nomenclature.tube_title.x_compose_tube_title__mutmut_18`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 15.

```diff
--- src/parsers/nomenclature/tube_title.py
+++ src/parsers/nomenclature/tube_title.py
@@ -5,5 +5,5 @@
     и ставится вместо него.
     """
     if is_rim_tape:
-        return join_title_parts('Ободная лента', model or size, brand, 'с вентилем' if valve else '')
+        return join_title_parts('Ободная лента', model or size, brand, 'XXс вентилемXX' if valve else '')
     return join_title_parts('Камера', size, brand, model, 'с вентилем' if valve else '')
```

### `parsers.nomenclature.tube_title.x_compose_tube_title__mutmut_19`

Статус: **survived**; тип: `string_case`; выбрано тестов: 15.

```diff
--- src/parsers/nomenclature/tube_title.py
+++ src/parsers/nomenclature/tube_title.py
@@ -5,5 +5,5 @@
     и ставится вместо него.
     """
     if is_rim_tape:
-        return join_title_parts('Ободная лента', model or size, brand, 'с вентилем' if valve else '')
+        return join_title_parts('Ободная лента', model or size, brand, 'С ВЕНТИЛЕМ' if valve else '')
     return join_title_parts('Камера', size, brand, model, 'с вентилем' if valve else '')
```

## src/parsers/price_schema/diff.py

### `parsers.price_schema.diff.x__usage__mutmut_2`

Статус: **survived**; тип: `other`; выбрано тестов: 12.

```diff
--- src/parsers/price_schema/diff.py
+++ src/parsers/price_schema/diff.py
@@ -1,3 +1,3 @@
 def _usage(column: int | str, columns: Columns) -> str:
     """Пояснение, в какое поле разбирается колонка."""
-    return f' (используется как «{columns[column]}»)' if column in columns else ''
+    return f' (используется как «{columns[column]}»)' if (column in columns) or True else ''
```

### `parsers.price_schema.diff.x__usage__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 12.

```diff
--- src/parsers/price_schema/diff.py
+++ src/parsers/price_schema/diff.py
@@ -1,3 +1,3 @@
 def _usage(column: int | str, columns: Columns) -> str:
     """Пояснение, в какое поле разбирается колонка."""
-    return f' (используется как «{columns[column]}»)' if column in columns else ''
+    return f' (используется как «{columns[column]}»)' if column in columns else 'XXXX'
```

## src/parsers/price_schema/header.py

### `parsers.price_schema.header.x__column_texts__mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R3 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 14.

```diff
--- src/parsers/price_schema/header.py
+++ src/parsers/price_schema/header.py
@@ -1,6 +1,6 @@
 def _column_texts(rows: HeadRows, column: int) -> Iterator[str]:
     """Тексты колонки снизу вверх, нормализованные по пробелам."""
     for row in reversed(rows):
-        cell = row[column] if column < len(row) else None
+        cell = row[column] if (column < len(row)) or True else None
         if isinstance(cell, str) and cell.strip():
             yield ' '.join(cell.split())
```

### `parsers.price_schema.header.x__column_texts__mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R3 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён. Контракт закреплён новым `test_column_at_row_length_has_no_header` в `tests/test_parsers/test_price_schema.py`.

Статус: **survived**; тип: `operator`; выбрано тестов: 14.

```diff
--- src/parsers/price_schema/header.py
+++ src/parsers/price_schema/header.py
@@ -1,6 +1,6 @@
 def _column_texts(rows: HeadRows, column: int) -> Iterator[str]:
     """Тексты колонки снизу вверх, нормализованные по пробелам."""
     for row in reversed(rows):
-        cell = row[column] if column < len(row) else None
+        cell = row[column] if column <= len(row) else None
         if isinstance(cell, str) and cell.strip():
             yield ' '.join(cell.split())
```

### `parsers.price_schema.header.x__column_texts__mutmut_8`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R3 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён. Контракт закреплён новым `test_header_normalizes_spaces_between_words` в `tests/test_parsers/test_price_schema.py`.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 14.

```diff
--- src/parsers/price_schema/header.py
+++ src/parsers/price_schema/header.py
@@ -3,4 +3,4 @@
     for row in reversed(rows):
         cell = row[column] if column < len(row) else None
         if isinstance(cell, str) and cell.strip():
-            yield ' '.join(cell.split())
+            yield 'XX XX'.join(cell.split())
```

### `parsers.price_schema.header.x_column_header__mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R3 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён. Контракт закреплён новым `test_column_at_row_length_has_no_header` в `tests/test_parsers/test_price_schema.py`.

Статус: **survived**; тип: `to_none`; выбрано тестов: 14.

```diff
--- src/parsers/price_schema/header.py
+++ src/parsers/price_schema/header.py
@@ -1,3 +1,3 @@
 def column_header(rows: HeadRows, column: int) -> str:
     """Заголовок колонки — самый нижний непустой текст над строкой данных."""
-    return next(_column_texts(rows, column), '')
+    return next(_column_texts(rows, column), None)
```

## src/parsers/price_schema/schema.py

### `parsers.price_schema.schema.x__json_keys__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R3 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён. Контракт закреплён новым `test_json_scalar_has_no_record_keys` в `tests/test_parsers/test_price_schema.py`.

Статус: **survived**; тип: `other`; выбрано тестов: 1.

```diff
--- src/parsers/price_schema/schema.py
+++ src/parsers/price_schema/schema.py
@@ -1,5 +1,5 @@
 def _json_keys(path: Path) -> frozenset[str]:
     """Объединение ключей всех записей json-прайса."""
     records = json.loads(path.read_text(encoding='UTF-8'))
-    rows = records if isinstance(records, list) else []
+    rows = records if (isinstance(records, list)) or True else []
     return frozenset(key for row in rows if isinstance(row, dict) for key in row)
```

### `parsers.price_schema.schema.x__sheet_head__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R3 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён. Контракт закреплён новым `test_xlsx_head_stops_at_hundred_rows` в `tests/test_parsers/test_price_schema.py`.

Статус: **survived**; тип: `to_none`; выбрано тестов: 5.

```diff
--- src/parsers/price_schema/schema.py
+++ src/parsers/price_schema/schema.py
@@ -1,4 +1,4 @@
 def _sheet_head(book: CalamineWorkbook, name: str) -> SheetHead:
     """Первые строки вкладки."""
-    rows = islice(book.get_sheet_by_name(name).iter_rows(), _HEADER_ROWS_LIMIT)
+    rows = islice(book.get_sheet_by_name(name).iter_rows(), None)
     return SheetHead(name, tuple(tuple(row) for row in rows))
```

### `parsers.price_schema.schema.x__sheets_schema__mutmut_9`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R3 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `number`; выбрано тестов: 14.

```diff
--- src/parsers/price_schema/schema.py
+++ src/parsers/price_schema/schema.py
@@ -3,7 +3,7 @@
 ) -> dict[int, SheetSchema]:
     """Схемы вкладок секции по индексу; индексы за пределами файла пропускаются."""
     mapped = [key for key in columns if isinstance(key, int)]
-    zone = max(start_row - 1, 0)
+    zone = max(start_row - 1, 1)
     indexes = sheet_indexes or tuple(range(len(head.sheets)))
     existing = [index for index in indexes if index < len(head.sheets)]
     return {index: _sheet_schema(head.sheets[index], mapped, zone) for index in existing}
```

### `parsers.price_schema.schema.x__sheets_schema__mutmut_11`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R3 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `operator`; выбрано тестов: 14.

```diff
--- src/parsers/price_schema/schema.py
+++ src/parsers/price_schema/schema.py
@@ -4,6 +4,6 @@
     """Схемы вкладок секции по индексу; индексы за пределами файла пропускаются."""
     mapped = [key for key in columns if isinstance(key, int)]
     zone = max(start_row - 1, 0)
-    indexes = sheet_indexes or tuple(range(len(head.sheets)))
+    indexes = sheet_indexes and tuple(range(len(head.sheets)))
     existing = [index for index in indexes if index < len(head.sheets)]
     return {index: _sheet_schema(head.sheets[index], mapped, zone) for index in existing}
```

### `parsers.price_schema.schema.x__sheets_schema__mutmut_12`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R3 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён. Контракт закреплён новым `test_empty_sheet_selection_uses_all_sheets` в `tests/test_parsers/test_price_schema.py`.

Статус: **survived**; тип: `other`; выбрано тестов: 14.

```diff
--- src/parsers/price_schema/schema.py
+++ src/parsers/price_schema/schema.py
@@ -4,6 +4,6 @@
     """Схемы вкладок секции по индексу; индексы за пределами файла пропускаются."""
     mapped = [key for key in columns if isinstance(key, int)]
     zone = max(start_row - 1, 0)
-    indexes = sheet_indexes or tuple(range(len(head.sheets)))
+    indexes = sheet_indexes or tuple(None)
     existing = [index for index in indexes if index < len(head.sheets)]
     return {index: _sheet_schema(head.sheets[index], mapped, zone) for index in existing}
```

### `parsers.price_schema.schema.x__sheets_schema__mutmut_13`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R3 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён. Контракт закреплён новым `test_empty_sheet_selection_uses_all_sheets` в `tests/test_parsers/test_price_schema.py`.

Статус: **survived**; тип: `other`; выбрано тестов: 14.

```diff
--- src/parsers/price_schema/schema.py
+++ src/parsers/price_schema/schema.py
@@ -4,6 +4,6 @@
     """Схемы вкладок секции по индексу; индексы за пределами файла пропускаются."""
     mapped = [key for key in columns if isinstance(key, int)]
     zone = max(start_row - 1, 0)
-    indexes = sheet_indexes or tuple(range(len(head.sheets)))
+    indexes = sheet_indexes or tuple(range(None))
     existing = [index for index in indexes if index < len(head.sheets)]
     return {index: _sheet_schema(head.sheets[index], mapped, zone) for index in existing}
```

### `parsers.price_schema.schema.x__sheets_schema__mutmut_15`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R3 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `operator`; выбрано тестов: 14.

```diff
--- src/parsers/price_schema/schema.py
+++ src/parsers/price_schema/schema.py
@@ -5,5 +5,5 @@
     mapped = [key for key in columns if isinstance(key, int)]
     zone = max(start_row - 1, 0)
     indexes = sheet_indexes or tuple(range(len(head.sheets)))
-    existing = [index for index in indexes if index < len(head.sheets)]
+    existing = [index for index in indexes if index <= len(head.sheets)]
     return {index: _sheet_schema(head.sheets[index], mapped, zone) for index in existing}
```

### `parsers.price_schema.schema.x_build_schema__mutmut_1`

Статус: **survived**; тип: `operator`; выбрано тестов: 15.

```diff
--- src/parsers/price_schema/schema.py
+++ src/parsers/price_schema/schema.py
@@ -1,6 +1,6 @@
 def build_schema(head: FileHead, *, start_row: int, sheet_indexes: tuple[int, ...], columns: Columns) -> PriceSchema:
     """Схема секции: для каждой вкладки секции — заголовки используемых колонок (последний текст над данными)."""
-    if head.json_keys or not head.sheets:
+    if head.json_keys and not head.sheets:
         used = {key for key in columns if isinstance(key, str)}
         return PriceSchema(sheets={}, json_keys=frozenset(used & head.json_keys))
     return PriceSchema(sheets=_sheets_schema(head, start_row, sheet_indexes, columns), json_keys=frozenset())
```

### `parsers.price_schema.schema.x_build_schema__mutmut_16`

Классификация 2026-11-14: Закрытый пробел проверки: идентичные удаляемые и добавляемые строки diff в той же функции сопоставлены с текущей генерацией (тот же ID). Целевой прогон R3 подтвердил killed на существующих тестах. Исторический survived в исходном отчёте сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 15.

```diff
--- src/parsers/price_schema/schema.py
+++ src/parsers/price_schema/schema.py
@@ -3,4 +3,4 @@
     if head.json_keys or not head.sheets:
         used = {key for key in columns if isinstance(key, str)}
         return PriceSchema(sheets={}, json_keys=frozenset(used & head.json_keys))
-    return PriceSchema(sheets=_sheets_schema(head, start_row, sheet_indexes, columns), json_keys=frozenset())
+    return PriceSchema(sheets=_sheets_schema(head, start_row, None, columns), json_keys=frozenset())
```

## src/parsers/registry.py

### `parsers.registry.x__build_parse_config__mutmut_10`

Статус: **survived**; тип: `to_none`; выбрано тестов: 22.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -7,5 +7,5 @@
     """Построить ParseConfiguration из секции конфига вендора."""
     params = parser_params_from_section(section, config.folder)
     return make_parse_config(
-        params, config_provider=config_provider, vendor_section=section, vendor_config=config, routing=routing
+        params, config_provider=config_provider, vendor_section=section, vendor_config=config, routing=None
     )
```

### `parsers.registry.x__build_parse_config__mutmut_15`

Статус: **survived**; тип: `other`; выбрано тестов: 22.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -7,5 +7,4 @@
     """Построить ParseConfiguration из секции конфига вендора."""
     params = parser_params_from_section(section, config.folder)
     return make_parse_config(
-        params, config_provider=config_provider, vendor_section=section, vendor_config=config, routing=routing
-    )
+        params, config_provider=config_provider, vendor_section=section, vendor_config=config, )
```

### `parsers.registry.x__vendor_entries__mutmut_8`

Статус: **survived**; тип: `to_none`; выбрано тестов: 5.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -5,7 +5,7 @@
         if not include_disabled and not config.enabled:
             continue
         ensure_groups_available(config)
-        routing = VendorRouting(config)
+        routing = None
         entries.extend(
             (BaseParser, _build_parse_config(section, config, config_provider, routing))
             for section in config.all_sections
```

### `parsers.registry.x__vendor_entries__mutmut_13`

Статус: **survived**; тип: `to_none`; выбрано тестов: 5.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -7,7 +7,7 @@
         ensure_groups_available(config)
         routing = VendorRouting(config)
         entries.extend(
-            (BaseParser, _build_parse_config(section, config, config_provider, routing))
+            (BaseParser, _build_parse_config(section, config, None, routing))
             for section in config.all_sections
         )
     return entries
```

### `parsers.registry.x__vendor_entries__mutmut_14`

Статус: **survived**; тип: `to_none`; выбрано тестов: 5.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -7,7 +7,7 @@
         ensure_groups_available(config)
         routing = VendorRouting(config)
         entries.extend(
-            (BaseParser, _build_parse_config(section, config, config_provider, routing))
+            (BaseParser, _build_parse_config(section, config, config_provider, None))
             for section in config.all_sections
         )
     return entries
```

### `parsers.registry.x__vendor_entries__mutmut_17`

Статус: **survived**; тип: `other`; выбрано тестов: 5.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -7,7 +7,7 @@
         ensure_groups_available(config)
         routing = VendorRouting(config)
         entries.extend(
-            (BaseParser, _build_parse_config(section, config, config_provider, routing))
+            (BaseParser, _build_parse_config(section, config, routing))
             for section in config.all_sections
         )
     return entries
```

### `parsers.registry.x__vendor_entries__mutmut_18`

Статус: **survived**; тип: `other`; выбрано тестов: 5.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -7,7 +7,7 @@
         ensure_groups_available(config)
         routing = VendorRouting(config)
         entries.extend(
-            (BaseParser, _build_parse_config(section, config, config_provider, routing))
+            (BaseParser, _build_parse_config(section, config, config_provider, ))
             for section in config.all_sections
         )
     return entries
```

### `parsers.registry.x_all_vendors_from_registry__mutmut_2`

Статус: **survived**; тип: `to_none`; выбрано тестов: 5.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -5,4 +5,4 @@
     Класс парсера — ``BaseParser`` во всех записях; поведение определяется
     стратегиями из конфига, которые хранятся в атрибутах ``ParseConfiguration``.
     """
-    return _vendor_entries(config_provider, include_disabled=False)
+    return _vendor_entries(config_provider, include_disabled=None)
```

### `parsers.registry.x_make_vendor_entry__mutmut_1`

Статус: **survived**; тип: `to_none`; выбрано тестов: 8.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -11,5 +11,5 @@
     Returns:
         (BaseParser, ParseConfiguration) с прикреплёнными метаданными.
     """
-    routing = VendorRouting(config) if config.product_groups else None
+    routing = None
     return (BaseParser, _build_parse_config(section, config, config_provider, routing))
```

### `parsers.registry.x_make_vendor_entry__mutmut_2`

Статус: **survived**; тип: `other`; выбрано тестов: 8.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -11,5 +11,5 @@
     Returns:
         (BaseParser, ParseConfiguration) с прикреплёнными метаданными.
     """
-    routing = VendorRouting(config) if config.product_groups else None
+    routing = VendorRouting(config) if (config.product_groups) and False else None
     return (BaseParser, _build_parse_config(section, config, config_provider, routing))
```

### `parsers.registry.x_make_vendor_entry__mutmut_3`

Статус: **survived**; тип: `other`; выбрано тестов: 8.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -11,5 +11,5 @@
     Returns:
         (BaseParser, ParseConfiguration) с прикреплёнными метаданными.
     """
-    routing = VendorRouting(config) if config.product_groups else None
+    routing = VendorRouting(config) if (config.product_groups) or True else None
     return (BaseParser, _build_parse_config(section, config, config_provider, routing))
```

### `parsers.registry.x_make_vendor_entry__mutmut_8`

Статус: **survived**; тип: `to_none`; выбрано тестов: 8.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -12,4 +12,4 @@
         (BaseParser, ParseConfiguration) с прикреплёнными метаданными.
     """
     routing = VendorRouting(config) if config.product_groups else None
-    return (BaseParser, _build_parse_config(section, config, config_provider, routing))
+    return (BaseParser, _build_parse_config(section, config, config_provider, None))
```

### `parsers.registry.x_make_vendor_entry__mutmut_12`

Статус: **survived**; тип: `other`; выбрано тестов: 8.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -12,4 +12,4 @@
         (BaseParser, ParseConfiguration) с прикреплёнными метаданными.
     """
     routing = VendorRouting(config) if config.product_groups else None
-    return (BaseParser, _build_parse_config(section, config, config_provider, routing))
+    return (BaseParser, _build_parse_config(section, config, config_provider, ))
```

### `parsers.registry.x_vendor_entry_for__mutmut_7`

Статус: **survived**; тип: `to_none`; выбрано тестов: 11.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -8,6 +8,6 @@
         ensure_section_available(config, code)
         for section in config.all_sections:
             if section.id == code:
-                routing = VendorRouting(config)
+                routing = None
                 return (BaseParser, _build_parse_config(section, config, config_provider, routing))
     raise UnknownVendorError(code)
```

### `parsers.registry.x_vendor_entry_for__mutmut_11`

Статус: **survived**; тип: `to_none`; выбрано тестов: 11.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -9,5 +9,5 @@
         for section in config.all_sections:
             if section.id == code:
                 routing = VendorRouting(config)
-                return (BaseParser, _build_parse_config(section, config, config_provider, routing))
+                return (BaseParser, _build_parse_config(section, config, None, routing))
     raise UnknownVendorError(code)
```

### `parsers.registry.x_vendor_entry_for__mutmut_12`

Статус: **survived**; тип: `to_none`; выбрано тестов: 11.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -9,5 +9,5 @@
         for section in config.all_sections:
             if section.id == code:
                 routing = VendorRouting(config)
-                return (BaseParser, _build_parse_config(section, config, config_provider, routing))
+                return (BaseParser, _build_parse_config(section, config, config_provider, None))
     raise UnknownVendorError(code)
```

### `parsers.registry.x_vendor_entry_for__mutmut_15`

Статус: **survived**; тип: `other`; выбрано тестов: 11.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -9,5 +9,5 @@
         for section in config.all_sections:
             if section.id == code:
                 routing = VendorRouting(config)
-                return (BaseParser, _build_parse_config(section, config, config_provider, routing))
+                return (BaseParser, _build_parse_config(section, config, routing))
     raise UnknownVendorError(code)
```

### `parsers.registry.x_vendor_entry_for__mutmut_16`

Статус: **survived**; тип: `other`; выбрано тестов: 11.

```diff
--- src/parsers/registry.py
+++ src/parsers/registry.py
@@ -9,5 +9,5 @@
         for section in config.all_sections:
             if section.id == code:
                 routing = VendorRouting(config)
-                return (BaseParser, _build_parse_config(section, config, config_provider, routing))
+                return (BaseParser, _build_parse_config(section, config, config_provider, ))
     raise UnknownVendorError(code)
```

## src/parsers/strategies/_autosnab_helper.py

### `parsers.strategies._autosnab_helper.x__lstrip_name__mutmut_14`

Статус: **survived**; тип: `method_swap`; выбрано тестов: 20.

```diff
--- src/parsers/strategies/_autosnab_helper.py
+++ src/parsers/strategies/_autosnab_helper.py
@@ -9,4 +9,4 @@
     tail = rest[len(prefix) :]
     if tail and not tail[0].isspace():
         return rest
-    return tail.lstrip()
+    return tail.rstrip()
```

### `parsers.strategies._autosnab_helper.x__parse_size__mutmut_33`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 21.

```diff
--- src/parsers/strategies/_autosnab_helper.py
+++ src/parsers/strategies/_autosnab_helper.py
@@ -6,7 +6,7 @@
             width.replace(',', '.'),
             height.replace(',', '.'),
             diameter.replace(',', '.'),
-            ext.replace(',', '.'),
+            ext.replace('XX,XX', '.'),
             title[end:],
         )
 
```

### `parsers.strategies._autosnab_helper.x__parse_size__mutmut_34`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 21.

```diff
--- src/parsers/strategies/_autosnab_helper.py
+++ src/parsers/strategies/_autosnab_helper.py
@@ -6,7 +6,7 @@
             width.replace(',', '.'),
             height.replace(',', '.'),
             diameter.replace(',', '.'),
-            ext.replace(',', '.'),
+            ext.replace(',', 'XX.XX'),
             title[end:],
         )
 
```

### `parsers.strategies._autosnab_helper.x_fill_from_title__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 21.

```diff
--- src/parsers/strategies/_autosnab_helper.py
+++ src/parsers/strategies/_autosnab_helper.py
@@ -1,6 +1,6 @@
 def fill_from_title(row_item: RowItem) -> None:
     """Заполнить width/height/diameter/model из title. Без совпадения — не трогать."""
-    parsed = _parse_size((row_item.identity.title or '').strip())
+    parsed = _parse_size((row_item.identity.title or 'XXXX').strip())
     if parsed is None:
         return
     _apply_size(row_item, parsed)
```

## src/parsers/strategies/_disk_title_parser.py

### `parsers.strategies._disk_title_parser.x__first_known__mutmut_5`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 43.

```diff
--- src/parsers/strategies/_disk_title_parser.py
+++ src/parsers/strategies/_disk_title_parser.py
@@ -1,7 +1,7 @@
 def _first_known(text: str, known: Mapping[str, str]) -> str:
     """Значение для первого слова названия, известного справочнику (скобки вокруг слова не мешают)."""
     for token in text.split():
-        found = known.get(token.strip('()').lower())
+        found = known.get(token.strip('XX()XX').lower())
         if found:
             return found
     return ''
```

### `parsers.strategies._disk_title_parser.x__thickness__mutmut_15`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 43.

```diff
--- src/parsers/strategies/_disk_title_parser.py
+++ src/parsers/strategies/_disk_title_parser.py
@@ -1,4 +1,4 @@
 def _thickness(text: str) -> str:
     """Толщина: ``(13мм)`` или голое ``16мм`` (кроме диаметра отверстия после числа отверстий)."""
     paren = _first_group(_THICKNESS_PAREN, text)
-    return paren or _first_group(_THICKNESS_BARE, _HOLES_HOLE_SIZE.sub(' ', text))
+    return paren or _first_group(_THICKNESS_BARE, _HOLES_HOLE_SIZE.sub('XX XX', text))
```

## src/parsers/strategies/_four_tochki_disk_helper.py

### `parsers.strategies._four_tochki_disk_helper.x_disk_name_suffix__mutmut_1`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 12.

```diff
--- src/parsers/strategies/_four_tochki_disk_helper.py
+++ src/parsers/strategies/_four_tochki_disk_helper.py
@@ -1,4 +1,4 @@
-def disk_name_suffix(name: str, model: str = '') -> str:
+def disk_name_suffix(name: str, model: str = 'XXXX') -> str:
     """Толщина, усиление, камерность и различающие хвосты из наименования; скобки модели не повторяются."""
     thickness = thickness_from_name(name)
     thick_label = f'({thickness} мм)' if thickness else ''
```

### `parsers.strategies._four_tochki_disk_helper.x_fill_disk_thickness__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 10.

```diff
--- src/parsers/strategies/_four_tochki_disk_helper.py
+++ src/parsers/strategies/_four_tochki_disk_helper.py
@@ -2,6 +2,6 @@
     """Заполнить толщину из исходного наименования, если колонка пуста."""
     if row_item.disk.disk_thickness:
         return
-    thickness = thickness_from_name(row_item.identity.title or '')
+    thickness = thickness_from_name(row_item.identity.title or 'XXXX')
     if thickness:
         row_item.set_field('disk_thickness', thickness)
```

## src/parsers/strategies/_four_tochki_tire_helper.py

### `parsers.strategies._four_tochki_tire_helper.x__camera__mutmut_5`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 47.

```diff
--- src/parsers/strategies/_four_tochki_tire_helper.py
+++ src/parsers/strategies/_four_tochki_tire_helper.py
@@ -2,7 +2,7 @@
     """Камерность колонки; если колонки нет — из названия (разбор кладёт только `TL`/`TT` в `intimacy`)."""
     if row_item.tire.camera_type:
         return str(row_item.tire.camera_type).strip()
-    camera = _CAMERA.search(row_item.identity.title or '')
+    camera = _CAMERA.search(row_item.identity.title or 'XXXX')
     if camera is not None:
         return ' '.join(camera.group(0).split())
     return str(row_item.tire.intimacy or '')
```

### `parsers.strategies._four_tochki_tire_helper.x__compose_title__mutmut_8`

Статус: **survived**; тип: `to_none`; выбрано тестов: 44.

```diff
--- src/parsers/strategies/_four_tochki_tire_helper.py
+++ src/parsers/strategies/_four_tochki_tire_helper.py
@@ -2,7 +2,7 @@
     """Собрать title по типу шины. dims: width, height_raw, diameter, construct."""
     height = f'/{dims[1]}'
     if not dims[1] or dims[1] == _PROFILE_L:
-        height = ''
+        height = None
     postfix = resolve_width_postfix(row_item, dims[0], dims[1], dims[2])
     construct_diameter = f'{dims[3]}{dims[2]}'.replace('RZ', 'ZR')
     size = join_size_parts(dims[0], postfix, height, construct_diameter)
```

### `parsers.strategies._four_tochki_tire_helper.x_default_tire_title__mutmut_1`

Статус: **survived**; тип: `to_none`; выбрано тестов: 39.

```diff
--- src/parsers/strategies/_four_tochki_tire_helper.py
+++ src/parsers/strategies/_four_tochki_tire_helper.py
@@ -1,6 +1,6 @@
 def default_tire_title(row_item: RowItem, size: str) -> str:
     """Обычный title легковой/спец: ось — только у спецтехники."""
-    special = is_special_tire(row_item)
+    special = None
     return compose_tire_title(
         row_item,
         size,
```

### `parsers.strategies._four_tochki_tire_helper.x_default_tire_title__mutmut_6`

Статус: **survived**; тип: `other`; выбрано тестов: 39.

```diff
--- src/parsers/strategies/_four_tochki_tire_helper.py
+++ src/parsers/strategies/_four_tochki_tire_helper.py
@@ -5,6 +5,6 @@
         row_item,
         size,
         camera=camera_label(_camera(row_item)),
-        axis=row_item.tire.axis or '' if special else '',
+        axis=None,
         run_flat=_runflat(row_item),
     )
```

### `parsers.strategies._four_tochki_tire_helper.x_default_tire_title__mutmut_11`

Статус: **survived**; тип: `other`; выбрано тестов: 39.

```diff
--- src/parsers/strategies/_four_tochki_tire_helper.py
+++ src/parsers/strategies/_four_tochki_tire_helper.py
@@ -5,6 +5,5 @@
         row_item,
         size,
         camera=camera_label(_camera(row_item)),
-        axis=row_item.tire.axis or '' if special else '',
         run_flat=_runflat(row_item),
     )
```

### `parsers.strategies._four_tochki_tire_helper.x_default_tire_title__mutmut_15`

Статус: **survived**; тип: `other`; выбрано тестов: 39.

```diff
--- src/parsers/strategies/_four_tochki_tire_helper.py
+++ src/parsers/strategies/_four_tochki_tire_helper.py
@@ -5,6 +5,6 @@
         row_item,
         size,
         camera=camera_label(_camera(row_item)),
-        axis=row_item.tire.axis or '' if special else '',
+        axis=row_item.tire.axis or '' if (special) and False else '',
         run_flat=_runflat(row_item),
     )
```

### `parsers.strategies._four_tochki_tire_helper.x_default_tire_title__mutmut_16`

Статус: **survived**; тип: `other`; выбрано тестов: 39.

```diff
--- src/parsers/strategies/_four_tochki_tire_helper.py
+++ src/parsers/strategies/_four_tochki_tire_helper.py
@@ -5,6 +5,6 @@
         row_item,
         size,
         camera=camera_label(_camera(row_item)),
-        axis=row_item.tire.axis or '' if special else '',
+        axis=row_item.tire.axis or '' if (special) or True else '',
         run_flat=_runflat(row_item),
     )
```

### `parsers.strategies._four_tochki_tire_helper.x_default_tire_title__mutmut_17`

Статус: **survived**; тип: `operator`; выбрано тестов: 39.

```diff
--- src/parsers/strategies/_four_tochki_tire_helper.py
+++ src/parsers/strategies/_four_tochki_tire_helper.py
@@ -5,6 +5,6 @@
         row_item,
         size,
         camera=camera_label(_camera(row_item)),
-        axis=row_item.tire.axis or '' if special else '',
+        axis=row_item.tire.axis and '' if special else '',
         run_flat=_runflat(row_item),
     )
```

### `parsers.strategies._four_tochki_tire_helper.x_default_tire_title__mutmut_18`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 39.

```diff
--- src/parsers/strategies/_four_tochki_tire_helper.py
+++ src/parsers/strategies/_four_tochki_tire_helper.py
@@ -5,6 +5,6 @@
         row_item,
         size,
         camera=camera_label(_camera(row_item)),
-        axis=row_item.tire.axis or '' if special else '',
+        axis=row_item.tire.axis or 'XXXX' if special else '',
         run_flat=_runflat(row_item),
     )
```

### `parsers.strategies._four_tochki_tire_helper.x_default_tire_title__mutmut_19`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 39.

```diff
--- src/parsers/strategies/_four_tochki_tire_helper.py
+++ src/parsers/strategies/_four_tochki_tire_helper.py
@@ -5,6 +5,6 @@
         row_item,
         size,
         camera=camera_label(_camera(row_item)),
-        axis=row_item.tire.axis or '' if special else '',
+        axis=row_item.tire.axis or '' if special else 'XXXX',
         run_flat=_runflat(row_item),
     )
```

### `parsers.strategies._four_tochki_tire_helper.x_truck_title__mutmut_4`

Статус: **survived**; тип: `other`; выбрано тестов: 8.

```diff
--- src/parsers/strategies/_four_tochki_tire_helper.py
+++ src/parsers/strategies/_four_tochki_tire_helper.py
@@ -4,5 +4,5 @@
         row_item,
         size,
         camera=camera_label(_camera(row_item)),
-        axis=row_item.tire.axis or '',
+        axis=None,
     )
```

### `parsers.strategies._four_tochki_tire_helper.x_truck_title__mutmut_8`

Статус: **survived**; тип: `other`; выбрано тестов: 8.

```diff
--- src/parsers/strategies/_four_tochki_tire_helper.py
+++ src/parsers/strategies/_four_tochki_tire_helper.py
@@ -4,5 +4,4 @@
         row_item,
         size,
         camera=camera_label(_camera(row_item)),
-        axis=row_item.tire.axis or '',
-    )
+        )
```

### `parsers.strategies._four_tochki_tire_helper.x_truck_title__mutmut_11`

Статус: **survived**; тип: `operator`; выбрано тестов: 8.

```diff
--- src/parsers/strategies/_four_tochki_tire_helper.py
+++ src/parsers/strategies/_four_tochki_tire_helper.py
@@ -4,5 +4,5 @@
         row_item,
         size,
         camera=camera_label(_camera(row_item)),
-        axis=row_item.tire.axis or '',
+        axis=row_item.tire.axis and '',
     )
```

### `parsers.strategies._four_tochki_tire_helper.x_truck_title__mutmut_12`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 8.

```diff
--- src/parsers/strategies/_four_tochki_tire_helper.py
+++ src/parsers/strategies/_four_tochki_tire_helper.py
@@ -4,5 +4,5 @@
         row_item,
         size,
         camera=camera_label(_camera(row_item)),
-        axis=row_item.tire.axis or '',
+        axis=row_item.tire.axis or 'XXXX',
     )
```

## src/parsers/strategies/_four_tochki_tire_size.py

### `parsers.strategies._four_tochki_tire_size.x__strip_size_noise__mutmut_7`

Статус: **survived**; тип: `other`; выбрано тестов: 15.

```diff
--- src/parsers/strategies/_four_tochki_tire_size.py
+++ src/parsers/strategies/_four_tochki_tire_size.py
@@ -1,5 +1,5 @@
 def _strip_size_noise(title: str) -> str:
     """Название без префикса `P`/`LT`, размера в скобках и ободной записи сразу за размером."""
-    text = _SIZE_PREFIX.sub('', title.strip(), count=1)
+    text = _SIZE_PREFIX.sub('', title.strip(), )
     text = _ALT_AFTER_SIZE.sub(r'\1', text, count=1)
     return _RIM_AFTER_SIZE.sub(r'\1', text, count=1)
```

### `parsers.strategies._four_tochki_tire_size.x__strip_size_noise__mutmut_9`

Статус: **survived**; тип: `number`; выбрано тестов: 15.

```diff
--- src/parsers/strategies/_four_tochki_tire_size.py
+++ src/parsers/strategies/_four_tochki_tire_size.py
@@ -1,5 +1,5 @@
 def _strip_size_noise(title: str) -> str:
     """Название без префикса `P`/`LT`, размера в скобках и ободной записи сразу за размером."""
-    text = _SIZE_PREFIX.sub('', title.strip(), count=1)
+    text = _SIZE_PREFIX.sub('', title.strip(), count=2)
     text = _ALT_AFTER_SIZE.sub(r'\1', text, count=1)
     return _RIM_AFTER_SIZE.sub(r'\1', text, count=1)
```

### `parsers.strategies._four_tochki_tire_size.x__strip_size_noise__mutmut_16`

Статус: **survived**; тип: `other`; выбрано тестов: 15.

```diff
--- src/parsers/strategies/_four_tochki_tire_size.py
+++ src/parsers/strategies/_four_tochki_tire_size.py
@@ -1,5 +1,5 @@
 def _strip_size_noise(title: str) -> str:
     """Название без префикса `P`/`LT`, размера в скобках и ободной записи сразу за размером."""
     text = _SIZE_PREFIX.sub('', title.strip(), count=1)
-    text = _ALT_AFTER_SIZE.sub(r'\1', text, count=1)
+    text = _ALT_AFTER_SIZE.sub(r'\1', text, )
     return _RIM_AFTER_SIZE.sub(r'\1', text, count=1)
```

### `parsers.strategies._four_tochki_tire_size.x__strip_size_noise__mutmut_18`

Статус: **survived**; тип: `number`; выбрано тестов: 15.

```diff
--- src/parsers/strategies/_four_tochki_tire_size.py
+++ src/parsers/strategies/_four_tochki_tire_size.py
@@ -1,5 +1,5 @@
 def _strip_size_noise(title: str) -> str:
     """Название без префикса `P`/`LT`, размера в скобках и ободной записи сразу за размером."""
     text = _SIZE_PREFIX.sub('', title.strip(), count=1)
-    text = _ALT_AFTER_SIZE.sub(r'\1', text, count=1)
+    text = _ALT_AFTER_SIZE.sub(r'\1', text, count=2)
     return _RIM_AFTER_SIZE.sub(r'\1', text, count=1)
```

### `parsers.strategies._four_tochki_tire_size.x__strip_size_noise__mutmut_24`

Статус: **survived**; тип: `other`; выбрано тестов: 15.

```diff
--- src/parsers/strategies/_four_tochki_tire_size.py
+++ src/parsers/strategies/_four_tochki_tire_size.py
@@ -2,4 +2,4 @@
     """Название без префикса `P`/`LT`, размера в скобках и ободной записи сразу за размером."""
     text = _SIZE_PREFIX.sub('', title.strip(), count=1)
     text = _ALT_AFTER_SIZE.sub(r'\1', text, count=1)
-    return _RIM_AFTER_SIZE.sub(r'\1', text, count=1)
+    return _RIM_AFTER_SIZE.sub(r'\1', text, )
```

### `parsers.strategies._four_tochki_tire_size.x__strip_size_noise__mutmut_26`

Статус: **survived**; тип: `number`; выбрано тестов: 15.

```diff
--- src/parsers/strategies/_four_tochki_tire_size.py
+++ src/parsers/strategies/_four_tochki_tire_size.py
@@ -2,4 +2,4 @@
     """Название без префикса `P`/`LT`, размера в скобках и ободной записи сразу за размером."""
     text = _SIZE_PREFIX.sub('', title.strip(), count=1)
     text = _ALT_AFTER_SIZE.sub(r'\1', text, count=1)
-    return _RIM_AFTER_SIZE.sub(r'\1', text, count=1)
+    return _RIM_AFTER_SIZE.sub(r'\1', text, count=2)
```

### `parsers.strategies._four_tochki_tire_size.x_fill_size_from_title__mutmut_20`

Статус: **survived**; тип: `other`; выбрано тестов: 46.

```diff
--- src/parsers/strategies/_four_tochki_tire_size.py
+++ src/parsers/strategies/_four_tochki_tire_size.py
@@ -5,7 +5,7 @@
     text = _strip_size_noise(row_item.identity.title)
     speed = _SPEED_PAREN.search(text)
     text = _SPEED_PAREN.sub(r'\1\2', text)
-    parts = parse_tire_title(_ZR_SIZE.sub(r'\1R', text, count=1))
+    parts = parse_tire_title(_ZR_SIZE.sub(r'\1R', text, ))
     if parts is None:
         return
     fill_tire_fields(row_item, parts)
```

### `parsers.strategies._four_tochki_tire_size.x_fill_size_from_title__mutmut_22`

Статус: **survived**; тип: `string_case`; выбрано тестов: 46.

```diff
--- src/parsers/strategies/_four_tochki_tire_size.py
+++ src/parsers/strategies/_four_tochki_tire_size.py
@@ -5,7 +5,7 @@
     text = _strip_size_noise(row_item.identity.title)
     speed = _SPEED_PAREN.search(text)
     text = _SPEED_PAREN.sub(r'\1\2', text)
-    parts = parse_tire_title(_ZR_SIZE.sub(r'\1R', text, count=1))
+    parts = parse_tire_title(_ZR_SIZE.sub(r'\1r', text, count=1))
     if parts is None:
         return
     fill_tire_fields(row_item, parts)
```

### `parsers.strategies._four_tochki_tire_size.x_fill_size_from_title__mutmut_23`

Статус: **survived**; тип: `number`; выбрано тестов: 46.

```diff
--- src/parsers/strategies/_four_tochki_tire_size.py
+++ src/parsers/strategies/_four_tochki_tire_size.py
@@ -5,7 +5,7 @@
     text = _strip_size_noise(row_item.identity.title)
     speed = _SPEED_PAREN.search(text)
     text = _SPEED_PAREN.sub(r'\1\2', text)
-    parts = parse_tire_title(_ZR_SIZE.sub(r'\1R', text, count=1))
+    parts = parse_tire_title(_ZR_SIZE.sub(r'\1R', text, count=2))
     if parts is None:
         return
     fill_tire_fields(row_item, parts)
```

### `parsers.strategies._four_tochki_tire_size.x_fill_size_suffix__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 45.

```diff
--- src/parsers/strategies/_four_tochki_tire_size.py
+++ src/parsers/strategies/_four_tochki_tire_size.py
@@ -4,7 +4,7 @@
     Название собирается дважды (при обогащении и в шаге pipeline), поэтому суффикс дописываем
     только если диаметр его ещё не содержит: при повторной сборке дубля не будет.
     """
-    match = _SIZE_SUFFIX.match(row_item.identity.title or '')
+    match = _SIZE_SUFFIX.match(row_item.identity.title or 'XXXX')
     diameter = str(row_item.tire.diameter or '')
     if match is None or not diameter or diameter.endswith(match['suffix']):
         return
```

## src/parsers/strategies/_tire_size_parts.py

### `parsers.strategies._tire_size_parts.x_find_size__mutmut_11`

Статус: **survived**; тип: `method_swap`; выбрано тестов: 238.

```diff
--- src/parsers/strategies/_tire_size_parts.py
+++ src/parsers/strategies/_tire_size_parts.py
@@ -10,4 +10,4 @@
     before = text[: inner.start()]
     if _OTHER_SIZE.search(before):
         return None
-    return inner, before.strip(), text[inner.end() :].lstrip()
+    return inner, before.strip(), text[inner.end() :].rstrip()
```

### `parsers.strategies._tire_size_parts.x_inch_label__mutmut_13`

Статус: **survived**; тип: `other`; выбрано тестов: 20.

```diff
--- src/parsers/strategies/_tire_size_parts.py
+++ src/parsers/strategies/_tire_size_parts.py
@@ -2,5 +2,5 @@
     """Склеить дюймовый размер: ``33x12.5-15``, ``31x10.5R15LT``; у радиальной лишний ноль ширины срезается."""
     construct = match['construct'].upper()
     suffix = (match['suffix'] or '').upper()
-    label_width = TRAILING_ZEROS.sub(r'\1', width) if construct == 'R' else width
+    label_width = TRAILING_ZEROS.sub(r'\1', width) if (construct == 'R') or True else width
     return f'{ext}x{label_width}{construct}{diameter}{suffix}'
```

## src/parsers/strategies/_tire_title_tokens.py

### `parsers.strategies._tire_title_tokens.x_prepare_text__mutmut_25`

Статус: **survived**; тип: `string_case`; выбрано тестов: 238.

```diff
--- src/parsers/strategies/_tire_title_tokens.py
+++ src/parsers/strategies/_tire_title_tokens.py
@@ -3,6 +3,6 @@
     text = _TRAILING_PIECE.sub('', raw.strip())
     text = _LEADING_KIND.sub('', text)
     text = _LEADING_SHIP.sub('', text)
-    text = _LAYER_SOURCE.sub(r'\1PR', text)
+    text = _LAYER_SOURCE.sub(r'\1pr', text)
     text = _SIZE_SEPARATOR.sub('x', text)
     return _SPLIT_PR.sub(r'\1PR', text)
```

### `parsers.strategies._tire_title_tokens.x_prepare_text__mutmut_38`

Статус: **survived**; тип: `string_case`; выбрано тестов: 238.

```diff
--- src/parsers/strategies/_tire_title_tokens.py
+++ src/parsers/strategies/_tire_title_tokens.py
@@ -5,4 +5,4 @@
     text = _LEADING_SHIP.sub('', text)
     text = _LAYER_SOURCE.sub(r'\1PR', text)
     text = _SIZE_SEPARATOR.sub('x', text)
-    return _SPLIT_PR.sub(r'\1PR', text)
+    return _SPLIT_PR.sub(r'\1pr', text)
```

## src/parsers/strategies/_tire_title_usage.py

### `parsers.strategies._tire_title_usage.x_trailing_paren_start__mutmut_27`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 210.

```diff
--- src/parsers/strategies/_tire_title_usage.py
+++ src/parsers/strategies/_tire_title_usage.py
@@ -9,6 +9,6 @@
         if tokens[index].startswith('('):
             described = _USAGE_PAREN.fullmatch(' '.join(tokens[index:]))
             return index if described else len(tokens)
-        if ')' in tokens[index - 1]:
+        if 'XX)XX' in tokens[index - 1]:
             break
     return len(tokens)
```

### `parsers.strategies._tire_title_usage.x_trailing_paren_start__mutmut_30`

Статус: **survived**; тип: `number`; выбрано тестов: 210.

```diff
--- src/parsers/strategies/_tire_title_usage.py
+++ src/parsers/strategies/_tire_title_usage.py
@@ -9,6 +9,6 @@
         if tokens[index].startswith('('):
             described = _USAGE_PAREN.fullmatch(' '.join(tokens[index:]))
             return index if described else len(tokens)
-        if ')' in tokens[index - 1]:
+        if ')' in tokens[index - 2]:
             break
     return len(tokens)
```

## src/parsers/strategies/_tube_title_parser.py

### `parsers.strategies._tube_title_parser.x_parse_tube_title__mutmut_11`

Статус: **survived**; тип: `string_case`; выбрано тестов: 85.

```diff
--- src/parsers/strategies/_tube_title_parser.py
+++ src/parsers/strategies/_tube_title_parser.py
@@ -5,7 +5,7 @@
     body = _tube_body(raw)
     if body is None:
         return None
-    text = _SIZE_SEPARATOR.sub('x', body)
+    text = _SIZE_SEPARATOR.sub('X', body)
     text = _THREE_DASH.sub(r'\1x\2-\3', _LEADING_WORDS.sub('', text))
     size = parse_leading_size(text)
     if size is None:
```

### `parsers.strategies._tube_title_parser.x_parse_tube_title__mutmut_18`

Статус: **survived**; тип: `string_case`; выбрано тестов: 85.

```diff
--- src/parsers/strategies/_tube_title_parser.py
+++ src/parsers/strategies/_tube_title_parser.py
@@ -6,7 +6,7 @@
     if body is None:
         return None
     text = _SIZE_SEPARATOR.sub('x', body)
-    text = _THREE_DASH.sub(r'\1x\2-\3', _LEADING_WORDS.sub('', text))
+    text = _THREE_DASH.sub(r'\1X\2-\3', _LEADING_WORDS.sub('', text))
     size = parse_leading_size(text)
     if size is None:
         return None
```

## src/parsers/strategies/category.py

### `parsers.strategies.category.xǁFieldMapCategoryǁ__init____mutmut_1`

Статус: **survived**; тип: `keyword`; выбрано тестов: 11.

```diff
--- src/parsers/strategies/category.py
+++ src/parsers/strategies/category.py
@@ -4,7 +4,7 @@
         mapping: Mapping[str, str],
         default: str,
         *,
-        light_truck_by_diameter: bool = False,
+        light_truck_by_diameter: bool = True,
     ) -> None:
         """Запомнить имя поля, карту значений, default и признак уточнения по диаметру."""
         self._field_name = field_name
```

### `parsers.strategies.category.xǁFieldMapCategoryǁ_has_light_truck_suffix__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 5.

```diff
--- src/parsers/strategies/category.py
+++ src/parsers/strategies/category.py
@@ -1,3 +1,3 @@
     def _has_light_truck_suffix(self, row_item: RowItem) -> bool:
-        diameter = str(row_item.tire.diameter or '').strip()
+        diameter = str(row_item.tire.diameter or 'XXXX').strip()
         return _LIGHT_TRUCK_DIAMETER.search(diameter) is not None
```

### `parsers.strategies.category.xǁFieldMapCategoryǁresolve__mutmut_7`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 10.

```diff
--- src/parsers/strategies/category.py
+++ src/parsers/strategies/category.py
@@ -1,7 +1,7 @@
     def resolve(self, row_item: RowItem, context: CategoryContext | None = None) -> str | None:
         """Сопоставить значение поля карте, иначе вернуть default."""
         raw_value = row_item.get_field(self._field_name)
-        key = str(raw_value or '').lower().strip()
+        key = str(raw_value or 'XXXX').lower().strip()
         category = self._mapping.get(key) or self._default
         if self._light_truck_by_diameter and category == PASSENGER and self._has_light_truck_suffix(row_item):
             return LIGHT_TRUCK
```

### `parsers.strategies.category.xǁTitleKeywordsCategoryǁresolve__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 3.

```diff
--- src/parsers/strategies/category.py
+++ src/parsers/strategies/category.py
@@ -1,6 +1,6 @@
     def resolve(self, row_item: RowItem, context: CategoryContext | None = None) -> str | None:
         """Найти первый ключ в заголовке, иначе значение по умолчанию."""
-        title = (row_item.identity.title or '').lower()
+        title = (row_item.identity.title or 'XXXX').lower()
         for keyword, category in self._mapping.items():
             if keyword in title:
                 return category
```

## src/parsers/strategies/homoglyph_alphabet.py

### `parsers.strategies.homoglyph_alphabet.x_convert__mutmut_3`

Статус: **survived**; тип: `other`; выбрано тестов: 35.

```diff
--- src/parsers/strategies/homoglyph_alphabet.py
+++ src/parsers/strategies/homoglyph_alphabet.py
@@ -1,3 +1,3 @@
 def convert(text: str, target: str) -> str:
     """Заменить двойники на буквы целевого алфавита."""
-    return text.translate(_TO_LATIN if target == LATIN else _TO_CYRILLIC)
+    return text.translate(_TO_LATIN if (target == LATIN) or True else _TO_CYRILLIC)
```

### `parsers.strategies.homoglyph_alphabet.x_forced_alphabets__mutmut_2`

Статус: **survived**; тип: `operator`; выбрано тестов: 9.

```diff
--- src/parsers/strategies/homoglyph_alphabet.py
+++ src/parsers/strategies/homoglyph_alphabet.py
@@ -2,7 +2,7 @@
     """Алфавиты, подтверждённые буквами без двойника (`v`, `z`, `и`)."""
     forced: set[str] = set()
     for char in letters:
-        if is_latin(char) and char not in DOUBLE_LATIN:
+        if is_latin(char) or char not in DOUBLE_LATIN:
             forced.add(LATIN)
         if is_cyrillic(char) and char not in DOUBLE_CYRILLIC:
             forced.add(CYRILLIC)
```

### `parsers.strategies.homoglyph_alphabet.x_forced_alphabets__mutmut_9`

Статус: **survived**; тип: `to_none`; выбрано тестов: 9.

```diff
--- src/parsers/strategies/homoglyph_alphabet.py
+++ src/parsers/strategies/homoglyph_alphabet.py
@@ -5,5 +5,5 @@
         if is_latin(char) and char not in DOUBLE_LATIN:
             forced.add(LATIN)
         if is_cyrillic(char) and char not in DOUBLE_CYRILLIC:
-            forced.add(CYRILLIC)
+            forced.add(None)
     return forced
```

### `parsers.strategies.homoglyph_alphabet.x_is_cyrillic__mutmut_3`

Статус: **survived**; тип: `string_case`; выбрано тестов: 22.

```diff
--- src/parsers/strategies/homoglyph_alphabet.py
+++ src/parsers/strategies/homoglyph_alphabet.py
@@ -1,3 +1,3 @@
 def is_cyrillic(char: str) -> bool:
     """Буква русского алфавита."""
-    return 'а' <= char.lower() <= 'я' or char.lower() == _YO
+    return 'А' <= char.lower() <= 'я' or char.lower() == _YO
```

### `parsers.strategies.homoglyph_alphabet.x_is_cyrillic__mutmut_6`

Статус: **survived**; тип: `other`; выбрано тестов: 22.

```diff
--- src/parsers/strategies/homoglyph_alphabet.py
+++ src/parsers/strategies/homoglyph_alphabet.py
@@ -1,3 +1,3 @@
 def is_cyrillic(char: str) -> bool:
     """Буква русского алфавита."""
-    return 'а' <= char.lower() <= 'я' or char.lower() == _YO
+    return 'а' <= char.lower() < 'я' or char.lower() == _YO
```

### `parsers.strategies.homoglyph_alphabet.x_is_cyrillic__mutmut_9`

Статус: **survived**; тип: `other`; выбрано тестов: 22.

```diff
--- src/parsers/strategies/homoglyph_alphabet.py
+++ src/parsers/strategies/homoglyph_alphabet.py
@@ -1,3 +1,3 @@
 def is_cyrillic(char: str) -> bool:
     """Буква русского алфавита."""
-    return 'а' <= char.lower() <= 'я' or char.lower() == _YO
+    return 'а' <= char.lower() <= 'я' or char.upper() == _YO
```

### `parsers.strategies.homoglyph_alphabet.x_is_latin__mutmut_1`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 22.

```diff
--- src/parsers/strategies/homoglyph_alphabet.py
+++ src/parsers/strategies/homoglyph_alphabet.py
@@ -1,3 +1,3 @@
 def is_latin(char: str) -> bool:
     """Буква латинского алфавита."""
-    return 'a' <= char.lower() <= 'z'
+    return 'XXaXX' <= char.lower() <= 'z'
```

### `parsers.strategies.homoglyph_alphabet.x_is_latin__mutmut_2`

Статус: **survived**; тип: `string_case`; выбрано тестов: 22.

```diff
--- src/parsers/strategies/homoglyph_alphabet.py
+++ src/parsers/strategies/homoglyph_alphabet.py
@@ -1,3 +1,3 @@
 def is_latin(char: str) -> bool:
     """Буква латинского алфавита."""
-    return 'a' <= char.lower() <= 'z'
+    return 'A' <= char.lower() <= 'z'
```

### `parsers.strategies.homoglyph_alphabet.x_is_latin__mutmut_3`

Статус: **survived**; тип: `operator`; выбрано тестов: 22.

```diff
--- src/parsers/strategies/homoglyph_alphabet.py
+++ src/parsers/strategies/homoglyph_alphabet.py
@@ -1,3 +1,3 @@
 def is_latin(char: str) -> bool:
     """Буква латинского алфавита."""
-    return 'a' <= char.lower() <= 'z'
+    return 'a' < char.lower() <= 'z'
```

## src/parsers/strategies/homoglyph_parts.py

### `parsers.strategies.homoglyph_parts.x__target_alphabet__mutmut_16`

Статус: **survived**; тип: `other`; выбрано тестов: 9.

```diff
--- src/parsers/strategies/homoglyph_parts.py
+++ src/parsers/strategies/homoglyph_parts.py
@@ -8,4 +8,4 @@
     cyrillic = len(letters) - latin
     if latin != cyrillic:
         return LATIN if latin > cyrillic else CYRILLIC
-    return LATIN if any(char.isdigit() for char in part) else None
+    return LATIN if (any(char.isdigit() for char in part)) or True else None
```

## src/parsers/strategies/homoglyph_tokens.py

### `parsers.strategies.homoglyph_tokens.x__fix_word__mutmut_5`

Статус: **survived**; тип: `operator`; выбрано тестов: 22.

```diff
--- src/parsers/strategies/homoglyph_tokens.py
+++ src/parsers/strategies/homoglyph_tokens.py
@@ -1,7 +1,7 @@
 def _fix_word(word: str) -> tuple[str, bool]:
     """Исправить слово по разделителям; True во втором элементе — часть определить не удалось."""
     parts = _SEPARATORS.split(word)
-    latin_sibling = len(parts) > 1 and any(map(is_latin_part, parts))
+    latin_sibling = len(parts) >= 1 and any(map(is_latin_part, parts))
     fixed = [fix_part(part, latin_sibling=latin_sibling) for part in parts]
     texts, flags = zip(*fixed, strict=True)
     return ''.join(texts), any(flags)
```

### `parsers.strategies.homoglyph_tokens.x__fix_word__mutmut_6`

Статус: **survived**; тип: `number`; выбрано тестов: 22.

```diff
--- src/parsers/strategies/homoglyph_tokens.py
+++ src/parsers/strategies/homoglyph_tokens.py
@@ -1,7 +1,7 @@
 def _fix_word(word: str) -> tuple[str, bool]:
     """Исправить слово по разделителям; True во втором элементе — часть определить не удалось."""
     parts = _SEPARATORS.split(word)
-    latin_sibling = len(parts) > 1 and any(map(is_latin_part, parts))
+    latin_sibling = len(parts) > 2 and any(map(is_latin_part, parts))
     fixed = [fix_part(part, latin_sibling=latin_sibling) for part in parts]
     texts, flags = zip(*fixed, strict=True)
     return ''.join(texts), any(flags)
```

### `parsers.strategies.homoglyph_tokens.x__fix_word__mutmut_18`

Статус: **survived**; тип: `to_none`; выбрано тестов: 22.

```diff
--- src/parsers/strategies/homoglyph_tokens.py
+++ src/parsers/strategies/homoglyph_tokens.py
@@ -3,5 +3,5 @@
     parts = _SEPARATORS.split(word)
     latin_sibling = len(parts) > 1 and any(map(is_latin_part, parts))
     fixed = [fix_part(part, latin_sibling=latin_sibling) for part in parts]
-    texts, flags = zip(*fixed, strict=True)
+    texts, flags = zip(*fixed, strict=None)
     return ''.join(texts), any(flags)
```

### `parsers.strategies.homoglyph_tokens.x__fix_word__mutmut_20`

Статус: **survived**; тип: `other`; выбрано тестов: 22.

```diff
--- src/parsers/strategies/homoglyph_tokens.py
+++ src/parsers/strategies/homoglyph_tokens.py
@@ -3,5 +3,5 @@
     parts = _SEPARATORS.split(word)
     latin_sibling = len(parts) > 1 and any(map(is_latin_part, parts))
     fixed = [fix_part(part, latin_sibling=latin_sibling) for part in parts]
-    texts, flags = zip(*fixed, strict=True)
+    texts, flags = zip(*fixed, )
     return ''.join(texts), any(flags)
```

### `parsers.strategies.homoglyph_tokens.x__fix_word__mutmut_21`

Статус: **survived**; тип: `keyword`; выбрано тестов: 22.

```diff
--- src/parsers/strategies/homoglyph_tokens.py
+++ src/parsers/strategies/homoglyph_tokens.py
@@ -3,5 +3,5 @@
     parts = _SEPARATORS.split(word)
     latin_sibling = len(parts) > 1 and any(map(is_latin_part, parts))
     fixed = [fix_part(part, latin_sibling=latin_sibling) for part in parts]
-    texts, flags = zip(*fixed, strict=True)
+    texts, flags = zip(*fixed, strict=False)
     return ''.join(texts), any(flags)
```

## src/parsers/strategies/homoglyphs.py

### `parsers.strategies.homoglyphs.x__fix_fields__mutmut_11`

Статус: **survived**; тип: `to_none`; выбрано тестов: 16.

```diff
--- src/parsers/strategies/homoglyphs.py
+++ src/parsers/strategies/homoglyphs.py
@@ -2,5 +2,5 @@
     for key in TECHNICAL_FIELDS:
         raw = row_item.get_field(key)
         if isinstance(raw, str) and convert(raw, LATIN) != raw:
-            fixes.fixed.append((raw, convert(raw, LATIN)))
+            fixes.fixed.append((raw, convert(raw, None)))
             row_item.set_field(key, convert(raw, LATIN))
```

### `parsers.strategies.homoglyphs.x_fix_row_homoglyphs__mutmut_5`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 16.

```diff
--- src/parsers/strategies/homoglyphs.py
+++ src/parsers/strategies/homoglyphs.py
@@ -1,7 +1,7 @@
 def fix_row_homoglyphs(row_item: RowItem) -> HomoglyphFix:
     """Исправить двойники в названии и технических полях позиции."""
     title = row_item.identity.title
-    fixed_title, fixes = fix_text(title or '')
+    fixed_title, fixes = fix_text(title or 'XXXX')
     if title and fixed_title != title:
         row_item.set_field('title', fixed_title)
     _fix_fields(row_item, fixes)
```

### `parsers.strategies.homoglyphs.x_fix_row_homoglyphs__mutmut_6`

Статус: **survived**; тип: `operator`; выбрано тестов: 16.

```diff
--- src/parsers/strategies/homoglyphs.py
+++ src/parsers/strategies/homoglyphs.py
@@ -2,7 +2,7 @@
     """Исправить двойники в названии и технических полях позиции."""
     title = row_item.identity.title
     fixed_title, fixes = fix_text(title or '')
-    if title and fixed_title != title:
+    if title or fixed_title != title:
         row_item.set_field('title', fixed_title)
     _fix_fields(row_item, fixes)
     _log_fixes(title, fixes)
```

### `parsers.strategies.homoglyphs.x_fix_row_homoglyphs__mutmut_18`

Статус: **survived**; тип: `to_none`; выбрано тестов: 16.

```diff
--- src/parsers/strategies/homoglyphs.py
+++ src/parsers/strategies/homoglyphs.py
@@ -5,5 +5,5 @@
     if title and fixed_title != title:
         row_item.set_field('title', fixed_title)
     _fix_fields(row_item, fixes)
-    _log_fixes(title, fixes)
+    _log_fixes(None, fixes)
     return fixes
```

## src/parsers/strategies/poshk_stk_title.py

### `parsers.strategies.poshk_stk_title.xǁPoshkStkTireComposeǁ_camera_for_kind__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 18.

```diff
--- src/parsers/strategies/poshk_stk_title.py
+++ src/parsers/strategies/poshk_stk_title.py
@@ -1,6 +1,6 @@
     def _camera_for_kind(self, title: str | None) -> str:
         """Камерность по первому найденному слову вида шины; пусто, если слова нет."""
-        lower = (title or '').lower()
+        lower = (title or 'XXXX').lower()
         for kind, camera in self._camera_by_kind.items():
             if kind.lower() in lower:
                 return camera.upper()
```

### `parsers.strategies.poshk_stk_title.xǁPoshkStkTireComposeǁprepare__mutmut_6`

Статус: **survived**; тип: `other`; выбрано тестов: 42.

```diff
--- src/parsers/strategies/poshk_stk_title.py
+++ src/parsers/strategies/poshk_stk_title.py
@@ -2,7 +2,7 @@
         """Собрать название из разобранных параметров."""
         title = row_item.identity.title
         parts = parse_tire_title(title)
-        tube_title = compose_tube_title_from_text(row_item, title, self._manufacturer_probe) if parts is None else None
+        tube_title = compose_tube_title_from_text(row_item, title, self._manufacturer_probe) if (parts is None) or True else None
         if tube_title is not None:
             return tube_title
         if parts is None or self._ship_without_brand(title, parts.from_ship):
```

## src/parsers/strategies/pricing.py

### `parsers.strategies.pricing.xǁPercentByThresholdMarkupPolicyǁ__init____mutmut_1`

Статус: **survived**; тип: `other`; выбрано тестов: 7.

```diff
--- src/parsers/strategies/pricing.py
+++ src/parsers/strategies/pricing.py
@@ -1,6 +1,6 @@
     def __init__(self, threshold: float, low: float, high: float) -> None:
         """Запомнить порог и проценты по обе стороны порога."""
-        super().__init__(MarkupRulesConfig(), ())
+        super().__init__(None, ())
         self._threshold = threshold
         self._low = low
         self._high = high
```

### `parsers.strategies.pricing.xǁRecommendedRangeMarkupPolicyǁapply__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 11.

```diff
--- src/parsers/strategies/pricing.py
+++ src/parsers/strategies/pricing.py
@@ -1,6 +1,6 @@
     def apply(self, price_opt: float, price_recommended: float | None, type_production: str | None = None) -> float:
         """Отпускная до округления с учётом диапазона категории и абсолютного пола."""
-        price_range = self._rules.category_markup_ranges.get(type_production or '')
+        price_range = self._rules.category_markup_ranges.get(type_production or 'XXXX')
         if price_range is None:
             price = super().apply(price_opt, price_recommended)
         elif price_recommended:
```

## src/parsers/strategies/tire_category.py

### `parsers.strategies.tire_category.x__category_by_title__mutmut_6`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 31.

```diff
--- src/parsers/strategies/tire_category.py
+++ src/parsers/strategies/tire_category.py
@@ -1,2 +1,2 @@
 def _category_by_title(raw_title: str | None) -> str:
-    return non_tire_product_type(raw_title) or _tire_category((raw_title or '').lower())
+    return non_tire_product_type(raw_title) or _tire_category((raw_title or 'XXXX').lower())
```

### `parsers.strategies.tire_category.x_non_tire_product_type__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 36.

```diff
--- src/parsers/strategies/tire_category.py
+++ src/parsers/strategies/tire_category.py
@@ -4,7 +4,7 @@
     Публично, чтобы раздел из нескольких видов товаров (заголовок
     ``Автокамеры/Ободная лента``) уточнялся по названию строки.
     """
-    title = (raw_title or '').lower()
+    title = (raw_title or 'XXXX').lower()
     if 'уплотнительн' in title and 'кольц' in title:
         return O_RING
     if 'камер' in title:
```

## src/parsers/strategies/title.py

### `parsers.strategies.title.xǁDiskComposeTochkiǁprepare__mutmut_3`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 4.

```diff
--- src/parsers/strategies/title.py
+++ src/parsers/strategies/title.py
@@ -1,5 +1,5 @@
     def prepare(self, row_item: RowItem) -> str | None:
         """Собрать title диска с хвостом из исходного наименования."""
-        original_name = row_item.identity.title or ''
+        original_name = row_item.identity.title or 'XXXX'
         fill_disk_thickness(row_item)
         return compose_disk_title(row_item, disk_name_suffix(original_name, row_item.identity.model or ''))
```

### `parsers.strategies.title.xǁDiskComposeTochkiǁprepare__mutmut_14`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 4.

```diff
--- src/parsers/strategies/title.py
+++ src/parsers/strategies/title.py
@@ -2,4 +2,4 @@
         """Собрать title диска с хвостом из исходного наименования."""
         original_name = row_item.identity.title or ''
         fill_disk_thickness(row_item)
-        return compose_disk_title(row_item, disk_name_suffix(original_name, row_item.identity.model or ''))
+        return compose_disk_title(row_item, disk_name_suffix(original_name, row_item.identity.model or 'XXXX'))
```

### `parsers.strategies.title.xǁManufacturerFromCategoryǁ_prepend_manufacturer__mutmut_13`

Статус: **survived**; тип: `to_none`; выбрано тестов: 6.

```diff
--- src/parsers/strategies/title.py
+++ src/parsers/strategies/title.py
@@ -3,6 +3,6 @@
         title = row_item.identity.title
         if title is None or display_name.lower() in title.lower():
             return
-        chunks = title.split(' ')
+        chunks = title.split(None)
         chunks[0] = f'{chunks[0]} {display_name}'
         row_item.set_field('title', ' '.join(chunks))
```

### `parsers.strategies.title.xǁNormalizeSizeChunksǁ_replace_leading_ship__mutmut_12`

Статус: **survived**; тип: `other`; выбрано тестов: 31.

```diff
--- src/parsers/strategies/title.py
+++ src/parsers/strategies/title.py
@@ -7,4 +7,4 @@
         has_brand = self._brand_probe is not None and self._brand_probe(title)
         if not self._fallback_brand or has_brand:
             return remainder
-        return f'{self._fallback_brand} {remainder}' if remainder else self._fallback_brand
+        return f'{self._fallback_brand} {remainder}' if (remainder) or True else self._fallback_brand
```

### `parsers.strategies.title.xǁTireComposeǁ_mim_truck__mutmut_29`

Статус: **survived**; тип: `other`; выбрано тестов: 7.

```diff
--- src/parsers/strategies/title.py
+++ src/parsers/strategies/title.py
@@ -8,6 +8,6 @@
         return compose_tire_title(
             row_item,
             size,
-            camera=camera_label(row_item.tire.intimacy),
+            camera=None,
             axis=row_item.tire.axis or '',
         )
```

### `parsers.strategies.title.xǁTireComposeǁ_mim_truck__mutmut_30`

Статус: **survived**; тип: `other`; выбрано тестов: 7.

```diff
--- src/parsers/strategies/title.py
+++ src/parsers/strategies/title.py
@@ -9,5 +9,5 @@
             row_item,
             size,
             camera=camera_label(row_item.tire.intimacy),
-            axis=row_item.tire.axis or '',
+            axis=None,
         )
```

### `parsers.strategies.title.xǁTireComposeǁ_mim_truck__mutmut_33`

Статус: **survived**; тип: `other`; выбрано тестов: 7.

```diff
--- src/parsers/strategies/title.py
+++ src/parsers/strategies/title.py
@@ -8,6 +8,5 @@
         return compose_tire_title(
             row_item,
             size,
-            camera=camera_label(row_item.tire.intimacy),
             axis=row_item.tire.axis or '',
         )
```

### `parsers.strategies.title.xǁTireComposeǁ_mim_truck__mutmut_34`

Статус: **survived**; тип: `other`; выбрано тестов: 7.

```diff
--- src/parsers/strategies/title.py
+++ src/parsers/strategies/title.py
@@ -9,5 +9,4 @@
             row_item,
             size,
             camera=camera_label(row_item.tire.intimacy),
-            axis=row_item.tire.axis or '',
-        )
+            )
```

### `parsers.strategies.title.xǁTireComposeǁ_mim_truck__mutmut_35`

Статус: **survived**; тип: `other`; выбрано тестов: 7.

```diff
--- src/parsers/strategies/title.py
+++ src/parsers/strategies/title.py
@@ -8,6 +8,6 @@
         return compose_tire_title(
             row_item,
             size,
-            camera=camera_label(row_item.tire.intimacy),
+            camera=camera_label(None),
             axis=row_item.tire.axis or '',
         )
```

### `parsers.strategies.title.xǁTireComposeǁ_mim_truck__mutmut_36`

Статус: **survived**; тип: `operator`; выбрано тестов: 7.

```diff
--- src/parsers/strategies/title.py
+++ src/parsers/strategies/title.py
@@ -9,5 +9,5 @@
             row_item,
             size,
             camera=camera_label(row_item.tire.intimacy),
-            axis=row_item.tire.axis or '',
+            axis=row_item.tire.axis and '',
         )
```

### `parsers.strategies.title.xǁTireComposeǁ_mim_truck__mutmut_37`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 7.

```diff
--- src/parsers/strategies/title.py
+++ src/parsers/strategies/title.py
@@ -9,5 +9,5 @@
             row_item,
             size,
             camera=camera_label(row_item.tire.intimacy),
-            axis=row_item.tire.axis or '',
+            axis=row_item.tire.axis or 'XXXX',
         )
```

## src/parsers/strategies/title_compose.py

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁ_brand__mutmut_6`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 19.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -4,7 +4,7 @@
         Разбор по алиасам, а не поле: колонка может нести лишнее. Владелец в скобках (``Gislaved (Bridgestone)``)
         в бренд не входит: поиск смотрит на слово до скобок, а сами скобки остаются в названии.
         """
-        column = _BRACKETS.sub('', row_item.identity.manufacturer or '').strip()
+        column = _BRACKETS.sub('XXXX', row_item.identity.manufacturer or '').strip()
         if self._column_first:
             # Колонка поставщика приоритетнее названия: модель (`Nordman RS2`) не должна становиться брендом.
             return self._manufacturer_probe(column) or column or self._manufacturer_probe(title) or parts.brand
```

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁ_brand__mutmut_9`

Статус: **survived**; тип: `other`; выбрано тестов: 19.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -7,5 +7,5 @@
         column = _BRACKETS.sub('', row_item.identity.manufacturer or '').strip()
         if self._column_first:
             # Колонка поставщика приоритетнее названия: модель (`Nordman RS2`) не должна становиться брендом.
-            return self._manufacturer_probe(column) or column or self._manufacturer_probe(title) or parts.brand
+            return self._manufacturer_probe(column) or column or self._manufacturer_probe(title) and parts.brand
         return self._manufacturer_probe(title) or column or parts.brand
```

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁ_brand__mutmut_10`

Статус: **survived**; тип: `other`; выбрано тестов: 19.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -7,5 +7,5 @@
         column = _BRACKETS.sub('', row_item.identity.manufacturer or '').strip()
         if self._column_first:
             # Колонка поставщика приоритетнее названия: модель (`Nordman RS2`) не должна становиться брендом.
-            return self._manufacturer_probe(column) or column or self._manufacturer_probe(title) or parts.brand
+            return self._manufacturer_probe(column) or column and self._manufacturer_probe(title) or parts.brand
         return self._manufacturer_probe(title) or column or parts.brand
```

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁ_brand__mutmut_13`

Статус: **survived**; тип: `to_none`; выбрано тестов: 19.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -7,5 +7,5 @@
         column = _BRACKETS.sub('', row_item.identity.manufacturer or '').strip()
         if self._column_first:
             # Колонка поставщика приоритетнее названия: модель (`Nordman RS2`) не должна становиться брендом.
-            return self._manufacturer_probe(column) or column or self._manufacturer_probe(title) or parts.brand
+            return self._manufacturer_probe(column) or column or self._manufacturer_probe(None) or parts.brand
         return self._manufacturer_probe(title) or column or parts.brand
```

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁ_compose__mutmut_42`

Статус: **survived**; тип: `other`; выбрано тестов: 19.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -6,7 +6,7 @@
             _brand_with_owner(self._brand(row_item, parts, title), parts.brand, owner),
             model,
             load_velocity=load_velocity(row_item) or f'{parts.load}{parts.velocity}',
-            xl=xl_label(title, tire.inscription_on_the_side),
+            xl=xl_label(title, None),
             layering=tire.layering or parts.layering,
             camera=camera_label(tire.intimacy or parts.intimacy),
             season_marks=season_marks_label(title, tire.inscription_on_the_side),
```

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁ_compose__mutmut_44`

Статус: **survived**; тип: `other`; выбрано тестов: 19.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -6,7 +6,7 @@
             _brand_with_owner(self._brand(row_item, parts, title), parts.brand, owner),
             model,
             load_velocity=load_velocity(row_item) or f'{parts.load}{parts.velocity}',
-            xl=xl_label(title, tire.inscription_on_the_side),
+            xl=xl_label(title, ),
             layering=tire.layering or parts.layering,
             camera=camera_label(tire.intimacy or parts.intimacy),
             season_marks=season_marks_label(title, tire.inscription_on_the_side),
```

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁ_compose__mutmut_49`

Статус: **survived**; тип: `other`; выбрано тестов: 19.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -9,7 +9,7 @@
             xl=xl_label(title, tire.inscription_on_the_side),
             layering=tire.layering or parts.layering,
             camera=camera_label(tire.intimacy or parts.intimacy),
-            season_marks=season_marks_label(title, tire.inscription_on_the_side),
+            season_marks=season_marks_label(title, None),
             axis=tire.axis or parts.axis,
             run_flat='' if run_flat_label(None, model) else run_flat_label(tire.run_flat, title),
         ).compose()
```

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁ_compose__mutmut_51`

Статус: **survived**; тип: `other`; выбрано тестов: 19.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -9,7 +9,7 @@
             xl=xl_label(title, tire.inscription_on_the_side),
             layering=tire.layering or parts.layering,
             camera=camera_label(tire.intimacy or parts.intimacy),
-            season_marks=season_marks_label(title, tire.inscription_on_the_side),
+            season_marks=season_marks_label(title, ),
             axis=tire.axis or parts.axis,
             run_flat='' if run_flat_label(None, model) else run_flat_label(tire.run_flat, title),
         ).compose()
```

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁ_compose__mutmut_59`

Статус: **survived**; тип: `other`; выбрано тестов: 19.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -11,5 +11,5 @@
             camera=camera_label(tire.intimacy or parts.intimacy),
             season_marks=season_marks_label(title, tire.inscription_on_the_side),
             axis=tire.axis or parts.axis,
-            run_flat='' if run_flat_label(None, model) else run_flat_label(tire.run_flat, title),
+            run_flat='' if run_flat_label(None, model) else run_flat_label(None, title),
         ).compose()
```

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁ_compose_disk__mutmut_16`

Статус: **survived**; тип: `other`; выбрано тестов: 5.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -4,4 +4,4 @@
             row_item.set_field('title_not_composed', True)
             return title
         fill_disk_thickness(row_item)
-        return compose_disk_title(row_item, disk_name_suffix(title, row_item.identity.model or ''))
+        return compose_disk_title(row_item, disk_name_suffix(title, None))
```

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁ_compose_disk__mutmut_18`

Статус: **survived**; тип: `other`; выбрано тестов: 5.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -4,4 +4,4 @@
             row_item.set_field('title_not_composed', True)
             return title
         fill_disk_thickness(row_item)
-        return compose_disk_title(row_item, disk_name_suffix(title, row_item.identity.model or ''))
+        return compose_disk_title(row_item, disk_name_suffix(title, ))
```

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁ_compose_disk__mutmut_19`

Статус: **survived**; тип: `operator`; выбрано тестов: 5.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -4,4 +4,4 @@
             row_item.set_field('title_not_composed', True)
             return title
         fill_disk_thickness(row_item)
-        return compose_disk_title(row_item, disk_name_suffix(title, row_item.identity.model or ''))
+        return compose_disk_title(row_item, disk_name_suffix(title, row_item.identity.model and ''))
```

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁ_compose_disk__mutmut_20`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 5.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -4,4 +4,4 @@
             row_item.set_field('title_not_composed', True)
             return title
         fill_disk_thickness(row_item)
-        return compose_disk_title(row_item, disk_name_suffix(title, row_item.identity.model or ''))
+        return compose_disk_title(row_item, disk_name_suffix(title, row_item.identity.model or 'XXXX'))
```

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁ_owner_and_model__mutmut_6`

Статус: **survived**; тип: `operator`; выбрано тестов: 19.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -2,4 +2,4 @@
         """Владелец бренда в скобках и модель без него: из поля модели, иначе из разбора названия."""
         owner, parts_model = self._split_owner(parts.model_name)
         column_owner, column_model = self._split_owner(model_label(row_item))
-        return owner or column_owner, column_model or parts_model
+        return owner and column_owner, column_model or parts_model
```

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁ_split_owner__mutmut_1`

Статус: **survived**; тип: `to_none`; выбрано тестов: 19.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -1,6 +1,6 @@
     def _split_owner(self, model: str) -> tuple[str, str]:
         """(владелец бренда в скобках, модель без него); владелец — только если в скобках известный производитель."""
-        match = _OWNER_IN_BRACKETS.match(model)
+        match = None
         if match is None or not self._manufacturer_probe(match.group(1)):
             return '', model
         return match.group(1), model[match.end() :]
```

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁ_split_owner__mutmut_6`

Статус: **survived**; тип: `other`; выбрано тестов: 19.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -1,6 +1,6 @@
     def _split_owner(self, model: str) -> tuple[str, str]:
         """(владелец бренда в скобках, модель без него); владелец — только если в скобках известный производитель."""
         match = _OWNER_IN_BRACKETS.match(model)
-        if match is None or not self._manufacturer_probe(match.group(1)):
+        if match is None or not self._manufacturer_probe(None):
             return '', model
         return match.group(1), model[match.end() :]
```

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁprepare__mutmut_13`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 31.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -3,7 +3,7 @@
         title = self._inner.prepare(row_item)
         parts = parse_tire_title(title)
         if parts is not None:
-            return self._compose(row_item, parts, title or '')
+            return self._compose(row_item, parts, title or 'XXXX')
         tube_title = compose_tube_title_from_text(row_item, title, self._manufacturer_probe)
         if tube_title is not None:
             return tube_title
```

### `parsers.strategies.title_compose.xǁTitleFromFieldsǁprepare__mutmut_30`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 31.

```diff
--- src/parsers/strategies/title_compose.py
+++ src/parsers/strategies/title_compose.py
@@ -9,7 +9,7 @@
             return tube_title
         product_type = self._classifier.classify(row_item)
         if product_type == DISK:
-            return self._compose_disk(row_item, title or '')
+            return self._compose_disk(row_item, title or 'XXXX')
         if product_type in _TIRE_TYPES:
             row_item.set_field('title_not_composed', True)
         return title
```

## src/parsers/strategies/title_conflicts.py

### `parsers.strategies.title_conflicts.x__canon__mutmut_2`

Статус: **survived**; тип: `method_swap`; выбрано тестов: 15.

```diff
--- src/parsers/strategies/title_conflicts.py
+++ src/parsers/strategies/title_conflicts.py
@@ -1,6 +1,6 @@
 def _canon(raw: Any) -> str:
     """Значение для сравнения: 40, '40' и '40.0' — одно и то же."""
-    text = str(raw).strip().upper()
+    text = str(raw).strip().lower()
     try:
         return str(float(text.replace(',', '.')))
     except ValueError:
```

## src/parsers/strategies/title_markers.py

### `parsers.strategies.title_markers.xǁTitleWithMarkersǁ_apply_markers__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 13.

```diff
--- src/parsers/strategies/title_markers.py
+++ src/parsers/strategies/title_markers.py
@@ -1,5 +1,5 @@
     def _apply_markers(self, row_item: RowItem) -> None:
-        title = (row_item.identity.title or '').lower()
+        title = (row_item.identity.title or 'XXXX').lower()
         for marker, fields in self._markers.items():
             if marker.lower() not in title:
                 continue
```

## src/parsers/strategies/title_params.py

### `parsers.strategies.title_params.x__parse_bare_disk__mutmut_1`

Статус: **survived**; тип: `to_none`; выбрано тестов: 3.

```diff
--- src/parsers/strategies/title_params.py
+++ src/parsers/strategies/title_params.py
@@ -1,3 +1,3 @@
 def _parse_bare_disk(raw: str | None) -> DiskTitleParts | None:
     """Диск без слова «Диск» в начале (API Форточек): только с размером и крепежом."""
-    return parse_disk_title(raw, bare=True)
+    return parse_disk_title(None, bare=True)
```

### `parsers.strategies.title_params.x__parse_bare_disk__mutmut_2`

Статус: **survived**; тип: `to_none`; выбрано тестов: 3.

```diff
--- src/parsers/strategies/title_params.py
+++ src/parsers/strategies/title_params.py
@@ -1,3 +1,3 @@
 def _parse_bare_disk(raw: str | None) -> DiskTitleParts | None:
     """Диск без слова «Диск» в начале (API Форточек): только с размером и крепежом."""
-    return parse_disk_title(raw, bare=True)
+    return parse_disk_title(raw, bare=None)
```

### `parsers.strategies.title_params.x__parse_bare_disk__mutmut_3`

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/parsers/strategies/title_params.py
+++ src/parsers/strategies/title_params.py
@@ -1,3 +1,3 @@
 def _parse_bare_disk(raw: str | None) -> DiskTitleParts | None:
     """Диск без слова «Диск» в начале (API Форточек): только с размером и крепежом."""
-    return parse_disk_title(raw, bare=True)
+    return parse_disk_title(bare=True)
```

### `parsers.strategies.title_params.x__parse_bare_disk__mutmut_4`

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/parsers/strategies/title_params.py
+++ src/parsers/strategies/title_params.py
@@ -1,3 +1,3 @@
 def _parse_bare_disk(raw: str | None) -> DiskTitleParts | None:
     """Диск без слова «Диск» в начале (API Форточек): только с размером и крепежом."""
-    return parse_disk_title(raw, bare=True)
+    return parse_disk_title(raw, )
```

### `parsers.strategies.title_params.x__parse_bare_disk__mutmut_5`

Статус: **survived**; тип: `keyword`; выбрано тестов: 3.

```diff
--- src/parsers/strategies/title_params.py
+++ src/parsers/strategies/title_params.py
@@ -1,3 +1,3 @@
 def _parse_bare_disk(raw: str | None) -> DiskTitleParts | None:
     """Диск без слова «Диск» в начале (API Форточек): только с размером и крепежом."""
-    return parse_disk_title(raw, bare=True)
+    return parse_disk_title(raw, bare=False)
```

## src/parsers/strategies/title_registry.py

### `parsers.strategies.title_registry.x__brand_probe__mutmut_5`

Статус: **survived**; тип: `to_none`; выбрано тестов: 2.

```diff
--- src/parsers/strategies/title_registry.py
+++ src/parsers/strategies/title_registry.py
@@ -1,4 +1,4 @@
 def _brand_probe(config_provider: ConfigProvider) -> BrandProbe:
     """Детектор бренда в title по алиасам производителей (границы как у BaseFinder)."""
-    finder = BaseFinder(AliasContainer(aliases_for_finder(load_aliases_map(config_provider))))
+    finder = BaseFinder(AliasContainer(aliases_for_finder(load_aliases_map(None))))
     return lambda title: finder.find_word_in_title(title)[0] is not None
```

### `parsers.strategies.title_registry.x__brand_probe__mutmut_8`

Статус: **survived**; тип: `number`; выбрано тестов: 2.

```diff
--- src/parsers/strategies/title_registry.py
+++ src/parsers/strategies/title_registry.py
@@ -1,4 +1,4 @@
 def _brand_probe(config_provider: ConfigProvider) -> BrandProbe:
     """Детектор бренда в title по алиасам производителей (границы как у BaseFinder)."""
     finder = BaseFinder(AliasContainer(aliases_for_finder(load_aliases_map(config_provider))))
-    return lambda title: finder.find_word_in_title(title)[0] is not None
+    return lambda title: finder.find_word_in_title(title)[1] is not None
```

### `parsers.strategies.title_registry.x__fallback_probe__mutmut_3`

Статус: **survived**; тип: `to_none`; выбрано тестов: 6.

```diff
--- src/parsers/strategies/title_registry.py
+++ src/parsers/strategies/title_registry.py
@@ -1,3 +1,3 @@
 def _fallback_probe(config: TitleConfig, config_provider: ConfigProvider) -> BrandProbe | None:
     """Детектор бренда нужен только при заданном ``fallback_brand``."""
-    return _brand_probe(config_provider) if config.fallback_brand else None
+    return _brand_probe(None) if config.fallback_brand else None
```

### `parsers.strategies.title_registry.x_make_title_strategy__mutmut_1`

Статус: **survived**; тип: `keyword`; выбрано тестов: 39.

```diff
--- src/parsers/strategies/title_registry.py
+++ src/parsers/strategies/title_registry.py
@@ -5,7 +5,7 @@
     manufacturer_reader: ManufacturerReader | None = None,
     *,
     config_provider: ConfigProvider,
-    column_first: bool = False,
+    column_first: bool = True,
 ) -> TitleStrategy:
     """Собрать стратегию title по слоту конфига; при `aliases` — обернуть картой."""
     check_params_flags(config, where)
```

### `parsers.strategies.title_registry.x_make_title_strategy__mutmut_3`

Статус: **survived**; тип: `to_none`; выбрано тестов: 39.

```diff
--- src/parsers/strategies/title_registry.py
+++ src/parsers/strategies/title_registry.py
@@ -8,7 +8,7 @@
     column_first: bool = False,
 ) -> TitleStrategy:
     """Собрать стратегию title по слоту конфига; при `aliases` — обернуть картой."""
-    check_params_flags(config, where)
+    check_params_flags(config, None)
     strategy = _build_strategy(config, where, manufacturer_reader, config_provider)
     if config.aliases:
         strategy = TitleWithAliases(strategy, load_title_aliases(supplier_name, config_provider))
```

### `parsers.strategies.title_registry.x_make_title_strategy__mutmut_21`

Статус: **survived**; тип: `to_none`; выбрано тестов: 39.

```diff
--- src/parsers/strategies/title_registry.py
+++ src/parsers/strategies/title_registry.py
@@ -11,7 +11,7 @@
     check_params_flags(config, where)
     strategy = _build_strategy(config, where, manufacturer_reader, config_provider)
     if config.aliases:
-        strategy = TitleWithAliases(strategy, load_title_aliases(supplier_name, config_provider))
+        strategy = TitleWithAliases(strategy, load_title_aliases(supplier_name, None))
     strategy = wrap_with_params(strategy, config, config_provider, column_first)
     if config.markers:
         strategy = TitleWithMarkers(strategy, config.markers)
```

### `parsers.strategies.title_registry.x_make_title_strategy__mutmut_28`

Статус: **survived**; тип: `to_none`; выбрано тестов: 39.

```diff
--- src/parsers/strategies/title_registry.py
+++ src/parsers/strategies/title_registry.py
@@ -12,7 +12,7 @@
     strategy = _build_strategy(config, where, manufacturer_reader, config_provider)
     if config.aliases:
         strategy = TitleWithAliases(strategy, load_title_aliases(supplier_name, config_provider))
-    strategy = wrap_with_params(strategy, config, config_provider, column_first)
+    strategy = wrap_with_params(strategy, config, config_provider, None)
     if config.markers:
         strategy = TitleWithMarkers(strategy, config.markers)
     return strategy
```

### `parsers.strategies.title_registry.x_make_title_strategy__mutmut_32`

Статус: **survived**; тип: `other`; выбрано тестов: 39.

```diff
--- src/parsers/strategies/title_registry.py
+++ src/parsers/strategies/title_registry.py
@@ -12,7 +12,7 @@
     strategy = _build_strategy(config, where, manufacturer_reader, config_provider)
     if config.aliases:
         strategy = TitleWithAliases(strategy, load_title_aliases(supplier_name, config_provider))
-    strategy = wrap_with_params(strategy, config, config_provider, column_first)
+    strategy = wrap_with_params(strategy, config, config_provider, )
     if config.markers:
         strategy = TitleWithMarkers(strategy, config.markers)
     return strategy
```

## src/parsers/strategies/title_wrap.py

### `parsers.strategies.title_wrap.x_manufacturer_probe__mutmut_6`

Статус: **survived**; тип: `other`; выбрано тестов: 5.

```diff
--- src/parsers/strategies/title_wrap.py
+++ src/parsers/strategies/title_wrap.py
@@ -1,4 +1,4 @@
 def manufacturer_probe(config_provider: ConfigProvider) -> ManufacturerProbe:
     """Производитель в title по алиасам производителей: тот же поиск, что и у ``ManufacturerFinder``."""
     finder = BaseFinder(AliasContainer(aliases_for_finder(load_aliases_map(config_provider))))
-    return lambda title: finder.find_word_in_title(title)[0]
+    return lambda title: None
```

### `parsers.strategies.title_wrap.x_manufacturer_probe__mutmut_7`

Статус: **survived**; тип: `to_none`; выбрано тестов: 5.

```diff
--- src/parsers/strategies/title_wrap.py
+++ src/parsers/strategies/title_wrap.py
@@ -1,4 +1,4 @@
 def manufacturer_probe(config_provider: ConfigProvider) -> ManufacturerProbe:
     """Производитель в title по алиасам производителей: тот же поиск, что и у ``ManufacturerFinder``."""
     finder = BaseFinder(AliasContainer(aliases_for_finder(load_aliases_map(config_provider))))
-    return lambda title: finder.find_word_in_title(title)[0]
+    return lambda title: finder.find_word_in_title(None)[0]
```

### `parsers.strategies.title_wrap.x_manufacturer_probe__mutmut_8`

Статус: **survived**; тип: `number`; выбрано тестов: 5.

```diff
--- src/parsers/strategies/title_wrap.py
+++ src/parsers/strategies/title_wrap.py
@@ -1,4 +1,4 @@
 def manufacturer_probe(config_provider: ConfigProvider) -> ManufacturerProbe:
     """Производитель в title по алиасам производителей: тот же поиск, что и у ``ManufacturerFinder``."""
     finder = BaseFinder(AliasContainer(aliases_for_finder(load_aliases_map(config_provider))))
-    return lambda title: finder.find_word_in_title(title)[0]
+    return lambda title: finder.find_word_in_title(title)[1]
```

### `parsers.strategies.title_wrap.x_wrap_with_params__mutmut_7`

Статус: **survived**; тип: `other`; выбрано тестов: 32.

```diff
--- src/parsers/strategies/title_wrap.py
+++ src/parsers/strategies/title_wrap.py
@@ -9,4 +9,4 @@
     parsed = ParamsFromTitle(strategy)
     if not config.compose:
         return parsed
-    return TitleFromFields(parsed, manufacturer_probe(config_provider), column_first=column_first)
+    return TitleFromFields(parsed, None, column_first=column_first)
```

### `parsers.strategies.title_wrap.x_wrap_with_params__mutmut_8`

Статус: **survived**; тип: `to_none`; выбрано тестов: 32.

```diff
--- src/parsers/strategies/title_wrap.py
+++ src/parsers/strategies/title_wrap.py
@@ -9,4 +9,4 @@
     parsed = ParamsFromTitle(strategy)
     if not config.compose:
         return parsed
-    return TitleFromFields(parsed, manufacturer_probe(config_provider), column_first=column_first)
+    return TitleFromFields(parsed, manufacturer_probe(config_provider), column_first=None)
```

### `parsers.strategies.title_wrap.x_wrap_with_params__mutmut_10`

Статус: **survived**; тип: `other`; выбрано тестов: 32.

```diff
--- src/parsers/strategies/title_wrap.py
+++ src/parsers/strategies/title_wrap.py
@@ -9,4 +9,4 @@
     parsed = ParamsFromTitle(strategy)
     if not config.compose:
         return parsed
-    return TitleFromFields(parsed, manufacturer_probe(config_provider), column_first=column_first)
+    return TitleFromFields(parsed, column_first=column_first)
```

### `parsers.strategies.title_wrap.x_wrap_with_params__mutmut_11`

Статус: **survived**; тип: `other`; выбрано тестов: 32.

```diff
--- src/parsers/strategies/title_wrap.py
+++ src/parsers/strategies/title_wrap.py
@@ -9,4 +9,4 @@
     parsed = ParamsFromTitle(strategy)
     if not config.compose:
         return parsed
-    return TitleFromFields(parsed, manufacturer_probe(config_provider), column_first=column_first)
+    return TitleFromFields(parsed, manufacturer_probe(config_provider), )
```

## src/parsers/strategies/tube_title.py

### `parsers.strategies.tube_title.x__brand__mutmut_3`

Статус: **survived**; тип: `other`; выбрано тестов: 10.

```diff
--- src/parsers/strategies/tube_title.py
+++ src/parsers/strategies/tube_title.py
@@ -1,4 +1,4 @@
 def _brand(row_item: RowItem, title: str | None, manufacturer_probe: ManufacturerProbe | None) -> str:
     """Производитель из текста поставщика, иначе из поля позиции."""
-    found = manufacturer_probe(title) if manufacturer_probe else None
+    found = manufacturer_probe(title) if (manufacturer_probe) or True else None
     return found or brand_label(row_item)
```

### `parsers.strategies.tube_title.x_compose_tube_title_from_text__mutmut_6`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 23.

```diff
--- src/parsers/strategies/tube_title.py
+++ src/parsers/strategies/tube_title.py
@@ -16,7 +16,7 @@
     """
     parts = parse_tube_title(title)
     if parts is None:
-        if TUBE_PREFIX.match(title or ''):
+        if TUBE_PREFIX.match(title or 'XXXX'):
             row_item.set_field('title_not_composed', True)
         return None
     size = tube_size_label(parts.width, parts.height_percent, parts.diameter, parts.ext_diameter, parts.width_max)
```

### `parsers.strategies.tube_title.x_compose_tube_title_from_text__mutmut_16`

Статус: **survived**; тип: `other`; выбрано тестов: 23.

```diff
--- src/parsers/strategies/tube_title.py
+++ src/parsers/strategies/tube_title.py
@@ -19,7 +19,7 @@
         if TUBE_PREFIX.match(title or ''):
             row_item.set_field('title_not_composed', True)
         return None
-    size = tube_size_label(parts.width, parts.height_percent, parts.diameter, parts.ext_diameter, parts.width_max)
+    size = tube_size_label(parts.width, None, parts.diameter, parts.ext_diameter, parts.width_max)
     is_rim_tape = bool(_RIM_TAPE_WORD.search(title or ''))
     model = tube_model_from_title(title, is_rim_tape=is_rim_tape)
     brand = _brand(row_item, title, manufacturer_probe)
```

### `parsers.strategies.tube_title.x_compose_tube_title_from_text__mutmut_29`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 23.

```diff
--- src/parsers/strategies/tube_title.py
+++ src/parsers/strategies/tube_title.py
@@ -20,7 +20,7 @@
             row_item.set_field('title_not_composed', True)
         return None
     size = tube_size_label(parts.width, parts.height_percent, parts.diameter, parts.ext_diameter, parts.width_max)
-    is_rim_tape = bool(_RIM_TAPE_WORD.search(title or ''))
+    is_rim_tape = bool(_RIM_TAPE_WORD.search(title or 'XXXX'))
     model = tube_model_from_title(title, is_rim_tape=is_rim_tape)
     brand = _brand(row_item, title, manufacturer_probe)
     return compose_tube_title(is_rim_tape, size, brand, model, valve=has_valve(title))
```

### `parsers.strategies.tube_title.x_compose_tube_title_from_text__mutmut_46`

Статус: **survived**; тип: `other`; выбрано тестов: 23.

```diff
--- src/parsers/strategies/tube_title.py
+++ src/parsers/strategies/tube_title.py
@@ -23,4 +23,4 @@
     is_rim_tape = bool(_RIM_TAPE_WORD.search(title or ''))
     model = tube_model_from_title(title, is_rim_tape=is_rim_tape)
     brand = _brand(row_item, title, manufacturer_probe)
-    return compose_tube_title(is_rim_tape, size, brand, model, valve=has_valve(title))
+    return compose_tube_title(is_rim_tape, size, brand, model, valve=None)
```

### `parsers.strategies.tube_title.x_compose_tube_title_from_text__mutmut_51`

Статус: **survived**; тип: `other`; выбрано тестов: 23.

```diff
--- src/parsers/strategies/tube_title.py
+++ src/parsers/strategies/tube_title.py
@@ -23,4 +23,4 @@
     is_rim_tape = bool(_RIM_TAPE_WORD.search(title or ''))
     model = tube_model_from_title(title, is_rim_tape=is_rim_tape)
     brand = _brand(row_item, title, manufacturer_probe)
-    return compose_tube_title(is_rim_tape, size, brand, model, valve=has_valve(title))
+    return compose_tube_title(is_rim_tape, size, brand, model, )
```

### `parsers.strategies.tube_title.x_compose_tube_title_from_text__mutmut_52`

Статус: **survived**; тип: `to_none`; выбрано тестов: 23.

```diff
--- src/parsers/strategies/tube_title.py
+++ src/parsers/strategies/tube_title.py
@@ -23,4 +23,4 @@
     is_rim_tape = bool(_RIM_TAPE_WORD.search(title or ''))
     model = tube_model_from_title(title, is_rim_tape=is_rim_tape)
     brand = _brand(row_item, title, manufacturer_probe)
-    return compose_tube_title(is_rim_tape, size, brand, model, valve=has_valve(title))
+    return compose_tube_title(is_rim_tape, size, brand, model, valve=has_valve(None))
```

## src/parsers/supplier_file_rules.py

### `parsers.supplier_file_rules.x__free_price_name__mutmut_3`

Статус: **survived**; тип: `other`; выбрано тестов: 18.

```diff
--- src/parsers/supplier_file_rules.py
+++ src/parsers/supplier_file_rules.py
@@ -1,6 +1,6 @@
 def _free_price_name(source: Path, rules: SupplierFileRules, taken: set[str], folder: str) -> str:
     """Первое свободное имя price<N>.<ext>, которое прочитает разбор поставщика."""
-    candidates = _price_names(source.suffix.lower()) if is_excel(source.name) else ()
+    candidates = _price_names(source.suffix.lower()) if (is_excel(source.name)) or True else ()
     for name in candidates:
         if name not in taken and rules.accepts(name):
             return name
```

### `parsers.supplier_file_rules.x__kept_names__mutmut_5`

Статус: **survived**; тип: `to_none`; выбрано тестов: 24.

```diff
--- src/parsers/supplier_file_rules.py
+++ src/parsers/supplier_file_rules.py
@@ -3,6 +3,6 @@
     planned: list[PriceFile] = []
     for source in matching:
         if any(price_file.name == source.name for price_file in planned):
-            raise SupplierPriceFileNameError(_MSG_DUPLICATE.format(folder=folder, name=source.name))
+            raise SupplierPriceFileNameError(_MSG_DUPLICATE.format(folder=None, name=source.name))
         planned.append(PriceFile(source, source.name))
     return planned
```

### `parsers.supplier_file_rules.x__price_names__mutmut_7`

Статус: **survived**; тип: `operator`; выбрано тестов: 17.

```diff
--- src/parsers/supplier_file_rules.py
+++ src/parsers/supplier_file_rules.py
@@ -1,4 +1,4 @@
 def _price_names(extension: str) -> tuple[str, ...]:
     """price.<ext>, price_2.<ext>, …"""
-    numbered = (f'{_PRICE_STEM}_{number}{extension}' for number in range(2, _MAX_PRICE_NUMBER + 1))
+    numbered = (f'{_PRICE_STEM}_{number}{extension}' for number in range(2, _MAX_PRICE_NUMBER - 1))
     return (f'{_PRICE_STEM}{extension}', *numbered)
```

### `parsers.supplier_file_rules.x__price_names__mutmut_8`

Статус: **survived**; тип: `number`; выбрано тестов: 17.

```diff
--- src/parsers/supplier_file_rules.py
+++ src/parsers/supplier_file_rules.py
@@ -1,4 +1,4 @@
 def _price_names(extension: str) -> tuple[str, ...]:
     """price.<ext>, price_2.<ext>, …"""
-    numbered = (f'{_PRICE_STEM}_{number}{extension}' for number in range(2, _MAX_PRICE_NUMBER + 1))
+    numbered = (f'{_PRICE_STEM}_{number}{extension}' for number in range(2, _MAX_PRICE_NUMBER + 2))
     return (f'{_PRICE_STEM}{extension}', *numbered)
```

### `parsers.supplier_file_rules.x_plan_files__mutmut_2`

Статус: **survived**; тип: `to_none`; выбрано тестов: 24.

```diff
--- src/parsers/supplier_file_rules.py
+++ src/parsers/supplier_file_rules.py
@@ -1,6 +1,6 @@
 def plan_files(folder: str, rules: SupplierFileRules, sources: list[Path]) -> list[PriceFile]:
     """Назначить имена: подходящие под маски — как есть, остальные Excel — price, price_2, …"""
-    planned = _kept_names(folder, [path for path in sources if rules.accepts(path.name)])
+    planned = _kept_names(None, [path for path in sources if rules.accepts(path.name)])
     others = [path for path in sources if not rules.accepts(path.name)]
     for other in others:
         taken = {price_file.name for price_file in planned}
```

## src/parsers/supplier_price/sources.py

### `parsers.supplier_price.sources.x__check_extension__mutmut_4`

Статус: **survived**; тип: `to_none`; выбрано тестов: 27.

```diff
--- src/parsers/supplier_price/sources.py
+++ src/parsers/supplier_price/sources.py
@@ -1,3 +1,3 @@
 def _check_extension(path: Path) -> None:
     if path.suffix.lower() not in _ALLOWED_EXTENSIONS:
-        raise InvalidPriceExtensionError(_MSG_EXTENSION.format(path.suffix, path.name))
+        raise InvalidPriceExtensionError(_MSG_EXTENSION.format(None, path.name))
```

## src/parsers/vendor_config/activation.py

### `parsers.vendor_config.activation.x_load_activation__mutmut_7`

Статус: **survived**; тип: `other`; выбрано тестов: 75.

```diff
--- src/parsers/vendor_config/activation.py
+++ src/parsers/vendor_config/activation.py
@@ -3,5 +3,5 @@
     path = Path(activation_file(config_provider))
     if not path.is_file():
         return {}
-    raw = as_config_object(read_json_file(str(path)), path.name)
+    raw = as_config_object(read_json_file(str(path)), None)
     return {folder: read_zero_one_flag(raw, folder, path.name) for folder in raw}
```

### `parsers.vendor_config.activation.x_set_vendor_enabled__mutmut_11`

Статус: **survived**; тип: `to_none`; выбрано тестов: 5.

```diff
--- src/parsers/vendor_config/activation.py
+++ src/parsers/vendor_config/activation.py
@@ -3,5 +3,5 @@
     path = Path(activation_file(config_provider))
     statuses = {**load_activation(config_provider), folder: enabled}
     ordered = dict(sorted(statuses.items()))
-    text = json.dumps(ordered, ensure_ascii=False, indent=2)
+    text = json.dumps(ordered, ensure_ascii=None, indent=2)
     path.write_text(f'{text}\n', encoding='utf-8')
```

### `parsers.vendor_config.activation.x_set_vendor_enabled__mutmut_12`

Статус: **survived**; тип: `to_none`; выбрано тестов: 5.

```diff
--- src/parsers/vendor_config/activation.py
+++ src/parsers/vendor_config/activation.py
@@ -3,5 +3,5 @@
     path = Path(activation_file(config_provider))
     statuses = {**load_activation(config_provider), folder: enabled}
     ordered = dict(sorted(statuses.items()))
-    text = json.dumps(ordered, ensure_ascii=False, indent=2)
+    text = json.dumps(ordered, ensure_ascii=False, indent=None)
     path.write_text(f'{text}\n', encoding='utf-8')
```

### `parsers.vendor_config.activation.x_set_vendor_enabled__mutmut_14`

Статус: **survived**; тип: `other`; выбрано тестов: 5.

```diff
--- src/parsers/vendor_config/activation.py
+++ src/parsers/vendor_config/activation.py
@@ -3,5 +3,5 @@
     path = Path(activation_file(config_provider))
     statuses = {**load_activation(config_provider), folder: enabled}
     ordered = dict(sorted(statuses.items()))
-    text = json.dumps(ordered, ensure_ascii=False, indent=2)
+    text = json.dumps(ordered, indent=2)
     path.write_text(f'{text}\n', encoding='utf-8')
```

### `parsers.vendor_config.activation.x_set_vendor_enabled__mutmut_15`

Статус: **survived**; тип: `other`; выбрано тестов: 5.

```diff
--- src/parsers/vendor_config/activation.py
+++ src/parsers/vendor_config/activation.py
@@ -3,5 +3,5 @@
     path = Path(activation_file(config_provider))
     statuses = {**load_activation(config_provider), folder: enabled}
     ordered = dict(sorted(statuses.items()))
-    text = json.dumps(ordered, ensure_ascii=False, indent=2)
+    text = json.dumps(ordered, ensure_ascii=False, )
     path.write_text(f'{text}\n', encoding='utf-8')
```

### `parsers.vendor_config.activation.x_set_vendor_enabled__mutmut_16`

Статус: **survived**; тип: `keyword`; выбрано тестов: 5.

```diff
--- src/parsers/vendor_config/activation.py
+++ src/parsers/vendor_config/activation.py
@@ -3,5 +3,5 @@
     path = Path(activation_file(config_provider))
     statuses = {**load_activation(config_provider), folder: enabled}
     ordered = dict(sorted(statuses.items()))
-    text = json.dumps(ordered, ensure_ascii=False, indent=2)
+    text = json.dumps(ordered, ensure_ascii=True, indent=2)
     path.write_text(f'{text}\n', encoding='utf-8')
```

### `parsers.vendor_config.activation.x_set_vendor_enabled__mutmut_17`

Статус: **survived**; тип: `number`; выбрано тестов: 5.

```diff
--- src/parsers/vendor_config/activation.py
+++ src/parsers/vendor_config/activation.py
@@ -3,5 +3,5 @@
     path = Path(activation_file(config_provider))
     statuses = {**load_activation(config_provider), folder: enabled}
     ordered = dict(sorted(statuses.items()))
-    text = json.dumps(ordered, ensure_ascii=False, indent=2)
+    text = json.dumps(ordered, ensure_ascii=False, indent=3)
     path.write_text(f'{text}\n', encoding='utf-8')
```

## src/parsers/vendor_config/battery_settings.py

### `parsers.vendor_config.battery_settings.xǁBatterySettingsǁfrom_dict__mutmut_20`

Статус: **survived**; тип: `to_none`; выбрано тестов: 116.

```diff
--- src/parsers/vendor_config/battery_settings.py
+++ src/parsers/vendor_config/battery_settings.py
@@ -2,7 +2,7 @@
     def from_dict(cls, payload: RawConfig, where: str) -> BatterySettings:
         """Проверить каждый заданный слот до наследования и сохранить типизированные настройки."""
         title = _slot(payload, 'title', ('strategy', 'lines'), where)
-        pricing = _slot(payload, 'pricing', ('policy', 'rules'), where)
+        pricing = _slot(payload, 'pricing', ('policy', 'rules'), None)
         behavior = _slot(payload, 'behavior', ('min_rest', 'rest'), where)
         _require_choice(title, 'strategy', 'plant', f'{where} → title')
         _require_choice(pricing, 'policy', 'recommended', f'{where} → pricing')
```

### `parsers.vendor_config.battery_settings.xǁBatterySettingsǁfrom_dict__mutmut_97`

Статус: **survived**; тип: `other`; выбрано тестов: 116.

```diff
--- src/parsers/vendor_config/battery_settings.py
+++ src/parsers/vendor_config/battery_settings.py
@@ -10,5 +10,5 @@
         return cls(
             lines=_read_lines(title, f'{where} → title'),
             min_rest=_minimum_rest(behavior, f'{where} → behavior'),
-            rules=MarkupRulesConfig.from_dict(read_object(pricing, 'rules', where), f'{where} → pricing → rules'),
+            rules=MarkupRulesConfig.from_dict(read_object(pricing, 'rules', where), None),
         )
```

### `parsers.vendor_config.battery_settings.xǁBatterySettingsǁfrom_dict__mutmut_102`

Статус: **survived**; тип: `to_none`; выбрано тестов: 116.

```diff
--- src/parsers/vendor_config/battery_settings.py
+++ src/parsers/vendor_config/battery_settings.py
@@ -10,5 +10,5 @@
         return cls(
             lines=_read_lines(title, f'{where} → title'),
             min_rest=_minimum_rest(behavior, f'{where} → behavior'),
-            rules=MarkupRulesConfig.from_dict(read_object(pricing, 'rules', where), f'{where} → pricing → rules'),
+            rules=MarkupRulesConfig.from_dict(read_object(pricing, 'rules', None), f'{where} → pricing → rules'),
         )
```

### `parsers.vendor_config.battery_settings.x__minimum_rest__mutmut_4`

Статус: **survived**; тип: `to_none`; выбрано тестов: 103.

```diff
--- src/parsers/vendor_config/battery_settings.py
+++ src/parsers/vendor_config/battery_settings.py
@@ -1,5 +1,5 @@
 def _minimum_rest(payload: RawConfig, where: str) -> int:
-    minimum = read_int(payload, 'min_rest', where, 1)
+    minimum = read_int(payload, 'min_rest', None, 1)
     if minimum < 1:
         raise ConfigValidationError(f'{where} → min_rest: минимальный остаток должен быть не меньше 1')
     return minimum
```

### `parsers.vendor_config.battery_settings.x__read_lines__mutmut_4`

Статус: **survived**; тип: `to_none`; выбрано тестов: 106.

```diff
--- src/parsers/vendor_config/battery_settings.py
+++ src/parsers/vendor_config/battery_settings.py
@@ -1,5 +1,5 @@
 def _read_lines(payload: RawConfig, where: str) -> tuple[str, ...]:
-    configured = read_str_list(payload, 'lines', where, PLANT_LINES)
+    configured = read_str_list(payload, 'lines', None, PLANT_LINES)
     lines = tuple(' '.join(line.split()) for line in configured)
     normalized = {line.casefold() for line in lines}
     if not lines or '' in normalized or len(normalized) != len(lines):
```

### `parsers.vendor_config.battery_settings.x__require_choice__mutmut_3`

Статус: **survived**; тип: `to_none`; выбрано тестов: 114.

```diff
--- src/parsers/vendor_config/battery_settings.py
+++ src/parsers/vendor_config/battery_settings.py
@@ -1,3 +1,3 @@
 def _require_choice(payload: RawConfig, key: str, expected: str, where: str) -> None:
-    if read_text(payload, key, where, expected) != expected:
+    if read_text(payload, key, None, expected) != expected:
         raise ConfigValidationError(f'{where} → {key}: для batteries поддерживается только {expected}')
```

### `parsers.vendor_config.battery_settings.x__slot__mutmut_4`

Статус: **survived**; тип: `to_none`; выбрано тестов: 116.

```diff
--- src/parsers/vendor_config/battery_settings.py
+++ src/parsers/vendor_config/battery_settings.py
@@ -1,5 +1,5 @@
 def _slot(payload: RawConfig, key: str, allowed: tuple[str, ...], where: str) -> RawConfig:
-    parsed = read_object(payload, key, where)
+    parsed = read_object(payload, key, None)
     for setting in parsed:
         if setting not in allowed:
             raise ConfigValidationError(f'{where} → {key} → {setting}: настройка недоступна для batteries')
```

## src/parsers/vendor_config/columns.py

### `parsers.vendor_config.columns.x__same_named_columns__mutmut_3`

Статус: **survived**; тип: `to_none`; выбрано тестов: 4.

```diff
--- src/parsers/vendor_config/columns.py
+++ src/parsers/vendor_config/columns.py
@@ -1,3 +1,3 @@
 def _same_named_columns(payload: RawConfig, where: str) -> Columns:
     """Колонки json списком: ключ исходной записи равен имени поля позиции."""
-    return {name: name for name in read_str_list(payload, COLUMNS_KEY, where)}
+    return {name: name for name in read_str_list(payload, COLUMNS_KEY, None)}
```

### `parsers.vendor_config.columns.x_read_columns__mutmut_4`

Статус: **survived**; тип: `to_none`; выбрано тестов: 221.

```diff
--- src/parsers/vendor_config/columns.py
+++ src/parsers/vendor_config/columns.py
@@ -6,7 +6,7 @@
     Для json колонки можно задать списком: ключ записи совпадает с полем позиции (`["code", "title"]`).
     """
     if reads_json and isinstance(payload.get(COLUMNS_KEY), list):
-        parsed = _same_named_columns(payload, where)
+        parsed = _same_named_columns(payload, None)
     elif reads_json:
         parsed = _keyed_columns(payload, where)
     else:
```

## src/parsers/vendor_config/common.py

### `parsers.vendor_config.common.xǁCommonVendorSettingsǁfrom_dict__mutmut_3`

Статус: **survived**; тип: `to_none`; выбрано тестов: 94.

```diff
--- src/parsers/vendor_config/common.py
+++ src/parsers/vendor_config/common.py
@@ -1,7 +1,7 @@
     @classmethod
     def from_dict(cls, raw: Any, where: str) -> CommonVendorSettings:
         """Разобрать `_common.json`."""
-        payload = as_config_object(raw, where)
+        payload = as_config_object(raw, None)
         return cls(
             defaults=reading_defaults(payload, where),
             title_reference_order=read_str_list(payload, 'title_reference_order', where, ()),
```

### `parsers.vendor_config.common.xǁCommonVendorSettingsǁfrom_dict__mutmut_9`

Статус: **survived**; тип: `to_none`; выбрано тестов: 94.

```diff
--- src/parsers/vendor_config/common.py
+++ src/parsers/vendor_config/common.py
@@ -6,5 +6,5 @@
             defaults=reading_defaults(payload, where),
             title_reference_order=read_str_list(payload, 'title_reference_order', where, ()),
             group_defaults=read_group_defaults(payload, where),
-            where=where,
+            where=None,
         )
```

### `parsers.vendor_config.common.xǁCommonVendorSettingsǁfrom_dict__mutmut_13`

Статус: **survived**; тип: `other`; выбрано тестов: 94.

```diff
--- src/parsers/vendor_config/common.py
+++ src/parsers/vendor_config/common.py
@@ -6,5 +6,4 @@
             defaults=reading_defaults(payload, where),
             title_reference_order=read_str_list(payload, 'title_reference_order', where, ()),
             group_defaults=read_group_defaults(payload, where),
-            where=where,
-        )
+            )
```

### `parsers.vendor_config.common.xǁCommonVendorSettingsǁfrom_dict__mutmut_20`

Статус: **survived**; тип: `to_none`; выбрано тестов: 94.

```diff
--- src/parsers/vendor_config/common.py
+++ src/parsers/vendor_config/common.py
@@ -4,7 +4,7 @@
         payload = as_config_object(raw, where)
         return cls(
             defaults=reading_defaults(payload, where),
-            title_reference_order=read_str_list(payload, 'title_reference_order', where, ()),
+            title_reference_order=read_str_list(payload, 'title_reference_order', None, ()),
             group_defaults=read_group_defaults(payload, where),
             where=where,
         )
```

## src/parsers/vendor_config/group_defaults.py

### `parsers.vendor_config.group_defaults.x__read_defaults__mutmut_21`

Статус: **survived**; тип: `to_none`; выбрано тестов: 51.

```diff
--- src/parsers/vendor_config/group_defaults.py
+++ src/parsers/vendor_config/group_defaults.py
@@ -4,7 +4,7 @@
     identifier = read_group_id(group, where)
     _check_keys(group, ('id', 'defaults'), where)
     defaults_where = f'{where} → defaults'
-    defaults = read_object(group, 'defaults', where)
+    defaults = read_object(group, 'defaults', None)
     _check_keys(defaults, (*READING_KEYS, *MODEL_KEYS), defaults_where)
     validate_group_settings(defaults, defaults_where, identifier, reads_json=True)
     return GroupDefaults(identifier, defaults, where)
```

### `parsers.vendor_config.group_defaults.x__read_defaults__mutmut_35`

Статус: **survived**; тип: `to_none`; выбрано тестов: 51.

```diff
--- src/parsers/vendor_config/group_defaults.py
+++ src/parsers/vendor_config/group_defaults.py
@@ -6,5 +6,5 @@
     defaults_where = f'{where} → defaults'
     defaults = read_object(group, 'defaults', where)
     _check_keys(defaults, (*READING_KEYS, *MODEL_KEYS), defaults_where)
-    validate_group_settings(defaults, defaults_where, identifier, reads_json=True)
+    validate_group_settings(defaults, defaults_where, None, reads_json=True)
     return GroupDefaults(identifier, defaults, where)
```

## src/parsers/vendor_config/group_fields.py

### `parsers.vendor_config.group_fields.x_read_group_id__mutmut_11`

Статус: **survived**; тип: `to_none`; выбрано тестов: 267.

```diff
--- src/parsers/vendor_config/group_fields.py
+++ src/parsers/vendor_config/group_fields.py
@@ -4,5 +4,5 @@
     try:
         return ProductGroup(identifier)
     except ValueError as error:
-        allowed = ', '.join(ProductGroup)
+        allowed = None
         raise ConfigValidationError(f'{where}.id: неизвестная группа {identifier!r}; допустимы {allowed}') from error
```

### `parsers.vendor_config.group_fields.x_read_group_id__mutmut_13`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 267.

```diff
--- src/parsers/vendor_config/group_fields.py
+++ src/parsers/vendor_config/group_fields.py
@@ -4,5 +4,5 @@
     try:
         return ProductGroup(identifier)
     except ValueError as error:
-        allowed = ', '.join(ProductGroup)
+        allowed = 'XX, XX'.join(ProductGroup)
         raise ConfigValidationError(f'{where}.id: неизвестная группа {identifier!r}; допустимы {allowed}') from error
```

## src/parsers/vendor_config/group_loading.py

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_9`

Статус: **survived**; тип: `to_none`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -1,7 +1,7 @@
 def _read_battery_section(section: RawConfig, where: str, inherited: RawConfig, vendor: VendorConfig) -> BatterySection:
     """Прочитать маршрут и разрешённые наследованием аккумуляторные настройки."""
     payload = merge_config(inherited, section)
-    templates = read_str_list(payload, 'file_templates', where, ())
+    templates = read_str_list(payload, 'file_templates', None, ())
     if not templates:
         raise ConfigValidationError(f'{where} → file_templates: требуется непустой список')
     sheet_indexes = read_int_list(section, 'sheet_indexes', where)
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_10`

Статус: **survived**; тип: `to_none`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -1,7 +1,7 @@
 def _read_battery_section(section: RawConfig, where: str, inherited: RawConfig, vendor: VendorConfig) -> BatterySection:
     """Прочитать маршрут и разрешённые наследованием аккумуляторные настройки."""
     payload = merge_config(inherited, section)
-    templates = read_str_list(payload, 'file_templates', where, ())
+    templates = read_str_list(payload, 'file_templates', where, None)
     if not templates:
         raise ConfigValidationError(f'{where} → file_templates: требуется непустой список')
     sheet_indexes = read_int_list(section, 'sheet_indexes', where)
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_13`

Статус: **survived**; тип: `other`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -1,7 +1,7 @@
 def _read_battery_section(section: RawConfig, where: str, inherited: RawConfig, vendor: VendorConfig) -> BatterySection:
     """Прочитать маршрут и разрешённые наследованием аккумуляторные настройки."""
     payload = merge_config(inherited, section)
-    templates = read_str_list(payload, 'file_templates', where, ())
+    templates = read_str_list(payload, 'file_templates', ())
     if not templates:
         raise ConfigValidationError(f'{where} → file_templates: требуется непустой список')
     sheet_indexes = read_int_list(section, 'sheet_indexes', where)
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_14`

Статус: **survived**; тип: `other`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -1,7 +1,7 @@
 def _read_battery_section(section: RawConfig, where: str, inherited: RawConfig, vendor: VendorConfig) -> BatterySection:
     """Прочитать маршрут и разрешённые наследованием аккумуляторные настройки."""
     payload = merge_config(inherited, section)
-    templates = read_str_list(payload, 'file_templates', where, ())
+    templates = read_str_list(payload, 'file_templates', where, )
     if not templates:
         raise ConfigValidationError(f'{where} → file_templates: требуется непустой список')
     sheet_indexes = read_int_list(section, 'sheet_indexes', where)
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_21`

Статус: **survived**; тип: `other`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -4,7 +4,7 @@
     templates = read_str_list(payload, 'file_templates', where, ())
     if not templates:
         raise ConfigValidationError(f'{where} → file_templates: требуется непустой список')
-    sheet_indexes = read_int_list(section, 'sheet_indexes', where)
+    sheet_indexes = read_int_list(section, None, where)
     if vendor.reader == 'json' and sheet_indexes:
         raise ConfigValidationError(f'{where} → sheet_indexes: JSON не содержит листов')
     return BatterySection(
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_22`

Статус: **survived**; тип: `to_none`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -4,7 +4,7 @@
     templates = read_str_list(payload, 'file_templates', where, ())
     if not templates:
         raise ConfigValidationError(f'{where} → file_templates: требуется непустой список')
-    sheet_indexes = read_int_list(section, 'sheet_indexes', where)
+    sheet_indexes = read_int_list(section, 'sheet_indexes', None)
     if vendor.reader == 'json' and sheet_indexes:
         raise ConfigValidationError(f'{where} → sheet_indexes: JSON не содержит листов')
     return BatterySection(
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_26`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -4,7 +4,7 @@
     templates = read_str_list(payload, 'file_templates', where, ())
     if not templates:
         raise ConfigValidationError(f'{where} → file_templates: требуется непустой список')
-    sheet_indexes = read_int_list(section, 'sheet_indexes', where)
+    sheet_indexes = read_int_list(section, 'XXsheet_indexesXX', where)
     if vendor.reader == 'json' and sheet_indexes:
         raise ConfigValidationError(f'{where} → sheet_indexes: JSON не содержит листов')
     return BatterySection(
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_27`

Статус: **survived**; тип: `string_case`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -4,7 +4,7 @@
     templates = read_str_list(payload, 'file_templates', where, ())
     if not templates:
         raise ConfigValidationError(f'{where} → file_templates: требуется непустой список')
-    sheet_indexes = read_int_list(section, 'sheet_indexes', where)
+    sheet_indexes = read_int_list(section, 'SHEET_INDEXES', where)
     if vendor.reader == 'json' and sheet_indexes:
         raise ConfigValidationError(f'{where} → sheet_indexes: JSON не содержит листов')
     return BatterySection(
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_30`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -5,7 +5,7 @@
     if not templates:
         raise ConfigValidationError(f'{where} → file_templates: требуется непустой список')
     sheet_indexes = read_int_list(section, 'sheet_indexes', where)
-    if vendor.reader == 'json' and sheet_indexes:
+    if vendor.reader == 'XXjsonXX' and sheet_indexes:
         raise ConfigValidationError(f'{where} → sheet_indexes: JSON не содержит листов')
     return BatterySection(
         id=read_text(section, 'id', where),
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_31`

Статус: **survived**; тип: `string_case`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -5,7 +5,7 @@
     if not templates:
         raise ConfigValidationError(f'{where} → file_templates: требуется непустой список')
     sheet_indexes = read_int_list(section, 'sheet_indexes', where)
-    if vendor.reader == 'json' and sheet_indexes:
+    if vendor.reader == 'JSON' and sheet_indexes:
         raise ConfigValidationError(f'{where} → sheet_indexes: JSON не содержит листов')
     return BatterySection(
         id=read_text(section, 'id', where),
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_36`

Статус: **survived**; тип: `other`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -12,7 +12,7 @@
         name=read_text(section, 'name', where, vendor.name),
         start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
         file_templates=templates,
-        sheet_info=read_text(section, 'sheet_info', where, ''),
+        sheet_info=None,
         sheet_indexes=sheet_indexes,
         row_selector=RowSelector.from_section(section, where),
         section_selector=SectionSelector.from_payload(payload, where),
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_47`

Статус: **survived**; тип: `other`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -12,7 +12,6 @@
         name=read_text(section, 'name', where, vendor.name),
         start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
         file_templates=templates,
-        sheet_info=read_text(section, 'sheet_info', where, ''),
         sheet_indexes=sheet_indexes,
         row_selector=RowSelector.from_section(section, where),
         section_selector=SectionSelector.from_payload(payload, where),
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_48`

Статус: **survived**; тип: `other`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -13,7 +13,6 @@
         start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
         file_templates=templates,
         sheet_info=read_text(section, 'sheet_info', where, ''),
-        sheet_indexes=sheet_indexes,
         row_selector=RowSelector.from_section(section, where),
         section_selector=SectionSelector.from_payload(payload, where),
         config_path=where,
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_56`

Статус: **survived**; тип: `to_none`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -8,7 +8,7 @@
     if vendor.reader == 'json' and sheet_indexes:
         raise ConfigValidationError(f'{where} → sheet_indexes: JSON не содержит листов')
     return BatterySection(
-        id=read_text(section, 'id', where),
+        id=read_text(section, 'id', None),
         name=read_text(section, 'name', where, vendor.name),
         start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
         file_templates=templates,
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_63`

Статус: **survived**; тип: `other`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -9,7 +9,7 @@
         raise ConfigValidationError(f'{where} → sheet_indexes: JSON не содержит листов')
     return BatterySection(
         id=read_text(section, 'id', where),
-        name=read_text(section, 'name', where, vendor.name),
+        name=read_text(section, None, where, vendor.name),
         start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
         file_templates=templates,
         sheet_info=read_text(section, 'sheet_info', where, ''),
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_64`

Статус: **survived**; тип: `to_none`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -9,7 +9,7 @@
         raise ConfigValidationError(f'{where} → sheet_indexes: JSON не содержит листов')
     return BatterySection(
         id=read_text(section, 'id', where),
-        name=read_text(section, 'name', where, vendor.name),
+        name=read_text(section, 'name', None, vendor.name),
         start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
         file_templates=templates,
         sheet_info=read_text(section, 'sheet_info', where, ''),
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_70`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -9,7 +9,7 @@
         raise ConfigValidationError(f'{where} → sheet_indexes: JSON не содержит листов')
     return BatterySection(
         id=read_text(section, 'id', where),
-        name=read_text(section, 'name', where, vendor.name),
+        name=read_text(section, 'XXnameXX', where, vendor.name),
         start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
         file_templates=templates,
         sheet_info=read_text(section, 'sheet_info', where, ''),
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_71`

Статус: **survived**; тип: `string_case`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -9,7 +9,7 @@
         raise ConfigValidationError(f'{where} → sheet_indexes: JSON не содержит листов')
     return BatterySection(
         id=read_text(section, 'id', where),
-        name=read_text(section, 'name', where, vendor.name),
+        name=read_text(section, 'NAME', where, vendor.name),
         start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
         file_templates=templates,
         sheet_info=read_text(section, 'sheet_info', where, ''),
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_74`

Статус: **survived**; тип: `to_none`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -10,7 +10,7 @@
     return BatterySection(
         id=read_text(section, 'id', where),
         name=read_text(section, 'name', where, vendor.name),
-        start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
+        start_row=read_int(payload, 'start_row', None, DEFAULT_START_ROW),
         file_templates=templates,
         sheet_info=read_text(section, 'sheet_info', where, ''),
         sheet_indexes=sheet_indexes,
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_83`

Статус: **survived**; тип: `other`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -12,7 +12,7 @@
         name=read_text(section, 'name', where, vendor.name),
         start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
         file_templates=templates,
-        sheet_info=read_text(section, 'sheet_info', where, ''),
+        sheet_info=read_text(section, None, where, ''),
         sheet_indexes=sheet_indexes,
         row_selector=RowSelector.from_section(section, where),
         section_selector=SectionSelector.from_payload(payload, where),
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_84`

Статус: **survived**; тип: `to_none`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -12,7 +12,7 @@
         name=read_text(section, 'name', where, vendor.name),
         start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
         file_templates=templates,
-        sheet_info=read_text(section, 'sheet_info', where, ''),
+        sheet_info=read_text(section, 'sheet_info', None, ''),
         sheet_indexes=sheet_indexes,
         row_selector=RowSelector.from_section(section, where),
         section_selector=SectionSelector.from_payload(payload, where),
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_90`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -12,7 +12,7 @@
         name=read_text(section, 'name', where, vendor.name),
         start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
         file_templates=templates,
-        sheet_info=read_text(section, 'sheet_info', where, ''),
+        sheet_info=read_text(section, 'XXsheet_infoXX', where, ''),
         sheet_indexes=sheet_indexes,
         row_selector=RowSelector.from_section(section, where),
         section_selector=SectionSelector.from_payload(payload, where),
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_91`

Статус: **survived**; тип: `string_case`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -12,7 +12,7 @@
         name=read_text(section, 'name', where, vendor.name),
         start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
         file_templates=templates,
-        sheet_info=read_text(section, 'sheet_info', where, ''),
+        sheet_info=read_text(section, 'SHEET_INFO', where, ''),
         sheet_indexes=sheet_indexes,
         row_selector=RowSelector.from_section(section, where),
         section_selector=SectionSelector.from_payload(payload, where),
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_92`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -12,7 +12,7 @@
         name=read_text(section, 'name', where, vendor.name),
         start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
         file_templates=templates,
-        sheet_info=read_text(section, 'sheet_info', where, ''),
+        sheet_info=read_text(section, 'sheet_info', where, 'XXXX'),
         sheet_indexes=sheet_indexes,
         row_selector=RowSelector.from_section(section, where),
         section_selector=SectionSelector.from_payload(payload, where),
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_94`

Статус: **survived**; тип: `to_none`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -14,7 +14,7 @@
         file_templates=templates,
         sheet_info=read_text(section, 'sheet_info', where, ''),
         sheet_indexes=sheet_indexes,
-        row_selector=RowSelector.from_section(section, where),
+        row_selector=RowSelector.from_section(section, None),
         section_selector=SectionSelector.from_payload(payload, where),
         config_path=where,
         columns=read_columns(payload, where, reads_json=vendor.reader == 'json', group=ProductGroup.BATTERIES),
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_98`

Статус: **survived**; тип: `to_none`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -15,7 +15,7 @@
         sheet_info=read_text(section, 'sheet_info', where, ''),
         sheet_indexes=sheet_indexes,
         row_selector=RowSelector.from_section(section, where),
-        section_selector=SectionSelector.from_payload(payload, where),
+        section_selector=SectionSelector.from_payload(payload, None),
         config_path=where,
         columns=read_columns(payload, where, reads_json=vendor.reader == 'json', group=ProductGroup.BATTERIES),
         processing=BatterySettings.from_dict(payload, where),
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_102`

Статус: **survived**; тип: `to_none`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -17,6 +17,6 @@
         row_selector=RowSelector.from_section(section, where),
         section_selector=SectionSelector.from_payload(payload, where),
         config_path=where,
-        columns=read_columns(payload, where, reads_json=vendor.reader == 'json', group=ProductGroup.BATTERIES),
+        columns=read_columns(payload, None, reads_json=vendor.reader == 'json', group=ProductGroup.BATTERIES),
         processing=BatterySettings.from_dict(payload, where),
     )
```

### `parsers.vendor_config.group_loading.x__read_battery_section__mutmut_113`

Статус: **survived**; тип: `to_none`; выбрано тестов: 60.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -18,5 +18,5 @@
         section_selector=SectionSelector.from_payload(payload, where),
         config_path=where,
         columns=read_columns(payload, where, reads_json=vendor.reader == 'json', group=ProductGroup.BATTERIES),
-        processing=BatterySettings.from_dict(payload, where),
+        processing=BatterySettings.from_dict(payload, None),
     )
```

### `parsers.vendor_config.group_loading.x_read_group__mutmut_5`

Статус: **survived**; тип: `other`; выбрано тестов: 149.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -2,7 +2,7 @@
     """Секции получают принадлежность по вложенности, а не по имени листа."""
     parsed_tires: list[VendorSection] = []
     parsed_batteries: list[BatterySection] = []
-    for index, section in enumerate(object_list(declaration.settings['sections'], declaration.where)):
+    for index, section in enumerate(object_list(declaration.settings['sections'], None)):
         where = f'{declaration.where} → sections[{index}]'
         read_text(section, 'id', f'{where}.id')
         if 'product_group' in section:
```

### `parsers.vendor_config.group_loading.x_read_group__mutmut_25`

Статус: **survived**; тип: `other`; выбрано тестов: 149.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -7,7 +7,7 @@
         read_text(section, 'id', f'{where}.id')
         if 'product_group' in section:
             raise ConfigValidationError(f'{where} → product_group: группа определяется вложенностью')
-        validate_group_settings(section, where, declaration.id, reads_json=vendor.reader == 'json', section_level=True)
+        validate_group_settings(section, where, None, reads_json=vendor.reader == 'json', section_level=True)
         if declaration.id is ProductGroup.TIRE_AND_DISK:
             parsed_tires.append(VendorSection.from_dict(section, where, vendor, declaration.settings))
         else:
```

### `parsers.vendor_config.group_loading.x_read_group__mutmut_65`

Статус: **survived**; тип: `other`; выбрано тестов: 149.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -16,5 +16,5 @@
         return BatteryConfig(tuple(parsed_batteries))
     return TireAndDiskConfig(
         tuple(parsed_tires),
-        BehaviorConfig.from_dict(read_object(declaration.settings, 'behavior', declaration.where), declaration.where),
+        BehaviorConfig.from_dict(read_object(declaration.settings, 'behavior', declaration.where), None),
     )
```

### `parsers.vendor_config.group_loading.x_read_group__mutmut_70`

Статус: **survived**; тип: `other`; выбрано тестов: 149.

```diff
--- src/parsers/vendor_config/group_loading.py
+++ src/parsers/vendor_config/group_loading.py
@@ -16,5 +16,5 @@
         return BatteryConfig(tuple(parsed_batteries))
     return TireAndDiskConfig(
         tuple(parsed_tires),
-        BehaviorConfig.from_dict(read_object(declaration.settings, 'behavior', declaration.where), declaration.where),
+        BehaviorConfig.from_dict(read_object(declaration.settings, 'behavior', None), declaration.where),
     )
```

## src/parsers/vendor_config/group_schema.py

### `parsers.vendor_config.group_schema.x__inherit_group__mutmut_5`

Статус: **survived**; тип: `other`; выбрано тестов: 236.

```diff
--- src/parsers/vendor_config/group_schema.py
+++ src/parsers/vendor_config/group_schema.py
@@ -10,7 +10,7 @@
     inherited = common_defaults
     for defaults in common.group_defaults:
         if defaults.id is group.id:
-            validate_group_settings(defaults.defaults, f'{defaults.where} → defaults', group.id, reads_json=reads_json)
+            validate_group_settings(defaults.defaults, f'{defaults.where} → defaults', None, reads_json=reads_json)
             inherited = merge_config(inherited, defaults.defaults)
     inherited = merge_config(inherited, vendor_defaults)
     validate_group_settings(group.settings, group.where, group.id, reads_json=reads_json)
```

### `parsers.vendor_config.group_schema.x_read_group_payloads__mutmut_13`

Статус: **survived**; тип: `other`; выбрано тестов: 264.

```diff
--- src/parsers/vendor_config/group_schema.py
+++ src/parsers/vendor_config/group_schema.py
@@ -6,7 +6,7 @@
         if key in payload:
             raise ConfigValidationError(f'{where} → {key}: нельзя сочетать старые настройки с product_groups')
     groups = object_list(payload.get('product_groups'), f'{where} → product_groups')
-    common_defaults = reading_defaults({'defaults': common.defaults}, common.where)
+    common_defaults = reading_defaults({'defaults': common.defaults}, None)
     defaults = reading_defaults(payload, where)
     parsed = _parse_groups(groups, where)
     return tuple(_inherit_group(group, common_defaults, defaults, common, reads_json=reads_json) for group in parsed)
```

## src/parsers/vendor_config/group_validation.py

### `parsers.vendor_config.group_validation.x__validate_tire_settings__mutmut_17`

Статус: **survived**; тип: `to_none`; выбрано тестов: 205.

```diff
--- src/parsers/vendor_config/group_validation.py
+++ src/parsers/vendor_config/group_validation.py
@@ -2,7 +2,7 @@
     """Проверить слоты и колонки шинной модели отдельно от соседних групп."""
     validate_strategy_names(payload, where)
     read_columns(payload, where, reads_json=reads_json)
-    CategoryConfig.from_dict(read_object(payload, 'category', where), f'{where} → category')
+    CategoryConfig.from_dict(read_object(payload, 'category', None), f'{where} → category')
     TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title')
     PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing')
     BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior')
```

### `parsers.vendor_config.group_validation.x__validate_tire_settings__mutmut_29`

Статус: **survived**; тип: `to_none`; выбрано тестов: 205.

```diff
--- src/parsers/vendor_config/group_validation.py
+++ src/parsers/vendor_config/group_validation.py
@@ -3,6 +3,6 @@
     validate_strategy_names(payload, where)
     read_columns(payload, where, reads_json=reads_json)
     CategoryConfig.from_dict(read_object(payload, 'category', where), f'{where} → category')
-    TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title')
+    TitleConfig.from_dict(read_object(payload, 'title', None), f'{where} → title')
     PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing')
     BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior')
```

### `parsers.vendor_config.group_validation.x__validate_tire_settings__mutmut_41`

Статус: **survived**; тип: `to_none`; выбрано тестов: 205.

```diff
--- src/parsers/vendor_config/group_validation.py
+++ src/parsers/vendor_config/group_validation.py
@@ -4,5 +4,5 @@
     read_columns(payload, where, reads_json=reads_json)
     CategoryConfig.from_dict(read_object(payload, 'category', where), f'{where} → category')
     TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title')
-    PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing')
+    PricingConfig.from_dict(read_object(payload, 'pricing', None), f'{where} → pricing')
     BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior')
```

### `parsers.vendor_config.group_validation.x__validate_tire_settings__mutmut_53`

Статус: **survived**; тип: `to_none`; выбрано тестов: 205.

```diff
--- src/parsers/vendor_config/group_validation.py
+++ src/parsers/vendor_config/group_validation.py
@@ -5,4 +5,4 @@
     CategoryConfig.from_dict(read_object(payload, 'category', where), f'{where} → category')
     TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title')
     PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing')
-    BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior')
+    BehaviorConfig.from_dict(read_object(payload, 'behavior', None), f'{where} → behavior')
```

### `parsers.vendor_config.group_validation.x_validate_group_settings__mutmut_7`

Статус: **survived**; тип: `to_none`; выбрано тестов: 248.

```diff
--- src/parsers/vendor_config/group_validation.py
+++ src/parsers/vendor_config/group_validation.py
@@ -3,7 +3,7 @@
 ) -> None:
     """Проверить исходный уровень, даже если следующий уровень его полностью заменит."""
     validate_reading_settings(payload, where)
-    _validate_row_selector(payload, where, section_level)
+    _validate_row_selector(payload, None, section_level)
     SectionSelector.from_payload(payload, where)
     if group is ProductGroup.BATTERIES:
         validate_battery_settings(payload, where, reads_json=reads_json)
```

### `parsers.vendor_config.group_validation.x_validate_group_settings__mutmut_13`

Статус: **survived**; тип: `to_none`; выбрано тестов: 248.

```diff
--- src/parsers/vendor_config/group_validation.py
+++ src/parsers/vendor_config/group_validation.py
@@ -4,7 +4,7 @@
     """Проверить исходный уровень, даже если следующий уровень его полностью заменит."""
     validate_reading_settings(payload, where)
     _validate_row_selector(payload, where, section_level)
-    SectionSelector.from_payload(payload, where)
+    SectionSelector.from_payload(payload, None)
     if group is ProductGroup.BATTERIES:
         validate_battery_settings(payload, where, reads_json=reads_json)
         return
```

### `parsers.vendor_config.group_validation.x_validate_reading_settings__mutmut_11`

Статус: **survived**; тип: `number`; выбрано тестов: 273.

```diff
--- src/parsers/vendor_config/group_validation.py
+++ src/parsers/vendor_config/group_validation.py
@@ -1,4 +1,4 @@
 def validate_reading_settings(payload: RawConfig, where: str) -> None:
     """Отсутствие значения допустимо, неверный заданный тип — нет."""
-    read_int(payload, 'start_row', where, 1)
+    read_int(payload, 'start_row', where, 2)
     read_str_list(payload, 'file_templates', where, ())
```

## src/parsers/vendor_config/models.py

### `parsers.vendor_config.models.x__read_grouped_vendor__mutmut_37`

Статус: **survived**; тип: `to_none`; выбрано тестов: 267.

```diff
--- src/parsers/vendor_config/models.py
+++ src/parsers/vendor_config/models.py
@@ -6,7 +6,7 @@
     declarations = read_group_payloads(payload, where, common, reads_json=reader == READER_JSON)
     vendor = VendorConfig(
         folder=folder,
-        code=read_text(payload, 'code', where),
+        code=read_text(payload, 'code', None),
         name=read_text(payload, 'name', where),
         reader=reader,
         source=read_text(payload, 'source', where, SOURCE_FILE),
```

### `parsers.vendor_config.models.x__read_grouped_vendor__mutmut_53`

Статус: **survived**; тип: `to_none`; выбрано тестов: 267.

```diff
--- src/parsers/vendor_config/models.py
+++ src/parsers/vendor_config/models.py
@@ -9,6 +9,6 @@
         code=read_text(payload, 'code', where),
         name=read_text(payload, 'name', where),
         reader=reader,
-        source=read_text(payload, 'source', where, SOURCE_FILE),
+        source=read_text(payload, 'source', None, SOURCE_FILE),
     )
     return replace(vendor, product_groups=tuple(read_group(declaration, vendor) for declaration in declarations))
```

## src/parsers/vendor_config/provider.py

### `parsers.vendor_config.provider.x__read_vendor__mutmut_3`

Статус: **survived**; тип: `other`; выбрано тестов: 51.

```diff
--- src/parsers/vendor_config/provider.py
+++ src/parsers/vendor_config/provider.py
@@ -1,6 +1,6 @@
 def _read_vendor(path: Path, common: CommonVendorSettings) -> VendorConfig:
     """Конфиг одного поставщика поверх общих настроек; `enabled` в нём запрещён — статус в vendor_activation.json."""
-    selected = select_source(read_json_file(str(path)), path.name)
+    selected = select_source(read_json_file(str(path)), None)
     if _ENABLED_KEY in selected or _ENABLED_KEY in common.defaults:
         raise ConfigValidationError(f'{path.name}: «enabled» перенесён в vendor_activation.json, уберите поле')
     return VendorConfig.from_dict(selected, path.stem, path.name, common=common)
```

## src/parsers/vendor_config/row_selector.py

### `parsers.vendor_config.row_selector.xǁRowSelectorǁfrom_dict__mutmut_3`

Статус: **survived**; тип: `to_none`; выбрано тестов: 6.

```diff
--- src/parsers/vendor_config/row_selector.py
+++ src/parsers/vendor_config/row_selector.py
@@ -1,6 +1,6 @@
     @classmethod
     def from_dict(cls, raw: Any, where: str) -> RowSelector:
-        payload = as_config_object(raw, where)
+        payload = as_config_object(raw, None)
         accepted = read_str_list(payload, 'values', where)
         if not accepted:
             raise ConfigValidationError(f'{where} → values: требуется непустой список уникальных строк')
```

### `parsers.vendor_config.row_selector.xǁRowSelectorǁfrom_dict__mutmut_25`

Статус: **survived**; тип: `to_none`; выбрано тестов: 6.

```diff
--- src/parsers/vendor_config/row_selector.py
+++ src/parsers/vendor_config/row_selector.py
@@ -6,4 +6,4 @@
             raise ConfigValidationError(f'{where} → values: требуется непустой список уникальных строк')
         if len(set(accepted)) != len(accepted):
             raise ConfigValidationError(f'{where} → values: значения должны быть уникальны')
-        return cls(column=read_text(payload, 'column', where), accepted_values=accepted)
+        return cls(column=read_text(payload, 'column', None), accepted_values=accepted)
```

### `parsers.vendor_config.row_selector.xǁRowSelectorǁfrom_section__mutmut_5`

Статус: **survived**; тип: `other`; выбрано тестов: 103.

```diff
--- src/parsers/vendor_config/row_selector.py
+++ src/parsers/vendor_config/row_selector.py
@@ -2,4 +2,4 @@
     def from_section(cls, section: RawConfig, where: str) -> RowSelector | None:
         if 'row_selector' not in section:
             return None
-        return cls.from_dict(section.get('row_selector'), f'{where} → row_selector')
+        return cls.from_dict(section.get('row_selector'), None)
```

## src/parsers/vendor_config/section_models.py

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_3`

Статус: **survived**; тип: `to_none`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -1,7 +1,7 @@
     @classmethod
     def from_dict(cls, raw: Any, where: str, vendor: VendorConfig, inherited: RawConfig) -> VendorSection:
         """Разобрать секцию поверх настроек поставщика `inherited`: объекты сливаются, значения заменяются."""
-        section = as_config_object(raw, where)
+        section = as_config_object(raw, None)
         payload = merge_config(inherited, section)
         file_templates = read_str_list(payload, 'file_templates', where, ())
         if not file_templates:
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_14`

Статус: **survived**; тип: `to_none`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -3,7 +3,7 @@
         """Разобрать секцию поверх настроек поставщика `inherited`: объекты сливаются, значения заменяются."""
         section = as_config_object(raw, where)
         payload = merge_config(inherited, section)
-        file_templates = read_str_list(payload, 'file_templates', where, ())
+        file_templates = read_str_list(payload, 'file_templates', None, ())
         if not file_templates:
             raise ConfigValidationError(f'{where}: {_MSG_TEMPLATES}')
         columns = read_columns(payload, where, reads_json=vendor.reader == READER_JSON)
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_15`

Статус: **survived**; тип: `to_none`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -3,7 +3,7 @@
         """Разобрать секцию поверх настроек поставщика `inherited`: объекты сливаются, значения заменяются."""
         section = as_config_object(raw, where)
         payload = merge_config(inherited, section)
-        file_templates = read_str_list(payload, 'file_templates', where, ())
+        file_templates = read_str_list(payload, 'file_templates', where, None)
         if not file_templates:
             raise ConfigValidationError(f'{where}: {_MSG_TEMPLATES}')
         columns = read_columns(payload, where, reads_json=vendor.reader == READER_JSON)
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_18`

Статус: **survived**; тип: `other`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -3,7 +3,7 @@
         """Разобрать секцию поверх настроек поставщика `inherited`: объекты сливаются, значения заменяются."""
         section = as_config_object(raw, where)
         payload = merge_config(inherited, section)
-        file_templates = read_str_list(payload, 'file_templates', where, ())
+        file_templates = read_str_list(payload, 'file_templates', ())
         if not file_templates:
             raise ConfigValidationError(f'{where}: {_MSG_TEMPLATES}')
         columns = read_columns(payload, where, reads_json=vendor.reader == READER_JSON)
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_19`

Статус: **survived**; тип: `other`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -3,7 +3,7 @@
         """Разобрать секцию поверх настроек поставщика `inherited`: объекты сливаются, значения заменяются."""
         section = as_config_object(raw, where)
         payload = merge_config(inherited, section)
-        file_templates = read_str_list(payload, 'file_templates', where, ())
+        file_templates = read_str_list(payload, 'file_templates', where, )
         if not file_templates:
             raise ConfigValidationError(f'{where}: {_MSG_TEMPLATES}')
         columns = read_columns(payload, where, reads_json=vendor.reader == READER_JSON)
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_26`

Статус: **survived**; тип: `to_none`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -6,7 +6,7 @@
         file_templates = read_str_list(payload, 'file_templates', where, ())
         if not file_templates:
             raise ConfigValidationError(f'{where}: {_MSG_TEMPLATES}')
-        columns = read_columns(payload, where, reads_json=vendor.reader == READER_JSON)
+        columns = read_columns(payload, None, reads_json=vendor.reader == READER_JSON)
         if not columns:
             raise ConfigValidationError(f'{where}: {_MSG_COLUMNS}')
         sheet_indexes = read_int_list(payload, 'sheet_indexes', where)
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_58`

Статус: **survived**; тип: `other`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -25,6 +25,6 @@
             pricing=PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing'),
             behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior'),
             row_selector=RowSelector.from_section(section, where),
-            section_selector=SectionSelector.from_payload(payload, where),
+            section_selector=None,
             config_path=where,
         )
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_59`

Статус: **survived**; тип: `to_none`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -26,5 +26,5 @@
             behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior'),
             row_selector=RowSelector.from_section(section, where),
             section_selector=SectionSelector.from_payload(payload, where),
-            config_path=where,
+            config_path=None,
         )
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_72`

Статус: **survived**; тип: `other`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -25,6 +25,5 @@
             pricing=PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing'),
             behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior'),
             row_selector=RowSelector.from_section(section, where),
-            section_selector=SectionSelector.from_payload(payload, where),
             config_path=where,
         )
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_73`

Статус: **survived**; тип: `other`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -26,5 +26,4 @@
             behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior'),
             row_selector=RowSelector.from_section(section, where),
             section_selector=SectionSelector.from_payload(payload, where),
-            config_path=where,
-        )
+            )
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_76`

Статус: **survived**; тип: `other`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -13,7 +13,7 @@
         if vendor.reader == READER_JSON and sheet_indexes:
             raise ConfigValidationError(f'{where} → sheet_indexes: JSON не содержит листов')
         return cls(
-            id=read_text(section, 'id', f'{where}.id'),
+            id=read_text(section, 'id', None),
             name=read_text(payload, 'name', where, vendor.name),
             start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
             file_templates=file_templates,
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_94`

Статус: **survived**; тип: `to_none`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -15,7 +15,7 @@
         return cls(
             id=read_text(section, 'id', f'{where}.id'),
             name=read_text(payload, 'name', where, vendor.name),
-            start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
+            start_row=read_int(payload, 'start_row', None, DEFAULT_START_ROW),
             file_templates=file_templates,
             columns=columns,
             sheet_info=read_text(payload, 'sheet_info', where, ''),
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_114`

Статус: **survived**; тип: `other`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -20,7 +20,7 @@
             columns=columns,
             sheet_info=read_text(payload, 'sheet_info', where, ''),
             sheet_indexes=sheet_indexes,
-            category=CategoryConfig.from_dict(read_object(payload, 'category', where), f'{where} → category'),
+            category=CategoryConfig.from_dict(read_object(payload, 'category', where), None),
             title=TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title'),
             pricing=PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing'),
             behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior'),
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_119`

Статус: **survived**; тип: `to_none`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -20,7 +20,7 @@
             columns=columns,
             sheet_info=read_text(payload, 'sheet_info', where, ''),
             sheet_indexes=sheet_indexes,
-            category=CategoryConfig.from_dict(read_object(payload, 'category', where), f'{where} → category'),
+            category=CategoryConfig.from_dict(read_object(payload, 'category', None), f'{where} → category'),
             title=TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title'),
             pricing=PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing'),
             behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior'),
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_126`

Статус: **survived**; тип: `other`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -21,7 +21,7 @@
             sheet_info=read_text(payload, 'sheet_info', where, ''),
             sheet_indexes=sheet_indexes,
             category=CategoryConfig.from_dict(read_object(payload, 'category', where), f'{where} → category'),
-            title=TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title'),
+            title=TitleConfig.from_dict(read_object(payload, 'title', where), None),
             pricing=PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing'),
             behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior'),
             row_selector=RowSelector.from_section(section, where),
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_131`

Статус: **survived**; тип: `to_none`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -21,7 +21,7 @@
             sheet_info=read_text(payload, 'sheet_info', where, ''),
             sheet_indexes=sheet_indexes,
             category=CategoryConfig.from_dict(read_object(payload, 'category', where), f'{where} → category'),
-            title=TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title'),
+            title=TitleConfig.from_dict(read_object(payload, 'title', None), f'{where} → title'),
             pricing=PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing'),
             behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior'),
             row_selector=RowSelector.from_section(section, where),
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_138`

Статус: **survived**; тип: `other`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -22,7 +22,7 @@
             sheet_indexes=sheet_indexes,
             category=CategoryConfig.from_dict(read_object(payload, 'category', where), f'{where} → category'),
             title=TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title'),
-            pricing=PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing'),
+            pricing=PricingConfig.from_dict(read_object(payload, 'pricing', where), None),
             behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior'),
             row_selector=RowSelector.from_section(section, where),
             section_selector=SectionSelector.from_payload(payload, where),
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_143`

Статус: **survived**; тип: `to_none`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -22,7 +22,7 @@
             sheet_indexes=sheet_indexes,
             category=CategoryConfig.from_dict(read_object(payload, 'category', where), f'{where} → category'),
             title=TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title'),
-            pricing=PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing'),
+            pricing=PricingConfig.from_dict(read_object(payload, 'pricing', None), f'{where} → pricing'),
             behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior'),
             row_selector=RowSelector.from_section(section, where),
             section_selector=SectionSelector.from_payload(payload, where),
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_150`

Статус: **survived**; тип: `other`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -23,7 +23,7 @@
             category=CategoryConfig.from_dict(read_object(payload, 'category', where), f'{where} → category'),
             title=TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title'),
             pricing=PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing'),
-            behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior'),
+            behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), None),
             row_selector=RowSelector.from_section(section, where),
             section_selector=SectionSelector.from_payload(payload, where),
             config_path=where,
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_155`

Статус: **survived**; тип: `to_none`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -23,7 +23,7 @@
             category=CategoryConfig.from_dict(read_object(payload, 'category', where), f'{where} → category'),
             title=TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title'),
             pricing=PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing'),
-            behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior'),
+            behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', None), f'{where} → behavior'),
             row_selector=RowSelector.from_section(section, where),
             section_selector=SectionSelector.from_payload(payload, where),
             config_path=where,
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_162`

Статус: **survived**; тип: `to_none`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -24,7 +24,7 @@
             title=TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title'),
             pricing=PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing'),
             behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior'),
-            row_selector=RowSelector.from_section(section, where),
+            row_selector=RowSelector.from_section(section, None),
             section_selector=SectionSelector.from_payload(payload, where),
             config_path=where,
         )
```

### `parsers.vendor_config.section_models.xǁVendorSectionǁfrom_dict__mutmut_166`

Статус: **survived**; тип: `to_none`; выбрано тестов: 93.

```diff
--- src/parsers/vendor_config/section_models.py
+++ src/parsers/vendor_config/section_models.py
@@ -25,6 +25,6 @@
             pricing=PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing'),
             behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior'),
             row_selector=RowSelector.from_section(section, where),
-            section_selector=SectionSelector.from_payload(payload, where),
+            section_selector=SectionSelector.from_payload(payload, None),
             config_path=where,
         )
```

## src/parsers/vendor_config/slot_configs.py

### `parsers.vendor_config.slot_configs.xǁBehaviorConfigǁfrom_dict__mutmut_40`

Статус: **survived**; тип: `to_none`; выбрано тестов: 149.

```diff
--- src/parsers/vendor_config/slot_configs.py
+++ src/parsers/vendor_config/slot_configs.py
@@ -4,7 +4,7 @@
         payload = as_config_object(raw, where)
         return cls(
             min_rest=read_int(payload, 'min_rest', where, DEFAULT_MIN_REST),
-            rest=read_text(payload, 'rest', where, REST_COUNT),
+            rest=read_text(payload, 'rest', None, REST_COUNT),
             skip_markup_without_opt=read_flag(payload, 'skip_markup_without_opt', where),
             zero_rest_without_category=read_flag(payload, 'zero_rest_without_category', where),
             collect_missing_recommended=read_flag(payload, 'collect_missing_recommended', where),
```

### `parsers.vendor_config.slot_configs.xǁBehaviorConfigǁfrom_dict__mutmut_85`

Статус: **survived**; тип: `to_none`; выбрано тестов: 149.

```diff
--- src/parsers/vendor_config/slot_configs.py
+++ src/parsers/vendor_config/slot_configs.py
@@ -9,7 +9,7 @@
             zero_rest_without_category=read_flag(payload, 'zero_rest_without_category', where),
             collect_missing_recommended=read_flag(payload, 'collect_missing_recommended', where),
             find_manufacturer_on_enrich=read_flag(payload, 'find_manufacturer_on_enrich', where, True),
-            manufacturer_column_first=read_flag(payload, 'manufacturer_column_first', where),
+            manufacturer_column_first=read_flag(payload, 'manufacturer_column_first', None),
             pipeline=read_str_list(payload, 'pipeline', where, DEFAULT_PIPELINE),
             warehouse_cities=read_str_list(payload, 'warehouse_cities', where, ()),
             order_from_warehouse_name=read_flag(payload, 'order_from_warehouse_name', where),
```

### `parsers.vendor_config.slot_configs.xǁBehaviorConfigǁfrom_dict__mutmut_93`

Статус: **survived**; тип: `to_none`; выбрано тестов: 149.

```diff
--- src/parsers/vendor_config/slot_configs.py
+++ src/parsers/vendor_config/slot_configs.py
@@ -10,7 +10,7 @@
             collect_missing_recommended=read_flag(payload, 'collect_missing_recommended', where),
             find_manufacturer_on_enrich=read_flag(payload, 'find_manufacturer_on_enrich', where, True),
             manufacturer_column_first=read_flag(payload, 'manufacturer_column_first', where),
-            pipeline=read_str_list(payload, 'pipeline', where, DEFAULT_PIPELINE),
+            pipeline=read_str_list(payload, 'pipeline', None, DEFAULT_PIPELINE),
             warehouse_cities=read_str_list(payload, 'warehouse_cities', where, ()),
             order_from_warehouse_name=read_flag(payload, 'order_from_warehouse_name', where),
             api_types=read_int_list(payload, 'api_types', where),
```

### `parsers.vendor_config.slot_configs.xǁBehaviorConfigǁfrom_dict__mutmut_103`

Статус: **survived**; тип: `to_none`; выбрано тестов: 149.

```diff
--- src/parsers/vendor_config/slot_configs.py
+++ src/parsers/vendor_config/slot_configs.py
@@ -11,7 +11,7 @@
             find_manufacturer_on_enrich=read_flag(payload, 'find_manufacturer_on_enrich', where, True),
             manufacturer_column_first=read_flag(payload, 'manufacturer_column_first', where),
             pipeline=read_str_list(payload, 'pipeline', where, DEFAULT_PIPELINE),
-            warehouse_cities=read_str_list(payload, 'warehouse_cities', where, ()),
+            warehouse_cities=read_str_list(payload, 'warehouse_cities', None, ()),
             order_from_warehouse_name=read_flag(payload, 'order_from_warehouse_name', where),
             api_types=read_int_list(payload, 'api_types', where),
         )
```

### `parsers.vendor_config.slot_configs.xǁBehaviorConfigǁfrom_dict__mutmut_113`

Статус: **survived**; тип: `to_none`; выбрано тестов: 149.

```diff
--- src/parsers/vendor_config/slot_configs.py
+++ src/parsers/vendor_config/slot_configs.py
@@ -12,6 +12,6 @@
             manufacturer_column_first=read_flag(payload, 'manufacturer_column_first', where),
             pipeline=read_str_list(payload, 'pipeline', where, DEFAULT_PIPELINE),
             warehouse_cities=read_str_list(payload, 'warehouse_cities', where, ()),
-            order_from_warehouse_name=read_flag(payload, 'order_from_warehouse_name', where),
+            order_from_warehouse_name=read_flag(payload, 'order_from_warehouse_name', None),
             api_types=read_int_list(payload, 'api_types', where),
         )
```

### `parsers.vendor_config.slot_configs.xǁBehaviorConfigǁfrom_dict__mutmut_121`

Статус: **survived**; тип: `to_none`; выбрано тестов: 149.

```diff
--- src/parsers/vendor_config/slot_configs.py
+++ src/parsers/vendor_config/slot_configs.py
@@ -13,5 +13,5 @@
             pipeline=read_str_list(payload, 'pipeline', where, DEFAULT_PIPELINE),
             warehouse_cities=read_str_list(payload, 'warehouse_cities', where, ()),
             order_from_warehouse_name=read_flag(payload, 'order_from_warehouse_name', where),
-            api_types=read_int_list(payload, 'api_types', where),
+            api_types=read_int_list(payload, 'api_types', None),
         )
```

### `parsers.vendor_config.slot_configs.xǁCategoryConfigǁfrom_dict__mutmut_28`

Статус: **survived**; тип: `to_none`; выбрано тестов: 188.

```diff
--- src/parsers/vendor_config/slot_configs.py
+++ src/parsers/vendor_config/slot_configs.py
@@ -3,7 +3,7 @@
         """Разобрать слот `category`: имя стратегии и её параметры."""
         payload = as_config_object(raw, where)
         return cls(
-            strategy=read_text(payload, 'strategy', where, DEFAULT_CATEGORY_STRATEGY),
+            strategy=read_text(payload, 'strategy', None, DEFAULT_CATEGORY_STRATEGY),
             fixed_value=read_text(payload, 'value', where, ''),
             field_name=read_text(payload, 'field', where, ''),
             mapping=read_str_map(payload, 'map', where),
```

### `parsers.vendor_config.slot_configs.xǁCategoryConfigǁfrom_dict__mutmut_113`

Статус: **survived**; тип: `to_none`; выбрано тестов: 188.

```diff
--- src/parsers/vendor_config/slot_configs.py
+++ src/parsers/vendor_config/slot_configs.py
@@ -12,5 +12,5 @@
             zero_rest_categories=read_str_list(payload, 'zero_rest_categories', where, ()),
             size_fields=read_field_map(payload, 'size_fields', where),
             calculate_type=read_flag(payload, 'calculate_type', where),
-            light_truck_by_diameter=read_flag(payload, 'light_truck_by_diameter', where),
+            light_truck_by_diameter=read_flag(payload, 'light_truck_by_diameter', None),
         )
```

### `parsers.vendor_config.slot_configs.xǁPricingConfigǁfrom_dict__mutmut_28`

Статус: **survived**; тип: `to_none`; выбрано тестов: 163.

```diff
--- src/parsers/vendor_config/slot_configs.py
+++ src/parsers/vendor_config/slot_configs.py
@@ -5,7 +5,7 @@
         rules_payload = read_object(payload, 'rules', where)
         rules_where = f'{where} → rules'
         return cls(
-            policy=read_text(payload, 'policy', where, DEFAULT_POLICY),
+            policy=read_text(payload, 'policy', None, DEFAULT_POLICY),
             rules=MarkupRulesConfig.from_dict(rules_payload, rules_where),
             threshold=read_number(rules_payload, 'threshold', rules_where),
             low=read_number(rules_payload, 'low', rules_where),
```

### `parsers.vendor_config.slot_configs.xǁTitleConfigǁfrom_dict__mutmut_26`

Статус: **survived**; тип: `to_none`; выбрано тестов: 180.

```diff
--- src/parsers/vendor_config/slot_configs.py
+++ src/parsers/vendor_config/slot_configs.py
@@ -3,7 +3,7 @@
         """Разобрать слот `title`."""
         payload = as_config_object(raw, where)
         return cls(
-            strategy=read_text(payload, 'strategy', where, DEFAULT_TITLE_STRATEGY),
+            strategy=read_text(payload, 'strategy', None, DEFAULT_TITLE_STRATEGY),
             variant=read_text(payload, 'variant', where, ''),
             aliases=read_flag(payload, 'aliases', where),
             fallback_brand=read_text(payload, 'fallback_brand', where, ''),
```

### `parsers.vendor_config.slot_configs.xǁTitleConfigǁfrom_dict__mutmut_98`

Статус: **survived**; тип: `to_none`; выбрано тестов: 180.

```diff
--- src/parsers/vendor_config/slot_configs.py
+++ src/parsers/vendor_config/slot_configs.py
@@ -11,5 +11,5 @@
             params_first=read_flag(payload, 'params_first', where),
             compose=read_flag(payload, 'compose', where),
             markers=read_field_map(payload, 'markers', where),
-            camera_by_kind=read_str_map(payload, 'camera_by_kind', where),
+            camera_by_kind=read_str_map(payload, 'camera_by_kind', None),
         )
```

## src/parsers/vendor_config/strategy_names.py

### `parsers.vendor_config.strategy_names.x__require_name__mutmut_2`

Статус: **survived**; тип: `to_none`; выбрано тестов: 38.

```diff
--- src/parsers/vendor_config/strategy_names.py
+++ src/parsers/vendor_config/strategy_names.py
@@ -1,5 +1,5 @@
 def _require_name(name: str, allowed: tuple[str, ...], where: str) -> None:
     """Отклонить чужое имя в исходном месте задания."""
     if name not in allowed:
-        available = ', '.join(allowed)
+        available = None
         raise ConfigValidationError(f'{where}: неизвестная стратегия tire_and_disk {name!r} (доступны: {available})')
```

### `parsers.vendor_config.strategy_names.x__require_name__mutmut_4`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 38.

```diff
--- src/parsers/vendor_config/strategy_names.py
+++ src/parsers/vendor_config/strategy_names.py
@@ -1,5 +1,5 @@
 def _require_name(name: str, allowed: tuple[str, ...], where: str) -> None:
     """Отклонить чужое имя в исходном месте задания."""
     if name not in allowed:
-        available = ', '.join(allowed)
+        available = 'XX, XX'.join(allowed)
         raise ConfigValidationError(f'{where}: неизвестная стратегия tire_and_disk {name!r} (доступны: {available})')
```

### `parsers.vendor_config.strategy_names.x_validate_strategy_names__mutmut_44`

Статус: **survived**; тип: `to_none`; выбрано тестов: 205.

```diff
--- src/parsers/vendor_config/strategy_names.py
+++ src/parsers/vendor_config/strategy_names.py
@@ -10,4 +10,4 @@
         if key in settings:
             name = read_text(settings, key, f'{where} → {slot}')
             _require_name(name, allowed, f'{where} → {slot} → {key}')
-    _validate_pipeline(read_object(payload, 'behavior', where), where)
+    _validate_pipeline(read_object(payload, 'behavior', None), where)
```

## src/parsers/writer/errors.py

### `parsers.writer.errors.xǁWorkbookNotInitializedErrorǁ__init____mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: R21 — survived; R22 — killed после ограничения regex полным сообщением. test_operations_require_workbook и test_save_requires_sheet проверяют точную диагностику ошибки порядка инициализации; поиск подстроки раньше пропускал XX по краям.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 3.

```diff
--- src/parsers/writer/errors.py
+++ src/parsers/writer/errors.py
@@ -1,2 +1,2 @@
     def __init__(self) -> None:
-        super().__init__('workbook is not initialized')
+        super().__init__('XXworkbook is not initializedXX')
```

### `parsers.writer.errors.xǁWorksheetNotInitializedErrorǁ__init____mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: R21 — survived; R22 — killed после ограничения regex полным сообщением. test_operations_require_sheet и test_operations_require_sheet_after_workbook_init проверяют точную диагностику отсутствующего листа, а не подстроку внутри изменённого сообщения.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 2.

```diff
--- src/parsers/writer/errors.py
+++ src/parsers/writer/errors.py
@@ -1,2 +1,2 @@
     def __init__(self) -> None:
-        super().__init__('worksheet is not initialized')
+        super().__init__('XXworksheet is not initializedXX')
```

## src/parsers/writer/group_files.py

### `parsers.writer.group_files.xǁGroupFileWriterǁ_write_book__mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed на существующих тестах. Конкретные провалы: test_workbook_sheets_keep_models_and_styles_independent[True-expected1], test_workbook_sheets_keep_models_and_styles_independent[False-expected0]. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 43.

```diff
--- src/parsers/writer/group_files.py
+++ src/parsers/writer/group_files.py
@@ -2,7 +2,7 @@
         driver = self._write_driver()
         multiple_sheets = len(book.sheets) > 1
         if multiple_sheets:
-            Path(self._result_folder).mkdir(parents=True, exist_ok=True)
+            Path(self._result_folder).mkdir(parents=None, exist_ok=True)
             driver.init_workbook(self._result_folder, book.file_name)
         result_path = ''
         for sheet in book.sheets:
```

### `parsers.writer.group_files.xǁGroupFileWriterǁ_write_book__mutmut_7`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed на существующих тестах. Конкретные провалы: test_workbook_sheets_keep_models_and_styles_independent[True-expected1], test_workbook_sheets_keep_models_and_styles_independent[False-expected0]. Исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 43.

```diff
--- src/parsers/writer/group_files.py
+++ src/parsers/writer/group_files.py
@@ -2,7 +2,7 @@
         driver = self._write_driver()
         multiple_sheets = len(book.sheets) > 1
         if multiple_sheets:
-            Path(self._result_folder).mkdir(parents=True, exist_ok=True)
+            Path(self._result_folder).mkdir(exist_ok=True)
             driver.init_workbook(self._result_folder, book.file_name)
         result_path = ''
         for sheet in book.sheets:
```

### `parsers.writer.group_files.xǁGroupFileWriterǁ_write_book__mutmut_10`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed на существующих тестах. Конкретные провалы: test_workbook_sheets_keep_models_and_styles_independent[False-expected0], test_workbook_sheets_keep_models_and_styles_independent[True-expected1]. Исторический survived сохранён.

Статус: **survived**; тип: `keyword`; выбрано тестов: 43.

```diff
--- src/parsers/writer/group_files.py
+++ src/parsers/writer/group_files.py
@@ -2,7 +2,7 @@
         driver = self._write_driver()
         multiple_sheets = len(book.sheets) > 1
         if multiple_sheets:
-            Path(self._result_folder).mkdir(parents=True, exist_ok=True)
+            Path(self._result_folder).mkdir(parents=False, exist_ok=True)
             driver.init_workbook(self._result_folder, book.file_name)
         result_path = ''
         for sheet in book.sheets:
```

### `parsers.writer.group_files.xǁGroupFileWriterǁ_write_book__mutmut_16`

Классификация 2026-11-14: Эквивалент: В корректно подготовленном плане каждая книга имеет хотя бы один лист: _place_sheets возвращает [] для отсутствующих листов. На каждом листе result_path безусловно присваивается из writer.get_result_path до возврата. Начальное None не читается; пустая книга, вручную переданная в приватный _write_book, не соответствует предусловию готового плана. Прямые запуски R14/R15 оставляют survived (248/251 passed); прохождение тестов не служит самостоятельным доказательством.

Статус: **survived**; тип: `to_none`; выбрано тестов: 43.

```diff
--- src/parsers/writer/group_files.py
+++ src/parsers/writer/group_files.py
@@ -4,7 +4,7 @@
         if multiple_sheets:
             Path(self._result_folder).mkdir(parents=True, exist_ok=True)
             driver.init_workbook(self._result_folder, book.file_name)
-        result_path = ''
+        result_path = None
         for sheet in book.sheets:
             writer = self._xls_writer(
                 driver,
```

### `parsers.writer.group_files.xǁGroupFileWriterǁ_write_book__mutmut_17`

Классификация 2026-11-14: Эквивалент: Для готового плана _place_sheets не создаёт книг без листов. Цикл безусловно перезаписывает result_path результатом get_result_path до возврата; начальная строка XXXX не наблюдается. Вывод ограничен контрактом готового плана, а не произвольным вызовом приватного _write_book. Прямые запуски R14/R15 оставляют survived (248/251 passed); прохождение тестов не служит самостоятельным доказательством.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 43.

```diff
--- src/parsers/writer/group_files.py
+++ src/parsers/writer/group_files.py
@@ -4,7 +4,7 @@
         if multiple_sheets:
             Path(self._result_folder).mkdir(parents=True, exist_ok=True)
             driver.init_workbook(self._result_folder, book.file_name)
-        result_path = ''
+        result_path = 'XXXX'
         for sheet in book.sheets:
             writer = self._xls_writer(
                 driver,
```

### `parsers.writer.group_files.xǁGroupFileWriterǁwrite_plan__mutmut_1`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed после усиления тестов. Конкретные провалы: test_prepared_plan_defaults_to_xlsx. Исторический survived сохранён.

Статус: **survived**; тип: `keyword`; выбрано тестов: 85.

```diff
--- src/parsers/writer/group_files.py
+++ src/parsers/writer/group_files.py
@@ -1,4 +1,4 @@
-    def write_plan(self, books: tuple[WorkbookPlan, ...], *, as_jsonl: bool = False) -> list[str]:
+    def write_plan(self, books: tuple[WorkbookPlan, ...], *, as_jsonl: bool = True) -> list[str]:
         """Записать полностью подготовленный план после проверки всех преобразователей."""
         if as_jsonl:
             return write_plan_jsonl(books, self._result_folder)
```

## src/parsers/writer/ixlsx_driver.py

### `parsers.writer.ixlsx_driver.xǁIXlsDriverǁwrite_head__mutmut_1`

Классификация 2026-11-14: Эквивалент по исполняемому контракту: метод IXlsDriver.write_head при любом row всегда поднимает NotImplementedError. XlsxWriterAdapter переопределяет метод и задаёт собственный дефолт row=0; изменение сигнатуры базового метода не меняет вызовы реализации. Интроспекция дефолтов интерфейса не является контрактом записи. R17 и R18: survived.

Статус: **survived**; тип: `number`; выбрано тестов: 1.

```diff
--- src/parsers/writer/ixlsx_driver.py
+++ src/parsers/writer/ixlsx_driver.py
@@ -1,3 +1,3 @@
-    def write_head(self, names: list[str], row: int = 0) -> None:
+    def write_head(self, names: list[str], row: int = 1) -> None:
         """write head at row (0 — первая строка листа)"""
         raise NotImplementedError
```

## src/parsers/writer/jsonl_codes.py

### `parsers.writer.jsonl_codes.x__next_code__mutmut_12`

Классификация 2026-11-14: Timeout подтверждён отдельным процессом с лимитом 2 с: `_next_code(set(), set())`. Инверсия условия заставляет перебирать все положительные индексы при пустом reserved, из цикла выхода нет. Исходная функция сразу возвращает @1. Это зацикливание мутанта, не исходного кода.

Статус: **timeout**; тип: `operator`; выбрано тестов: 43.

```diff
--- src/parsers/writer/jsonl_codes.py
+++ src/parsers/writer/jsonl_codes.py
@@ -1,6 +1,6 @@
 def _next_code(used: set[str], reserved: set[str]) -> str:
     indexes = (int(code[1:]) for code in used)
     index = max(indexes, default=0) + 1
-    while f'{_CODE_PREFIX}{index}' in reserved:
+    while f'{_CODE_PREFIX}{index}' not in reserved:
         index += 1
     return f'{_CODE_PREFIX}{index}'
```

### `parsers.writer.jsonl_codes.x__next_code__mutmut_13`

Классификация 2026-11-14: Timeout подтверждён отдельным процессом с лимитом 2 с: `_next_code(set(), {'@1'})`. После попадания в reserved присваивание index=1 снова проверяет тот же занятый код и зацикливает поиск. Исходная функция увеличивает индекс и возвращает @2.

Статус: **timeout**; тип: `operator`; выбрано тестов: 43.

```diff
--- src/parsers/writer/jsonl_codes.py
+++ src/parsers/writer/jsonl_codes.py
@@ -2,5 +2,5 @@
     indexes = (int(code[1:]) for code in used)
     index = max(indexes, default=0) + 1
     while f'{_CODE_PREFIX}{index}' in reserved:
-        index += 1
+        index = 1
     return f'{_CODE_PREFIX}{index}'
```

## src/parsers/writer/jsonl_meta.py

### `parsers.writer.jsonl_meta.x__check_file__mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed на существующих тестах. Конкретные провалы: test_jsonl_incompatible_schema_error_names_file. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 54.

```diff
--- src/parsers/writer/jsonl_meta.py
+++ src/parsers/writer/jsonl_meta.py
@@ -3,4 +3,4 @@
         if path.exists():
             raise metadata_error(path)
     elif any(previous[key] != planned[key] for key in IDENTITY_KEYS):
-        raise metadata_error(path)
+        raise metadata_error(None)
```

### `parsers.writer.jsonl_meta.x_check_existing__mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed после усиления тестов. Конкретные провалы: test_registry_case_change_cannot_claim_existing_file. Исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 54.

```diff
--- src/parsers/writer/jsonl_meta.py
+++ src/parsers/writer/jsonl_meta.py
@@ -2,6 +2,6 @@
     """Принадлежность существующих потоков должна совпадать с новым планом."""
     names = {name.casefold(): name for name in registry}
     for name, schema in planned.items():
-        if names.get(name.casefold(), name) != name:
+        if names.get(None, name) != name:
             raise metadata_error(folder / name)
         _check_file(folder / name, registry.get(name), schema)
```

## src/parsers/writer/jsonl_packing.py

### `parsers.writer.jsonl_packing.x__serialize_row__mutmut_3`

Классификация 2026-11-14: Эквивалент: json.dumps проверяет ensure_ascii по истинности; False и None одинаково сохраняют Unicode без ASCII-экранирования. Остальные параметры и завершающий перевод строки неизменны. R21/R22: survived, 259 passed.

Статус: **survived**; тип: `to_none`; выбрано тестов: 64.

```diff
--- src/parsers/writer/jsonl_packing.py
+++ src/parsers/writer/jsonl_packing.py
@@ -1,3 +1,3 @@
 def _serialize_row(row: PriceRow) -> str:
-    packed = json.dumps(row, ensure_ascii=False, default=str, separators=_SEPARATORS)
+    packed = json.dumps(row, ensure_ascii=None, default=str, separators=_SEPARATORS)
     return f'{packed}\n'
```

## src/parsers/writer/jsonl_publish.py

### `parsers.writer.jsonl_publish.x__replace_files__mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff убит существующим test_jsonl_stages_replacement_on_result_filesystem в R21 и R22. Каталог staging должен лежать на файловой системе результата, чтобы Path.replace не зависел от возможности переноса между файловыми системами. Тест проверяет аргумент TemporaryDirectory; реальный EXDEV в этих прогонах не воспроизводился.

Статус: **survived**; тип: `to_none`; выбрано тестов: 53.

```diff
--- src/parsers/writer/jsonl_publish.py
+++ src/parsers/writer/jsonl_publish.py
@@ -1,7 +1,7 @@
 def _replace_files(folder: Path, payloads: dict[str, str]) -> None:
     previous = {name: _read_previous(folder / name) for name in payloads}
     replaced: list[str] = []
-    with TemporaryDirectory(dir=folder) as staging:
+    with TemporaryDirectory(dir=None) as staging:
         for name, payload in payloads.items():
             Path(staging, name).write_text(payload, encoding='utf-8')
         try:
```

### `parsers.writer.jsonl_publish.x_publish_jsonl__mutmut_19`

Классификация 2026-11-14: Эквивалент: ensure_ascii=False и None одинаково отключают экранирование Unicode в json.dumps метаданных; состав реестра и публикация не меняются. R21/R22: survived, 259 passed.

Статус: **survived**; тип: `to_none`; выбрано тестов: 66.

```diff
--- src/parsers/writer/jsonl_publish.py
+++ src/parsers/writer/jsonl_publish.py
@@ -8,7 +8,7 @@
     folder.mkdir(parents=True, exist_ok=True)
     payloads = {
         **streams,
-        RESULT_META_FILE: json.dumps({'version': META_VERSION, 'files': registry}, ensure_ascii=False),
+        RESULT_META_FILE: json.dumps({'version': META_VERSION, 'files': registry}, ensure_ascii=None),
     }
     _replace_files(folder, payloads)
     return [str((folder / name).resolve()) for name in streams]
```

## src/parsers/writer/jsonl_schema.py

### `parsers.writer.jsonl_schema.x_valid_name__mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff убит существующим test_jsonl_rejects_parent_and_windows_paths для ../price.jsonl и folder/../price.jsonl в R21 и R22. Подмена .. разрешает родительский сегмент; это различимое нарушение проверки имён, а не эквивалент.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 27.

```diff
--- src/parsers/writer/jsonl_schema.py
+++ src/parsers/writer/jsonl_schema.py
@@ -1,6 +1,6 @@
 def valid_name(name: str) -> bool:
     path = PurePosixPath(name)
-    forbidden = (path.is_absolute(), '..' in path.parts, '\\' in name)
+    forbidden = (path.is_absolute(), 'XX..XX' in path.parts, '\\' in name)
     if str(path) != name:
         return False
     return not any(forbidden) and path.suffix == '.jsonl'
```

### `parsers.writer.jsonl_schema.x_valid_name__mutmut_6`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff убит существующим test_jsonl_rejects_parent_and_windows_paths для имени с обратной косой чертой в R21 и R22. PurePosixPath не превращает её в разделитель; запрет обеспечивается именно проверкой символа.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 27.

```diff
--- src/parsers/writer/jsonl_schema.py
+++ src/parsers/writer/jsonl_schema.py
@@ -1,6 +1,6 @@
 def valid_name(name: str) -> bool:
     path = PurePosixPath(name)
-    forbidden = (path.is_absolute(), '..' in path.parts, '\\' in name)
+    forbidden = (path.is_absolute(), '..' in path.parts, 'XX\\XX' in name)
     if str(path) != name:
         return False
     return not any(forbidden) and path.suffix == '.jsonl'
```

## src/parsers/writer/jsonl_writer.py

### `parsers.writer.jsonl_writer.x__template_name__mutmut_6`

Классификация 2026-11-14: Эквивалент в контракте write_template_jsonl: приватный _template_name возвращает имя только в WorkbookPlan; _pack_books затем вызывает jsonl_name, который берёт Path(name).stem и заново добавляет .jsonl. Поэтому промежуточные .jsonl и .JSONL дают одинаковые публикуемые имена и метаданные; иных потребителей _template_name нет. R21/R22: survived, 259 passed.

Статус: **survived**; тип: `string_case`; выбрано тестов: 27.

```diff
--- src/parsers/writer/jsonl_writer.py
+++ src/parsers/writer/jsonl_writer.py
@@ -1,3 +1,3 @@
 def _template_name(template: IWriteTemplate) -> str:
     name = template.get_file_name().format(now=datetime.date.today().isoformat())
-    return Path(name).with_suffix('.jsonl').name
+    return Path(name).with_suffix('.JSONL').name
```

## src/parsers/writer/output_names.py

### `parsers.writer.output_names.x_output_file_name__mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed на существующих тестах. Конкретные провалы: test_invalid_file_name_includes_template_location. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 120.

```diff
--- src/parsers/writer/output_names.py
+++ src/parsers/writer/output_names.py
@@ -1,6 +1,6 @@
 def output_file_name(pattern: str, current_date: str, where: str) -> str:
     """Подставить только дату и проверить имя файла для всех поддерживаемых ОС."""
-    _validate_pattern(pattern, where)
+    _validate_pattern(pattern, None)
     name = pattern.format(now=current_date)
     invalid = not name.endswith('.xlsx') or '..' in name
     invalid = invalid or name.endswith(('.', ' '))
```

### `parsers.writer.output_names.x_output_file_name__mutmut_13`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed на существующих тестах. Конкретные провалы: test_invalid_file_name[price..xlsx]. Исторический survived сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 120.

```diff
--- src/parsers/writer/output_names.py
+++ src/parsers/writer/output_names.py
@@ -2,7 +2,7 @@
     """Подставить только дату и проверить имя файла для всех поддерживаемых ОС."""
     _validate_pattern(pattern, where)
     name = pattern.format(now=current_date)
-    invalid = not name.endswith('.xlsx') or '..' in name
+    invalid = not name.endswith('.xlsx') or 'XX..XX' in name
     invalid = invalid or name.endswith(('.', ' '))
     device = PureWindowsPath(name).stem.split('.')[0].casefold()
     invalid = invalid or device in _DEVICE_NAMES
```

### `parsers.writer.output_names.x_output_file_name__mutmut_18`

Классификация 2026-11-14: Эквивалент: Для допустимого имени обязательное окончание .xlsx исключает и конечную точку, и конечное XX.XX. Остальные имена уже отклонены проверкой расширения; изменённая проверка не влияет ни на решение, ни на сообщение. Прямые запуски R14/R15 оставляют survived (248/251 passed); прохождение тестов не служит самостоятельным доказательством.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 120.

```diff
--- src/parsers/writer/output_names.py
+++ src/parsers/writer/output_names.py
@@ -3,7 +3,7 @@
     _validate_pattern(pattern, where)
     name = pattern.format(now=current_date)
     invalid = not name.endswith('.xlsx') or '..' in name
-    invalid = invalid or name.endswith(('.', ' '))
+    invalid = invalid or name.endswith(('XX.XX', ' '))
     device = PureWindowsPath(name).stem.split('.')[0].casefold()
     invalid = invalid or device in _DEVICE_NAMES
     if invalid or _forbidden(name, '<>:"|?*/\\'):
```

### `parsers.writer.output_names.x_output_file_name__mutmut_19`

Классификация 2026-11-14: Эквивалент: Для допустимого имени обязательно окончание .xlsx, поэтому имя не может оканчиваться ни пробелом, ни XX XX. Для остальных имён invalid уже истинен из-за расширения; сообщение ошибки не меняется. Прямые запуски R14/R15 оставляют survived (248/251 passed); прохождение тестов не служит самостоятельным доказательством.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 120.

```diff
--- src/parsers/writer/output_names.py
+++ src/parsers/writer/output_names.py
@@ -3,7 +3,7 @@
     _validate_pattern(pattern, where)
     name = pattern.format(now=current_date)
     invalid = not name.endswith('.xlsx') or '..' in name
-    invalid = invalid or name.endswith(('.', ' '))
+    invalid = invalid or name.endswith(('.', 'XX XX'))
     device = PureWindowsPath(name).stem.split('.')[0].casefold()
     invalid = invalid or device in _DEVICE_NAMES
     if invalid or _forbidden(name, '<>:"|?*/\\'):
```

### `parsers.writer.output_names.x_output_file_name__mutmut_21`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed на существующих тестах. Конкретные провалы: test_invalid_file_name[CON.backup.xlsx]. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 120.

```diff
--- src/parsers/writer/output_names.py
+++ src/parsers/writer/output_names.py
@@ -4,7 +4,7 @@
     name = pattern.format(now=current_date)
     invalid = not name.endswith('.xlsx') or '..' in name
     invalid = invalid or name.endswith(('.', ' '))
-    device = PureWindowsPath(name).stem.split('.')[0].casefold()
+    device = PureWindowsPath(name).stem.split(None)[0].casefold()
     invalid = invalid or device in _DEVICE_NAMES
     if invalid or _forbidden(name, '<>:"|?*/\\'):
         raise ConfigValidationError(f'{where} → file_name: недопустимое имя файла {name!r}')
```

### `parsers.writer.output_names.x_output_file_name__mutmut_23`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed на существующих тестах. Конкретные провалы: test_invalid_file_name[CON.backup.xlsx]. Исторический survived сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 120.

```diff
--- src/parsers/writer/output_names.py
+++ src/parsers/writer/output_names.py
@@ -4,7 +4,7 @@
     name = pattern.format(now=current_date)
     invalid = not name.endswith('.xlsx') or '..' in name
     invalid = invalid or name.endswith(('.', ' '))
-    device = PureWindowsPath(name).stem.split('.')[0].casefold()
+    device = PureWindowsPath(name).stem.split('XX.XX')[0].casefold()
     invalid = invalid or device in _DEVICE_NAMES
     if invalid or _forbidden(name, '<>:"|?*/\\'):
         raise ConfigValidationError(f'{where} → file_name: недопустимое имя файла {name!r}')
```

### `parsers.writer.output_names.x_output_file_name__mutmut_33`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed после усиления тестов. Конкретные провалы: test_latin_x_is_allowed_in_output_names. Исторический survived сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 120.

```diff
--- src/parsers/writer/output_names.py
+++ src/parsers/writer/output_names.py
@@ -6,6 +6,6 @@
     invalid = invalid or name.endswith(('.', ' '))
     device = PureWindowsPath(name).stem.split('.')[0].casefold()
     invalid = invalid or device in _DEVICE_NAMES
-    if invalid or _forbidden(name, '<>:"|?*/\\'):
+    if invalid or _forbidden(name, 'XX<>:"|?*/\\XX'):
         raise ConfigValidationError(f'{where} → file_name: недопустимое имя файла {name!r}')
     return name
```

### `parsers.writer.output_names.x_validate_sheet_name__mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed на существующих тестах. Конкретные провалы: test_sheet_name_allows_excel_maximum_length. Исторический survived сохранён.

Статус: **survived**; тип: `operator`; выбрано тестов: 131.

```diff
--- src/parsers/writer/output_names.py
+++ src/parsers/writer/output_names.py
@@ -1,6 +1,6 @@
 def validate_sheet_name(name: str, where: str) -> None:
     """Отклонить имя, которое Excel исправил бы или запретил."""
-    invalid = not name.strip() or len(name) > MAX_SHEET_NAME
+    invalid = not name.strip() or len(name) >= MAX_SHEET_NAME
     invalid = invalid or name.casefold() == 'history'
     invalid = invalid or name.startswith("'") or name.endswith("'")
     if invalid or _forbidden(name, r':\/?*[]'):
```

### `parsers.writer.output_names.x_validate_sheet_name__mutmut_22`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed после усиления тестов. Конкретные провалы: test_latin_x_is_allowed_in_output_names. Исторический survived сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 131.

```diff
--- src/parsers/writer/output_names.py
+++ src/parsers/writer/output_names.py
@@ -3,5 +3,5 @@
     invalid = not name.strip() or len(name) > MAX_SHEET_NAME
     invalid = invalid or name.casefold() == 'history'
     invalid = invalid or name.startswith("'") or name.endswith("'")
-    if invalid or _forbidden(name, r':\/?*[]'):
+    if invalid or _forbidden(name, r'XX:\/?*[]XX'):
         raise ConfigValidationError(f'{where} → sheet_name: недопустимое имя листа {name!r}')
```

## src/parsers/writer/output_paths.py

### `parsers.writer.output_paths.x__register_path__mutmut_1`

Классификация 2026-11-14: Эквивалент: Для XLSX shared всегда передаётся явно. Дефолт используется для JSONL: повтор с тем же owner невозможен в validate_outputs, потому что template_id уникальны, а группа внутри шаблона не повторяется. При разных owner обе версии отклоняют конфликт. Это эквивалент в достижимых состояниях публичной валидации; приватный вызов с искусственно повторённым owner в вывод не входит. Прямые запуски R14/R15 оставляют survived (248/251 passed); прохождение тестов не служит самостоятельным доказательством.

Статус: **survived**; тип: `keyword`; выбрано тестов: 105.

```diff
--- src/parsers/writer/output_paths.py
+++ src/parsers/writer/output_paths.py
@@ -1,4 +1,4 @@
-def _register_path(name: str, owner: str, paths: dict[str, str], *, shared: bool = False) -> None:
+def _register_path(name: str, owner: str, paths: dict[str, str], *, shared: bool = True) -> None:
     key = name.casefold()
     previous = paths.get(key)
     if previous is not None and not (shared and previous == owner):
```

### `parsers.writer.output_paths.x__register_path__mutmut_8`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed после усиления тестов. Конкретные провалы: test_workbook_path_cannot_be_shared_by_different_templates. Исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 105.

```diff
--- src/parsers/writer/output_paths.py
+++ src/parsers/writer/output_paths.py
@@ -1,6 +1,6 @@
 def _register_path(name: str, owner: str, paths: dict[str, str], *, shared: bool = False) -> None:
     key = name.casefold()
     previous = paths.get(key)
-    if previous is not None and not (shared and previous == owner):
+    if previous is not None and not (shared or previous == owner):
         raise ConfigValidationError(f'{owner} → file_name: путь {name!r} уже занят: {previous}')
     paths[key] = owner
```

### `parsers.writer.output_paths.x_register_paths__mutmut_9`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed на существующих тестах. Конкретные провалы: test_unselected_group_filename_is_still_validated. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 106.

```diff
--- src/parsers/writer/output_paths.py
+++ src/parsers/writer/output_paths.py
@@ -1,7 +1,7 @@
 def register_paths(output: TemplateOutput, group: GroupOutput, current_date: str, paths: dict[str, str]) -> None:
     where = f'Шаблон {output.template_id} → {group.id}'
     pattern = group.file_name if output.mode == OutputMode.SEPARATE_FILES else output.file_name
-    name = output_file_name(pattern or '', current_date, where)
+    name = output_file_name(pattern or '', current_date, None)
     owner = where if output.mode == OutputMode.SEPARATE_FILES else f'Шаблон {output.template_id}'
     _register_path(name, owner, paths, shared=output.mode == OutputMode.WORKBOOK_SHEETS)
     _register_path(jsonl_name(name, output.mode, group.id), where, paths)
```

### `parsers.writer.output_paths.x_register_paths__mutmut_14`

Классификация 2026-11-14: Закрытый пробел проверки: R14 и R15 оставляли survived; после проверки исходного пустого значения имени в диагностике прямое применение исторического diff в R16 убито test_empty_group_filename_reports_original_value (1 failed, 251 passed). Структура требует не None, но допускает пустую строку до проверки имени, поэтому прежний групповой вывод о недостижимости fallback исправлен.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 106.

```diff
--- src/parsers/writer/output_paths.py
+++ src/parsers/writer/output_paths.py
@@ -1,7 +1,7 @@
 def register_paths(output: TemplateOutput, group: GroupOutput, current_date: str, paths: dict[str, str]) -> None:
     where = f'Шаблон {output.template_id} → {group.id}'
     pattern = group.file_name if output.mode == OutputMode.SEPARATE_FILES else output.file_name
-    name = output_file_name(pattern or '', current_date, where)
+    name = output_file_name(pattern or 'XXXX', current_date, where)
     owner = where if output.mode == OutputMode.SEPARATE_FILES else f'Шаблон {output.template_id}'
     _register_path(name, owner, paths, shared=output.mode == OutputMode.WORKBOOK_SHEETS)
     _register_path(jsonl_name(name, output.mode, group.id), where, paths)
```

### `parsers.writer.output_paths.x_register_paths__mutmut_15`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed на существующих тестах. Конкретные провалы: test_workbook_path_cannot_be_shared_by_different_templates, test_path_collision_names_group_owner. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 106.

```diff
--- src/parsers/writer/output_paths.py
+++ src/parsers/writer/output_paths.py
@@ -2,6 +2,6 @@
     where = f'Шаблон {output.template_id} → {group.id}'
     pattern = group.file_name if output.mode == OutputMode.SEPARATE_FILES else output.file_name
     name = output_file_name(pattern or '', current_date, where)
-    owner = where if output.mode == OutputMode.SEPARATE_FILES else f'Шаблон {output.template_id}'
+    owner = None
     _register_path(name, owner, paths, shared=output.mode == OutputMode.WORKBOOK_SHEETS)
     _register_path(jsonl_name(name, output.mode, group.id), where, paths)
```

### `parsers.writer.output_paths.x_register_paths__mutmut_16`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed на существующих тестах. Конкретные провалы: test_path_collision_names_group_owner. Исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 106.

```diff
--- src/parsers/writer/output_paths.py
+++ src/parsers/writer/output_paths.py
@@ -2,6 +2,6 @@
     where = f'Шаблон {output.template_id} → {group.id}'
     pattern = group.file_name if output.mode == OutputMode.SEPARATE_FILES else output.file_name
     name = output_file_name(pattern or '', current_date, where)
-    owner = where if output.mode == OutputMode.SEPARATE_FILES else f'Шаблон {output.template_id}'
+    owner = where if (output.mode == OutputMode.SEPARATE_FILES) and False else f'Шаблон {output.template_id}'
     _register_path(name, owner, paths, shared=output.mode == OutputMode.WORKBOOK_SHEETS)
     _register_path(jsonl_name(name, output.mode, group.id), where, paths)
```

### `parsers.writer.output_paths.x_register_paths__mutmut_20`

Классификация 2026-11-14: Закрытый пробел проверки: исторический diff применён с единственным точным совпадением полного контекста в R15; killed на существующих тестах. Конкретные провалы: test_path_collision_names_group_owner, test_workbook_path_cannot_be_shared_by_different_templates. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 106.

```diff
--- src/parsers/writer/output_paths.py
+++ src/parsers/writer/output_paths.py
@@ -3,5 +3,5 @@
     pattern = group.file_name if output.mode == OutputMode.SEPARATE_FILES else output.file_name
     name = output_file_name(pattern or '', current_date, where)
     owner = where if output.mode == OutputMode.SEPARATE_FILES else f'Шаблон {output.template_id}'
-    _register_path(name, owner, paths, shared=output.mode == OutputMode.WORKBOOK_SHEETS)
+    _register_path(name, None, paths, shared=output.mode == OutputMode.WORKBOOK_SHEETS)
     _register_path(jsonl_name(name, output.mode, group.id), where, paths)
```

## src/parsers/writer/output_plan.py

### `parsers.writer.output_plan.x__place_sheets__mutmut_6`

Классификация 2026-11-14: Эквивалент в контракте публичного prepare_output_plan: аргумент where используется output_file_name только в ошибках. До _place_sheets validate_outputs → register_paths проверяет то же имя с той же датой. Настройки GroupOutput/TemplateOutput frozen, поэтому при построении книги имя остаётся допустимым и where не наблюдается. Прямой вызов приватного _place_sheets с невалидированным шаблоном вне этого контракта. R20: 259 passed, exit 0; основание эквивалентности — предварительная валидация, а не один результат тестов.

Статус: **survived**; тип: `other`; выбрано тестов: 93.

```diff
--- src/parsers/writer/output_plan.py
+++ src/parsers/writer/output_plan.py
@@ -2,7 +2,7 @@
     if not sheets:
         return []
     if output.mode == OutputMode.WORKBOOK_SHEETS:
-        name = output_file_name(output.file_name or '', current_date, output.template_id)
+        name = output_file_name(output.file_name or '', current_date, None)
         return [WorkbookPlan(output.template_id, name, sheets, output.mode)]
     return [
         WorkbookPlan(
```

### `parsers.writer.output_plan.x__place_sheets__mutmut_11`

Классификация 2026-11-14: Эквивалент в контракте публичного prepare_output_plan: ветка fallback имени в _place_sheets недостижима. Для workbook_sheets validate_structure требует file_name не None, затем register_paths отклоняет пустую строку через output_file_name; для separate_files те же проверки выполняются для каждой группы. До построения книги доходят только непустые имена; frozen-настройки сохраняют их. Замена пустого fallback на XXXX не влияет на результат. R20: 259 passed, exit 0; прямой приватный вызов без валидации не включён в контракт.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 93.

```diff
--- src/parsers/writer/output_plan.py
+++ src/parsers/writer/output_plan.py
@@ -2,7 +2,7 @@
     if not sheets:
         return []
     if output.mode == OutputMode.WORKBOOK_SHEETS:
-        name = output_file_name(output.file_name or '', current_date, output.template_id)
+        name = output_file_name(output.file_name or 'XXXX', current_date, output.template_id)
         return [WorkbookPlan(output.template_id, name, sheets, output.mode)]
     return [
         WorkbookPlan(
```

### `parsers.writer.output_plan.x__place_sheets__mutmut_15`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff отдельно применён с единственным совпадением полного контекста во временной копии. R20: killed на существующем тесте `test_group_sources_have_independent_settings[workbook_sheets-1]` (exit 1). База: 259 passed. Исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 93.

```diff
--- src/parsers/writer/output_plan.py
+++ src/parsers/writer/output_plan.py
@@ -3,7 +3,7 @@
         return []
     if output.mode == OutputMode.WORKBOOK_SHEETS:
         name = output_file_name(output.file_name or '', current_date, output.template_id)
-        return [WorkbookPlan(output.template_id, name, sheets, output.mode)]
+        return [WorkbookPlan(output.template_id, name, sheets, None)]
     return [
         WorkbookPlan(
             output.template_id,
```

### `parsers.writer.output_plan.x__place_sheets__mutmut_28`

Классификация 2026-11-14: Эквивалент в контракте публичного prepare_output_plan: аргумент where используется output_file_name только в ошибках. До _place_sheets validate_outputs → register_paths проверяет то же имя с той же датой. Настройки GroupOutput/TemplateOutput frozen, поэтому при построении книги имя остаётся допустимым и where не наблюдается. Прямой вызов приватного _place_sheets с невалидированным шаблоном вне этого контракта. R20: 259 passed, exit 0; основание эквивалентности — предварительная валидация, а не один результат тестов.

Статус: **survived**; тип: `other`; выбрано тестов: 93.

```diff
--- src/parsers/writer/output_plan.py
+++ src/parsers/writer/output_plan.py
@@ -7,7 +7,7 @@
     return [
         WorkbookPlan(
             output.template_id,
-            output_file_name(sheet.settings.file_name or '', current_date, output.template_id),
+            output_file_name(sheet.settings.file_name or '', current_date, None),
             (sheet,),
         )
         for sheet in sheets
```

### `parsers.writer.output_plan.x__place_sheets__mutmut_33`

Классификация 2026-11-14: Эквивалент в контракте публичного prepare_output_plan: ветка fallback имени в _place_sheets недостижима. Для workbook_sheets validate_structure требует file_name не None, затем register_paths отклоняет пустую строку через output_file_name; для separate_files те же проверки выполняются для каждой группы. До построения книги доходят только непустые имена; frozen-настройки сохраняют их. Замена пустого fallback на XXXX не влияет на результат. R20: 259 passed, exit 0; прямой приватный вызов без валидации не включён в контракт.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 93.

```diff
--- src/parsers/writer/output_plan.py
+++ src/parsers/writer/output_plan.py
@@ -7,7 +7,7 @@
     return [
         WorkbookPlan(
             output.template_id,
-            output_file_name(sheet.settings.file_name or '', current_date, output.template_id),
+            output_file_name(sheet.settings.file_name or 'XXXX', current_date, output.template_id),
             (sheet,),
         )
         for sheet in sheets
```

### `parsers.writer.output_plan.x_prepare_output_plan__mutmut_15`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff отдельно применён с единственным совпадением полного контекста во временной копии. R20: killed на существующем тесте `test_explicit_selection_is_validated_before_preparing_positions` (exit 1). База: 259 passed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 99.

```diff
--- src/parsers/writer/output_plan.py
+++ src/parsers/writer/output_plan.py
@@ -16,7 +16,7 @@
         selected,
         schemas=_schemas(sources),
         current_date=current_date,
-        selections=selections,
+        selections=None,
     )
     selections = selections or {output.template_id: selected for output in outputs}
     return tuple(
```

### `parsers.writer.output_plan.x_prepare_output_plan__mutmut_20`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff отдельно применён с единственным совпадением полного контекста во временной копии. R20: killed на существующем тесте `test_explicit_selection_is_validated_before_preparing_positions` (exit 1). База: 259 passed. Исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 99.

```diff
--- src/parsers/writer/output_plan.py
+++ src/parsers/writer/output_plan.py
@@ -16,8 +16,7 @@
         selected,
         schemas=_schemas(sources),
         current_date=current_date,
-        selections=selections,
-    )
+        )
     selections = selections or {output.template_id: selected for output in outputs}
     return tuple(
         chain.from_iterable(
```

## src/parsers/writer/output_structure.py

### `parsers.writer.output_structure.x__validate_sheets__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff отдельно применён с единственным совпадением полного контекста во временной копии. R20: killed на существующем тесте `test_invalid_sheet_name_includes_template_location` (exit 1). База: 259 passed. Исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 116.

```diff
--- src/parsers/writer/output_structure.py
+++ src/parsers/writer/output_structure.py
@@ -1,7 +1,7 @@
 def _validate_sheets(output: TemplateOutput, where: str) -> None:
     names: set[str] = set()
     for group in output.groups:
-        validate_sheet_name(group.sheet_name, f'{where} → {group.id}')
+        validate_sheet_name(group.sheet_name, None)
         sheet = group.sheet_name.casefold()
         if output.mode == OutputMode.WORKBOOK_SHEETS and sheet in names:
             raise ConfigValidationError(f'{where} → {group.id} → sheet_name: повтор имени листа')
```

### `parsers.writer.output_structure.x_validate_structure__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff отдельно применён с единственным совпадением полного контекста во временной копии. R20: killed на существующем тесте `test_blank_template_identifier_rejected` (exit 1). База: 259 passed. Исторический survived сохранён.

Статус: **survived**; тип: `operator`; выбрано тестов: 121.

```diff
--- src/parsers/writer/output_structure.py
+++ src/parsers/writer/output_structure.py
@@ -2,7 +2,7 @@
     """Проверить объявление групп, выбор и размещение книг."""
     where = f'Шаблон {output.template_id}'
     identifiers = [group.id for group in output.groups]
-    if not output.template_id.strip() or not identifiers:
+    if not output.template_id.strip() and not identifiers:
         raise ConfigValidationError(f'{where} → groups: пустое описание')
     if len(set(identifiers)) != len(identifiers):
         raise ConfigValidationError(f'{where} → groups: повтор группы')
```

### `parsers.writer.output_structure.x_validate_structure__mutmut_19`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff отдельно применён с единственным совпадением полного контекста во временной копии. R20: killed на существующем тесте `test_invalid_sheet_name_includes_template_location` (exit 1). База: 259 passed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 121.

```diff
--- src/parsers/writer/output_structure.py
+++ src/parsers/writer/output_structure.py
@@ -10,4 +10,4 @@
     if missing:
         raise ConfigValidationError(f'{where} → groups: выбраны неподдерживаемые группы {sorted(missing)}')
     _validate_mode(output, where)
-    _validate_sheets(output, where)
+    _validate_sheets(output, None)
```

## src/parsers/writer/output_validation.py

### `parsers.writer.output_validation.x_validate_outputs__mutmut_11`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff отдельно применён с единственным совпадением полного контекста во временной копии. R20: killed на существующем тесте `test_repeated_template_identifier_rejected` (exit 1). База: 259 passed. Исторический survived сохранён.

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 122.

```diff
--- src/parsers/writer/output_validation.py
+++ src/parsers/writer/output_validation.py
@@ -15,7 +15,7 @@
     current_date = current_date or date.today().isoformat()
     paths: dict[str, str] = {}
     if len({output.template_id for output in outputs}) != len(outputs):
-        raise ConfigValidationError('Повтор template_id в плане записи')
+        raise ConfigValidationError('XXПовтор template_id в плане записиXX')
     selections = selections or {output.template_id: selected for output in outputs}
     for output in outputs:
         _validate_template(output, selections[output.template_id], schemas, current_date, paths)
```

### `parsers.writer.output_validation.x_validate_outputs__mutmut_12`

Классификация 2026-11-14: Закрытый пробел проверки: точный исторический diff отдельно применён с единственным совпадением полного контекста во временной копии. R20: killed на существующем тесте `test_repeated_template_identifier_rejected` (exit 1). База: 259 passed. Исторический survived сохранён.

Статус: **survived**; тип: `string_case`; выбрано тестов: 122.

```diff
--- src/parsers/writer/output_validation.py
+++ src/parsers/writer/output_validation.py
@@ -15,7 +15,7 @@
     current_date = current_date or date.today().isoformat()
     paths: dict[str, str] = {}
     if len({output.template_id for output in outputs}) != len(outputs):
-        raise ConfigValidationError('Повтор template_id в плане записи')
+        raise ConfigValidationError('повтор template_id в плане записи')
     selections = selections or {output.template_id: selected for output in outputs}
     for output in outputs:
         _validate_template(output, selections[output.template_id], schemas, current_date, paths)
```

## src/parsers/writer/templates/all_templates.py

### `parsers.writer.templates.all_templates.x_writer_template_name__mutmut_4`

Статус: **survived**; тип: `other`; выбрано тестов: 88.

```diff
--- src/parsers/writer/templates/all_templates.py
+++ src/parsers/writer/templates/all_templates.py
@@ -1,3 +1,3 @@
 def writer_template_name(template: type[IWriteTemplate]) -> str:
     """Имя шаблона как в CLI: for_drom, for_inner, for_full."""
-    return template.__module__.rsplit('.', maxsplit=1)[-1]
+    return template.__module__.rsplit('.', )[-1]
```

### `parsers.writer.templates.all_templates.x_writer_template_name__mutmut_7`

Статус: **survived**; тип: `number`; выбрано тестов: 88.

```diff
--- src/parsers/writer/templates/all_templates.py
+++ src/parsers/writer/templates/all_templates.py
@@ -1,3 +1,3 @@
 def writer_template_name(template: type[IWriteTemplate]) -> str:
     """Имя шаблона как в CLI: for_drom, for_inner, for_full."""
-    return template.__module__.rsplit('.', maxsplit=1)[-1]
+    return template.__module__.rsplit('.', maxsplit=2)[-1]
```

### `parsers.writer.templates.all_templates.x_writer_template_name__mutmut_8`

Статус: **survived**; тип: `operator`; выбрано тестов: 88.

```diff
--- src/parsers/writer/templates/all_templates.py
+++ src/parsers/writer/templates/all_templates.py
@@ -1,3 +1,3 @@
 def writer_template_name(template: type[IWriteTemplate]) -> str:
     """Имя шаблона как в CLI: for_drom, for_inner, for_full."""
-    return template.__module__.rsplit('.', maxsplit=1)[-1]
+    return template.__module__.rsplit('.', maxsplit=1)[+1]
```

## src/parsers/writer/templates/group_templates.py

### `parsers.writer.templates.group_templates.x__drom_batteries__mutmut_7`

Статус: **survived**; тип: `other`; выбрано тестов: 27.

```diff
--- src/parsers/writer/templates/group_templates.py
+++ src/parsers/writer/templates/group_templates.py
@@ -24,6 +24,5 @@
             {'EFB': {_FIELD: 'efb'}},
             {'AGM': {_FIELD: 'agm'}},
         ],
-        filters={'rest_count': [None, '']},
         file_name='price_drom_akb_{now}.xlsx',
     )
```

### `parsers.writer.templates.group_templates.x__drom_batteries__mutmut_32`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 27.

```diff
--- src/parsers/writer/templates/group_templates.py
+++ src/parsers/writer/templates/group_templates.py
@@ -6,7 +6,7 @@
             {'Тип товара': {'default_value': 'Аккумулятор'}},
             {'Бренд': {_FIELD: 'manufacturer_name'}},
             {'Номенклатура': {_FIELD: 'title'}},
-            {'Цена': {_FIELD: 'sale_price', 'format': '@'}},
+            {'Цена': {_FIELD: 'sale_price', 'XXformatXX': '@'}},
             {'Остаток': {_FIELD: 'rest_count'}},
             {'Наличие': {'default_value': 'В наличии'}},
             {'Состояние': {'default_value': 'Новое'}},
```

### `parsers.writer.templates.group_templates.x__drom_batteries__mutmut_33`

Статус: **survived**; тип: `string_case`; выбрано тестов: 27.

```diff
--- src/parsers/writer/templates/group_templates.py
+++ src/parsers/writer/templates/group_templates.py
@@ -6,7 +6,7 @@
             {'Тип товара': {'default_value': 'Аккумулятор'}},
             {'Бренд': {_FIELD: 'manufacturer_name'}},
             {'Номенклатура': {_FIELD: 'title'}},
-            {'Цена': {_FIELD: 'sale_price', 'format': '@'}},
+            {'Цена': {_FIELD: 'sale_price', 'FORMAT': '@'}},
             {'Остаток': {_FIELD: 'rest_count'}},
             {'Наличие': {'default_value': 'В наличии'}},
             {'Состояние': {'default_value': 'Новое'}},
```

### `parsers.writer.templates.group_templates.x__drom_batteries__mutmut_34`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 27.

```diff
--- src/parsers/writer/templates/group_templates.py
+++ src/parsers/writer/templates/group_templates.py
@@ -6,7 +6,7 @@
             {'Тип товара': {'default_value': 'Аккумулятор'}},
             {'Бренд': {_FIELD: 'manufacturer_name'}},
             {'Номенклатура': {_FIELD: 'title'}},
-            {'Цена': {_FIELD: 'sale_price', 'format': '@'}},
+            {'Цена': {_FIELD: 'sale_price', 'format': 'XX@XX'}},
             {'Остаток': {_FIELD: 'rest_count'}},
             {'Наличие': {'default_value': 'В наличии'}},
             {'Состояние': {'default_value': 'Новое'}},
```

### `parsers.writer.templates.group_templates.x__drom_batteries__mutmut_43`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 27.

```diff
--- src/parsers/writer/templates/group_templates.py
+++ src/parsers/writer/templates/group_templates.py
@@ -8,7 +8,7 @@
             {'Номенклатура': {_FIELD: 'title'}},
             {'Цена': {_FIELD: 'sale_price', 'format': '@'}},
             {'Остаток': {_FIELD: 'rest_count'}},
-            {'Наличие': {'default_value': 'В наличии'}},
+            {'Наличие': {'XXdefault_valueXX': 'В наличии'}},
             {'Состояние': {'default_value': 'Новое'}},
             {'Ёмкость, А·ч': {_FIELD: 'capacity_ah'}},
             {'Пусковой ток, А': {_FIELD: 'starting_current_a'}},
```

### `parsers.writer.templates.group_templates.x__drom_batteries__mutmut_44`

Статус: **survived**; тип: `string_case`; выбрано тестов: 27.

```diff
--- src/parsers/writer/templates/group_templates.py
+++ src/parsers/writer/templates/group_templates.py
@@ -8,7 +8,7 @@
             {'Номенклатура': {_FIELD: 'title'}},
             {'Цена': {_FIELD: 'sale_price', 'format': '@'}},
             {'Остаток': {_FIELD: 'rest_count'}},
-            {'Наличие': {'default_value': 'В наличии'}},
+            {'Наличие': {'DEFAULT_VALUE': 'В наличии'}},
             {'Состояние': {'default_value': 'Новое'}},
             {'Ёмкость, А·ч': {_FIELD: 'capacity_ah'}},
             {'Пусковой ток, А': {_FIELD: 'starting_current_a'}},
```

### `parsers.writer.templates.group_templates.x__drom_batteries__mutmut_45`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 27.

```diff
--- src/parsers/writer/templates/group_templates.py
+++ src/parsers/writer/templates/group_templates.py
@@ -8,7 +8,7 @@
             {'Номенклатура': {_FIELD: 'title'}},
             {'Цена': {_FIELD: 'sale_price', 'format': '@'}},
             {'Остаток': {_FIELD: 'rest_count'}},
-            {'Наличие': {'default_value': 'В наличии'}},
+            {'Наличие': {'default_value': 'XXВ наличииXX'}},
             {'Состояние': {'default_value': 'Новое'}},
             {'Ёмкость, А·ч': {_FIELD: 'capacity_ah'}},
             {'Пусковой ток, А': {_FIELD: 'starting_current_a'}},
```

### `parsers.writer.templates.group_templates.x__drom_batteries__mutmut_46`

Статус: **survived**; тип: `string_case`; выбрано тестов: 27.

```diff
--- src/parsers/writer/templates/group_templates.py
+++ src/parsers/writer/templates/group_templates.py
@@ -8,7 +8,7 @@
             {'Номенклатура': {_FIELD: 'title'}},
             {'Цена': {_FIELD: 'sale_price', 'format': '@'}},
             {'Остаток': {_FIELD: 'rest_count'}},
-            {'Наличие': {'default_value': 'В наличии'}},
+            {'Наличие': {'default_value': 'в наличии'}},
             {'Состояние': {'default_value': 'Новое'}},
             {'Ёмкость, А·ч': {_FIELD: 'capacity_ah'}},
             {'Пусковой ток, А': {_FIELD: 'starting_current_a'}},
```

### `parsers.writer.templates.group_templates.x__drom_batteries__mutmut_47`

Статус: **survived**; тип: `string_case`; выбрано тестов: 27.

```diff
--- src/parsers/writer/templates/group_templates.py
+++ src/parsers/writer/templates/group_templates.py
@@ -8,7 +8,7 @@
             {'Номенклатура': {_FIELD: 'title'}},
             {'Цена': {_FIELD: 'sale_price', 'format': '@'}},
             {'Остаток': {_FIELD: 'rest_count'}},
-            {'Наличие': {'default_value': 'В наличии'}},
+            {'Наличие': {'default_value': 'В НАЛИЧИИ'}},
             {'Состояние': {'default_value': 'Новое'}},
             {'Ёмкость, А·ч': {_FIELD: 'capacity_ah'}},
             {'Пусковой ток, А': {_FIELD: 'starting_current_a'}},
```

### `parsers.writer.templates.group_templates.x__drom_batteries__mutmut_51`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 27.

```diff
--- src/parsers/writer/templates/group_templates.py
+++ src/parsers/writer/templates/group_templates.py
@@ -9,7 +9,7 @@
             {'Цена': {_FIELD: 'sale_price', 'format': '@'}},
             {'Остаток': {_FIELD: 'rest_count'}},
             {'Наличие': {'default_value': 'В наличии'}},
-            {'Состояние': {'default_value': 'Новое'}},
+            {'Состояние': {'XXdefault_valueXX': 'Новое'}},
             {'Ёмкость, А·ч': {_FIELD: 'capacity_ah'}},
             {'Пусковой ток, А': {_FIELD: 'starting_current_a'}},
             {'Длина, мм': {_FIELD: 'length_mm'}},
```

### `parsers.writer.templates.group_templates.x__drom_batteries__mutmut_52`

Статус: **survived**; тип: `string_case`; выбрано тестов: 27.

```diff
--- src/parsers/writer/templates/group_templates.py
+++ src/parsers/writer/templates/group_templates.py
@@ -9,7 +9,7 @@
             {'Цена': {_FIELD: 'sale_price', 'format': '@'}},
             {'Остаток': {_FIELD: 'rest_count'}},
             {'Наличие': {'default_value': 'В наличии'}},
-            {'Состояние': {'default_value': 'Новое'}},
+            {'Состояние': {'DEFAULT_VALUE': 'Новое'}},
             {'Ёмкость, А·ч': {_FIELD: 'capacity_ah'}},
             {'Пусковой ток, А': {_FIELD: 'starting_current_a'}},
             {'Длина, мм': {_FIELD: 'length_mm'}},
```

### `parsers.writer.templates.group_templates.x__drom_batteries__mutmut_53`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 27.

```diff
--- src/parsers/writer/templates/group_templates.py
+++ src/parsers/writer/templates/group_templates.py
@@ -9,7 +9,7 @@
             {'Цена': {_FIELD: 'sale_price', 'format': '@'}},
             {'Остаток': {_FIELD: 'rest_count'}},
             {'Наличие': {'default_value': 'В наличии'}},
-            {'Состояние': {'default_value': 'Новое'}},
+            {'Состояние': {'default_value': 'XXНовоеXX'}},
             {'Ёмкость, А·ч': {_FIELD: 'capacity_ah'}},
             {'Пусковой ток, А': {_FIELD: 'starting_current_a'}},
             {'Длина, мм': {_FIELD: 'length_mm'}},
```

### `parsers.writer.templates.group_templates.x__drom_batteries__mutmut_54`

Статус: **survived**; тип: `string_case`; выбрано тестов: 27.

```diff
--- src/parsers/writer/templates/group_templates.py
+++ src/parsers/writer/templates/group_templates.py
@@ -9,7 +9,7 @@
             {'Цена': {_FIELD: 'sale_price', 'format': '@'}},
             {'Остаток': {_FIELD: 'rest_count'}},
             {'Наличие': {'default_value': 'В наличии'}},
-            {'Состояние': {'default_value': 'Новое'}},
+            {'Состояние': {'default_value': 'новое'}},
             {'Ёмкость, А·ч': {_FIELD: 'capacity_ah'}},
             {'Пусковой ток, А': {_FIELD: 'starting_current_a'}},
             {'Длина, мм': {_FIELD: 'length_mm'}},
```

### `parsers.writer.templates.group_templates.x__drom_batteries__mutmut_55`

Статус: **survived**; тип: `string_case`; выбрано тестов: 27.

```diff
--- src/parsers/writer/templates/group_templates.py
+++ src/parsers/writer/templates/group_templates.py
@@ -9,7 +9,7 @@
             {'Цена': {_FIELD: 'sale_price', 'format': '@'}},
             {'Остаток': {_FIELD: 'rest_count'}},
             {'Наличие': {'default_value': 'В наличии'}},
-            {'Состояние': {'default_value': 'Новое'}},
+            {'Состояние': {'default_value': 'НОВОЕ'}},
             {'Ёмкость, А·ч': {_FIELD: 'capacity_ah'}},
             {'Пусковой ток, А': {_FIELD: 'starting_current_a'}},
             {'Длина, мм': {_FIELD: 'length_mm'}},
```

### `parsers.writer.templates.group_templates.x__drom_batteries__mutmut_121`

Статус: **survived**; тип: `string_wrap`; выбрано тестов: 27.

```diff
--- src/parsers/writer/templates/group_templates.py
+++ src/parsers/writer/templates/group_templates.py
@@ -24,6 +24,6 @@
             {'EFB': {_FIELD: 'efb'}},
             {'AGM': {_FIELD: 'agm'}},
         ],
-        filters={'rest_count': [None, '']},
+        filters={'rest_count': [None, 'XXXX']},
         file_name='price_drom_akb_{now}.xlsx',
     )
```

## src/parsers/writer/xls_writer.py

### `parsers.writer.xls_writer.xǁXlsWriterǁwrite_sheet__mutmut_18`

Статус: **survived**; тип: `other`; выбрано тестов: 62.

```diff
--- src/parsers/writer/xls_writer.py
+++ src/parsers/writer/xls_writer.py
@@ -5,6 +5,6 @@
         legend = self.template.colors().get('legend') or []
         offset = write_legend(self.driver, legend)
         helpers = [ColumnHelper(col) for col in self.template.columns()]
-        self.driver.write_head([col.name for col in helpers], offset)
+        self.driver.write_head([col.name for col in helpers], )
         for row_index, product in enumerate(make_exclude(self.parse_result, self.exclude), start=offset):
             self._write_row(product, row_index, helpers, self._get_color(product))
```

### `parsers.writer.xls_writer.x__to_str__mutmut_2`

Статус: **survived**; тип: `other`; выбрано тестов: 143.

```diff
--- src/parsers/writer/xls_writer.py
+++ src/parsers/writer/xls_writer.py
@@ -1,7 +1,7 @@
 def _to_str(raw_value: CellValue | list[str]) -> CellValue:
     """Список — через запятую, логическое значение — «Да» или пусто, остальные скаляры — без изменений."""
     if isinstance(raw_value, bool):
-        return 'Да' if raw_value else None
+        return 'Да' if (raw_value) or True else None
     if isinstance(raw_value, list):
         filtered_items = [element for element in raw_value if element]
         return ', '.join(filtered_items)
```

### `parsers.writer.xls_writer.x_cell_value__mutmut_4`

Статус: **survived**; тип: `other`; выбрано тестов: 143.

```diff
--- src/parsers/writer/xls_writer.py
+++ src/parsers/writer/xls_writer.py
@@ -4,7 +4,7 @@
         return None
 
     field_name = col.field
-    raw_value = row_item.get(field_name) if field_name else None
+    raw_value = row_item.get(field_name) if (field_name) or True else None
     if raw_value is True and col.true_value:
         raw_value = col.true_value
     raw_value = raw_value or col.def_value
```

## src/parsers/writer/xlsxwriter_adapter.py

### `parsers.writer.xlsxwriter_adapter.xǁXlsxWriterAdapterǁ__init____mutmut_4`

Классификация 2026-11-14: Эквивалент для публичного жизненного цикла драйвера: _columns безусловно заменяется пустым словарём в add_sheet перед использованием. До add_sheet write/set_column_format поднимают WorksheetNotInitializedError; начальное значение не читается. R17 и R18: survived.

Статус: **survived**; тип: `to_none`; выбрано тестов: 43.

```diff
--- src/parsers/writer/xlsxwriter_adapter.py
+++ src/parsers/writer/xlsxwriter_adapter.py
@@ -2,5 +2,5 @@
         self._book: Workbook | None = None
         self._sheet: Worksheet | None = None
         self._formats: dict[tuple[str, str, bool], Format] = {}
-        self._columns: dict[int, str] = {}
+        self._columns: dict[int, str] = None
         self._widths: dict[int, int] = {}
```

### `parsers.writer.xlsxwriter_adapter.xǁXlsxWriterAdapterǁ__init____mutmut_5`

Классификация 2026-11-14: Эквивалент для публичного жизненного цикла драйвера: _widths безусловно заменяется пустым словарём в add_sheet перед использованием. До add_sheet write/set_column_format поднимают WorksheetNotInitializedError; начальное значение не читается. R17 и R18: survived.

Статус: **survived**; тип: `to_none`; выбрано тестов: 43.

```diff
--- src/parsers/writer/xlsxwriter_adapter.py
+++ src/parsers/writer/xlsxwriter_adapter.py
@@ -3,4 +3,4 @@
         self._sheet: Worksheet | None = None
         self._formats: dict[tuple[str, str, bool], Format] = {}
         self._columns: dict[int, str] = {}
-        self._widths: dict[int, int] = {}
+        self._widths: dict[int, int] = None
```

### `parsers.writer.xlsxwriter_adapter.xǁXlsxWriterAdapterǁset_column_format__mutmut_1`

Классификация 2026-11-14: Закрытый пробел проверки: Открытая книга без выбранного листа — допустимое промежуточное состояние публичного API. Замена or на and пропускает проверку и даёт AttributeError вместо WorksheetNotInitializedError. R17: survived на прежних тестах; R18: killed после усиления, падает `tests/test_parsers/test_writer/test_xlsxwriter_adapter.py::test_operations_require_sheet_after_workbook_init[set_column_format-args1]`. Исторический diff применён с единственным точным совпадением полного контекста; номер новой генерации не использовался.

Статус: **survived**; тип: `operator`; выбрано тестов: 37.

```diff
--- src/parsers/writer/xlsxwriter_adapter.py
+++ src/parsers/writer/xlsxwriter_adapter.py
@@ -1,6 +1,6 @@
     def set_column_format(self, column_format: dict[int, str]) -> None:
         """Индексы колонок в шаблонах начинаются с единицы."""
-        if self._sheet is None or self._book is None:
+        if self._sheet is None and self._book is None:
             raise WorksheetNotInitializedError()
         self._columns.update(column_format)
         for index, number_format in column_format.items():
```

### `parsers.writer.xlsxwriter_adapter.xǁXlsxWriterAdapterǁset_column_format__mutmut_6`

Классификация 2026-11-14: Закрытый пробел проверки: Формат пустой колонки наблюдаем в сохранённом XLSX и не перезаписывается явным форматом ячейки, когда ячеек нет. Проверены форматы колонок A и C; смещение индекса, удаление формата и замена number_format на None различимы. R17: survived на прежних тестах; R18: killed после усиления, падает `tests/test_parsers/test_writer/test_xlsxwriter_adapter.py::test_column_formats_are_saved_without_cells`. Исторический diff применён с единственным точным совпадением полного контекста; номер новой генерации не использовался.

Статус: **survived**; тип: `operator`; выбрано тестов: 37.

```diff
--- src/parsers/writer/xlsxwriter_adapter.py
+++ src/parsers/writer/xlsxwriter_adapter.py
@@ -4,6 +4,6 @@
             raise WorksheetNotInitializedError()
         self._columns.update(column_format)
         for index, number_format in column_format.items():
-            col = index - 1
+            col = index + 1
             cell_format = _cell_format(self._book, self._formats, number_format)
             self._sheet.set_column(col, col, None, cell_format)
```

### `parsers.writer.xlsxwriter_adapter.xǁXlsxWriterAdapterǁset_column_format__mutmut_7`

Классификация 2026-11-14: Закрытый пробел проверки: Формат пустой колонки наблюдаем в сохранённом XLSX и не перезаписывается явным форматом ячейки, когда ячеек нет. Проверены форматы колонок A и C; смещение индекса, удаление формата и замена number_format на None различимы. R17: survived на прежних тестах; R18: killed после усиления, падает `tests/test_parsers/test_writer/test_xlsxwriter_adapter.py::test_column_formats_are_saved_without_cells`. Исторический diff применён с единственным точным совпадением полного контекста; номер новой генерации не использовался.

Статус: **survived**; тип: `number`; выбрано тестов: 37.

```diff
--- src/parsers/writer/xlsxwriter_adapter.py
+++ src/parsers/writer/xlsxwriter_adapter.py
@@ -4,6 +4,6 @@
             raise WorksheetNotInitializedError()
         self._columns.update(column_format)
         for index, number_format in column_format.items():
-            col = index - 1
+            col = index - 2
             cell_format = _cell_format(self._book, self._formats, number_format)
             self._sheet.set_column(col, col, None, cell_format)
```

### `parsers.writer.xlsxwriter_adapter.xǁXlsxWriterAdapterǁset_column_format__mutmut_8`

Классификация 2026-11-14: Закрытый пробел проверки: Формат пустой колонки наблюдаем в сохранённом XLSX и не перезаписывается явным форматом ячейки, когда ячеек нет. Проверены форматы колонок A и C; смещение индекса, удаление формата и замена number_format на None различимы. R17: survived на прежних тестах; R18: killed после усиления, падает `tests/test_parsers/test_writer/test_xlsxwriter_adapter.py::test_column_formats_are_saved_without_cells`. Исторический diff применён с единственным точным совпадением полного контекста; номер новой генерации не использовался.

Статус: **survived**; тип: `to_none`; выбрано тестов: 37.

```diff
--- src/parsers/writer/xlsxwriter_adapter.py
+++ src/parsers/writer/xlsxwriter_adapter.py
@@ -5,5 +5,5 @@
         self._columns.update(column_format)
         for index, number_format in column_format.items():
             col = index - 1
-            cell_format = _cell_format(self._book, self._formats, number_format)
+            cell_format = None
             self._sheet.set_column(col, col, None, cell_format)
```

### `parsers.writer.xlsxwriter_adapter.xǁXlsxWriterAdapterǁset_column_format__mutmut_11`

Классификация 2026-11-14: Закрытый пробел проверки: Формат пустой колонки наблюдаем в сохранённом XLSX и не перезаписывается явным форматом ячейки, когда ячеек нет. Проверены форматы колонок A и C; удаление формата и замена number_format на None различимы. R17: survived на прежних тестах; R18: killed после усиления, падает `tests/test_parsers/test_writer/test_xlsxwriter_adapter.py::test_column_formats_are_saved_without_cells`. Исторический diff применён с единственным точным совпадением полного контекста; номер новой генерации не использовался.

Статус: **survived**; тип: `to_none`; выбрано тестов: 37.

```diff
--- src/parsers/writer/xlsxwriter_adapter.py
+++ src/parsers/writer/xlsxwriter_adapter.py
@@ -5,5 +5,5 @@
         self._columns.update(column_format)
         for index, number_format in column_format.items():
             col = index - 1
-            cell_format = _cell_format(self._book, self._formats, number_format)
+            cell_format = _cell_format(self._book, self._formats, None)
             self._sheet.set_column(col, col, None, cell_format)
```

### `parsers.writer.xlsxwriter_adapter.xǁXlsxWriterAdapterǁset_column_format__mutmut_17`

Классификация 2026-11-14: Закрытый пробел проверки: Формат пустой колонки наблюдаем в сохранённом XLSX и не перезаписывается явным форматом ячейки, когда ячеек нет. Проверены форматы колонок A и C; удаление формата и замена number_format на None различимы. R17: survived на прежних тестах; R18: killed после усиления, падает `tests/test_parsers/test_writer/test_xlsxwriter_adapter.py::test_column_formats_are_saved_without_cells`. Исторический diff применён с единственным точным совпадением полного контекста; номер новой генерации не использовался.

Статус: **survived**; тип: `to_none`; выбрано тестов: 37.

```diff
--- src/parsers/writer/xlsxwriter_adapter.py
+++ src/parsers/writer/xlsxwriter_adapter.py
@@ -6,4 +6,4 @@
         for index, number_format in column_format.items():
             col = index - 1
             cell_format = _cell_format(self._book, self._formats, number_format)
-            self._sheet.set_column(col, col, None, cell_format)
+            self._sheet.set_column(col, col, None, None)
```

### `parsers.writer.xlsxwriter_adapter.xǁXlsxWriterAdapterǁset_column_format__mutmut_21`

Классификация 2026-11-14: Закрытый пробел проверки: Формат пустой колонки наблюдаем в сохранённом XLSX и не перезаписывается явным форматом ячейки, когда ячеек нет. Проверены форматы колонок A и C; смещение индекса, удаление формата и замена number_format на None различимы. R17: survived на прежних тестах; R18: killed после усиления, падает `tests/test_parsers/test_writer/test_xlsxwriter_adapter.py::test_column_formats_are_saved_without_cells`. Исторический diff применён с единственным точным совпадением полного контекста; номер новой генерации не использовался.

Статус: **survived**; тип: `other`; выбрано тестов: 37.

```diff
--- src/parsers/writer/xlsxwriter_adapter.py
+++ src/parsers/writer/xlsxwriter_adapter.py
@@ -6,4 +6,4 @@
         for index, number_format in column_format.items():
             col = index - 1
             cell_format = _cell_format(self._book, self._formats, number_format)
-            self._sheet.set_column(col, col, None, cell_format)
+            self._sheet.set_column(col, col, None, )
```

### `parsers.writer.xlsxwriter_adapter.xǁXlsxWriterAdapterǁwrite__mutmut_1`

Классификация 2026-11-14: Закрытый пробел проверки: Открытая книга без выбранного листа — допустимое промежуточное состояние публичного API. Замена or на and пропускает проверку и даёт AttributeError вместо WorksheetNotInitializedError. R17: survived на прежних тестах; R18: killed после усиления, падает `tests/test_parsers/test_writer/test_xlsxwriter_adapter.py::test_operations_require_sheet_after_workbook_init[write-args0]`. Исторический diff применён с единственным точным совпадением полного контекста; номер новой генерации не использовался.

Статус: **survived**; тип: `operator`; выбрано тестов: 39.

```diff
--- src/parsers/writer/xlsxwriter_adapter.py
+++ src/parsers/writer/xlsxwriter_adapter.py
@@ -7,7 +7,7 @@
         _color: str | None = None,
     ) -> None:
         """Записать ячейку, сохранив числовой формат под заливкой."""
-        if self._sheet is None or self._book is None:
+        if self._sheet is None and self._book is None:
             raise WorksheetNotInitializedError()
         number_format = self._columns.get(col_idx + 1, 'General')
         bold = bool(style)
```

### `parsers.writer.xlsxwriter_adapter.x__update_width__mutmut_1`

Классификация 2026-11-14: Разбор не завершён: прежнее общее объяснение эквивалентности отозвано. R17 и R18: survived. R19 с точным историческим diff обнаружил публичную последовательность init_workbook → add_sheet → write(0, 0, 'x') → set_column_format({1: '@'}) → write(1, 0, 'y') → save: ширина A в исходном XLSX 9.140625, в мутанте 5.0. Причина: set_column_format сбрасывает фактическую ширину через set_column(..., None, ...), но оставляет прежний _widths; при равной длине исходный код пропускает обновление, мутант повторяет его. Это различимый публичный вход, а не доказанный эквивалент. Требуется определить контракт изменения форматов после записи; тест под текущее расхождение не добавлен, код приложения не менялся.

Статус: **survived**; тип: `operator`; выбрано тестов: 37.

```diff
--- src/parsers/writer/xlsxwriter_adapter.py
+++ src/parsers/writer/xlsxwriter_adapter.py
@@ -6,7 +6,7 @@
     cell_format: Format,
 ) -> None:
     """Компенсировать добавляемый XlsxWriter отступ, сохранив прежнюю ширину."""
-    if length <= widths.get(column, -1):
+    if length < widths.get(column, -1):
         return
     widths[column] = length
     width = length + _WIDTH_PADDING - _COLUMN_PADDING_PIXELS / _CHAR_PIXELS
```

### `parsers.writer.xlsxwriter_adapter.x__update_width__mutmut_6`

Классификация 2026-11-14: Закрытый пробел проверки: Для первой ячейки длины 0 или 1 дефолт +1 пропускает установку ширины. Исходный XLSX сохраняет ширину 4 или 5, мутант оставляет ширину Excel по умолчанию. Проверены строка из одного символа, пустая строка, None и 0. R17: survived на прежних тестах; R18: killed после усиления, падает `tests/test_parsers/test_writer/test_xlsxwriter_adapter.py::test_short_values_set_column_width[-4]`. Исторический diff применён с единственным точным совпадением полного контекста; номер новой генерации не использовался.

Статус: **survived**; тип: `operator`; выбрано тестов: 37.

```diff
--- src/parsers/writer/xlsxwriter_adapter.py
+++ src/parsers/writer/xlsxwriter_adapter.py
@@ -6,7 +6,7 @@
     cell_format: Format,
 ) -> None:
     """Компенсировать добавляемый XlsxWriter отступ, сохранив прежнюю ширину."""
-    if length <= widths.get(column, -1):
+    if length <= widths.get(column, +1):
         return
     widths[column] = length
     width = length + _WIDTH_PADDING - _COLUMN_PADDING_PIXELS / _CHAR_PIXELS
```

### `parsers.writer.xlsxwriter_adapter.x__update_width__mutmut_7`

Классификация 2026-11-14: Эквивалент: length = len(str(cell_content or '')) всегда неотрицателен. При первом обращении к колонке сравнение с -1 и -2 одинаково ложно; после первого присваивания widths[column] дефолт больше не используется до add_sheet, который сбрасывает весь словарь. R17 и R18: survived.

Статус: **survived**; тип: `number`; выбрано тестов: 37.

```diff
--- src/parsers/writer/xlsxwriter_adapter.py
+++ src/parsers/writer/xlsxwriter_adapter.py
@@ -6,7 +6,7 @@
     cell_format: Format,
 ) -> None:
     """Компенсировать добавляемый XlsxWriter отступ, сохранив прежнюю ширину."""
-    if length <= widths.get(column, -1):
+    if length <= widths.get(column, -2):
         return
     widths[column] = length
     width = length + _WIDTH_PADDING - _COLUMN_PADDING_PIXELS / _CHAR_PIXELS
```

## src/parsers/xls_reader.py

### `parsers.xls_reader.xǁXlsReaderǁnext_row_values__mutmut_10`

Статус: **survived**; тип: `operator`; выбрано тестов: 16.

```diff
--- src/parsers/xls_reader.py
+++ src/parsers/xls_reader.py
@@ -4,7 +4,7 @@
             return False
 
         cols = sheet_cols(sheet)
-        end_col = cols if cols <= self.reader_params.max_columns else self.reader_params.max_columns
+        end_col = cols if cols < self.reader_params.max_columns else self.reader_params.max_columns
         cur_row = self.cur_row
         self.cur_row += 1
 
```

### `parsers.xls_reader.xǁXlsReaderǁnext_row_values__mutmut_32`

Статус: **survived**; тип: `other`; выбрано тестов: 16.

```diff
--- src/parsers/xls_reader.py
+++ src/parsers/xls_reader.py
@@ -19,6 +19,6 @@
 
         if is_empty_row(self.cur_row_values):
             self.skipped_empty_rows += 1
-            return not is_end_row(self.cur_row_values, self.skipped_empty_rows)
+            return not is_end_row(None, self.skipped_empty_rows)
 
         return self.cur_row_values
```

### `parsers.xls_reader.xǁXlsReaderǁsheets__mutmut_1`

Статус: **survived**; тип: `to_none`; выбрано тестов: 1.

```diff
--- src/parsers/xls_reader.py
+++ src/parsers/xls_reader.py
@@ -1,3 +1,3 @@
     def sheets(self) -> list[Sheet]:
         """get sheet list"""
-        return [self._load_sheet(s_name) for s_name in self._sheet_names()]
+        return [self._load_sheet(None) for s_name in self._sheet_names()]
```

### `parsers.xls_reader.x__raw_table__mutmut_3`

Статус: **survived**; тип: `operator`; выбрано тестов: 5.

```diff
--- src/parsers/xls_reader.py
+++ src/parsers/xls_reader.py
@@ -1,6 +1,6 @@
 def _raw_table(reader: XlsReader, sheet_index: int, sheet_name: str) -> RawTable:
     sheet = reader._load_sheet(sheet_name)
-    if len(sheet) > reader.reader_params.max_rows:
+    if len(sheet) >= reader.reader_params.max_rows:
         raise MaxRowsReachedError(reader.reader_params.max_rows)
     end_col = min(sheet_cols(sheet), reader.reader_params.max_columns) if sheet else 0
     rows = []
```

### `parsers.xls_reader.x__raw_table__mutmut_4`

Статус: **survived**; тип: `to_none`; выбрано тестов: 5.

```diff
--- src/parsers/xls_reader.py
+++ src/parsers/xls_reader.py
@@ -2,7 +2,7 @@
     sheet = reader._load_sheet(sheet_name)
     if len(sheet) > reader.reader_params.max_rows:
         raise MaxRowsReachedError(reader.reader_params.max_rows)
-    end_col = min(sheet_cols(sheet), reader.reader_params.max_columns) if sheet else 0
+    end_col = None
     rows = []
     for row_number, source_row in enumerate(sheet, start=1):
         rows.append(_raw_row(source_row[:end_col], row_number))
```

### `parsers.xls_reader.x__raw_table__mutmut_6`

Статус: **survived**; тип: `other`; выбрано тестов: 5.

```diff
--- src/parsers/xls_reader.py
+++ src/parsers/xls_reader.py
@@ -2,7 +2,7 @@
     sheet = reader._load_sheet(sheet_name)
     if len(sheet) > reader.reader_params.max_rows:
         raise MaxRowsReachedError(reader.reader_params.max_rows)
-    end_col = min(sheet_cols(sheet), reader.reader_params.max_columns) if sheet else 0
+    end_col = min(sheet_cols(sheet), reader.reader_params.max_columns) if (sheet) or True else 0
     rows = []
     for row_number, source_row in enumerate(sheet, start=1):
         rows.append(_raw_row(source_row[:end_col], row_number))
```

### `parsers.xls_reader.x__raw_table__mutmut_12`

Статус: **survived**; тип: `number`; выбрано тестов: 5.

```diff
--- src/parsers/xls_reader.py
+++ src/parsers/xls_reader.py
@@ -2,7 +2,7 @@
     sheet = reader._load_sheet(sheet_name)
     if len(sheet) > reader.reader_params.max_rows:
         raise MaxRowsReachedError(reader.reader_params.max_rows)
-    end_col = min(sheet_cols(sheet), reader.reader_params.max_columns) if sheet else 0
+    end_col = min(sheet_cols(sheet), reader.reader_params.max_columns) if sheet else 1
     rows = []
     for row_number, source_row in enumerate(sheet, start=1):
         rows.append(_raw_row(source_row[:end_col], row_number))
```

## src/services/doubles_service.py

### `services.doubles_service.xǁDoublesServiceǁmake_report__mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: test_make_report_passes_selection проверяет передачу того же объекта ParseSelection оркестратору; безусловная ветка parse_all() теряет этот аргумент. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 5.

```diff
--- src/services/doubles_service.py
+++ src/services/doubles_service.py
@@ -1,7 +1,7 @@
     def make_report(self, *, as_jsonl: bool = False, selection: ParseSelection | None = None) -> DoublesReport:
         """Разобрать всех поставщиков и записать отчёт о дублях."""
         parse_result = (
-            self._orchestrator.parse_all() if selection is None else self._orchestrator.parse_all(selection=selection)
+            self._orchestrator.parse_all() if (selection is None) or True else self._orchestrator.parse_all(selection=selection)
         )
         if not parse_result.groups:
             return DoublesReport(parse_result=parse_result, doubles=[], path=None)
```

### `services.doubles_service.xǁDoublesServiceǁmake_report__mutmut_6`

Классификация 2026-11-14: Закрытый пробел проверки: test_make_report_passes_selection проверяет передачу того же объекта ParseSelection; подмена selection на None нарушает вызов оркестратора. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 5.

```diff
--- src/services/doubles_service.py
+++ src/services/doubles_service.py
@@ -1,7 +1,7 @@
     def make_report(self, *, as_jsonl: bool = False, selection: ParseSelection | None = None) -> DoublesReport:
         """Разобрать всех поставщиков и записать отчёт о дублях."""
         parse_result = (
-            self._orchestrator.parse_all() if selection is None else self._orchestrator.parse_all(selection=selection)
+            self._orchestrator.parse_all() if selection is None else self._orchestrator.parse_all(selection=None)
         )
         if not parse_result.groups:
             return DoublesReport(parse_result=parse_result, doubles=[], path=None)
```

### `services.doubles_service.xǁDoublesServiceǁmake_report__mutmut_8`

Классификация 2026-11-14: Закрытый пробел проверки: test_make_report_without_selected_groups_creates_no_file теперь проверяет идентичность report.parse_result результату оркестратора даже при отсутствии выбранных групп. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 5.

```diff
--- src/services/doubles_service.py
+++ src/services/doubles_service.py
@@ -4,7 +4,7 @@
             self._orchestrator.parse_all() if selection is None else self._orchestrator.parse_all(selection=selection)
         )
         if not parse_result.groups:
-            return DoublesReport(parse_result=parse_result, doubles=[], path=None)
+            return DoublesReport(parse_result=None, doubles=[], path=None)
         doubles = [
             row for row in parse_result.tire_and_disk_items if row.duplicate.is_double or row.duplicate.double_candidate
         ]
```

### `services.doubles_service.xǁDoublesServiceǁmake_report__mutmut_26`

Классификация 2026-11-14: Закрытый пробел проверки: test_make_report_without_output_files задаёт выбранный пустой шинный пакет и writer с результатом []; путь должен оставаться None. Безусловное files[0] вызывает IndexError. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 5.

```diff
--- src/services/doubles_service.py
+++ src/services/doubles_service.py
@@ -9,5 +9,5 @@
             row for row in parse_result.tire_and_disk_items if row.duplicate.is_double or row.duplicate.double_candidate
         ]
         files = self._report_service.write_result(parse_result, template='for_doubles', as_jsonl=as_jsonl)
-        path = files[0] if files else None
+        path = files[0] if (files) or True else None
         return DoublesReport(parse_result=parse_result, doubles=doubles, path=path, files=files)
```

## src/services/four_tochki_service.py

### `services.four_tochki_service.xǁFourTochkiServiceǁ__init____mutmut_1`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R6: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 3.

```diff
--- src/services/four_tochki_service.py
+++ src/services/four_tochki_service.py
@@ -1,2 +1,2 @@
     def __init__(self, config_provider: ConfigProvider | None = None) -> None:
-        self._config_provider = config_provider
+        self._config_provider = None
```

### `services.four_tochki_service.xǁFourTochkiServiceǁupload_data__mutmut_1`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R6: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 2.

```diff
--- src/services/four_tochki_service.py
+++ src/services/four_tochki_service.py
@@ -1,6 +1,6 @@
     def upload_data(self) -> bool:
         """Загрузить удалённые данные в file_prices/four_tochki; вернуть False, если поставщик отключён."""
-        provider = self._config_provider or get_config_provider()
+        provider = None
         if skip_disabled_upload(_VENDOR_FOLDER, provider):
             return False
         load_remote_vendor_data(api=get_four_tochki_api_config(), groups=load_four_tochki_warehouse_groups(provider))
```

### `services.four_tochki_service.xǁFourTochkiServiceǁupload_data__mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R6: killed. Исторический survived сохранён.

Статус: **survived**; тип: `operator`; выбрано тестов: 2.

```diff
--- src/services/four_tochki_service.py
+++ src/services/four_tochki_service.py
@@ -1,6 +1,6 @@
     def upload_data(self) -> bool:
         """Загрузить удалённые данные в file_prices/four_tochki; вернуть False, если поставщик отключён."""
-        provider = self._config_provider or get_config_provider()
+        provider = self._config_provider and get_config_provider()
         if skip_disabled_upload(_VENDOR_FOLDER, provider):
             return False
         load_remote_vendor_data(api=get_four_tochki_api_config(), groups=load_four_tochki_warehouse_groups(provider))
```

### `services.four_tochki_service.xǁFourTochkiServiceǁupload_data__mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R6: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 2.

```diff
--- src/services/four_tochki_service.py
+++ src/services/four_tochki_service.py
@@ -1,7 +1,7 @@
     def upload_data(self) -> bool:
         """Загрузить удалённые данные в file_prices/four_tochki; вернуть False, если поставщик отключён."""
         provider = self._config_provider or get_config_provider()
-        if skip_disabled_upload(_VENDOR_FOLDER, provider):
+        if skip_disabled_upload(_VENDOR_FOLDER, None):
             return False
         load_remote_vendor_data(api=get_four_tochki_api_config(), groups=load_four_tochki_warehouse_groups(provider))
         return True
```

### `services.four_tochki_service.xǁFourTochkiServiceǁupload_data__mutmut_12`

Классификация 2026-11-14: Закрытый пробел проверки: В test_upload_four_tochki_data проверяется передача явного FakeConfigProvider в load_four_tochki_warehouse_groups; прежний постоянный return_value скрывал потерю аргумента. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R6: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 2.

```diff
--- src/services/four_tochki_service.py
+++ src/services/four_tochki_service.py
@@ -3,5 +3,5 @@
         provider = self._config_provider or get_config_provider()
         if skip_disabled_upload(_VENDOR_FOLDER, provider):
             return False
-        load_remote_vendor_data(api=get_four_tochki_api_config(), groups=load_four_tochki_warehouse_groups(provider))
+        load_remote_vendor_data(api=get_four_tochki_api_config(), groups=load_four_tochki_warehouse_groups(None))
         return True
```

### `services.four_tochki_service.x_load_remote_vendor_data__mutmut_6`

Классификация 2026-11-14: Закрытый пробел проверки: В test_four_tochki_load_selects_warehouses_and_downloads_to_price_folder проверяется передача того же api в fetch_warehouses; прежний постоянный return_value скрывал потерю настроек запроса справочника. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R6: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 1.

```diff
--- src/services/four_tochki_service.py
+++ src/services/four_tochki_service.py
@@ -1,6 +1,6 @@
 def load_remote_vendor_data(*, api: FourTochkiApiConfig, groups: Sequence[FourTochkiWarehouseGroup]) -> None:
     """Подобрать склады API по группам, вывести их и выгрузить шины и диски в file_prices/four_tochki."""
-    warehouses = select_warehouses(groups, fetch_warehouses(api))
+    warehouses = select_warehouses(groups, fetch_warehouses(None))
     log_selected_warehouses(groups, warehouses)
     dest_dir = Path(get_config_provider().price_folder(_VENDOR_FOLDER))
     download_catalogs(dest_dir=dest_dir, api=api, warehouses=warehouses)
```

## src/services/group_processing.py

### `services.group_processing.x__group_tires__mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: test_group_packages_passes_reference_priority проверяет передачу непустой очереди эталонов в фабрику группировки; None вместо очереди различим. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 17.

```diff
--- src/services/group_processing.py
+++ src/services/group_processing.py
@@ -2,7 +2,7 @@
     parsed: ParseResult, tire_factory: GrouperFactory, source: VendorSource, target: logging.Logger
 ) -> None:
     grouper = tire_factory(
-        parsed.tire_and_disk_items, aliases_map=source.aliases_map(), reference_priority=source.reference_priority()
+        parsed.tire_and_disk_items, aliases_map=source.aliases_map(), reference_priority=None
     )
     grouped = grouper.group_by_params().get_row_items()
     parsed.replace_package(TireAndDiskResult(tuple(grouped)))
```

### `services.group_processing.x__group_tires__mutmut_7`

Классификация 2026-11-14: Закрытый пробел проверки: test_group_packages_passes_reference_priority проверяет передачу непустой очереди эталонов в фабрику группировки; удаление аргумента различимо. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 17.

```diff
--- src/services/group_processing.py
+++ src/services/group_processing.py
@@ -2,8 +2,7 @@
     parsed: ParseResult, tire_factory: GrouperFactory, source: VendorSource, target: logging.Logger
 ) -> None:
     grouper = tire_factory(
-        parsed.tire_and_disk_items, aliases_map=source.aliases_map(), reference_priority=source.reference_priority()
-    )
+        parsed.tire_and_disk_items, aliases_map=source.aliases_map(), )
     grouped = grouper.group_by_params().get_row_items()
     parsed.replace_package(TireAndDiskResult(tuple(grouped)))
     counters = parsed.statistics.setdefault(ProductGroup.TIRE_AND_DISK, GroupStatistics())
```

### `services.group_processing.x__group_tires__mutmut_14`

Классификация 2026-11-14: Закрытый пробел проверки: test_group_packages_passes_reference_priority передаёт group_packages выбранный шинный пакет без предварительно созданной статистики. GroupStatistics должен создаваться до обновления счётчиков; None приводит к AttributeError. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 17.

```diff
--- src/services/group_processing.py
+++ src/services/group_processing.py
@@ -6,7 +6,7 @@
     )
     grouped = grouper.group_by_params().get_row_items()
     parsed.replace_package(TireAndDiskResult(tuple(grouped)))
-    counters = parsed.statistics.setdefault(ProductGroup.TIRE_AND_DISK, GroupStatistics())
+    counters = parsed.statistics.setdefault(ProductGroup.TIRE_AND_DISK, None)
     counters.item_count = len(grouped)
     counters.priced_items = sum(bool(row.pricing.price_opt) for row in grouped)
     counters.doubles = sum(bool(row.duplicate.is_double) for row in grouped)
```

### `services.group_processing.x__group_tires__mutmut_16`

Классификация 2026-11-14: Закрытый пробел проверки: test_group_packages_passes_reference_priority передаёт group_packages выбранный шинный пакет без предварительно созданной статистики. Отсутствующий default setdefault создаёт None вместо GroupStatistics и приводит к AttributeError. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 17.

```diff
--- src/services/group_processing.py
+++ src/services/group_processing.py
@@ -6,7 +6,7 @@
     )
     grouped = grouper.group_by_params().get_row_items()
     parsed.replace_package(TireAndDiskResult(tuple(grouped)))
-    counters = parsed.statistics.setdefault(ProductGroup.TIRE_AND_DISK, GroupStatistics())
+    counters = parsed.statistics.setdefault(ProductGroup.TIRE_AND_DISK, )
     counters.item_count = len(grouped)
     counters.priced_items = sum(bool(row.pricing.price_opt) for row in grouped)
     counters.doubles = sum(bool(row.duplicate.is_double) for row in grouped)
```

## src/services/mail_service.py

### `services.mail_service.xǁMailServiceǁfetch_prices__mutmut_19`

Классификация 2026-11-14: Закрытый пробел проверки: Существующий test_fetch_prices_uses_injected_provider_for_vendor_filtering отклоняет иной провайдер при чтении конфигов поставщиков; потеря provider при передаче в _collect обнаруживается. Целевой прогон R7 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 13.

```diff
--- src/services/mail_service.py
+++ src/services/mail_service.py
@@ -5,4 +5,4 @@
         account = config.account
         client = connect(account.host, account.port, account.folder, get_mail_credentials())
         with _MailSession(client) as inbox:
-            return _collect(inbox, config, list_price_folders(inbox, account.folder), provider)
+            return _collect(inbox, config, list_price_folders(inbox, account.folder), None)
```

### `services.mail_service.x__collect__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: Существующий test_fetch_prices_uses_injected_provider_for_vendor_filtering отклоняет None вместо явно переданного провайдера в skip_mail_fetch. Целевой прогон R7 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 12.

```diff
--- src/services/mail_service.py
+++ src/services/mail_service.py
@@ -4,7 +4,7 @@
     """Обойти активные профили: найти письмо, записать вложение, собрать итог."""
     fetched: list[MailFetchResult] = []
     for folder, profile in config.enabled_profiles().items():
-        if skip_mail_fetch(folder, config_provider):
+        if skip_mail_fetch(folder, None):
             continue
         found = find_latest_price(client, folders, profile=profile)
         if found is None:
```

### `services.mail_service.x__collect__mutmut_6`

Классификация 2026-11-14: Закрытый пробел проверки: test_fetch_prices_continues_after_skipped_vendor ставит отключённого и API-поставщика перед активным файловым. break теряет последнего; проверяются его результат, поиск письма и сохранение. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `keyword`; выбрано тестов: 12.

```diff
--- src/services/mail_service.py
+++ src/services/mail_service.py
@@ -5,7 +5,7 @@
     fetched: list[MailFetchResult] = []
     for folder, profile in config.enabled_profiles().items():
         if skip_mail_fetch(folder, config_provider):
-            continue
+            break
         found = find_latest_price(client, folders, profile=profile)
         if found is None:
             logger.warning(f'Для поставщика «{folder}» подходящее письмо не найдено.')
```

## src/services/mim_service.py

### `services.mim_service.xǁMimServiceǁ__init____mutmut_1`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R6: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 5.

```diff
--- src/services/mim_service.py
+++ src/services/mim_service.py
@@ -1,2 +1,2 @@
     def __init__(self, config_provider: ConfigProvider | None = None) -> None:
-        self._config_provider = config_provider
+        self._config_provider = None
```

### `services.mim_service.xǁMimServiceǁupload_data__mutmut_1`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R6: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 4.

```diff
--- src/services/mim_service.py
+++ src/services/mim_service.py
@@ -1,6 +1,6 @@
     def upload_data(self) -> bool:
         """Загрузить удалённые данные в file_prices/mim; вернуть False, если поставщик отключён."""
-        provider = self._config_provider or get_config_provider()
+        provider = None
         if skip_disabled_upload(_VENDOR_FOLDER, provider):
             return False
         api = get_mim_api_config()
```

### `services.mim_service.xǁMimServiceǁupload_data__mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R6: killed. Исторический survived сохранён.

Статус: **survived**; тип: `operator`; выбрано тестов: 4.

```diff
--- src/services/mim_service.py
+++ src/services/mim_service.py
@@ -1,6 +1,6 @@
     def upload_data(self) -> bool:
         """Загрузить удалённые данные в file_prices/mim; вернуть False, если поставщик отключён."""
-        provider = self._config_provider or get_config_provider()
+        provider = self._config_provider and get_config_provider()
         if skip_disabled_upload(_VENDOR_FOLDER, provider):
             return False
         api = get_mim_api_config()
```

### `services.mim_service.xǁMimServiceǁupload_data__mutmut_4`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R6: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 4.

```diff
--- src/services/mim_service.py
+++ src/services/mim_service.py
@@ -1,7 +1,7 @@
     def upload_data(self) -> bool:
         """Загрузить удалённые данные в file_prices/mim; вернуть False, если поставщик отключён."""
         provider = self._config_provider or get_config_provider()
-        if skip_disabled_upload(_VENDOR_FOLDER, provider):
+        if skip_disabled_upload(_VENDOR_FOLDER, None):
             return False
         api = get_mim_api_config()
         types = resolve_types(_configured_types(provider))
```

### `services.mim_service.xǁMimServiceǁupload_data__mutmut_11`

Классификация 2026-11-14: Закрытый пробел проверки: Тесты test_mim_service через _upload проверяют явный FakeConfigProvider в load_vendor_configs: аргумент должен пройти и upload_data, и _configured_types. Прежний постоянный return_value скрывал потерю аргумента. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R6: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 4.

```diff
--- src/services/mim_service.py
+++ src/services/mim_service.py
@@ -4,7 +4,7 @@
         if skip_disabled_upload(_VENDOR_FOLDER, provider):
             return False
         api = get_mim_api_config()
-        types = resolve_types(_configured_types(provider))
+        types = resolve_types(_configured_types(None))
         request = MimApiRequest(host=api.host, token=api.token, types=types)
         load_remote_vendor_data(api=request)
         return True
```

### `services.mim_service.x__configured_types__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: Тесты test_mim_service через _upload проверяют явный FakeConfigProvider в load_vendor_configs: аргумент должен пройти и upload_data, и _configured_types. Прежний постоянный return_value скрывал потерю аргумента. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R6: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 3.

```diff
--- src/services/mim_service.py
+++ src/services/mim_service.py
@@ -1,6 +1,6 @@
 def _configured_types(config_provider: ConfigProvider) -> tuple[int, ...]:
     """Категории из `behavior.api_types` конфига МИМ; конфига нет — пусто (набор по умолчанию)."""
-    config = load_vendor_configs(config_provider).get(_VENDOR_FOLDER)
+    config = load_vendor_configs(None).get(_VENDOR_FOLDER)
     if config is not None:
         for group in config.product_groups:
             if isinstance(group, TireAndDiskConfig):
```

## src/services/parse_logging.py

### `services.parse_logging.x__homoglyph_messages__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: Существующий test_parser_messages_homoglyph_counter_is_independent проверяет fixes без suspects и suspects без fixes; and теряет обе независимые сводки. Целевой прогон R7 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `operator`; выбрано тестов: 20.

```diff
--- src/services/parse_logging.py
+++ src/services/parse_logging.py
@@ -1,7 +1,7 @@
 def _homoglyph_messages(parser: SupplierParser) -> list[LogMessage]:
     """Сколько кириллических двойников исправлено у поставщика и сколько смесей оставлено в логе."""
     stats = parser.stats
-    if not (stats.homoglyph_fixes or stats.homoglyph_suspects):
+    if not (stats.homoglyph_fixes and stats.homoglyph_suspects):
         return []
     text = (
         f'{parser!r}: кириллические двойники исправлены: {stats.homoglyph_fixes}, '
```

## src/services/parse_orchestrator.py

### `services.parse_orchestrator.xǁParseOrchestratorǁ_parse_supplier__mutmut_26`

Классификация 2026-11-14: Закрытый пробел проверки: test_other_package_keeps_only_common_counters теперь задаёт ненулевые homoglyph_fixes и titles_not_composed чужой группы и проверяет отсутствие шинных сообщений в caplog. Удаление product_group включает шинную сводку по умолчанию. Целевой прогон R10 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 23.

```diff
--- src/services/parse_orchestrator.py
+++ src/services/parse_orchestrator.py
@@ -11,4 +11,4 @@
             counters.black_list_skips += parser.stats.black_list_skips
             if parsed.product_group is ProductGroup.TIRE_AND_DISK:
                 parse_result.tire_and_disk_diagnostics.accumulate(parser.stats, _parser_unknown_skips(parser))
-            _emit(parser_messages(parser, parsed.product_group))
+            _emit(parser_messages(parser, ))
```

### `services.parse_orchestrator.xǁParseOrchestratorǁparse_all__mutmut_12`

Классификация 2026-11-14: Закрытый пробел проверки: test_battery_selection_available_before_parser_failure задаёт ParseConfiguration с группой batteries и отказ фабрики; ParseSelection должен сохранить batteries. Безусловный выбор tire_and_disk нарушает результат. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 21.

```diff
--- src/services/parse_orchestrator.py
+++ src/services/parse_orchestrator.py
@@ -6,7 +6,7 @@
         if selection is not None:
             selection.groups = tuple(
                 dict.fromkeys(
-                    ProductGroup.TIRE_AND_DISK if config is None else config.product_group or ProductGroup.TIRE_AND_DISK
+                    ProductGroup.TIRE_AND_DISK if (config is None) or True else config.product_group or ProductGroup.TIRE_AND_DISK
                     for _, config in selected
                 )
             )
```

### `services.parse_orchestrator.xǁParseOrchestratorǁparse_all__mutmut_14`

Классификация 2026-11-14: Закрытый пробел проверки: test_battery_selection_available_before_parser_failure задаёт ParseConfiguration с группой batteries и отказ фабрики; and заменяет выбранную группу на tire_and_disk. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `operator`; выбрано тестов: 21.

```diff
--- src/services/parse_orchestrator.py
+++ src/services/parse_orchestrator.py
@@ -6,7 +6,7 @@
         if selection is not None:
             selection.groups = tuple(
                 dict.fromkeys(
-                    ProductGroup.TIRE_AND_DISK if config is None else config.product_group or ProductGroup.TIRE_AND_DISK
+                    ProductGroup.TIRE_AND_DISK if config is None else config.product_group and ProductGroup.TIRE_AND_DISK
                     for _, config in selected
                 )
             )
```

## src/services/price_report.py

### `services.price_report.xǁPriceReportServiceǁfrom_factories__mutmut_1`

Классификация 2026-11-14: Закрытый пробел проверки: test_from_factories_passes_nonempty_positions проверяет передачу непустого списка RowItem и зависимостей в CommonPriceOut; None вместо списка различим. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 3.

```diff
--- src/services/price_report.py
+++ src/services/price_report.py
@@ -10,7 +10,7 @@
 
         def writer_factory(row_items: list[RowItem]) -> CommonPriceOut:
             return CommonPriceOut(
-                row_items,
+                None,
                 xls_writer=xls_writer,
                 write_driver=write_driver,
                 config_provider=config_provider(),
```

### `services.price_report.xǁPriceReportServiceǁfrom_factories__mutmut_10`

Классификация 2026-11-14: Закрытый пробел проверки: test_from_factories_connects_group_writer вызывает write_result у собранного сервиса и проверяет создание GroupFileWriter с переданными фабриками; None вместо фабрики останавливает запись. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 3.

```diff
--- src/services/price_report.py
+++ src/services/price_report.py
@@ -22,5 +22,5 @@
             )
 
         return cls(
-            writer_factory=writer_factory, group_writer_factory=group_writer_factory, config_provider=config_provider
+            writer_factory=writer_factory, group_writer_factory=None, config_provider=config_provider
         )
```

### `services.price_report.xǁPriceReportServiceǁfrom_factories__mutmut_11`

Классификация 2026-11-14: Закрытый пробел проверки: test_from_factories_connects_group_writer вызывает write_result и проверяет передачу конкретного провайдера в output_sources; None вместо функции провайдера останавливает запись. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 3.

```diff
--- src/services/price_report.py
+++ src/services/price_report.py
@@ -22,5 +22,5 @@
             )
 
         return cls(
-            writer_factory=writer_factory, group_writer_factory=group_writer_factory, config_provider=config_provider
+            writer_factory=writer_factory, group_writer_factory=group_writer_factory, config_provider=None
         )
```

### `services.price_report.xǁPriceReportServiceǁfrom_factories__mutmut_13`

Классификация 2026-11-14: Закрытый пробел проверки: test_from_factories_connects_group_writer вызывает write_result у собранного сервиса; удаление group_writer_factory оставляет None и останавливает запись. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/services/price_report.py
+++ src/services/price_report.py
@@ -22,5 +22,5 @@
             )
 
         return cls(
-            writer_factory=writer_factory, group_writer_factory=group_writer_factory, config_provider=config_provider
+            writer_factory=writer_factory, config_provider=config_provider
         )
```

### `services.price_report.xǁPriceReportServiceǁfrom_factories__mutmut_14`

Классификация 2026-11-14: Закрытый пробел проверки: test_from_factories_connects_group_writer вызывает write_result и проверяет передачу конкретного провайдера в output_sources; удаление config_provider оставляет None и останавливает запись. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/services/price_report.py
+++ src/services/price_report.py
@@ -22,5 +22,4 @@
             )
 
         return cls(
-            writer_factory=writer_factory, group_writer_factory=group_writer_factory, config_provider=config_provider
-        )
+            writer_factory=writer_factory, group_writer_factory=group_writer_factory, )
```

### `services.price_report.xǁPriceReportServiceǁwrite_result__mutmut_1`

Классификация 2026-11-14: Закрытый пробел проверки: test_write_result_logs_start_before_writing_and_elapsed и test_from_factories_connects_group_writer теперь проверяют as_jsonl=False при вызове без флага; True нарушает формат записи. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `keyword`; выбрано тестов: 3.

```diff
--- src/services/price_report.py
+++ src/services/price_report.py
@@ -1,4 +1,4 @@
-    def write_result(self, parsed: ParseResult, *, template: str | None = None, as_jsonl: bool = False) -> list[str]:
+    def write_result(self, parsed: ParseResult, *, template: str | None = None, as_jsonl: bool = True) -> list[str]:
         """Сохранить границы пакетов от оркестратора до выходных преобразователей."""
         if self._group_writer_factory is None or self._config_provider is None:
             raise RuntimeError('Фабрика групповой записи не настроена')
```

### `services.price_report.xǁPriceReportServiceǁwrite_result__mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: test_write_result_requires_both_dependencies по отдельности убирает фабрику группового писателя и функцию провайдера. В обоих случаях требуется RuntimeError до подготовки источников; and пропускает проверку и приводит к TypeError. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `operator`; выбрано тестов: 3.

```diff
--- src/services/price_report.py
+++ src/services/price_report.py
@@ -1,6 +1,6 @@
     def write_result(self, parsed: ParseResult, *, template: str | None = None, as_jsonl: bool = False) -> list[str]:
         """Сохранить границы пакетов от оркестратора до выходных преобразователей."""
-        if self._group_writer_factory is None or self._config_provider is None:
+        if self._group_writer_factory is None and self._config_provider is None:
             raise RuntimeError('Фабрика групповой записи не настроена')
         start_time = time.monotonic()
         logger.info('Начало формирования и сохранения итоговых прайсов')
```

### `services.price_report.xǁPriceReportServiceǁwrite_result__mutmut_16`

Классификация 2026-11-14: Закрытый пробел проверки: test_write_result_logs_start_before_writing_and_elapsed и test_from_factories_connects_group_writer проверяют передачу selected=parsed.groups.keys(); None стирает явно заданный выбор групп. Целевой прогон R9 подтвердил killed. Удаляемые и добавляемые строки diff совпадают внутри той же функции (тот же ID); исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/services/price_report.py
+++ src/services/price_report.py
@@ -6,7 +6,7 @@
         logger.info('Начало формирования и сохранения итоговых прайсов')
         sources = output_sources(parsed.groups, self._config_provider())
         paths = write_group_prices(
-            self._group_writer_factory(), sources, template=template, as_jsonl=as_jsonl, selected=parsed.groups.keys()
+            self._group_writer_factory(), sources, template=template, as_jsonl=as_jsonl, selected=None
         )
         elapsed = time.monotonic() - start_time
         logger.info(f'Итоговые прайсы сформированы и сохранены ({elapsed:.2f} сек), файлов: {len(paths)}\n')
```

## src/services/price_schema_service.py

### `services.price_schema_service.xǁPriceSchemaServiceǁ__init____mutmut_1`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R4: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 11.

```diff
--- src/services/price_schema_service.py
+++ src/services/price_schema_service.py
@@ -1,6 +1,6 @@
     def __init__(self, backup_folder: Path | None = None, config_provider: ConfigProvider | None = None) -> None:
         """`backup_folder` — куда класть копию (по умолчанию временная папка ОС); `config_provider` — пути окружения."""
-        self._config_provider = config_provider
+        self._config_provider = None
         self._backup = backup_folder or default_backup_folder()
         self._depth = 0
         self._copied = False
```

### `services.price_schema_service.xǁPriceSchemaServiceǁ__init____mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R4: killed. Исторический survived сохранён.

Статус: **survived**; тип: `operator`; выбрано тестов: 11.

```diff
--- src/services/price_schema_service.py
+++ src/services/price_schema_service.py
@@ -1,6 +1,6 @@
     def __init__(self, backup_folder: Path | None = None, config_provider: ConfigProvider | None = None) -> None:
         """`backup_folder` — куда класть копию (по умолчанию временная папка ОС); `config_provider` — пути окружения."""
         self._config_provider = config_provider
-        self._backup = backup_folder or default_backup_folder()
+        self._backup = backup_folder and default_backup_folder()
         self._depth = 0
         self._copied = False
```

### `services.price_schema_service.xǁPriceSchemaServiceǁ__init____mutmut_6`

Классификация 2026-11-14: Эквивалент: Начальное _copied не читается ни snapshot, ни check; при первом входе в guard (depth=0) оно перезаписывается результатом snapshot до чтения в finally. Замена False на None ненаблюдаема через публичный API. Прогон R4 оставляет survived.

Статус: **survived**; тип: `to_none`; выбрано тестов: 11.

```diff
--- src/services/price_schema_service.py
+++ src/services/price_schema_service.py
@@ -3,4 +3,4 @@
         self._config_provider = config_provider
         self._backup = backup_folder or default_backup_folder()
         self._depth = 0
-        self._copied = False
+        self._copied = None
```

### `services.price_schema_service.xǁPriceSchemaServiceǁ__init____mutmut_7`

Классификация 2026-11-14: Эквивалент: Начальное _copied не читается ни snapshot, ни check; при первом входе в guard (depth=0) оно перезаписывается результатом snapshot до чтения в finally. Замена False на True ненаблюдаема через публичный API. Прогон R4 оставляет survived.

Статус: **survived**; тип: `keyword`; выбрано тестов: 11.

```diff
--- src/services/price_schema_service.py
+++ src/services/price_schema_service.py
@@ -3,4 +3,4 @@
         self._config_provider = config_provider
         self._backup = backup_folder or default_backup_folder()
         self._depth = 0
-        self._copied = False
+        self._copied = True
```

### `services.price_schema_service.xǁPriceSchemaServiceǁ_vendor_warnings__mutmut_20`

Классификация 2026-11-14: Эквивалент: Значения словаря warnings не читаются: list(warnings) возвращает только ключи. Замена None на пустую строку сохраняет сообщения, порядок и удаление дублей. Прогон R4 оставляет survived.

Статус: **survived**; тип: `none_to_empty`; выбрано тестов: 5.

```diff
--- src/services/price_schema_service.py
+++ src/services/price_schema_service.py
@@ -5,5 +5,5 @@
             for path in _section_files(vendor.folder, section, self._provider()):
                 old_path = self._backup / vendor.folder / path.name
                 for change in _file_changes(old_path, path, section, heads):
-                    warnings[_message(vendor, section, path, change)] = None
+                    warnings[_message(vendor, section, path, change)] = ""
         return list(warnings)
```

### `services.price_schema_service.xǁPriceSchemaServiceǁcheck__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R4: killed. Исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 5.

```diff
--- src/services/price_schema_service.py
+++ src/services/price_schema_service.py
@@ -2,7 +2,7 @@
         """Сравнить схемы прайсов копии и текущих файлов; предупреждения выводятся в лог и возвращаются."""
         warnings: list[str] = []
         heads: dict[Path, FileHead | None] = {}
-        for vendor in load_vendor_configs(self._provider()).values():
+        for vendor in load_vendor_configs(None).values():
             warnings.extend(self._vendor_warnings(vendor, heads))
         for warning in warnings:
             logger.warning(warning)
```

### `services.price_schema_service.xǁPriceSchemaServiceǁsnapshot__mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R4: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 7.

```diff
--- src/services/price_schema_service.py
+++ src/services/price_schema_service.py
@@ -1,7 +1,7 @@
     def snapshot(self) -> bool:
         """Скопировать file_prices (кроме result) в папку копии; не вышло — предупреждение и False."""
         provider = self._provider()
-        skip = Path(provider.result_folder())
+        skip = None
         try:
             backup_prices(Path(provider.price_folder('')), self._backup, skip=skip)
         except OSError as exc:
```

### `services.price_schema_service.xǁPriceSchemaServiceǁsnapshot__mutmut_6`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R4: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 7.

```diff
--- src/services/price_schema_service.py
+++ src/services/price_schema_service.py
@@ -3,7 +3,7 @@
         provider = self._provider()
         skip = Path(provider.result_folder())
         try:
-            backup_prices(Path(provider.price_folder('')), self._backup, skip=skip)
+            backup_prices(Path(provider.price_folder('')), self._backup, skip=None)
         except OSError as exc:
             logger.warning(f'Не удалось сделать копию прайсов ({exc}): схемы прайсов не будут сравнены.')
             return False
```

### `services.price_schema_service.xǁPriceSchemaServiceǁsnapshot__mutmut_9`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R4: killed. Исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 7.

```diff
--- src/services/price_schema_service.py
+++ src/services/price_schema_service.py
@@ -3,7 +3,7 @@
         provider = self._provider()
         skip = Path(provider.result_folder())
         try:
-            backup_prices(Path(provider.price_folder('')), self._backup, skip=skip)
+            backup_prices(Path(provider.price_folder('')), self._backup, )
         except OSError as exc:
             logger.warning(f'Не удалось сделать копию прайсов ({exc}): схемы прайсов не будут сравнены.')
             return False
```

### `services.price_schema_service.x__schema__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R4: killed. Исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 3.

```diff
--- src/services/price_schema_service.py
+++ src/services/price_schema_service.py
@@ -1,5 +1,5 @@
 def _schema(head: FileHead, section: VendorSection | BatterySection) -> PriceSchema:
     """Схема файла для секции."""
     return build_schema(
-        head, start_row=section.start_row, sheet_indexes=section.sheet_indexes, columns=_columns(section)
+        head, start_row=section.start_row, sheet_indexes=None, columns=_columns(section)
     )
```

## src/services/vendor_activity.py

### `services.vendor_activity.x_is_vendor_enabled__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R4: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 11.

```diff
--- src/services/vendor_activity.py
+++ src/services/vendor_activity.py
@@ -1,4 +1,4 @@
 def is_vendor_enabled(folder: str, config_provider: ConfigProvider) -> bool:
     """Поставщик включён в настройках; конфига нет — считаем включённым (как раньше)."""
-    config = load_vendor_configs(config_provider).get(folder)
+    config = load_vendor_configs(None).get(folder)
     return True if config is None else bool(config.enabled)
```

### `services.vendor_activity.x_skip_disabled_upload__mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R4: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 8.

```diff
--- src/services/vendor_activity.py
+++ src/services/vendor_activity.py
@@ -1,6 +1,6 @@
 def skip_disabled_upload(folder: str, config_provider: ConfigProvider) -> bool:
     """Вернуть True и написать в лог, если поставщик отключён и данные по API грузить не нужно."""
-    if is_vendor_enabled(folder, config_provider):
+    if is_vendor_enabled(folder, None):
         return False
     logger.info(
         f'Поставщик «{folder}» отключён в настройках, данные по API не загружаются.',
```

### `services.vendor_activity.x_skip_mail_fetch__mutmut_3`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R4: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 12.

```diff
--- src/services/vendor_activity.py
+++ src/services/vendor_activity.py
@@ -1,6 +1,6 @@
 def skip_mail_fetch(folder: str, config_provider: ConfigProvider) -> bool:
     """Вернуть True, если прайс по почте не нужен; отключение поставщика записать в лог."""
-    config = load_vendor_configs(config_provider).get(folder)
+    config = load_vendor_configs(None).get(folder)
     if config is None:
         return False
     if not config.enabled:
```

## src/services/zapaska_service.py

### `services.zapaska_service.xǁZapaskaServiceǁ__init____mutmut_1`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R4: killed. Исторический survived сохранён.

Статус: **survived**; тип: `to_none`; выбрано тестов: 3.

```diff
--- src/services/zapaska_service.py
+++ src/services/zapaska_service.py
@@ -1,2 +1,2 @@
     def __init__(self, config_provider: ConfigProvider | None = None) -> None:
-        self._config_provider = config_provider
+        self._config_provider = None
```

### `services.zapaska_service.xǁZapaskaServiceǁupload_data__mutmut_2`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R4: killed. Исторический survived сохранён.

Статус: **survived**; тип: `other`; выбрано тестов: 2.

```diff
--- src/services/zapaska_service.py
+++ src/services/zapaska_service.py
@@ -1,6 +1,6 @@
     def upload_data(self) -> bool:
         """Загрузить удалённые данные в локальную базу; вернуть False, если поставщик отключён."""
-        if skip_disabled_upload(_VENDOR_FOLDER, self._config_provider or get_config_provider()):
+        if skip_disabled_upload(_VENDOR_FOLDER, None):
             return False
         load_remote_vendor_data(api=get_zapaska_api_config())
         return True
```

### `services.zapaska_service.xǁZapaskaServiceǁupload_data__mutmut_5`

Классификация 2026-11-14: Закрытый пробел проверки: Повторный целевой прогон подтвердил killed на существующих тестах. Идентичные удаляемые и добавляемые строки diff сопоставлены в той же функции (тот же ID); результат R4: killed. Исторический survived сохранён.

Статус: **survived**; тип: `operator`; выбрано тестов: 2.

```diff
--- src/services/zapaska_service.py
+++ src/services/zapaska_service.py
@@ -1,6 +1,6 @@
     def upload_data(self) -> bool:
         """Загрузить удалённые данные в локальную базу; вернуть False, если поставщик отключён."""
-        if skip_disabled_upload(_VENDOR_FOLDER, self._config_provider or get_config_provider()):
+        if skip_disabled_upload(_VENDOR_FOLDER, self._config_provider and get_config_provider()):
             return False
         load_remote_vendor_data(api=get_zapaska_api_config())
         return True
```
