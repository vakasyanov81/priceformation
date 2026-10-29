"""Лёгковесный DI-контейнер приложения.

Регистрация фабрик по интерфейсу и ленивое разрешение зависимостей.
Один контейнер на процесс; ``configure_services()`` собирает граф при старте.
"""

from collections.abc import Callable
from typing import Any, cast

type _Interface = Callable[..., Any]
type _Factory[Service] = Callable[[], Service]

_factories: dict[_Interface, Callable[[], Any]] = {}
_instances: dict[_Interface, Any] = {}


class ServiceNotRegisteredError(LookupError):
    """Запрошенный интерфейс не зарегистрирован в контейнере."""


class ServiceProvider:
    """Простой DI-контейнер: фабрики по интерфейсу, ленивое разрешение."""

    @classmethod
    def register[Service](cls, interface: Callable[..., Service], factory: _Factory[Service]) -> None:
        """Зарегистрировать фабрику для интерфейса."""
        _factories[interface] = factory
        _instances.pop(interface, None)

    @classmethod
    def resolve[Service](cls, interface: Callable[..., Service]) -> Service:
        """Получить экземпляр интерфейса; результат кэшируется (singleton)."""
        if interface not in _instances:
            _instances[interface] = cls._factory(interface)()
        return cast(Service, _instances[interface])

    @classmethod
    def create[Service](cls, interface: Callable[..., Service]) -> Service:
        """Создать новый экземпляр интерфейса (transient)."""
        return cast(Service, cls._factory(interface)())

    @classmethod
    def _factory(cls, interface: _Interface) -> Callable[[], Any]:
        try:
            return _factories[interface]
        except KeyError as exc:
            raise ServiceNotRegisteredError(interface) from exc

    @classmethod
    def reset(cls) -> None:
        """Сбросить кэшированные экземпляры; регистрации фабрик сохраняются."""
        _instances.clear()

    @classmethod
    def clear(cls) -> None:
        """Полный сброс: удалить и экземпляры, и регистрации фабрик."""
        _instances.clear()
        _factories.clear()

    @classmethod
    def is_configured(cls) -> bool:
        """Есть ли зарегистрированные фабрики."""
        return bool(_factories)
