# 16. Title aliases через parse_paths — подробно

Краткая задача: [16-parse-paths-aliases.md](../16-parse-paths-aliases.md)  
Зависит от: [14-detail](14-writer-layers-detail.md)

## Суть проблемы

`zapaska_disk_json.py`:

```python
from cfg.main import MainConfig

def _load_title_aliases(supplier_name: str) -> dict:
    raw = json.loads(read_file(MainConfig().title_aliases_file_path)) or {}
    return invert_map(raw.get(supplier_name) or {})
```

Единственный remaining импорт `cfg` в disk-парсере после выноса HTTP (15 — tire). Остальной конфиг пользователя (`markup_rules`, `black_list`, aliases производителей) идёт через `get_parse_paths().config_file(name)`. Title aliases — тот же `parse_config/title_aliases.json`, но путь собран в `MainCfg.title_aliases_file_path` как конкатенация строк с `os.sep`.

Ключ в JSON — `supplier.name` («Запаска (диски)»), не folder `zapaska`. Tire-парсер наследует `__init__` диска и грузит aliases по **своему** `supplier.name` («Запаска (шины)»). Файл может содержать две секции. Сохранить ключ = `name`, не folder, пока не доказано обратное.

`FileNotFoundError` → `{}` (молча пусто). Это поведение сохранить.

`invert_map`: `{correct: [incorrect, ...]}` → `{incorrect: correct}` для подмены title.

## Подробное решение

1. `get_parse_paths().config_file("title_aliases.json")` (имя как `__TITLE_ALIASES_FILE_NAME__` в cfg.main — сверить строку `title_aliases.json`).

2. Удалить `from cfg.main import MainConfig`.

3. Опционально: перенести загрузку в `data_provider` по образцу `manufacturer_aliases.py` (`TitleAliasesProvider`), чтобы vendor не делал JSON сам. Это лучше DIP, но не обязательно, если достаточно смены пути. Минимум — `config_file`. Полный provider — предпочтительно, чтобы не плодить `_load_title_aliases` в vendors.

4. Тест: без файла → пустой dict; с JSON секцией имени поставщика → invert; `MainConfig` не импортируется (grep).

5. `init_cfg()` в тестах парсера по-прежнему нужен, если `get_parse_paths` не сконфигурирован — как у black_list.

## Ожидаемый результат

- `grep cfg` по `zapaska_disk_json.py` пуст.
- Подмена title по aliases как сейчас.
- Нет файла → пустые aliases, разбор не падает.

## Риски

- Сменить ключ на folder_name — шины и диски разделят одну секцию или потеряют aliases.
- `MainConfig()` создаёт объект с путями от `__file__` пакета cfg, не от `configure_parse_paths`. В тестах с подменённым `parse_config` example сейчас aliases могли читаться **не** из example, а из прод-пути проекта. После перехода на `get_parse_paths()` тесты станут последовательными — проверить, не «чинили» ли скрыто прод-файлом. Это исправление слоя, возможны сюрпризы в тестах Zapaska title.
