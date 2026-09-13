# Task-10: Абстрактный ConfigProvider

## Проблема

Управление путями и окружением размазано по:

- `cfg/main.py` — `MainConfig` с десятками жёстко закодированных путей.
- `core/parse_paths.py` — `get_parse_paths()` использует `MainConfig` напрямую.
- `parsers/data_provider/vendor_list.py` — `read_file(get_parse_paths().config_file(_CONFIG_FILE))`.

Это:
- **Жёсткая привязка к файловой системе** — нельзя запустить в памяти или тесте без файлов.
- **Нет подмены для тестов** — `parse_paths.py` читает `MainConfig`, который — класс, не объект.
- **Смешение конфигурации и инфраструктуры** — `MainConfig` знает и про папки, и про имена файлов.
- **Глобальный синглтон** — `MainConfig` — это класс, менять его состояние для тестов опасно.

## Решение

### 1. `ConfigProvider` — интерфейс

```python
# domain/protocols.py


class ConfigProvider(Protocol):
    """Провайдер конфигурации окружения."""

    @property
    def project_root(self) -> str:
        """Корень проекта."""
        ...

    def config_file(self, name: str) -> str:
        """Полный путь к файлу конфигурации в parse_config/."""
        ...

    def price_folder(self, supplier_folder: str) -> str:
        """Путь к папке прайсов поставщика."""
        ...

    def result_folder(self) -> str:
        """Папка для результатов."""
        ...

    def log_folder(self) -> str:
        """Папка для логов."""
        ...
```

### 2. Реализация по умолчанию — `FileConfigProvider`

```python
# infrastructure/config/file_config_provider.py


class FileConfigProvider(ConfigProvider):
    def __init__(self, project_root: str | None = None):
        self._root = project_root or self._detect_root()
        self._user_config = f'{self._root}/parse_config'
        self._prices = f'{self._root}/file_prices'
        self._result = f'{self._prices}/result'
        self._logs = f'{self._root}/logs'

    def config_file(self, name: str) -> str:
        return f'{self._user_config}/{name}'

    def price_folder(self, supplier_folder: str) -> str:
        return f'{self._prices}/{supplier_folder}'

    def result_folder(self) -> str:
        return self._result

    def log_folder(self) -> str:
        return self._logs
```

### 3. Реализация для тестов — `FakeConfigProvider`

```python
# tests/fake_config_provider.py


class FakeConfigProvider:
    """ConfigProvider с изолированными временными папками."""

    def __init__(self, tmp_path: Path):
        self._root = tmp_path
        self._result = tmp_path / 'result'
        self._logs = tmp_path / 'logs'
        self._user_config = tmp_path / 'parse_config'
        os.makedirs(self._result)
        os.makedirs(self._logs)
        os.makedirs(self._user_config)

    def config_file(self, name: str) -> str:
        return str(self._user_config / name)

    def result_folder(self) -> str:
        return str(self._result)

    ...
```

### 4. `get_parse_paths()` становится `resolve_provider()`

```python
# services/service_provider.py (или domain/configure.py)

_provider: ConfigProvider | None = None


def get_config_provider() -> ConfigProvider:
    if _provider is None:
        _provider = FileConfigProvider()
    return _provider


def set_config_provider(provider: ConfigProvider) -> None:
    global _provider
    _provider = provider
```

## План миграции

1. Создать протокол `ConfigProvider` в `domain/protocols.py`.
2. Создать `FileConfigProvider` в `infrastructure/config/`.
3. Переписать `get_parse_paths()` на `ConfigProvider`.
4. Подменить во всех data_provider'ах прямые вызовы `get_parse_paths()` на `get_config_provider().config_file(...)`.
5. Создать `FakeConfigProvider` для тестов.
6. Добавить в `conftest.py` `set_config_provider(FakeConfigProvider(tmp_path))`.
7. Удалить `cfg/main.py` (весь конфиг теперь в `FileConfigProvider`).

## Критерии готовности

- [ ] Ни один модуль не ссылается на `MainConfig` или `cfg.main.get_config()`.
- [ ] `core/parse_paths.py` работает через `ConfigProvider`.
- [ ] Тесты могут подменить конфигурацию без файловой системы.
- [ ] При добавлении нового пути не нужно править класс-синглтон, только протокол.