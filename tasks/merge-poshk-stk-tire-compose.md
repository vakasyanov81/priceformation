# Объединение стратегий `poshk_tire_compose` и `stk_tire_compose`

Статус: ✅ выполнено 2026-10-14 (в рамках task-13 M4). Отличия от плана:

- `_USAGE_WORDS`/`_USAGE_PREFIXES` расширены всем словарём хвостов STK из
  боевого прайса (`вед`, `стройка`, `карьерка/вед`, `руль/ прицеп`), а не
  только `руль`/`змейка`; префиксы обобщены (`вед`, `рул`, `приц`, `карьер`).
- Канонический бренд заменяет только начало токена: `Алтайшина-421`,
  `КАМА-310` сохраняют слитную модель (`_canonical_brand`).
- Исправлен суффикс размера: `C`/`LT` только отдельной буквой — раньше
  `205/55R16 Cordiant` давал `205/55R16C ordiant` (ошибка была в обоих хелперах).
- `PoshkStkTireCompose(fallback_brand, brand_probe)` — без дефолтов: реестр
  передаёт их всегда.
- Документация — `README.md` (отдельного `README_MarkupRules.md` нет).

Сверка на боевых прайсах (до — `stk_tire_compose` у обоих поставщиков, без
группировки, 373 позиции): STK 25/25 без изменений; Пошк — 89 перестановок
в порядок Пионера (нагрузка перед PR), 16 позиций с исправленными полями при
том же названии (индекс `126A6` вместо модели, об/лента без размера), 35 с
исправленным названием (`Кама Кама` → `Кама И-68А`, `Кама-310`); 4 сдвоенных
размера (`165-13 /6.45-13`, `265/80-16(33х10.5-16)`) по правилу Пошка уходят
в нормализацию и теряют разобранные поля.

План работ. Итог: одна общая стратегия слота `title` — `poshk_stk_tire_compose`,
которую используют оба поставщика (СТК и Пошк). Имя выбрано в диалоге;
`tire_compose` не трогаем — оно занято variant-стратегией (MIM/Форточки).

## Контекст и корень проблемы

- Сейчас есть две почти одинаковые реализации «сборки названия шины в порядке
  Пионера»: `StkTireCompose` (`stk_title.py` + `_stk_title_helper.py`) и
  `PoshkTireCompose` (`poshk_title.py` + `_poshk_title_helper.py`).
- В реестре (`title_registry.py`) зарегистрирован только `stk_tire_compose`.
  `poshk_tire_compose` — «сирота»: класса нет в `_SIMPLE_STRATEGIES`, конфиг
  Пошка, ссылавшийся на него, был бы невалиден (поэтому ранее переключили
  `parse_config/vendors/poshk.json` на `stk_tire_compose`).
- Хелпер Пошка — надмножество: ловит обёртки (`Шина`, `а/п`, `автошина`,
  `автопокрышка`), `н.с.N`, `, шт`, `12.4L-16`, производителя из хвоста
  (`НКШЗ`/`БШК`/`ОШЗ`/`ЯШЗ`/`ВолШЗ`), бренд-заглушку. Хелпер STK проще.
- Различия, которые нужно reconcil-нуть при слиянии:
  - хвостовые маркеры STK `руль`, `змейка` отсутствуют в `_USAGE_WORDS` Пошка;
  - STK переопределяет бренд каноническим `row_item.identity.manufacturer`,
    Пошк — нет;
  - `_LOAD_SPEED` Пошка богаче (`[A-Za-z]\d?`, `111A6`), размер Пошка
    поддерживает low-profile `L` (`12.4L-16`).

## Решение

Один хелпер + один класс стратегии. За основу берём парсер Пошка (надмножество)
и добавляем к нему маркеры STK; бренд перекрываем каноническим производителем
(поведение STK — надмножество, Пошк-примеры без `manufacturer` не меняются).

### Шаг 1. Общий хелпер

Слить `_stk_title_helper.py` + `_poshk_title_helper.py` →
`src/parsers/strategies/_tire_title_parser.py`:

- dataclass `TireTitleParts`, функции `parse_tire_title`,
  `fill_tire_fields`;
- базовый разбор и сборка — из Пошка (`PoshkTitleParts.compose`, `_resolve_fields`,
  `_compose_model`, `_prepare_text`, `_clean_tokens`, `_merge_pr`,
  `_strip_kind_suffix`, `_size_label` с low-profile);
- в `_USAGE_WORDS` добавить STK-маркеры `руль`, `змейка`;
- сохранить `from_ship`/`_LEADING_SHIP` (нужны для `fallback_brand` Пошка);
- удалить `_stk_title_helper.py` и `_poshk_title_helper.py`.

Проверка: все примеры склейки STK и Пошка из тестов дают прежний результат.

### Шаг 2. Общая стратегия

Слить `stk_title.py` + `poshk_title.py` → `src/parsers/strategies/poshk_stk_title.py`,
класс `PoshkStkTireCompose`:

- `__init__(fallback_brand='', brand_probe=None)` — как у Пошка;
- `prepare`: разбор `parse_tire_title`; при `None` или «Шина без бренда» —
  `NormalizeSizeChunks` (fallback); иначе `fill_tire_fields` и
  `parts.compose(row_item.identity.manufacturer)` (бренд — как у STK);
- удалить `stk_title.py` и `poshk_title.py`.

### Шаг 3. Реестр

`src/parsers/strategies/title_registry.py`:

- импорт `PoshkStkTireCompose`;
- в `_AVAILABLE` заменить `stk_tire_compose` на `poshk_stk_tire_compose`;
- в `_SIMPLE_STRATEGIES` убрать `stk_tire_compose`;
- в `_build_strategy` добавить ветку (как у `normalize_size_chunks`):
  `poshk_stk_tire_compose` → `PoshkStkTireCompose(config.fallback_brand, probe)`,
  где `probe = _brand_probe()` только при заданном `fallback_brand`.

### Шаг 4. Конфиги

- `parse_config/vendors/stk.json`: `title.strategy` → `poshk_stk_tire_compose`.
- `parse_config/vendors/poshk.json`: `title.strategy` → `poshk_stk_tire_compose`
  (без `fallback_brand`).
- Эталонные копии `tests/parse_config_example/vendors/stk.json` и
  `integration_tests/parse_config_example/vendors/stk.json` — тот же апдейт
  (сейчас там `stk_tire_compose`).

### Шаг 5. Тесты

- Слить `test_stk_title_helper.py` + `test_poshk_title_helper.py` →
  `test_tire_title_parser.py` (импорт новых имён, те же кейсы).
- Слить `test_stk_title.py` + `test_poshk_title.py` →
  `test_poshk_stk_title.py` (класс `PoshkStkTireCompose`).
- `test_title_registry.py`: заменить `('stk_tire_compose', StkTireCompose)` на
  `('poshk_stk_tire_compose', PoshkStkTireCompose)`.
- Удалить 4 старых тест-файла.
- Цель — покрытие ≥ 95% (CI `--cov-fail-under=95`), желательно 100% нового кода.

### Шаг 6. Документация

- `README_MarkupRules.md`, таблица `title`: добавить строку
  `poshk_stk_tire_compose` (сборка названия шины в порядке Пионера: СТК и Пошк;
  опционально `fallback_brand`).

## Проверки (из CI / justfile)

1. `uv run pytest`
2. `uv run black --check --diff .`
3. `uv run ruff check .`
4. `uv run flake8 .`
5. `uv run mypy .`
6. `uv run lint-imports`
7. `uv run vulture`
8. `uv run bandit -r src -c pyproject.toml`
9. `uv run pip-audit`

## Риски

- Расхождение поведения при слиянии model/usage: закрывается union-тестами
  (оба набора примеров должны проходить через один класс).
- Покрытие: удаление кода вместе с тестами сохраняет долю; новый общий код
  должен быть покрыт полностью.
- `from_ship`/`fallback_brand` нельзя выкидывать «за ненадобностью» — иначе
  `vulture` пометит мёртвый код; ветка реестра сохраняет возможность.
