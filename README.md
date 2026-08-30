## Описание скрипта

Скрипт предназначен для формирования общего прайс листа на основе набора прайс листов от поставщиков с названием позиции
отпускной ценой, остатками и другими параметрами.
Скрипт автоматически задает наценку по позициям исходя из [настроек](README_MarkupRules.md)
(поставщики, наценка, бренды, фильтры).

## Как использовать?
1. Создайте в корне проекта раздел "file_prices". Внутри данной папки необходимо разделы с  
   названиями поставщиков. 
   
2. Внутри данных разделов необходимо разместить файлы с прайс листами и остатками
   (если предусмотрено форматом).
```
file_prices
    poshk   ( имя поставщика )
        price*.xls  ( прайс лист. может содержать рекомендованную цену )
        ...
        rest*.xls  ( файл с остатками и рекомендованными ценами )
        ...
    zapaska
        price*.xls
        ...
        rest*.xls
        ...
...
```
3. Запустите скрипт "run.bat" лежащий в корне проекта.
4. В разделе "file_prices/result" будут расположены файлы с результатом работы скрипта.
```
file_prices
    result
        file_[current date].xls  ( Прайс лист для внутреннего использования )
        file_drom_[current date].xls ( прайс лист для drom.ru )
```

## CLI

Без аргументов открывается интерактивное меню. Для Django и других скриптов — подкоманда:

```
uv run --no-dev --locked python src/run.py parse --json
```

Команды:

- `parse` — разобрать прайсы поставщиков и записать файлы
- `doubles` — разобрать прайсы и записать отчёт о дублях
- `zapaska` — выгрузить прайсы запаски по API
- `get_supliers` — названия поставщиков: `{"1": {"sup_code": "poshk", "sup_title": "Пошк"}}`
- `load_supplier_prices` — загрузить прайсы в папки поставщиков: `{"1": "/full/path/any_price_name.xls"}`. Файл перемещается в `file_prices/<sup_code>/price.xls` (или `.xlsx`). Допустимы только `xls` и `xlsx`

Флаги:

- `--json` — одна JSON-строка в stdout, логи не печатаются; прайсы пишутся в `.jsonl` (те же шаблоны, что xlsx), рядом — `result_meta.json`
- `--all-result` — в JSON включить позиции разбора (без флага — только статистика). Сам по себе тоже включает JSON-режим
- `--clear-previous-result` — удалить всё из `file_prices/result` перед записью
- `--result-template NAME` — для `parse`: записать только этот шаблон (`for_inner`, `for_drom`). Без флага — все шаблоны. Неизвестное имя — ошибка (код 1; в JSON-режиме `ok: false`)

Без `--json` та же команда выполняется как в меню (человекочитаемый вывод).

Код выхода: `0` при успехе, `1` при ошибке. Для `parse` / `doubles` / `zapaska` в JSON всегда одни и те же ключи: `ok`, `action`, `stats`, `files` (пути к jsonl и `result_meta.json`), `warnings`, `suppliers` (включённые), `disabled_suppliers` (выключенные в `vendor_list.json`), `positions`, `error`.
`get_supliers` печатает каталог поставщиков: ключ — код, значение — `sup_code` (папка) и `sup_title` (название). `--json` для этой команды не обязателен.
`load_supplier_prices` тоже всегда в JSON. Успех: `ok`, `action`, `files` (пути к `price.xls` / `price.xlsx`), `suppliers` (загруженные). Ошибка: `ok`, `action`, `error`. Полей разбора (`positions`, `stats`, …) нет. Файл с диска перемещается, исходное имя не сохраняется.
Каждая строка jsonl — объект с ключами `"1"`, `"2"`, … вместо названий колонок (`price_*.jsonl`, `price_drom_*.jsonl`, `doubles_*.jsonl`). Ключи с `null` в строку не пишутся.
Расшифровка — в `result_meta.json` в той же папке: `{"1": "Тип товара", "2": "Бренд", …}`. Ключ у колонки общий для всех jsonl запуска.
Повторяющиеся строки (кроме номенклатуры) в jsonl заменяются на `"@1"`, `"@2"`, …; словарь лежит в `values`: `{"@1": "Автошина"}`. Числа (цены, остатки) не кодируются.

```
uv run --no-dev --locked python src/run.py parse --json --clear-previous-result
uv run --no-dev --locked python src/run.py parse --json --all-result
uv run --no-dev --locked python src/run.py parse --json --result-template for_drom
uv run --no-dev --locked python src/run.py doubles --json
uv run --no-dev --locked python src/run.py zapaska --json
uv run --no-dev --locked python src/run.py get_supliers
uv run --no-dev --locked python src/run.py load_supplier_prices='{"1": "/full/path/any_price_name.xls"}'
```

## Technical details:
- The library https://github.com/python-excel/xlrd is used to work with excel.
- The library https://github.com/python-excel/xlwt is used for writing to excel
