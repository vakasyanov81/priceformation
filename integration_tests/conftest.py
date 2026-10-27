"""fixtures for integration tests"""

import logging
from collections.abc import Iterator

import pytest
from log_watch import LoggerWatch, LoggerWatcher, records_of

from cfg import init_cfg
from domain.config_context import get_config_provider, set_config_provider
from parsers.base_parser.nomenclature_correction import clear_nomenclature_cache
from parsers.data_provider.manufacturer_aliases import (
    clear_manufacturer_aliases_cache,
)
from services.configure import configure_services
from services.service_provider import ServiceProvider


@pytest.fixture
def watch_logger(caplog: pytest.LogCaptureFixture) -> LoggerWatcher:
    """Поднять уровень логгера и отдавать его записи: (уровень, текст) — после вызова кода."""

    def _watch(logger_name: str, level: int = logging.INFO) -> LoggerWatch:
        caplog.set_level(level, logger=logger_name)
        return lambda: records_of(caplog, logger_name)

    return _watch


def pytest_configure() -> None:
    """Композиция интеграционных тестов: пути логов и parse_config."""
    init_cfg()
    configure_services()


@pytest.fixture(autouse=True)
def _config_provider_restored() -> Iterator[None]:
    """Провайдер путей, какой был до теста, возвращается после."""
    previous = get_config_provider()
    yield
    set_config_provider(previous)


@pytest.fixture(autouse=True)
def _log_files_untouched(monkeypatch: pytest.MonkeyPatch) -> None:
    """Разбор в тестах не обнуляет боевые файлы логов."""
    monkeypatch.setattr('services.parse_orchestrator.clear_log_files', lambda: None)


@pytest.fixture(autouse=True)
def _clear_process_file_caches() -> None:
    """Сброс модульных кэшей файлов, чтобы тесты не зависели от порядка."""
    clear_nomenclature_cache()
    clear_manufacturer_aliases_cache()


@pytest.fixture(autouse=True)
def _service_provider_isolated() -> Iterator[None]:
    """DI-контейнер: базовая сборка до теста, сброс после (без глобальных завязок)."""
    ServiceProvider.clear()
    configure_services()
    yield
    ServiceProvider.reset()
