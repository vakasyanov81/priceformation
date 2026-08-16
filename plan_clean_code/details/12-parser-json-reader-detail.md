# 12. JSON reader для Zapaska — подробно

Краткая задача: [12-parser-json-reader.md](../12-parser-json-reader.md)  
Зависит от: [09-detail](09-parser-pipeline-detail.md)

## Суть проблемы

`IXlsReader.parse(sheet_indexes) -> list[dict]` — контракт сырых строк. Zapaska обходит его:

```python
def raw_parse(self, text_json_file_full_path: str) -> list[dict]:
    with Path(...).open() as f:
        loaded = json.loads(f.read())
    rename_fields(loaded, parser_params.columns)
    return loaded
```

Парсер совмещает I/O, JSON и маппинг ключей API (`cae` → `code_art`, …). `BaseParser.get_xls_reader` для Zapaska не вызывается. Тесты вынуждены класть файлы на диск или лезть в override.

`rename_fields` мутирует словари in-place (pop source keys). `column_mapping` в disk, tire копирует и дополняет height/load_index/….

HTTP загрузки файла — задача 15; здесь только **чтение уже лежащего JSON**.

## Подробное решение

1. `JsonPriceReader` (рядом с `xls_reader.py` или `parsers/json_reader.py`) с тем же духом, что `XlsReader.get_instance(path, params)`:

   - читает UTF-8 JSON;
   - ожидает `list[dict]`;
   - применяет `columns: dict[str, str]` (не int→name как xls);
   - `parse(sheet_indexes=None)` игнорирует sheet_indexes или принимает пустой список — чтобы `BaseParser.raw_parse` не ветвился.

2. Маппинг колонок остаётся в `ParserParams.columns` (уже так). Reader не знает Zapaska.

3. `ZapaskaDiskJSON` не override `raw_parse` **или** override только фабрику ридера: `xls_reader=JsonPriceReader` в конструкторе/конфиге. Лучше параметр `reader_factory` уже есть (`xls_reader: type[XlsReaderFactory]`). Расширить протокол: factory, которой всё равно xls это или json. Имя `xls_reader` лживое — в этой задаче можно не переименовывать глобально (шум), но factory должна уметь JSON.

4. `rename_fields` переехать в reader. Тест reader: вход `[{"cae": "1", "price": 10}]`, columns disk mapping → ключ `code_art` / `price_opt`.

5. Fake: список dict без диска для юнит-тестов парсера (по аналогии `FakeXlsReader`).

6. Не трогать `HTTPSConnection`.

## Ожидаемый результат

- `Path.open` + `json.loads` нет в `zapaska_disk_json.py`.
- Parse-тесты disk/tire зелёные.
- `BaseParser.raw_parse` один: `self.get_xls_reader(path).parse(sheet_indexes)`.

## Риски

- JSON объект `{}` вместо списка — сейчас `cast` проглотит и упадёт на итерации. Явная ошибка типа.
- `rename_fields` не копирует: если ключ уже в RowItem-имени и в API — проверить коллизии.
- Tire mapping обновляет копию `column_mapping` на уровне модуля — порядок import disk→tire. Не сломать.
