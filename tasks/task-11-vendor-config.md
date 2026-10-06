# Task-11: Поставщики целиком в конфигурации (один BaseParser)

## Проблема

Специфика каждого поставщика размазана по коду и конфигам:

- **Колонки, старт-роу, листы, шаблоны файлов** захардкожены в
  `src/parsers/vendors/*` — 11 классов-парсеров (stk, poshk, pioner, autosnab54,
  mim-1/2/3sheet, four_tochki-1/2sheet, zapaska-disk/tire). Новый поставщик =
  новый Python-модуль + декоратор `@register_vendor` + правка
  `registry._VENDORS_TO_IMPORT` + `config_name_map`.
- **Специфика ценообразования** наполовину в JSON
  (`<supplier>_markup_rules.json`), наполовину в коде: политика выбирается
  строкой в декораторе (`markup_policy='map_on_opt'`), грузовые наценки Мим
  (порог 13000 → 7 %/5 %) вообще захардкожены константами с TODO «вынести в
  настройки» (`mim_2sheet.py:14-16`).
- **Поведение** (категории, title, остатки, порядок шагов) — переопределения
  хуков `BaseParser` в каждом вендорском классе.
- **Два идентификатора**: код реестра (`mim-1sheet`) ≠ ключ `vendor_list.json`
  (`mim`); резолв конфига хрупкий (три источника + `config_name_map`).
- Побочные следствия: у STK нет `stk_markup_rules.json` и при `enabled: 1` он
  падает; секция `api` с логином/паролем лежит мёртвым грузом в
  `four_tochki_markup_rules.json`.

Цель: остаётся **один `BaseParser`**, поведение которого целиком описывается
конфигом `parse_config/vendors/<folder>.json`. Пользователь добавляет нового
поставщика: кладёт JSON + прайс в `file_prices/<folder>/` — без правки кода.

## Решение

### 1. Схема конфига: один файл = одна папка поставщика

`parse_config/vendors/<folder>.json`:

```json
{
  "enabled": 1,
  "code": "4",
  "name": "Мим",
  "start_row": 2,
  "file_templates": ["price*.xls", "price*.xlsx"],
  "reader": "xls",
  "pricing": {
    "policy": "base",
    "rules": {
      "markup_rules": { "rule_22": { "min": 0, "max": 5001, "percent": 0.20 } },
      "min_recommended_percent_markup": 0.15,
      "max_recommended_percent_markup": 0,
      "absolute_markup_rules": { "min_absolute_markup": 300, "markup_percent": 1.3 }
    }
  },
  "behavior": {
    "min_rest": 4,
    "rest": "count",
    "find_manufacturer_on_enrich": true,
    "pipeline": ["title", "min_rest", "category", "markup"]
  },
  "sections": [
    {
      "id": "4",
      "name": "Мим",
      "sheet_info": "Вкладка #1",
      "sheet_indexes": [0],
      "columns": { "0": "code", "1": "title", "19": "price_opt" },
      "category": { "strategy": "fixed", "value": "Легковая шина" },
      "title": { "strategy": "tire_compose", "variant": "mim_simple" }
    },
    {
      "id": "4",
      "sheet_indexes": [1],
      "pricing": {
        "policy": "percent_by_threshold",
        "rules": { "threshold": 13000, "low": 0.07, "high": 0.05 }
      }
    }
  ]
}
```

Уровни:

- **supplier** — `enabled`, `code`/`name` (дефолт для секций), `start_row`,
  `file_templates`, `reader` (`xls` | `json`), `pricing` и `behavior` по
  умолчанию.
- **section** — лист/файл: `sheet_indexes`, `columns`, свои `id`/`name`,
  `category`, `title` и переопределение `pricing`.

Ключевые решения:

- **`columns`** — строковые ключи (`"1": "code"`); для `reader: "json"` —
  маппинг JSON-ключей, как сегодня в Запаске (`cae → code_art`).
- **`pricing.rules`** — содержимое `<supplier>_markup_rules.json` переносится
  внутрь; **`enabled`** переезжает из `vendor_list.json`. Оба старых файла
  удаляются.
- **`id`/`name` на уровне секции** — сохраняет все 8 внешних ИД каталога
  (`1, 2, 22, 3, 4, 5, 6, 7`) и имена «Запаска (диски)/(шины)»:
  `get_supliers`/`load_supplier_prices` продолжают отдавать те же записи.
  Реестровые коды вида `mim-1sheet` исчезают (используются только в тестах и
  `parse_vendor`, который не завязан на CLI).
- `row_item_adaptor`, `stop_words` из `ParserParams` выпадают: всегда `RowItem`;
  стоп-слова идут из `black_list` (уже так, поле не читается).
- Секция `api` с кредами из `four_tochki_markup_rules.json` не переносится —
  мёртвая, удаляется.

### 2. Каталог стратегий: `src/parsers/strategies/`

Именованные стратегии, реестр `имя → фабрика`; неизвестное имя →
`ConfigValidationError` с именем файла и путём до ключа. Новый поставщик
составляется из конфига, если хватает существующих стратегий; действительно
новое поведение = добавить стратегию в библиотеку (код).

| Слот | Стратегии | Откуда взято |
|---|---|---|
| `category.strategy` | `none` — не менять; `fixed` (+`value`); `title_keywords` (+`map`, +`default`); `field_map` (+`field`, +`map`, +`default`); `column_canonical` (+`unknown_skip`); `header_rows` (+`zero_rest_categories`) | base; mim, four_tochki-2, zapaska-disk; poshk; four_tochki-1; zapaska-tire; pioner |
| `title.strategy` | `default`; `normalize_size_chunks`; `fill_fields_from_title`; `tire_compose` (variants: `mim_simple`, `mim_truck`, `four_tochki`); `disk_compose_four_tochki`; `manufacturer_from_category`; флаг `aliases` (читает `title_aliases.json`) | base; poshk; autosnab; mim-1/2, four_tochki-1; four_tochki-2; pioner; zapaska |
| `pricing.policy` | `base`; `identity`; `map_on_opt`; `recommended_or_map`; **`percent_by_threshold`** (+`threshold`/`low`/`high` — новый, снимает TODO в `mim_2sheet`) | `markup_policy.py` + mim-2sheet |
| `behavior.rest` | `count` (остаток как есть); `minus_reserve` (`rest - reserve`) | base; pioner |
| `behavior.pipeline` | упорядоченный список шагов `title / min_rest / category / markup` | переопределение `process_parsed_row` у pioner |

Флаги `behavior`:

- `min_rest: 0` — отключает отсечку (сегодня: пошк пустым хуком, autosnab
  `get_min_rest_count() = 0`; эквивалентность проверить тестами);
- `skip_markup_without_opt` — пустой закуп не трогает строку (zapaska);
- `zero_rest_without_category` — нет категории → остаток 0 (zapaska);
- `collect_missing_recommended` — собирать строки без РРЦ в
  `not_matched_position` (zapaska);
- `find_manufacturer_on_enrich` (pioner: `false`).

### 3. BaseParser — config-driven

- Хуки (`category_for`, `get_prepared_title`, `skip_by_min_rest`,
  `get_item_rest`, `add_price_markup`, `after_row_mapped`, порядок
  `process_parsed_row`) резолвятся в стратегии из конфига секции — наследников
  `BaseParser` больше нет.
- `ParserParams` собирается из `VendorConfig` (функция, не ручной объект в
  модуле вендора).
- Форма `make_parser` / `ParseOrchestrator` / `VendorEntry =
  tuple[type[BaseParser], ParseConfiguration]` сохраняется — оркестратор
  меняется минимально (`vendor_markup_policy_for` читает policy из конфига, а
  не из атрибута класса).

### 4. Реестр из конфигов

`src/parsers/registry.py`:

- вместо декоратора `@register_vendor` и ленивого `_VENDORS_TO_IMPORT` — скан
  `parse_config/vendors/*.json` (кэш, инвалидация — как у других провайдеров);
- `vendor_entry_for(id)` находит секцию по `id`; `all_vendors()` строит записи
  по секциям;
- удаляются `register_vendor`, `config_name_map`,
  `_get_config_for_vendor`/`_config_from_*` (три хрупких источника конфига),
  `vendor_list.py` (провайдер `vendor_list.json`);
- `enabled` читается из конфига поставщика (`vendor_config_is_enabled`
  становится тривиальным).

## Миграция 11 парсеров → 7 конфигов

| Было | Становится |
|---|---|
| `stk` (только params) | конфиг `stk`: columns, `map_on_opt`, id 7 |
| `poshk` | title `normalize_size_chunks`, category `title_keywords`, `min_rest: 0`, `map_on_opt` |
| `pioner` | `pipeline: ["category","min_rest","markup","title"]`, category `header_rows` (+`zero_rest_categories: ["прочие"]`), rest `minus_reserve`, title `manufacturer_from_category`, `find_manufacturer_on_enrich: false` |
| `autosnab54` | title `fill_fields_from_title`, `min_rest: 0`, `identity` |
| `mim-1/2/3sheet` | 3 секции в одном конфиге; у секции 2 свой `pricing` (`percent_by_threshold`) |
| `four_tochki-1/2sheet` | 2 секции; category `field_map`/`fixed`, title `tire_compose(four_tochki)`/`disk_compose_four_tochki`, `recommended_or_map` |
| `zapaska-disk/tire` | `reader: "json"`, 2 секции (файлы `disk.json`/`tire.json`, id 2/22), category `fixed`/`column_canonical`, `aliases: true`, флаги пропусков |

## План миграции (этапы)

1. ✅ **Схема и загрузчик** — модели `VendorConfig` / `VendorSection` (frozen
   dataclass, `from_dict` с путём до ключа, примитивы из
   `parsers/vendor_config/fields.py`), провайдер `parse_config/vendors/*.json`
   с кэшем. Тесты валидации. Существующие парсеры не трогаем.
   Готово: `src/parsers/vendor_config/`, `tests/test_parsers/test_vendor_config/`,
   сброс кэша в `tests/conftest.py`.
2. ✅ **Библиотека стратегий** — перенести поведение вендоров из `vendors/` в
   именованные стратегии порциями (category → title → pricing → rest/pipeline),
   юнит-тест на каждую; старые парсеры временно делегируют стратегиям —
   существующие тесты фиксируют поведение.
   Готово: `src/parsers/strategies/` (12 модулей, 6 category + 7 title + 5 pricing
   + 2 rest + pipeline), `tests/test_parsers/test_strategies/` (8 файлов, 75 тестов),
   демо интеграции `src/parsers/base_parser/strategies_integration.py`.
3. ✅ **BaseParser → config-driven** — хуки резолвятся в стратегии;
   `ParserParams` собирается из `VendorConfig`; `vendor_markup_policy_for`
   читает policy из конфига.
   Готово: `StrategyHooks` (стратегии → хуки BaseParser),
   `parser_params_from_section()`, `vendor_markup_policy_from_config()`,
   `strategy_hooks_from_section()`, `make_config_driven_parser()`;
   9 тестов на делегирование хуков и pipeline.
4. ✅ **Реестр из конфигов** — скан `vendors/*.json`, `vendor_entry_for(id)` по
   секциям; удалить `register_vendor`, `config_name_map`, `_VENDORS_TO_IMPORT`,
   `vendor_list.py`.
5. **Миграция данных** — 7 конфигов + удаление `vendor_list.json` и
   `*_markup_rules.json`; `load_config` принимает подпапку `vendors/`;
   parity-прогон старого и нового кода на интеграционных фикстурах
   (`integration_tests/`) — результаты идентичны.
6. **Снос легаси** — `src/parsers/vendors/**` (~1000 строк), устаревшие
   провайдеры; обновить `tests/test_architecture_markers.py` (маркер
   `parse_config.parser_params`), `AGENTS.md`, `README`.
7. **Полный CI** — `just ci`.

## Критерии готовности

- [ ] `src/parsers/vendors/` отсутствует; в `src/` ровно один парсер —
      `BaseParser`.
- [x] 7 конфигов в `parse_config/vendors/`; `vendor_list.json` и
      `*_markup_rules.json` удалены.
- [ ] Новый поставщик = 1 JSON без правки Python: подтверждается тестом
      (фиктивный конфиг поднимается и парсит фикстуру).
- [x] Внешние ИД каталога не изменились: 8 записей, zapaska → `2`/`22`,
      `get_supliers` отдаёт те же данные.
- [x] Грузовые наценки Мим заданы конфигом (`percent_by_threshold`), TODO в
      `mim_2sheet` исчез вместе с файлом.
- [ ] Существующие тесты вендоров переписаны на конфиги и зелёные; parity на
      интеграционных фикстурах.
- [x] `just ci` зелёный (pytest ≥ 95 %, black, ruff, flake8, mypy,
      lint-imports, vulture, bandit, pip-audit).

## Риски / тонкие места

1. **Пионер** — stateful-категории из заголовочных строк + перестановка шагов
   `pipeline`; самая хрупкая миграция. Текущие тесты = спецификация.
2. **Title-композиции** (Форточки-диски, Мим) — точность переноса; только
   тесты на золотые строки.
3. **`percent_by_threshold` против `mim_2sheet`** — разница в записи
   `percent_markup` (map% × 100 против вычисления после округления цены);
   сверить с `tests/.../test_parse_mim_sheet2.py`.
4. **`min_rest: 0` против «отключённого» min-rest пошк** — проверить
   эквивалентность (пустой хук vs `apply_min_rest(rest, 0)`).
5. **Покрытие 95 %** — стратегии пишутся только вместе с тестами; старые
   тесты вендоров переписываются, а не выбрасываются.
6. **Порядок `pipeline`** — дефолт = текущий порядок base
   (`title → min_rest → category → markup`); отклонения — только явным
   списком в конфиге.

## Что НЕ делаем

- Не вводим мини-DSL (regex/выражения прямо в конфиге): сложное поведение —
  именованные стратегии в коде, конфиг ссылается по имени.
- Не сохраняем fallback на старые `vendor_list.json` /
  `<supplier>_markup_rules.json` — переход полный, параллельной поддержки двух
  схем нет.
- Не трогаем writer/шаблоны вывода, группировку, `RowItem` — они уже
  отделены.
- Не типизируем `manufacturer_aliases.json` / `title_aliases.json` (вне
  объёма, как в task-08).
