# Task-02: Dependency Injection

## Проблема

Зависимости конструируются вручную в нескольких местах:

1. **`make_parser()`** — standalone-функция, принимающая кучу опциональных параметров.
2. **`ParseConfiguration`** — создаётся через `make_parse_config()` с опциональными провайдерами.
3. **`CommonPrice`** — создаёт `CommonPriceGrouper` внутри.
4. **`CommonPriceOut`** — принимает `type[XlsWriter]`, `type[XlsxWriterDriver]` как параметры класса, но создаёт внутри writer без DI.
5. **`run_machine.py`** — в `_command_payload` создаёт `CommonPrice()` руками.

Всё это делает тестирование сложнее (нужны моки на уровне классов) и усложняет расширение.

## Решение

### 1. `ServiceProvider` — простой DI-контейнер

```python
# services/service_provider.py


class ServiceProvider:
    """Простой DI-контейнер. Регистрация через декоратор или configure()."""

    _registry: dict[type, Callable[[], Any]] = {}
    _instances: dict[type, Any] = {}

    @classmethod
    def register[T](cls, interface: type[T], factory: Callable[[], T]) -> None:
        cls._registry[interface] = factory

    @classmethod
    def resolve[T](cls, interface: type[T]) -> T:
        if interface not in cls._instances:
            factory = cls._registry[interface]
            cls._instances[interface] = factory()
        return cls._instances[interface]

    @classmethod
    def reset(cls) -> None:
        cls._instances.clear()


# configure.py — сборка графа зависимостей
def configure_services() -> None:
    ServiceProvider.register(PriceSource, FilePricesSource)
    ServiceProvider.register(VendorListProvider, VendorListProviderFromUserConfig)
    ...
```

### 2. `make_parser()` уходит в `ServiceProvider`

```python
ServiceProvider.register_factory(
    BaseParser,
    lambda: make_parser(parser_cls, config, markup_policy=...),
)
```

### 3. `CommonPrice` получает зависимости через конструктор

```python
class CommonPrice:
    def __init__(
        self,
        grouper_factory: Callable[[list[RowItem]], CommonPriceGrouper] | None = None,
        config_provider: ConfigProvider | None = None,
    ):
        self._grouper_factory = grouper_factory or CommonPriceGrouper
        ...
```

## План миграции

1. Создать `services/service_provider.py`.
2. Создать `services/configure.py` со сборкой графа.
3. `CommonPrice` — добавить DI-конструктор.
4. `CommonPriceOut` — добавить DI-конструктор.
5. `run.py` / `run_machine.py` — вызывать `configure_services()` один раз при старте.
6. Тесты — `ServiceProvider.reset()` в `conftest.py`.

## Критерии готовности

- [ ] Все зависимости конструируются через `ServiceProvider`.
- [ ] `configure_services()` вызывается один раз при старте приложения.
- [ ] Тесты не зависят от глобального контейнера (reset после каждого теста).
- [ ] `make_parser()` удалён или переведён на `ServiceProvider`.