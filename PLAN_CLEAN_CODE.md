# План: выравнивание архитектуры под Clean Code

Цель: разделить оркестрацию, домен (наценка, нормализация) и адаптеры поставщиков.
Не менять пользовательский сценарий (`run.py`: прайс / Zapaska API / отчёт о дублях).

Не делать в рамках этого плана: DI-контейнер, пакет `services/`, веб/БД из `TODOS.md`.

Задачи лежат в [`plan_clean_code/`](plan_clean_code/). Ниже — индекс и зависимости.

## Текущее состояние

Пайплайн читается:

`run.py` → `CommonPrice` → `BaseParser` / vendors → `CommonPriceGrouper` → `CommonPriceOut` → `XlsWriter`

Ломает Clean Code:

- **SRP** — `BaseParser` оркестрирует именованные шаги pipeline; glob ещё в `get_file_prices` ([11](plan_clean_code/11-parser-price-source.md)), JSON/HTTP Zapaska — [12](plan_clean_code/12-parser-json-reader.md)/[15](plan_clean_code/15-zapaska-http.md).
- **OCP / DRY** — новый поставщик = правка `all_vendors.py` + копипаста `ParseConfiguration` в 12 файлах.
- **DIP** — `xls_writer` и Zapaska импортируют `cfg`; HTTP живёт внутри парсера JSON.
- Наценка: политики в `markup_policy.py` (Mim, map-on-opt, identity, recommended-or-map, Zapaska через флаги JSON). Vendors задают mapping; Mim sheet2 ещё со своим override грузовых % (вне этапа 1).

Критерий готовности плана: vendors задают только mapping колонок и хуки title/category; наценка и I/O — за отдельными портами. Закрывается задачей [18](plan_clean_code/18-demeter.md).

## Индекс задач

| ID | Задача | Этап | Статус |
| --- | --- | --- | --- |
| [01](plan_clean_code/01-markup-policy.md) | Вынести `MarkupPolicy` | 1 | сделана |
| [02](plan_clean_code/02-markup-poshk-pioner.md) | Poshk / Pioner на общую политику | 1 | сделана |
| [03](plan_clean_code/03-markup-stk.md) | STK: наценка в JSON | 1 | сделана |
| [04](plan_clean_code/04-markup-zapaska.md) | Zapaska: наценка в JSON | 1 | сделана |
| [05](plan_clean_code/05-markup-autosnab.md) | Autosnab: политика «без наценки» | 1 | сделана |
| [06](plan_clean_code/06-markup-cleanup.md) | Очистка `BaseParser` и контракт JSON | 1 | сделана |
| [07](plan_clean_code/07-config-factory.md) | Фабрика `make_parse_config` | 2 | сделана |
| [08](plan_clean_code/08-config-cache.md) | Кэш наценки на экземпляре | 2 | сделана |
| [09](plan_clean_code/09-parser-pipeline.md) | Явный pipeline парсера | 3 | сделана |
| [10](plan_clean_code/10-parser-hooks.md) | Хуки vendors вместо циклов `process()` | 3 | не начата |
| [11](plan_clean_code/11-parser-price-source.md) | `PriceSource` вместо glob | 3 | не начата |
| [12](plan_clean_code/12-parser-json-reader.md) | JSON reader для Zapaska | 3 | не начата |
| [13](plan_clean_code/13-parser-dead-code.md) | Мёртвый Command, title, Пионер | 3 | не начата |
| [14](plan_clean_code/14-writer-layers.md) | Writer без cfg и I/O в конструкторе | 4 | не начата |
| [15](plan_clean_code/15-zapaska-http.md) | HTTP-клиент Zapaska вне парсера | 4 | не начата |
| [16](plan_clean_code/16-parse-paths-aliases.md) | Title aliases через `parse_paths` | 4 | не начата |
| [17](plan_clean_code/17-process-caches.md) | Предсказуемые кэши процесса | 4 | не начата |
| [18](plan_clean_code/18-demeter.md) | Law of Demeter для `ParseConfiguration` | 4 | не начата |

---

## Этап 1. Единая политика наценки

**Зачем.** Смена правила сейчас требует правок в базовом классе и в нескольких поставщиках. JSON `markup_rules` для части vendors игнорируется.

**Задачи**

1. [01. Вынести MarkupPolicy](plan_clean_code/01-markup-policy.md) — **сделана**
2. [02. Poshk / Pioner](plan_clean_code/02-markup-poshk-pioner.md) — после 01 — **сделана**
3. [03. STK в JSON](plan_clean_code/03-markup-stk.md) — после 01 — **сделана**
4. [04. Zapaska в JSON](plan_clean_code/04-markup-zapaska.md) — после 01 — **сделана**
5. [05. Autosnab без наценки](plan_clean_code/05-markup-autosnab.md) — после 01 — **сделана**
6. [06. Очистка и контракт](plan_clean_code/06-markup-cleanup.md) — после 02–05 — **сделана**

02–05 можно вести параллельно после 01.

**Готово, когда** нет дублирующих формул в vendors; диапазоны Zapaska/STK меняются JSON-ом; `uv run pytest` зелёный.

**Не делать:** общий рефакторинг `process()`, смена колонок, HTTP Zapaska.

---

## Этап 2. Фабрика конфига поставщика

**Зачем.** 12 одинаковых блоков `BasePriceParseConfigurationParams`. Ошибка в одном провайдере размножается.

**Задачи**

1. [07. Фабрика `make_parse_config`](plan_clean_code/07-config-factory.md) — **сделана**
2. [08. Кэш на экземпляре](plan_clean_code/08-config-cache.md) — **сделана**

**Готово, когда** блок провайдеров один; новый поставщик не копирует 7 строк; кэш не шарится между vendors.

**Не делать:** plugin/entry points, ленивая загрузка vendors, смена `vendor_list.json`.

---

## Этап 3. Разрезать `BaseParser`

**Зачем.** `parse`/`process` — два комка без имён шагов. Хук `process_parsed_row` уже есть (наценка, skip rest, category), но Mim/FourTochki/остальные vendors всё ещё дублируют тело хука; glob и JSON-чтение живут в парсере.

**Задачи**

1. [09. Pipeline](plan_clean_code/09-parser-pipeline.md) — после [06](plan_clean_code/06-markup-cleanup.md)
2. [10. Хуки vendors](plan_clean_code/10-parser-hooks.md) — после 09
3. [11. PriceSource](plan_clean_code/11-parser-price-source.md) — после 09
4. [12. JSON reader](plan_clean_code/12-parser-json-reader.md) — после 09
5. [13. Мёртвый код / title / Пионер](plan_clean_code/13-parser-dead-code.md) — после 10

11 и 12 можно параллельно после 09.

**Готово, когда** `BaseParser` оркестрирует шаги без формул наценки и glob; vendors без копипасты цикла; фикстуры без регрессий.

**Не делать:** вынос HTTP Zapaska ([15](plan_clean_code/15-zapaska-http.md)), смена формата выходных XLSX.

---

## Этап 4. Слои и побочные эффекты

**Зачем.** `cfg` — композиционный корень. Adapters не должны его импортировать. Конструктор не должен писать файлы.

**Задачи**

1. [14. Writer](plan_clean_code/14-writer-layers.md) — после [11](plan_clean_code/11-parser-price-source.md)
2. [15. HTTP Zapaska](plan_clean_code/15-zapaska-http.md) — после [12](plan_clean_code/12-parser-json-reader.md)
3. [16. Title aliases](plan_clean_code/16-parse-paths-aliases.md) — после 14
4. [17. Кэши процесса](plan_clean_code/17-process-caches.md) — после [08](plan_clean_code/08-config-cache.md)
5. [18. Law of Demeter](plan_clean_code/18-demeter.md) — после [07](plan_clean_code/07-config-factory.md)

**Готово, когда** в `src/parsers` нет импорта `cfg` (кроме, при необходимости, `run.py`); импорт writer не вызывает `init_cfg()`; API Zapaska тестируется без парсера прайса.

---

## Порядок и зависимости

```
Этап 1 (наценка)     ── 01 → (02 ‖ 03 ‖ 04 ‖ 05) → 06
Этап 2 (фабрика)     ── 07 → 08; можно параллельно с 1
Этап 3 (BaseParser)  ── после 06: 09 → (10 → 13) ‖ 11 ‖ 12
Этап 4 (слои)        ── 14 после 11; 15 после 12; 16 после 14; 17 после 08; 18 после 07
```

Каждая задача — отдельный коммит (или PR) с зелёными `pytest` / black / ruff / flake8 / mypy / vulture по правилам репозитория.

## Вне скоупа

- Статусы номенклатуры и заливка в БД (`TODOS.md`).
- Наценка в разрезе грузовая / легковая / спецшина — после этапа 1 политика это позволит без нового God-object.
- Динамическая регистрация поставщиков (entry points) — не нужна при 11 парсерах.
- Переписывание `RowItem` (50+ полей) — DTO домена, не блокер слоёв.
