"""Тесты DI-контейнера ServiceProvider."""

from collections.abc import Iterator

import pytest

from services.service_provider import ServiceNotRegisteredError, ServiceProvider


class _SampleService:
    """Простая служба для проверки контейнера."""

    def __init__(self, marker: str = 'sample') -> None:
        self.marker = marker


_SERVICE_KEY: type[_SampleService] = _SampleService


@pytest.fixture(autouse=True)
def _clean_provider() -> Iterator[None]:
    """Чистый контейнер до и после теста."""
    ServiceProvider.clear()
    yield
    ServiceProvider.clear()


def test_resolve_creates_and_caches() -> None:
    """resolve создаёт экземпляр один раз и дальше отдаёт кэш."""
    ServiceProvider.register(_SERVICE_KEY, lambda: _SampleService('cached'))
    first = ServiceProvider.resolve(_SERVICE_KEY)
    assert ServiceProvider.resolve(_SERVICE_KEY) is first
    assert first.marker == 'cached'


def test_factory_runs_lazily() -> None:
    """фабрика не вызывается до первого resolve."""
    calls: list[int] = []
    ServiceProvider.register(_SERVICE_KEY, lambda: _counted_factory(calls))
    assert not calls
    ServiceProvider.resolve(_SERVICE_KEY)
    assert calls == [1]


def _counted_factory(calls: list[int]) -> _SampleService:
    calls.append(1)
    return _SampleService()


def test_create_is_transient() -> None:
    """create всегда вызывает фабрику заново."""
    ServiceProvider.register(_SERVICE_KEY, _SampleService)
    first = ServiceProvider.create(_SERVICE_KEY)
    assert ServiceProvider.create(_SERVICE_KEY) is not first


def test_register_overwrites_factory() -> None:
    """повторная регистрация интерфейса заменяет фабрику."""
    ServiceProvider.register(_SERVICE_KEY, lambda: _SampleService('old'))
    ServiceProvider.register(_SERVICE_KEY, lambda: _SampleService('new'))
    assert ServiceProvider.resolve(_SERVICE_KEY).marker == 'new'


def test_register_drops_cached_instance() -> None:
    """перерегистрация сбрасывает кэшированный экземпляр."""
    ServiceProvider.register(_SERVICE_KEY, lambda: _SampleService('old'))
    first = ServiceProvider.resolve(_SERVICE_KEY)
    ServiceProvider.register(_SERVICE_KEY, lambda: _SampleService('new'))
    assert ServiceProvider.resolve(_SERVICE_KEY) is not first


def test_unregistered_interface_raises() -> None:
    """без фабрики resolve и create бросают ServiceNotRegisteredError."""
    with pytest.raises(ServiceNotRegisteredError):
        ServiceProvider.resolve(_SERVICE_KEY)
    with pytest.raises(ServiceNotRegisteredError):
        ServiceProvider.create(_SERVICE_KEY)


def test_reset_drops_instances_keeps_factories() -> None:
    """reset сбрасывает экземпляры, но оставляет регистрации."""
    ServiceProvider.register(_SERVICE_KEY, _SampleService)
    first = ServiceProvider.resolve(_SERVICE_KEY)
    ServiceProvider.reset()
    assert ServiceProvider.resolve(_SERVICE_KEY) is not first


def test_clear_drops_registrations() -> None:
    """clear удаляет и экземпляры, и регистрации."""
    ServiceProvider.register(_SERVICE_KEY, _SampleService)
    assert ServiceProvider.is_configured()
    ServiceProvider.clear()
    assert not ServiceProvider.is_configured()
    with pytest.raises(ServiceNotRegisteredError):
        ServiceProvider.resolve(_SERVICE_KEY)
