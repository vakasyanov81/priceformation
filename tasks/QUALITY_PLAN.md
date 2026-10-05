# План устранения замечаний по качеству кода

Документ описывает замечания, найденные при ревью кода на срезе
`a4c0174` (#275). Замечания уже отсортированы по риску: сверху — то, что
пропускает в репозиторий или в колесо то, чего там быть не должно.

План не пересекается с [архитектурным](./PLAN.md) (те задачи закрыты) и с
[планом тестов](./MUTATION_TESTS.md) (тот меняет только `tests/`). Здесь
трогаем конфигурацию CI, состав пакета и остатки `BaseParser`.

---

## Сводка

| # | Задача | Кратко | Приоритет | Статус |
|---|--------|--------|-----------|--------|
| Q1 | [Bandit и pip-audit в CI](#q1--bandit-и-pip-audit-в-ci) | Security-гейты есть только в pre-commit, PR их не проверяет | P0 | ⬜ |
| Q2 | [Тестовые заглушки вне production-пакета](#q2--тестовые-заглушки-вне-production-пакета) | Три `fake_*` едут в колесо через `only-include = ["src"]` | P0 | ⬜ |
| Q3 | [Убрать `bandit skips = ["B101"]`](#q3--убрать-bandit-skips--b101) | Исключение устарело: в `src/` нет ни одного assert | P1 | ⬜ |
| Q4 | [Мёртвые атрибуты в `register_vendor`](#q4--мёртвые-атрибуты-в-register_vendor) | `_vendor_code` и `_enabled_by_default` читают только тесты | P1 | ⬜ |
| Q5 | [Строгий API шаблонов записи](#q5--строгий-api-шаблонов-записи) | `hasattr`/`getattr` глушит опечатки в `__COLUMNS__` и т. п. | P1 | ⬜ |
| Q6 | [Вызов приватного метода чужого объекта](#q6--вызов-приватного-метода-чужого-объекта) | `BaseParser` лезет в `_row_processor._require_markup_policy()` | P1 | ⬜ |
| Q7 | [Пасс-срю `BaseParser` → `TitleFilter`](#q7--пасс-срю-baseparser--titlefilter) | 5 мёртвых делегатов + 5 непокрытых строк | P1 | ⬜ |
| Q8 | [`ParserParams`: общие мутабельные списки](#q8--parserparams-общие-мутабельные-списки) | `dataclasses.replace` делит списки между вкладками MIM | P1 | ⬜ |
| Q9 | [Противоречия в настройках покрытия](#q9--противоречия-в-настройках-покрытия) | `--cov=tests` против `omit` в `.coveragerc`, дубли `per-file-ignores` | P2 | ⬜ |
| Q10 | [Устаревшая ссылка в CI](#q10--устаревшая-ссылка-в-ci) | Workflow ссылается на несуществующий `.cursor/rules/` | P2 | ⬜ |
| Q11 | [`dataclasses.replace` + мутация в MIM](#q11--dataclassesreplace--мутация-в-mim) | Три вкладки отличаются одной строкой, а не тремя | P2 | ⬜ |
| Q12 | [Опечатки в именах модулей](#q12--опечатки-в-именах-модулей) | `xwlt_driver.py`, `ixls_driver.py` | P2 | ⬜ |
| Q13 | [Дублирующиеся дефолты в `RowItem`](#q13--дублирующиеся-дефолты-в-rowitem) | `field(default_factory=...)` и ручной `__init__` описывают одно и то же | P2 | ⬜ |
| Q14 | [Покрытие `title_filter.py`](#q14--покрытие-title_filterpy) | 86 % — минимум по проекту | P2 | ⬜ |

---

## Q1 — Bandit и pip-audit в CI

### Проблема

`.github/workflows/python-app.yml` выполняет семь шагов: `pytest`, `black`,
`ruff`, `flake8`, `mypy`, `lint-imports`, `vulture`. `bandit` и `pip-audit`
в workflow отсутствуют, хотя:

- `AGENTS.md` объявляет шаги 8–9 как часть CI-набора;
- `.pre-commit-config.yaml` выполняет оба.

Итог: уязвимая зависимость или небезопасный вызов ловятся только хуком, который
обходится `--no-verify`, и PR-ветка их не поймает.

### Решение

Дописать в `python-app.yml` два шага — в том же порядке, что в `justfile audit`
и в `.pre-commit-config.yaml`, чтобы все три источника правды совпадали:

```yaml
      - name: Check security with bandit
        run: uv run bandit -r src -c pyproject.toml
      - name: Audit dependencies
        run: uv run pip-audit
```

Флаги не переопределять: настройки уже в `pyproject.toml`.

### Критерии готовности

- [ ] Оба шага присутствуют в workflow.
- [ ] Локальный `just audit` и CI-шаги дают одинаковый результат на одном коммите.
- [ ] `AGENTS.md` не расходится с `.github/workflows/python-app.yml`.

---

## Q2 — Тестовые заглушки вне production-пакета

### Проблема

Три файла дублей лежат под `src/`, а hatch собирает `only-include = ["src"]`:

| Файл | Строк | Кто импортирует |
| --- | ---: | --- |
| `src/parsers/fake_xls_reader.py` | 28 | 8 тестовых модулей |
| `src/parsers/fake_json_reader.py` | 26 | `tests/test_parsers/test_vendors/test_parse_zapaska_disk_json.py` |
| `src/parsers/writer/fake_driver.py` | 55 | `test_writer_drom.py`, `test_writer_doubles.py` |

В `load_tests/` и `pipelines/` их не引用ает никто. Итого 109 строк тестовых
дублей попадают в колесо.

Отличать надо от `src/infrastructure/config/fake_config_provider.py`: он
используется в `load_tests/_make_price_once.py:8`, то есть дубль нужен за
пределами тестов, и оставить его в `src/` — сознательное решение.

### Решение

Перенести три файла в `tests/` рядом с потребителями:

```
tests/fakes/fake_xls_reader.py
tests/fakes/fake_json_reader.py
tests/fakes/fake_driver.py
```

`tests/conftest.py:12` уже добавляет корень `tests/` в `sys.path`, поэтому
импорты станут `from fakes.fake_xls_reader import FakeXlsReader` — по образцу
существующего `from log_watch import LoggerWatcher`.

Следствия, которые надо обновить в том же коммите:

- `pyproject.toml` `[tool.mutmut] do_not_mutate` — пути `src/parsers/fake_*`
  и `src/parsers/writer/fake_driver.py` больше не существуют (строки 160–162).
- `pyproject.toml` `[tool.vulture] paths` уже включает `tests` — править не нужно.

Проверить, что дублей не осталось в колесе:

```bash
uv build && uv run python -c "import zipfile,glob; \
  print([n for n in zipfile.ZipFile(glob.glob('dist/*.whl')[0]).namelist() if 'fake' in n])"
```

### Критерии готовности

- [ ] `grep -rn "fake_xls_reader\|fake_json_reader\|fake_driver" src/` пуст.
- [ ] В `dist/*.whl` нет файлов с `fake` в имени, кроме `fake_config_provider.py`.
- [ ] `[tool.mutmut] do_not_mutate` не ссылается на несуществующие пути.
- [ ] `uv run pytest` зелёный, `just test` проходит порог покрытия.

---

## Q3 — Убрать `bandit skips = ["B101"]`

### Проблема

`pyproject.toml:215`:

```toml
skips = ["B101"]
```

Над этим — комментарий «Allow assert statements in source (they are
production-use in this project)». В `src/` **ноль** assert'ов, так что
комментарий описывает несуществующую практику. Само исключение опаснее
комментария: оно разрешит assert-based control flow в проде, который
`python -O` вырежет без предупреждения.

### Решение

Удалить и `skips`, и комментарий. Bandit должен ловить новые assert'ы, а не
молчать о них.

### Критерии готовности

- [ ] В `[tool.bandit]` нет `skips`.
- [ ] `uv run bandit -r src -c pyproject.toml` даёт 0 issues (проверено на текущем
  состоянии с пустым `skips` — расхождений нет).

---

## Q4 — Мёртвые атрибуты в `register_vendor`

### Проблема

`src/parsers/registry.py:87-89` пишет три атрибута класса:

```python
cls._vendor_code = code                    # type: ignore[attr-defined]
cls._markup_policy_type = markup_policy   # type: ignore[attr-defined]
cls._enabled_by_default = enabled_by_default  # type: ignore[attr-defined]
```

`_markup_policy_type` читается в `vendor_markup_policy_for` (`registry.py:180`) —
живой. Остальные два читаются **только** из
`tests/test_parsers/test_registry.py:85,87,97,99`, то есть тесты проверяют
факт записи. Vulture их не видит именно потому, что на них ссылаются тесты.

Плюс три `type: ignore[attr-defined]` в пятистрочном враперере.

### Решение

Удалить `_vendor_code` и `_enabled_by_default` из враперера, из регистра
(`register_vendor` тогда теряет параметр `enabled_by_default`) и из теста.
Оставшийся `_markup_policy_type` объявить в `BaseParser` как
`_markup_policy_type: MarkupPolicySpec = None` — это убирает `type: ignore`
и делает контракт видимым.

Отдельно решить, нужен ли `enabled_by_default` как поведение: сейчас он ни на
что не влияет, включение вендора определяется `vendor_list.json`. Если
понадобится, добавлять вендора в `vendor_list.json` — не в декоратор.

### Критерии готовности

- [ ] `grep -rn "_vendor_code\|_enabled_by_default" src/` пуст.
- [ ] В `registry.py` не осталось `type: ignore[attr-defined]`.
- [ ] `uv run vulture` по-прежнему чист.

---

## Q5 — Строгий API шаблонов записи

### Проблема

`src/parsers/writer/templates/iwrite_template.py:24-42` читает четыре
настройки шаблона через `hasattr` + `getattr` строкой:

```python
ex_field = '__EXCLUDE__'
return getattr(self, ex_field) if hasattr(self, ex_field) else {}
```

Опечатка в имени атрибута подкласса даёт `{}` / `[]` /
`'default_result.xls'` — тихо. Для сравнения, `RowField` в
`domain/row_item/row_item.py:64-70` на неизвестный ключ бросает
`AttributeError` с подсказкой. В одном проекте два противоположных подхода к
одной и той же проблеме.

### Решение

Заменить `hasattr`/`getattr` на чтение через `cls.__dict__`-безопасный
дескриптор по образцу `RowField` — например, `ClassVarSetting` с
`__set_name__`-проверкой, чтобы misspelled-атрибут всплывал при первом же
создании подкласса, а не при записи файла.

Альтернатива, если дескриптор покажется перебором: оставить явные
`ClassVar`-объявления с `None` по умолчанию в `IWriteTemplate` и читать
`self.__COLUMNS__ or []` — опечатка тогда ломает импорт, а не вывод.

Выбрать один подход и применить его также в
`common_price_group_fields.py`, если там та же схема доступа.

### Критерии готовности

- [ ] `grep -rn "hasattr" src/parsers/writer/` пуст.
- [ ] Тест падает на подклассе с опечаткой в `__COLUMNS__` (см. Q14 — там же
  добавляется недостающее покрытие).
- [ ] `tests/test_architecture_markers.py` проверяет запрет `hasattr`-доступа к
  шаблонным настройкам.

---

## Q6 — Вызов приватного метода чужого объекта

### Проблема

`src/parsers/base_parser/base_parser.py:251`:

```python
def _require_markup_policy(self) -> MarkupPolicy:
    return self._row_processor._require_markup_policy()
```

`BaseParser` — снаружи `_row_processor`, но это единственный способ узнать
политику. Соглашение «приватное от своего класса» тут нарушено.

### Решение

Переименовать `RowProcessor._require_markup_policy` в публичное
`require_markup_policy()` (`src/parsers/base_parser/row_processor.py`), вызов
в `BaseParser` — без подчёркивания. Проверить, что `vulture` не посчитает
`_require_markup_policy` мёртвым сразу после переименования.

### Критерии готовности

- [ ] `grep -rn "_require_markup_policy" src/` пуст.
- [ ] `uv run vulture` чист.

---

## Q7 — Пасс-срю `BaseParser` → `TitleFilter`

### Проблема

`src/parsers/base_parser/base_parser.py:266-282` — пять делегатов без единого
вызывающего в `src/`:

| Метод | Вызовы в `src` | Вызовы в тестах | Покрытие |
| --- | ---: | ---: | --- |
| `has_stop_word` | 0 | 0 | строка 270 не покрыта |
| `check_title_in_black_list` | 0 | 0 | 273 |
| `get_black_list` | 0 | 0 | 276 |
| `prepare_black_list` | 0 | 0 | 279 |
| `get_stop_words` | 0 | 0 | 282 |

Пять строк из двадцати пропущенных в отчёте покрытия — эти. Плюс `# noqa:
WPS214` на строке 49 и exemption `src/domain/row_item/row_item.py: WPS214` в
`setup.cfg`, которые существуют в том числе ради них.

Остались реально используемыми: `is_valid_title` (три вызова в
`base_parser_row.py`), `get_prepared_title` и `set_prepared_title`
(переопределяются вендорами).

### Решение

Удалить пять методов вместе с соответствующими строками отчёта покрытия.
Если после Q8 в `BaseParser` останется меньше методов, снять `# noqa: WPS214`
со строки 49 и попробовать убрать exemption `WPS214` для `row_item.py` из
`setup.cfg`.

### Критерии готовности

- [ ] Покрытие `base_parser.py` выше 98 % без пропущенных строк в диапазоне 266-282.
- [ ] `uv run vulture` не предлагает удалить новые публичные методы.

---

## Q8 — `ParserParams`: общие мутабельные списки

### Проблема

`ParserParams` (`src/parsers/base_parser/base_parser_config.py:29-39`) —
изменяемый `@dataclass` со списочными полями `stop_words`, `file_templates`,
`sheet_indexes`. Вендоры строят свои параметры через
`dataclasses.replace(base_params)` (`mim_1sheet.py:14`, `mim_2sheet.py:19`,
`mim_3sheet.py`), а `replace` копирует поверхностно — списки остаются общими
объектами:

```
stop_words shared: True
file_templates shared: True
columns shared: False   # columns переприсваивается новым dict
```

Проверено: `p1.stop_words.append('ХАК')` видно и в `mim_params`, и в
`mim_sheet_2_params`. Сейчас никто эти списки в рантайме не мутирует
(`grep -E "\.(append|extend|insert)\(" по `stop_words`/`file_templates` пуст),
поэтому это латентная мина, а не текущий баг. Но `AGENTS.md` объявляет, что
пользовательские JSON-конфиги разбираются в frozen-модели; `ParserParams` до
этого стандарта не доведён, а параметры вендоров — модульные синглтоны, мутируемые
через `params.field = ...` в соседних строках.

### Решение

Два шага, по возрастанию инвазивности:

1. Пометить `ParserParams` как `frozen=True`. Мутации вида
   `mim_sheet_2_params.sheet_info = 'Вкладка #2'` перестанут работать — их
   заменит Q11 (одним вызовом `replace`).
2. Списочные поля сделать tuple: `stop_words: tuple[str, ...]`. Тогда
   поверхностное копирование `replace` безопасно, и следующий вендор не сможет
   испортить предыдущего.

Проверить, что ни один потребитель не мутирует параметры и не ждёт `list`.

### Критерии готовности

- [ ] `grep -rnE "params\.[a-z_]+ \+=|params\.[a-z_]+\.(append|extend)" src/` пуст.
- [ ] `uv run mypy .` — без новых ошибок на `tuple[str, ...]` в провайдерах.
- [ ] `uv run pytest` зелёный.

---

## Q9 — Противоречия в настройках покрытия

### Проблема

Два независимых источника настроек coverage описывают разное:

- `pyproject.toml` `addopts`: `--cov=src` **и** `--cov=tests`;
- `.coveragerc`: `omit = ./tests/* ./integration_tests/* ./load_tests/* ./run_mut.py`.

`--cov=tests` при этом, что `.coveragerc` просит его пропустить, — конфликт.
Плюс дубли в `per-file-ignores`: `"tests/*.py"` и `"tests/**/*.py"`
(`pyproject.toml:84-85`), так же `load_tests` (строки 90-91). В каждой паре одна
запись мёртвая.

### Решение

- Убрать `--cov=tests` из `addopts`: тестовый код не измеряется, а `.coveragerc`
  это уже отражает.
- `.coveragerc` оставить как есть — теперь он единственный источник `omit`.
- Удалить дублирующиеся ключи `per-file-ignores`, оставив `**`-варианты.

### Критерии готовности

- [ ] `grep -c "cov=tests" pyproject.toml` → 0.
- [ ] В `per-file-ignores` нет одновременно `X/*.py` и `X/**/*.py`.
- [ ] `just test` проходит порог 95 %, отчёт покрытия не изменился для `src/`.

---

## Q10 — Устаревшая ссылка в CI

### Проблема

`.github/workflows/python-app.yml:1`:

```
# Mirrors local quality gates from .cursor/rules/post-change-checks.mdc.
```

Каталога `.cursor` в репозитории нет — он в `.gitignore` («Buggy: .cursor/»).
Комментарий ссылается на источник правды, которого не существует.

### Решение

Заменить на актуальный источник — `justfile` и `.pre-commit-config.yaml`
(они и являются правдой после Q1/Q3). Аналогичную ссылку на
`.cursor/rules/` стоит вычистить из `.pi/skills/code-review/SKILL.md:50-51` —
там это условная формулировка «если есть», поэтому она безвредна и править
не обязательно.

### Критерии готовности

- [ ] `grep -rn "\.cursor" .github/` пуст.

---

## Q11 — `dataclasses.replace` + мутация в MIM

### Проблема

В `src/parsers/vendors/mim/mim_1sheet.py:14-17`, `mim_2sheet.py:19-21`,
`mim_3sheet.py` один логический шаг размазан на четыре строки:

```python
mim_sheet_2_params = dataclasses.replace(mim_params)
mim_sheet_2_params.sheet_info = 'Вкладка #2'
mim_sheet_2_params.sheet_indexes = [1]
mim_sheet_2_params.columns = { ... }   # 17 строк
```

Три вкладки отличаются по сути тремя значениями, но diff между файлами
показывает не различие, а переписывание.

### Решение

Свести к одному вызову на файл, сохраняя словарь `columns` многострочным:

```python
mim_sheet_2_params = dataclasses.replace(
    mim_params,
    sheet_info='Вкладка #2',
    sheet_indexes=[1],
    columns={
        0: RowItem.code.name,
        ...
    },
)
```

Выполнять после Q8 — только тогда `frozen=True` не сломает вендоров.

### Критерии готовности

- [ ] В трёх `mim_*sheet.py` нет присваиваний `mim_*_params.<field> = ...`.
- [ ] `grep -rn "^mim_sheet.*params\.[a-z_]* = " src/parsers/vendors/mim/` пуст.

---

## Q12 — Опечатки в именах модулей

### Проблема

`src/parsers/writer/xwlt_driver.py` (должно быть `xlsx_driver.py`) — класс
внутри называется верно: `XlsxWriterDriver`. Рядом `src/parsers/writer/ixls_driver.py`
(должно быть `ixlsx_driver.py`), который экспортирует `IXlsDriver`.

Опечатки в именах модулей разошлись по импортам: `ixls_driver` импортируется в
`common_price_output.py:14`, `xls_writer.py:9`, `fake_driver.py:7`,
`xwlt_driver.py:11`, `services/configure.py:7`.

### Решение

Переименовать оба файла вместе с импортами и тестами
(`tests/test_parsers/test_writer/test_ixls_driver.py`). Имя класса
`IXlsDriver` оставить как есть — переименование интерфейса выходит за рамки
правки опечаток и не нужно для выпуска.

Отдельно проверить, что в `.gitignore` нет правила, которое поймает новые
имена при `git mv`.

### Критерии готовности

- [ ] `grep -rn "ixls_driver\|xwlt_driver" . --include=*.py` пуст.
- [ ] `uv run pytest` зелёный.

---

## Q13 — Дублирующиеся дефолты в `RowItem`

### Проблема

`src/domain/row_item/row_item.py` объявляет все десять полей как
`field(default_factory=...)` (строки 77-86), но класс помечен
`@dataclass(eq=False, init=False)` и тут же имеет ручной `__init__`
(строки 150-162), присваивающий те же десять полей теми же значениями.

```python
@dataclass(eq=False, init=False)
class RowItem:
    identity: ProductIdentity = field(default_factory=ProductIdentity)
    ...
    def __init__(self, raw_row=None):
        self.identity = ProductIdentity()
        ...
```

Дефолты живут в двух местах: добавить восьмое поле — значит дописать его в
обоих списках. От дата-класса при `eq=False, init=False` остаётся только
`__repr__`.

### Решение

Убрать ручной `__init__`, оставив объявления `field(default_factory=...)`, и
сгенерированный `__init__` не подходит — он не принимает `raw_row`.
Значит, оставить ручной `__init__`, а объявления полей превратить в
`ClassVar`-подобные аннотации без `field()`:

```python
@dataclass(eq=False, init=False)
class RowItem:
    identity: ProductIdentity
    ...
```

и оставить `field(default_factory=...)` **только** если без него `dataclass`
сломает `__repr__` на неинициализированных полях. Проверить, что
`__repr__` и `parse_errors` работают после удаления `field(...)`.

Проверить заранее: `tests/test_domain/test_row_item/test_row_item_golden.py`
(332 строки) — эталон формы строки, он первым покажет, что поменялось.

### Критерии готовности

- [ ] Каждое из десяти полей объявлено в одном месте, а не в двух.
- [ ] `uv run pytest tests/test_domain/test_row_item` зелёный без правок теста.
- [ ] `test_row_item_golden.py` не потребовал изменения ожидаемых значений.

---

## Q14 — Покрытие `title_filter.py`

### Проблема

86 % — минимум по проекту (все остальные модули 93-99 %, `TOTAL` 99 %).
Непокрыты строки 15, 37 и 57-60:

- `title_filter.py:15` — `strip_words_in_title` на пустой строке;
- `title_filter.py:37` — `_parse_config` при `config is None`;
- `title_filter.py:57-60` — `set_prepared_title` целиком.

`set_prepared_title` не вызывается ни напрямую, ни через `BaseParser`
(единственный путь — `base_parser_row.py:20`, и там работает базовая версия
`BaseParser.set_prepared_title`, которая не вызывает `TitleFilter.set_prepared_title`).
То есть метод `TitleFilter.set_prepared_title` — дубль, который в
продакшн-потоке не исполняется.

### Решение

- `title_filter.py:15` — добавить в `tests/test_base_parser/test_row_filters.py`
  тест на `strip_words_in_title('')`.
- `title_filter.py:37` — тест на `TitleFilter(None)` плюс вызов метода,
  ожидающий `ParseConfigNotSetError`.
- `title_filter.py:56-60` — удалить метод как мёртвый (см. Q7) либо, если
  решаем оставить, покрыть тестом. Предпочтительно удалить: `BaseParser` уже
  имеет рабочую `set_prepared_title` (base_parser.py:260-264), дубль даёт две
  реализации одного поведения.

### Критерии готовности

- [ ] Покрытие `title_filter.py` ≥ 95 %.
- [ ] В `title_filter.py` нет метода, которого нет в графе вызовов.

---

## Порядок выполнения

Побочные эффекты задач пересекаются, поэтому порядок зафиксирован:

1. **Q9, Q10** — чистая конфигурация, ничего не трогают в `src/`. Можно начать с них.
2. **Q1, Q3** — гейты безопасности; Q1 добавит в CI то, что Q3 перестаёт
   заглушать. Сначала Q3, потом Q1, чтобы CI не начал падать на новом правиле.
3. **Q4, Q6** — точечные правки в `registry.py` и `row_processor.py`, с проверкой
   vulture после каждой.
4. **Q13** — `RowItem` крупным блоком, отдельно, с golden-тестом.
5. **Q8, Q11** — `ParserParams` и MIM связаны: `frozen=True` без одно-
   вызовного `replace` сломает вендоров. Q11 первым или одним коммитом с Q8.
6. **Q7** — после Q8, чтобы оценить, снимается ли `# noqa: WPS214`.
7. **Q12** — переименование файлов, изолировано, не требует общего контекста.
8. **Q2** — перенос заглушек; требует поправить `[tool.mutmut]`.
9. **Q5, Q14** — вместе: Q5 меняет API шаблонов, Q14 добавляет к нему тесты.

После каждой задачи — `just ci` (9 гейтов). Финальный прогон — `just ci` плюс
`./pipelines/run_mutation_test.sh`, чтобы убедиться, что набор мутантов не вырос
и score не просел.