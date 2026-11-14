"""global fixtures"""

from pathlib import Path

import pytest
import shared_fixtures

from domain.config_context import set_config_provider
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.base_parser.nomenclature_correction import clear_nomenclature_cache
from parsers.data_provider.manufacturer_aliases import (
    clear_manufacturer_aliases_cache,
)
from parsers.mail.provider import clear_mail_config_cache
from parsers.vendor_config.provider import clear_vendor_configs_cache

_ROOT = Path(__file__).resolve().parent


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
def _clear_process_file_caches(monkeypatch: pytest.MonkeyPatch) -> None:
    """Сброс модульных кэшей файлов, чтобы тесты не зависели от порядка; разбор не обнуляет боевые логи."""
    monkeypatch.setattr('services.parse_orchestrator.clear_log_files', lambda: None)
    clear_nomenclature_cache()
    clear_manufacturer_aliases_cache()
    clear_vendor_configs_cache()
    clear_mail_config_cache()


watch_logger = shared_fixtures.watch_logger
pytest_configure = shared_fixtures.pytest_configure
_config_provider_restored = shared_fixtures.config_provider_restored
_service_provider_isolated = shared_fixtures.service_provider_isolated
