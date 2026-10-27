# Task-22: Остаточный долг после task-21 (`parsers/base_parser`)

Вынесено из [task-21](./task-21-base-parser-composition.md): к ней эти пункты не относились, но всплыли при разборе `BaseParser` на коллабораторов. Каждый пункт — отдельный мелкий коммит (одна причина — один фикс).

## Проблема

1. **`# noqa: WPS214` без `FIXME`** (нарушение правила AGENTS.md «Подавление линт/типов» для `src/`):
   - `title_filter.py:23` — `TitleFilter`;
   - `protocols.py:44` — `TitleFilterProtocol`;
   - `row_processor.py:44` — `RowProcessor` (4 метода, подавление, скорее всего, устарело).
2. **`ParserSettings.set_parse_config` вызывается только из тестов.** `TitleFilter` держит ссылку на конфиг, переданный при создании, и после смены конфига остаётся на старом (раньше `ParserCore.set_parse_config` сбрасывал его кэш, но не подменял конфиг).
3. **`PriceFiles.type_production` только записывается** (`read_rows`), в `src/` нигде не читается; его проверяет один тест. Не путать с `RowItem.vendor.type_production`.
4. **Дублирование знания о `ParseConfiguration`.** `registry.vendor_config_is_enabled` дублирует `ParseConfiguration.is_enabled`; `services/vendor_parser.py:15-16` читает приватные `_vendor_section` / `_vendor_config` через `getattr`; `registry.py` пишет их присваиванием (`parse_config._vendor_section = ...`).

## Решение

1. **WPS214.** Найти роли, которые смешаны в классе, и разрезать (как `CategoryService` → `CategoryLookup` + `CategoryService` в task-21). `TitleFilter`: чёрный список / стоп-слова / проверка допустимости; `TitleFilterProtocol` повторяет его границу. Для `RowProcessor` сначала снять `noqa` и проверить, нужен ли он вообще. Директиву снять в том же коммите.
2. **`set_parse_config`.** Убрать метод и переписать три теста (`test_manufacturer_cache.py`, `test_row_filters.py`, `test_parser_settings.py`) на создание нового `ParserSettings`. Если же смена конфига нужна, то `TitleFilter` должен получать конфиг из `ParserSettings`, а не копировать ссылку.
3. **`type_production`.** Удалить поле и `type_production_from_filename` вместе с тестами (или подтвердить, что читатель нужен, и тогда добавить его).
4. **`ParseConfiguration`.** Дать явный способ задать секцию и конфиг вендора (конструктор или метод `with_vendor(section, config)`) и читать их публичными свойствами; перевести `registry.py` и `services/vendor_parser.py`; `vendor_config_is_enabled` удалить в пользу `ParseConfiguration.is_enabled`.

Ограничение: вывод парсеров не меняется (`integration_tests/test_parity_vendor_config.py`); подавления не добавляются.

## План

1. Пункт 3 (самый мелкий, удаление).
2. Пункт 2.
3. Пункт 1: `RowProcessor`, затем `TitleFilter` и `TitleFilterProtocol`.
4. Пункт 4.

После каждого шага — полный набор проверок из AGENTS.md; коммит только после подтверждения.

## Критерии готовности

- [ ] В `src/parsers/base_parser/` нет `# noqa: WPS214`.
- [ ] `ParserSettings.set_parse_config` и `PriceFiles.type_production` удалены или обоснованно используются в `src/`.
- [ ] `getattr(..., '_vendor_section' | '_vendor_config')` в `src/` нет; `vendor_config_is_enabled` удалена.
- [ ] Вывод парсеров не изменился.
- [ ] Проверки по AGENTS.md проходят по всему репозиторию (exit 0).
