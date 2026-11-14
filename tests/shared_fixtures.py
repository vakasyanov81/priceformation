"""Общие фикстуры логов, конфигурации и DI для обоих наборов тестов."""

import logging
from collections.abc import Iterator

import pytest
from log_watch import LoggerWatch, LoggerWatcher, records_of

from cfg import init_cfg
from cfg.services import configure_services
from domain.config_context import get_config_provider, set_config_provider
from services.service_provider import ServiceProvider


@pytest.fixture
def watch_logger(caplog: pytest.LogCaptureFixture) -> LoggerWatcher:
    """Поднять уровень логгера и отдавать его записи: (уровень, текст) — после вызова кода."""

    def _watch(logger_name: str, level: int = logging.INFO) -> LoggerWatch:
        caplog.set_level(level, logger=logger_name)
        return lambda: records_of(caplog, logger_name)

    return _watch


def pytest_configure() -> None:
    """Композиция тестов: те же пути, что и init_cfg в run.main."""
    init_cfg()
    configure_services()


@pytest.fixture(autouse=True)
def config_provider_restored() -> Iterator[None]:
    """Провайдер путей, какой был до теста, возвращается после."""
    previous = get_config_provider()
    yield
    set_config_provider(previous)


@pytest.fixture(autouse=True)
def service_provider_isolated() -> Iterator[None]:
    """DI-контейнер: базовая сборка до теста, сброс после (без глобальных завязок)."""
    ServiceProvider.clear()
    configure_services()
    yield
    ServiceProvider.reset()
