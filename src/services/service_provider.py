"""Лёгковесный DI-контейнер приложения.

Регистрация фабрик по интерфейсу и ленивое разрешение зависимостей.
Один контейнер на процесс; ``configure_services()`` собирает граф при старте.
"""

from collections.abc import Callable
from typing import Any

type _ServiceFactory = Callable[[], Any]

_factories: dict[type[Any], _ServiceFactory] = {}
_instances: dict[type[Any], Any] = {}


class ServiceNotRegisteredError(LookupError):
    """Запрошенный интерфейс не зарегистрирован в контейнере."""


class ServiceProvider:
    """Простой DI-контейнер: фабрики по интерфейсу, ленивое разрешение."""

    @classmethod
    def register(cls, interface: type[Any], factory: _ServiceFactory) -> None:
        """Зарегистрировать фабрику для интерфейса."""
        _factories[interface] = factory
        _instances.pop(interface, None)

    @classmethod
    def resolve(cls, interface: type[Any]) -> Any:
        """Получить экземпляр интерфейса; результат кэшируется (singleton)."""
        if interface not in _instances:
            _instances[interface] = cls._factory(interface)()
        return _instances[interface]

    @classmethod
    def create(cls, interface: type[Any]) -> Any:
        """Создать новый экземпляр интерфейса (transient)."""
        return cls._factory(interface)()

    @classmethod
    def _factory(cls, interface: type[Any]) -> _ServiceFactory:
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
