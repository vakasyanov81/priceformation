# 11. PriceSource вместо glob в BaseParser — подробно

Краткая задача: [11-parser-price-source.md](../11-parser-price-source.md)  
Зависит от: [09-detail](09-parser-pipeline-detail.md)
Статус: сделана

## Суть проблемы

Внизу `base_parser.py`:

```python
def _glob_price_files(supplier_folder: Path, templates: list[str]) -> list[str]:
    for f_tmp in templates:
        list_files.extend(str(path) for path in supplier_folder.glob(f_tmp))

def get_file_prices(parser) -> list[str]:
    prices_root = Path(get_parse_paths().file_prices_folder)
    supplier_folder = prices_root / parser.parser_params().supplier.folder_name
    list_files = _glob_price_files(...)
    if not list_files:
        raise SupplierNotHavePricesError(...)
```

`parse()` делает `self.files = self.files or get_file_prices(self)`. Парсер знает раскладку `file_prices/<folder>/price*.xls`. Тесты уже передают `file_prices=` в конструктор (`FakeXlsReader`) — порт фактически есть, но прод-путь зашит в модуле парсера.

Это мешает: подменить источник (БД, HTTP-скачанный буфер) без правки `BaseParser`; тестировать pipeline без диска; держать SRP (парсер ≠ FS).

`get_parse_paths()` уже отделён от `cfg` — источник путей правильный; выносить нужно **glob**, не схему папок.

## Подробное решение

1. Интерфейс:

```python
class PriceSource(Protocol):
    def list_files(self, folder_name: str, templates: list[str]) -> list[str]: ...
```

Реализация `FilePricesSource`: `root / folder_name`, glob шаблонов, как сейчас. Пустой список → пусть парсер или source бросает `SupplierNotHavePricesError` с именем поставщика (имя сейчас берётся из `parser.parser_params().supplier.name` — передать в source или бросать в парсере если `not files`).

2. `BaseParser.__init__(..., price_source: PriceSource | None = None)`. Если `file_prices` уже передан — source не звать.

3. Убрать `_glob_price_files` / `get_file_prices` из `base_parser.py` (или оставить тонкую обёртку, зовущую source — лучше удалить, чтобы не было двух входов).

4. Тесты `test_file_prices.py` перевести на `FilePricesSource` + парсер с mock source. Сохранить текст ошибки «Прайсов у поставщика (Имя) не обнаружено!».

5. Не менять `file_prices/result` и имена шаблонов vendors.

## Ожидаемый результат

- В `BaseParser` нет `Path.glob`.
- Прод: тот же набор файлов в том же порядке, что `glob` по шаблонам (порядок сейчас = порядок templates, внутри — порядок pathlib; **зафиксировать**, если тесты чувствительны к порядку листов).
- Юнит-тесты парсера без реальной папки поставщика.

## Риски

- Порядок файлов: `list.extend(glob)` по каждому шаблону. `price*.xls` затем `price*.xlsx` — сохранить последовательность шаблонов.
- Zapaska templates `disk.json` / `tire.json` — тот же source, не отдельный класс в этой задаче.
- Не импортировать `cfg` в source: только `get_parse_paths()`.
