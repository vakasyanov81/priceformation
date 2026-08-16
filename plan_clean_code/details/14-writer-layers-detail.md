# 14. Writer без cfg и без I/O в конструкторе — подробно

Краткая задача: [14-writer-layers.md](../14-writer-layers.md)  
Зависит от: [11-detail](11-parser-price-source-detail.md)

## Суть проблемы

`src/parsers/writer/xls_writer.py`:

```python
from cfg import init_cfg
config = init_cfg()
```

На **импорт модуля** поднимается весь композиционный корень: пути логов, parse_paths, MainConfig. Любой `from parsers.writer.xls_writer import XlsWriter` в тесте требует/портит глобальную конфигурацию.

Конструктор:

```python
def __init__(self, driver, parse_result, template):
    create_result_folder()
    self.driver.init_workbook(config.main.result_folder_path, self.get_file_name())
    ...
    self.write()  # сразу пишет все строки и save()
```

Создание объекта = побочный эффект на диск. Нельзя собрать writer в тестах без папки `file_prices/result`. `CommonPriceOut` полагается на это: `XlsWriter(driver, rows, template)` и для doubles ещё `get_result_path()`.

`cfg` задуман как вход `run.py`. `data_provider` уже ходит в `get_parse_paths()`. Writer — единственный крупный адаптер в `parsers/`, который всё ещё импортирует `cfg` (кроме Zapaska).

`result_folder_path` сейчас `{project}/file_prices/result/`. В `ParsePaths` есть только `file_prices_folder` и `user_config_folder` — **папки result нет**. Решение: расширить `ParsePaths` полем `result_folder` (проставить в `init_cfg._configure_core_parse_paths`) **или** вычислять `Path(file_prices_folder) / "result"`. Явный аргумент `result_folder: str` в writer предпочтителен для тестов (tmpdir).

## Подробное решение

1. Удалить `from cfg import init_cfg` и модульный `config = init_cfg()`.

2. Сигнатура:

```python
class XlsWriter:
    def __init__(self, driver, parse_result, template, *, result_folder: str):
        self._result_folder = result_folder
        ...
        # НЕ вызывать write() здесь

    def write(self) -> None:
        Path(self._result_folder).mkdir(parents=True, exist_ok=True)
        self.driver.init_workbook(...)
        ...
        self.driver.save()
```

3. `CommonPriceOut` передаёт папку (из `get_parse_paths()` после расширения) и вызывает `.write()`. Для doubles — то же, затем `get_result_path()`.

4. Тесты writer: передавать tmpdir; импорт модуля без `init_cfg`. Тест: `importlib.reload` не зовёт configure (можно spy на `init_cfg` — не должен вызываться).

5. `get_file_name()` остаётся от шаблона + даты; не менять формат `file_{now}.xlsx`.

6. `run.py` по-прежнему делает `init_cfg()` первым — parse_paths будут заполнены до write.

## Ожидаемый результат

- `grep` `src/parsers/writer` — нет `cfg`.
- `import parsers.writer.xls_writer` в свежем процессе без предварительного `init_cfg` **не** падает на путях логов (сейчас `init_cfg` на import как раз это маскирует). Если `get_parse_paths` зовётся только из `CommonPriceOut.write_*`, импорт writer чистый.
- Файлы inner/drom/doubles пишутся туда же, что сейчас.
- Конструктор не создаёт xlsx; без `write()` диск пуст.

## Риски

- Тесты, которые только конструировали `XlsWriter` и ждали файл, сломаются — добавить `.write()`.
- Дата в имени файла (`%Y-%m-%d`) — не менять.
- `create_result_folder` гоняется на каждый writer (inner + drom) — mkdir exist_ok идемпотентен.
