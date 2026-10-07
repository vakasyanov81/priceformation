## Описание скрипта

Скрипт предназначен для формирования общего прайс листа на основе набора прайс листов от поставщиков с названием позиции
отпускной ценой, остатками и другими параметрами.
Скрипт автоматически задает наценку по позициям исходя из [настроек](README_MarkupRules.md)
(поставщики, наценка, бренды, фильтры).

Поведение каждого поставщика целиком описывается одним JSON-файлом
`parse_config/vendors/<folder>.json`. Новый поставщик добавляется без правки
Python-кода — только конфигом и папкой с прайсами.

## Как использовать?
1. Создайте в корне проекта папку "file_prices". Внутри — подпапки поставщиков.
   Имя подпапки совпадает с именем файла конфига
   `parse_config/vendors/<folder>.json` без расширения.

2. Добавьте поставщика в `parse_config/vendors/<folder>.json` — порядок описан
   ниже в разделе «Новый поставщик», полный разбор полей — в
   [README_MarkupRules.md](README_MarkupRules.md).

3. Положите в `file_prices/<folder>/` файлы прайсов по маскам `file_templates`:
   для Excel — `price*.xls` / `price*.xlsx`, для JSON-источников — свои имена
   (у Запаски `disk.json` / `tire.json`).
```
file_prices
    poshk              ( имя папки = parse_config/vendors/poshk.json )
        price*.xls
    mim
        price*.xlsx
    zapaska            ( reader: "json" )
        disk.json
        tire.json
...
```
4. Запустите скрипт "run.bat" (на Windows) или "run.sh" (на Linux) из каталога `src`.
5. В разделе "file_prices/result" будут расположены файлы с результатом работы скрипта.
```
file_prices
    result
        file_[current date].xls  ( Прайс лист для внутреннего использования )
        file_drom_[current date].xls ( прайс лист для drom.ru )
```

## Новый поставщик
1. Создайте `parse_config/vendors/<folder>.json` (можно загрузить готовый файл
   через `load_config` — см. CLI ниже). Имя файла = имя папки в `file_prices`.
2. Задайте `enabled: 1`, `code` (ИД каталога), `name`, `start_row`,
   `file_templates`, `reader` (`xls` по умолчанию или `json`), `pricing` и хотя бы
   одну `sections` с `columns` и стратегиями `category` / `title`.
3. Положите прайсы в `file_prices/<folder>/`.
4. Перезапустите разбор. Если нужно новое поведение, которого нет среди готовых
   стратегий, — только оно требует кода (новая именованная стратегия).

Полная схема и список стратегий — в [README_MarkupRules.md](README_MarkupRules.md).

## CLI

Без аргументов открывается интерактивное меню. Для Django и других скриптов — подкоманда:

```
uv run pf parse --json
```

Команда доступна как `priceformation` и короткий алиас `pf` — это одна и та же
точка входа `src/run.py`, объявленная в `[project.scripts]`:

```
uv run priceformation parse --json
uv run pf parse --json
```

Полный список флагов — `uv run pf --help`. Из justfile то же самое: `just run`
(меню) и `just run parse --json`.

Команды:

- `parse` — разобрать прайсы поставщиков и записать файлы
- `doubles` — разобрать прайсы и записать отчёт о дублях
- `zapaska_load_api_data` — выгрузить прайсы запаски по API
- `get_supliers` — названия поставщиков: `{"1": {"sup_code": "poshk", "sup_title": "Пошк"}}`
- `load_supplier_prices` — загрузить прайсы в папки поставщиков: `{"1": "/full/path/any_price_name.xls"}` или `{"poshk": "/full/path/any_price_name.xls"}`. Ключ — ИД поставщика или `sup_code`. Файл перемещается в `file_prices/<sup_code>/price.xls` (или `.xlsx`). Допустимы только `xls` и `xlsx`
- `load_config` — загрузить файл или папку настроек: полный путь к `*.json`, `*.xlsx`, `black_list` или к папке с такими файлами. Файлы перемещаются в `parse_config` с теми же именами (существующие заменяются). Файл из папки `vendors/` кладётся в `parse_config/vendors/` — так удобно заливать конфиги поставщиков. Для `*.json` содержимое проверяется как JSON. Если в папке есть файлы другого формата — ошибка, ничего не переносится

Флаги:

- `--json` — одна JSON-строка в stdout, логи не печатаются; прайсы пишутся в `.jsonl` (те же шаблоны, что xlsx), рядом — `result_meta.json`
- `--all-result` — в JSON включить позиции разбора (без флага — только статистика). Сам по себе тоже включает JSON-режим
- `--clear-previous-result` — удалить всё из `file_prices/result` перед записью
- `--result-template NAME` — для `parse`: записать только этот шаблон (`for_inner`, `for_drom`, `for_full`). Без флага — `for_inner` и `for_drom` (`for_full` только явно). Неизвестное имя — ошибка (код 1; в JSON-режиме `ok: false`)

Без `--json` та же команда выполняется как в меню (человекочитаемый вывод).

Код выхода: `0` при успехе, `1` при ошибке. Во всех JSON-ответах с `ok` есть `elapsed_seconds` (секунды, два знака) — и при успехе, и при ошибке. Для `parse` / `doubles` те же ключи, что раньше: `ok`, `action`, `stats`, `files` (пути к jsonl и `result_meta.json`), `warnings`, `suppliers` (включённые), `disabled_suppliers` (выключенные, `enabled: 0`, в `parse_config/vendors/*.json`), `positions`, `error`; `elapsed_seconds` дублируется на верхнем уровне и в `stats`.
`zapaska_load_api_data` в JSON: успех `ok`, `action`, `elapsed_seconds`; ошибка `ok`, `action`, `error`, `elapsed_seconds`. Полей разбора нет.
`get_supliers` печатает каталог поставщиков: ключ — код, значение — `sup_code` (папка) и `sup_title` (название). `--json` для этой команды не обязателен. Каталог без `ok`/`elapsed_seconds`.
`load_supplier_prices` тоже всегда в JSON. Успех: `ok`, `action`, `files` (пути к `price.xls` / `price.xlsx`), `suppliers` (загруженные), `elapsed_seconds`. Ошибка: `ok`, `action`, `error`, `elapsed_seconds`. Полей разбора (`positions`, `stats`, …) нет. Файл с диска перемещается, исходное имя не сохраняется.
`load_config` тоже всегда в JSON. Успех: `ok`, `action`, `files` (пути в `parse_config`), `elapsed_seconds`. Ошибка: `ok`, `action`, `error`, `elapsed_seconds`. Полей разбора нет. Исходные файлы перемещаются, имена сохраняются. Из папки берутся только файлы верхнего уровня.
Каждая строка jsonl — объект с ключами `"1"`, `"2"`, … вместо названий колонок (`price_*.jsonl`, `price_drom_*.jsonl`, `price_full_*.jsonl`, `doubles_*.jsonl`). Ключи с `null` в строку не пишутся.
Расшифровка — в `result_meta.json` в той же папке: `{"1": "Тип товара", "2": "Бренд", …}`. Ключ у колонки общий для всех jsonl запуска.
Повторяющиеся строки (кроме номенклатуры) в jsonl заменяются на `"@1"`, `"@2"`, …, только если код короче значения; словарь лежит в `values`: `{"@1": "Автошина"}`. Числа и строки-числа (в том числе с точкой) не кодируются.

```
uv run pf parse --json --clear-previous-result
uv run pf parse --json --all-result
uv run pf parse --json --result-template for_drom
uv run pf parse --json --result-template for_full
uv run pf doubles --json
uv run pf zapaska_load_api_data --json
uv run pf get_supliers
uv run pf load_supplier_prices='{"1": "/full/path/any_price_name.xls"}'
uv run pf load_supplier_prices='{"poshk": "/full/path/any_price_name.xls"}'
uv run pf load_config=/full/path/vendors/mim.json
uv run pf load_config=/full/path/correct-nomenclature.xlsx
uv run pf load_config=/full/path/black_list
uv run pf load_config=/full/path/settings_dir
uv run pf load_config=/full/path/vendors
```

## Technical details:
- The library https://github.com/python-excel/xlrd is used to work with excel.
- The library https://github.com/python-excel/xlwt is used for writing to excel
