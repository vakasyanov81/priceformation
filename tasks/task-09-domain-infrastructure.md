# Task-09: Разделение core/ на domain/ и infrastructure/

## Проблема

Пакет `core/` сейчас содержит:

- **Бизнес-исключения** (`CoreExceptionError`, `SupplierNotHavePricesError`) — это чистая логика.
- **Инфраструктуру** (`file_reader.py` — IO, `init_log.py` — настройка логгера).
- **Смешанное** (`parse_paths.py` — и интерфейс, и работа с файловой системой).

Нет разделения на:
- **Domain** — сущности, порты (interfaces), бизнес-правила.
- **Infrastructure** — адаптеры к файлам, сети, логгированию.

## Решение

### 1. Новая структура

```
src/
    domain/                     ← бизнес-логика, независимая от IO
        __init__.py
        exceptions.py           ← CoreExceptionError, SupplierNotHavePricesError
        row_item.py             ← RowItem, Value Objects (после Task-05)
        markup_policy.py        ← чистые политики наценки
        protocols.py            ← Ports: ConfigProvider, DataProvider, PriceSource
        ...
    
    infrastructure/             ← реализации, работающие с IO
        __init__.py
        config/
            paths.py            ← parse_paths (но через ConfigProvider)
            file_config_provider.py
        data/
            file_reader.py      ← read_file
            xls_reader.py       ← XlsReader
            json_reader.py
        logging/
            log_setup.py
        ...
    
    parsers/                    ← остаётся без изменений (вендоры)
    
    services/                   ← оркестрация (после Task-03)
    
    cfg/                        ← можно удалить после переноса в infrastructure/config
```

### 2. Порты (interfaces) в domain

```python
# domain/protocols.py


class ConfigProvider(Protocol):
    def result_folder(self) -> str: ...
    def config_file(self, name: str) -> str: ...
    def log_folder(self) -> str: ...
    def project_root(self) -> str: ...


class DataProvider(Protocol):
    def read_text(self, path: str) -> str: ...
    def path_exists(self, path: str) -> bool: ...
```

### 3. Имлементации в infrastructure

```python
# infrastructure/config/file_config_provider.py


class FileConfigProvider:
    """ConfigProvider, основанный на файловой структуре проекта."""

    def __init__(self, project_root: str = ...):
        self._root = project_root
        self._parse_config = project_root + '/parse_config'
        ...
```

### 4. Существующий код переезжает

- `core/exceptions.py` → `domain/exceptions.py`
- `core/parse_paths.py` → `infrastructure/config/paths.py`
- `core/file_reader.py` → `infrastructure/data/file_reader.py`
- `core/init_log.py` → `infrastructure/logging/log_setup.py`
- `cfg/main.py` → удалить (заменено `FileConfigProvider`)

## План миграции

1. Создать `domain/` и `infrastructure/`.
2. Перенести `core/exceptions.py` в `domain/exceptions.py`.
3. Создать `domain/protocols.py` с портами.
4. Перенести `cfg/main.py` + `core/parse_paths.py` → `infrastructure/config/` как `FileConfigProvider`.
5. Перенести `core/file_reader.py` → `infrastructure/data/file_reader.py`.
6. Перенести `core/init_log.py` → `infrastructure/logging/log_setup.py`.
7. Оставить `core/` как re-export для обратной совместимости (или удалить после полной миграции).
8. Поправить все импорты.

## Критерии готовности

- [ ] `domain/` не имеет импортов из `core/`, `infrastructure/` или IO-библиотек.
- [ ] `infrastructure/` не имеет импортов из `parsers/` (только из `domain/`).
- [ ] Все IO-операции проходят через порты (protocols).
- [ ] `cfg/main.py` удалён или помечен deprecated.
- [ ] `core/exceptions.py` удалён или является re-export из `domain/exceptions.py`.