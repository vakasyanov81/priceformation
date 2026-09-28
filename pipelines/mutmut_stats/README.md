# mutmut_stats

Собирает детерминированную статистику по результатам [mutmut](https://github.com/boxed/mutmut):
кто выжил, какие изменения повторяются, какие тесты вообще не задевают функцию.

Запускать из корня репозитория.

## Подготовка

Сначала нужен каталог `mutants/` после прогона mutmut:

```bash
pipelines/run_mutation_test.sh
```

или вручную, но с обязательной чисткой bytecode (см. «Ловушка: stale `__pycache__`»):

```bash
find src -name __pycache__ -type d -print0 | xargs -0 -r rm -rf
PYTHONDONTWRITEBYTECODE=1 uv run mutmut run
```

Конфиг mutmut — в `pyproject.toml` (`[tool.mutmut]`). Источник мутаций — `src/`, тесты — `tests/`.

## Ловушка: stale `__pycache__`

mutmut 3.8.0 правит файл в `src/` и запускает тесты, но не чистит `__pycache__`.
Если рядом лежат `.pyc` от предыдущего прогона, Python импортирует именно их:
мутированный модуль продолжает жить после того, как source уже откатили, и
mutmut объявляет мутанта убитым или, наоборот, выжившим не по той причине.
Симптом — одинаковый размер файла и та же секунда mtime при изменённом содержимом.

Что делать:

- перед прогоном и после него удалять `src/**/__pycache__`;
- запускать mutmut с `PYTHONDONTWRITEBYTECODE=1`, чтобы кэш не создавался вовсе;
- не гонять `uv run mutmut run` параллельно с `uv run pytest`: mutmut в этот момент
  патчит `src/`, и обычный прогон тестов измеряет мутированный код.

## Ловушка: тесты, зависящие от чистого `sys.modules`

mutmut начинает прогон с `--collect-only`, после чего тесты идут в том же
процессе. Если тест рассчитывает на «модуль ещё не импортирован», он падает
не на мутанте, а на clean-тестах: `Failed to run clean test`.

Так ведёт себя `tests/test_parsers/test_registry.py`: стаб-вендор лежит в
`sys.modules` после сбора тестов, `importlib.import_module()` возвращает кэш без
повторной регистрации. Тест вычищает модуль из `sys.modules` перед импортом и
сравнивает классы по имени, а не по идентичности объекта. Общее правило для новых
тестов: не полагаться на порядок импортов, либо изолировать `sys.modules` явно.

## Запуск

```bash
uv run python -m pipelines.mutmut_stats
```

По умолчанию читает `mutants/` и пишет туда же:

- `mutants/mutmut-analysis.md` — отчёт для чтения
- `mutants/mutmut-analysis.json` — тот же разбор в JSON

В stdout — краткая сводка:

```text
mutants: 120; survived: 8; score: 93.3%
written: mutants/mutmut-analysis.md
written: mutants/mutmut-analysis.json
```

Если каталога нет, утилита завершится с кодом 1 и подсказкой запустить `uv run mutmut run`.

## Опции

```bash
uv run python -m pipelines.mutmut_stats --help
```

| флаг | смысл |
| --- | --- |
| `--mutants-dir PATH` | каталог с кэшем mutmut (по умолчанию `mutants`) |
| `--output-dir PATH` | куда писать `.md` и `.json` (по умолчанию тот же `--mutants-dir`) |
| `--stdout` | полный markdown в stdout вместо краткой сводки |

Примеры:

```bash
# отчёты в отдельную папку
uv run python -m pipelines.mutmut_stats --output-dir reports/mutmut

# посмотреть отчёт в терминале
uv run python -m pipelines.mutmut_stats --stdout
```

## Что смотреть в отчёте

**Сводка** — сколько мутантов в каждом статусе и mutation score.

Формула: `score = killed / (killed + survived)`. `timeout`, `no tests` и прочие
неинтересные статусы в знаменатель не входят, поэтому score всегда выше, чем
при делении на общее число мутантов. Считать score «процентом от всех мутантов»
нельзя — цифры будут несопоставимы между прогонами.

Дальше считаются только «интересные» статусы: `survived`, `no tests`, `timeout`, `suspicious`, `segfault`.

- **Выжившие по файлам / функциям / типу** — где слабые места
- **Одинаковые изменения** — повторяющиеся правки (`== → !=`, `lower → upper`, …)
- **Карточки мутантов** — diff, связанные тесты и короткая подсказка, если мутант похож на эквивалентный

Если у карточки нет тестов, mutmut не видел вызовов этой функции из `tests/` — убивать мутанта нечем.

## Типы изменений

Классификатор смотрит на unified diff исходной и мутированной функции:

| тип | пример |
| --- | --- |
| `operator` | `== → !=`, `< → <=` |
| `method_swap` | `lower → upper` |
| `keyword` | `True → False`, `not → ∅` |
| `string_wrap` | `utf-8 → XXutf-8XX` |
| `string_case` | `utf-8 → UTF-8` |
| `number` | `0 → 1` |
| `to_none` | `title.strip() → None` |
| `none_to_empty` | `None → ""` |
| `other` / `unknown` | не распознано |

## Как пользоваться карточками

1. Откройте `mutmut-analysis.md`.
2. Начните с функций и типов с наибольшим числом выживших.
3. По diff решите: дыра в тесте или эквивалентная мутация (регистр строки, `encoding=None` и т.п.).
4. Если тестов нет — добавьте вызов функции в `tests/`, затем снова `uv run mutmut run`.
