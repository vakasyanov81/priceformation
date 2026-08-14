# mutmut_stats

Собирает детерминированную статистику по результатам [mutmut](https://github.com/boxed/mutmut):
кто выжил, какие изменения повторяются, какие тесты вообще не задевают функцию.

Запускать из корня репозитория.

## Подготовка

Сначала нужен каталог `mutants/` после прогона mutmut:

```bash
uv run mutmut run
```

Конфиг mutmut — в `pyproject.toml` (`[tool.mutmut]`). Источник мутаций — `src/`, тесты — `tests/`.

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

**Сводка** — сколько мутантов в каждом статусе и mutation score:
`killed / (killed + survived)`.

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
