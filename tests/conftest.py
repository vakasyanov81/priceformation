"""global fixtures"""

import logging
from collections.abc import Iterator
from pathlib import Path

import pytest
from log_watch import LoggerWatch, LoggerWatcher, records_of

from cfg import init_cfg
from domain.config_context import get_config_provider, set_config_provider
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.base_parser.nomenclature_correction import clear_nomenclature_cache
from parsers.data_provider.manufacturer_aliases import (
    clear_manufacturer_aliases_cache,
)
from parsers.mail.provider import clear_mail_config_cache
from parsers.vendor_config.provider import clear_vendor_configs_cache
from services.configure import configure_services
from services.service_provider import ServiceProvider

_ROOT = Path(__file__).resolve().parent


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


@pytest.fixture
def fake_config_provider(tmp_path: Path) -> FakeConfigProvider:
    """Пути окружения во временной папке вместо файлов проекта."""
    provider = FakeConfigProvider(tmp_path)
    set_config_provider(provider)
    return provider


@pytest.fixture
def example_vendors_provider(tmp_path: Path) -> FakeConfigProvider:
    """Провайдер на дубликате конфигов поставщиков из tests/parse_config_example/vendors.

    Тесты, проверяющие наполнение реестра/каталога, читают копию, а не боевой
    `parse_config/vendors/`, и не ломаются при правке реальных настроек.
    """
    provider = FakeConfigProvider(tmp_path, config_folder=_ROOT / 'parse_config_example')
    set_config_provider(provider)
    clear_vendor_configs_cache()
    return provider


@pytest.fixture(autouse=True)
def _config_provider_restored() -> Iterator[None]:
    """Провайдер путей, какой был до теста, возвращается после."""
    previous = get_config_provider()
    yield
    set_config_provider(previous)


@pytest.fixture(autouse=True)
def _clear_process_file_caches(monkeypatch: pytest.MonkeyPatch) -> None:
    """Сброс модульных кэшей файлов, чтобы тесты не зависели от порядка; разбор не обнуляет боевые логи."""
    monkeypatch.setattr('services.parse_orchestrator.clear_log_files', lambda: None)
    clear_nomenclature_cache()
    clear_manufacturer_aliases_cache()
    clear_vendor_configs_cache()
    clear_mail_config_cache()


@pytest.fixture(autouse=True)
def _service_provider_isolated() -> Iterator[None]:
    """DI-контейнер: базовая сборка до теста, сброс после (без глобальных завязок)."""
    ServiceProvider.clear()
    configure_services()
    yield
    ServiceProvider.reset()
