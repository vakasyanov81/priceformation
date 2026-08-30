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

Флаги:

- `--json` — одна JSON-строка в stdout, логи не печатаются
- `--all-result` — в JSON включить позиции разбора (без флага — только статистика). Сам по себе тоже включает JSON-режим

Без `--json` та же команда выполняется как в меню (человекочитаемый вывод).

Код выхода: `0` при успехе, `1` при ошибке. В JSON всегда одни и те же ключи: `ok`, `action`, `took` (например `"12 seconds"`), `stats`, `files`, `warnings`, `suppliers`, `positions`, `error`.

```
uv run --no-dev --locked python src/run.py parse --json --all-result
uv run --no-dev --locked python src/run.py doubles --json
uv run --no-dev --locked python src/run.py zapaska --json
```

## Technical details:
- The library https://github.com/python-excel/xlrd is used to work with excel.
- The library https://github.com/python-excel/xlwt is used for writing to excel
