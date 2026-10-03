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
        row_item/               ← RowItem и Value Objects (после Task-05 и #275)
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

- [x] `domain/` не имеет импортов из `core/`, `infrastructure/` или IO-библиотек.
- [x] `infrastructure/` не имеет импортов из `parsers/` (только из `domain/`).
- [x] Все IO-операции проходят через порты (protocols).
- [x] `cfg/main.py` удалён или помечен deprecated.
- [x] `core/exceptions.py` удалён или является re-export из `domain/exceptions.py`.

## Что сделано (2026-10-02)

Пакет `src/core/` удалён целиком, модули разложены по слоям:

| Откуда | Куда | Что |
| --- | --- | --- |
| `core/exceptions.py` | `domain/exceptions.py` | `CoreExceptionError`, `SupplierNotHavePricesError`, `make_raise` |
| `core/config_provider.py` | `domain/config_context.py` | `get_config_provider()` / `set_config_provider()` |
| `core/parse_paths.py` | `infrastructure/config/result_folder.py` | `clear_result_folder()` |
| `core/file_reader.py` | `infrastructure/data/file_reader.py` | `read_file`, `try_read_file` |
| `core/log_message.py` | `infrastructure/logging/log_message.py` | `log_msg`/`err_msg`/`warn_msg`/`print_log` |
| `core/log_paths.py` | `infrastructure/logging/log_paths.py` | `LogPaths`, `configure_log_paths` |
| `core/log_resolve.py` | `infrastructure/logging/log_resolve.py` | уровни, пути и методы логирования |
| `core/init_log.py` | `infrastructure/logging/log_setup.py` | `init_log` и создание папки логов |
| `core/wrappers.py` | `infrastructure/logging/wrappers.py` | декоратор `@logging` |
| `core/async_utils.py` | `services/async_utils.py` | `try_call` — перевод ошибок домена в код возврата |

Новые файлы:

- `domain/exception_log.py` — приёмник сообщений об исключениях (`ExceptionLogSink`,
  `set_exception_log_sink`, `log_exception`). Домен больше не импортирует логи и не
  знает, куда пишет: `CoreExceptionError.to_log` собирает сообщение со стеком и
  отдаёт приёмнику.
- `infrastructure/logging/exception_logging.py` — `write_exception_log`: пишет в
  лог-файл, а при недоступном логе — в `logging.error`. Регистрируется в
  `cfg.init_cfg()`.

Правки по шагам:

- `import core` в `src/parsers/xls_reader.py` заменён на прямой импорт из
  `domain.exceptions`; попутно `MaxRowsReached` → `MaxRowsReachedError` (ruff N818).
- `init_cfg()` дополнительно назначает приёмник логов исключений.
- Тесты `tests/test_core/` разложены по слоям: `tests/test_domain/`,
  `tests/test_infrastructure/`, `tests/test_services/test_async_utils.py`.
- Проверки границ слоёв живут в `tests/test_layer_boundaries.py`; добавлены запреты
  `infrastructure → parsers/cfg` и проверка, что `src/core/` больше нет.
- Конфиги обновлены: `[tool.mutmut] do_not_mutate` и `per-file-ignores` в `setup.cfg`.

Не в объёме задачи (остаётся за другими тикетами): `cfg/zapaska_api.py` читает `.env`
напрямую — перенос чтения env за порт отдельная задача.